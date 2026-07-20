# Slide 15 Specification

page_type: section-summary
title: 阶段一已形成完整实验闭环
key_message: 阶段一已完成任务定义、基线对比、自研模型、消融和 clean 微调，下一步重点是多 seed 与分层误差诊断。
layout: 一条圆弧式实验闭环，依次经过五个节点；中心显示“15min–4h 风速/风向联合预测”；底部左右分列“已完成”和“待验证”。
visual_style: YCFD-IMAGE-DECK-v2；深蓝闭环轨道，已完成节点青绿发光，待验证节点用琥珀虚线；整页像成熟技术路线总结。
image_prompt: "Use case: infographic-diagram. 16:9 Chinese stage-summary slide. Exact title: ‘阶段一已形成完整实验闭环’. A clean circular experimental loop with five nodes: ‘任务定义’, ‘Persistence 基线’, ‘FuXi-CFD / PatchTST’, ‘特征与窗口消融’, ‘OpenOA clean 微调’. Center: ‘未来 15min–4h 风速/风向联合预测’. Bottom verified results: ‘full test PatchTST MAE 1.3299’ and ‘clean 微调 MAE 1.2486’. Bottom amber next step: ‘多随机种子｜分 horizon｜分风机｜分风速区间’. Dark navy, cyan completed loop, large labels, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 阶段一成果与局限
    editable: false
dependencies:
  - slide-14
qa_checklist:
  - 五个实验环节齐全
  - 两个关键 MAE 数值准确
  - 待验证事项完整但不拥挤
  - 页面明显承担阶段小结作用

