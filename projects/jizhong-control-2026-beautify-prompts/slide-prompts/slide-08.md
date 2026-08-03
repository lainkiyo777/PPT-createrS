# Slide 08 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-08.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-08.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Scenario one slide. Recompose as a visual evidence-chain architecture: a compact source-evidence rail (CMS trend, peer comparison, video/infrared/UAV) feeds a four-stage diagnostic loop and closes at human confirmation, work order, sample and model iteration. Preserve every numbered stage, evidence label, VLM+RAG block and both boundary statements. Generate clean connectors and evidence containers; all labels and numbers remain deterministic overlay.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 研究内容和技术指标
- 8
- 典型场景一：风机振动异常的多模态证据链诊断
- 现场/系统素材（待补充）
- CMS振动趋势
- 待插入真实素材
- 同型机组横向对比
- 待插入真实素材
- 风机视频/红外/无人机复拍
- 待插入真实素材
- ① 异常触发
- CMS振动
- 超过动态基线
- 边缘生成
- 异常候选
- ② 多源证据联查与统一事件包
- SCADA/CMS
- 功率·温度
- 振动特征
- 环境气象
- 风速·温湿度
- 区域扰动
- 同型机组
- 横向对比
- 识别个体偏离
- 历史基线
- 纵向趋势
- 识别早期劣化
- 视觉复拍
- 风机视频/红外
- 云台或无人机
- ③ 集控智能研判
- VLM+RAG解释
- 异常类型
- 风险等级·置信度
- 证据摘要
- 检查建议
- 不直接停机控制
- ④ 闭环处置
- 人工终核
- 发起工单
- 结果回填
- 样本入库
- 模型迭代
- 研判依据：视觉—时序—环境—历史—同侪—知识联合印证
- 输出边界：系统提供证据链和建议，由集控专业人员确认后进入生产流程

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
