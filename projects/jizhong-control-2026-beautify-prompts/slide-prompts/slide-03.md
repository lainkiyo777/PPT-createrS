# Slide 03 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-03.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-03.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Section divider. Preserve the strong vertical blue block at left, the large white section numeral treatment, the centered five-item agenda and the small top-right logo. Align the five numbered diamonds and text to a clear vertical rhythm. Do not add explanatory content or imagery.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 项目背景和研究意义
- 研究内容和技术指标
- 预期成果和技术创新
- 经费预算和经济效益
- 项目进度和推广应用

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
