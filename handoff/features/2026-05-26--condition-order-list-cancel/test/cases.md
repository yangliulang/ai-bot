# 测试用例（API）

> 测试 Agent 在 `backend_done` 后执行。存量实现见 `server/tests/test_futures_cancel_condition_trade.py`。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | 条件单列表 | 绑定用户；mock openOrders 含 1 条件单行 + 1 普通限价行；`GET …/condition-orders?userId=` | **200**；`scenarioId=automation.condition_orders_read`；`len(orders)==1`；`totalOpenOrders==2`；条件单行含 `triggerType` | P0 |
| TC-02 | AC-2 | symbol 过滤 | 同 TC-01；`GET` 带 `symbol=BTC-USDT` | **200**；`symbol`/`contractName` 与 mock 一致；`orders` 仍为条件单过滤结果 | P0 |
| TC-03 | AC-3 | 撤销条件单 | 绑定用户；mock cancel；`POST …/cancel-condition` Body `userId`+`symbol`+`orderId` | **200**；`scenarioId=automation.condition_order_cancel`；含 `orderId`/`exchangeOrderPreview` | P0 |
| TC-04 | AC-4 | 未绑定 | 无 binding 的 `userId` 调用 `GET …/condition-orders` 与 `POST …/cancel-condition` | **403**；`code=AGENT_SUBACCOUNT_REQUIRED` | P0 |
| TC-05 | AC-5 | 功能关闭 | `CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false`；已绑定用户调用 GET/POST | **403**；`code=FEATURE_AGENT_FUTURES_OFF` | P0 |
| TC-06 | AC-6 | openOrders 失败 | 绑定用户；mock `fetch_signed_futures_open_orders_json` 抛 `AGENT_FUTURES_OPEN_ORDERS_FAILED`；`GET …/condition-orders` | **502**；`code=AGENT_FUTURES_OPEN_ORDERS_FAILED` | P0 |
| TC-07 | AC-7 | 撤单拒单 | 绑定用户；mock cancel 抛 `AGENT_FUTURES_CANCEL_REJECTED`；`POST …/cancel-condition` | **400**；`code=AGENT_FUTURES_CANCEL_REJECTED` | P0 |
| TC-08 | AC-8 | 意图路由 | `POST …/intent/recognize` 文本「查询我的条件单 BTC-USDT」；再「永续 撤销条件单 … 订单号 …」 | 前者 **`scenarioId=automation.condition_orders_read`**、`nextStep=ROUTE_READ_SKILL`；后者 **`automation.condition_order_cancel`**、`CONFIRM_TYPE_A` | P0 |
| TC-09 | AC-1 | 行过滤单元 | 调用 `_is_condition_order_row` | 含 `triggerType` → true；普通 LIMIT 行 → false | P1 |

## 契约测试

- [x] `GET …/condition-orders` / `POST …/cancel-condition` 200 体 camelCase 与 `api.openapi.yaml` 一致（backend 自测 pytest）
- [x] 错误体 `code`/`message` 与 OpenAPI 示例一致（TC-04～07）

## 自动化映射

| 用例 | 建议 pytest |
|------|-------------|
| TC-01 | `test_futures_cancel_condition_trade.py::test_condition_orders_read_http` |
| TC-02 | 同上（已带 `symbol` param）或扩写断言 |
| TC-03 | `::test_condition_cancel_http_success` |
| TC-04～TC-07 | 扩写 `test_futures_cancel_condition_trade.py` 或本包 `test_condition_order_list_cancel.py` |
| TC-08 | `::test_runtime_intent_condition_orders_read` · `::test_runtime_intent_condition_cancel_confirm` |
| TC-09 | `::test_is_condition_order_row_filter` |
