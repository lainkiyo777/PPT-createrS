# 模型路由与职责边界

配置源：`skills/ppt-creaters/agents/model-routing.json`
实现：`skills/ppt-creaters/scripts/model_router.py`
审计输出：`output/model-routing-manifest.json`

## 1. 路由表

| Role | Primary model | Escalation / fallback | 主要职责 |
|---|---|---|---|
| `orchestrator` | `gpt-5.6-sol` | 无静默 fallback | 需求理解、模式判断、模板语言、叙事、模型路由、人工 Gate、状态控制 |
| `producer` | `gpt-5.6-sol` | 无静默 fallback | 关键页、复杂 spec、风格抽象、image2 prompt、按 issue 修订 |
| `slide_worker` | `gpt-5.6-terra` | high/critical -> `gpt-5.6-sol` | 普通 spec、文案压缩、普通讲稿、批量扩展视觉规则 |
| `low_cost_worker` | `gpt-5.6-luna` | `gpt-5.4-mini` | 解析、分类、YAML/JSON 整理、日志、目录检查、机械测试 |
| `reviewer` | `gpt-5.6-terra` | 无静默 fallback | 预览、叙事、风格匹配、字体/密度/重复性、讲稿审核 |
| `final_reviewer` | `gpt-5.6-sol` | 无静默 fallback | 最终 PPT、关键技术结论、数据一致性、交付质量审核 |

## 2. 路由算法

1. 从 role config 读取 primary model。
2. 若 `slide_worker` 的 complexity 为 `high` 或 `critical`，改用声明的 `escalation_model`。
3. 若宿主提供 `available_models`，检查选定模型是否可用。
4. 仅当 role 显式声明 `fallback_model` 且该模型可用时使用 fallback。
5. 否则抛出 `ModelUnavailableError`，由 Orchestrator 将构建置为 `failed`。
6. 把 role、requested model、selected model、reason、fallback flag 和 timestamp 追加到 audit manifest。

## 3. 不可静默处理的情况

- Reviewer 模型不可用时，不得用 low-cost model 代审。
- Orchestrator/Producer 不得自动降级为 Terra 或 Mini。
- Luna 不可用时只有 `gpt-5.4-mini` 是合法 fallback。
- Slide Worker complexity escalation 是职责升级，不是任意 fallback；审计记录必须保留原 requested model 和原因。
- 当前运行环境没有直接模型调用能力时，仍必须写路由接口与配置，并在宿主绑定前明确等待或失败。

## 4. Reviewer 的额外约束

模型选择不授予工具权限。Reviewer 与 Final Reviewer 无论使用什么模型，都必须在：

- `isolated_context: true`
- `read_only: true`
- review-pack-only path validation
- no `image2`
- no presentation/PPTX mutation
- no filesystem write

的 capability boundary 内运行。

## 5. Manifest 示例

```json
{
  "schema_version": 1,
  "routing_decisions": [
    {
      "role": "reviewer",
      "model": "gpt-5.6-terra",
      "requested_model": "gpt-5.6-terra",
      "reason": "configured primary model",
      "fallback_used": false,
      "timestamp": "2026-07-21T00:00:00+00:00"
    }
  ]
}
```

Manifest 只记录路由事实，不替代模型调用日志、image2 manifest、状态 transition evidence 或 Reviewer evaluation。
