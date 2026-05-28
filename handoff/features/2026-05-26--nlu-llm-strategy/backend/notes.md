# 后端实现说明 — NLU LLM 默认策略

> feature `2026-05-26--nlu-llm-strategy` · `backend_done`

## Base URL

- 本地：`http://127.0.0.1:8080`
- OpenAPI：`http://127.0.0.1:8080/openapi.json`

## 启动

```bash
cd server && uv run chainup-agent-api
```

## 鉴权

- **Admin** `GET|PATCH /api/v1/admin/ai/defaults`：与其它 AI Settings 一致（Bearer / 控制台 JWT，见 `server/docs/BACKEND_SPEC.md`）。
- **Agent** `POST /api/v1/agent/intent/recognize`：须 DB 会话（与其它 Agent 写库路由一致）。

## 实现摘要

| 项 | 位置 |
|----|------|
| `gateway_defaults.intentNluUseLlm`（默认 `false`） | `admin_ai_settings.DEFAULT_GATEWAY_DEFAULTS` |
| 有效策略 `resolve_effective_intent_nlu_use_llm` | `agent_intent_pipeline.py` |
| LLM 分支条件 | `recognize_intent_full`（env **或** Admin defaults） |
| 响应字段 `effectiveIntentNluUseLlm` | `IntentRecognizeResponse` |
| TG timeline `intentNluLlmEnabled` | `telegram_bound_reply._append_intent_nlu_prompt_timeline`（取 **effective**） |

### 有效策略优先级

1. `CHAINUP_AGENT_INTENT_NLU_USE_LLM=true` → 强制尝试 LLM（可回退 `keyword_v1`）
2. `gateway_defaults.intentNluUseLlm=true` → 同上
3. 否则仅 `keyword_v1`

配置变更读 DB merged defaults，**无需重启**进程。

## 错误码

| HTTP | code | 场景 |
|------|------|------|
| 409 | `AGENT_AI_SETTINGS_VERSION_CONFLICT` | PATCH defaults `If-Match` 与 `row_version` 不一致 |
| 422 | `VALIDATION_ERROR` | `intentNluUseLlm` 非 boolean |
| 422 | `AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG` | PATCH 引用不存在的 catalog `modelId` |

Intent recognize：NLU 失败/回退均为 **200** + `nlu.source=keyword_v1`（无 5xx）。

## curl 示例

```bash
# 读取 defaults（含 intentNluUseLlm）
curl -s http://127.0.0.1:8080/api/v1/admin/ai/defaults | jq '.intentNluUseLlm'

# 开启 Admin 侧 LLM 优先（需已 seed catalog）
curl -s -X PATCH http://127.0.0.1:8080/api/v1/admin/ai/defaults \
  -H 'Content-Type: application/json' \
  -d '{"intentNluUseLlm": true}' | jq '.intentNluUseLlm'

# 意图识别（观察 effectiveIntentNluUseLlm / nlu.source）
curl -s -X POST http://127.0.0.1:8080/api/v1/agent/intent/recognize \
  -H 'Content-Type: application/json' \
  -d '{"text": "查询 BTC 账户余额", "locale": "zh-Hans"}' \
  | jq '{nluSource, effectiveIntentNluUseLlm, scenarioId}'

# env 强制（覆盖 Admin false）
CHAINUP_AGENT_INTENT_NLU_USE_LLM=true uv run chainup-agent-api
```

## 测试

```bash
cd server && uv run pytest tests/test_nlu_llm_strategy.py -q
```

## 与契约差异

无（实现与功能包 `api.openapi.yaml` 一致）。
