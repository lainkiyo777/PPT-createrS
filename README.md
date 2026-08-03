# PPT Creaters

Version 2.1.0 of the image-first Codex Skill for producing presentation decks.

## Included

- `skills/ppt-creaters/`: reusable Codex Skill and its templates, contracts, tests, and validators.
- `materials/整合版PPT内容大纲.md`: source Markdown used for the included deck.
- `output/`: the verified 24-slide v1.0.0 image-first production artifact, including outline, independent slide specs, preview images, final images, PPTX, QA report, and generation report.
- `skills/ppt-creaters/templates/` and `scripts/validate_p0.py`: the P0 configuration, typography, data, notes, output-mode, and gate contracts.
- `projects/jizhong-control-2026-beautify-prompts/`: the 14-page template-reference regression artifact that learns a blue PPTX template, generates per-page image prompts/previews, and assembles an image-only PPTX.

## Pipeline

```text
source → outline → independent slide specs → preview images → preview review
→ final images → image-only PPTX assembly → QA and deterministic validation
```

When a template is supplied for visual reference, v2.1 adds an explicit route:

```text
template PPTX → style profile + per-page reference images
→ semantic re-composition → host image_gen previews
→ review → high-resolution final images → full-slide image-only PPTX
```

The template is not silently treated as a duplicate-slide layout. `style-reference` is the default; `strict-template` requires explicit user selection. Run `python skills/ppt-creaters/scripts/template_reference_pipeline.py validate-demo projects/jizhong-control-2026-beautify-prompts` to check the checked-in example.

The included `presentation.pptx` is intentionally image-only: each slide is one approved final image covering the full 16:9 canvas.
