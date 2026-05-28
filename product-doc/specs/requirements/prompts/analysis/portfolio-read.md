# Analysis · Portfolio read（账户只读）

**路径**：`specs/requirements/prompts/analysis/portfolio-read.md`。  
**Publish SSOT**：[`prompt-management`](../../domains/admin/prompt-management/overview.md)。

**索引**：[`README`](./README.md)

> **Publish 正文**：统一 **`pp-analysis-core`**。**本文**为 **账户只读能力语义分卷**，**非**独立发布包。

---

## 1. 范围（本文）

- **余额、持仓、在途挂单、盈亏 / 敞口 / 保证金占用（聚合口径）** — **只读**，不把 ticker **现价**等同于已实现盈亏 — [`portfolio-insight`](../../domains/agent/exchange-agent/portfolio-insight.md)、[`exchange-agent/intents` §3](../../domains/agent/exchange-agent/intents.md)。

---

## 2. 与其它 analysis 分卷（示意）

| 用户像在问 | **优先归本文** | **不归本文** |
|-------------|----------------|---------------|
| 我有多少 XX、盈亏多少、保证金够不够 | ✓ | 纯「BTC 现价」→ [`market-analysis.md`](./market-analysis.md) |
| 撤单/下单怎么做（即便顺带问了盈亏） | 先答 **只读** 部分 | **写** → [`../intents/trade.md`](../intents/trade.md) |

---

## 3. 工具与事实（防幻觉）

- **声称「刚查了交易所侧私有视图」（持仓/余额/订单列表）**：须在 [`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md) 登记之 **只读 skill** **成功闭环后**方可这么说 — 否则 **澄清无法调取或引导绑定**，**禁止编造持仓数字** — [`observability/hallucination`](../../observability/hallucination.md)、[`safety/privilege`](../safety/privilege.md)。

---

## 4. 话术下限

- **非投顾**：[`system/system.md`](../system/system.md) **§1**。  
- **与下单同桌**：用户顺带下单 → **只读答复可与追问分拆**；**写路径** **单独**走 [`confirmation/order-confirmation`](../confirmation/order-confirmation.md)，默认 **不**在答复里弱化确认链 — [`../intents/analysis.md`](../intents/analysis.md)。  
- **失败 / UNKNOWN**：[`shared/common-phrases` §2](../shared/common-phrases.md)、[`Runtime/unknown-state`](../../Runtime/unknown-state.md)、[`error-normalization`](../../Runtime/error-normalization.md)。

---

**文档版本**：1.4.0-mvp · **维护**：产品 + Prompt owner · **本版**：**目录 README**。
