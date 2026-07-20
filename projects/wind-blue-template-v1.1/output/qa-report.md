status: pass

# QA report

## Output integrity

- Expected slide count: 24
- Final PPTX slide count: 24
- Preview image count: 24
- Final image count: 24
- Missing preview/final files: none
- Preview dimensions: [(1280, 720)]
- Final dimensions: [(1920, 1080)]
- Canvas ratio: 16:9

## Production-image contract

- Every final page contains exactly one full-slide image at (0, 0, 1280, 720).
- Final image resolution is 1920×1080; previews are distinct 1280×720 renders.
- Final PPTX is assembled from `final-images/slide-XX.png`; no body text, table, chart, screenshot, or icon was rebuilt as native PowerPoint content.

## Typography and overflow

- Body role minimum: 28px; preferred: 30px.
- Chart/table label minimum: 24px; preferred: 26px.
- Cover title “短时功率预测模型” is kept on one line within its title role.
- Artifact-tool structure QA: pass; 0 issues.
- Official `slides_test.py` probe was attempted but could not complete because its Windows JSON path handoff emitted an invalid escape; image-only full-canvas placement was therefore checked directly with artifact-tool.

## Source and template fidelity

- Source Markdown: `input/整合版PPT内容大纲.md`
- Template audit: 11 source slides inspected.
- Official template-plan check: pass.
- Official template-fidelity check on the edited template author deck: pass.
- Full test and OpenOA clean test remain separate evaluation contexts.
- Speaker notes: 24 files written and read back into the final deck.
