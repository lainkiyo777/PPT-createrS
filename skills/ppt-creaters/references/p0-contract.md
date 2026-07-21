# P0 Contract Reference

This reference is the executable contract behind `SKILL.md` v1.2.0. It keeps detailed schemas out of the trigger document while preserving deterministic validation.

## Configuration

`deck-config.yaml` uses one scalar value for each of these keys:

```yaml
presentation_type: technical-report
visual_style: technology-dark
presentation_effect: keynote
workflow_mode: manual
selection_mode: guided
template_application_mode: style-reference
output_mode: production-image
notes_mode: full
content_density: medium
target_duration_minutes: 20
language: zh-CN
aspect_ratio: 16:9
audience: technical-management
style_confidence: 0.92
classification_reason: >
  Explain the classification using source evidence.
```

The validator accepts only the enumerations documented in `SKILL.md`. `style_confidence` is in `[0, 1]`; `target_duration_minutes` is positive; `aspect_ratio` is `16:9`.

`deck-brief.yaml` must include at least:

```yaml
target_slide_count: 12
presentation_goal: Explain the decision and next action.
source_material: materials/source.md
audience: technical-management
use_case: formal-report
```

## Imported template profile gate

When `deck-config.yaml` contains `template_source`, it must also contain `template_profile`. The profile path is deterministic:

```text
references/deck-library/profiles/<template-name>/style-profile.yaml
```

`<template-name>` is the imported PPTX filename without its extension. The profile must be created before style candidates, slide specs, previews, or final images. It is a style profile, not a source-slide coordinate map, and must contain:

```yaml
color_palette: {}
typography: {}
spacing: {}
composition_language: {}
image_treatment: {}
chart_style: {}
icon_style: {}
page_rhythm: {}
layout_principles: []
prohibited_behaviors: []
```

Coordinates, duplicate-slide mappings, and inherited text boxes are optional observations only; they are not the profile's design contract.

The profile must describe observed template behavior and constraints, not merely repeat a screenshot, a background filename, or a palette. A missing `template_profile`, missing profile file, wrong profile path, or missing section is a hard failure. The existing deck must not proceed to page generation while this gate fails.

## P0-A configuration and interaction gate

`deck-config.confirmed.yaml` is required before outline, slide specs, previews, final images, or PPTX. The orchestration gate is implemented by `scripts/workflow_runner.py` and records durable state in `build-state.yaml`. `build-status.json` is only a compatibility mirror.

For `selection_mode: guided`, the gate must display numbered choices for these fields and wait for explicit user confirmation:

```text
presentation_type
visual_style
presentation_effect
template_application_mode
output_mode
notes_mode
target_duration_minutes
content_density
```

Display `workflow_mode: manual` and `selection_mode: guided` as the defaults. Only an explicit user-supplied `workflow_mode: auto` plus `selection_mode: direct` pair opts out.

If no confirmation is received, the only valid state is:

```text
build_status: awaiting_configuration
```

A GUI selector is optional. A numbered text prompt is the required fallback. Recommendations may be displayed but cannot be accepted automatically.

For `workflow_mode: manual`, call `image2` and create exactly `candidate-a`, `candidate-b`, and `candidate-c`. Each contains `cover.png`, `section.png`, `content.png`, `result.png`, and `style-profile.yaml`. The candidates interpret the same template as university research clean, technology launch, and data technical report respectively. Then wait for a user choice. Before that choice the only valid state is:

```text
build_status: awaiting_style_selection
```

Only a user choice may create `selected-style.yaml`, which must include:

```yaml
selected_candidate: candidate-b
selected_by: user
confirmation_timestamp: 2026-07-21T00:00:00+00:00
candidate_profile_path: style-candidates/candidate-b/style-profile.yaml
```

`selected_by: ai`, missing confirmation metadata, or an uploaded template must never satisfy this gate. `workflow_mode: auto` may skip prompting only when `deck-config.confirmed.yaml` records `confirmation_method: auto_inference` and the selection report records the inferred values. `selection_mode: direct` requires proof that every required field was explicitly provided by the user.

Every image2 call must be appended to `image-generation-manifest.json` with `tool_name`, `prompt_path`, `reference_images`, `output_path`, `timestamp`, and `status`. Candidate validation fails if the manifest is missing, a candidate output lacks a successful image2 record, or a different tool created it. An unavailable image2 adapter is a hard failure; `presentation` is never a fallback image generator.

## Template application mode

`template_application_mode` defaults to `style-reference` and must be resolved before page generation.

- `style-reference`: inherit colors, font language, whitespace, shapes, icons, image treatment, chart language, and visual rhythm. Do not duplicate source slides or bind source textbox coordinates. Recompose every page from its semantic content and continue the image-first flow.
- `adaptive-layout`: reference page families and broad composition only. Move, resize, delete, and add text boxes; change columns, cards, image ratios; and add charts, flows, arrows, nodes, or architecture structures. Content semantics outrank template fidelity.
- `strict-template`: enable only when the user explicitly selects strict brand-template use. Only this mode may use duplicate-slide and inherited text boxes as the primary strategy. It is never the default, and an uploaded PPTX is not confirmation.

A confirmed strict choice must record `template_application_mode_selected_by: user` or an explicit user field in `deck-config.confirmed.yaml`.

## Manual selection Gate

Manual mode requires:

```text
style-candidates/
├── candidate-a/
│   ├── style-profile.yaml
│   ├── cover.png
│   ├── section.png
│   ├── content.png
│   └── result.png
└── candidate-b/ ...
selected-style.yaml
```

There must be exactly three candidates. The user confirmation is represented by `selected-style.yaml`; full preview generation is blocked until it exists and `selected_by` is `user`. Candidate generation ends the invocation at `awaiting_style_selection`.

## Style-reference image-first rule

In `style-reference`, generate independent slide specs from the outline, choose a `dominant_visual` for each page, and build prompts from the style profile plus approved template preview references. Preview images must be reviewed before `final-images`. The model may generate backgrounds, composition, decorative geometry, and scene imagery; exact Chinese, key numbers, tables, and charts must be deterministic overlays or code-rendered assets.

## Typography

The default scale is:

| Role | Minimum | Preferred | Maximum |
| --- | ---: | ---: | ---: |
| cover_title | 72 | 84 | 92 |
| section_title | 60 | 68 | 76 |
| page_title | 46 | 52 | 56 |
| key_metric | 48 | 60 | 72 |
| group_title | 32 | 35 | 38 |
| body | 28 | 31 | 34 |
| chart_label | 24 | 26 | 28 |
| footnote | 18 | 20 | 21 |

The `typography-scale.yaml` canvas is 1920×1080. Every slide spec references roles rather than ad-hoc pixel sizes. A role may not drift by more than ±10% within a section. A page may use at most four font sizes unless the typography report documents why. Overflow is solved by editing content or splitting the page, never by shrinking below the minimum.

## Data and chart lineage

`data/metrics.json` is a map of unique metric IDs:

```json
{
  "patchtst_full_speed_mae": {
    "value": 1.3299,
    "unit": "m/s",
    "precision": 4,
    "source": "experiment-results.csv",
    "slides": [12, 15, 24]
  }
}
```

`data/tables.json` stores table records. Each chart has a JSON dataset under `data/chart-data/`. Slide specs and notes reference metric IDs; they must not repeat a key number as an independent source. A data QA report must identify missing keys, conflicting values, invalid precision, and chart datasets that are not used by code rendering.

## Slide spec

Use one `slide-specs/slide-XX.yaml` per page:

```yaml
slide_number: 8
page_type: architecture
title: 阶段一先预测未来风况
key_message: 为功率映射模型提供未来风速和风向输入
font_roles:
  title: page_title
  body: body
  metrics: key_metric
layout:
  structure: horizontal-process
  columns: 4
  reuse_mode: new-composition
visual_style:
  profile: references/deck-library/profiles/<template-name>/style-profile.yaml
  semantic_override: content chooses composition
visual:
  style: technology-dark
  effect: keynote
  glow_level: medium
  contrast_level: dramatic
image_prompt: >-
  Learn the imported template's visual language and approved preview references;
  do not copy source Chinese, source text, or exact textbox layout. Recompose the
  scene for this page's semantics. The image model owns background, composition,
  decoration, and scene imagery; deterministic code owns exact Chinese, numbers,
  tables, and chart labels.
style_reference_prompt: >-
  Analyze and inherit the reference template's colors, typography language,
  whitespace, graphic vocabulary, photography, and page rhythm. Do not copy pages.
reference_images:
  - references/template-previews/page-01.png
dominant_visual: Future wind field forecast process
deterministic_text_overlay: Exact Chinese title, labels, metric values, sources, and footnotes.
deterministic_chart_overlay: Render chart axes, series, labels, and legends from data/chart-data by code.
source_slide_reference: null
source_assets: []
dependencies: []
referenced_metrics:
  - prediction_horizons
speaker_notes:
  file: ../speaker-notes/slide-08.md
qa_checklist:
  - title_not_overflow
  - body_font_above_minimum
  - metrics_match_source
  - notes_present
```

The validator checks field presence, including the six required image/style/overlay fields, contiguous filenames, slide count, metric references, and notes-file linkage. A missing `image_prompt` blocks previews. It does not claim that visual judgment can be reduced to regex; visual review remains a required Gate.

## Speaker notes

For `summary` and `full`, each page has a matching Markdown note:

```yaml
slide_number: 8
purpose: Explain why the first stage forecasts future wind conditions.
estimated_duration_seconds: 50
referenced_metrics:
  - prediction_horizons
```

The Markdown body contains `## 建议讲稿`, `## 重点强调`, and page transitions when applicable. Notes explain beyond the visible text, use metric IDs, avoid exaggerated conclusions, and sum approximately to the configured duration. `full` notes are written into real PowerPoint `notesSlides`. Reopen the saved PPTX and verify notesSlides count, slide relationship mapping, and exact Markdown text page by page. External Markdown alone never passes.

## Output mode details

`production-image` requires one final PNG per page, `final-images-qa.json`, and `presentation.pptx`. Call `presentation` only after final-image and speaker-note counts equal slide count, final-image QA passes, and `selected-style.yaml` says `selected_by: user`. Presentation may only create a blank 16:9 deck, insert one full-slide image per page, write notes, save, and reopen. Native text boxes, shapes, charts, layout design, image modification, and fallback page generation are forbidden.

`hybrid-editable` is a contract, not permission to claim unsupported editability. The builder must list which objects are native and which remain images, and QA must inspect both classes.

`background-only` requires one background and one JSON layout guide per page plus `presentation-backgrounds.pptx`. The guide keeps coordinates and semantic regions editable while the background remains decorative. Long body copy and immutable key figures are forbidden in background images.

## Gate reports

At the end of a successful build, reports must record:

```text
Gate 1 configuration: pass
Gate 2 outline: pass
Gate 3 slide specs: pass
Gate 4 data: pass
Gate 5 previews: pass
Gate 6 typography: pass
Gate 7 final images: pass
Gate 8 speaker notes: pass
Gate 9 PPT assembly: pass
Gate 10 notes round-trip: pass
Gate 11 final review: pass
```

Any failed gate writes `build_status: failed`, preserves diagnostic artifacts, and prevents the final publication step.
