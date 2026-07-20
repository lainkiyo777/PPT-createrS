# Slide 10 Specification

page_type: task-definition
title: 阶段一同时预测 16 个未来时点
key_message: 任务以 288 个历史步长预测 h3–h48 的风速和风向三维表示，并分别评价速度和周期角度误差。
layout: 左侧是“288 steps = 24h”大数字，中央是“16 horizons × 3 targets”大数字，不绘制含虚构数值的矩阵；右侧用方向圆环解释 sin/cos；底部只放两组指标。
visual_style: YCFD-IMAGE-DECK-v2；深蓝科学可视化，青绿色时序矩阵，方向环用琥珀点强调 0°/360° 连续性。
image_prompt: "Use case: scientific-educational. 16:9 Chinese multi-horizon forecasting slide. Exact title: ‘阶段一同时预测 16 个未来时点’. Left dominant text, exact: ‘历史输入 288 steps = 24h’. The number must be 288, never 283. Center dominant text: ‘16 horizons × 3 targets’, with only three labels ‘wind speed｜direction sin｜direction cos’ and range ‘h3–h48 = 15–240min’. Do not generate a matrix or any example prediction values. Right: simple circular direction ring illustrating 0°/360° continuity. Bottom metrics: ‘风速：MAE / RMSE (m/s)’ and ‘风向：周期角度 MAE (deg)’. Dark navy, cyan accents, large labels, no tiny text, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 任务设置与指标
    editable: false
dependencies:
  - slide-09
qa_checklist:
  - 288 steps、24h、h3–h48、16×3 准确
  - 风向 sin/cos 表达准确
  - 指标单位准确
  - 方向圆环不误导为分类任务



## Revision

- Spec version: v2
- Reason: v1 预览将 288 错写为 283，并生成了无来源矩阵数值
