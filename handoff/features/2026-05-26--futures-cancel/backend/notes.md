# 后端说明 — 2026-05-26--futures-cancel

> Phase 2.3 存量实现 · 契约核对完成 · **backend_done**

## 启动与环境

| 项 | 值 |
|----|-----|
| 启动 | `cd server && uv run chainup-agent-api` |
| Base URL | http://127.0.0.1:8080 |
| 功能包 OpenAPI | `handoff/features/2026-05-26--futures-cancel/api.openapi.yaml` |

## 实现位置

| 层 | 模块 |
|----|------|
| Router | `chainup_agent/api/routers/v1/agent_trade_futures.py` · `POST /cancel` |
| 应用 | `chainup_agent/application/agent_futures_trade.py` · `futures_cancel_order_for_bound_user` |
| 交易所 | `POST /fapi/v1/cancel`（`coobit_fapi_v1_cancel_body`） |
| 意图 | `agent_intent_pipeline.py` · `EXECUTE_FUTURES_CANCEL` |
| TG | `telegram_bound_reply.py`（`step == EXECUTE_FUTURES_CANCEL`） |

## 路由与错误码

| Method | Path | 成功 `scenarioId` | 主要错误 |
|--------|------|-------------------|----------|
| POST | `/api/v1/agent/trade/futures/cancel` | `trade.futures.cancel_order` | 403 `AGENT_SUBACCOUNT_REQUIRED` · 403 `FEATURE_AGENT_FUTURES_OFF` · 400 `AGENT_FUTURES_CANCEL_REJECTED` · 422 `VALIDATION_ERROR` |

**200 响应**：camelCase 直出（非信封）。

**撤单时间线**：`execution_accept` → 写交易所 → `execution_finalize` SUCCESS（`note=futures_cancel_http`）；失败走 `finalize_trade_http_on_error`。

## curl 示例

```bash
curl -s -X POST http://127.0.0.1:8080/api/v1/agent/trade/futures/cancel \
  -H 'Content-Type: application/json' \
  -d '{"userId":"79","symbol":"BTC-USDT","orderId":"259396989397942275"}'
```

## 自测（pytest）

```bash
cd server && uv run pytest \
  tests/test_futures_cancel.py \
  tests/test_futures_cancel_condition_trade.py::test_futures_cancel_http_success \
  tests/test_futures_cancel_condition_trade.py::test_scenarios_futures_cancel_and_condition_read_ready \
  tests/test_futures_cancel_condition_trade.py::test_runtime_intent_futures_cancel_execute \
  tests/test_futures_cancel_condition_trade.py::test_coobit_fapi_cancel_body -q
```

2026-05-28 本地：**9 passed**（功能包 P0；另 `test_futures_cancel_condition_trade.py` 全文件 14 passed 含条件单回归）。

| TC | pytest |
|----|--------|
| TC-01 | `test_futures_cancel_http_success` |
| TC-02 | `test_futures_cancel_tc02_unbound_user_403` |
| TC-03 | `test_futures_cancel_tc03_feature_futures_off_403` |
| TC-04 | `test_futures_cancel_tc04_cancel_rejected_400` |
| TC-05 | `test_futures_cancel_tc05_validation_empty_symbol_422` · `…_empty_order_id_422` |
| TC-06 | `test_runtime_intent_futures_cancel_execute` |
| TC-07 | `test_scenarios_futures_cancel_and_condition_read_ready`（断言 `trade.futures.cancel_order`） |
| TC-08 (P1) | `test_coobit_fapi_cancel_body` |

## 与功能包 OpenAPI 差异

| 项 | 说明 |
|----|------|
| — | **无** — 路径、字段 alias、错误码与 `api.openapi.yaml` 一致 |

## 与相邻包边界

| 能力 | 本包 | 其它包 |
|------|------|--------|
| 条件单查/撤 | 否 | `2026-05-26--condition-order-list-cancel` |
| 写 UNKNOWN | 否 | `2026-05-26--trading-write-unknown-global` |

## 关联文档

- `server/docs/BACKEND_SPEC.md` Phase2.5
- `server/docs/TRADING_PHASE2_REMAINING.md` §2.3
