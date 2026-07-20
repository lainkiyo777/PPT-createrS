# Slide 08 Specification

page_type: task-flow
title: 先预测未来风况，再预测未来功率
key_message: 阶段一以过去 24 小时 SCADA 序列预测未来 15 分钟至 4 小时的风速和风向。
layout: 横向流程：左侧只用一条抽象的 24h SCADA 序列带，不显示具体变量列表；中间时序模型核心，右侧扇形展开 16 个 horizon；下方用一句话说明阶段一不直接预测功率。
visual_style: YCFD-IMAGE-DECK-v2；深色时序空间，青色历史轨迹进入模型，未来轨迹从青绿渐变到浅蓝，具有科学预测感。
image_prompt: "Use case: scientific-educational. 16:9 Chinese forecasting task slide. Exact title: ‘先预测未来风况，再预测未来功率’. Horizontal flow with exactly three blocks: ‘过去 24h SCADA 序列’ → ‘时序预测模型’ → ‘未来风速 + 未来风向’. Do not name any historical variables; specifically do not show pressure, humidity, 气压 or 湿度. Future horizon fan labeled ‘15min, 30min, …, 240min｜16 horizons’. Static context under model: ‘风机 ID / 类型 / 坐标 / 地形’. Bottom statement: ‘阶段一不直接预测功率，而是为功率映射提供未来风况’. Dark navy, cyan forecast curves, large labels, no extra variables, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 阶段一任务定义
    editable: false
dependencies:
  - slide-07
qa_checklist:
  - 历史输入为 24h
  - 输出为未来风速和风向
  - 时间范围为 15min–240min、16 horizons
  - 明确阶段一不直接预测功率



## Revision

- Spec version: v2
- Reason: v1 预览出现源材料外的气压和湿度标签
