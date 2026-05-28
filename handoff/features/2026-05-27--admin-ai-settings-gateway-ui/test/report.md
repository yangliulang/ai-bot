# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-27
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · SQLite 隔离库（`conftest` · `_init_schema_sqlite`）
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 5（P0×4 + P1×1） | 5 | 0 | 0 | 0 |

自动化：

```bash
cd server && uv run pytest tests/test_admin_ai_settings_gateway_ui.py -v
# 5 passed in ~0.6s
```

前序回归（可选一并跑）：

```bash
cd server && uv run pytest tests/test_nlu_llm_strategy.py tests/test_telegram_llm_narrate.py -q
# 19 passed（backend/notes.md）
```

## 用例执行明细

| ID | 优先级 | 结果 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | 通过 | `test_gateway_ui_tc01_get_defaults_has_gateway_fields` — `intentNluUseLlm` boolean；`telegramLlmNarrate` 含 9 键且均为 boolean |
| TC-02 | P0 | 通过 | `test_gateway_ui_tc02_patch_intent_nlu_use_llm` — PATCH 切换并 GET 持久化 |
| TC-03 | P0 | 通过 | `test_gateway_ui_tc03_patch_narrate_partial_merge` — 仅 `readMarketDepth=true`，其余 8 键不变 |
| TC-04 | P1 | 通过 | `test_gateway_ui_tc04_patch_unknown_narrate_field_422` — **422** `VALIDATION_ERROR` |
| TC-05 | P0 | 通过 | `test_gateway_ui_tc05_patch_scenario_chat_model` — `scenarioChatModel=gpt-4.1-mini` **200** |

## 契约抽查

- [x] camelCase：`intentNluUseLlm`、`telegramLlmNarrate.*` 与 `api.openapi.yaml` 一致
- [x] 错误体含 `code` + `message`（TC-04）
- [x] 本包无新 path；`GET/PATCH /api/v1/admin/ai/defaults` 行为与 brief AC-2～AC-5、AC-7 一致

`./scripts/check-test-coverage.sh handoff/features/2026-05-27--admin-ai-settings-gateway-ui` → 退出码 **0**（contract 阶段已验）。

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- 本包 **含页面**；API P0 通过后 `next: frontend-agent`。下一 Chat：**`/pipeline-frontend-integrate 2026-05-27--admin-ai-settings-gateway-ui`**（在 `/ai-settings?tab=runtime` 增加网关策略 UI）。
- 新增 pytest：`server/tests/test_admin_ai_settings_gateway_ui.py`（本功能包 TC 追溯专用）。
- 本机 `:8080` `/health` → **200**（可选 curl 手验；P0 以 pytest 为准）。
