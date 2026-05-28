# 合约撤单契约收口

> 功能 ID：`2026-05-26--futures-cancel`  
> 产品 Agent 定稿 · Phase-2 **P1** · 路线图 **Step 2.3** 存量实现契约化

## 背景

**`POST /api/v1/agent/trade/futures/cancel`** 已在服务端交付（Phase 2.3 · `agent_trade_futures.py`、`agent_futures_trade.py`），对接交易所 **`POST /fapi/v1/cancel`**（**`contractName` + `orderId`**）。

场景 **`trade.futures.cancel_order`** 已注册为 **ready**；意图识别在槽位齐全时返回 **`plan.nextStep=EXECUTE_FUTURES_CANCEL`**，Telegram 可直接执行 HTTP 撤单。

本包 **不新增运行时行为**，将存量实现 **沉淀为功能包契约**（`brief` + `api.openapi.yaml` + 测试追溯），供后端核对 OpenAPI、测试 Agent 回归，并与 **`2026-05-26--condition-order-list-cancel`**（条件单查/撤）边界区分。

## 用户故事

- 作为 **交易员（TG/HTTP）**，我希望 **按合约标的与订单号撤销永续/合约挂单**，无需直连交易所 OpenAPI。
- 作为 **运营/排障**，我希望 HTTP 响应含 **`scenarioId=trade.futures.cancel_order`** 与 **`exchangeOrderPreview`**，且对应 **`executionId`** 时间线可追踪。
- 作为 **后端/测试**，我希望功能包 OpenAPI 与 **`BACKEND_SPEC`**、**`test_futures_cancel_condition_trade.py`** 一致，避免与条件单路径混淆。

## 验收标准

- [x] **AC-1**：已绑定托管 API 的用户，`POST /api/v1/agent/trade/futures/cancel` Body **`userId`**、**`symbol`**（如 `BTC-USDT`）、**`orderId`** 返回 **200**，JSON 含 **`scenarioId=trade.futures.cancel_order`**、**`orderId`** / **`orderIdString`** / **`contractName`** / **`exchangeOrderPreview`**；对应 **`executionId`** 时间线 **finalize SUCCESS**（`note` 含 `futures_cancel_http`）。
- [x] **AC-2**：**未绑定** 托管 API 的 **`userId`** 调用上述 **POST** 返回 **403**，**`code=AGENT_SUBACCOUNT_REQUIRED`**。
- [x] **AC-3**：**`CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false`** 时，上述 **POST** 返回 **403**，**`code=FEATURE_AGENT_FUTURES_OFF`**。
- [x] **AC-4**：交易所撤单明确拒单时，**POST** 返回 **400**，**`code=AGENT_FUTURES_CANCEL_REJECTED`**（与 **`POST …/cancel-condition`** 同源语义）。
- [x] **AC-5**：Body 缺 **`symbol`** 或 **`orderId`**（空串）时返回 **422**，**`code=VALIDATION_ERROR`**。
- [x] **AC-6**：**`POST /api/v1/agent/intent/recognize`**：文本含「永续/合约撤单」类表述且槽位含标的+订单号 → **`scenarioId=trade.futures.cancel_order`** 且 **`plan.nextStep=EXECUTE_FUTURES_CANCEL`**。
- [x] **AC-7**：**`GET /api/v1/agent/scenarios`** 中 **`trade.futures.cancel_order`** 的 **`readiness=ready`**。
- [x] **AC-8**：撤单请求体经 **`coobit_fapi_v1_cancel_body`** 生成 **`contractName` + `orderId`**，与交易所 PATH 一致（领域单测）。

## 范围

### 本期包含

- 功能包 **`api.openapi.yaml`**：`POST …/futures/cancel` 及错误体。
- **`brief.md`**、**`test/*`** 追溯矩阵；**`backend/notes.md`** 存量路径索引。
- 后端 **契约对齐**（实现已存在：核对路由、字段 alias、错误码；差异记入 `backend/notes.md`）。
- 测试 Agent 执行 **`test/cases.md`** P0（复用/扩写 **`tests/test_futures_cancel_condition_trade.py`**，必要时新增 **`test_futures_cancel.py`** 覆盖 TC-02～05）。

### 本期不包含

- **条件单查/撤** **`GET …/condition-orders`**、**`POST …/cancel-condition`**（见 **`2026-05-26--condition-order-list-cancel`**）。
- **条件单创建** **`POST …/condition-order`**。
- **Admin / Deeplink** 新页面（**含页面：否**）。
- **全局 UNKNOWN 写路径**（见 **`2026-05-26--trading-write-unknown-global`**）；本包仅普通撤单 HTTP。

## 界面与交互（无页面）

**含页面：否**。用户触达：**HTTP API**、**Runtime 意图**（**`EXECUTE_FUTURES_CANCEL`**）、Telegram 绑定会话内直接撤单；Admin 无新增路由。

## 非功能要求

- 撤单须经 **已绑定** 子账户凭证；**不得** 在响应或时间线写入 Secret。
- 与 **`BACKEND_SPEC` §2.1** 一致：API JSON camelCase、时间字段 UTC。

## 实现备注（存量）

| 层 | 路径 / 测试 |
|----|-------------|
| Router | `server/chainup_agent/api/routers/v1/agent_trade_futures.py` · `POST /cancel` |
| 应用层 | `server/chainup_agent/application/agent_futures_trade.py` · `futures_cancel_order_for_bound_user` |
| 交易所 | `POST /fapi/v1/cancel` |
| 自动化 | `server/tests/test_futures_cancel_condition_trade.py`（`test_futures_cancel_http_success` 等） |
| 文档 | `server/docs/BACKEND_SPEC.md` Phase2.5 · `TRADING_PHASE2_REMAINING.md` §2.3 |

## 待确认问题

- [x] Q1：响应为 FastAPI **`response_model` 直出**（camelCase），**非** `{ code: 0, data }` 信封。
- [x] Q2：本包 **不** 重复实现；`backend.implement` 以 **契约核对 + 必要差异修正 + 补测** 为主。
- [x] Q3：与条件单撤单 **同交易所 PATH**，**`scenarioId`** 区分 **`trade.futures.cancel_order`** vs **`automation.condition_order_cancel`**。
