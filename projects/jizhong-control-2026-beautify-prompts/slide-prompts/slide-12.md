# Slide 12 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-12.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-12.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Economic-benefits slide. Keep the three value pillars and their exact text, but recompose them as three metric cards connected by a restrained value-chain arrow or a small waterfall-style logic diagram derived only from the supplied figures. Keep 168万元/年, 2.1年, 三类价值, all supporting calculations and the disclaimer verbatim. Do not imply audited results or add a new financial claim.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 经费预算和经济效益
- 12
- 经济效益产出
- 01  直接经济效益
- 168万元/年
- 示范年度净效益
- 年度节资效益约201万元
- 人工审核节约96万元
- 减少非计划停机损失60万元
- 减少外委算法定制45万元
- 扣除年度运维成本约33万元
- 02  推广应用效益
- 2.1年
- 单套静态投资回收期
- 单套推广投入约350万元
- 单套年净收益约170万元
- 计划2030—2032年推广9套
- 形成算法、知识和流程模板的规模化复制
- 03  安全与管理效益
- 三类价值
- 安全提升｜管理提效｜资产沉淀
- 提升异常早期发现、检修过程监督和闭环验收能力
- 减少重复审核和漏判风险
- 沉淀集团自主样本、知识和模型资产
- 降低对单一厂商依赖
- 注：经济效益为申报测算值，最终以试点运行台账和财务核定结果为准。

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
