# Slide 16 Specification

page_type: task-flow
title: 阶段二学习“风况到功率”的映射
key_message: 阶段二不是再次做时序预测，而是将目标时刻风速、风向、温度和机组信息映射为有功功率。
layout: 左侧为四类输入粒子汇聚到中间映射函数，右侧为单一功率仪表和额定功率上限；底部用四个大数字交代样本规模。
visual_style: YCFD-IMAGE-DECK-v2；深色物理映射场景，青绿输入向量汇入琥珀色功率输出；数字简洁有力。
image_prompt: "Use case: scientific-educational. 16:9 Chinese power-mapping task slide. Exact title: ‘阶段二学习“风况到功率”的映射’. Flow: ‘风速 + 风向 + 温度 + 风机编号’ → ‘功率映射模型’ → ‘目标时刻有功功率’. Bottom large metrics: ‘62,537 清洗后样本’, ‘4 台机组’, ‘6250 kW 额定功率’, ‘43,775 / 9,381 / 9,381 训练/验证/测试’. Add statement: ‘阶段二不是再次做时序预测’. Dark navy, cyan input streams, amber power output, large readable text, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 阶段二任务与数据
    editable: false
dependencies:
  - slide-15
qa_checklist:
  - 四类输入和输出准确
  - 62,537、4、6250、数据划分准确
  - 明确不是再次做时序预测
  - 视觉与阶段一有连续性

