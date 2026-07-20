# Slide 14 Specification

page_type: result-highlight
title: clean 微调带来最明确收益
key_message: PatchTST 经 full 预训练再在 clean 数据微调后，Speed MAE 降至 1.2486，较 OpenOA persistence 改善 16.75%。
layout: 中央为从 full 预训练到 clean 微调的路径箭头，终点以“1.2486”超大数字呈现；下方用六个方法的紧凑排名条，右侧标 clean test 仅 1,273 窗口。
visual_style: YCFD-IMAGE-DECK-v2；青绿色训练流贯穿全页，终点高亮；样本量限制用琥珀色圆角提示，但不做密集表格。
image_prompt: "Use case: productivity-visual. 16:9 Chinese fine-tuning result slide. Exact title: ‘clean 微调带来最明确收益’. Central flow: ‘FULL 预训练’ → ‘OPENOA CLEAN 微调’ → dominant result ‘PatchTST 1.2486 m/s’. Secondary metrics: ‘RMSE 1.5982’, ‘风向角 MAE 5.20°’, ‘较 persistence 改善 16.75%’. Small ranked comparison with exact Speed MAE: persistence 1.4998, FuXi clean-only 1.4102, FuXi full→clean 1.2787, PatchTST clean-only 1.4681, PatchTST full→clean 1.2486. Amber note: ‘clean test = 1,273 windows，仅说明清洗与微调潜力’. Dark navy, cyan flow, large typography, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: OpenOA clean 微调结果
    editable: false
dependencies:
  - slide-13
qa_checklist:
  - 1.2486、1.5982、5.20°、16.75% 准确
  - full→clean 路径清楚
  - clean test 1,273 的限制可见
  - 不与 full test 混排结论

