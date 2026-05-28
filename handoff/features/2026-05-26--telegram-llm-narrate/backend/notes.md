# Backend notes — 2026-05-26--telegram-llm-narrate

## Base URL

- 本地：`http://127.0.0.1:8080`
- Admin defaults：`GET|PATCH /api/v1/admin/ai/defaults`

## 启动

```bash
cd server && uv run chainup-agent-api
```

## 实现摘要

- **`gateway_defaults.telegramLlmNarrate`**：9 个 boolean 场景键（见功能包 `brief.md` 表）；seed 与 `read_gateway_defaults_merged` 归一化后全量回显。
- **有效策略**：`resolve_effective_telegram_llm_narrate` / `build_effective_telegram_llm_narrate_map`（`telegram_llm_narrate_policy.py`）— 对应 env `true` 优先，否则 Admin 字段。
- **`build_telegram_bound_user_reply`**：每回合读 merged defaults，九处 narrate/preamble 使用 effective map。
- **时间线**：进入 narrate 分支时 payload 写入 **`effectiveTelegramLlmNarrateEnabled: true`**；未进入 narrate 分支时不写 narrate 事件。

## curl 示例

```bash
# 读取（含九场景默认 false）
curl -s http://127.0.0.1:8080/api/v1/admin/ai/defaults | jq '.telegramLlmNarrate'

# 仅开启 ticker narrate
curl -s -X PATCH http://127.0.0.1:8080/api/v1/admin/ai/defaults \
  -H 'Content-Type: application/json' \
  -d '{"telegramLlmNarrate":{"readMarketTicker":true}}' | jq '.telegramLlmNarrate'

# 再开启 depth（ticker 应保持 true — AC-8）
curl -s -X PATCH http://127.0.0.1:8080/api/v1/admin/ai/defaults \
  -H 'Content-Type: application/json' \
  -d '{"telegramLlmNarrate":{"readMarketDepth":true}}' | jq '.telegramLlmNarrate'
```

## 测试

```bash
cd server && uv run pytest tests/test_telegram_llm_narrate.py -q
```

## 与 OpenAPI 差异

- 无；行为与功能包 `api.openapi.yaml` 一致。
