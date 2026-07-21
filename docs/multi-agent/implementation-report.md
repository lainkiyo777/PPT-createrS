# Multi-Agent PPT 架构实施报告

实施日期：2026-07-21
最终状态：架构重构与配置 Gate 冒烟通过；未生成完整 PPT

## 1. 完成内容

### 持久化 Orchestrator

- 建立 15 状态的 `build-state.yaml` 状态机。
- 限制只有 Orchestrator 可以 transition，并要求每次 transition 提供真实 evidence file。
- 首次 invocation 不消费用户输入，固定生成 pending config 并停在 `awaiting_configuration`。
- 防止单次执行进入两个未来 `awaiting_*` 状态。
- `completed` 必须引用代码计算通过的 `gate-decision.json`。

### 多模型路由

- 建立 `agents/model-routing.json`，实现 Orchestrator、Producer、Slide Worker、Low-cost Worker、Reviewer 和 Final Reviewer 的指定模型与职责。
- 实现 Slide Worker complexity escalation 和 Low-cost Worker 显式 fallback。
- 模型不可用且没有声明 fallback 时抛错，不做静默替换。
- 把每次决策追加写入 `model-routing-manifest.json`。

### Producer–Reviewer 隔离

- Reviewer session 只读，拒绝文件写入、image2、presentation、PPTX mutation 与 apply_patch。
- 只允许读取冻结 review-pack 内的路径。
- review-pack 排除 Producer 对话、日志、自评、模型信息和总结；每个文件记录 SHA-256。
- `evaluation.json` 由宿主以 Orchestrator 身份追加保存，Producer/Worker 无权修改。

### Rubric、Schema 与确定性 Gate

- 新增 style candidate、preview、final delivery、speaker notes 四套 Rubric。
- 最终权重和阈值按需求实现：minimum score 85，maximum critical failures 0。
- 新增 evaluation 与 slide spec JSON Schema。
- 代码忽略 Reviewer 自报 `total_score`/`passed`，重算加权总分。
- 无 evidence 的 issue 形成验证错误并阻止通过。
- 每轮审核由 Orchestrator 生成 `deterministic-checks.json`，合并 image2、selected-style、计数、分辨率、字体、数据、PPTX 与 notesSlides 检查。

### 有界修订

- 失败轮次写入不可变 `artifacts/round-XX/structured-issues.json`。
- `revising` 必须等待 `revision-ready.json` 且 `revised_by: producer`，才允许再生成。
- 记录失败发生在 preview 或 final phase，并回到对应再生成状态。
- 第二轮仍失败时转入 `awaiting_human_review`。

### image2 与 presentation 边界

- manual 候选必须由 image2 生成 A/B/C 三套，每套四张图和 style profile。
- manifest 记录 tool、version、prompt、reference、output、timestamp、success、error。
- image2 不可用/失败时构建失败，不允许 presentation fallback。
- presentation 仅允许空白 deck、满版 final image、speaker notes、保存和回读。
- 真实 notesSlides 的数量、映射和文本一致性为硬检查。

## 2. 测试结果

执行命令：

```powershell
python -m unittest discover -s skills/ppt-creaters/tests -v
```

结果：

```text
Ran 72 tests in 6.607s
OK
```

22 项用户必测场景均有直接映射，详见 `docs/multi-agent/test-plan.md`。新增回归还覆盖 model routing、Reviewer 冻结包、host-side deterministic checks、Producer revision evidence 和相对 output path。

脚本语法检查：全部 `scripts/*.py` 通过 `py_compile`。

官方 Skill 校验：

```text
Skill is valid!
```

## 3. 冒烟测试

输入：

- `materials/整合版PPT内容大纲.md`
- `skills/ppt-creaters/references/deck-library/inbox/蓝色模板.pptx`
- manual / guided / style-reference

最终运行目录：`projects/multi-agent-manual-guided-smoke-20260721-r2/output/`

结果：

```text
build_status: awaiting_configuration
waiting for user configuration confirmation
exit_code: 0
```

状态 history 记录 `initialized -> awaiting_configuration`，actor 为 `orchestrator`，evidence 为 pending config、selection report 和 model routing manifest。

确认不存在：

- `deck-config.confirmed.yaml`
- `style-candidates/`
- `image-generation-manifest.json`
- `selected-style.yaml`
- `preview-images/`
- `final-images/`
- `presentation.pptx`

完整终端输出与负向文件检查保存于 `docs/p0/manual-guided-smoke-test.md`。

第一次 CLI 冒烟暴露了相对 output path 被重复拼接的问题；新增 `test_initial_run_accepts_relative_output_path` 后，将 runner 与 state machine 入口统一解析为绝对路径。第二个全新任务重新运行后通过。

## 4. 主要实现文件

- `skills/ppt-creaters/SKILL.md`
- `skills/ppt-creaters/references/multi-agent-contract.md`
- `skills/ppt-creaters/agents/model-routing.json`
- `skills/ppt-creaters/scripts/state_machine.py`
- `skills/ppt-creaters/scripts/model_router.py`
- `skills/ppt-creaters/scripts/workflow_runner.py`
- `skills/ppt-creaters/scripts/review_isolation.py`
- `skills/ppt-creaters/scripts/review_gate.py`
- `skills/ppt-creaters/scripts/review_cycle.py`
- `skills/ppt-creaters/scripts/deterministic_checks.py`
- `skills/ppt-creaters/rubrics/`
- `skills/ppt-creaters/schemas/`
- `skills/ppt-creaters/tests/test_multi_agent_contract.py`

## 5. 明确限制

- 模型路由是 provider-neutral 接口，实际远程模型调用仍需由宿主绑定；未绑定或模型不可用时不得假装成功。
- 本轮没有执行 image2 候选生成、完整 preview/final image、presentation 合成或 24 页视觉 QA，因为冒烟边界明确要求停在配置 Gate。
- `hybrid-editable` 与 `background-only` 保留既有契约；本轮重点验证 production-image 的 image2 provenance、assembly-only 和真实 notesSlides 边界。

## 6. 结论

本轮目标已完成：PPT Creaters 已从单次生成流程升级为多模型、可审计、持久状态、人工 Gate、独立 Reviewer 与确定性放行架构。系统当前停在用户配置选择之前，没有替用户做决定，也没有生成完整 PPT。
