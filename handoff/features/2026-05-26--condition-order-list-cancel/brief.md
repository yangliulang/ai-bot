# 条件单查撤契约收口

> 功能 ID：`2026-05-26--condition-order-list-cancel`  
> 产品 Agent 定稿 · Phase-2 **P1** · 路线图 **Step 2.5** 存量实现契约化

## 背景

**`GET /api/v1/agent/trade/futures/condition-orders`** 与 **`POST /api/v1/agent/trade/futures/cancel-condition`** 已在服务端交付（Phase 2.5 · `agent_trade_futures.py`、`agent_futures_condition_trade.py`），对接交易所 **`GET /fapi/v1/openOrders`**（过滤条件单行）与 **`POST /fapi/v1/cancel`**。

场景 **`automation.condition_orders_read`** / **`automation.condition_order_cancel`** 已注册为 **ready**，Telegram 支持 **`ccp`/`ccx`** 类型 A 确认撤单；意图识别可路由至 **只读列表** 与 **CONFIRM_TYPE_A**。

本包 **不新增运行时行为**，将存量实现 **沉淀为功能包契约**（`brief` + `api.openapi.yaml` + 测试追溯），供后端核对 OpenAPI、测试 Agent 回归，并与 **`2026-05-26--futures-cancel`**（普通合约撤单）边界区分。

## 用户故事

- 作为 **交易员（TG/HTTP）**，我希望 **查询当前条件单/计划委托** 并 **按订单号撤销**，无需直连交易所 OpenAPI。
- 作为 **运营/排障**，我希望 HTTP 响应含 **`scenarioId`**、**`orders`** 裁剪字段与 **`totalOpenOrders`**，便于区分「全部挂单数」与「条件单行数」。
- 作为 **后端/测试**，我希望功能包 OpenAPI 与 **`BACKEND_SPEC`**、**`test_futures_cancel_condition_trade.py`** 一致，避免口头约定漂移。

## 验收标准

- [x] **AC-1**：已绑定托管 API 的用户，`GET /api/v1/agent/trade/futures/condition-orders?userId=` 返回 **200**，JSON 含 **`scenarioId=automation.condition_orders_read`**、**`orders`**（数组，元素均为含 **`triggerType`** 或等价字段的条件单行）、**`totalOpenOrders`**（交易所 openOrders 全量条数，含非条件单）。
- [x] **AC-2**：`GET …/condition-orders` 带可选 Query **`symbol`**（如 `BTC-USDT`）时，**200**；**`symbol`** / **`contractName`** 与过滤结果一致；mock 下仅返回该标的挂单集合中的条件单行。
- [x] **AC-3**：已绑定用户，`POST /api/v1/agent/trade/futures/cancel-condition` Body **`userId`**、**`symbol`**、**`orderId`** 返回 **200**，**`scenarioId=automation.condition_order_cancel`**，含 **`orderId`** / **`orderIdString`** / **`contractName`** / **`exchangeOrderPreview`**；对应 **`executionId`** 时间线 **finalize SUCCESS**（`note` 含 `futures_condition_cancel_http`）。
- [x] **AC-4**：**未绑定** 托管 API 的 **`userId`** 调用 **GET …/condition-orders** 或 **POST …/cancel-condition** 返回 **403**，**`code=AGENT_SUBACCOUNT_REQUIRED`**。
- [x] **AC-5**：**`CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false`** 时，上述 **GET/POST** 返回 **403**，**`code=FEATURE_AGENT_FUTURES_OFF`**。
- [x] **AC-6**：交易所 openOrders 调用失败（非拒单）时，`GET …/condition-orders` 返回 **502**，**`code=AGENT_FUTURES_OPEN_ORDERS_FAILED`**。
- [x] **AC-7**：交易所撤单明确拒单时，`POST …/cancel-condition` 返回 **400**，**`code=AGENT_FUTURES_CANCEL_REJECTED`**（与普通 **`POST …/futures/cancel`** 同源语义）。
- [x] **AC-8**：**`POST /api/v1/agent/intent/recognize`**：文本含「查询条件单」类表述 → **`scenarioId=automation.condition_orders_read`** 且 **`plan.nextStep=ROUTE_READ_SKILL`**；文本含「撤销条件单」+ 订单号 → **`scenarioId=automation.condition_order_cancel`** 且 **`plan.nextStep=CONFIRM_TYPE_A`**。

## 范围

### 本期包含

- 功能包 **`api.openapi.yaml`**：`GET …/condition-orders`、`POST …/cancel-condition` 及错误体。
- **`brief.md`**、**`test/*`** 追溯矩阵；**`backend/notes.md`** 存量路径索引。
- 后端 **契约对齐**（实现已存在：核对路由、字段 alias、错误码；差异记入 `backend/notes.md`）。
- 测试 Agent 执行 **`test/cases.md`** P0（复用/扩写 **`tests/test_futures_cancel_condition_trade.py`**）。

### 本期不包含

- **条件单创建** **`POST …/condition-order`**（见 **`test_condition_trade.py`** / 独立场景包，本包仅 **查/撤**）。
- **普通合约撤单** **`POST …/futures/cancel`**（见 **`2026-05-26--futures-cancel`**）。
- **Admin / Deeplink** 新页面（**含页面：否**）。
- 修改 openOrders **过滤算法** 或新增交易所 PATH（除非与 OpenAPI 不一致的 bugfix）。

## 界面与交互（无页面）

**含页面：否**。用户触达：**HTTP API**、**Runtime 意图**、**Telegram** 类型 A（`ccp`/`ccx`）与只读编排；Admin 无新增路由。

## 非功能要求

- 查单/撤单须经 **已绑定** 子账户凭证；**不得** 在响应或时间线写入 Secret。
- **`orders`** 为交易所行裁剪副本，**不得** 断言列表外订单状态。
- 与 **`BACKEND_SPEC` §2.1** 一致：API JSON camelCase、时间字段 UTC。

## 实现备注（存量）

| 层 | 路径 / 测试 |
|----|-------------|
| Router | `server/chainup_agent/api/routers/v1/agent_trade_futures.py` |
| 应用层 | `server/chainup_agent/application/agent_futures_condition_trade.py` |
| 交易所 | `GET/POST /fapi/v1/openOrders`、`POST /fapi/v1/cancel`（经 `agent_futures_trade`） |
| 自动化 | `server/tests/test_futures_cancel_condition_trade.py` |
| 文档 | `server/docs/BACKEND_SPEC.md` Phase2.5 · `TRADING_PHASE2_REMAINING.md` §2.5 |

## 待确认问题

- [x] Q1：响应为 FastAPI **`response_model` 直出**（camelCase），**非** `{ code: 0, data }` 信封。
- [x] Q2：本包 **不** 重复实现；`backend.implement` 以 **契约核对 + 必要差异修正 + 补测** 为主。
- [x] Q3：**`totalOpenOrders`** 为过滤前 openOrders 总数；**`orders.length`** 为条件单行数 — 与存量实现一致。
