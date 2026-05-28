# 后端说明 — 2026-05-27--admin-ai-settings-gateway-ui

> **本包无新增后端实现** · API 已由前序功能包交付 · `backend_done` 为回归确认。

## 启动与环境

| 项 | 值 |
|----|-----|
| 启动 | `cd server && uv run chainup-agent-api` |
| Base URL | http://127.0.0.1:8080 |
| 迁移 | 无本包专用迁移（defaults 存 `gateway_defaults` 存量表） |
| 功能包 OpenAPI | `handoff/features/2026-05-27--admin-ai-settings-gateway-ui/api.openapi.yaml` |

## 已实现（勿重复开发）

| 能力 | 功能包 | 模块 |
|------|--------|------|
| `intentNluUseLlm` | `2026-05-26--nlu-llm-strategy` | `application/admin_ai_settings.py` · `recognize_intent_full` |
| `telegramLlmNarrate`（9 字段） | `2026-05-26--telegram-llm-narrate` | `application/telegram_llm_narrate_policy.py` · `telegram_bound_reply` |
| 深度合并 PATCH | 存量 | `admin_ai_settings.py` · `_deep_merge_defaults` / `_validate_gateway_patch` |

## 路由（FE 消费）

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/v1/admin/ai/defaults` | 含 `intentNluUseLlm` + 完整 `telegramLlmNarrate`（9 boolean） |
| PATCH | `/api/v1/admin/ai/defaults` | 部分字段更新；可选 `If-Match` → **409** `AGENT_AI_SETTINGS_VERSION_CONFLICT` |

## 错误码（本包 UI 相关）

| code | HTTP | 场景 |
|------|------|------|
| `VALIDATION_ERROR` | 422 | `telegramLlmNarrate` 未知字段 / 非 boolean |
| `AGENT_AI_SETTINGS_VERSION_CONFLICT` | 409 | If-Match 版本冲突 |
| `AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG` | 422 | `scenarioChatModel` 等引用未登记模型（AC-7 存量） |
| `ADMIN_CONSOLE_AUTH_REQUIRED` | 401 | 无 Bearer |

## curl 示例

```bash
# 登录（env 模式示例；database 模式用 seed-admin 账户）
TOKEN=$(curl -s -X POST http://127.0.0.1:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"YOUR_USER","password":"YOUR_PASS"}' | jq -r .access_token)

# GET — TC-01 / AC-2
curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8080/api/v1/admin/ai/defaults \
  | jq '{intentNluUseLlm, telegramLlmNarrate}'

# PATCH — 仅 NLU（AC-3）
curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  http://127.0.0.1:8080/api/v1/admin/ai/defaults \
  -d '{"intentNluUseLlm":true}'

# PATCH — 仅 narrate 单场景（AC-4，其它 8 键保持不变）
curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  http://127.0.0.1:8080/api/v1/admin/ai/defaults \
  -d '{"telegramLlmNarrate":{"readMarketDepth":true}}'

# PATCH — 非法键（TC-04 P1）→ 422
curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  http://127.0.0.1:8080/api/v1/admin/ai/defaults \
  -d '{"telegramLlmNarrate":{"notAField":true}}'
```

## 自测（回归）

```bash
cd server && uv run pytest tests/test_nlu_llm_strategy.py tests/test_telegram_llm_narrate.py -q
# 2026-05-26：19 passed
```

| 本包 TC | 覆盖方式 | 结果 |
|---------|----------|------|
| TC-01 | pytest GET defaults + 本机 curl | ✅ 9 narrate 键 + boolean |
| TC-02 | `test_admin_defaults_intent_nlu_use_llm_patch_get` | ✅ |
| TC-03 | `test_admin_defaults_telegram_llm_narrate_*`（narrate 包） | ✅ 部分 PATCH 不覆盖其它键 |
| TC-04 | 本机 curl 未知字段 | ✅ **422** `VALIDATION_ERROR` |
| TC-05 | `test_api.py` · `test_admin_ai_gateway_defaults_patch_422_unknown_model_id` 等 | ✅ 存量 scenario 模型 |

## 与功能包 OpenAPI 差异

| 项 | 说明 |
|----|------|
| 无 | 行为与 `api.openapi.yaml` 一致；全量 schema 见 `product-doc/specs/openapi/admin/ai-settings.yaml` |

## 关联

- `handoff/features/2026-05-26--nlu-llm-strategy/`
- `handoff/features/2026-05-26--telegram-llm-narrate/`
- `product-doc/specs/openapi/admin/ai-settings.yaml`
