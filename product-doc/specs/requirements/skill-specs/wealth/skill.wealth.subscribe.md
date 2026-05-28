# Skill · `skill.wealth.subscribe`（理财申购）

**路径**：`specs/requirements/skill-specs/wealth/skill.wealth.subscribe.md`。

**业务**：用户 **显式锁定 SKU** 的 **申购/参与** 写路径 — **不适用** 现货/合约委托版式。

**FR-T11**：本篇 **§1～§6 自包含**。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.wealth.subscribe` |
| **`skillSpecVersion`** | `0.1.0-mvp` |
| **`scenarioId`（主）** | `wealth.subscribe` |
| **流程** | [`wealth-via-agent`](../../flows/wealth-via-agent.md) **S1 类 1 → 写链** |
| **Telegram** | [`telegram/overview` §2.5.5](../../domains/agent/telegram/overview.md) |
| **状态** | **`contract-complete`**（矩阵 **TBD** 时走 **主站回退**，见 §5） |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`productId` / SKU** | ✓ | string | 产品编码 — **寄存器冻结** |
| **`amount`** | ✓ | decimal | 申购金额（**币种** 与产品规则一致） |
| **`currency`** | △ | string | 未从产品推断时 **必填** |
| **`term` / 期限** | △ | — | 若产品多期限 **须** 用户选定 |

**禁止**：未锁定 SKU 的泛推荐 → **`wealth.recommend`** 只读链，**非** 本 skill 直接写。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_TRADING=ON` 且 `FEATURE_AGENT_WEALTH=ON` | **`FR-T05`** |
| **V-02** | **FR-T02**（触及私有读/可买性） | 引导绑定 |
| **V-03** | SKU 存在且 **对用户可申购** | **`FR-T05`** / 换产品 |
| **V-04** | `amount` ≥ 产品 **最小申购** · 精度 | 追问 |
| **V-05** | 矩阵 **写 PATH 已冻结** | 否则 **`WEALTH_ACTION_REQUIRES_WEB`**（§5） |
| **V-06** | 余额/额度预检通过 | **无类型 A** |

---

## 3. Confirmation Schema（类型 A）

**一张类型 A**（理财 **无** 交易双确认，**除非** 产品另定高危链）。

**MUST**（§2.5.5）：

| 字段 | 说明 |
|------|------|
| **业务线** | **理财 / 申购**（**非** 限价市价表） |
| **产品** | 名称 + **SKU/编码摘要** |
| **`amount` + 币种** | 与将提交一致 |
| **期限 / APR** | **若适用** · **无事实不填** |
| **风险须知** | **独立段** — [`risk-disclosure`](../../prompts/confirmation/risk-disclosure.md) |

**禁止**：Secret；**禁止** 谎称已申购成功（推荐卡 **≠** 本确认）。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无 SKU** | 追问或走 **recommend** | 猜产品 |
| **无金额** | 追问 | **类型 A** |
| **仅对比收益** | 只读 **recommend** | 附带写 |
| **504 / UNKNOWN** | [`unknown-state`](../../Runtime/unknown-state.md) | 让用户重复申购 |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 理财写 **未入矩阵** / 强制主站 | Deeplink + 说明 | **`WEALTH_ACTION_REQUIRES_WEB`** — [`boundaries` §8.3](../../domains/agent/exchange-agent/boundaries.md) |
| 写闸关闭 | **FR-T05** | |
| 用户实际要 **赎回** | 切 **`skill.wealth.redeem`** | **FR-T07** |
| 现货/合约买卖措辞 | 纠偏 **trade.*** | **FR-T07** |

---

## 6. API / 写路径（设计索引）

| 动作 | PATH |
|------|------|
| **申购写** | **理财矩阵**（[`design/api`](../../../design/api.md)）— **冻结前不得假闭环** |
| **只读** | 产品列表、可买性、余额 — **B 类 tool** |

---

**文档版本**：0.1.0-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**S-08 mvp-ready · 含 WEB 回退闸**。
