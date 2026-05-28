# 写路径 504 UNKNOWN 全局扩面

> 功能 ID：`2026-05-26--trading-write-unknown-global`  
> 产品 Agent 定稿 · `contract_ready`

## 背景

路线图 **§6.2** 与 **`POST|GET /api/v1/agent/trading/reconcile`** 已交付（查单闭合 UNKNOWN 终态）。当前 **交易所写路径**（`post_signed_*`）在 HTTP **504** 或 **写超时** 时，部分仍返回 **`AGENT_OPENAPI_PROBE_FAILED`** / 场景失败码，时间线 **`exchangeOutcome`** 虽可能为 `unknown`，但 **HTTP `code`、用户话术、execution 终态** 不一致，存在 **误报成败** 风险。本功能在 **不改对账 HTTP 契约** 前提下，对 **全量 Coobit 签名写** 统一 **`AGENT_EXCHANGE_WRITE_UNKNOWN`** 语义，并与 §6 对账串联。

## 用户故事

- 作为 **交易员（TG/HTTP）**，当交易所写请求 **超时或 504** 时，我希望收到 **中性话术**（仍在确认），而不是「下单失败/已成功」的误判，以便稍后对账或重试。
- 作为 **运营/排障**，我希望时间线 **`trading.exchange_private`** 在未知写时 **`exchangeOutcome=unknown`**，并可对同一 **`executionId`** 调用 **`trading/reconcile`** 闭合终态。

## 验收标准

- [x] **AC-1**：下列 Coobit **签名写** 在 HTTP **504** 或 **写超时** 时，统一抛出 **`AppError`**：`code=AGENT_EXCHANGE_WRITE_UNKNOWN`、`status_code=502`、`details.exchangeOutcome=unknown`、中性 **`message`**（禁止断言成交/撤单成功或失败）  
  **范围**：`post_signed_spot_order_json`、`post_signed_spot_cancel_json`、`post_signed_futures_order_json`、`post_signed_futures_cancel_json`、`post_signed_margin_order_json`、`post_signed_futures_condition_order_json`（及条件单撤单所用 cancel 写）。
- [x] **AC-2**：**现货** HTTP 写（代表 **`POST /api/v1/agent/trade/spot/limit-order`** 或 **`/flash-convert`**）在模拟 504/超时后，响应 **`code=AGENT_EXCHANGE_WRITE_UNKNOWN`**；对应 **`executionId`** 时间线存在 **`trading.exchange_private`** 且 **`exchangeOutcome=unknown`**。
- [x] **AC-3**：**现货撤单** **`POST /api/v1/agent/trade/spot/cancel`** 满足 AC-2 同等 UNKNOWN 语义（时间线 method 为撤单 PATH）。
- [x] **AC-4**：**合约** **`POST /api/v1/agent/trade/futures/order`** 与 **`POST …/futures/cancel`** 满足 AC-2 同等语义（`/fapi/v1/order`、`/fapi/v1/cancel`）。
- [x] **AC-5**：**全仓杠杆** **`POST /api/v1/agent/trade/margin/order`** 满足 AC-2 同等语义。
- [x] **AC-6**：**条件单** **`POST …/futures/condition-order`** 与 **`POST …/futures/cancel-condition`** 满足 AC-2 同等语义。
- [x] **AC-7**：在 AC-2 产生的 **`executionId`** 上，**`POST /api/v1/agent/trading/reconcile`** 返回 **200**（`resolutionStatus` 为终态或 `stillUnknown=true`）；若尚无 reconcile 事件，**`GET …/trading/reconcile/status`** 返回 **`resolutionStatus=UNKNOWN`**（回归 §6，不修改对账契约字段）。
- [x] **AC-8**：交易所 **明确拒单**（如 **`AGENT_SPOT_ORDER_REJECTED`** / **`AGENT_FUTURES_ORDER_REJECTED`**）仍为 **fail** 语义，**不得** 映射为 **`AGENT_EXCHANGE_WRITE_UNKNOWN`**。
- [x] **AC-9**：HTTP 写路径在 **`AGENT_EXCHANGE_WRITE_UNKNOWN`** 时，**`execution_finalize`** 的 outcome 为 **`UNKNOWN`**（或文档约定的待对账态），**不得** 仅记 **`FAILED`** 导致控制台/统计误判（与中性话术一致）。

## 范围

### 本期包含

- **`server/chainup_agent/infrastructure/exchange/coobit_openapi.py`**：`post_signed_*` 写统一 UNKNOWN 探测（504 / timeout）。
- **应用层**：`agent_spot_trade` / `agent_futures_trade` / `agent_futures_condition_trade` / `agent_margin_trade` 对 **`AGENT_EXCHANGE_WRITE_UNKNOWN`** 的时间线 **`exchangeOutcome`** 与 **`_`*_timeline_exchange_outcome`** 对齐。
- **HTTP 路由**：上列 Agent trade 写接口的错误响应与 execution 终态（AC-9）。
- **测试**：pytest 模拟 504/超时 + reconcile 回归；功能包 OpenAPI 描述 **502 UNKNOWN** 错误体。
- **依赖（已实现，本包不重复开发）**：`POST|GET /api/v1/agent/trading/reconcile` · `domain/trading_reconcile.py`。

### 本期不包含

- 新增对账 API 字段或 Admin 控制台页面。
- **Telegram** 全场景文案逐条改版（仅要求与 HTTP 同源 **`AppError.message`** 中性；TG 深链可后续包）。
- **改单** `CANCEL_SUCCEEDED_REPLACE_FAILED` 机制变更（已支持 **`reconcileSuggested`**，本包仅保证其前置 unknown 写一致）。
- 读路径（openOrders、quote、查单）的 504 处理（查单已在 `fetch_signed_*` 部分覆盖）。

## 非功能要求

- 与 GitBook 一致：**504 ⇒ 结果 UNKNOWN**，须走对账或查单，禁止客户端重试同一写请求冒充幂等成功。
- 不将 **`summary` / 订单全文** 写入非必要日志；时间线 preview 保持现有脱敏规则。
- 性能：写路径仅增加状态分支判断，不增加额外交易所往返。

## 待确认问题

- [x] Q1：是否覆盖 **现货改单** 两步写？— **是**（cancel/order 均走 `post_signed_spot_*`，纳入 AC-1 列表；改单专用码 **`AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED`** 保持现状）。
- [x] Q2：TG callback 写是否在本包一并验收？— **否（P1 后续包）**；本期 P0 以 HTTP + pytest 验收通过。
