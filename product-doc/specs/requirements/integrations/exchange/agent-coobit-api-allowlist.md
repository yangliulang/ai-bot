# Agent Runtime · Coobit 子账户 API 白名单（首版 · 仅现有矩阵 PATH）

**定位**：在 **不新增** Coobit 交易所接口的前提下，规定 **Agent 运行时网关** **允许调用** 的子账户 scope **HTTP PATH** 集合；与 **`design/api.md` 子账户矩阵「非书面延期」行**、**`specs/openapi/exchange/coobit-*.yaml`** **同窗**。**不替代** 所内生产 OpenAPI 终裁与 Key `authority` 对签。

**权威链**：

- 能力面与延期语义：**[`../../../design/api.md`](../../../design/api.md)**（子账户矩阵 · **CC-P0-02 / CC-P1-01**）
- 用户流程与确认：**[`../../flows/trade-via-agent.md`](../../flows/trade-via-agent.md)**、**[`telegram/overview` §2.5 · 类型 A；总则 §2～§2.6](../../domains/agent/telegram/overview.md)**
- 路由键：**[`../../domains/agent/agent-orchestration/routing-engine.md`](../../domains/agent/agent-orchestration/routing-engine.md)**
- 收口索引：**[`../../contract-closure.md`](../../contract-closure.md)**

**原则**：仅下列 PATH **可**出现在「经类型 A 确认后的写」或「策略必需只读」调用图中；其余矩阵格标 **书面延期** 或 **非目标** 者 — **禁止**以未文档化接口补齐；须 **`FR-T05`**、**主站 Deeplink** 或 **`WEALTH_ACTION_REQUIRES_WEB`** / **`TRANSFER_REQUIRES_WEB`** 等已登记稳定码。

**实现宿主（ARCH `openapi-ai` / 官方 Skill 包）**：当 **对上 Coobit HTTP** **由** **所内官方 `openapi-ai`（Skill、CLI、MCP 等）** **发起时**，**本条 PATH 边界不变**。**禁止** **因更换实现载体而放宽白名单**，**或引入矩阵未冻结** **`requestPath`。** **官方发布物须 pin**，**并与 **`specs/openapi/exchange/coobit-*`、`design/api.md`** **同窗评审升级** — **同窗** **[`integrations/exchange/overview.md`「Coobit · 官方 openapi-ai（Skill）采纳」节](overview.md)**。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../contract-closure.md)。

## 1. 双网关

| 域 | 文档锚 |
|----|--------|
| **现货 / 杠杆 / 钱包侧**（`sapi`、`/sapi/v1/asset/*`） | [`coobit-public.yaml`](../../../openapi/exchange/coobit-public.yaml)、[`coobit-spot.yaml`](../../../openapi/exchange/coobit-spot.yaml)、[`coobit-margin.yaml`](../../../openapi/exchange/coobit-margin.yaml)、[`coobit-wealth.yaml`](../../../openapi/exchange/coobit-wealth.yaml) |
| **合约侧**（`fapi`） | [`coobit-futures.yaml`](../../../openapi/exchange/coobit-futures.yaml)、[`coobit-automation.yaml`](../../../openapi/exchange/coobit-automation.yaml) |
| **listenKey（若启用 WS）** | [`user-private-ws.yaml`](../../../openapi/stream/user-private-ws.yaml)（**可选**；无则不承诺 Push，**REST 查单兜底**见 **`Runtime/reconciliation.md`**） |

**baseurl** 以所内冻结为准，**禁止**混用 host。

---

## 2. 按 `scenarioId` 的允许 PATH（最小集）

下列 **`requestPath`** 与 **`design/api.md`** 矩阵 **非延期** 行一致；**方法** 以 GitBook / 所内 spec 为准（表内为常用方法）。

### 2.1 只读 · 行情 / 账户（所有写路径的前置）

| 用途 | 方法 | requestPath | 备注 |
|------|------|-------------|------|
| 公开探活与时间 | GET | `/sapi/v2/ping`、`/sapi/v2/time` | 可与 `symbols/depth/ticker/...` 同属公开层 |
| 公开行情 | GET | `/sapi/v2/symbols`、`/depth`、`/ticker`、`/trades`、`/klines` | 所内可免 Key；**实现以所内为准** |
| 币币账户与成交 | GET | `/sapi/v1/account`、`/sapi/v2/order`、`/openOrders`、`/myTrades`；**或** `/sapi/v3/historyOrders`、`/sapi/v3/myTrades` | **v2/v3** **终裁**见所内 |
| 合约行情 | GET | `/fapi/v1/ping`、`/time`、`/contracts`、`/depth`、`/ticker`、`/ticker_all`、`/index`、`/klines` | **独立 host** |
| 合约账户 | GET | `/fapi/v1/account` | 持仓/保证金视图 |
| 合约订单/成交 | GET | `/fapi/v1/order`、`/openOrders`、`/myTrades`；历史类 **`orderHistorical`/`profitHistorical`** | 对账 **`design/api.md` REST↔WS 表** |

### 2.2 现货 · `trade.spot.flash_convert` / 现货市价族

| 用途 | 方法 | requestPath |
|------|------|-------------|
| 下单（含市价） | POST | `/sapi/v2/order`（及 **`/order/test`** 若做校验） |
| 撤单 | POST | `/sapi/v2/cancel` |
| 可选批量 | POST | `/sapi/v2/batchOrders`、`/batchCancel` | **若产品启用**；每笔确认语义仍以 **ADR-001** 为准 |

### 2.3 现货限价 · `trade.spot.limit_order`

| 用途 | 方法 | requestPath |
|------|------|-------------|
| 下单 | POST | `/sapi/v2/order` |
| 撤单 | POST | `/sapi/v2/cancel` |
| **「改单」（逻辑）** | **单次用户确认后** **`POST /sapi/v2/cancel` →（对账）→ `POST /sapi/v2/order`** | **一张类型 A** **授权** **顺序两笔写**（**无第二次确认**）；**新单** **须** **新** **`clientOrderId`** · **详** [`trade-via-agent.md`](../../flows/trade-via-agent.md) **专节 · 逻辑改单**、**ADR-001 §5** |

### 2.4 全仓杠杆 · `margin.cross.*`（仅矩阵已登记）

| 用途 | 方法 | requestPath |
|------|------|-------------|
| 杠杆下单 | POST | `/sapi/v2/margin/order` |
| 杠杆撤单 | POST | `/sapi/v2/margin/cancel` |
| 查单 / 开放委托 / 成交 | GET | `/sapi/v2/margin/order`、`/margin/openOrders`、`/margin/myTrades` |

**禁止**：**借还、计息自动化** — 矩阵 **书面延期**；须拒答或主站。

### 2.5 合约 · `trade.futures.*` / 条件单族

| 用途 | 方法 | requestPath |
|------|------|-------------|
| 开平仓 | POST | `/fapi/v1/order` |
| 撤单 | POST | `/fapi/v1/cancel`、`/cancel_all`（**若产品允许全撤**） |
| 调杠杆/保证金 | POST | `/fapi/v1/edit_lever`、`/edit_position_margin`、`/edit_user_margin_model`、`/edit_user_position_model` |
| 条件/计划委托 | POST | `/fapi/v1/conditionOrder` | 与 **`cancel`/`order`/`openOrders`** 配合 |
| **「改单」（逻辑）** | **单次用户确认后** **`POST /fapi/v1/cancel` →（对账）→ `POST /fapi/v1/order`** | **同窗** **现货逻辑改单**；**`scenarioId`** **`trade.futures.amend_limit_order`** |

### 2.6 理财 · `wealth.*`

| 用途 | 方法 | requestPath |
|------|------|-------------|
| 按类型账户只读 | POST | `/sapi/v1/asset/account/by_type`（**矩阵行**：`accountType` 含 **`4=otc`** 等） |
| 申购/赎回（在模板允许时） | POST | `/sapi/v1/asset/universal_transfer` | 配合 **`universal_transfer_query`** |
| **细分产品目录** | — | **延期** → **不得**依赖未登记 PATH |

未纳入模板或所内强制主站 → **`WEALTH_ACTION_REQUIRES_WEB`**（**[`boundaries.md`](../../domains/agent/exchange-agent/boundaries.md)** §8.3）。

### 2.7 子账户内多账本划转（**条件**）

仅当 **产品/模板书面纳入**（**[`boundaries.md`](../../domains/agent/exchange-agent/boundaries.md)** §8.4）：

**典型用途（与产品一致）**：**全仓杠杆**（`margin.cross.*`）**下单链** **中**，**全仓可用不足** **且** **同子账户币币可调拨** → **经对话内类型 A** **后** **调用** **下表** **完成** **现货 → cross** **归集**，**再** **衔接** **`POST …/margin/order`** — **流程 SSOT** **[`trade-via-agent.md`](../../flows/trade-via-agent.md)** **专节 · 第四步**。

| 用途 | 方法 | requestPath |
|------|------|-------------|
| 万向划转 | POST | `/sapi/v1/asset/universal_transfer`、`/universal_transfer_query` |
| 现货账本划转 | POST | `/sapi/v1/asset/transfer`、`/transferQuery` |

---

## 3. 首版 **不得** 作为 Coobit 直接调用的「能力面」（须降级）

以下 **不**分配 **`design/api.md` 冻结 PATH**（或整格延期），**网关不得**假装已支持：

| 能力 | 缺口 ID / 备注 | 系统行为 |
|------|----------------|----------|
| 现货 OCO / Bracket | **CC-P1-01** + **`product.md` §非目标（本阶段不交付）** | **`FR-T05`** **/ 主站**；**禁止** **假成交 · 假类型 A** |
| 现货计划/条件单 | **CC-P0-02** | **仅合约** `conditionOrder`；现货侧 **分步限价 + 说明** 或 **引导合约/主站** |
| 杠杆借币/还币/利息查询（自动化） | **CC-P0-02** | **仅** 已有余额下 **margin 下单**；借还 → **`FR-T05`/主站** |
| 理财细分产品 API | **CC-P0-02** | **粗粒度 `by_type`** + **`universal_transfer`**；其余 **`WEALTH_ACTION_REQUIRES_WEB`** |
| 网格 / DCA 机器人 | **非目标** | **不接** |

---

## 4. 运行时实现检查清单（摘录）

1. **子账户 Key**：**仅** `FR-T01` 绑定之私有 Key；默认 **禁止** 主账户 Key（**`design/api.md` 边界**）。
2. **幂等**：**`newClientOrderId`/`clientOrderId`**（字段名以 Spot/Margin/Futures 文档为准）+ 运行侧 `executionId` 分层。
3. **504 / UNKNOWN**：**不得**直接当失败；**查单闭环**（**`architecture.md`**）。
4. **观测**：**`coobitRequestId`**（或所内等价）写入 **`observability`**；**`exchangeViewSource`**：REST / WS / MIXED（**若实现**）。

---

**文档版本**：2026-05-20 · **维护**：Agent Runtime / 集成 owner · **本版**：**§3** **OCO/bracket **`product.md` §非目标** **同窗**。承 **2026-05-12**。
