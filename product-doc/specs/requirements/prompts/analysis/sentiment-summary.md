# Analysis · Sentiment summary（条文）

**路径**：`specs/requirements/prompts/analysis/sentiment-summary.md`。  
**Publish SSOT**：[`prompt-management`](../../domains/admin/prompt-management/overview.md)。

**索引**：[`README`](./README.md)

> **Publish 正文**：统一 **`pp-analysis-core`**。**本文**为 **舆情/情绪能力语义分卷**，**非**独立发布包。

---

## 1. 范围（本文）

- **舆情聚合、讨论热度、情绪倾向摘要**（社媒/社区/新闻标题情绪 **等非私密持仓数据**）。  
- **流程**：[`read-analyze-and-search-via-agent`](../../flows/read-analyze-and-search-via-agent.md) **C 类**（**`research.sentiment_and_news`** 等）。  
- **能力宿主**：[`market-intelligence`](../../domains/agent/exchange-agent/market-intelligence.md)；**外网 ADR** → [`contract-closure` CC-P1-02](../../contract-closure.md)。

---

## 2. 与其它 analysis 分卷（示意）

| 主题 | **归本文** | **不归本文** |
|------|------------|---------------|
| 恐慌贪婪、论坛多空氛围 | ✓ | Funding **费率事实** → [`market-analysis.md`](./market-analysis.md) |
| 宏观政策 **传闻** | ✓（须降级置信） | **已落地监管条文解读** → **慎答**，同窗 [`boundaries`](../../domains/agent/exchange-agent/boundaries.md) |
| K 线形态教学 | ✗ | [`technical-analysis.md`](./technical-analysis.md) |

---

## 3. 工具与事实（防幻觉）

- **声称「采集了某平台实时舆情统计」**：须有 **登记数据源/skill 成功闭环**；否则 **标明二手摘要或无法核实** — [`hallucination`](../../observability/hallucination.md)。

---

## 4. 话术下限

- **来源不确定 / 传言**：**显式降级置信**，**不当事实断言**。  
- **情绪叙事**：**可** **用** **Trader Narrative Anchors**（[`common-phrases` §8/§8.7](../shared/common-phrases.md)）**描述** **「市场偏谨慎/偏亢奋」** — **须** **与** **数据源 Facts 同窗**；**禁止** **无来源编造 crowd 情绪**；**禁止** **用舆情** **替代** **交易所 ticker/Funding 数值** — **同窗** [`system/system.md` §6.3](../system/system.md)。  
- **合规**：不煽动操纵市场、不捏造监管结论 — [`boundaries`](../../domains/agent/exchange-agent/boundaries.md)。  
- **非投顾 / 不提供个性化配资**：[`system/system.md`](../system/system.md) **§1**、**§4**；更深 stablecoin/合规边界同窗 **`boundaries`**。  
- **与 trade 分流**：默认 **不**附带下单诱导；用户明确要求交易 → [`../intents/trade.md`](../intents/trade.md) → [`../trading/README.md`](../trading/README.md)。  
- **失败 / UNKNOWN**：[`shared/common-phrases` §2](../shared/common-phrases.md)、[`Runtime/unknown-state`](../../Runtime/unknown-state.md)。

---

**文档版本**：1.4.1-mvp · **维护**：产品 + Prompt owner · **本版**：**§1 范围恢复 + §4 链 system §6.3**。**承** 1.4.0。
