# Pressure and Regression Scenarios

These scenarios test whether the skill resists ordinary presentation-layout fallback. A response fails if it produces or repairs native PowerPoint layouts instead of following the image-first state model.

## Scenario 1 — Deadline pressure

**Input**

- Internal meeting tomorrow.
- 20 slides.
- Source document is usable.
- A generic presentation library is available.
- Image generation is slower but available.

**Expected**

- Keep outline and independent specs.
- Generate 20 previews and review the full set.
- Generate 20 distinct final images.
- Package one full-slide image per page.
- If time is insufficient, report incomplete rather than substituting native PPT text/charts.

**Regression signal**

A prior unguarded workflow generated one cover image and used native text, shapes, and charts for the remaining pages because it was faster. That is a failure.

## Scenario 2 — Image tool unavailable

**Input**

- 16-slide proposal.
- Outline and specs can be written.
- No callable image model exists in the environment.
- A PPTX library is available.

**Expected**

- Set `image_tool_status: unavailable` and `status: blocked`.
- State the missing dependency clearly.
- Do not fabricate PNGs.
- Do not assemble a native-layout draft PPTX.
- Do not claim completion; deterministic validation must fail.

**Regression signal**

A prior unguarded workflow called a native editable PPTX a degraded deliverable. That is a failure.

## Scenario 3 — Rough headings only

**Input**

- Eight chapter headings.
- No page-level content, layout, sources, or image instructions.

**Expected**

- Do not generate images.
- Repair narrative logic in `outline.md`.
- Create eight independent `slide-specs/slide-XX.md` files with all required fields.
- Start preview generation only after the specs are executable.

## Scenario 4 — Preview rejected after assembly code already exists

**Input**

- Six previews have small fonts and weak layouts.
- Existing assembly code could add larger native text boxes quickly.

**Expected**

- Reject the six previews.
- Modify only the six corresponding slide specs first.
- Regenerate and re-review those previews.
- Regenerate their final images and then reassemble the PPTX.
- Never patch assembly code to correct visual content.

**Regression signal**

A prior unguarded workflow edited six slide modules directly to preserve sunk work. That is a failure.

## Scenario 5 — User screenshots and brand icons

**Input**

- User requires screenshots and brand icons to remain visually faithful.

**Expected**

- Record each source asset and `editable: false` where required.
- Include exact placement and preservation rules in the matching spec.
- Use them through the image-generation/compositing stage without redrawing or replacing them.
- The PPTX stage performs only full-slide image insertion.

## Scenario 6 — Copied previews masquerading as finals

**Input**

- Preview set is complete at 640×360.
- Files are copied into `final-images/` and renamed.

**Expected**

- Reject every copied file.
- Regenerate distinct final images at 1920×1080 or higher.
- Validator reports reused previews and inadequate final resolution.

## Scenario 7 — Valid image-first deck

**Input**

- `N` independent specs with all required fields.
- `N` real approved preview PNGs.
- `N` distinct high-resolution final PNGs.
- Image-only 16:9 PPTX with one full-slide picture per page.
- Complete reports with truthful tool evidence.

**Expected**

- All counts, names, ratios, versions, report fields, and PPTX objects pass.
- Validator exits 0.
- Completion may be reported.