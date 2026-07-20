# Slide 07 Specification

page_type: data-quality
title: 数据质量良好，但异常仍需业务归因
key_message: 数据无空值、无重复且主间隔为 5 分钟，但零出力、负出力和局部缺口不能直接判定为故障。
layout: 左侧用三个大型绿色通过指标“0 空值、0 重复、5min 主间隔”；右侧为真实/理论电量对比与 83.95% 大数字；底部一条琥珀色风险说明。
visual_style: YCFD-IMAGE-DECK-v2；深蓝质量监测界面但不做密集仪表盘；青绿表示通过，琥珀表示待归因。
image_prompt: "Use case: productivity-visual. 16:9 Chinese data-quality slide. Exact title: ‘数据质量良好，但异常仍需业务归因’. Three large quality signals: ‘空值 0’, ‘完全重复 0’, ‘主采样间隔 5min’. Right dominant metric: ‘实际/理论电量 83.95%’, with ‘12,522.10 MWh’ versus ‘14,915.58 MWh’. Bottom amber statement: ‘零出力、负出力和局部缺口需结合状态、告警、限电与检修数据归因’. Dark navy, cyan/green for passed checks, restrained amber risk, large text, no tiny table, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 质量结论和基础统计
    editable: false
dependencies:
  - slide-06
qa_checklist:
  - 三项质量指标准确
  - 12,522.10、14,915.58、83.95% 准确
  - 风险说明不将异常直接归因为故障
  - 数字和正文在投屏尺度可读

## Supporting statistics

- 平均风速 5.01m/s；最大风速 18.85m/s
- 平均有功功率 1,233.23kW；最大有功功率 6,297.13kW

