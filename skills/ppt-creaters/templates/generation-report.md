---
status: completed
page_count: {{slide_count}}
image_tool: {{actual_image_tool_or_adapter}}
image_tool_status: available
ppt_assembly_mode: full-slide-images-only
---

# Generation Report

## Request resolution

- Source material: {{source_material}}
- Goal: {{presentation_goal}}
- Audience/use case: {{audience_and_use_case}}
- Language/duration: {{language_and_duration}}
- Assumptions: {{disclosed_assumptions_or_none}}
- Brand constraints: {{brand_constraints_or_none}}

## Global visual system

- System ID/version: {{visual_system_id_and_version}}
- Canvas: 16:9
- Palette: {{palette}}
- Typography hierarchy: {{typography_hierarchy}}
- Grid/spacing/safe margin: {{grid_spacing_safe_margin}}
- Image/icon/chart style: {{image_icon_chart_style}}
- Borders/radius/shadow: {{border_radius_shadow}}
- Forbidden elements: {{forbidden_elements}}

## Tool evidence

- Image adapter actually used: {{actual_image_tool_or_adapter}}
- Preview generation capability verified: yes
- Final generation capability verified: yes
- PPTX packaging adapter actually used: {{actual_pptx_packaging_adapter}}
- Packaging behavior: blank 16:9 deck plus one full-slide image per page

## Per-slide lineage

| Slide | Spec version | Preview file | Preview version/status | Final file | Final version/status | Source assets |
|---|---|---|---|---|---|---|
| slide-{{slide_id}} | {{spec_version}} | preview-images/slide-{{slide_id}}.png | {{preview_version_and_approved_status}} | final-images/slide-{{slide_id}}.png | {{final_version_and_verified_status}} | {{asset_ids_or_none}} |

Repeat the row for every slide. Never replace a higher version with a lower one.

## Stage record

- Source checked: {{timestamp_or_run_marker}}
- Outline completed: {{timestamp_or_run_marker}}
- Specs completed: {{timestamp_or_run_marker}}
- Previews completed: {{timestamp_or_run_marker}}
- Previews approved: {{timestamp_or_run_marker}}
- Finals completed: {{timestamp_or_run_marker}}
- PPTX assembled: {{timestamp_or_run_marker}}
- QA passed: {{timestamp_or_run_marker}}
- Deterministic validator: pass

If the image tool is unavailable, set `status: blocked` and `image_tool_status: unavailable`; do not create or claim preview images, final images, or PPTX.