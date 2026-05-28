# 产品验收 — 2026-05-26--futures-cancel

> product.accept · 2026-05-28 · **结论：通过**

## 验收依据

| 来源 | 结论 |
|------|------|
| `brief.md` AC-1～AC-8 | 本文件逐项勾选 |
| `test/report.md` | API P0 TC-01～07 全通过；P1 TC-08 通过 |
| `test/e2e-report.md` | E2E N/A（无页面） |
| `design/ui-review.md` | 无 UI，走查 N/A；无 P0 |
| `frontend/integration.md` | 空跑收口；无 `admin/` 变更 |
| `backend/notes.md` | 存量实现对齐；`test_futures_cancel.py` 补 TC-02～05 |

`./scripts/check-test-coverage.sh handoff/features/2026-05-26--futures-cancel` → **0**

## AC 对照

| AC | 验收结论 | 证据 |
|----|----------|------|
| AC-1 | 通过 | TC-01；`trade.futures.cancel_order` **200**；`orderIdString`/`exchangeOrderPreview` |
| AC-2 | 通过 | TC-02；403 `AGENT_SUBACCOUNT_REQUIRED` |
| AC-3 | 通过 | TC-03；403 `FEATURE_AGENT_FUTURES_OFF` |
| AC-4 | 通过 | TC-04；400 `AGENT_FUTURES_CANCEL_REJECTED` |
| AC-5 | 通过 | TC-05；422 `VALIDATION_ERROR`（空 symbol/orderId） |
| AC-6 | 通过 | TC-06；`EXECUTE_FUTURES_CANCEL` |
| AC-7 | 通过 | TC-07；`trade.futures.cancel_order` **ready** |
| AC-8 | 通过 | TC-08；`coobit_fapi_v1_cancel_body` |

## 范围外 / P1 backlog（不阻塞 done）

| 项 | 说明 | 跟进 |
|----|------|------|
| TG 绑定会话直接撤单 | staging 手工 | 可选 `telegram-write-path-staging` |
| 条件单查/撤 | `condition-orders` / `cancel-condition` | **`2026-05-26--condition-order-list-cancel`**（已 done） |
| 写 UNKNOWN 全局 | `test_trading_write_unknown_global` | **`2026-05-26--trading-write-unknown-global`** |

## 交付物

- 功能包契约：`brief.md`、`api.openapi.yaml`、`test/*`、`backend/notes.md`
- 测试：`server/tests/test_futures_cancel.py`、`server/tests/test_futures_cancel_condition_trade.py`（精选用例）
- 实现（存量，本包无生产 diff）：`agent_trade_futures.py` · `futures_cancel_order_for_bound_user`

## 收口

Phase-2 **P1**「合约撤单契约收口」（Step 2.3 存量）**done**；与 **`condition-order-list-cancel`** 边界已文档化。Phase-2 backlog 仅剩 **P2** `telegram-write-path-staging`（planned）。
