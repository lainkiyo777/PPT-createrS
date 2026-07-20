# PPT Creaters

Version 1.1.0 of the image-first Codex Skill for producing presentation decks.

## Included

- `skills/ppt-creaters/`: reusable Codex Skill and its templates, checklists, tests, and validator.
- `materials/整合版PPT内容大纲.md`: source Markdown used for the included deck.
- `output/`: the verified 24-slide v1.0.0 image-first production artifact, including outline, independent slide specs, preview images, final images, PPTX, QA report, and generation report.
- `skills/ppt-creaters/templates/` and `scripts/validate_p0.py`: the v1.1.0 P0 configuration, typography, data, notes, output-mode, and gate contracts.

## Pipeline

```text
source → outline → independent slide specs → preview images → preview review
→ final images → image-only PPTX assembly → QA and deterministic validation
```

The included `presentation.pptx` is intentionally image-only: each slide is one approved final image covering the full 16:9 canvas.
