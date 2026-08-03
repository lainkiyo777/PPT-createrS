# Slide 06 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-06.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-06.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Five-task slide. Recompose the five tasks as a readable vertical or horizontal journey with five numbered stations, short descriptions and large metric chips, followed by a separate verification band. Preserve each task's wording and metric exactly. Use generated connector geometry and simple task icons only as visual aids; do not collapse the content into icon-only decoration.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 研究内容和技术指标
- 6
- 五项研究任务及对应技术指标
- 1
- 多模态数据与知识底座
- 统一设备对象、异常事件和证据模型；建设样本库、图文知识库及数据治理工具。
- 样本库1套、图文知识库1套
- 2
- 跨模态设备异常诊断
- 融合视频、红外、SCADA/CMS、气象、历史和同侪信息，形成可追溯证据链。
- 虚警过滤率≥90%；准确率≥90%
- 3
- 检修全过程监督与核验
- 识别安全违章、安措、工序和工艺；核验工单、两票、三措两案图文视频一致性。
- 审核效率提升≥80%
- 4
- 云边模型自适应演进
- 云端大模型处理长尾异常，人工确认后沉淀样本，蒸馏并下发边缘小模型。
- 核心算法≥4类；迭代周期≤7天
- 5
- 双中台及示范应用
- 建设算法中台、业务调度中台和低代码流程编排，在集控中心及两场站示范。
- 平台1套；示范场站2个
- 验证方式：标注测试集、历史数据回放、旁路试运行、现场全过程记录及第三方评价。

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
