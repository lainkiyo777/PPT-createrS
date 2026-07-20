# PPT Creaters

Version 1.0.0 of the image-first Codex Skill for producing presentation decks.

## Included

- `skills/ppt-creaters/`: reusable Codex Skill and its templates, checklists, tests, and validator.
- `materials/整合版PPT内容大纲.md`: source Markdown used for the included deck.
- `output/`: the complete 24-slide image-first production artifact, including outline, independent slide specs, preview images, final images, PPTX, QA report, and generation report.

## Pipeline

```text
source → outline → independent slide specs → preview images → preview review
→ final images → image-only PPTX assembly → QA and deterministic validation
```

The included `presentation.pptx` is intentionally image-only: each slide is one approved final image covering the full 16:9 canvas.
