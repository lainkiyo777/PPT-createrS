# Slide 11 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-11.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-11.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Budget slide. Keep the full seven-row table as the authoritative content, but allow a small companion visual (for example, a restrained horizontal share bar or donut) derived only from the exact percentages. Preserve all amounts, percentages, uses, total row and annual arrangement footer verbatim. Use a blue table header, alternating light rows, right-aligned numbers and a red total; the companion chart must never replace or contradict the table.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 经费预算和经济效益
- 11
- 经费预算投入（总额1450万元）
- 预算科目
- 金额（万元）
- 占比
- 主要用途
- 设备费
- 417
- 28.8%
- 边缘计算、视频接入、测试与示范配套设备
- 测试化验加工费
- 426
- 29.4%
- 算法测试、系统加工、第三方评价及现场测试
- 差旅费/会议费
- 137
- 9.4%
- 现场调研、联调、测试及项目会议
- 出版/知识产权费
- 106
- 7.3%
- 专利、软件著作权、规范及论文
- 劳务费
- 23
- 1.6%
- 试验、数据整理及辅助研发劳务
- 薪酬
- 253
- 17.4%
- 项目研发人员投入
- 管理费
- 88
- 6.1%
- 项目组织实施与综合管理
- 合计
- 1450
- 100%
- 年度安排：2027年580万元｜2028年580万元｜2029年290万元

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
