# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-26
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · SQLite 隔离库（`conftest`）· 绑定库用例辅以 `CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY=true`
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 9（P0×8 + P1×1） | 9 | 0 | 0 | 0 |

自动化主集：`uv run pytest tests/test_telegram_llm_narrate.py -v` → **10 passed**（约 1.1s，含 2 条 unit + 8 条 P0 映射）。

回归：`tests/test_api.py::test_telegram_flash_type_a_llm_preamble_prepended` → **1 passed**（Type-A 闪兑 preamble 链，env 开启；与 AC-6 Type-A 语义对齐）。

## 用例执行明细

| ID | 优先级 | 结果 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | 通过 | `test_admin_defaults_telegram_llm_narrate_patch_get` — PATCH/GET `telegramLlmNarrate.readMarketTicker` |
| TC-02 | P0 | 通过 | `test_telegram_ticker_narrate_via_admin_defaults` — Admin 开启、env 关闭 → LLM 正文出站 |
| TC-03 | P0 | 通过 | `test_telegram_ticker_narrate_llm_fallback_deterministic` — LLM 失败 → 确定性 ticker 行、webhook 200 |
| TC-04 | P0 | 通过 | `test_telegram_ticker_narrate_disabled_skips_llm` — `invoke_llm_chat_for_telegram` 未调用 |
| TC-05 | P0 | 通过 | `test_telegram_ticker_narrate_env_overrides_admin_false` — env 强制开启覆盖 admin false |
| TC-06 | P0 | 通过 | `test_telegram_depth_narrate_via_admin_defaults`（只读 depth）+ 回归 `test_telegram_flash_type_a_llm_preamble_prepended`（Type-A）；共用 `resolve_effective_*` 已由 unit 覆盖 |
| TC-07 | P0 | 通过 | `test_telegram_ticker_narrate_timeline_effective_flag` — timeline `summary.effectiveTelegramLlmNarrateEnabled=true` |
| TC-08 | P0 | 通过 | `test_admin_defaults_telegram_llm_narrate_partial_patch` — 单字段 PATCH 不重置其它键 |
| TC-09 | P1 | 通过 | `test_admin_defaults…` GET 初值九字段均为 false |

## 契约抽查

- [x] `telegramLlmNarrate` 九键出现在 GET 合并视图（TC-01）
- [x] PATCH 深度合并（TC-08）
- [x] 时间线字段名与 `backend/notes.md` 一致（`effectiveTelegramLlmNarrateEnabled`）

`./scripts/check-test-coverage.sh handoff/features/2026-05-26--telegram-llm-narrate` → 退出码 **0**。

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- **无本期页面**（`brief.md` · `test/coverage.md` 含页面=否）。下一 Chat：**`/pipeline-frontend-integrate 2026-05-26--telegram-llm-narrate`** 空跑 `frontend/integration.md`，再 **`/pipeline-test-e2e`** 记 E2E **N/A**。
- TC-06 未在本包内为 `spotFlashConfirm` 单独写 Admin PATCH 用例；Type-A 行为由存量回归 + 与 depth 相同的 effective 解析保证，风险可接受。
