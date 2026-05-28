# Skill · `skill.spot.amend_limit_order`（现货限价 · 逻辑改单）

**路径**：`specs/requirements/skill-specs/spot/skill.spot.amend_limit_order.md`。

**业务**：**在途现货限价单** 改价/改量 — **无** 交易所单笔 amend API → **单次类型 A** 授权后 **`cancel` →（对账）→ `order`**。

**FR-T11**：本篇 **§1～§6 自包含**。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.spot.amend_limit_order` |
| **`skillSpecVersion`** | `0.1.0-contract` |
| **`scenarioId`（主）** | `trade.spot.amend_limit_order` |
| **流程** | [`trade-via-agent` 专节 · 逻辑改单](../../flows/trade-via-agent.md) |
| **编排冻结** | [`runtime-freeze` §3.7](../../domains/agent/agent-orchestration/runtime-freeze.md) |
| **Telegram** | [`telegram/overview` §2.5.2 · 逻辑改单](../../domains/agent/telegram/overview.md) |
| **状态** | **`contract-complete`** |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`originalOrderId`** | △ | string | 原单 `orderId`；**或** 可由 `clientOrderId` 只读解析 |
| **`originalClientOrderId`** | △ | string | 与上 **二选一** 可定位在途单 |
| **`symbol`** | ✓ | string | **须** 与原单一致（只读校验） |
| **`side`** | ✓ | enum | **须** 与原单一致 |
| **`type`** | ✓ | enum | **固定** `LIMIT` |
| **`price`** | ✓ | decimal | **新** 委托价 |
| **`quantity`** | ✓ | decimal | **新** 数量（**部成** 场景见 §2 **V-08**） |
| **`timeInForce`** | △ | enum | 变更时 **须** 在卡面可见 |
| **`newClientOrderId`** | — | string | 序 3 **新单** 幂等键 — **禁止** 复用原单 |

**前置**：用户意图为 **改价/改量/换掉当前挂单**；**非** 新开仓首单 → **`skill.spot.limit_order`**。

**禁止**：无在途单却走改单；**禁止** 与 OCO/bracket 混称改单。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_AGENT_SPOT=ON` | **`FR-T05`** |
| **V-02** | **FR-T02** | 绑定引导 |
| **V-03** | 原单 **可识别** 且 **为限价在途** | **`FR-T05`** / 改走新挂单 |
| **V-04** | 新 `price`/`quantity` 精度、**minNotional** | 追问 |
| **V-05** | **FR-T12** 偏离带（若 Guard ON） | 拒答或建议价第二张 A |
| **V-06** | **类型 A 未确认** | **禁止** 序 1 `cancel` |
| **V-07** | 新参 **与卡面一致** | 禁止确认后改参 |
| **V-08** | 原单 **部成**：产品规则定义可撤余量 | 卡面 **明示** 针对剩余量 |

---

## 3. Confirmation Schema（类型 A）

**仅一张类型 A**（**非** 撤、建各一张）。

**MUST**：

| 字段 | 说明 |
|------|------|
| **标题语境** | 「修改挂单 / 调整委托」类 — **非** 裸「确认」 |
| **原单摘要** | `orderId` 或 client 摘要、symbol、side、原价量 |
| **新单全文** | 新 `price`、`quantity`、`timeInForce` 等 |
| **披露句** | **须含**「确认后将先撤销原委托，再提交新委托」 |
| **变更对比** | 变更字段 **原→新** 并列 |

**步骤 3 之前**：**禁止** `cancel` / `order` 写。

**确认后体验**：[`telegram` 逻辑改单确认后表](../../domains/agent/telegram/overview.md) — 进行中 / 撤败 / 撤成单败 / 新单挂上。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无法定位原单** | 只读 `openOrders` 或追问 | 猜 orderId |
| **无新价或新量** | 追问 | **类型 A** |
| **用户要全新挂单** | 切 **`limit_order`** | 改单 skill |
| **序 1 后 UNKNOWN** | 查单 + [`unknown-state`](../../Runtime/unknown-state.md) | 「改单成功」 |
| **序 3 失败** | 明示原单已撤、新单未立 | 成功终局话术 |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 全仓/合约改单 | 各 skill / **FR-T05** | **FR-T07** |
| 全仓杠杆 Telegram 撤改 | 主站 | **trade-via-agent 全仓首版不承诺** |
| OCO/bracket | **product.md §非目标** | |
| 矩阵无 cancel/order | **FR-T05** | |

---

## 6. API / 写路径（设计索引）

| 序 | 动作 | PATH |
|:--:|------|------|
| 1 | 撤原单 | `POST /sapi/v2/cancel` |
| 2 | 查单（若需） | `GET /sapi/v2/order`、`openOrders` |
| 3 | 挂新单 | `POST /sapi/v2/order`（**新** `newClientOrderId`） |

**禁止序**：**先 3 后 1**。**对签**：[`trade-via-agent` 逻辑改单专节](../../flows/trade-via-agent.md)、[`runtime-freeze` §3.7](../../domains/agent/agent-orchestration/runtime-freeze.md)。

---

**文档版本**：0.1.0-contract · **维护**：产品 + Agent Runtime owner · **本版**：**逻辑改单现货 · 首版自包含**。
