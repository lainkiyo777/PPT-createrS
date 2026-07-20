# Final QA Checklist

## Contract and counts

- [ ] The output root contains only the required seven entries.
- [ ] `slide-specs/` contains one contiguous Markdown file per page.
- [ ] Preview count equals slide count.
- [ ] Final-image count equals slide count.
- [ ] Preview and final filenames map one-to-one to specs.
- [ ] No final file is byte-identical to its preview.
- [ ] Every final image is a readable 16:9 PNG of at least 1920×1080.

## Visual and content quality

- [ ] Every title wraps intentionally; important titles remain on one line where specified.
- [ ] Body copy, chart labels, axes, legends, sources, and notes are legible at presentation scale.
- [ ] Font hierarchy has no small-text risk.
- [ ] No visual element or text is cropped, clipped, or beyond safe margins.
- [ ] Key figures and claims match checked source material.
- [ ] User-provided screenshots and brand icons remain faithful to their source treatment.
- [ ] Colors, typography, imagery, charts, spacing, borders, radius, and shadows follow one visual system.
- [ ] Correct final versions are used in correct slide order.

## PPTX packaging

- [ ] Deck ratio is 16:9.
- [ ] PPTX page count equals final-image count.
- [ ] Every slide contains exactly one picture covering the full canvas.
- [ ] No slide contains native text, shapes, tables, charts, groups, or corrective overlays.
- [ ] Images are not distorted or selectively cropped.
- [ ] `presentation.pptx` opens normally.

## Reports and deterministic gate

- [ ] `qa-report.md` records page count, image counts, aspect ratio, missing files, font-size risk, and overflow results.
- [ ] `generation-report.md` records the actual tools, global visual system, spec/preview/final versions, and stage status.
- [ ] `scripts/validate_pipeline.py` exits 0 and prints the PASS result.
- [ ] Completion is reported only after the deterministic gate passes.