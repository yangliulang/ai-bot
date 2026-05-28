# Skill · `skill.wealth.redeem`（理财赎回）

**路径**：`specs/requirements/skill-specs/wealth/skill.wealth.redeem.md`。

**业务**：用户 **赎回 / 取出 / 退出** 已持仓理财 SKU 的写路径 — **不适用** 交易四轨委托版式。

**FR-T11**：本篇 **§1～§6 自包含**。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.wealth.redeem` |
| **`skillSpecVersion`** | `0.2.0-contract` |
| **`scenarioId`（主）** | `wealth.redeem` |
| **流程** | [`wealth-via-agent`](../../flows/wealth-via-agent.md) **S1 类 3** |
| **Telegram** | [`telegram/overview` §2.5.5](../../domains/agent/telegram/overview.md) |
| **状态** | **`contract-complete`** |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`productId` / SKU** | △ | string | 用户点名产品；**未点名** → **`wealth.holdings_read`** 后追问 |
| **`amount`** | △ | decimal | 部分赎回金额/份额 |
| **`redeemAll`** | △ | bool | 「全部取出」→ **`true`**（API 字段映射寄存器冻结） |

**互斥**：`redeemAll=true` 时 **不得** 再要求口述 `amount`（除非产品规则要求二次确认部分上限）。

**持仓只读**：`wealth.holdings_read` — **无写**、**无类型 A**。

**禁止**：未持仓却发起赎回写；**禁止** 与申购 skill 混路由。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_TRADING=ON` 且 `FEATURE_AGENT_WEALTH=ON` | **`FR-T05`** |
| **V-02** | **FR-T02** | 绑定引导 |
| **V-03** | 持仓存在且 **可赎**（未到期锁仓等） | **`FR-T05`** + 可读原因 |
| **V-04** | `amount` ≤ 可赎余额；精度合法 | 追问 |
| **V-05** | 矩阵赎回写 PATH **已冻结** | **`WEALTH_ACTION_REQUIRES_WEB`**（§5） |
| **V-06** | 预检（赎回费、到账时间、最小赎回）通过 | **无类型 A** |

---

## 3. Confirmation Schema（类型 A）

**一张类型 A**（除非产品另定高危二次确认）。

**MUST**（[`telegram/overview` §2.5.5](../../domains/agent/telegram/overview.md)）：

| 字段 | 说明 |
|------|------|
| **业务线** | **理财 / 赎回** |
| **产品** | SKU + 可读名称 |
| **赎回数量/份额** | 与 API 一致；**全额** 时明示 |
| **预估到账** | **仅** 预检可得 |
| **费用/提前赎回惩罚** | **若有** 须独立可读句 |
| **到账时间口径** | **若** 预检返回则展示 |

**禁止**：Secret；**禁止** 「推荐卡」冒充已赎回；**禁止** 现货限价表版式。

**步骤 3 之前**：**禁止** `call_exchange_write`；**禁止** 声称已到账。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **多只持仓** | 列举 + 追问 SKU | 猜持仓 |
| **无持仓** | 只读结论 + 无写 | 类型 A |
| **无金额且非全额** | 追问份额或确认全额 | **类型 A** |
| **用户要申购** | 切 **`skill.wealth.subscribe`** | |
| **504 / UNKNOWN** | [`unknown-state`](../../Runtime/unknown-state.md) | 重复赎回 |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 赎回写未入矩阵 / 强制主站 | Deeplink | **`WEALTH_ACTION_REQUIRES_WEB`** — [`boundaries` §8.3](../../domains/agent/exchange-agent/boundaries.md) |
| 理财写闸关闭 | **FR-T05** | |
| 用户要申购 | **`skill.wealth.subscribe`** | **FR-T07** |
| 现货/合约买卖 | **`trade.*`** | **FR-T07** |
| 矩阵 PATH TBD | **FR-T05**；**禁止** 类型 A 假闭环 | |

---

## 6. API / 写路径（设计索引）

| 动作 | PATH |
|------|------|
| **赎回写** | 理财矩阵 — [`design/api`](../../../design/api.md) |
| **持仓只读** | 矩阵 **GET** 族 · `wealth.holdings_read` |

**对签**：[`wealth-via-agent`](../../flows/wealth-via-agent.md)、[`trade-assistance` §8.2](../../domains/agent/exchange-agent/trade-assistance.md)。

---

**文档版本**：0.2.0-contract · **维护**：产品 + Agent Runtime owner · **本版**：**S-09 自包含（§5 不再外链 subscribe）**。
