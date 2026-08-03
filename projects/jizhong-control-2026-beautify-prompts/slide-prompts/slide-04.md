# Slide 04 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-04.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-04.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Background/problems slide. Keep the left column as four numbered problem cards and the right column as three framed source-material panels plus the 研究意义 callout. Preserve the exact labels 待插入真实素材 and captions. Improve card heights, line spacing and the visual distinction between problem statements and research significance; keep the bottom blue angled corner and all source text.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 项目背景和研究意义
- 4
- 业务背景与主要问题
- 01  集控审核负荷持续增加
- 场站少人化后，工单、两票、三措两案及闭环材料向集控侧集中，人工逐项核文、核图、核视频，效率和一致性难以保证。
- 02  多源数据尚未形成联合研判
- 视频、红外、SCADA、CMS、气象及历史缺陷分散在不同系统，单模态阈值告警易受天气、反光、动物和设备工况影响。
- 03  检修过程监督和质量验收不足
- 现场作业多依赖事后抽查，安全措施、关键工序、工艺质量与处理前后状态缺少连续、可追溯的图文视频证据。
- 04  新异常场景模型迭代周期较长
- 长尾故障样本少，边缘模型认知能力有限，新场景识别依赖厂家采样、训练和排期，难以形成自主迭代能力。
- 现场/系统素材（待补充）
- 集控中心现场或监控大厅
- 待插入真实素材
- 珠雉风电场
- 待插入真实素材
- 茂兰光伏电站
- 待插入真实素材
- 研究意义：
- 从单点智能识别延伸到“感知—研判—监督—核验—反馈—迭代”闭环，支撑新能源场站少人化运行。

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
