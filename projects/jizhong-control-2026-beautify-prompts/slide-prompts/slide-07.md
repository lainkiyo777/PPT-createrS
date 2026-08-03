# Slide 07 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-07.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-07.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Technical-route slide. Generate a new but template-consistent architecture/flow diagram: research objects feed a five-task backbone, which terminates in assessment outputs. Keep every source object, task title, arrow phrase, threshold and output chip verbatim, but allow the task bands, nodes, arrows and bottom KPI cards to be rearranged for a clean reading path. Use blue rails, white cards and restrained red metric accents; the result must read as an engineering route, not a decorative infographic.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 研究内容和技术指标
- 7
- 技术路线
- 研究对象
- 视频/红外
- 无人机巡检
- SCADA/CMS
- 气象环境
- 设备台账
- 历史缺陷
- 工单/两票
- 三措两案
- 移动视频
- 规程案例
- 任务1
- 多模态数据与知识底座
- 统一设备对象模型｜事件关联与证据包｜数据质量评价｜样本库、图文知识库与异常知识图谱
- 任务2｜跨模态设备异常诊断
- 异常候选生成 → 多源证据联查 → 同侪/历史对比
- → VLM+RAG综合解释 → 风险标签与处置建议
- 任务3｜检修全过程监督与业务核验
- 工单/票据解析 → 作业前预检 → 作业中视频监督
- → 作业后图文视频核验 → 证据缺口与人工终核
- 任务4｜云边模型演进
- 边缘初筛
- 云端兜底
- 人工确认·样本入库
- 训练蒸馏·灰度发布
- 任务5
- 双中台集成与低代码流程编排
- 算法中台 + 业务调度中台｜组件化封装｜集控与两场站部署｜旁路试运行与工程验证
- 考核输出
- 平台与资源
- 平台1套
- 样本库/知识库各1套
- 诊断效果
- 虚警过滤率、准确率
- 均≥90%
- 业务效率
- 审核效率提升
- ≥80%
- 演进能力
- 核心算法≥4类
- 迭代周期≤7天
- 示范成果
- 2个示范场站
- 第三方测试评价

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
