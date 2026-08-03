---
name: ppt-creaters
description: Build or refactor auditable, multi-model PowerPoint production workflows from topics, Markdown, documents, data, or PPTX templates. Use when Codex must create a presentation with explicit configuration choices, visual-generator provenance, deterministic text/charts/notes, isolated read-only review, persistent human Gates, verified PowerPoint speaker notes, or an image-only final PPTX; also use when diagnosing or testing those workflow contracts.
---

# PPT Creaters

Release: 2.1.0

Build presentations as a persistent, auditable workflow. Confirm configuration before generation, use the configured visual generator for visual composition, keep exact content deterministic, isolate Reviewer context, and let code—not a model—calculate PASS/FAIL.

Read `references/multi-agent-contract.md` before changing orchestration, review, state, or artifact contracts. Read `references/p0-contract.md` when validating detailed output-mode fields and legacy P0 artifacts.
Read `references/template-reference-image-pipeline.md` when a PPTX template is supplied or the user asks to preserve a template's visual language. The checked-in process evidence is summarized in `docs/p0/v2.1-template-reference-process.md`.

## Run the orchestrator

Use `scripts/workflow_runner.py <output-dir>` as the only workflow entry point. Treat `scripts/config_gate.py` as a compatibility helper only.

Create `deck-config.yaml` and `deck-brief.yaml` before invoking the runner. Unless both modes were explicitly supplied as `workflow_mode: auto` and `selection_mode: direct`, resolve them to:

```yaml
workflow_mode: manual
selection_mode: guided
```

Treat an uploaded template only as `template_source`; never treat it as configuration confirmation, style selection, or permission to use `strict-template`.

## Declare visual and PPT adapters

Set `visual_generator` in `deck-config.yaml` to the actual host adapter name. Use `image_gen` when the Codex image-generation adapter is available; use `image2` only when the host explicitly provides an adapter with `tool_name: image2`. The runner records the actual adapter name and model/tool version in `image-generation-manifest.json`. A missing or misidentified adapter is a hard failure with an injection-path diagnostic; never substitute `presentation`, PIL, screenshots, or an unverified fallback for visual generation.

Set `presentation_adapter` to the actual PPT assembly adapter. The CLI entry point does not invent adapters: the host must inject adapters implementing `generate(prompt_path, reference_images, output_path)` and `assemble(...)`, or the run stops before producing a deck.

## Route models explicitly

Load `agents/model-routing.json` through `scripts/model_router.py`. Record every decision in `output/model-routing-manifest.json`. Fail when a required model is unavailable and no declared fallback is available; never substitute silently.

Use these roles:

- Orchestrator (`gpt-5.6-sol`): interpret requirements, plan narrative, route models, control state, and manage human/Reviewer Gates. Do not perform mechanical work or self-approve.
- Producer (`gpt-5.6-sol`): create narrative, style abstraction, key/complex specs, visual-generator prompts, and revisions. Do not modify review results, change workflow state, or cross a Gate.
- Slide Worker (`gpt-5.6-terra`; escalate complex work to `gpt-5.6-sol`): expand approved rules into ordinary specs, compressed copy, and notes.
- Low-cost Worker (`gpt-5.6-luna`; explicit fallback `gpt-5.4-mini`): parse, classify, normalize, log, inspect, and run mechanical checks.
- Reviewer (`gpt-5.6-terra`) and Final Reviewer (`gpt-5.6-sol`): inspect only frozen review packs in isolated, read-only contexts. Do not read Producer context, write files, call the visual generator, or call PPT tools.

## Enforce persistent state and Gates

Persist state in `output/build-state.yaml` and mirror it to `build-status.json`. Allow only:

```text
initialized
awaiting_configuration
generating_style_candidates
awaiting_style_selection
generating_slide_specs
generating_previews
awaiting_preview_approval
generating_final_images
assembling_ppt
reviewing
revising
awaiting_human_review
final_qa
completed
failed
```

Let only the Orchestrator transition state. Record timestamp, actor, stage, evidence files, and message for every transition. Require at least one existing evidence file. Never enter two future `awaiting_*` states in one invocation. Stop immediately after the next human Gate.

Allow `completed` only when a real `gate-decision.json` records both `passed: true` and `deterministic_checks_passed: true`.

## Stop at configuration on the first run

On the first invocation, do not consume user input. Display choices for all eight fields, write `deck-config.pending.yaml` and `config-selection-report.md`, transition to `awaiting_configuration`, and stop:

- `presentation_type`
- `visual_style`
- `presentation_effect`
- `template_application_mode`
- `output_mode`
- `notes_mode`
- `target_duration_minutes`
- `content_density`

After explicit manual/guided confirmation, write `deck-config.confirmed.yaml` with `confirmed_by: user`, `confirmation_timestamp`, and a `configuration_source` entry for every field. Do not continue without this evidence.

## Generate and stop at style candidates

In manual mode, generate exactly three interpretations of the same template with real calls to the configured `visual_generator` adapter:

- Candidate A: clean university research—white canvas, blue structure, restrained and formal.
- Candidate B: technology launch—deep blue/high contrast, stronger hero visual and impact.
- Candidate C: data technical report—chart-first, explicit hierarchy, research-result oriented.

Generate `cover.png`, `section.png`, `content.png`, `result.png`, and `style-profile.yaml` for each candidate. Record every call in `image-generation-manifest.json` with:

`tool_name`, `model_or_tool_version`, `prompt_path`, `reference_images`, `output_path`, `timestamp`, `success`, and `error`.

Fail when the configured visual generator is unavailable, not called, unsuccessful, or missing from the manifest. Never use `presentation` or code-rendered cards as a visual-generator fallback. Transition to `awaiting_style_selection`, display A/B/C, and stop. Never auto-select Candidate A.

Accept only `selected-style.yaml` with `selected_by: user`, `selected_candidate`, `confirmation_timestamp`, `candidate_profile_path`, and `template_profile`.

## Apply templates semantically

Default to `style-reference`. Profile a supplied PPTX at `references/deck-library/profiles/<template-name>/style-profile.yaml`, covering palette, typography, spacing, composition, image treatment, icons, charts, page rhythm, layout principles, and prohibited behaviors.

In `style-reference`, learn the visual language but never copy source slides, source text, or exact textbox coordinates. Recompose from current semantics. Let the configured visual generator own background, scene, composition, and decoration. Let deterministic code own accurate Chinese, numbers, tables, charts, labels, page numbers, sources, and footnotes.

Use `adaptive-layout` for flexible page-family reuse. Use duplicate-slide and inherited textboxes as the primary method only in explicitly user-selected `strict-template` mode.

### v2.1 template-reference image route

When the request is “参考模板风格/按模板美化” rather than strict brand duplication, run the image-first route in `references/template-reference-image-pipeline.md`:

1. Inspect the supplied PPTX and export per-page `reference-slides/source-slide-XX.png`; derive `style-profile.yaml` before any page image is generated.
2. Generate the outline and independent page specs before calling the host visual adapter. Each page selects a `dominant_visual` and records its semantic composition, exact source content, flexible layout, template inheritance, and prohibited inheritance.
3. Call the actual host `image_gen` adapter once per page with the corresponding reference slide image. Prompt language must say: learn the visual language, do not copy source text, do not copy exact textbox coordinates, and recompose for the current page semantics. Architecture, comparison, flow, timeline, and chart pages may introduce new geometry when `style-reference` or `adaptive-layout` is selected.
4. Review the complete preview set before producing final images. A failed page returns to its slide spec/prompt; it must not be “fixed” by editing PPT assembly code.
5. Assemble a blank 16:9 deck from one approved final image per page. Do not create native body text, tables, charts, or a template-source duplicate slide. Verify the saved deck and notes after reopening.

The host owns the image-model call. This repository must not invent a CLI/API or claim a result when `image_gen`/`image2` is unavailable. Use `scripts/template_reference_pipeline.py validate-output <output-dir>` for the canonical `reference-slides → preview-images → final-images → presentation.pptx` contract. The checked-in demo can be checked with `validate-demo` and explicitly warns that it reuses approved previews as its image source.

## Producer/Slide Worker handoff

The runner does not invent outline or slide-spec content. After style selection, it persists `build_status: generating_slide_specs` and stops if `slide-specs/slide-XX.yaml` files are absent. The Producer/Slide Worker must create and validate those files; the next runner invocation resumes at preview generation. Never skip this handoff by writing previews or PPTX directly.

## Require independent slide specs

Create one `slide-specs/slide-XX.yaml` per page and validate it against `schemas/slide-spec.schema.json`. Require:

`slide_number`, `page_type`, `key_message`, `dominant_visual`, `template_application_mode`, `style_reference_prompt`, `image_prompt`, `reference_images`, `layout_flexibility`, `visual_inheritance`, `prohibited_inheritance`, `deterministic_text_overlay`, `deterministic_chart_overlay`, `referenced_metrics`, `speaker_notes_path`, and `qa_checklist`.

Block previews when `image_prompt` is absent. Tell the configured visual generator to learn style, avoid source text/coordinates, recompose for semantics, reserve safe overlay areas, and avoid unverifiable numbers or long Chinese copy.

## Isolate review and calculate the Gate

Build immutable `review-pack/round-XX/` directories with `scripts/review_isolation.py`. Include only the approved brief/config/style/rubric, source materials, specs, previews, overview, metrics, notes, and final PPTX when present. Hash files in `review-pack-manifest.json`. Exclude Producer conversation, logs, model identity, self-assessment, and persuasive summaries.

Have the Reviewer return JSON matching `schemas/evaluation.schema.json`. Persist it append-only as `reviews/round-XX/evaluation.json` through the Orchestrator. Require evidence for every issue.

Run `scripts/deterministic_checks.py` for counts, resolution, typography, data, visual-generator provenance, selected style, presentation structure, and notes round-trip. Run `scripts/review_gate.py` to recompute weighted score and ignore model-declared `total_score` or `passed`.

Use the final weights from `rubrics/final-delivery-rubric.yaml` and calculate:

```text
passed = recalculated_score >= 85
         AND critical_failures == 0
         AND deterministic_checks_passed == true
         AND evaluation_schema_errors == 0
```

After a failed review, pass only structured issues to Producer. Preserve `artifacts/round-01/` and `artifacts/round-02/`; require `revision-ready.json` before regeneration. After the second failed round, transition to `awaiting_human_review` and stop.

## Restrict final assembly

Call `presentation` only after final-image count equals slide count, final-image QA passes, notes count equals slide count, and `selected-style.yaml` says `selected_by: user`.

Permit assembly to create a blank 16:9 deck, insert one full-slide final image per page, write the matching speaker note, save, reopen, and verify. Forbid layouts, text boxes, shapes, charts, image modification, page design, and visual-generator fallback.

Require real `ppt/notesSlides/notesSlideN.xml` parts. Verify count, slide mapping, and exact text equality with `speaker-notes/slide-XX.md`. External Markdown without valid notesSlides is a hard failure.

## Preserve the output contract

```text
output/
├── build-state.yaml
├── build-status.json
├── deck-config.yaml
├── deck-config.pending.yaml
├── deck-config.confirmed.yaml
├── deck-brief.yaml
├── config-selection-report.md
├── model-routing-manifest.json
├── image-generation-manifest.json
├── selected-style.yaml
├── style-candidates/candidate-{a,b,c}/
├── outline.md
├── slide-specs/slide-XX.yaml
├── data/{metrics.json,tables.json,chart-data/}
├── preview-images/
├── final-images/
├── final-images-qa.json
├── speaker-notes/slide-XX.md
├── review-pack/round-XX/
├── reviews/round-XX/{review-request.json,evaluation.json,deterministic-checks.json,gate-decision.json}
├── artifacts/round-XX/{structured-issues.json,revision-ready.json}
├── presentation.pptx
└── *-qa-report.md
```

## Validate changes

Run:

```text
python -m unittest discover -s skills/ppt-creaters/tests -v
python scripts/validate_pipeline.py <output-dir>
python scripts/validate_p0.py <output-dir>
python skills/ppt-creaters/scripts/template_reference_pipeline.py validate-output <output-dir> --slide-count <N>
```

`validate_pipeline.py` detects the 2.0 `build-state.yaml`/YAML-spec contract; its Markdown-spec path is retained only for legacy P0 fixtures. Both validators must agree before publication.

Use `scripts/presentation_guard.py` for assembly/notes checks, `scripts/artifact_guards.py` for visual-generator/spec checks, and `scripts/template_policy.py` for template-mode semantics. Never claim success for an unavailable adapter, missing artifact, or unexecuted check.
