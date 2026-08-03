# Slide 05 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-05.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-05.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Research-content slide. Use the source as a high-fidelity visual anchor but recompose it as a strong before/after comparison matrix on top, a red 项目边界 divider, and a four-stage research-output pipeline below. Keep all comparison rows, four numbered research outputs and the overall-work sequence verbatim. Add simple arrows and a pipeline rail if helpful; no new research claim may be introduced.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 研究内容和技术指标
- 5
- 科技项目与常规信息化建设的本质区别
- 常规信息化项目
- 建设目标
- 已有业务流程线上化、系统集成与功能交付
- 主要工作
- 软件购置/配置、接口开发、数据迁移、部署实施
- 验收重点
- 功能完整、系统可用、用户覆盖和上线运行
- 本科技项目
- 科研目标
- 突破未知机理、核心算法及云边协同工程化关键技术
- 主要工作
- 模型/算法/架构研究，实验验证、原型研制和示范
- 验收重点
- 对照试验、量化指标、第三方测试及自主知识产权
- 项目边界：平台是承载算法验证和示范应用的载体，不以软件采购、系统集成和功能上线作为主要科研产出。
- 本项目需要研究的新技术、研究对象与研发输出
- 01  跨模态证据链诊断
- 研究：视觉、时序、环境、历史、同侪及知识的时空对齐、证据聚合与置信度计算。
- 输出：可解释异常诊断算法。
- 02  多模态语义核验
- 研究：作业对象、步骤、安措和工艺识别，图文视频一致性判断及证据缺口定位。
- 输出：全过程监督与核验算法。
- 03  云边模型自演进
- 研究：边云任务划分、长尾样本准入、模型蒸馏压缩、灰度发布与回滚。
- 输出：持续演进方法和边缘模型。
- 04  多模态低代码双中台
- 研究：算法组件化、事件/流程编排、人工终核及跨场景复用机制。
- 输出：算法中台和业务调度中台原型。
- 总体工作思路：技术机理 → 核心算法 → 原型系统 → 历史回放 → 旁路试运行 → 第三方测试 → 两场站示范

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
