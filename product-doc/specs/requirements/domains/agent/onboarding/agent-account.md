# Agent 账户与子账户载体

本卷描述 **账本与交易主权**：Coobit **母子账户**中的 **Agent 专用子账户**如何作为本产品默认锚点，及其与运营台 **Agent Instance** 的关系。**计费公式、账务分录、`billCode`** 宿主为 [**`billing-management`**](../../../domains/admin/billing-management/overview.md)。

---

## 1. Agent 专用子账户（账务锚）

| 维度 | 产品断言 |
|------|----------|
| **存在性** | 对每个在产品侧已进入「可使用 Agent」生命周期的 **`userId`**（**Coobit 母账户 UID**，[`overview` §1.2](overview.md)），须存在 **至多一条**由本产品默认挂载的 Agent 专用子账户，除非 **agent-management** 与 **`product`** **书面**引入多实例/多账户策略。 |
| **私域调用** | 凡触及交易所 **`trading.exchange_private`** 族能力，默认仅能经由本子账户 scope 凭据调用；与 **`product`**、[ **`trade-assistance`**](../exchange-agent/trade-assistance.md) **及 FR-T01** 同窗。 |
| **资金与计费边界** | **交易/理财写路径**：**交易所侧消耗** 默认锚定本子账户 · **现货 · USDT 可用**（**§7.4.1**）。**Agent 消耗计费（S5）**：**仅轨 B 权益核销**（**`me/commerce`**），**不**在 S5 对 Agent 消耗 **扣子账户 Token/USDT** —— [**`commerce-model`**](../../../domains/admin/billing-management/commerce-model.md)、[**`billing` §2**](../../../domains/admin/billing-management/overview.md)。 |
| **开立路径** | **子账户本体**须在所内账户体系中达到 **`billing` §2「就绪」**（可走 Coobit 既有开立能力；**非**本绑定页职责）；**与本产品 Runtime 的 API 绑定**经 **[`initialization-flow` §1.2](initialization-flow.md)** **单页校验通过后**完成；用户 **须在绑定页提交** **`agentSubAccountUid`**、Key/Secret **并完成服务端校验**（**禁止**跳过校验即宣称绑定）。 |

---

## 2. 与 Agent Instance（运营台）的关系

| 概念 | 说明 |
|------|------|
| **Template → Instance** | [**`agent-management`**](../../../domains/admin/agent-management/overview.md)：实例创建可将「本子账户就绪」列为前置之一，与 **`FEATURE*`、billing、准入**同窗。 |
| **状态展示** | 控制台 Runtime 摘要与用户侧 **`agentState`/`lastProductBlockReason`** 须可归因对齐（附录 A、[ **`agent-management/functions` §7.1**](../../../domains/admin/agent-management/functions.md) 同窗）。 |

**FR-ON03 / SC-ON-03**：禁止长期出现「控制台实例健康、会话侧却以 **`AGENT_SUBACCOUNT_BLOCKED`** 无期拦截」且无 FEATURE/灰度说明。

---

## 3. 可出现在「非密钥面」的标识符

在用户摘要 HTTP、工单、审计中可出现的字段（最小必要，脱敏以 **`design`/运营规范**为准）：

| 示例（非穷举） | 语义 |
|----------------|------|
| 子账户公开 id | 与交易所子账户只读标识对齐 |
| **`agentTradingApiKeyId`** | 绑定的是哪一把 API Key（公开 id，非 Secret） |
| **`agentTradingApiBindingStatus`** | 是否已绑定至本产品；枚举宿主 **`design`/附录 A** |

Secret / passphrase **仅**在密钥托管与 Agent Runtime 内以可操作形态出现。

---

## 4. 与 **`config` §8.2** **对读**

**子账户 id、绑定态、公开 Key id** 在用户摘要/运营协查中的业务含义与 **禁止项**：[`overview` §1.3](overview.md)。本卷 **§3** 列 **永不出密钥面**的字段范式。

---

## 5. 非目标

- 不重写主站母子账户账务内核状态机。  
- 不展开单笔 **`executionId`** 工具链归因（宿主 **exchange-agent**、**observability**）。

---

**文档版本**：1.2.1 · **维护**：产品 + Accounts owner · **本版**：§1 **开立路径** **绑定页**措辞（承 **1.2.0**）。
