# Manual-Gated Image-First Workflow Design

## Goal

把 `ppt-creaters` 从“单次执行贯穿所有页面生成阶段”的约定改成可恢复、可审计、不可跨越人工 Gate 的持久化工作流；本轮不重新生成完整 PPT。

## Scope

- 修改范围限定为 `skills/ppt-creaters/` 下的 runtime scripts、tests、templates/contracts，以及 `docs/p0/` 的冒烟日志。
- 现有 `output/` 与 `projects/*/output/` 中的完整 PPT 产物不覆盖、不修补、不作为新流程的成功证据。
- manual/guided 是默认路径；只有调用方同时显式提供 `workflow_mode: auto` 和 `selection_mode: direct` 时，才允许使用 auto/direct。

## Architecture

### 1. Persistent state machine

`state_machine.py` owns the ordered states:

```text
awaiting_configuration
  -> generating_style_candidates
  -> awaiting_style_selection
  -> generating_previews
  -> awaiting_preview_approval
  -> generating_final_images
  -> assembling_ppt
  -> final_qa
  -> completed
```

Any runtime exception records `failed` with an error message and timestamp. State is stored in `output/build-state.yaml`, including the current state, workflow/selection modes, run identifier, transition history, and the last completed stage. State writes are atomic (`.tmp` then replace) so a terminated run can resume from the last durable state.

`run_once()` is the only stage driver. It reads the persisted state, executes at most one stage that may reach an `awaiting_*` state, persists the next state, and returns. It never calls a later stage after entering an awaiting state. A transition guard rejects invalid edges and detects a single execution that crosses two awaiting states.

### 2. Configuration Gate

`config_gate.py` remains the user-facing configuration boundary but writes the new YAML state file. A config is considered explicitly auto/direct only when both mode keys were supplied by the caller with exactly those values. Otherwise both keys resolve to `manual` and `guided` and the first run displays/requests confirmation for:

- `presentation_type`
- `visual_style`
- `presentation_effect`
- `template_application_mode`
- `output_mode`
- `notes_mode`
- `target_duration_minutes`
- `content_density`

`template_source` is recorded as an input reference only. It never creates `deck-config.confirmed.yaml`, `selected-style.yaml`, or a candidate selection by itself.

### 3. image2 boundary

`image2_adapter.py` defines an injectable `Image2Client` protocol. Candidate and slide generation can only use an adapter whose manifest record has `tool_name: image2`. The adapter must produce the requested output file; unavailable, missing, or differently named adapters are hard failures. No `presentation` fallback exists.

Manual style selection creates exactly three candidate packages:

```text
style-candidates/candidate-a/{cover,section,content,result}.png
style-candidates/candidate-b/{cover,section,content,result}.png
style-candidates/candidate-c/{cover,section,content,result}.png
```

Each package also contains `style-profile.yaml`. Every image2 attempt appends a record to `output/image-generation-manifest.json` containing `tool_name`, `prompt_path`, `reference_images`, `output_path`, `timestamp`, and `success`/`failure` information. Candidate generation ends in `awaiting_style_selection`; no candidate is selected automatically.

### 4. style-reference slide specs

`slide_specs.py` validates each spec before preview generation. Required fields are:

- `image_prompt`
- `style_reference_prompt`
- `reference_images`
- `dominant_visual`
- `deterministic_text_overlay`
- `deterministic_chart_overlay`

The style-reference prompt describes transferable color, typography, whitespace, geometry, image treatment, chart language, and rhythm. It explicitly forbids copying source text, source slide coordinates, or source page structure. image2 owns visual background, scene, composition, and decoration; deterministic code owns exact Chinese, numbers, charts, labels, and footnotes. A missing `image_prompt` blocks preview generation.

### 5. Presentation boundary and notes

`presentation_adapter.py` exposes only `assemble(final_images, speaker_notes, output_path)` plus a read-back verifier. Before invocation it enforces:

- final image count equals slide count;
- final images passed QA;
- speaker-note count equals slide count;
- `selected-style.yaml` contains `selected_by: user`.

The production-image assembler creates a blank 16:9 deck, places one full-slide image per slide, writes real PowerPoint `notesSlides`, saves the PPTX, reopens it, and verifies slide-to-note mapping. It has no APIs for text boxes, shapes, charts, layouts, or image editing. An audit adapter raises if any forbidden presentation operation is requested. A PPTX with only external Markdown notes or without matching `notesSlides` fails.

### 6. Validator

`validate_workflow.py` and the existing P0 validator enforce the same contract at runtime and after the build. They validate state, mode defaults, manifest provenance, candidate completeness, selected-style provenance, slide-spec fields, final-image readiness, presentation call order, and actual notes-slide round-trip. Missing manifest, non-image2 candidates, AI-selected styles, premature presentation calls, native layout objects, and missing notes are hard failures.

## Error handling

- Every hard failure writes `build_status: failed`, an error code/message, and an event in `build-state.yaml`.
- A failed image2 call remains in the manifest with `success: false`; it is never silently replaced.
- Existing artifacts are not deleted by the workflow. A failed run is resumable only after the failed precondition is corrected and the caller starts a new run from the persisted failure state according to the explicit recovery API.
- External Markdown notes without `notesSlides` are insufficient and are reported as a notes round-trip failure.

## Test strategy

TDD starts with failing tests covering the twelve requested regressions:

1. default mode stops at `awaiting_configuration`;
2. uploaded template cannot skip configuration;
3. manual mode creates three candidates;
4. non-image2 candidate generation fails;
5. missing image-generation manifest fails;
6. unselected candidate blocks full preview;
7. `selected_by != user` fails;
8. presentation before final images fails;
9. presentation text/shape operations fail;
10. PPTX without `notesSlides` fails;
11. one execution cannot cross two awaiting states;
12. unavailable image2 fails without fallback.

Additional tests cover YAML persistence, atomic writes, required slide-spec fields, manifest records, final-image count checks, note mapping, and a real manual/guided smoke invocation. The smoke invocation uses the supplied wind Markdown and blue template but stops after printing/storing configuration choices at `awaiting_configuration`; it must create no candidates, previews, final images, or PPTX.

## Out of scope

- Generating or visually tuning a complete 24-slide deck.
- Building a GUI selector.
- Making PPTX body objects editable.
- Treating a template as a source-slide layout map.
