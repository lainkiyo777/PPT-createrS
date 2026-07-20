# Slide 22 Specification

page_type: end-to-end-architecture
title: 端到端闭环是下一阶段落地重点
key_message: 从 SCADA 清洗、未来风况预测、MoE 功率映射到考核评估必须按同一数据口径完成端到端验证。
layout: 一条大尺度环形闭环横贯画布，六个节点依次连接；底部独立一条“需要补充的数据”带，五类数据以图标与短标签呈现。
visual_style: YCFD-IMAGE-DECK-v2；深蓝系统架构，青绿主闭环，输出评估用琥珀；节点为简洁技术实体而非 UI 卡片。
image_prompt: "Use case: infographic-diagram. 16:9 Chinese end-to-end wind forecasting architecture. Exact title: ‘端到端闭环是下一阶段落地重点’. Six connected stages: ‘原始 SCADA’ → ‘清洗与特征’ → ‘PatchTST / FuXi-CFD’ → ‘未来风速风向’ → ‘MoE 功率映射’ → ‘15–240min 误差与合格率评估’. Show a feedback arrow from evaluation to data/model improvement. Bottom data needs: ‘状态码｜告警｜限电｜检修｜并网与计量’. Dark navy, cyan/teal closed loop, amber evaluation node, large labels, no crossing arrows, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 完整闭环流程与补充数据
    editable: false
dependencies:
  - slide-21
qa_checklist:
  - 六阶段流程顺序正确
  - 15–240min 评估范围准确
  - 五类补充数据完整
  - 闭环反馈箭头清楚且不穿过文字

