# Slide 11 Specification

page_type: model-roadmap
title: 模型路线从基线走向自研架构
key_message: 统一路线包含 Persistence 基线、VIMTS/KAFNet 复现模型，以及 FuXi-CFD 与 PatchTST 两类自研方案。
layout: 一条从左到右加深的模型演进轨道；四个模型家族沿轨道排布，最右侧自研模型体量最大；背景用抽象时序 patch 和 transformer 层次。
visual_style: YCFD-IMAGE-DECK-v2；深色技术路线图，基线灰蓝、复现模型蓝、自研模型高亮青绿；避免四张等尺寸卡片。
image_prompt: "Use case: infographic-diagram. 16:9 Chinese model-roadmap slide. Exact title: ‘模型路线从基线走向自研架构’. One continuous evolution path: ‘Persistence｜简单基线’ → ‘VIMTS / KAFNet｜复现模型’ → ‘FuXi-CFD / LightFuXi｜Transformer + 静态上下文’ → ‘PatchTST｜channel-independent patch encoder’. Highlight the last two as ‘我们的方法’. Dark navy with cyan progression, abstract sequence patches and transformer layers, large readable Chinese text, no unrelated models, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 阶段一模型分组
    editable: false
dependencies:
  - slide-10
qa_checklist:
  - 四组模型名称和分类准确
  - FuXi-CFD 与 PatchTST 均标为我们的方法
  - 路线表达演进而非简单并列
  - 无源材料外模型

