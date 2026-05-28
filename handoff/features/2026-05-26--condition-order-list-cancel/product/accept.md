# 产品验收 — 2026-05-26--condition-order-list-cancel

> product.accept · 2026-05-28 · **结论：通过**

## 验收依据

| 来源 | 结论 |
|------|------|
| `brief.md` AC-1～AC-8 | 本文件逐项勾选 |
| `test/report.md` | API P0 TC-01～08 全通过；P1 TC-09 通过 |
| `test/e2e-report.md` | E2E N/A（无页面） |
| `design/ui-review.md` | 无 UI，走查 N/A；无 P0 |
| `frontend/integration.md` | 空跑收口；无 `admin/` 变更 |
| `backend/notes.md` | 存量实现对齐；无新路由 |

`./scripts/check-test-coverage.sh handoff/features/2026-05-26--condition-order-list-cancel` → **0**

## AC 对照

| AC | 验收结论 | 证据 |
|----|----------|------|
| AC-1 | 通过 | TC-01；`scenarioId=automation.condition_orders_read`；`orders`/`totalOpenOrders`/`triggerType` |
| AC-2 | 通过 | TC-02；Query `symbol=BTC-USDT` |
| AC-3 | 通过 | TC-03；`automation.condition_order_cancel` **200** |
| AC-4 | 通过 | TC-04；403 `AGENT_SUBACCOUNT_REQUIRED`（GET+POST） |
| AC-5 | 通过 | TC-05；403 `FEATURE_AGENT_FUTURES_OFF` |
| AC-6 | 通过 | TC-06；502 `AGENT_FUTURES_OPEN_ORDERS_FAILED` |
| AC-7 | 通过 | TC-07；400 `AGENT_FUTURES_CANCEL_REJECTED` |
| AC-8 | 通过 | TC-08；意图 `ROUTE_READ_SKILL` / `CONFIRM_TYPE_A` |

## 范围外 / P1 backlog（不阻塞 done）

| 项 | 说明 | 跟进 |
|----|------|------|
| TG `ccp`/`ccx` | 类型 A 撤单 staging 手工 | `test/e2e-cases.md` P1；可选 `telegram-write-path-staging` |
| 条件单创建 | `POST …/condition-order` | 独立场景包，非本包 |
| 普通合约撤单 | `POST …/futures/cancel` | **`2026-05-26--futures-cancel`** |

## 交付物

- 功能包契约：`brief.md`、`api.openapi.yaml`、`test/*`、`backend/notes.md`
- 测试：`server/tests/test_futures_cancel_condition_trade.py`、`server/tests/test_condition_order_list_cancel.py`
- 实现（存量，本包无生产 diff）：`agent_trade_futures.py`、`agent_futures_condition_trade.py`

## 收口

Phase-2 **P1**「条件单查/撤契约收口」（Step 2.5 存量）**done**；HTTP/Runtime 契约与 OpenAPI、pytest 追溯一致，与 **`futures-cancel`** 边界已文档化。
