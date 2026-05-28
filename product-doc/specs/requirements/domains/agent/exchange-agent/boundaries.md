# Exchange Agent · 边界与非目标（Boundaries）

**路径**：`specs/requirements/domains/agent/exchange-agent/boundaries.md`。

**职责**：**产品与合规边界**：**须回退主站**的能力（**稳定码 + Deeplink 下限**）、**Kill/叠层** **呈现原则**（**与** [`../runtime/`](../runtime/) **及** [**`Runtime/overview.md`**](../../../Runtime/overview.md)、[**`freeze-policy.md`**](../../../Runtime/freeze-policy.md) **同窗**）、**不提供投资建议**、**禁止静默代用户确认** **等**。**承接**原 **`risk.md` §8.x** **主站回退** **叙事**（**与** [`../../../../design/api.md`](../../../../design/api.md) **「矩阵缺项」** **一致**）。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 全局原则

| 原则 | 说明 |
|------|------|
| **矩阵终裁** | **`design/api.md` 未列 / PATH 为 TBD** → **不实现、不承诺**；**用户可见** **稳定拒答** **见** **`FR-T05`** **同窗** [`../../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md)。 |
| **写须确认** | **每一笔** **`call_exchange_write`** **前** **类型 A**（**Telegram** **等**）— **ADR-001** [`../../../../design/adr/001-telegram-confirm-before-coobit-write.md`](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)。 |
| **非投顾** | **任何** **自然语言** **收益/风险结论** **须** **Disclaimer**；**不得** **保证** **收益** **或** **代替** **用户** **风险承受判断**。 |

---

## 2. 稳定码索引（下限 · 与流程对签）

| 稳定码 / 主题 | 典型触发 | 用户侧动作 |
|----------------|----------|------------|
| **`WEALTH_ACTION_REQUIRES_WEB`** | **理财写** **未** **纳入** **矩阵模板** **或** **所内强制主站** | **Deeplink** **主站** **完成** **申购/赎回** **等** — **同窗** [`../../../flows/wealth-via-agent.md`](../../../flows/wealth-via-agent.md) |
| **`TRANSFER_REQUIRES_WEB`** | **`universal_transfer` / 划转** **未入模板** **或** **策略拒绝对话内自动划转** | **主站** **或** **重新走** **显式** **类型 A** **链** — **同窗** [`../../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) **全仓专节** |
| **`FR-T05`** **族** | **能力不可用** **/ 参数不合法** **/ 计费或 gate** | **可读** **错误摘要** **+** **不** **伪造** **成交** |
| **`PRICE_REJECTED_AGENT_BAND`** | **限价** **相对** **参考价** **超出** **运营偏离带**（**`FR-T12`/`AGENT_PRICE_*`**） | **会话稳定码** **—** **澄清** **或** **建议价** **分支**；**不入** **`billing` `billCode`** — **同窗** [`../../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) **现货限价 · 第五步** |
| **矩阵 `TBD` / 私读未就绪** | **`design/api` PATH 未冻结** **或** **触及** **`trading.exchange_private`** **而** **`FR-T02`** **未通过** | **`FR-T05` 透明拒答** **或** **主站/开通 Deeplink**；**禁止** **用** **`tool.market.*`** **顶替** **成交/持仓叙事** |

---

> **章节编号**：下文 **§8.3、§8.4** 沿用旧版 `risk.md` 的 **§8** 编号习惯，故正文从 **§8** 起跳，**不设 §3～§7**。**§9** **为** **`runtime-policy` / `trading-agent-config`** **补篇**（**独立** **编号**，**非** **填补** **§3～§7**）。

## 8. 主站回退条（承接原 `risk.md` 编号）

### 8.3 理财写 · 主站回退（`WEALTH_ACTION_REQUIRES_WEB`）

**当** **理财相关写** **无法** **在** **Agent 范围** **内** **以** **已冻结 API** **安全落地** **时** **须** **返回** **`WEALTH_ACTION_REQUIRES_WEB`** **并** **提供** **主站 Deeplink**（**细节** **Telegram §2.5.5** **同窗** [`../telegram/overview.md`](../telegram/overview.md)）。**计费** **是否** **仍** **`accepted`** → **同窗** **`billing`** **与** [`../../../flows/wealth-via-agent.md`](../../../flows/wealth-via-agent.md)。

### 8.4 划转 · 模板与拒答（`TRANSFER_REQUIRES_WEB`）

**全仓** **等** **场景** **下** **拟** **划转** **若** **未** **满足** **流程模板**（**或** **用户** **未** **对** **该笔** **类型 A**）→ **`TRANSFER_REQUIRES_WEB`** **或** **重入** **确认** **链**。**不得** **静默** **从** **现货** **扣款** **至** **保证金** **账户** **不经** **确认**。

**产品语义「自动划转」**（**如** **杠杆下单前** **从** **币币** **归集** **至** **全仓**）：**仅指** **用户已在对话内对该笔划转** **完成类型 A** **后**，由运行时 **代发** **划转 API** **并** **自动衔接** **同一轮** **`margin.cross.*`** **下单链** — **仍须** **在卡面** **展示** **币种与数额**；**不等价于** **免确认**、**不展示** **或** **后台代替用户授权**。

---

## 9. Runtime 交易政策（`trading-agent-config` 对签）

**目的**：承接原 **`runtime-policy`** **叙事** **与** [`../../admin/trading-agent-config/keys.md`](../../admin/trading-agent-config/keys.md) **表内** **「见 `runtime-policy` §n」** **类** **指针**；**`configKey` 枚举 / JSON Schema** **以** **`design`/OpenAPI + 附录 A §5.1** **终裁**。**全局风险横切索引**：[`../../../risk/README.md`](../../../risk/README.md)。

<a id="2-runtime-trading-policy-priority运行时配置叠层优先级"></a>

### 9.1 配置叠层优先级

**全局 `configKey` 为底**；**`agent-management` 发布模板** 对风控类键 **只可收紧、不可放宽** — 同窗 [`../../admin/trading-agent-config/functions.md`](../../admin/trading-agent-config/functions.md) **§2.6**、[`../../admin/agent-management/rules.md`](../../admin/agent-management/rules.md)。

<a id="4-confirmation-policy交易确认策略"></a>

### 9.2 交易确认策略（大额与冷却）

**大额订单阈**（**`AGENT_LARGE_ORDER_THRESHOLD_USDT`** 等）**用于** **运营定义之** **增强确认 / 频控** **入口**；**与** **类型 A、合约/杠杆 `risk-disclosure` 串联** **分工** — **编排 SSOT** [`../agent-orchestration/confirmation-flow.md`](../agent-orchestration/confirmation-flow.md)、**Prompt** [`../../../prompts/trading/futures.md`](../../../prompts/trading/futures.md)。**冷却与高频写窗**（**`AGENT_COOLDOWN_SEC`、`AGENT_HFT_*`**）**同窗** [`../../../risk/exposure-limit.md`](../../../risk/exposure-limit.md)。

<a id="6-position-governance仓位治理"></a>

### 9.3 仓位治理（净敞口与集中度）

**净名义敞口上限**（**`AGENT_MAX_NET_EXPOSURE_USDT`**）、**最大交易币种数**（**`AGENT_MAX_DISTINCT_SYMBOLS`**）、**单币占比**（**`AGENT_MAX_SINGLE_SYMBOL_WEIGHT_BPS`**）**及** **会话亏损闸**（**`AGENT_MAX_SESSION_LOSS_USDT`**）**之** **产品含义** **见** [`../../../risk/exposure-limit.md`](../../../risk/exposure-limit.md)；**Portfolio 只读输入** [`portfolio-insight.md`](portfolio-insight.md)。**超限** **须** **透明拒答** — **与** **`FR-T09`** **精神** **同窗** [`trade-assistance.md`](trade-assistance.md) **§2**。

<a id="7-market-scope-governance市场范围治理"></a>

### 9.4 市场范围治理（产品线闸）

**`FEATURE_AGENT_FUTURES`**：**V1 默认 OFF**；**开启** **须** **与** **合规 / 所内策略** **对签** — 同窗 [`../../admin/trading-agent-config/keys.md`](../../admin/trading-agent-config/keys.md) **§2**、[`overview.md`](overview.md) **§3**。**现货 / 杠杆 / 理财** **等** **键** **同窗** **`keys` §2**；**杠杆运营上限**（**`AGENT_MAX_LEVERAGE`** **等**）**同窗** [`../../../risk/leverage-limit.md`](../../../risk/leverage-limit.md)。

---

## 10. 互引

| 文档 | 关系 |
|------|------|
| [`trade-assistance.md`](trade-assistance.md) | **确认闸门** **与** **写** |
| [`risk-alerts.md`](risk-alerts.md) | 风险 **外显** |
| [`monitoring-tasks.md`](monitoring-tasks.md) | **通知过载** **与** **退订** |
| [`../../../../design/api.md`](../../../../design/api.md) | **矩阵缺项**；**对账 PATH** **专节** **同窗** **`Runtime/reconciliation`** |
| [`../../../contract-closure.md`](../../../contract-closure.md) | **收口索引**：**§1·第 6 款** **WS+REST 视图承诺链**（**同窗** **`trade-assistance` §2.5**、**`design/api` 对账专节**、**`Runtime/reconciliation`**、**`observability` §2/`SC-OBS06`**） |
| [`../onboarding/`](../onboarding/) | **授权与就绪** |
| [`../../../Runtime/reconciliation.md`](../../../Runtime/reconciliation.md) | 交易所 REST↔WS **对账与真相源次序**（平台政策） |
| [`../../../Runtime/unknown-state.md`](../../../Runtime/unknown-state.md) | **`504`/UNKNOWN** 下限 |
| [`../../../Runtime/error-normalization.md`](../../../Runtime/error-normalization.md) | 上游错误 → **`stableReason`** **映射契约** |
| [`../../../integrations/exchange/overview.md`](../../../integrations/exchange/overview.md) | 交易所 **上游** GitBook 索引（**非** Runtime） |
| [`../../../risk/README.md`](../../../risk/README.md) | **全局风险** **横切索引**（**Kill / 护栏键 / 确认 / 合规** **指针**） |
| [`../../../risk/acceptance.md`](../../../risk/acceptance.md) | **`SC-RISK-01～05`** **横切验收** |

**文档版本**：0.3.7 · **维护**：产品 + 合规/交互 owner · **本版**：**§8.4** **补** **「自动划转」** **产品语义**（**确认后代发 + 衔接下单** **≠** **免确认**）。**顺延 0.3.6** …
