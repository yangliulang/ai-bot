# 后端说明 — 2026-05-26--condition-order-list-cancel

> Phase 2.5 存量实现 · 契约核对完成 · **backend_done**

## 启动与环境

| 项 | 值 |
|----|-----|
| 启动 | `cd server && uv run chainup-agent-api` |
| Base URL | http://127.0.0.1:8080 |
| 功能包 OpenAPI | `handoff/features/2026-05-26--condition-order-list-cancel/api.openapi.yaml` |

## 实现位置

| 层 | 模块 |
|----|------|
| Router | `chainup_agent/api/routers/v1/agent_trade_futures.py` |
| 列表/撤单应用 | `chainup_agent/application/agent_futures_condition_trade.py` |
| openOrders/cancel 写 | `chainup_agent/application/agent_futures_trade.py` |
| 行过滤 | `_is_condition_order_row` |
| 意图 | `agent_intent_pipeline.py` · `agent_access_evaluate.py` |
| TG | `telegram_callback_handler.py` · `telegram_bound_reply.py` |

## 路由与错误码

| Method | Path | 成功 `scenarioId` | 主要错误 |
|--------|------|-------------------|----------|
| GET | `/api/v1/agent/trade/futures/condition-orders` | `automation.condition_orders_read` | 403 `AGENT_SUBACCOUNT_REQUIRED` · 403 `FEATURE_AGENT_FUTURES_OFF` · 502 `AGENT_FUTURES_OPEN_ORDERS_FAILED` |
| POST | `/api/v1/agent/trade/futures/cancel-condition` | `automation.condition_order_cancel` | 同上 + 400 `AGENT_FUTURES_CANCEL_REJECTED` |

**200 响应**：camelCase 直出（非信封）。**`totalOpenOrders`** = 过滤前 openOrders 总数；**`orders`** = 仅条件单行。

**撤单时间线**：`execution_accept` → 写交易所 → `execution_finalize` SUCCESS（`futures_condition_cancel_http`）；拒单/失败走 `finalize_trade_http_on_error`。

## curl 示例

```bash
# 列表（需已绑定 userId）
curl -s 'http://127.0.0.1:8080/api/v1/agent/trade/futures/condition-orders?userId=79&symbol=BTC-USDT'

# 撤销
curl -s -X POST http://127.0.0.1:8080/api/v1/agent/trade/futures/cancel-condition \
  -H 'Content-Type: application/json' \
  -d '{"userId":"79","symbol":"BTC-USDT","orderId":"111"}'
```

## 自测（pytest）

```bash
cd server && uv run pytest \
  tests/test_futures_cancel_condition_trade.py \
  tests/test_condition_order_list_cancel.py -q
```

2026-05-27 本地：**13 passed**（存量 9 + 功能包 TC-04～07 共 4）。

| TC | pytest |
|----|--------|
| TC-01, TC-02 | `test_condition_orders_read_http` |
| TC-03 | `test_condition_cancel_http_success` |
| TC-04 | `test_condition_list_cancel_tc04_unbound_user_403` |
| TC-05 | `test_condition_list_cancel_tc05_feature_futures_off_403` |
| TC-06 | `test_condition_list_cancel_tc06_open_orders_failed_502` |
| TC-07 | `test_condition_list_cancel_tc07_cancel_rejected_400` |
| TC-08 | `test_runtime_intent_condition_orders_read` · `test_runtime_intent_condition_cancel_confirm` |
| TC-09 (P1) | `test_is_condition_order_row_filter` |

## 与功能包 OpenAPI 差异

| 项 | 说明 |
|----|------|
| — | **无** — 路径、字段 alias、错误码与 `api.openapi.yaml` 一致 |

## 与相邻包边界

| 能力 | 本包 | 其它包 |
|------|------|--------|
| 条件单 **创建** | 否 | `POST …/condition-order` · `test_condition_trade.py` |
| 普通合约撤单 | 否 | `POST …/futures/cancel` · `2026-05-26--futures-cancel` |
| 写 UNKNOWN | 否 | `2026-05-26--trading-write-unknown-global` |

## 关联文档

- `server/docs/BACKEND_SPEC.md` Phase2.5
- `server/docs/TRADING_PHASE2_REMAINING.md` §2.5
