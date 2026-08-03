# Slide 01 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-01.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-01.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Cover slide. Keep the existing centered black/red title hierarchy and the horizontal blue divider. Retain the right-aligned Huaneng logo and the six metadata rows below. Improve the long project title's line breaking so no final word is stranded; keep the red '技术审查答辩' emphasis, row baselines, equal left labels, and generous white space. Make the 1450万元 and research period readable without changing any characters.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 项目名称：
- 基于云边协同多模态大模型的新能源装备状态感知与管控闭环技术研究及应用
- 申报单位：
- 中国华能集团有限公司贵州分公司
- 承办单位：
- 贵州清洁能源分公司
- 拟承担单位：
- 西安热工研究院有限公司
- 研究周期和经费：
- 3年（2027—2029年）        1450万元
- 负  责  人：
- 安欣、徐超        技术负责人：王靖程
- 共14页  2026年XX月XX日

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
