# PPT Creaters

> Version 2.0.0 — Auditable Multi-Agent PPT Production Workflow

PPT Creaters 是一个面向 AI Agent 的可审计 PowerPoint 生产系统。v2.0.0 将 PPT 生成从“一次性生成任务”升级为具备 **持久状态管理、人工确认 Gate、多模型协作、独立 Reviewer 和确定性质量控制** 的生产流水线。

核心原则：

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

模型返回的 `passed` 或 `total_score` 不作为最终依据。

---

## 🚀 Quick Start

### 1. 准备配置

创建：

```text
deck-config.yaml
deck-brief.yaml
```

默认模式：

```yaml
workflow_mode: manual
selection_mode: guided
```

### 2. 启动 Workflow

```bash
python skills/ppt-creaters/scripts/workflow_runner.py <output-dir>
```

### 3. 验证

```bash
python -m unittest discover -s skills/ppt-creaters/tests -v

python scripts/validate_p0.py <output-dir>
```

---

## 📦 Output Structure

```text
output/
├── build-state.yaml
├── model-routing-manifest.json
├── image-generation-manifest.json
├── selected-style.yaml
├── slide-specs/
├── preview-images/
├── final-images/
├── speaker-notes/
├── review-pack/
├── reviews/
├── presentation.pptx
└── qa-report.md
```

---

## 🧪 Validation

v2.0.0 测试覆盖：

- workflow state machine
- model routing
- reviewer isolation
- deterministic gate
- artifact validation
- PPTX notes round-trip

当前测试结果：

```text
Ran 72 tests
OK
```

---

## ⚠️ Current Limitations

- 模型路由目前为 provider-neutral 接口，实际模型调用需要宿主绑定。
- image2、presentation adapter 不可用时不会静默降级。
- v2.0.0 架构升级重点是生产流程可靠性，不包含完整 24 页 PPT 视觉产出验证。

---

## 📚 Documentation

主要文档：

```text
docs/multi-agent/
├── architecture-design.md
├── current-state-audit.md
├── implementation-report.md
├── model-routing.md
└── test-plan.md
```

---

## License

See repository license for details.
