# 测试用例（API）

> 测试 Agent 在 `backend_done` 后执行。实现前由 product.contract 定稿。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | Coobit 写 504 | mock `httpx` 对 `post_signed_spot_order_json` 返回 status=504 | 抛出 `AGENT_EXCHANGE_WRITE_UNKNOWN`；`details.exchangeOutcome=unknown` | P0 |
| TC-02 | AC-2 | 现货限价写 HTTP | mock 504 → `POST /api/v1/agent/trade/spot/limit-order`（绑定用户） | 502 + `code=AGENT_EXCHANGE_WRITE_UNKNOWN`；DB 时间线 `trading.exchange_private.exchangeOutcome=unknown` | P0 |
| TC-03 | AC-3 | 现货撤单 | mock `post_signed_spot_cancel_json` 504 → `POST …/spot/cancel` | 同 TC-02 语义；methodPath 为 cancel | P0 |
| TC-04 | AC-4 | 合约写/撤 | mock futures order/cancel 504 → 对应 POST | UNKNOWN code + 时间线 unknown | P0 |
| TC-05 | AC-5 | 杠杆写 | mock margin order 504 → `POST …/margin/order` | UNKNOWN + 时间线 unknown | P0 |
| TC-06 | AC-6 | 条件单 | mock condition order + cancel 504 | 两路由均为 UNKNOWN | P0 |
| TC-07 | AC-7 | 对账回归 | 在 TC-02 的 executionId 上 `POST …/reconcile`；再 `GET …/status` | reconcile 200；status 在未有 reconcile 事件前可为 `UNKNOWN` | P0 |
| TC-08 | AC-8 | 拒单对照 | mock 交易所 body 拒单（非 504） | `AGENT_SPOT_ORDER_REJECTED`（或 futures 等价）；**非** `AGENT_EXCHANGE_WRITE_UNKNOWN` | P0 |
| TC-09 | AC-9 | 终态 | UNKNOWN 写失败后查 `agent_execution` / finalize | outcome=`UNKNOWN`（或约定待对账），非仅 `FAILED` | P0 |
| TC-10 | AC-1 | 写超时 | mock `TimeoutException` on post_signed write | `AGENT_EXCHANGE_WRITE_UNKNOWN` + `details.reason=timeout` | P1 |

## 契约测试

- [x] 502 错误体字段与 `api.openapi.yaml` `AppErrorExchangeWriteUnknown` 一致
- [x] `message` 为中性文案（不含「已成功」「已失败」终态断言）

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| TC-10 | 传输层超时 | 同 504，映射 UNKNOWN 而非 `AGENT_OPENAPI_PROBE_FAILED` |
