# 测试用例（API）

> 测试 Agent 在 `backend_done` 后执行。存量实现见 `server/tests/test_futures_cancel_condition_trade.py`；TC-02～05 可由 backend 扩写 `test_futures_cancel.py`。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | 合约撤单成功 | 绑定用户；mock `post_signed_futures_cancel_json`；`POST …/futures/cancel` Body `userId`+`symbol`+`orderId` | **200**；`scenarioId=trade.futures.cancel_order`；含 `orderIdString`/`exchangeOrderPreview` | P0 |
| TC-02 | AC-2 | 未绑定 | 无 binding 的 `userId` 调用 `POST …/futures/cancel` | **403**；`code=AGENT_SUBACCOUNT_REQUIRED` | P0 |
| TC-03 | AC-3 | 功能关闭 | `CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false`；已绑定用户 `POST …/cancel` | **403**；`code=FEATURE_AGENT_FUTURES_OFF` | P0 |
| TC-04 | AC-4 | 撤单拒单 | 绑定用户；mock cancel 抛 `AGENT_FUTURES_CANCEL_REJECTED`；`POST …/cancel` | **400**；`code=AGENT_FUTURES_CANCEL_REJECTED` | P0 |
| TC-05 | AC-5 | 参数校验 | 绑定用户；`POST` Body `symbol=""` 或缺 `orderId` | **422**；`code=VALIDATION_ERROR` | P0 |
| TC-06 | AC-6 | 意图路由 | `POST …/intent/recognize` 文本「永续 BTC-USDT 撤单 订单号 …」 | **`scenarioId=trade.futures.cancel_order`**；`nextStep=EXECUTE_FUTURES_CANCEL` | P0 |
| TC-07 | AC-7 | 场景就绪 | `GET …/scenarios` | `trade.futures.cancel_order.readiness==ready` | P0 |
| TC-08 | AC-8 | cancel body | 调用 `coobit_fapi_v1_cancel_body(contract_name, order_id)` | `contractName`+`orderId` 与交易所约定一致 | P1 |

## 契约测试

- [x] `POST …/futures/cancel` 200 体 camelCase 与 `api.openapi.yaml` 一致（backend 自测 pytest）
- [x] 错误体 `code`/`message` 与 OpenAPI 示例一致（TC-02～05）

## 自动化映射

| 用例 | 建议 pytest |
|------|-------------|
| TC-01 | `test_futures_cancel_condition_trade.py::test_futures_cancel_http_success` |
| TC-02～TC-05 | 扩写 `test_futures_cancel.py` 或同目录新文件 |
| TC-06 | `::test_runtime_intent_futures_cancel_execute` |
| TC-07 | `::test_scenarios_futures_cancel_and_condition_read_ready`（断言 cancel_order 分支） |
| TC-08 | `::test_coobit_fapi_cancel_body` |
