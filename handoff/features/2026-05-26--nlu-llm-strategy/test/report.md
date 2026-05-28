# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-26
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · SQLite 隔离库（`conftest`）· `CHAINUP_AGENT_INTENT_NLU_USE_LLM=false`（autouse）
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 9（P0×8 + P1×1） | 9 | 0 | 0 | 0 |

自动化：`uv run pytest tests/test_nlu_llm_strategy.py -v` → **9 passed**（约 0.75s）。

## 用例执行明细

| ID | 优先级 | 结果 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | 通过 | `test_admin_defaults_intent_nlu_use_llm_patch_get` — PATCH/GET `intentNluUseLlm` |
| TC-02 | P0 | 通过 | `test_intent_recognize_llm_via_admin_defaults` — `nlu.source=llm_structured_v1` |
| TC-03 | P0 | 通过 | `test_intent_recognize_llm_fallback_keyword` — mock 返回 None → `keyword_v1`、200 |
| TC-04 | P0 | 通过 | `test_intent_recognize_keyword_only_skips_llm` — LLM helper `assert_not_awaited` |
| TC-05 | P0 | 通过 | `test_intent_recognize_env_overrides_admin_defaults` — env 覆盖 admin false |
| TC-06 | P0 | 通过 | TC-02/04/05 响应断言 `effectiveIntentNluUseLlm` 与分支一致 |
| TC-07 | P0 | 通过 | `test_telegram_timeline_intent_nlu_llm_enabled_uses_effective` — payload 非 env 原始值 |
| TC-08 | P0 | 通过 | `test_intent_recognize_prompt_injection_forbidden_fallback` — 200 + `keyword_v1` |
| TC-09 | P1 | 通过 | 手工 ASGI：`text=""` → 200、`EMPTY_INPUT`、`effectiveIntentNluUseLlm=false` |

## 契约抽查

- [x] `intentNluUseLlm` 合并默认 **false**（`test_admin_defaults…` GET 初值）
- [x] `effectiveIntentNluUseLlm` 出现在 recognize 响应（TC-02/04/06）
- [x] 功能包 `api.openapi.yaml` 与 `handoff/features/2026-05-26--nlu-llm-strategy/api.openapi.yaml` 字段一致（实现侧 `IntentRecognizeResponse`）

`./scripts/check-test-coverage.sh handoff/features/2026-05-26--nlu-llm-strategy` → 退出码 **0**。

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- **无本期页面**（`brief.md` · `test/coverage.md` 含页面=否）。`status.yaml` 按标准 **`next: frontend-agent`**；建议下一 Chat 执行 **`/pipeline-frontend-integrate 2026-05-26--nlu-llm-strategy`** 由 frontend-agent **空跑收口** `frontend/integration.md`（无代码变更），再 **`/pipeline-test-e2e`** 记 E2E **N/A**。
- 本地 `:8080` Admin defaults 需 Bearer（`ADMIN_CONSOLE_AUTH_REQUIRED`）；P0 以 pytest 为准，与 `backend/notes.md` 一致。
