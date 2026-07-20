# Slide 06 Specification

page_type: system-map
title: 字段完整覆盖“输入—响应—输出”
key_message: 字段体系覆盖外部风况、机组控制响应和功率结果，刚好对应预测链路。
layout: 画布中央为一台半透明风机剖面，左侧风况变量进入，机舱内部显示响应变量，右侧输出三类功率；顶部保留结论式标题。
visual_style: YCFD-IMAGE-DECK-v2；工程数字孪生风格，深蓝底、青绿流线和简洁技术标注；避免多栏表格。
image_prompt: "Use case: scientific-educational. 16:9 Chinese wind-turbine digital-twin slide. Exact title: ‘字段完整覆盖“输入—响应—输出”’. A single central turbine cutaway. Left input labels: ‘风速｜风向｜室外温度’. Inside response labels: ‘发电机转速｜桨叶角’. Right output labels: ‘实际有功｜理论有功｜无功功率’. Small identity ribbon: ‘风机编号｜风机类型｜时间’. Use cyan directional flows, dark navy background, large Chinese labels, technical but uncluttered, no extra fields, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 字段分类与用途
    editable: false
dependencies:
  - slide-05
qa_checklist:
  - 输入、响应、输出变量归类准确
  - 主视觉清楚表现数据链路
  - 文字不压在复杂背景上
  - 不出现源材料之外的字段
