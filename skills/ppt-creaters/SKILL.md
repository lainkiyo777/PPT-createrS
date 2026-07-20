---
name: ppt-creaters
description: Use when turning a topic, document, or outline into a configurable presentation with controlled text, data, typography, speaker notes, and verifiable PPT output.
---

# PPT Creaters

Release: 1.1.0

## Overview

This Skill is a configurable PPT production orchestrator. It supports image-first production, a hybrid-editable contract, and background-only output while keeping content planning, typography, data, notes, and QA explicit.

Core principle: **先参数化，再结构化；先确定性文字和数据，再视觉化。**

The image adapter may create backgrounds, scenes, decorative visuals, and concept art. Code or a deterministic renderer must create Chinese titles, body text, key numbers, tables, charts, labels, page numbers, sources, and footnotes.

## When to Use

Use this Skill when a topic, document, rough outline, or dataset must become a controlled presentation and the user needs one or more of the following: a selectable presentation type/style/effect, auto or manual workflow, production-image, hybrid-editable, or background-only output, speaker notes, deterministic metrics/charts, font-size guarantees, or a verifiable PPTX.

Do not use it for a one-title edit, light copy polishing, or a tiny format change to an existing complete deck.

## Required Configuration

Before page generation, create both `deck-config.yaml` and `deck-brief.yaml`.

`deck-config.yaml` must declare:

- `presentation_type`: `research-report`, `technical-report`, `introductory`, `academic-defense`, `product-solution`, `executive-summary`, or `training-course`.
- `visual_style`: `academic-clean`, `university-formal`, `technology-dark`, `industrial-technical`, `business-data`, `light-modern`, or `institutional-red`.
- `presentation_effect`: `keynote`, `formal-report`, `academic`, `storytelling`, `dashboard`, `documentary`, or `minimal`.
- `workflow_mode`: `auto` or `manual`.
- `selection_mode`: `direct` or `guided`.
- `output_mode`: `production-image`, `hybrid-editable`, or `background-only`.
- `notes_mode`: `none`, `summary`, or `full`.
- `content_density`, `target_duration_minutes`, `language`, `aspect_ratio`, `audience`, `style_confidence`, and `classification_reason`.

`deck-brief.yaml` must include `target_slide_count` and `presentation_goal`, plus source, audience, use-case, language, duration, and output-directory context when available.

If `workflow_mode: auto`, classify the parameters and record the reason. If `workflow_mode: manual` and `selection_mode: guided`, generate 2–4 candidate packages under `style-candidates/`, wait for confirmation, and write `selected-style.yaml`. Do not generate the full deck before that file exists. `selection_mode: direct` may proceed when the user explicitly supplied all parameters.

## Output Mode Contracts

### production-image

Generate one complete approved final PNG per slide and assemble `presentation.pptx` with one full-slide image per page. Do not recreate body text, tables, charts, screenshots, or icons as native PowerPoint objects.

### hybrid-editable

Keep the mode contract and output interfaces explicit: visual backgrounds and complex illustrations may be images, while titles, body copy, metrics, tables, charts, and notes are deterministic editable objects. Do not claim full hybrid editability unless every editable object is actually implemented and validated.

### background-only

Generate only `backgrounds/slide-XX-bg.png`, `layout-guides/slide-XX-layout.json`, and `presentation-backgrounds.pptx`. Background images must not contain long body copy or immutable key numbers. Layout guides must include `slide_number`, `page_type`, `title_area`, and `subtitle_area`.

## End-to-End Workflow and Gates

Advance only when the previous gate passes. A failed gate yields `build_status: failed` and stops publication.

1. **Configuration gate:** validate enums, required fields, style confidence, aspect ratio, duration, and mode prerequisites.
2. **Brief and outline gate:** read the source, record gaps/assumptions, and create a narrative `outline.md`; do not use loose headings as a deck plan.
3. **Slide-spec gate:** create one `slide-specs/slide-XX.yaml` per page. Each spec includes the required fields in `templates/slide-spec.yaml` and references font roles, metrics, source assets, speaker notes, dependencies, and acceptance checks.
4. **Data gate:** create `data/metrics.json`, `data/tables.json`, and JSON datasets under `data/chart-data/`. Every key metric has one unique ID; specs and notes reference IDs instead of duplicating numeric literals. Charts are code-rendered from `chart-data`.
5. **Preview gate:** generate one preview image per spec with the selected visual system. Review the ordered set. A failed page returns to its own YAML spec before any image or PPTX regeneration.
6. **Typography gate:** create `typography-scale.yaml` and `typography-qa-report.md`. Body text is at least 28 px, chart/table labels at least 24 px, footnotes at least 18 px, and a role stays within ±10% across pages. Do not shrink text indefinitely; delete, restructure, or split content.
7. **Final-image gate:** after preview approval, generate distinct final images at no less than 1920×1080. Do not label a preview as final.
8. **Speaker-note gate:** for `summary` or `full`, create one `speaker-notes/slide-XX.md` per page. Full notes explain the page instead of copying it, cite metric IDs, include emphasis and transitions, and total approximately `target_duration_minutes`. Create `speaker-notes-report.md`.
9. **PPT assembly gate:** use the selected output-mode adapter. Production-image assembly inserts only final images at full canvas; background-only assembly inserts backgrounds and layout guides; hybrid assembly must expose its actual editable-object contract.
10. **Notes round-trip gate:** when notes are written to PPTX, save, reopen, read them back, and compare every page with `speaker-notes/`. Missing, shifted, or changed notes fail the build.
11. **Final gate:** produce `visual-qa-report.md`, `typography-qa-report.md`, `data-qa-report.md`, `speaker-notes-report.md`, and `generation-report.md`; run both validators before marking the build complete.

## Deterministic Content Rules

- Do not ask an image model to render exact Chinese copy, key figures, tables, axes, chart labels, professional terms, page numbers, sources, or footnotes.
- Do not hand-write the same metric in multiple artifacts. Resolve it from `metrics.json` by unique key.
- A data conflict, missing source, missing metric, missing chart dataset, invalid font role, missing note, or failed read-back is a hard build failure.
- Never invent an external image/PPT tool, command, API, output file, or successful result. If an adapter is unavailable, report the blocked state and preserve executable prompts and manifests only.

## Fixed v1.1 Output Contract

```text
output/
├── deck-config.yaml
├── deck-brief.yaml
├── selected-style.yaml                 # required for manual + guided
├── outline.md
├── typography-scale.yaml
├── style-candidates/                   # required for manual + guided
├── slide-specs/slide-XX.yaml
├── speaker-notes/slide-XX.md           # required for summary/full
├── data/metrics.json
├── data/tables.json
├── data/chart-data/*.json
├── charts/
├── backgrounds/                        # background-only
├── layout-guides/                      # background-only
├── preview-images/
├── final-images/                       # production-image
├── overview/overview.png
├── presentation.pptx
├── visual-qa-report.md
├── typography-qa-report.md
├── data-qa-report.md
├── speaker-notes-report.md
└── generation-report.md
```

The legacy v1.0 fixed image-only validator remains available as `scripts/validate_pipeline.py`. The P0 contract validator is `scripts/validate_p0.py`; it is dependency-free and prints `build_status: failed` on any hard failure.

## Non-Negotiable Rules

1. Never generate images directly from a rough outline.
2. Never omit independent slide specs.
3. Never enter formal generation in manual-guided mode without `selected-style.yaml`.
4. Never use conflicting visual systems across pages.
5. Never allow body text below 28 px or chart/table labels below 24 px.
6. Never duplicate key numeric literals instead of referencing `metrics.json`.
7. Never use an image model to fabricate exact data or long Chinese text.
8. Never publish when any gate, notes round-trip, or validator fails.
9. Never use ordinary presentation layout as a degraded fallback for production-image.
10. Never claim unavailable tools, generated files, editable objects, or successful checks.

## P1 Scope

P0 reserves interfaces and directories for large-scale template retrieval, a graphical style selector, automatic template learning, complete hybrid-editable authoring, and university brand adaptation. These are not required for v1.1.0.

## References and Templates

- Read `references/p0-contract.md` for schemas, mode-specific examples, and gate details.
- Start from `templates/deck-config.yaml`, `templates/deck-brief.yaml`, `templates/typography-scale.yaml`, `templates/slide-spec.yaml`, `templates/speaker-note.md`, `templates/metrics.json`, `templates/tables.json`, and `templates/layout-guide.json`.
- Run `python scripts/validate_p0.py <output>` for P0 contracts and `python scripts/validate_pipeline.py <output>` for the legacy production-image contract.
