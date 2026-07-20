# Slide 18 Specification

page_type: result-highlight
title: MoE 在两类工况下均取得最优结果
key_message: MoE 全测试集 MAE 为 179.17kW，正常工况 MAE 为 154.31kW，并在 R² 和合格率上同步领先。
layout: 左侧为五模型 MAE 对比的双系列条形图（全测试/正常工况），右侧用四个大数字展示 MoE 关键指标；底部仅保留一句结论。
visual_style: YCFD-IMAGE-DECK-v2；深蓝结果页，MoE 亮青绿色，其他模型灰蓝；正常工况用更浅色同系，关键值直接标注。
image_prompt: "Use case: productivity-visual. 16:9 Chinese model result slide. Exact title: ‘MoE 在两类工况下均取得最优结果’. Dual bar comparison MAE kW: XGBoost ‘208.83 / 181.80’, MLP ‘182.81 / 158.21’, FT-Transformer-lite ‘183.44 / 157.47’, 灰盒+残差 ‘183.63 / 155.54’, MoE ‘179.17 / 154.31’; order is full test / normal condition. Highlight MoE. Right metrics: ‘R² 0.9323 / 0.9573’, ‘NMAE 2.87%’, ‘WAPE 15.14%’, ‘15min 合格率 84.83% / 88.04%’. Dark navy, large labels, no tiny table, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 阶段二模型结果
    editable: false
dependencies:
  - slide-17
qa_checklist:
  - 五模型两类 MAE 数值准确
  - MoE 的 R²、NMAE、WAPE、合格率准确
  - 两类工况颜色可区分
  - 明确 MoE 为当前最优
