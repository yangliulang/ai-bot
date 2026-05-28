# 测试报告（API）

> 测试 Agent 在 `backend_done` 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-27
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · SQLite 隔离库；API `http://127.0.0.1:8080/health` → **200**
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 8（P0）+ 1（P1） | 9 | 0 | 0 | 0 |

说明：pytest 共 **13** 条（含普通合约撤单 `test_futures_cancel_http_success`、场景就绪、领域单测等 **包外** 回归）；功能包 P0 **TC-01～08** 均覆盖。

自动化：

```bash
cd server && uv run pytest \
  tests/test_futures_cancel_condition_trade.py \
  tests/test_condition_order_list_cancel.py -v
# 13 passed in ~0.9s
```

## 用例执行明细

| ID | 优先级 | 结果 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | 通过 | `test_condition_orders_read_http` — `scenarioId=automation.condition_orders_read`；`len(orders)==1`；`totalOpenOrders==2`；含 `triggerType` |
| TC-02 | P0 | 通过 | 同上（Query `symbol=BTC-USDT`） |
| TC-03 | P0 | 通过 | `test_condition_cancel_http_success` — `automation.condition_order_cancel` **200** |
| TC-04 | P0 | 通过 | `test_condition_list_cancel_tc04_unbound_user_403` — GET/POST **403** `AGENT_SUBACCOUNT_REQUIRED` |
| TC-05 | P0 | 通过 | `test_condition_list_cancel_tc05_feature_futures_off_403` — **403** `FEATURE_AGENT_FUTURES_OFF` |
| TC-06 | P0 | 通过 | `test_condition_list_cancel_tc06_open_orders_failed_502` — **502** `AGENT_FUTURES_OPEN_ORDERS_FAILED` |
| TC-07 | P0 | 通过 | `test_condition_list_cancel_tc07_cancel_rejected_400` — **400** `AGENT_FUTURES_CANCEL_REJECTED` |
| TC-08 | P0 | 通过 | `test_runtime_intent_condition_orders_read` · `test_runtime_intent_condition_cancel_confirm` |
| TC-09 | P1 | 通过 | `test_is_condition_order_row_filter` |

## 契约抽查

- [x] `GET …/condition-orders` / `POST …/cancel-condition` 200 camelCase 与 `api.openapi.yaml` 一致
- [x] 403/400/502 错误体 `code` 与 OpenAPI 示例一致
- [x] `totalOpenOrders` vs `orders` 语义与 brief AC-1 一致

`./scripts/check-test-coverage.sh handoff/features/2026-05-26--condition-order-list-cancel` → **0**

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- **含页面：否**；下一 Chat：**`/pipeline-frontend-integrate`**（空跑）→ **`/pipeline-test-e2e`**（E2E N/A）→ designer/product。
- 普通 **`POST …/futures/cancel`** 回归在 `test_futures_cancel_http_success`，归属 **`2026-05-26--futures-cancel`** 包，不记入本包 AC。
