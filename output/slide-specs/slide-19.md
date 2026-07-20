# Slide 19 Specification

page_type: architecture
title: 多专家门控适配不同风况曲线
key_message: MoE 用 Gate 按风况分配专家权重，并结合风机个体表示拟合不同工况下的功率曲线。
layout: 左侧输入变量与风机 Embedding 汇成特征 z；中央 Gate 将信号分流到三个专家；右侧加权融合输出功率；右下角放简化公式和五个指标。
visual_style: YCFD-IMAGE-DECK-v2；深蓝神经架构图，Gate 为青绿色光核，三专家使用同系不同明度，输出用琥珀色能量束；连接清楚不交叉文字。
image_prompt: "Use case: scientific-educational. 16:9 Chinese MoE architecture slide. Exact title: ‘多专家门控适配不同风况曲线’. Flow: ‘风速｜风向｜温度｜衍生特征｜风机 Embedding’ → ‘特征向量 z’ → ‘Gate: Softmax’ → three expert branches ‘Expert 1 / Expert 2 / Expert 3’ → ‘加权融合’ → ‘功率预测’. Include exact simplified formula: ‘P̂ = 6250 × Σ gₖ(z)·Expertₖ(z)’. Metrics: ‘MAE 179.17kW｜正常工况 154.31kW｜R² 0.9573｜合格率 88.04%’. Dark navy, cyan nodes, clean arrows, no native dashboard cards, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: MoE 结构和关键公式
    editable: false
dependencies:
  - slide-18
qa_checklist:
  - 输入、Gate、Experts、融合、输出顺序准确
  - 6250 缩放和公式含义准确
  - 四个关键指标准确
  - 箭头不穿过节点或标签

