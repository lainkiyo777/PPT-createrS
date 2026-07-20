---
name: ppt-creaters
version: 1.0.0
description: Use when creating a presentation from a topic, source document, or outline where every slide must be produced and approved as an image before PPTX assembly.
---

# PPT Creaters

## Overview

This skill is an image-first PPT production orchestrator. It turns source material into an approved set of complete slide images, then packages those images into a PPTX without recreating the layout inside PowerPoint.

Core principle: **先结构化，再视觉化；先生成逐页规格，再生成图片。**

Iron law:

> NO FINAL PPTX WITHOUT COMPLETE PREVIEW AND FINAL IMAGE SETS.

The PPT assembler is a transport layer, not a design surface. If a step cannot meet this contract, stop with an explicit blocked result. Never silently fall back to a normal presentation-layout workflow.

## When to Use

Use this skill when:

- A topic must become a complete presentation.
- A document must become a report or proposal deck.
- A rough outline lacks slide-level content and visual design.
- Every slide must share one visual system.
- AI image generation is expected for complete slide compositions.
- The final PPTX must preserve approved visual output exactly.

Do not use it for:

- Editing one simple title.
- Polishing a small amount of existing text.
- Minor formatting edits to a complete user-provided PPTX.
- A request that explicitly requires editable native PowerPoint text, tables, or charts.

For the last case, explain that it conflicts with this skill's image-only output contract and use a different workflow only after the user chooses that trade-off.

## Required Inputs

Resolve and record these before generating the outline:

- `source_material`
- `presentation_goal`
- `audience`
- `use_case`
- `language`
- `target_slide_count`
- `presentation_duration`
- `visual_references`
- `brand_constraints`
- `available_tools`
- `output_directory`

If information is missing, list the gap and a conservative assumption. Never invent a key figure, citation, brand asset, screenshot, or tool capability.

## Fixed Output Contract

Use this exact deliverable structure:

```text
output/
├── outline.md
├── slide-specs/
│   ├── slide-01.md
│   └── ...
├── preview-images/
│   ├── slide-01.png
│   └── ...
├── final-images/
│   ├── slide-01.png
│   └── ...
├── presentation.pptx
├── qa-report.md
└── generation-report.md
```

Do not add legacy deliverables such as `slide-specs.txt`, `brief.md`, `visual-style.md`, or `image-manifest.yaml` under `output/`. Resolved requirements, global visual rules, tool evidence, provenance, and asset versions belong in `generation-report.md` and the independent slide specs.

## State Model

Only advance in this order:

```text
source_checked
  → outlined
  → specified
  → previews_complete
  → previews_approved
  → finals_complete
  → assembled
  → qa_passed
  → validated
```

A later state is invalid if any earlier gate is incomplete. A deadline does not change the state model.

## Workflow

### Phase A — Source and Tool Gate

**Input:** source material and requested outcome.

**Actions:**

1. Read the source before writing key claims or data.
2. Resolve goal, audience, use case, page count, duration, language, brand constraints, and aspect ratio.
3. Inspect the actual environment for an image-generation capability and a PPTX packaging capability.
4. Record the real adapter/tool names and availability in `generation-report.md`.

**Output:** initialized `generation-report.md` with `status: in_progress` or `status: blocked`.

**Exit condition:** source gaps are disclosed and an actual image tool is available.

If no image tool is available, stop. Report `image_tool_status: unavailable`, preserve any valid text planning already completed, do not create dummy images, do not create a PPTX, and do not claim completion.

### Phase B — Outline

**Input:** checked source and resolved requirements.

**Actions:**

1. Create `output/outline.md` from [templates/outline.md](templates/outline.md).
2. Build a narrative, not a list of loose headings.
3. For every slide, define its role, key conclusion, and transition from the previous slide to the next.
4. Keep `slide_count` equal to the intended final page count.

**Output:** `outline.md`.

**Exit condition:** the story has a clear beginning, reasoning chain, evidence/solution, conclusion, and action where appropriate.

### Phase C — Independent Slide Specs

**Input:** approved or internally consistent outline.

**Actions:**

1. Create exactly one file per slide: `output/slide-specs/slide-XX.md`.
2. Use [templates/slide-spec.md](templates/slide-spec.md).
3. Every file must include these exact top-level fields:
   - `page_type`
   - `title`
   - `key_message`
   - `layout`
   - `visual_style`
   - `image_prompt`
   - `source_assets`
   - `dependencies`
   - `qa_checklist`
4. Put all visible copy, data, chart semantics, image instructions, hierarchy, spacing, typography, source fidelity, and acceptance criteria inside the spec.
5. Repeat the shared visual-system identifier and all page-specific deviations in `visual_style`.

**Output:** one contiguous set from `slide-01.md` to `slide-NN.md`.

**Exit condition:** every pixel-bearing decision is executable from the spec without consulting a rough outline.

Never generate preview or final images directly from a rough outline.

### Phase D — Preview Images

**Input:** complete slide specs and a verified image tool.

**Actions:**

1. Generate one actual 16:9 PNG per spec into `output/preview-images/`.
2. Send the slide's complete `image_prompt`, page content, cited assets, and the same global visual-system rules to the configured image adapter.
3. Name files exactly `slide-01.png` through `slide-NN.png`.
4. Present the full ordered preview set for review. An optional contact sheet may be shown as a review convenience, but it does not replace the individual files and is not part of the fixed output contract.
5. Record tool, model/adapter label, prompt/spec version, file name, dimensions, and generation status in `generation-report.md`.

**Output:** preview PNG count equals slide count.

**Exit condition:** all preview files exist and can be visually reviewed.

Do not use screenshots produced after PPT assembly as previews. Preview generation must precede final generation and assembly.

### Phase E — Preview Review and Revision Gate

**Input:** the complete ordered preview set.

Review every slide with [checklists/preview-review.md](checklists/preview-review.md). Check message accuracy, completeness, numbers, readability, title wrapping, font-size hierarchy, layout, cropping, chart comprehension, repetition, visual consistency, and source-asset fidelity.

If a slide fails:

1. Mark that preview rejected.
2. Edit only its `slide-specs/slide-XX.md` first.
3. Increment the spec/prompt version in `generation-report.md`.
4. Regenerate only its preview image.
5. Review it again.

Do not patch PPT assembly code, add a native text box, or redraw a chart in PowerPoint to fix a rejected preview.

**Output:** per-slide pass/fail record.

**Exit condition:** every preview passes. A partial pass cannot advance.

### Phase F — Final Images

**Input:** approved specs, approved previews, the same visual system, and a verified image tool.

**Actions:**

1. Regenerate every page as a distinct final PNG at no less than 1920×1080.
2. Use the approved spec and preview as constraints.
3. Preserve information structure, copy, hierarchy, and source-asset treatment.
4. Store files as `output/final-images/slide-XX.png`.
5. Record versions and dimensions in `generation-report.md`.

**Output:** final PNG count equals slide count.

**Exit condition:** all final images exist, are 16:9, meet resolution requirements, and are not copied low-resolution previews.

Final generation must not reinterpret or restructure an approved page.

### Phase G — PPTX Assembly

**Input:** complete final-image set only.

**Actions:**

1. Create a blank 16:9 deck.
2. For slide `N`, insert only `final-images/slide-NN.png` at `(0, 0)` and size it to the full slide.
3. Preserve page order and image aspect ratio.
4. Save as `output/presentation.pptx`.

**Output:** an image-only PPTX.

**Exit condition:** page count equals final-image count; each slide contains exactly one full-slide picture and no native text, shape, table, chart, group, or replacement icon.

The assembly phase must never:

- Re-layout body text, tables, or charts.
- Modify approved images.
- Redraw screenshots.
- Replace user-provided icons.
- Crop key information.
- Add corrective overlays.
- Use an older asset version over a newer approved version.

### Phase H — QA and Validation

**Input:** all fixed-contract deliverables.

**Actions:**

1. Create `qa-report.md` from [templates/qa-report.md](templates/qa-report.md).
2. Check page count, missing/duplicate files, preview/final counts, aspect ratios, final resolution, wrong versions, title wrapping, font-size risk, content legibility, cropping, overflow, source-number fidelity, visual consistency, and file openability.
3. Create the final `generation-report.md` from [templates/generation-report.md](templates/generation-report.md).
4. Run:

```text
python scripts/validate_pipeline.py <path-to-output>
```

Run the command from this skill directory, or use the script's absolute path. This is the validator's real interface; do not invent flags.

**Output:** `qa-report.md`, `generation-report.md`, and validator result.

**Exit condition:** validator prints `PASS: image-first pipeline validation succeeded` and exits with code 0.

Never set `status: completed` or report success before the validator passes.

## Decision Rules

1. **Is source material sufficient?**
   - No: document missing information and conservative assumptions; do not invent key data.
   - Yes: proceed to outline.
2. **Do complete independent slide specs exist?**
   - No: create/fix them before any image generation.
   - Yes: proceed to previews.
3. **Is an actual image tool available?**
   - No: mark blocked and stop; no fake images or PPTX.
   - Yes: generate all previews.
4. **Does every preview pass?**
   - No: return to the corresponding spec only.
   - Yes: generate every final image.
5. **Do final images exactly match the spec set?**
   - No: do not assemble.
   - Yes: package them full-slide.
6. **Does deterministic validation pass?**
   - No: fix the responsible upstream artifact and re-run.
   - Yes: report completion.

## Tool Adapter Rules

Image and PPTX tools are configurable adapters. Examples such as Nano Banana Lite for previews or Codex image g2 for final images are labels, not guaranteed capabilities. Never invent their API, CLI, parameters, results, or availability.

A tool may be used only after its callable interface is actually present. The image adapter must return a real file for each requested slide. The PPTX adapter may only create a blank deck and place full-slide images.

Using a generic presentation tool to create native slide layouts violates this skill even if the result looks polished.

## Non-Negotiable Rules

1. Never generate final images from a rough outline.
2. Never omit independent slide specs.
3. Never use conflicting visual systems across pages.
4. Never invent image or PPT tool calls.
5. Never claim nonexistent files were generated.
6. Never modify approved slide content during PPTX assembly.
7. Never overwrite a newer asset with an older version.
8. Never label a low-resolution preview as a final image.
9. Never create key data without checking the source.
10. Never use urgency to bypass content structure or image gates.
11. Never use ordinary PowerPoint layout as a degraded fallback.
12. Never repair a rejected preview by changing assembly code.

## Regression Signals

Treat these rationalizations as failures:

| Rationalization | Required response |
|---|---|
| “The deadline is close, so native PPT text is faster.” | Keep the image pipeline; if it cannot finish, report blocked/incomplete. |
| “The image tool is unavailable, so deliver a normal editable PPTX.” | Stop and report the missing dependency. |
| “The deck already exists; patch six slides in code.” | Revise six specs, regenerate their previews/finals, then reassemble. |
| “Post-assembly screenshots can count as previews.” | Reject; previews must exist before final images and PPTX. |
| “A contact sheet is enough.” | Reject; every slide needs its own preview and final PNG. |

## References

- [Outline template](templates/outline.md)
- [Slide-spec template](templates/slide-spec.md)
- [QA-report template](templates/qa-report.md)
- [Generation-report template](templates/generation-report.md)
- [Preview-review checklist](checklists/preview-review.md)
- [Final-QA checklist](checklists/final-qa.md)
- [Pressure and regression scenarios](tests/scenarios.md)
- [Deterministic validator](scripts/validate_pipeline.py)