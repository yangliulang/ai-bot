# Skill · `skill.margin.cross_market_order`（全仓杠杆 · 市价）

**路径**：`specs/requirements/skill-specs/margin/skill.margin.cross_market_order.md`。

**业务**：**全仓（cross）** 杠杆 **市价** 借买/卖还 — **`POST /sapi/v2/margin/order`** 族；**逐仓（isolated）** **不得** 走本 skill。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.margin.cross_market_order` |
| **`skillSpecVersion`** | `0.1.0-mvp` |
| **`scenarioId`（主）** | `margin.cross.market_order` |
| **`confirmation-flow`** | [`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md) + **强制二次确认** |
| **流程** | [`trade-via-agent` 专节 · 全仓杠杆（cross）](../../flows/trade-via-agent.md) |
| **Telegram** | [`telegram/overview` §2.5.3](../../domains/agent/telegram/overview.md) |
| **状态** | **`contract-complete`** |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`symbol`** | ✓ | string | 交易对（如 `BTC_USDT`） |
| **`side`** | ✓ | enum | 产品语义 **借钱买入** ↔ `BUY`；**卖出还款** ↔ `SELL` — **映射须在寄存器冻结** |
| **`type`** | ✓ | enum | **固定** `MARKET`（**无** 可解析限价时） |
| **`quantity`** | △ | decimal | **base** 数量 |
| **`quoteQty`** | △ | decimal | **计价金额**；与 **`quantity`** **二选一** |
| **`autoBorrow`** | △ | bool | **默认 `true`**；卡面 **须** 可读披露借币/计息 |
| **`autoRepay`** | △ | bool | API 支持且用户意图为卖还时 — **卡面自然语言可见** |
| **`price`** | ✗ | — | **市价 skill 禁止**；有明确限价 → **`skill.margin.cross_limit_order`** |

**分流（FR-T07）**：

- **仅当** 用户 **明确** 杠杆/借还/保证金率/可借额度等 → **`margin.cross.*`**。  
- 「买点 BTC」**未** 提杠杆 → **`trade.spot.flash_convert`** 或 **`trade.spot.limit_order`**，**非** 本 skill。

**歧义**：USDT 金额 vs 标的数量 → **须澄清**。

**前置划转（非本 skill 参数，但同窗流程）**：全仓可用不足且现货可调拨 → **独立划转类型 A**（`margin.cross.transfer_in` 族）— [`trade-via-agent` 专节第四步](../../flows/trade-via-agent.md)、[`boundaries` §8.4](../../domains/agent/exchange-agent/boundaries.md)。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_TRADING=ON` 且 `FEATURE_AGENT_MARGIN=ON` | **`FR-T05`** |
| **V-02** | **FR-T02** · 子账户 scope | 引导绑定 |
| **V-03** | `symbol` 支持 **cross** 杠杆 | **`FR-T05`** |
| **V-04** | 数量/金额 **步进 / minNotional** | 追问 |
| **V-05** | **写前预检**（可借、维持保证金、预估借入、偏离带等） | **无首张类型 A** |
| **V-06** | 拟 **划转** 且矩阵未入模板 / 策略拒绝 | **`TRANSFER_REQUIRES_WEB`** + 主站 |
| **V-07** | **首张 + 第二张** 类型 A **均未** `CONFIRMED` | **禁止** `POST …/margin/order` |

**Telegram 首版**：**撤单/改单** **不承诺** — [`telegram/overview` §2.5.3](../../domains/agent/telegram/overview.md)。

---

## 3. Confirmation Schema（类型 A）

**强制二次确认**（**两张** 摘要或等价 — **ADR-001**）：

1. **首张**：方向、币对、**全仓** 标注、市价、数量/名义、**预估借入**、计息提示、风险档位（低/中/高 — 预检后）。  
2. **第二张**：**再摘要** 关键数字；**无「不再提示」**。

**若含「币币 → 全仓」划转**：**划转须独立类型 A**（币种、数额、方向可读）→ **用户确认后** 编排 **代发** 划转 API → **再** 进入委托预检与下单卡 — **非免确认**。

**类型 A MUST**（[`telegram/overview` §2.5.3 · 全仓市价](../../domains/agent/telegram/overview.md)）：

| 字段 | 说明 |
|------|------|
| **业务线** | **全仓杠杆**（与现货、合约版式区分） |
| **`symbol` / `side`** | 币对 + 借买/卖还可读文案 |
| **订单类型** | **市价** |
| **数量/名义** | 单位写清 |
| **预估借入** | **仅** 预检可得 |
| **计息/风险** | 浮动利率提示；中/高档 **风险披露** — [`risk-disclosure`](../../prompts/confirmation/risk-disclosure.md) |

**步骤 3 之前**：**禁止** 写；**禁止** 声称已成交。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无杠杆语义却路由到此** | 纠偏 **spot / futures** | 默认借币买 |
| **无方向/标的/数量** | 追问 | **首张类型 A** |
| **用户给限价** | 切 **`skill.margin.cross_limit_order`** | 市价 skill 带 `price` |
| **划转未确认** | 展示划转卡或 **`TRANSFER_REQUIRES_WEB`** | 静默扣现货 |
| **预检失败** | 短因 + 建议 | 双卡后仍写 |
| **504 / UNKNOWN** | [`unknown-state`](../../Runtime/unknown-state.md) | 重复下单 |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 全仓写闸关闭 | **FR-T05** | |
| **无借还措辞** 的普通买卖 | **`trade.spot.*`** | **FR-T07** |
| 合约/永续意图 | **`trade.futures.*`** | **FR-T07** |
| 逐仓 **isolated** | 另立法 / **FR-T05** | |
| 杠杆挂单 **止盈止损**（首版） | **FR-T05** / 主站 | **trade-via-agent 专节首版不承诺** |
| 矩阵 PATH **TBD** | **FR-T05** + 能力边界 | |

---

## 6. API / 写路径（设计索引）

| 动作 | PATH |
|------|------|
| **全仓下单** | `POST /sapi/v2/margin/order`（**市价**） |
| **预检只读** | `GET …/margin/*` 等 + 规则引擎 |
| **子账户划转** | `universal_transfer` / `asset/transfer`（**独立确认**） — [`design/api`](../../../design/api.md) §8.4 |

**对签**：[`agent-coobit-api-allowlist`](../../integrations/exchange/agent-coobit-api-allowlist.md)、[`design/api`](../../../design/api.md) **cross 矩阵**。

---

**文档版本**：0.1.0-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**S-06 mvp-ready · 对齐 trade-via-agent 全仓专节 + 双确认**。
