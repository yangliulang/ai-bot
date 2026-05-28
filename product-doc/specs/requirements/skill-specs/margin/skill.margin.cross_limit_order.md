# Skill · `skill.margin.cross_limit_order`（全仓杠杆 · 限价）

**路径**：`specs/requirements/skill-specs/margin/skill.margin.cross_limit_order.md`。

**业务**：**全仓（cross）** 杠杆 **限价** 借买/卖还 — **`POST /sapi/v2/margin/order`**（`LIMIT` + `price`）；**逐仓** **不得** 走本 skill。

**FR-T11**：本篇 **§1～§6 自包含** — **禁止**「仅读 S-06 市价 skill + 本篇两行增量」作为操作规范。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.margin.cross_limit_order` |
| **`skillSpecVersion`** | `0.2.0-contract` |
| **`scenarioId`（主）** | `margin.cross.limit_order` |
| **`confirmation-flow`** | [`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md) + **强制二次确认** |
| **流程** | [`trade-via-agent` 专节 · 全仓杠杆](../../flows/trade-via-agent.md) |
| **Telegram** | [`telegram/overview` §2.5.3 · 全仓限价](../../domains/agent/telegram/overview.md) |
| **状态** | **`contract-complete`** |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`symbol`** | ✓ | string | 交易对（如 `BTC_USDT`） |
| **`side`** | ✓ | enum | 借钱买入 ↔ `BUY`；卖出还款 ↔ `SELL`（寄存器冻结映射） |
| **`type`** | ✓ | enum | **固定** `LIMIT` |
| **`price`** | ✓ | decimal | 委托单价 · **`tickSize`** |
| **`quantity`** | △ | decimal | base 数量 |
| **`quoteQty`** | △ | decimal | 计价金额；与 **`quantity`** **二选一** |
| **`autoBorrow`** | △ | bool | **默认 `true`**；计息须在卡可读 |
| **`autoRepay`** | △ | bool | 卖还语义且 API 支持时卡面可见 |

**路由**：

- 限价语义（挂单、限价、到价等）→ **本 skill**。  
- **未指定价格** → **`skill.margin.cross_market_order`**。  
- **无杠杆/借还措辞** 的普通买卖 → **`trade.spot.*`**，**非** 本 skill。

**歧义**：USDT 金额 vs 标的数量 → **须澄清**。

**划转前置**：全仓不足且现货可调拨 → **独立划转类型 A**（`margin.cross.transfer_in`）— [`trade-via-agent` 第四步](../../flows/trade-via-agent.md)、[`boundaries` §8.4](../../domains/agent/exchange-agent/boundaries.md)。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_TRADING=ON` 且 `FEATURE_AGENT_MARGIN=ON` | **`FR-T05`** |
| **V-02** | **FR-T02** | 绑定引导 |
| **V-03** | `symbol` 支持 **cross** | **`FR-T05`** |
| **V-04** | `price` > 0；**`tickSize`** | 追问 |
| **V-05** | 数量/金额步进、**minNotional** | 追问 |
| **V-06** | **写前预检**（可借、维持保证金、预估借入、限价偏离） | **无首张类型 A** |
| **V-07** | 划转：矩阵未入模板 / 未确认 | **`TRANSFER_REQUIRES_WEB`** 或重入确认 |
| **V-08** | **首张 + 第二张** 类型 A 均未确认 | **禁止** `POST …/margin/order` |
| **V-09** | 缺 `price` | **禁止** 类型 A |

**限价偏离**：以 **预检 / 所内规则** 为准（**非** 默认现货 **FR-T12** 路径）。

**首版**：Agent **不承诺** 全仓撤单/改单 — [`telegram` §2.5.3](../../domains/agent/telegram/overview.md)。

---

## 3. Confirmation Schema（类型 A）

**强制二次确认**（两张摘要，**无「不再提示」**）：

1. **首张**：全仓标注、限价 + **`price`**、方向、数量/名义、预估借入、计息、风险档。  
2. **第二张**：关键数字再摘要。

**限价增量 MUST**：

| 字段 | 说明 |
|------|------|
| **订单类型** | **限价** |
| **成交说明** | 不保证立即成交；触发前为挂单语义 |

**划转**：若展示「币币 → 全仓」→ **独立类型 A** 确认后编排代发，**再** 进入下单卡。

**步骤 3 之前**：**禁止** 写；**禁止** 声称已成交/已挂单终局。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无杠杆语义** | 纠偏 spot/futures | 默认借币 |
| **无 `price`** | 追问 | **类型 A** |
| **无方向/标的/数量** | 追问 | **首张类型 A** |
| **用户要市价** | 切 **`cross_market_order`** | 限价 skill 无 price 提交 |
| **划转未确认** | 划转卡或 **`TRANSFER_REQUIRES_WEB`** | 静默划现货 |
| **预检失败** | 短因 | 双卡后仍写 |
| **504 / UNKNOWN** | [`unknown-state`](../../Runtime/unknown-state.md) | 重复下单 |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 全仓写闸关闭 | **FR-T05** | |
| 普通现货买卖 | **`trade.spot.*`** | **FR-T07** |
| 合约永续 | **`trade.futures.*`** | **FR-T07** |
| 逐仓 isolated | **FR-T05** / 另立法 | |
| 杠杆挂单止盈止损（首版） | 主站 / **FR-T05** | |
| 矩阵 TBD | **FR-T05** | |

---

## 6. API / 写路径（设计索引）

| 动作 | PATH |
|------|------|
| **全仓限价下单** | `POST /sapi/v2/margin/order`（`LIMIT` + `price`） |
| **预检** | `GET …/margin/*` + 规则引擎 |
| **划转** | `universal_transfer` / `asset/transfer`（**独立类型 A**） |

**对签**：[`agent-coobit-api-allowlist`](../../integrations/exchange/agent-coobit-api-allowlist.md)、[`design/api`](../../../design/api.md)。

---

**文档版本**：0.2.0-contract · **维护**：产品 + Agent Runtime owner · **本版**：**S-07 自包含正文（原增量骨架已合并）**。
