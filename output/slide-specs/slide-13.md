# Slide 13 Specification

page_type: ablation
title: 24 小时历史窗口最均衡
key_message: 去除桨叶角后 Speed MAE 下降 3.84%，24 小时窗口在风速精度和历史信息之间最均衡。
layout: 左侧为“去桨叶角”前后对比的大号坡度图；右侧为 6h/12h/24h/36h 四点折线，24h 用青绿光环标记，36h 旁注明风向略优但风速变差。
visual_style: YCFD-IMAGE-DECK-v2；深色实验分析页，青绿代表改进，灰蓝为对照，琥珀用于权衡提示；数据直接标注。
image_prompt: "Use case: productivity-visual. 16:9 Chinese ablation result slide. Exact title: ‘24 小时历史窗口最均衡’. Left comparison: ‘全特征 1.4295’ → ‘去除桨叶角 1.3746’, label ‘Speed MAE ↓3.84%’. Right four-point history chart: ‘6h 1.4513’, ‘12h 1.3940’, ‘24h 1.3746’, ‘36h 1.4069’; highlight 24h. Add concise note: ‘36h 风向 11.78° 略优，但风速误差回升’. Dark navy, cyan/teal highlight, large labels, no tiny table, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 特征与历史窗口消融
    editable: false
dependencies:
  - slide-12
qa_checklist:
  - 全特征、去桨叶角数值与 3.84% 准确
  - 四个窗口 Speed MAE 准确
  - 24h 为当前较优结论
  - 36h 风向权衡说明准确

