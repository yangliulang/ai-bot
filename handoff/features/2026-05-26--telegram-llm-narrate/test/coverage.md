# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-26--telegram-llm-narrate` |
| 含页面（需 E2E） | 否 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | telegramLlmNarrate 读写 | TC-01 | — | `GET\|PATCH …/admin/ai/defaults` |
| AC-2 | ticker 启用 → LLM narrate | TC-02 | — | TG webhook + mock LLM |
| AC-3 | LLM 失败 → 确定性回落 | TC-03 | — | mock LLM fail → sendMessage |
| AC-4 | 关闭 → 无 LLM | TC-04 | — | defaults/env false |
| AC-5 | env=true 覆盖 admin false | TC-05 | — | `TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER` |
| AC-6 | 8 场景共用 effective 解析 | TC-06 | — | depth + spot flash 各一例 |
| AC-7 | timeline effective 字段 | TC-07 | — | `effectiveTelegramLlmNarrateEnabled` |
| AC-8 | PATCH 部分合并 | TC-08 | — | 单字段 PATCH 不重置其它 |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/admin/ai/defaults | TC-01 |
| PATCH | /api/v1/admin/ai/defaults | TC-01, TC-08 |
| — | Telegram webhook（无 OpenAPI path） | TC-02～TC-07 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 无页面，E2E 不适用
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-26--telegram-llm-narrate` 退出码 0
