# Manual/Guided P0 冒烟测试日志

- 执行日期：2026-07-21
- 任务目录：`projects/p0-manual-guided-smoke-20260721/`
- 风电 Markdown：`materials/整合版PPT内容大纲.md`
- 蓝色模板：`skills/ppt-creaters/references/deck-library/inbox/蓝色模板.pptx`
- 预期终点：`build_status: awaiting_configuration`
- 用户输入：无

## 启动命令

```powershell
python skills/ppt-creaters/scripts/workflow_runner.py projects/p0-manual-guided-smoke-20260721/output
```

## 展示的配置项

```text
workflow_mode: manual
selection_mode: guided

presentation_type (recommended: technical-report)
  1) research-report
  2) technical-report
  3) introductory
  4) academic-defense
  5) product-solution
  6) executive-summary
  7) training-course

visual_style (recommended: academic-clean)
  1) academic-clean
  2) university-formal
  3) technology-dark
  4) industrial-technical
  5) business-data
  6) light-modern
  7) institutional-red

presentation_effect (recommended: formal-report)
  1) keynote
  2) formal-report
  3) academic
  4) storytelling
  5) dashboard
  6) documentary
  7) minimal

template_application_mode (recommended: style-reference)
  1) style-reference
  2) adaptive-layout
  3) strict-template

output_mode (recommended: production-image)
  1) production-image
  2) hybrid-editable
  3) background-only

notes_mode (recommended: full)
  1) none
  2) summary
  3) full

target_duration_minutes (recommended: 20)
  1) 10
  2) 15
  3) 20
  4) 30
  5) 45

content_density (recommended: medium)
  1) low
  2) medium
  3) high
```

首次提示等待用户选择 `presentation_type`。标准输入为空，运行器未应用推荐项，随即停止。

## 运行结果

```text
build_status: awaiting_configuration
waiting for user configuration confirmation
exit_code: 0
```

`output/build-state.yaml`：

```yaml
build_status: "awaiting_configuration"
workflow_mode: "manual"
selection_mode: "guided"
last_stage: "configuration"
run_id: "6adc89a337ea480f8d52c97dce2f40fe"
updated_at: "2026-07-21T08:38:11.618044+00:00"
transition_history: []
message: "waiting for user configuration confirmation"
```

## 工件检查

```text
deck-config.yaml=True
deck-brief.yaml=True
build-state.yaml=True
build-status.json=True
config-selection-report.md=True
deck-config.confirmed.yaml=False
style-candidates=False
image-generation-manifest.json=False
selected-style.yaml=False
preview-images=False
final-images=False
presentation.pptx=False
```

## 结论

通过。新 manual/guided 任务展示了八项配置选择，模板上传未被视为确认。本次执行只停在 `awaiting_configuration`，未自动确认、未调用 image2、未生成候选图、未生成预览、未生成完整 24 页、未调用 presentation、未生成 PPTX。

---

# Multi-Agent v2 全新冒烟测试

- 执行日期：2026-07-21
- 任务目录：`projects/multi-agent-manual-guided-smoke-20260721-r2/`
- 风电 Markdown：`materials/整合版PPT内容大纲.md`
- 蓝色模板：`skills/ppt-creaters/references/deck-library/inbox/蓝色模板.pptx`
- 显式模式：`workflow_mode: manual`、`selection_mode: guided`、`template_application_mode: style-reference`
- 用户输入：无

## 启动命令

```powershell
python -X utf8 skills/ppt-creaters/scripts/workflow_runner.py projects/multi-agent-manual-guided-smoke-20260721-r2/output
```

## 完整终端输出

```text
必须先确认配置；上传模板只提供 template_source，不代表确认任何选项。
workflow_mode: manual; selection_mode: guided（默认）
presentation_type (recommended: 'technical-report')
  1) research-report
  2) technical-report
  3) introductory
  4) academic-defense
  5) product-solution
  6) executive-summary
  7) training-course
visual_style (recommended: 'academic-clean')
  1) academic-clean
  2) university-formal
  3) technology-dark
  4) industrial-technical
  5) business-data
  6) light-modern
  7) institutional-red
presentation_effect (recommended: 'formal-report')
  1) keynote
  2) formal-report
  3) academic
  4) storytelling
  5) dashboard
  6) documentary
  7) minimal
template_application_mode (recommended: 'style-reference')
  1) style-reference
  2) adaptive-layout
  3) strict-template
output_mode (recommended: 'production-image')
  1) production-image
  2) hybrid-editable
  3) background-only
notes_mode (recommended: 'full')
  1) none
  2) summary
  3) full
target_duration_minutes (recommended: 20)
  1) 10
  2) 15
  3) 20
  4) 30
  5) 45
content_density (recommended: 'medium')
  1) low
  2) medium
  3) high
build_status: awaiting_configuration
waiting for user configuration confirmation
```

退出码：`0`

## 状态证据

```yaml
build_status: "awaiting_configuration"
workflow_mode: "manual"
selection_mode: "guided"
last_stage: "configuration"
transition_history:
  - from: initialized
    to: awaiting_configuration
    stage: configuration
    actor: orchestrator
    evidence_files:
      - deck-config.pending.yaml
      - config-selection-report.md
      - model-routing-manifest.json
message: "waiting for user configuration confirmation"
revision_round: 0
artifact_version: "round-00"
```

实际生成文件只有：

```text
build-state.yaml
build-status.json
config-selection-report.md
deck-brief.yaml
deck-config.pending.yaml
deck-config.yaml
model-routing-manifest.json
```

负向检查全部通过：

```text
deck-config.confirmed.yaml=False
style-candidates=False
image-generation-manifest.json=False
selected-style.yaml=False
preview-images=False
final-images=False
presentation.pptx=False
```

结论：通过。运行器展示八项配置后立即停在 `awaiting_configuration`；没有替用户确认，没有调用 image2，没有生成候选、预览、final image 或 PPTX。
