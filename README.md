# PPT Creaters

Version 2.1.0 of the image-first Codex Skill for producing presentation decks.

PPT Creaters 是一个面向 AI Agent 的可审计 PowerPoint 生产系统。v2.0.0 将 PPT 生成从“一次性生成任务”升级为具备 **持久状态管理、人工确认 Gate、多模型协作、独立 Reviewer 和确定性质量控制** 的生产流水线。

- `skills/ppt-creaters/`: reusable Codex Skill and its templates, contracts, tests, and validators.
- `materials/整合版PPT内容大纲.md`: source Markdown used for the included deck.
- `output/`: the verified 24-slide v1.0.0 image-first production artifact, including outline, independent slide specs, preview images, final images, PPTX, QA report, and generation report.
- `skills/ppt-creaters/templates/` and `scripts/validate_p0.py`: the P0 configuration, typography, data, notes, output-mode, and gate contracts.
- `projects/jizhong-control-2026-beautify-prompts/`: the 14-page template-reference regression artifact that learns a blue PPTX template, generates per-page image prompts/previews, and assembles an image-only PPTX.

> 模型负责创造，代码负责验证；系统不会让模型自行宣布成功。

---

## ✨ v2.0.0 新特性

### 1. 多 Agent 生产架构

v2.0.0 引入明确职责分离：

| 角色 | 职责 |
| --- | --- |
| Orchestrator | 管理流程状态、权限、人工 Gate 和模型路由 |
| Producer | 负责叙事设计、视觉规划、slide spec 和修改 |
| Slide Worker | 扩展页面结构、文案和演讲备注 |
| Low-cost Worker | 执行解析、分类、检查等机械任务 |
| Reviewer | 在隔离环境中进行独立审核 |
| Deterministic Code | 执行最终 PASS/FAIL 判断 |

---

### 2. 持久化 Workflow State

所有生产过程由状态机驱动：

```text
initialized
  ↓
awaiting_configuration
  ↓
generating_style_candidates
  ↓
awaiting_style_selection
  ↓
generating_slide_specs
  ↓
generating_previews
  ↓
awaiting_preview_approval
  ↓
generating_final_images
  ↓
assembling_ppt
  ↓
reviewing
  ↓
final_qa
  ↓
completed
```

每次状态变化都会记录：

- actor
- timestamp
- stage
- evidence files
- transition message

---

### 3. Human Gate 人工确认机制

系统不会自动跳过关键决策。

首次运行会停留在：

```text
awaiting_configuration
```

等待用户确认：

- presentation type
- visual style
- template mode
- output mode
- notes mode
- content density
- target duration

模板上传不会被视为用户授权。

---

### 4. Image-first Visual Pipeline

v2.0.0 强化 image-first 生产模式：

```text
source
 → outline
 → slide specs
 → image generation
 → preview review
 → final images
 → PPTX assembly
 → QA
```

最终 PPTX 默认采用：

- 空白 16:9 deck
- 每页一张完整 final image
- 自动写入 speaker notes
- 回读验证 notesSlides

---

### 5. 独立 Reviewer 与 Deterministic Gate

Reviewer 只访问冻结的 `review-pack`：

禁止读取：

- Producer 对话
- 模型自评
- 生成日志
- 说服性总结

最终通过条件由代码重新计算：

```text
passed =
score >= 85
AND critical_failures == 0
AND deterministic_checks_passed == true
AND schema_errors == 0
```

When a template is supplied for visual reference, v2.1 adds an explicit route:

```text
template PPTX → style profile + per-page reference images
→ semantic re-composition → host image_gen previews
→ review → high-resolution final images → full-slide image-only PPTX
```

The template is not silently treated as a duplicate-slide layout. `style-reference` is the default; `strict-template` requires explicit user selection. Run `python skills/ppt-creaters/scripts/template_reference_pipeline.py validate-demo projects/jizhong-control-2026-beautify-prompts` to check the checked-in example.

The included `presentation.pptx` is intentionally image-only: each slide is one approved final image covering the full 16:9 canvas.
