---
status: pass
page_count: {{slide_count}}
preview_image_count: {{slide_count}}
final_image_count: {{slide_count}}
aspect_ratio_check: pass
missing_files_check: pass
font_size_risk_check: pass
overflow_check: pass
---

# QA Report

## Machine-verifiable results

- Required output entries: pass
- Independent slide-spec sequence: pass
- Preview filename/count match: pass
- Final filename/count match: pass
- Preview/final files are distinct: pass
- Final images are at least 1920×1080: pass
- PPTX page count match: pass
- PPTX contains one full-slide picture per slide: pass
- PPTX contains no native text, shapes, tables, charts, or groups: pass

## Visual and content review

| Slide | Title wrapping | Font-size risk | Overflow/crop | Key-message clarity | Data/source fidelity | Visual consistency | Result |
|---|---|---|---|---|---|---|---|
| slide-{{slide_id}} | pass | pass | pass | pass | pass | pass | pass |

Repeat the row for every slide. Mark the report `pass` only when every row passes and the deck opens normally.

## Validator evidence

- Command: `python scripts/validate_pipeline.py {{output_directory}}`
- Exit code: 0
- Result: `PASS: image-first pipeline validation succeeded`