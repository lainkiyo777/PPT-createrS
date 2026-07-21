import importlib.util
import json
import os
import shutil
import stat
import unittest
import uuid
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
TEST_TMP_ROOT = SKILL_ROOT / ".test-tmp-multi-agent"


def load_script(name):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"ppt_creaters_test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_mapping(path):
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        try:
            result[key.strip()] = json.loads(value)
        except json.JSONDecodeError:
            result[key.strip()] = value.strip("\"'")
    return result


def high_score_evaluation(*, critical=None, issues=None):
    dimensions = {
        "workflow_compliance": 95,
        "content_accuracy": 95,
        "narrative_structure": 90,
        "visual_quality": 90,
        "typography": 90,
        "data_integrity": 95,
        "speaker_notes": 90,
        "template_style_alignment": 90,
    }
    return {
        "review_id": "review-01",
        "artifact_version": "round-01",
        "total_score": 100,
        "passed": True,
        "critical_failures": list(critical or []),
        "dimension_scores": dimensions,
        "issues": list(issues or []),
        "revision_priority": [],
    }


class MultiAgentContractTests(unittest.TestCase):
    def setUp(self):
        self.case_root = TEST_TMP_ROOT / f"{self._testMethodName}-{uuid.uuid4().hex}"
        self.output = self.case_root / "output"
        self.output.mkdir(parents=True)

    def tearDown(self):
        def remove_readonly(function, path, _error):
            os.chmod(path, stat.S_IWRITE)
            function(path)

        shutil.rmtree(self.case_root, onerror=remove_readonly)

    def test_model_router_exposes_required_roles_and_models(self):
        routing = load_script("model_router")
        router = routing.ModelRouter(SKILL_ROOT / "agents" / "model-routing.json")
        self.assertEqual("gpt-5.6-sol", router.route("orchestrator").model)
        self.assertEqual("gpt-5.6-sol", router.route("producer").model)
        self.assertEqual("gpt-5.6-terra", router.route("reviewer").model)
        self.assertEqual("gpt-5.6-sol", router.route("slide_worker", complexity="high").model)

    def test_unavailable_model_is_not_silently_ignored(self):
        routing = load_script("model_router")
        router = routing.ModelRouter(SKILL_ROOT / "agents" / "model-routing.json")
        with self.assertRaises(routing.ModelUnavailableError):
            router.route("reviewer", available_models={"gpt-5.4-mini"})

    def test_initial_run_writes_pending_config_and_stops(self):
        runner = load_script("workflow_runner")
        result = runner.run_once(
            self.output,
            config={"template_source": "blue-template.pptx"},
            input_fn=lambda _="": self.fail("initialized run must not consume a user selection"),
            output_fn=lambda _: None,
        )
        self.assertEqual("awaiting_configuration", result.status)
        pending = read_mapping(self.output / "deck-config.pending.yaml")
        self.assertEqual("manual", pending["workflow_mode"])
        self.assertEqual("guided", pending["selection_mode"])
        state = read_mapping(self.output / "build-state.yaml")
        self.assertEqual("awaiting_configuration", state["build_status"])

    def test_initial_run_accepts_relative_output_path(self):
        runner = load_script("workflow_runner")
        relative_output = self.output.relative_to(Path.cwd())
        result = runner.run_once(relative_output, output_fn=lambda _: None)
        self.assertEqual("awaiting_configuration", result.status)
        self.assertTrue((self.output / "deck-config.pending.yaml").is_file())

    def test_state_transition_records_actor_and_evidence(self):
        state_module = load_script("state_machine")
        evidence = self.output / "evidence.json"
        evidence.write_text("{}", encoding="utf-8")
        machine = state_module.WorkflowStateMachine(self.output)
        machine.load()
        state = machine.transition(
            "awaiting_configuration",
            stage="configuration",
            actor="orchestrator",
            evidence_files=[evidence],
        )
        last = state.transition_history[-1]
        self.assertEqual("orchestrator", last["actor"])
        self.assertTrue(last["evidence_files"])

    def test_producer_cannot_mark_completed(self):
        state_module = load_script("state_machine")
        evidence = self.output / "gate.json"
        evidence.write_text("{}", encoding="utf-8")
        machine = state_module.WorkflowStateMachine(self.output)
        state = machine.load()
        state.build_status = "final_qa"
        machine.save(state)
        with self.assertRaises(state_module.ActorPermissionError):
            machine.transition(
                "completed",
                stage="completion",
                actor="producer",
                evidence_files=[evidence],
            )

    def test_orchestrator_cannot_complete_without_passed_deterministic_gate(self):
        state_module = load_script("state_machine")
        decision = self.output / "reviews" / "round-01" / "gate-decision.json"
        decision.parent.mkdir(parents=True)
        decision.write_text(json.dumps({"passed": False, "deterministic_checks_passed": True}), encoding="utf-8")
        machine = state_module.WorkflowStateMachine(self.output)
        state = machine.load()
        state.build_status = "final_qa"
        machine.save(state)
        with self.assertRaises(state_module.ActorPermissionError):
            machine.transition(
                "completed",
                stage="completion",
                actor="orchestrator",
                evidence_files=[decision],
            )

    def test_reviewer_has_no_write_permission(self):
        isolation = load_script("review_isolation")
        pack = self.output / "review-pack"
        pack.mkdir()
        (pack / "user-brief.md").write_text("brief", encoding="utf-8")
        session = isolation.ReviewerSession(pack)
        with self.assertRaises(isolation.PermissionDenied):
            session.write("preview-images/slide-01.png", b"changed")

    def test_reviewer_has_no_image2_permission(self):
        isolation = load_script("review_isolation")
        pack = self.output / "review-pack"
        pack.mkdir()
        session = isolation.ReviewerSession(pack)
        with self.assertRaises(isolation.PermissionDenied):
            session.call_tool("image2")

    def test_reviewer_context_rejects_producer_logs(self):
        isolation = load_script("review_isolation")
        pack = self.output / "review-pack"
        pack.mkdir()
        producer_log = self.output / "producer.log"
        producer_log.write_text("private producer context", encoding="utf-8")
        with self.assertRaises(isolation.ContaminatedContextError):
            isolation.validate_reviewer_context(pack, [pack / "user-brief.md", producer_log])

    def test_review_pack_is_frozen_and_excludes_producer_private_context(self):
        isolation = load_script("review_isolation")
        (self.output / "user-brief.md").write_text("brief", encoding="utf-8")
        (self.output / "producer.log").write_text("private", encoding="utf-8")
        rubric = SKILL_ROOT / "rubrics" / "preview-rubric.yaml"
        pack = isolation.ReviewPackBuilder(self.output).build(
            self.output / "review-pack",
            rubric_path=rubric,
        )
        manifest = json.loads((pack / "review-pack-manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["producer_private_context_included"])
        self.assertFalse((pack / "producer.log").exists())
        self.assertTrue((pack / "rubric.yaml").is_file())

    def test_producer_cannot_modify_evaluation(self):
        isolation = load_script("review_isolation")
        controller = isolation.ArtifactAccessController(self.output)
        evaluation = self.output / "reviews" / "round-01" / "evaluation.json"
        with self.assertRaises(isolation.PermissionDenied):
            controller.assert_write_allowed("producer", evaluation)

    def test_critical_failure_prevents_pass(self):
        gate_module = load_script("review_gate")
        gate = gate_module.DeterministicReviewGate(SKILL_ROOT / "rubrics" / "final-delivery-rubric.yaml")
        decision = gate.evaluate(
            high_score_evaluation(critical=["presentation_participated_in_page_design"]),
            deterministic_checks_passed=True,
        )
        self.assertFalse(decision.passed)

    def test_score_below_threshold_prevents_pass(self):
        gate_module = load_script("review_gate")
        evaluation = high_score_evaluation()
        evaluation["dimension_scores"] = {key: 80 for key in evaluation["dimension_scores"]}
        gate = gate_module.DeterministicReviewGate(SKILL_ROOT / "rubrics" / "final-delivery-rubric.yaml")
        decision = gate.evaluate(evaluation, deterministic_checks_passed=True)
        self.assertFalse(decision.passed)
        self.assertEqual(80, decision.total_score)

    def test_issue_without_evidence_is_invalid(self):
        gate_module = load_script("review_gate")
        issue = {
            "id": "ISSUE-1",
            "severity": "major",
            "criterion": "typography",
            "slides": [3],
            "finding": "Text is too dense",
            "evidence": "",
            "required_fix": "Reduce copy",
        }
        gate = gate_module.DeterministicReviewGate(SKILL_ROOT / "rubrics" / "final-delivery-rubric.yaml")
        decision = gate.evaluate(high_score_evaluation(issues=[issue]), deterministic_checks_passed=True)
        self.assertFalse(decision.passed)
        self.assertTrue(any("evidence" in error for error in decision.validation_errors))

    def test_two_failed_rounds_end_at_awaiting_human_review(self):
        state_module = load_script("state_machine")
        cycle_module = load_script("review_cycle")
        machine = state_module.WorkflowStateMachine(self.output)
        state = machine.load()
        state.build_status = "reviewing"
        machine.save(state)
        controller = cycle_module.RevisionController(self.output, machine, max_rounds=2)
        controller.record_failure(round_number=1, issues=[{"id": "A"}])
        state = machine.load()
        state.build_status = "reviewing"
        machine.save(state)
        result = controller.record_failure(round_number=2, issues=[{"id": "B"}])
        self.assertEqual("awaiting_human_review", result.build_status)
        self.assertTrue((self.output / "artifacts" / "round-01").is_dir())
        self.assertTrue((self.output / "artifacts" / "round-02").is_dir())

    def test_review_pack_creates_host_side_deterministic_checks(self):
        runner = load_script("workflow_runner")
        pack_manifest, request_path, checks_path = runner._prepare_review_pack(
            self.output,
            rubric_name="preview-rubric.yaml",
            reviewer_role="reviewer",
            reviewer_model="gpt-5.6-terra",
            phase="preview",
            slide_count=0,
        )
        self.assertTrue(pack_manifest.is_file())
        self.assertTrue(request_path.is_file())
        checks = json.loads(checks_path.read_text(encoding="utf-8"))
        self.assertEqual("preview", checks["phase"])
        self.assertIn("deterministic_checks_passed", checks)

    def test_revising_waits_for_producer_revision_evidence(self):
        runner = load_script("workflow_runner")
        state_module = load_script("state_machine")
        issue_dir = self.output / "artifacts" / "round-01"
        issue_dir.mkdir(parents=True)
        (issue_dir / "structured-issues.json").write_text(
            json.dumps({"round": 1, "review_phase": "preview", "issues": [{"id": "A"}]}),
            encoding="utf-8",
        )
        machine = state_module.WorkflowStateMachine(self.output)
        state = machine.load()
        state.build_status = "revising"
        state.revision_round = 1
        machine.save(state)

        waiting = runner.run_once(self.output, output_fn=lambda _: None)
        self.assertEqual("revising", waiting.status)

        ready = issue_dir / "revision-ready.json"
        ready.write_text(json.dumps({"revised_by": "producer"}), encoding="utf-8")
        advanced = runner.run_once(self.output, output_fn=lambda _: None)
        self.assertEqual("generating_previews", advanced.status)


if __name__ == "__main__":
    unittest.main()
