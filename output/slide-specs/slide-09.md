# Slide 09 Specification

page_type: comparison
title: full 与 clean 是两套不同评估口径
key_message: full test 更接近真实复杂工况，OpenOA clean test 用于评估清洗和微调潜力，两者不可混排。
layout: 画布以一条中轴分为左右两个宽区；左边 full 展示完整样本量和复杂工况，右边 clean 展示清洗后窗口和用途；底部用“不可直接混排”连接警示。
visual_style: YCFD-IMAGE-DECK-v2；左侧深青、右侧蓝绿，背景用不同密度的数据点表现复杂与清洁，不做小字表格。
image_prompt: "Use case: productivity-visual. 16:9 Chinese comparison slide. Exact title: ‘full 与 clean 是两套不同评估口径’. Left half: ‘FULL SUPERVISED’, numbers ‘train 67,657｜val 24,870｜test 22,589’, caption ‘完整工况·主模型统一对比’. Right half: ‘OPENOA CLEAN’, numbers ‘train 8,031｜val 1,413｜test 1,273’, caption ‘清洗工况·微调与上限评估’. Bottom strong statement: ‘两个 test 口径不可直接混排排名’. Dark navy, clear split-screen, large digits, no tiny table, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: full 与 OpenOA clean 划分
    editable: false
dependencies:
  - slide-08
qa_checklist:
  - 两套 train/val/test 数量准确
  - 口径用途表述准确
  - “不可直接混排”清晰
  - 左右对比在风格上统一

## Additional source evidence

- 原始 supervised windows：115,116
- OpenOA clean windows：10,717
- normal rows：88,880；comm_gap：44,553；sensor_fault：29,413

