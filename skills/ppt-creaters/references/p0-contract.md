# P0 Contract Reference

This reference is the executable contract behind `SKILL.md` v1.1.0. It keeps detailed schemas out of the trigger document while preserving deterministic validation.

## Configuration

`deck-config.yaml` uses one scalar value for each of these keys:

```yaml
presentation_type: technical-report
visual_style: technology-dark
presentation_effect: keynote
workflow_mode: manual
selection_mode: guided
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

## Manual selection Gate

Manual + guided mode requires:

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

There must be 2–4 candidates. The user confirmation is represented by `selected-style.yaml`; formal page generation is blocked until it exists. Auto or direct mode can skip this gate only when their parameters are already resolved.

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
visual:
  style: technology-dark
  effect: keynote
  glow_level: medium
  contrast_level: dramatic
image_prompt: Describe the complete visual composition with exact image constraints.
source_assets: []
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

The validator checks field presence, contiguous filenames, slide count, metric references, and notes-file linkage. It does not claim that visual judgment can be reduced to regex; visual review remains a required gate.

## Speaker notes

For `summary` and `full`, each page has a matching Markdown note:

```yaml
slide_number: 8
purpose: Explain why the first stage forecasts future wind conditions.
estimated_duration_seconds: 50
referenced_metrics:
  - prediction_horizons
```

The Markdown body contains `## 建议讲稿`, `## 重点强调`, and page transitions when applicable. Notes explain beyond the visible text, use metric IDs, avoid exaggerated conclusions, and sum approximately to the configured duration. `full` notes are written into PPTX speaker notes, then read back from the saved PPTX and compared page by page.

## Output mode details

`production-image` requires one final PNG per page and `presentation.pptx`. It is intentionally non-editable and must use one full-slide picture per page.

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
