# Slide 20 Specification

page_type: error-analysis
title: 高风速区是当前主要误差来源
key_message: 8m/s 以上误差显著上升，9–12m/s 区间可达到 600–1000kW，应成为高功率专项优化重点。
layout: 左侧 64% 为低风速、中风速、高风速三个定性区间，不绘制无来源的逐点误差曲线；严格高亮 9–12m/s 区间及“600–1000kW 量级”；右侧用“样本少—控制增强—工况差异”三段因果链。
visual_style: YCFD-IMAGE-DECK-v2；深色分析页，低中风速为青绿，高风速风险区渐变为琥珀红；强调一张图和一条因果链。
image_prompt: "Use case: productivity-visual. 16:9 Chinese error-analysis slide. Exact title: ‘高风速区是当前主要误差来源’. Left qualitative three-zone visual, not a numeric line chart: ‘低风速｜误差较低’, ‘中等风速｜趋势拟合较好’, ‘8m/s 以上｜误差明显增大’. Highlight one strict amber band only: ‘9–12m/s｜约 600–1000kW 量级’. Do not extend the highlighted band beyond 12m/s and do not invent point-by-point MAE values. Right causal chain: ‘高功率样本较少’ → ‘接近额定功率后控制策略增强’ → ‘桨距/限电/偏航/设备状态扩大差异’. Bottom actions: ‘高功率加权｜分段专家｜高风速校准｜额定功率物理约束’. Dark navy, cyan-to-amber risk gradient, large labels, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 高风速误差现象、原因和优化
    editable: false
dependencies:
  - slide-19
qa_checklist:
  - 8m/s 与 9–12m/s 风险区准确
  - 600–1000kW 表述为量级而非精确单点
  - 原因和优化均来自源材料
  - 风险色不影响其他文字可读性



## Revision

- Spec version: v2
- Reason: v1 预览将风险带扩展到 12m/s 之外并绘制了无来源曲线
