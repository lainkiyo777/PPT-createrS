# Slide 13 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-13.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-13.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Schedule and rollout slide. Generate a clean three-year timeline with milestone nodes and a second rollout lane below, connected by a restrained expansion arrow. Keep every year label, milestone description, rollout paragraph and red implementation principle verbatim. Use the source blue bands, white cards and bottom corner; prioritize reading order and generous whitespace.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 项目进度和推广应用
- 13
- 里程碑节点
- 2027年｜基础研发
- 完成需求、接口和技术方案；完成对象模型、样本库、知识库初版；形成诊断、监督和核验算法原型。
- 2028年｜集成试运行
- 完成云边模型演进、算法中台和业务调度中台；完成两示范场站部署联调及旁路试运行。
- 2029年｜验证验收
- 完成长周期稳定性与典型场景验证；完成第三方评价、72小时现场测试、成果固化及项目验收。
- 推广应用
- 01  贵州区域先行
- 在贵州集控中心及珠雉风电场、茂兰光伏电站形成风电、光伏标准配置和场景模板。
- 02  集团内部复制
- 依托标准接口、低代码流程和算法算子，复制到其他新能源区域公司及相近设备类型。
- 03  行业场景延伸
- 在保持数据与安全边界的前提下，向储能、升压站辅助监控及综合能源场景延伸。
- 实施原则：先历史回放、再旁路运行、后业务嵌入；系统辅助研判，人工终核机制和安全生产责任边界不变。

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
