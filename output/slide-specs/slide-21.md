# Slide 21 Specification

page_type: integration-bridge
title: 两阶段衔接后形成未来功率预测
key_message: 阶段一回答“未来风况是什么”，阶段二回答“该风况对应多少功率”，两者合并才形成 15 分钟至 4 小时预测链路。
layout: 左侧为阶段一未来风速/风向曲线，中间插入 MoE 映射核，右侧展开未来功率曲线；上下各放一句问答式说明，底部突出正常工况 15min 合格率。
visual_style: YCFD-IMAGE-DECK-v2；深色闭环桥接页，阶段一青色、MoE 青绿、功率输出琥珀金，三段连续且无割裂卡片。
image_prompt: "Use case: infographic-diagram. 16:9 Chinese integration slide. Exact title: ‘两阶段衔接后形成未来功率预测’. One continuous flow: ‘阶段一｜未来风速 + 未来风向’ → ‘MoE｜+ 温度 + 风机编号’ → ‘未来 15min–4h 功率’. Top captions: ‘未来风况是什么？’ and ‘这个风况对应多少功率？’. Bottom metrics: ‘当前功率映射：全测试 MAE 179.17kW｜正常工况 MAE 154.31kW｜15min 合格率 88.04%’. Dark navy, cyan-to-amber energy flow, large readable Chinese, no extra stages, no watermark."
source_assets:
  - asset_id: source-outline
    file: 整合版PPT内容大纲.md
    usage: 阶段二结论和两阶段衔接
    editable: false
dependencies:
  - slide-20
qa_checklist:
  - 两阶段问题定义准确
  - MoE 输入包含未来风况、温度和风机编号
  - 15min–4h 范围和三项指标准确
  - 流程连续且方向明确

