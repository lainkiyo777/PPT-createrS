import importlib.util
import json
import shutil
import unittest
import uuid
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / 'scripts'
TMP = SKILL_ROOT / '.test-tmp-runtime-regressions'

def load(name):
    spec = importlib.util.spec_from_file_location(f'ppt_runtime_{name}', SCRIPTS / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ImageGenAdapter:
    tool_name = 'image_gen'
    model_or_tool_version = 'bundled-imagegen-test-v1'
    def generate(self, *, prompt_path, reference_images, output_path):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(b'fake-image-for-adapter-contract')
        return True

class ImageAdapterContractTests(unittest.TestCase):
    def setUp(self):
        self.root = TMP / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        (self.root / 'deck-config.confirmed.yaml').write_text(
            'visual_generator: image_gen\n', encoding='utf-8'
        )
        self.prompt = self.root / 'prompt.txt'
        self.prompt.write_text('test prompt', encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_declared_image_gen_adapter_is_accepted_and_recorded(self):
        runner = load('workflow_runner')
        runner._call_image2(
            ImageGenAdapter(),
            output_dir=self.root,
            prompt_path=self.prompt,
            reference_images=['template-preview.png'],
            output_path=self.root / 'slide.png',
        )
        manifest = json.loads((self.root / 'image-generation-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual('image_gen', manifest['calls'][0]['tool_name'])
        self.assertTrue(manifest['calls'][0]['success'])

    def test_runner_rejects_auto_strict_template_before_generation(self):
        runner = load('workflow_runner')
        config = {
            'workflow_mode':'auto','selection_mode':'direct','presentation_type':'technical-report',
            'visual_style':'industrial-technical','presentation_effect':'formal-report',
            'template_application_mode':'strict-template','output_mode':'production-image',
            'notes_mode':'full','target_duration_minutes':20,'content_density':'medium',
        }
        first = runner.run_once(self.root, config=config, input_fn=lambda prompt: '', output_fn=lambda _: None)
        self.assertEqual('awaiting_configuration', first.status)
        second = runner.run_once(self.root, config=config, input_fn=lambda prompt: (_ for _ in ()).throw(RuntimeError('prompted')), output_fn=lambda _: None)
        self.assertEqual('failed', second.status)
        self.assertIn('strict-template', second.message)

    def test_runner_blocks_generation_when_imported_template_profile_is_missing(self):
        runner = load('workflow_runner')
        source = self.root / 'references' / 'deck-library' / 'inbox' / 'blue.pptx'
        source.parent.mkdir(parents=True)
        source.write_bytes(b'pptx')
        config = {
            'presentation_type':'technical-report','visual_style':'academic-clean','presentation_effect':'formal-report',
            'workflow_mode':'manual','selection_mode':'guided','template_application_mode':'style-reference',
            'output_mode':'production-image','notes_mode':'full','target_duration_minutes':20,'content_density':'medium',
            'template_source':'references/deck-library/inbox/blue.pptx',
        }
        runner.run_once(self.root, config=config, input_fn=lambda prompt: '', output_fn=lambda _: None)
        values = iter(['2','1','2','1','1','3','3','2','yes'])
        result = runner.run_once(self.root, config=config, input_fn=lambda prompt: next(values), output_fn=lambda _: None)
        self.assertEqual('failed', result.status)
        self.assertIn('template contract', result.message)

    def test_auto_direct_config_file_is_preserved_on_second_run(self):
        runner = load('workflow_runner')
        config = {
            'workflow_mode':'auto','selection_mode':'direct','presentation_type':'technical-report',
            'visual_style':'industrial-technical','presentation_effect':'formal-report',
            'template_application_mode':'style-reference','output_mode':'production-image',
            'notes_mode':'full','target_duration_minutes':20,'content_density':'medium',
        }
        (self.root / 'deck-config.yaml').write_text('\n'.join(f'{k}: {v}' for k,v in config.items())+'\n', encoding='utf-8')
        first = runner.run_once(self.root, input_fn=lambda prompt: '', output_fn=lambda _: None)
        self.assertEqual('awaiting_configuration', first.status)
        second = runner.run_once(self.root, input_fn=lambda prompt: (_ for _ in ()).throw(RuntimeError('prompted')), output_fn=lambda _: None)
        self.assertEqual('generating_slide_specs', second.status)

    def test_python_pptx_one_emu_rounding_is_valid_16_9(self):
        guard = load('presentation_guard')
        self.assertTrue(guard.is_valid_16_9_size((12191999, 6858000)))
        self.assertFalse(guard.is_valid_16_9_size((12000000, 6858000)))

    def test_auto_assembly_gate_does_not_require_selected_style(self):
        guard = load('presentation_guard')
        (self.root / 'deck-config.confirmed.yaml').write_text('workflow_mode: auto\nselection_mode: direct\n', encoding='utf-8')
        (self.root / 'final-images').mkdir()
        (self.root / 'final-images' / 'slide-01.png').write_bytes(b'png')
        (self.root / 'final-images-qa.json').write_text(json.dumps({'status':'pass','image_count':1}), encoding='utf-8')
        (self.root / 'speaker-notes').mkdir()
        (self.root / 'speaker-notes' / 'slide-01.md').write_text('note', encoding='utf-8')
        guard.assert_assembly_ready(self.root, slide_count=1)

    def test_auto_preview_gate_does_not_require_selected_style(self):
        guards = load('artifact_guards')
        (self.root / 'deck-config.confirmed.yaml').write_text('workflow_mode: auto\nselection_mode: direct\nvisual_generator: image_gen\n', encoding='utf-8')
        guards.assert_preview_generation_allowed(self.root)

    def test_auto_deterministic_checks_do_not_require_user_style_candidate(self):
        checks = load('deterministic_checks')
        (self.root / 'deck-config.confirmed.yaml').write_text('workflow_mode: auto\nselection_mode: direct\nvisual_generator: image_gen\n', encoding='utf-8')
        spec = self.root / 'slide-specs' / 'slide-01.yaml'
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text('slide_number: 1\n', encoding='utf-8')
        (self.root / 'preview-images').mkdir()
        (self.root / 'preview-images' / 'slide-01.png').write_bytes(b'not-a-real-png')
        (self.root / 'typography-qa-report.md').write_text('status: pass\n', encoding='utf-8')
        (self.root / 'data-qa-report.md').write_text('status: pass\n', encoding='utf-8')
        (self.root / 'data').mkdir()
        (self.root / 'data' / 'metrics.json').write_text('{}', encoding='utf-8')
        payload = checks.DeterministicCheckRunner(self.root).run(phase='preview', slide_count=1, report_path=self.root / 'checks.json')
        self.assertTrue(payload['checks']['selected_style']['passed'])
        self.assertTrue(payload['checks']['image2_manifest']['passed'])
        self.assertTrue(payload['checks']['visual_generator_manifest']['passed'])

    def test_manifest_accepts_configured_image_gen_tool(self):
        guards = load('artifact_guards')
        calls = []
        for candidate in ('candidate-a', 'candidate-b', 'candidate-c'):
            for page_type in ('cover', 'section', 'content', 'result'):
                path = self.root / 'style-candidates' / candidate / f'{page_type}.png'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'png')
                (path.parent / 'style-profile.yaml').write_text('profile: test\n', encoding='utf-8')
                calls.append({'tool_name':'image_gen','model_or_tool_version':'test-v1','prompt_path':'prompt.txt','reference_images':['template.png'],'output_path':path.relative_to(self.root).as_posix(),'timestamp':'now','success':True,'error':None})
        (self.root / 'image-generation-manifest.json').write_text(json.dumps({'calls':calls}),encoding='utf-8')
        self.assertEqual([], guards.validate_style_candidates(self.root))

    def test_missing_declared_adapter_names_the_required_tool(self):
        runner = load('workflow_runner')
        with self.assertRaisesRegex(RuntimeError, 'image_gen'):
            runner._call_image2(
                None,
                output_dir=self.root,
                prompt_path=self.prompt,
                reference_images=['template-preview.png'],
                output_path=self.root / 'slide.png',
            )

    def test_candidate_prompt_names_the_configured_visual_generator(self):
        runner = load('workflow_runner')
        prompt = runner._candidate_prompt('clean technical report', 'cover', visual_tool='image_gen')
        self.assertIn('image_gen', prompt)
        self.assertNotIn('Use image2', prompt)

    def test_slide_specs_require_title_layout_and_visual_style(self):
        guards = load('artifact_guards')
        spec = self.root / 'slide-specs' / 'slide-01.yaml'
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(
            'slide_number: 1\npage_type: content\nkey_message: message\n'
            'image_prompt: prompt\nstyle_reference_prompt: style\nreference_images: [template.png]\n'
            'dominant_visual: chart\ndeterministic_text_overlay: text\n'
            'deterministic_chart_overlay: chart\nlayout_flexibility: recompose\n'
            'visual_inheritance: blue\nprohibited_inheritance: source coordinates\n'
            'referenced_metrics: []\nspeaker_notes_path: notes/slide-01.md\nqa_checklist: [legible]\n',
            encoding='utf-8',
        )
        _, errors = guards.validate_slide_specs(self.root)
        self.assertTrue(any('title' in error for error in errors))
        self.assertTrue(any('layout' in error for error in errors))
        self.assertTrue(any('visual_style' in error for error in errors))

    def test_slide_spec_number_must_match_filename(self):
        guards = load('artifact_guards')
        spec = self.root / 'slide-specs' / 'slide-02.yaml'
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(
            'slide_number: 1\npage_type: content\ntitle: title\nkey_message: message\n'
            'layout: full\nvisual_style: blue\ntemplate_application_mode: style-reference\n'
            'image_prompt: prompt\nstyle_reference_prompt: style\nreference_images: [template.png]\n'
            'dominant_visual: chart\ndeterministic_text_overlay: text\n'
            'deterministic_chart_overlay: chart\nlayout_flexibility: recompose\n'
            'visual_inheritance: blue\nprohibited_inheritance: source coordinates\n'
            'referenced_metrics: []\nspeaker_notes_path: notes/slide-01.md\nqa_checklist: [legible]\n',
            encoding='utf-8',
        )
        _, errors = guards.validate_slide_specs(self.root)
        self.assertTrue(any('slide_number' in error and 'filename' in error for error in errors))

    def test_slide_specs_must_be_contiguous(self):
        guards = load('artifact_guards')
        spec = self.root / 'slide-specs' / 'slide-02.yaml'
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text('slide_number: 2\n', encoding='utf-8')
        _, errors = guards.validate_slide_specs(self.root)
        self.assertTrue(any('contiguous' in error for error in errors))

if __name__ == '__main__':
    unittest.main()
