# Multi-Agent PPT 测试计划

## 1. 策略

测试分为五层：配置/人工 Gate、模板语义、image2 provenance、Reviewer/确定性 Gate、PPTX/notes round-trip。先写失败测试，再实现最小确定性约束；禁止通过放宽断言来修复回归。

主命令：

```powershell
python -m unittest discover -s skills/ppt-creaters/tests -v
```

## 2. 用户要求的 22 项测试映射

| # | 必测行为 | 实际测试 |
|---:|---|---|
| 1 | 默认运行停在 `awaiting_configuration` | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_01_default_stops_at_awaiting_configuration` |
| 2 | 上传模板不能跳过配置选择 | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_02_template_upload_does_not_skip_configuration` |
| 3 | manual 模式生成三个候选 | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_03_manual_mode_generates_exactly_three_image2_candidates` |
| 4 | 三个候选必须来自 image2 | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_04_candidates_not_generated_by_image2_fail` |
| 5 | manifest 缺失时失败 | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_05_missing_image_manifest_fails_candidate_validation` |
| 6 | 用户未选候选不能生成完整 PPT/preview | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_06_unselected_candidate_blocks_full_preview` |
| 7 | `selected_by=ai` 失败 | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_07_selected_by_must_be_user` |
| 8 | style-reference 不能全部 duplicate-slide | `test_template_application_mode.TemplateApplicationModeTests.test_style_reference_rejects_full_duplicate_slide_mapping` |
| 9 | style-reference 允许空 `source_slide_reference` | `test_template_application_mode.TemplateApplicationModeTests.test_style_reference_allows_empty_source_slide_reference` |
| 10 | final-images 前不能调用 presentation | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_08_presentation_before_final_images_is_blocked` |
| 11 | presentation 创建文本框或图形时失败 | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_09_presentation_with_textbox_or_shape_fails` |
| 12 | Reviewer 无写权限 | `test_multi_agent_contract.MultiAgentContractTests.test_reviewer_has_no_write_permission` |
| 13 | Reviewer 无 image2 权限 | `test_multi_agent_contract.MultiAgentContractTests.test_reviewer_has_no_image2_permission` |
| 14 | Reviewer 上下文不能包含 Producer 日志 | `test_multi_agent_contract.MultiAgentContractTests.test_reviewer_context_rejects_producer_logs` |
| 15 | Producer 不能修改 evaluation | `test_multi_agent_contract.MultiAgentContractTests.test_producer_cannot_modify_evaluation` |
| 16 | critical failure 存在时不能通过 | `test_multi_agent_contract.MultiAgentContractTests.test_critical_failure_prevents_pass` |
| 17 | 总分低于阈值不能通过 | `test_multi_agent_contract.MultiAgentContractTests.test_score_below_threshold_prevents_pass` |
| 18 | 无证据 issue 无效并阻止通过 | `test_multi_agent_contract.MultiAgentContractTests.test_issue_without_evidence_is_invalid` |
| 19 | 两轮失败后进入 `awaiting_human_review` | `test_multi_agent_contract.MultiAgentContractTests.test_two_failed_rounds_end_at_awaiting_human_review` |
| 20 | 最终 PPTX 无 notesSlides 时失败 | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_10_presentation_without_notes_slides_fails` |
| 21 | 同一次执行不能跨两个 awaiting 状态 | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_11_one_run_cannot_cross_two_future_awaiting_states` |
| 22 | image2 失败时不能 fallback 到 presentation | `test_p0_workflow_architecture.P0WorkflowArchitectureTests.test_12_image2_unavailable_fails_without_presentation_fallback` |

## 3. Multi-Agent 增强测试

| 行为 | 测试 |
|---|---|
| 模型角色与指定模型匹配 | `test_model_router_exposes_required_roles_and_models` |
| 模型不可用不得静默忽略 | `test_unavailable_model_is_not_silently_ignored` |
| 首次运行不消费输入并写 pending config | `test_initial_run_writes_pending_config_and_stops` |
| transition 记录 actor 与 evidence | `test_state_transition_records_actor_and_evidence` |
| Producer 无权 completed | `test_producer_cannot_mark_completed` |
| Orchestrator 无 deterministic PASS 也不能 completed | `test_orchestrator_cannot_complete_without_passed_deterministic_gate` |
| review-pack 冻结且排除 Producer 私有上下文 | `test_review_pack_is_frozen_and_excludes_producer_private_context` |
| 每轮生成 host-side deterministic checks | `test_review_pack_creates_host_side_deterministic_checks` |
| `revising` 等待 Producer revision evidence | `test_revising_waits_for_producer_revision_evidence` |

## 4. 冒烟验收

输入：延长风电 Markdown、蓝色模板、manual/guided/style-reference。

必须满足：

- `build-state.yaml` 与 `build-status.json` 都是 `awaiting_configuration`；
- 生成 `deck-config.pending.yaml`；
- 日志展示八个配置字段及选项；
- 没有 `deck-config.confirmed.yaml`；
- 没有 `style-candidates/` 或 image2 manifest；
- 没有 preview/final images；
- 没有 PPTX。

冒烟运行不得传入自动确认输入，也不得绑定 image2 或 presentation adapter。
