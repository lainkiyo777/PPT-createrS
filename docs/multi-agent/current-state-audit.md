# PPT Creaters 当前状态审计

审计日期：2026-07-21
审计范围：`skills/ppt-creaters/`、相关测试、延长风电 manual/guided 工作流
本轮边界：只重构工作流架构，不生成完整 PPT

## 1. 审计结论

原工作流具备内容规划、模板引用、图片优先输出和基础校验能力，但控制权集中在单次生成流程中，缺少可执行的多模型职责边界、独立 Reviewer 上下文和由确定性代码控制的最终放行。用户确认的六项 P0 失败因此不是页面样式问题，而是 orchestration、authorization 与 auditability 问题。

修复后的系统将生成流程拆为 Orchestrator、Producer、Worker、Reviewer/Final Reviewer 和 deterministic code 五类权限域，以持久化状态、证据文件和不可变审核轮次约束执行。

## 2. 基线缺口与风险

| 审计项 | 基线问题 | 风险 | 修复状态 |
|---|---|---|---|
| 配置 Gate | 模板上传可能被错误理解为用户已完成选择 | 未经授权生成内容或锁定模板模式 | 已修复：首次运行固定写 pending config 并停止 |
| 三套候选 | manual 模式未形成可验证的 A/B/C image2 候选链 | 用户没有真实选择权，候选来源不可审计 | 已修复：12 次 image2 调用和 manifest 为硬前置 |
| style-reference | 未把模板视觉语法稳定转换为逐页 image prompt | 容易退化为复制源页或继承文本框 | 已修复：语义重构、独立 spec 与 prompt 字段为硬约束 |
| presentation 边界 | 页面设计与最终合成职责混杂 | image2 失败时可能被原生 PPT 页面兜底 | 已修复：只允许空白 deck、满版图、notes、保存和回读 |
| Speaker notes | 外部 Markdown 可能替代真实 notesSlides | 交付 PPTX 无法在 PowerPoint 演讲者视图中使用 | 已修复：OOXML notesSlides 数量、映射和文本回读为硬检查 |
| 人工 Gate | 单次执行可能连续跨越多个等待阶段 | 用户确认被系统自动代替 | 已修复：持久状态和 multi-await violation 检测 |
| 模型职责 | 无显式 role-to-model 路由和不可用处理 | 模型分工可被静默忽略 | 已修复：显式配置、审计 manifest、声明式 fallback |
| Reviewer 独立性 | Reviewer 可能看到 Producer 自评或修改产物 | 审核受污染，无法证明独立 | 已修复：冻结 review-pack、只读 capability facade |
| 最终 PASS/FAIL | 生成模型可在文本中自行宣布通过 | 分数、critical failure 与事实检查不可复现 | 已修复：代码重算分数并合并 deterministic checks |
| 修订循环 | 失败后缺少上限和不可变轮次 | 无限重试或覆盖上轮证据 | 已修复：两轮上限，之后 `awaiting_human_review` |

## 3. 现有可复用资产

- `scripts/validate_p0.py`：配置、模板、字体、数据、notes 与输出模式综合校验。
- `scripts/template_policy.py`：`style-reference`、`adaptive-layout`、`strict-template` 语义约束。
- `scripts/artifact_guards.py`：image2 manifest、候选包、slide spec 与 selected-style 前置条件。
- `scripts/presentation_guard.py`：组装前置条件、PPTX 对象结构和 notesSlides 回读。
- `scripts/workflow_runner.py`：本轮升级为唯一状态驱动入口。
- 既有 54 个 P0/模板/管线测试：为新架构提供回归基线。

## 4. 本轮新增控制面

- `agents/model-routing.json` 与 `scripts/model_router.py`
- `scripts/state_machine.py`
- `scripts/review_isolation.py`
- `scripts/review_gate.py`
- `scripts/review_cycle.py`
- `scripts/deterministic_checks.py`
- `schemas/evaluation.schema.json`
- `schemas/slide-spec.schema.json`
- 四套 `rubrics/*.yaml`
- multi-agent contract tests 与五份架构文档

## 5. 剩余边界

模型路由层当前是 provider-neutral 接口：它选择并审计模型，但具体模型调用由宿主运行时绑定。Reviewer 也通过只读 session 与 review request 对接宿主，而不是在仓库脚本中直接调用远程模型。这是有意的职责分离；若宿主未提供指定模型或 image2/presentation adapter，构建必须失败或等待，不得静默降级。

本轮不验证完整 24 页视觉产出，也不运行 image2 或 presentation。真实冒烟测试只验证首次配置 Gate。
