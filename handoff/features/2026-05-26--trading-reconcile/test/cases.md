# 测试用例（API）

> 测试 Agent 在 `backend_done` 后执行。存量实现见 `server/tests/test_trading_reconcile.py`；本表为功能包 P0 追溯。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | 改单半失败对账 | 绑定用户；构造 execution 时间线 cancel 成功 + submit fail；mock 现货查单；`POST /api/v1/agent/trading/reconcile` Body `userId`+`executionId` | **200**；`caseKind=CANCEL_SUCCEEDED_REPLACE_FAILED`；`reconcileId`、`resolutionStatus`、`stillUnknown`、`userMessage`、`orderLookups` 非空 | P0 |
| TC-02 | AC-2 | 对账后 status | 在 TC-01 成功后 `GET …/trading/reconcile/status?userId=&executionId=` | **200**；`lastReconcileAtSeq` 非 null；`resolutionStatus`/`stillUnknown` 与 POST 一致 | P0 |
| TC-03 | AC-3 | 待对账 UNKNOWN | 仅写入 `trading.exchange_private` outcome=unknown（504）；无 reconcile 事件；`GET …/status` | **200**；`resolutionStatus=UNKNOWN`；`stillUnknown=true`；`caseKind=SUBMIT_UNKNOWN` | P0 |
| TC-04 | AC-4 | 未绑定用户 | 无 binding 的 `userId` 调用 `POST …/reconcile` | **403**；`code=AGENT_SUBACCOUNT_REQUIRED` | P0 |
| TC-05 | AC-5 | execution 不存在 | 已绑定用户；`executionId` 随机；`POST` 或 `GET status` | **404**；`code=AGENT_RECONCILE_EXECUTION_NOT_FOUND` | P0 |
| TC-06 | AC-6 | 无查单目标 | 已绑定；`POST` 仅 `userId`（无 executionId/symbol/orderId） | **422**；`code=AGENT_RECONCILE_NO_QUERY_TARGETS` | P0 |
| TC-07 | AC-7 | 时间线事件 | TC-01 后查询该 execution 时间线或事件 API | 存在 `trading.reconcile`；payload 含 `reconcileId`、`caseKind`、`resolutionStatus` | P0 |
| TC-08 | AC-8 | 改单对账引导 | mock cancel 成功 + submit 失败；`POST …/trade/spot/amend-limit-order` | **502**；`code=AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED`；`details.reconcileSuggested=true`；含 `reconcileCaseKind`、`reconcilePath` | P0 |
| TC-09 | AC-6 | 非法 caseKind | 已绑定；`POST` Body `caseKind=INVALID` | **422**；`code=VALIDATION_ERROR` | P1 |

## 契约测试

- [x] `POST|GET …/reconcile*` 200 体字段名 camelCase，与 `api.openapi.yaml` schema 一致
- [x] 错误体 `code`/`message` 与 OpenAPI 示例一致
- [x] `userMessage` 在 `stillUnknown=true` 时不断言终态成功/失败

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| TC-09 | caseKind 枚举外 | 422 VALIDATION_ERROR |
| — | 查单订单不存在 | `orderLookups` 项 `notFound=true` 或 `canonicalStatus=INCONCLUSIVE`（不 500） |

## 自动化映射

| 用例 | 建议 pytest |
|------|-------------|
| TC-01, TC-02, TC-03 | `tests/test_trading_reconcile.py::test_reconcile_http_with_execution` · `test_reconcile_status_pending_unknown` |
| TC-04～TC-06, TC-09 | 扩写 `test_trading_reconcile.py` 或本功能包专用模块 |
| TC-08 | `tests/test_spot_amend_trade.py`（补 assert `reconcileSuggested`） |
