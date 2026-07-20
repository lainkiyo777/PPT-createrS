# Slide 17 Specification

page_type: model-roadmap
title: 功率建模从树模型演进到多专家
key_message: 传统机器学习、深度表格模型、特征训练改进和多工况结构形成逐级演进，最终走向 MoE。
layout: 一条向上的四级技术阶梯；每一级只显示模型家族和一个代表性改进，最高一级为 MoE 多专家结构。
visual_style: YCFD-IMAGE-DECK-v2；深色立体阶梯但保持扁平技术表达，青绿色随成熟度增强；最高层用明亮光带，不做模型名称堆砌。
image_prompt: "Use case: infographic-diagram. 16:9 Chinese model-evolution slide. Exact title: ‘功率建模从树模型演进到多专家’. Four ascending stages: ‘01 树模型｜LightGBM / XGBoost / RandomForest’, ‘02 深度表格｜MLP / DeepFM / FT-Transformer-lite’, ‘03 特征与训练｜风机 Embedding / 风向 sin-cos / 风速²·³ / 高功率加权’, ‘04 结构改进｜MoE 多工况专家’. Highlight MoE at the summit. Dark navy, cyan ascending energy line, large readable labels, no clutter, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 阶段二方法路线
    editable: false
dependencies:
  - slide-16
qa_checklist:
  - 四级路线与模型归类准确
  - 关键特征改进完整
  - MoE 作为最终结构高亮
  - 不出现源材料外模型

