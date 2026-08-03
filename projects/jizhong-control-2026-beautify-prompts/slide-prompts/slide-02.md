# Slide 02 prompt — template-preserving beautification

- **Reference image:** `../reference-slides/source-slide-02.png`
- **Template application mode:** `adaptive-layout` (high-fidelity, template language locked; composition flexible)
- **Content policy:** exact source text; no copy editing, no new claims, no page-count change

## Copy-ready prompt

```text
You are beautifying one existing PowerPoint slide, not redesigning the presentation from scratch.
Use the attached reference image source-slide-02.png as the primary template and composition reference.
Keep the 16:9 canvas, the white Huaneng template, blue title rule, upper-right logo, bottom blue rule, angled corner and page number.
Use the source page as a high-fidelity template anchor, preserving the title band, logo, footer and visual rhythm. You may reorganize the composition for clarity: move or resize cards, change columns, merge or split content groups, and add architecture diagrams, flowcharts, swimlanes, timelines or restrained charts when they visualize existing source content.
Do not add, remove, translate, summarize or reinterpret any information. Do not change any number, unit, symbol, label, metric, caveat or process step. A structural change is acceptable only if every source text item remains present and the page still reads as the same topic.
Use Microsoft YaHei/微软雅黑 or the closest Chinese sans-serif. Keep title 28–32 pt equivalent, section labels 20–22 pt, body 17–19 pt where space allows, dense content at least 14 pt and footnotes 12–14 pt. Never solve overflow by shrinking all text.
Use the source palette only: Huaneng blue, deep navy, black/dark gray, light blue-gray panels and restrained red emphasis. Keep flat white cards, thin blue borders, blue header bars and simple arrows. No dark tech background, neon glow, 3D effect, unrelated stock imagery, new logo or watermark.
The image layer may polish background, cards, borders, non-text decoration and safe crops only. Render every Chinese phrase, number, table, chart label, arrow caption and page number later with a deterministic vector/text overlay from the verbatim list below. If space is tight, reflow within the existing zones; do not omit content.

PAGE-SPECIFIC COMPOSITION
Summary slide. Recompose the dense summary into one clear left-to-right closed-loop architecture (多源参数 → 边缘感知 → 证据推理 → 业务核验 → 自适应演进) with two compact evidence panels and a lower comparison/推广 strip. The source five-step content, two middle-platform bars, necessity/innovation/benefit/feasibility statements and comparison arrows must all remain. Generate clean blue architecture nodes and connectors, then place every Chinese phrase and metric as deterministic overlay; do not replace the content with a generic dashboard.

VERBATIM SOURCE TEXT — MUST BE PRESERVED EXACTLY
- 项目汇报总结
- 技术原理：统一设备对象与时间窗口，聚合视觉、时序、环境、业务和知识证据，驱动诊断—核验—反馈闭环
- 01 多源参数
- 视觉·红外·时序
- 气象·历史·同侪
- 票据·规程·案例
- 02 边缘感知
- 协议适配与时空对齐
- 动态基线·轻量模型
- 生成异常候选
- 03 证据推理
- 统一事件包
- 跨模态特征与证据聚合
- VLM+RAG专业解释
- 04 业务核验
- 作业前中后监督
- 图文视频一致性判断
- 智能预审·人工终核
- 05 自适应演进
- 确认结果样本化
- 训练评测·模型蒸馏
- 边缘发布·监测回滚
- 算法中台｜模型·知识·样本·训练·发布
- 业务调度中台｜事件·流程·终核·统计
- 终核及处置反馈 → 样本沉淀 → 训练评测 → 模型蒸馏 → 边缘下发
- 系统关系：算法中台提供模型能力，业务调度中台组织事件与流程，在集控中心及风电、光伏场站验证
- 必要性
- • 单模态、静态阈值告警虚警多
- • 工单/两票/三措两案依赖人工核文核图
- • 长尾异常模型依赖厂家，扩展周期长
- 创新性与先进性
- • 拟提出视觉—时序—环境—历史—同侪—知识证据链诊断
- • 拟研发作业前中后监督与图文视频语义核验机制
- • 拟构建云端兜底、边缘蒸馏下发及双中台编排机制
- 量化增值与成果
- • 虚警过滤率、典型异常识别准确率≥90%
- • 审核效率提升≥80%；新异常迭代≤7天
- • 核心算法≥4类；平台/样本库/知识库各1套
- • 风电、光伏2个示范场站
- 与已有技术对比及推广可行性
- 现有技术
- →
- 本项目技术增量
- 单模态/静态阈值
- →
- 多源证据链联合研判
- 字段校验/人工审核
- →
- 图文视频语义核验
- 厂家黑盒模型
- →
- 云端兜底+边缘自演进
- 推广可行性
- 利旧现有视频、SCADA/CMS和业务系统；采用标准接口、组件化算法与低代码流程；风电、光伏两场站验证后可向集团复制。
- 2

FINAL CHECKS
- The finished page is recognizably the same source template and page family.
- All verbatim text, numbers, symbols, source-material labels and page number are present and readable.
- No title is awkwardly wrapped; no body text is microscopic; no card, table, arrow or frame collides with another.
- No visual element changes the source meaning or implies a new claim.
```
