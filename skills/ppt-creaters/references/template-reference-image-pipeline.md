# v2.1 模板参考型 image-first 流程

本契约固化了已验证的“参考模板但重新构图”路线。模板只提供视觉语言，当前内容仍然经过需求解析、叙事大纲、逐页规格、预览审核、高清生成和整页图片合成。

## 适用定义

当用户说“按这个模板美化”“参考模板风格”或上传模板但没有明确要求逐页复制时，使用：

```yaml
template_application_mode: style-reference
```

该模式继承颜色、字体语言、留白、形状、图标、图片处理、图表语言和页面节奏；不复制源页文字、精确文本框坐标或 duplicate-slide 映射。每页必须根据当前语义选择 `dominant_visual`，可以重新安排标题、正文、图表、流程、架构和场景图。

`adaptive-layout` 可以参考页面家族并移动、缩放、删除和新增元素；`strict-template` 只有用户明确选择品牌模板保真时才可使用，不能由“上传了 PPTX”推断。

## 已验证的生产顺序

1. 读取源 Markdown/PPTX，确认页数、原文、数字和用户不可修改的素材。
2. 解析模板每页，输出 `style-profile.yaml` 和 `reference-slides/source-slide-XX.png`。参考页图只用于视觉学习和提示词，不是最终页面底图。
3. 先写 `outline.md`，再写独立 `slide-specs/slide-XX.yaml`。每个规格写明页面语义、`dominant_visual`、可变布局、模板继承项、禁止继承项、图表/架构需求、精确文字来源和验收条件。
4. 为每页生成 prompt，明确“学习视觉风格、不复制原文字、不复制精确文本框布局、按当前语义重新构图”。Codex 宿主直接调用实际可用的 `image_gen`（或经宿主注入且明确声明的 `image2`）逐页生成预览；代码不得伪造 API、CLI、输出文件或成功状态。
5. 预览图按页审核：先改对应 slide spec 和 prompt，再重生成该页；审核未通过时不得直接改 PPT 合成代码。
6. 预览通过后，在正式模式按已确认规格和参考图逐页生成 `final-images/slide-XX.png`。高清生成不得改变信息结构、关键数字或页面语义；图片内准确中文、数字、表格和图表由确定性渲染或已审核的最终页面素材保证。
7. 合成阶段只创建空白 16:9 PPTX，并把每一张 final image 按页码以 `full-slide` 全幅铺满插入，可写入对应 speaker notes。禁止重新排版正文、表格、图表，禁止重绘、替换、非等比裁切已确认图片。
8. 渲染 PPTX 后执行页数、图片数量、16:9、单图铺满、notes、缺失文件、低清和越界检查，生成 `qa-report.md` 与 `generation-report.md`。

## 工具边界与退化

视觉生成器是宿主能力，不是本仓库可假定存在的命令。运行时必须记录 `tool_name`、模型/工具版本、prompt 路径、参考图、输出路径、时间和成功/错误状态。若宿主没有可用图片工具，应明确失败并输出完整 prompt、命名规则和待执行清单；不得用 `presentation`、截图或 PIL 冒充图片模型结果。

PPT 合成器同样由宿主注入。不存在时，输出素材清单和合成任务清单，不能宣称 PPTX 已生成。

## v2.1 示例证据

`projects/jizhong-control-2026-beautify-prompts/` 保存了一套 14 页模板参考型实测：

- `reference-slides/`：逐页模板参考图；
- `slide-prompts/`：逐页 prompt，均要求保持模板语言但按语义重构；
- `generated-previews/`：14 张 16:9 预览图及联系表；
- `presentation.pptx`：每页单张全幅图片的可打开 PPTX；
- `prompt-index.md`、`template-beautify-contract.md`、`source-text-inventory.md`：输入、约束和生成证据。

该示例用于回归视觉路线，不把预览图自动宣称为正式高清交付。生产运行必须继续创建独立 `preview-images/` 与 `final-images/`，并让 `template_reference_pipeline.py validate-output` 通过。

## 可运行验证

验证正式输出目录：

```text
python skills/ppt-creaters/scripts/template_reference_pipeline.py validate-output <output-dir> --slide-count 14
```

验证本仓库示例（示例明确记录了预览复用限制）：

```text
python skills/ppt-creaters/scripts/template_reference_pipeline.py validate-demo projects/jizhong-control-2026-beautify-prompts
```

验证器只检查实际存在的文件和 PPTX 结构；它不会伪造图片生成或替代人工视觉审核。
