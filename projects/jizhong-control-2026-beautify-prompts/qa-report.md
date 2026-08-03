# QA report — template-reference image-first demo

## Deterministic checks

- Reference images: 14, numbered 01–14 — pass
- Preview images: 14, numbered 01–14 — pass
- Preview dimensions: 1672×941 (16:9) — pass
- PPTX slide count: 14 — pass
- PPTX page order: 01–14 — pass
- PPTX structure: one full-slide picture per page; no native body text/table/chart objects — pass
- Notes: 14 slide notes parts — pass

## Visual review note

The blue template language is consistent across the set and page compositions vary by semantic purpose. The visual review was performed from the preview contact sheet and rendered deck montage.

## Known issue retained for follow-up

The image model rendered the printed footer page number on slide 14 as `9` inside the artwork. The PPTX page order and file numbering remain correct. This is a content-in-image QA issue, not a PPTX ordering issue; a production rerun must correct the slide prompt/final image before release.
