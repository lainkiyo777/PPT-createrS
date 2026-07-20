# Slide 12 Specification

page_type: result-highlight
title: PatchTST 在 full test 当前领先
key_message: PatchTST 的 Speed MAE 为 1.3299，较 Persistence 改善 10.56%，但当前主要是单 seed 结果。
layout: 左侧 62% 为六模型横向条形图，越短越好；右侧 38% 用大数字突出 1.3299、11.37° 和 10.56%；底部保留单 seed 风险说明。
visual_style: YCFD-IMAGE-DECK-v2；深蓝结果页，PatchTST 用明亮青绿，Persistence 灰蓝，KAFNet 的负提升用琥珀；直标数值，不使用图例小字。
image_prompt: "Use case: productivity-visual. 16:9 Chinese model result slide. Exact title: ‘PatchTST 在 full test 当前领先’. Horizontal bar chart labeled ‘Speed MAE ↓’: Persistence 1.4869, FuXi-CFD best 1.3552, FuXi-CFD 坐标+地形 1.3669, PatchTST 1.3299, VIMTS 1.3643, KAFNet 1.5708. Highlight PatchTST. Right large metrics: ‘1.3299 m/s’, ‘11.37°’, ‘较 Persistence 改善 10.56%’. Bottom note: ‘当前为单 seed 实验，不作统计显著性表述’. Dark navy, cyan highlight, amber only for KAFNet regression, large direct labels, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: full test 模型结果
    editable: false
dependencies:
  - slide-11
qa_checklist:
  - 六个 Speed MAE 数值准确
  - PatchTST 1.3299、11.37°、10.56% 准确
  - 条形图明确越低越好
  - 单 seed 限制可见
