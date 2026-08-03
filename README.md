# PPT Creaters

Version 2.1.0 — an auditable, image-first Codex Skill for producing PowerPoint decks from Markdown, documents, rough outlines, data, or an existing PPTX template.

## What is included

- `skills/ppt-creaters/`: the reusable Skill, contracts, templates, adapters, tests, and validators.
- `materials/`: source Markdown and the v1 image-first reference material.
- `output/`: the canonical image-first output example with outline, slide specs, previews, final images, PPTX, and QA reports.
- `projects/jizhong-control-2026-beautify-prompts/`: a 14-page template-reference regression artifact with extracted reference slides, per-page prompts, preview images, and an image-only PPTX.

## Core production flow

```text
source → brief → outline → independent slide specs
→ style profile → preview images → preview review
→ final images → full-slide image-only PPTX → QA
```

When a template is supplied for visual reference, the v2.1 route is:

```text
template PPTX → style-profile.yaml + reference-slides/source-slide-XX.png
→ semantic re-composition → host image_gen previews
→ review → high-resolution final images → full-slide image-only PPTX
```

The default `template_application_mode` is `style-reference`: inherit the template's visual language, but redesign each page for its own meaning. `strict-template` is allowed only after the user explicitly selects it; uploading a PPTX never counts as confirmation.

## Quick start

Run the Skill from the repository root. The runner is intentionally one-stage-at-a-time and persists its state in the output directory.

### 1. Create a task directory

```powershell
New-Item -ItemType Directory -Force output/my-deck | Out-Null
Copy-Item skills/ppt-creaters/templates/deck-config.yaml output/my-deck/deck-config.yaml
```

Create `output/my-deck/deck-brief.yaml` with the source material and audience. At minimum, identify:

```yaml
source_material: materials/整合版PPT内容大纲.md
presentation_goal: technical review and decision support
audience: technical-management
language: zh-CN
target_slide_count: 14
delivery_mode: production
output_directory: output/my-deck
```

Edit `deck-config.yaml` before running. The important fields are:

```yaml
presentation_type: technical-report
visual_style: technology-dark
presentation_effect: keynote
workflow_mode: manual       # manual | auto | direct
selection_mode: guided      # guided | direct
template_application_mode: style-reference
output_mode: production-image
visual_generator: image_gen
notes_mode: full
content_density: medium
target_duration_minutes: 20
```

Then invoke the persistent runner:

```powershell
python skills/ppt-creaters/scripts/workflow_runner.py output/my-deck
```

If the runner stops at a human Gate, complete the requested artifact and run the same command again. It must not silently choose a style or continue through a future Gate.

## Configuration and human Gates

Unless the user explicitly provides `workflow_mode: auto` and `selection_mode: direct`, the first run defaults to `manual` + `guided` and stops at `awaiting_configuration`. The configuration confirmation must include:

- presentation type;
- visual style;
- presentation effect;
- template application mode;
- output mode;
- notes mode;
- target duration;
- content density.

Guided mode writes `deck-config.pending.yaml` and waits for a user-confirmed `deck-config.confirmed.yaml`. Manual mode then generates three real visual candidates and waits for `selected-style.yaml` with `selected_by: user`. Candidate A is never auto-selected.

The next mandatory handoff is one independent spec per page. Do not generate previews directly from a rough outline. After preview generation, review the complete set; a failed page returns to its slide spec/prompt. Only approved previews may proceed to distinct final images and PPTX assembly.

## Using a PPTX template as a reference

1. Import the PPTX and create `references/deck-library/profiles/<template-name>/style-profile.yaml` before page generation.
2. Export `reference-slides/source-slide-XX.png` for visual reference.
3. Keep exact source text, key numbers, tables, and charts in the slide specs or deterministic overlays.
4. Let each page choose a `dominant_visual`: architecture, comparison chart, process flow, timeline, scene, or result view.
5. Prompt the host image generator to learn the colors, typography language, spacing, geometry, and rhythm; explicitly prohibit copying source text and exact source textbox coordinates.
6. Recompose pages according to current content. Use `adaptive-layout` when the template's page family is useful but the number of cards, columns, nodes, arrows, or charts must change.

Read [the v2.1 template-reference contract](skills/ppt-creaters/references/template-reference-image-pipeline.md) for the complete route and failure policy.

## Visual and PPT tool boundary

`visual_generator` names a real adapter supplied by the Codex host. Use `image_gen` when the host exposes the image-generation capability; use `image2` only when the host explicitly provides an adapter with that name. The Skill records the tool name, version, prompt, references, output path, timestamp, and status.

The repository does not invent image-model APIs, CLI commands, or model results. If no image adapter is available, the run must fail clearly and return prompts, filenames, and a task list. The PPT adapter is also host-provided; if unavailable, output a truthful assembly checklist instead of a fabricated PPTX.

## Canonical output contract

Production output must contain:

```text
output/
├── outline.md
├── slide-specs/slide-01.yaml
├── slide-specs/slide-02.yaml
├── preview-images/slide-01.png
├── final-images/slide-01.png
├── presentation.pptx
├── qa-report.md
└── generation-report.md
```

The image-first assembler creates a blank 16:9 deck and inserts exactly one approved final image per slide, full-slide. It does not re-layout body text, tables, charts, screenshots, or icons inside PowerPoint.

## Validation

Run the full test suite and the relevant output checks:

```powershell
python -m unittest discover -s skills/ppt-creaters/tests -v
python skills/ppt-creaters/scripts/validate_pipeline.py output/my-deck
python skills/ppt-creaters/scripts/validate_p0.py output/my-deck
python skills/ppt-creaters/scripts/template_reference_pipeline.py validate-output output/my-deck --slide-count 14
```

For the checked-in template-reference demo:

```powershell
python skills/ppt-creaters/scripts/template_reference_pipeline.py validate-demo projects/jizhong-control-2026-beautify-prompts
```

The demo intentionally reuses approved preview assets as its image source so the liked visual result remains reproducible. A production run must generate a separate `final-images/` set; a preview must never be labelled as a high-resolution final asset.

## Troubleshooting

- `awaiting_configuration`: confirm all required fields in `deck-config.confirmed.yaml`; the runner is correctly paused.
- `awaiting_style_selection`: inspect the three candidate packages and create `selected-style.yaml` only after user choice.
- missing `image-generation-manifest.json`: the visual adapter was not called or its provenance is incomplete.
- preview/final count mismatch: create contiguous `slide-XX.png` files for every page; do not skip a page.
- template profile missing: generate the required `style-profile.yaml` before any preview.
- image or PPT adapter unavailable: stop and use the emitted prompts/task list; do not substitute presentation layout or screenshots.

## Reference files

- [Skill contract](skills/ppt-creaters/SKILL.md)
- [P0 contract](skills/ppt-creaters/references/p0-contract.md)
- [Template-reference image pipeline](skills/ppt-creaters/references/template-reference-image-pipeline.md)
- [v2.1 process evidence](docs/p0/v2.1-template-reference-process.md)
- [14-page demo prompts](projects/jizhong-control-2026-beautify-prompts/slide-prompts/slide-01.md)
- [Demo presentation](projects/jizhong-control-2026-beautify-prompts/presentation.pptx)
