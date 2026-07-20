# Slide {{slide_id}} Specification

page_type: {{page_type}}
title: {{title}}
key_message: {{one_sentence_conclusion}}
layout: {{complete_16_9_composition_with_regions_alignment_spacing_and_reading_order}}
visual_style: {{global_system_id_plus_page_specific_typography_palette_imagery_chart_icon_border_shadow_rules}}
image_prompt: {{self_contained_prompt_including_exact_visible_copy_data_visual_hierarchy_layout_style_aspect_ratio_and_forbidden_changes}}
source_assets:
  - asset_id: {{asset_id}}
    file: {{source_file}}
    usage: {{exact_usage}}
    editable: {{true_or_false}}
dependencies:
  - {{upstream_slide_asset_or_source_dependency}}
qa_checklist:
  - {{key_message_is_immediately_clear}}
  - {{all_visible_text_matches_the_spec_and_is_legible}}
  - {{title_has_no_unintended_line_break}}
  - {{font_hierarchy_has_no_small_text_risk}}
  - {{numbers_and_chart_semantics_match_sources}}
  - {{layout_has_no_crop_or_overflow}}
  - {{visual_system_matches_other_slides}}

## Objective

{{what_this_page_must_accomplish}}

## Audience takeaway

{{what_the_audience_should_remember_or_do}}

## Visible content

- Title copy: {{exact_title_copy}}
- Subtitle copy: {{exact_subtitle_copy_or_none}}
- Body copy: {{exact_body_copy}}
- Labels/callouts: {{exact_labels_and_callouts}}
- Footer/source copy: {{exact_footer_or_source_copy}}

## Data and chart semantics

- Data source: {{source_reference_or_none}}
- Exact values: {{verified_values_or_none}}
- Chart type: {{chart_type_or_none}}
- Axes/units/legend: {{axes_units_legend_or_none}}
- Intended comparison: {{comparison_or_none}}

## Visual composition

- Main visual: {{subject_scene_or_diagram}}
- Supporting visuals: {{supporting_elements}}
- Icon/screenshot handling: {{original_asset_handling}}
- Focal hierarchy: {{first_second_third_attention_order}}
- Safe margins: {{safe_margin_definition}}

## Generation record

- Spec version: {{spec_version}}
- Preview target: preview-images/slide-{{slide_id}}.png
- Final target: final-images/slide-{{slide_id}}.png
- Final minimum dimensions: 1920x1080