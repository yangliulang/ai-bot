# 504 / UNKNOWN 对账 HTTP 契约收口

> 功能 ID：`2026-05-26--trading-reconcile`  
> 产品 Agent 定稿 · 对齐 closure **P‑03** / Recovery、路线图 **§6.2**

## 背景

**`POST|GET /api/v1/agent/trading/reconcile`** 已在服务端交付（`domain/trading_reconcile.py`、`application/agent_trading_reconcile.py`、`pytest tests/test_trading_reconcile.py`），用于在 **504 / 写超时 / 改单半失败** 后通过 **交易所查单** 闭合终态，并写入时间线 **`trading.reconcile`**。

Phase-2 本包 **不新增运行时行为**，将存量实现 **沉淀为功能包契约**（`brief` + `api.openapi.yaml` + 测试追溯），供后端核对 OpenAPI、测试 Agent 回归、以及与 **`2026-05-26--trading-write-unknown-global`** 的依赖边界对齐。

## 用户故事

- 作为 **交易员（TG/HTTP）**，当写路径返回 **UNKNOWN** 或改单 **撤成补单失败** 时，我希望调用 **对账 API** 获得 **中性 `userMessage`** 与 **`resolutionStatus`**，而不是被误判为已成功或已失败。
- 作为 **运营/排障**，我希望对同一 **`executionId`** 查询 **最近一次对账** 或 **待对账 UNKNOWN** 状态，以便与 Observability 时间线交叉验证。
- 作为 **后端/测试**，我希望功能包 OpenAPI 与 **`BACKEND_SPEC` §6**、**`test_trading_reconcile.py`** 一致，避免口头约定漂移。

## 验收标准

- [x] **AC-1**：对已绑定用户、时间线含 **改单半失败**（cancel 成功 + submit 失败）的 **`executionId`**，`POST /api/v1/agent/trading/reconcile` Body **`userId`** + **`executionId`** 返回 **200**，JSON 含 **`reconcileId`**、**`caseKind=CANCEL_SUCCEEDED_REPLACE_FAILED`**、**`resolutionStatus`**（`OPEN`/`PARTIAL_FAILURE`/`CANCELLED` 等终态之一）、**`stillUnknown`**（boolean）、**`userMessage`**（中性话术）、**`orderLookups`**（数组，长度 ≥ 1）。
- [x] **AC-2**：在 AC-1 成功对账后，`GET /api/v1/agent/trading/reconcile/status?userId=&executionId=` 返回 **200**，**`lastReconcileAtSeq`** 非空，**`resolutionStatus`** 与最近一次对账一致，**`stillUnknown`** 与 AC-1 聚合结果一致。
- [x] **AC-3**：对时间线仅有 **`trading.exchange_private`** 且 **`exchangeOutcome=unknown`**（如 HTTP 504）、**尚无** **`trading.reconcile`** 事件的 **`executionId`**，`GET …/reconcile/status` 返回 **200**，**`resolutionStatus=UNKNOWN`**、**`stillUnknown=true`**、**`caseKind=SUBMIT_UNKNOWN`**（或自时间线推断的等价 case）。
- [x] **AC-4**：**未绑定** 托管 API 的 **`userId`** 调用 **`POST …/reconcile`** 返回 **403**，**`code=AGENT_SUBACCOUNT_REQUIRED`**。
- [x] **AC-5**：**`executionId`** 不存在或与 **`userId`** 不匹配时，`POST` 或 `GET …/status` 返回 **404**，**`code=AGENT_RECONCILE_EXECUTION_NOT_FOUND`**。
- [x] **AC-6**：**无** `executionId` 且无法从 Body 构造查单目标（无 symbol/orderId 等）时，`POST …/reconcile` 返回 **422**，**`code=AGENT_RECONCILE_NO_QUERY_TARGETS`**。
- [x] **AC-7**：AC-1 成功对账后，该 **`executionId`** 时间线新增 **`event_name=trading.reconcile`** 事件，payload 含 **`reconcileId`**、**`caseKind`**、**`resolutionStatus`**。
- [x] **AC-8**：现货改单 **`POST /api/v1/agent/trade/spot/amend-limit-order`** 在 cancel 成功、replace 失败时返回 **502**，**`code=AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED`**，**`details.reconcileSuggested=true`**，且含 **`reconcileCaseKind`**、**`reconcilePath`**（指向对账 HTTP）。

## 范围

### 本期包含

- 功能包 **`api.openapi.yaml`**：`POST /api/v1/agent/trading/reconcile`、`GET …/reconcile/status` 及错误体。
- **`brief.md`** 验收标准与 **`test/*`** 追溯矩阵。
- 后端 **契约对齐**（实现已存在：核对路由、字段 alias、错误码与 OpenAPI 一致；差异记入 `backend/notes.md`）。
- 测试 Agent 执行 **`test/cases.md`** P0（可复用/扩写 **`tests/test_trading_reconcile.py`** 等）。

### 本期不包含

- 修改对账 **聚合算法** 或新增 **`caseKind`**（除非与 OpenAPI 不一致的 bugfix）。
- **Admin / Deeplink** 对账页面（**含页面：否**）。
- **写路径 504 全局扩面**（已由 **`2026-05-26--trading-write-unknown-global`** 覆盖）。
- TG 内嵌「一键对账」按钮文案（P1）。

## 界面与交互（无页面）

**含页面：否**。用户触达路径为 **HTTP API**、**Runtime/TG 编排** 调用对账；Admin Observability 仅消费既有时间线事件，本包不新增路由。

## 非功能要求

- 查单须经 **已绑定** 子账户凭证；**不得** 在响应或时间线写入 Secret。
- **`userMessage`** / **`neutralHint`** 为中性话术，**不得** 断言「已成功下单」或「已确定失败」当 **`stillUnknown=true`**。
- 与 **`BACKEND_SPEC` §2.1** 一致：API JSON 时间字段 UTC。

## 实现备注（存量）

| 层 | 路径 / 测试 |
|----|-------------|
| Router | `server/chainup_agent/api/routers/v1/agent_trading_reconcile.py` |
| 应用层 | `server/chainup_agent/application/agent_trading_reconcile.py` |
| 领域 | `server/chainup_agent/domain/trading_reconcile.py` |
| 自动化 | `server/tests/test_trading_reconcile.py` |
| 文档 | `server/docs/BACKEND_SPEC.md` §6 · `API_INTEGRATION_GUIDE.md` §4.3d |

## 待确认问题

- [x] Q1：响应为 FastAPI **`response_model` 直出**（camelCase），**非** `{ code: 0, data }` 信封 — 与存量 Agent 交易 API 一致。
- [x] Q2：本包 **不** 重复实现；`backend.implement` 以 **契约核对 + 必要差异修正** 为主。
