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
- `template_application_mode`: `style-reference` (default), `adaptive-layout`, or `strict-template`.
- `content_density`, `target_duration_minutes`, `language`, `aspect_ratio`, `audience`, `style_confidence`, and `classification_reason`.

`deck-brief.yaml` must include `target_slide_count` and `presentation_goal`, plus source, audience, use-case, language, duration, and output-directory context when available.

When a user supplies a PPTX template, `deck-config.yaml` must also declare:

- `template_source`: the imported PPTX path.
- `template_profile`: `references/deck-library/profiles/<template-name>/style-profile.yaml`.

Before candidate selection, slide specs, previews, or final images, create and validate the profile at that exact path. The profile is a semantic style contract, not a screenshot, source-slide map, or palette-only note. It must contain `color_palette`, `typography`, `spacing`, `composition_language`, `image_treatment`, `chart_style`, `icon_style`, `page_rhythm`, `layout_principles`, and `prohibited_behaviors`. Coordinates and duplicate-slide mappings are optional observations only. If either the profile or its required sections is missing, stop with `build_status: failed`; do not use the template for a full deck.

### Template application modes

Resolve `template_application_mode` before outline or slide generation.

- **style-reference (default):** inherit the template's colors, font language, whitespace, shapes, icons, image treatment, chart language, and rhythm. Do not copy source slides or bind source textbox coordinates. Recompose every page for its current semantics and continue the independent-spec -> text-to-image -> preview-review -> final-image flow.
- **adaptive-layout:** reference page families and broad composition while allowing text boxes and visual elements to move, resize, be deleted, or be added. Change columns, cards, image ratios, charts, flows, arrows, nodes, and architecture structures when content requires it. Content semantics outrank template fidelity.
- **strict-template:** use only when the user explicitly asks for strict brand-template application. Only this mode may use duplicate-slide and inherited text boxes as the primary strategy. It is never the default, and an uploaded PPTX does not constitute confirmation.

In style-reference, use template preview images as style references in each image prompt. State that the model must learn the visual language, not copy source text or exact textbox layout, and must recompose the page. Let the image model handle background, scene, composition, and decoration; render exact Chinese, key numbers, tables, and charts deterministically. Review previews before final generation.

### P0-A configuration selection gate

Run `python scripts/config_gate.py <output>` before creating `outline.md`, slide specs, previews, final images, or `presentation.pptx`.

- When `selection_mode: guided`, display numbered options for `presentation_type`, `visual_style`, `presentation_effect`, `workflow_mode`, `selection_mode`, `template_application_mode`, `output_mode`, `notes_mode`, `target_duration_minutes`, and `content_density`. Use a text prompt when a GUI selector is unavailable. Do not apply the recommendation without a user confirmation.
- Until the user confirms, write `build-status.json` and `config-selection-report.md` with `build_status: awaiting_configuration`, and exit the current generation stage. Do not create `deck-config.confirmed.yaml`.
- After confirmation, write `deck-config.confirmed.yaml`. No downstream stage may run without that file.
- When `workflow_mode: manual`, create 2 to 4 complete candidate packages under `style-candidates/`, display them, and wait. Until the user selects one, write `build_status: awaiting_style_selection` and do not write `selected-style.yaml`.
- After a user selection, write `selected-style.yaml` with `selected_candidate`, `selected_by: user`, `confirmation_timestamp`, and `candidate_profile_path`. `selected_by: ai` or an omitted field is a hard failure.
- `workflow_mode: auto` may skip prompting only when the report records the inferred values and `confirmation_method: auto_inference` in `deck-config.confirmed.yaml`.
- `selection_mode: direct` is valid only when the caller can prove that every required configuration field was explicitly supplied by the user; an uploaded template is not proof of confirmation.

The gate implementation is `scripts/config_gate.py`; downstream code must call `assert_generation_allowed(output, stage)` immediately before every outline, spec, image, PPTX, and publication stage.

If `workflow_mode: auto`, classify the parameters and record the reason. If `workflow_mode: manual`, generate 2 to 4 candidate packages under `style-candidates/`, wait for user selection, and write `selected-style.yaml` only after that selection. Do not generate the full deck before that file exists. `selection_mode: direct` does not skip the manual candidate gate.

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
2. **Template profile gate:** when `template_source` is present, require the matching `style-profile.yaml` and all required sections before any deck-level generation. Treat the profile as the source of truth for page families, title geometry, density, charts, and decoration. Never reduce it to a background image or a color palette.
3. **Brief and outline gate:** read the source, record gaps/assumptions, and create a narrative `outline.md`; do not use loose headings as a deck plan.
4. **Slide-spec gate:** create one `slide-specs/slide-XX.yaml` per page. Each spec includes `page_type`, `title`, `key_message`, `layout`, `visual_style`, `image_prompt`, `source_assets`, `dependencies`, `qa_checklist`, `template_application_mode`, `dominant_visual`, `layout_flexibility`, `visual_inheritance`, and `prohibited_inheritance`. `source_slide_reference` is optional and may be empty. Every analytical page must name a dominant visual or chart requirement. Do not require a source slide.
5. **Data gate:** create `data/metrics.json`, `data/tables.json`, and JSON datasets under `data/chart-data/`. Every key metric has one unique ID; specs and notes reference IDs instead of duplicating numeric literals. Charts are code-rendered from `chart-data`.
6. **Preview gate:** generate one preview image per spec with the selected visual system. Review the ordered set for narrative fit, visual adequacy, density, and family variation. A failed page returns to its own YAML spec before any image or PPTX regeneration.
7. **Typography gate:** create `typography-scale.yaml` and `typography-qa-report.md`. Body text is at least 28 px, chart/table labels at least 24 px, footnotes at least 18 px, and a role stays within plus or minus 10% across pages. Apply the profile's per-family title positions and density limits. Do not shrink text indefinitely; delete, restructure, or split content.
8. **Final-image gate:** after preview approval, generate distinct final images at no less than 1920x1080. Do not label a preview as final.
9. **Speaker-note gate:** for `summary` or `full`, create one `speaker-notes/slide-XX.md` per page. Full notes explain the page instead of copying it, cite metric IDs, include emphasis and transitions, and total approximately `target_duration_minutes`. Create `speaker-notes-report.md`.
10. **PPT assembly gate:** use the selected output-mode adapter. Production-image assembly inserts only final images at full canvas; background-only assembly inserts backgrounds and layout guides; hybrid assembly must expose its actual editable-object contract. Assembly must not rescue an unapproved template shell by adding ordinary native body layout.
11. **Notes round-trip gate:** when notes are written to PPTX, save, reopen, read them back, and compare every page with `speaker-notes/`. Missing, shifted, or changed notes fail the build.
12. **Final gate:** produce `visual-qa-report.md`, `typography-qa-report.md`, `data-qa-report.md`, `speaker-notes-report.md`, and `generation-report.md`; run both validators before marking the build complete.

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
├── deck-config.confirmed.yaml             # required after P0-A confirmation
├── build-status.json                      # awaiting_* blocks all downstream stages
├── config-selection-report.md
├── selected-style.yaml                 # required for manual mode
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
2a. Never let an imported template force strict-template; missing mode always resolves to style-reference.
3. Never enter formal generation in manual mode without `selected-style.yaml`.
4. Never use conflicting visual systems across pages.
5. Never allow body text below 28 px or chart/table labels below 24 px.
6. Never duplicate key numeric literals instead of referencing `metrics.json`.
7. Never use an image model to fabricate exact data or long Chinese text.
8. Never publish when any gate, notes round-trip, or validator fails.
9. Never use ordinary presentation layout as a degraded fallback for production-image.
10. Never claim unavailable tools, generated files, editable objects, or successful checks.
11. Never use an imported template without its matching `style-profile.yaml`.
12. In style-reference, never use full-page duplicate-slide mappings, source text, or fixed source textbox coordinates.
13. When content exceeds a template family's capacity, recompose or split the page; do not shrink type or force inherited containers.
14. In strict-template only, and only after explicit user confirmation, may duplicate-slide and inherited textboxes be the primary strategy.
15. Never generate an outline, slide spec, image, PPTX, or publication without `deck-config.confirmed.yaml`.
15. Never auto-confirm a guided configuration or select candidate-a in manual mode.
16. Never continue manual mode when `selected-style.yaml` is missing or `selected_by` is not `user`.
18. Never infer that an uploaded template is a configuration, style, or strict-template confirmation.

## P1 Scope

P0 reserves interfaces and directories for large-scale template retrieval, a graphical style selector, automatic template learning, complete hybrid-editable authoring, and university brand adaptation. These are not required for v1.1.0.

## References and Templates

- Read `references/p0-contract.md` for schemas, mode-specific examples, and gate details.
- Use `scripts/template_policy.py` to validate template application modes and slide composition semantics before generation.
- For any supplied PPTX, read `references/deck-library/profiles/<template-name>/style-profile.yaml` after creating it and before selecting a page family.
- Start from `templates/deck-config.yaml`, `templates/deck-brief.yaml`, `templates/typography-scale.yaml`, `templates/slide-spec.yaml`, `templates/speaker-note.md`, `templates/metrics.json`, `templates/tables.json`, and `templates/layout-guide.json`.
- Run `python scripts/validate_p0.py <output>` for P0 contracts and `python scripts/validate_pipeline.py <output>` for the legacy production-image contract.
