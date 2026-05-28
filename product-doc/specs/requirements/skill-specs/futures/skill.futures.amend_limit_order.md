# Skill · `skill.futures.amend_limit_order`（合约限价 · 逻辑改单）

**路径**：`specs/requirements/skill-specs/futures/skill.futures.amend_limit_order.md`。

**业务**：**在途永续限价单** 改价/改量 — **单次类型 A** 后 **`POST /fapi/v1/cancel` → 对账 → `POST /fapi/v1/order`**。

**FR-T11**：本篇 **§1～§6 自包含**。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.futures.amend_limit_order` |
| **`skillSpecVersion`** | `0.1.0-contract` |
| **`scenarioId`（主）** | `trade.futures.amend_limit_order` |
| **流程** | [`trade-via-agent` 专节 · 逻辑改单](../../flows/trade-via-agent.md) |
| **编排冻结** | [`runtime-freeze` §3.7](../../domains/agent/agent-orchestration/runtime-freeze.md) |
| **Telegram** | [`telegram/overview` §2.5.4 · 逻辑改单](../../domains/agent/telegram/overview.md) |
| **状态** | **`contract-complete`** |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`originalOrderId`** | △ | string | 原单标识 |
| **`symbol`** | ✓ | string | 与原单一致 |
| **`side` / 开平语义** | ✓ | — | 与原单一致 |
| **`type`** | ✓ | enum | **固定** `LIMIT` |
| **`price`** | ✓ | decimal | **新** 委托价 |
| **`quantity`** | ✓ | decimal | **新** 数量 |
| **`qtyUnit`** | ✓ | enum | 张 / 币 |
| **`reduceOnly`** | △ | bool | 若原单为平仓单 **须** 卡面可见 |
| **`leverage` / `marginMode`** | △ | — | 变更时 **须在卡面** 明示 |
| **`newClientOrderId`** | — | string | 新单幂等 — **禁止** 复用原单 |

**前置**：在途 **限价** 改参；**非** 条件单 → **`take_profit_stop`**。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_AGENT_FUTURES=ON` | **`FR-T05`** |
| **V-02** | **FR-T02** · fapi | 绑定 |
| **V-03** | 原单可识别且为限价在途 | **`FR-T05`** |
| **V-04** | 新价量精度、步进 | 追问 |
| **V-05** | 开平 × `reduceOnly` 自洽 | 追问 |
| **V-06** | **类型 A 已消费** 方可序 1 | 禁止先 cancel |
| **V-07** | 部成规则（同窗现货改单） | 卡面明示 |

---

## 3. Confirmation Schema（类型 A）

**仅一张类型 A**。

**MUST**：

| 字段 | 说明 |
|------|------|
| **标题** | 「修改永续限价挂单」类 — **非** 含糊「已完成」 |
| **原单摘要** | 合约、开平、原价量、张/币单位 |
| **新单全文** | 新 `price`、`quantity`、`reduceOnly`、将用杠杆/模式 |
| **披露句** | **须含** 先撤销原委托再提交新委托 |
| **原→新** | 变更字段并列 |

**步骤 3 之前**：**禁止** cancel/order。

**确认后**：同窗 **telegram §2.5.4 逻辑改单**（**SC-CH-TG-FUT-05**）。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无原单** | 只读查单 / 追问 | 猜单 |
| **无新参** | 追问 | **类型 A** |
| **撤成单败** | 模板含下一步 | 「改单成功」 |
| **504** | [`unknown-state`](../../Runtime/unknown-state.md) | 重复 cancel+order |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 现货改单 | **`skill.spot.amend_limit_order`** | **FR-T07** |
| 条件单改触价 | **`take_profit_stop`** | |
| 全仓杠杆撤改 | 主站 **FR-T05** | |
| 矩阵 TBD | **FR-T05** | |

---

## 6. API / 写路径（设计索引）

| 序 | PATH |
|:--:|------|
| 1 | `POST /fapi/v1/cancel` |
| 2 | `GET` 订单 / 持仓（对账） |
| 3 | `POST /fapi/v1/order`（**新** clientOrderId） |

**对签**：[`agent-coobit-api-allowlist`](../../integrations/exchange/agent-coobit-api-allowlist.md)、[`trade-via-agent` 逻辑改单](../../flows/trade-via-agent.md)。

---

**文档版本**：0.1.0-contract · **维护**：产品 + Agent Runtime owner · **本版**：**逻辑改单合约 · 首版自包含**。
