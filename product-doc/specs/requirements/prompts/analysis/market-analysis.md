# Analysis · Market（条文）

**路径**：`specs/requirements/prompts/analysis/market-analysis.md`。  
**Publish SSOT**：[`prompt-management`](../../domains/admin/prompt-management/overview.md)。

**索引**：[`README`](./README.md)

> **Publish 正文**：统一 **`pp-analysis-core`**（[`governance-map.md` §4](../governance-map.md#4-读侧--监控--统一分析包)）。**本文**为 **行情类能力语义分卷**，**非**独立 `pp-analysis-market-*` 包。

---

## 1. 范围（本文）

- **公开侧市场数据叙事**：现货/合约 **标价与涨跌**、Funding、**盘口/深度摘要**、**公开指数或费率口径类事实** — **只读**。  
- **流程**：[`read-analyze-and-search-via-agent`](../../flows/read-analyze-and-search-via-agent.md)；**MI** → [`market-intelligence` §4](../../domains/agent/exchange-agent/market-intelligence.md)。  
- **Runtime Facts**：[`market-runtime-payload` §3](../../domains/agent/exchange-agent/market-runtime-payload.md) **`userVisibleMarketData`/`marketInsightData`**（**§3.3 `lastPrice`**）。

---

## 2. 与其它 analysis 分卷（示意）

| 主题 | **归本文** | **归其它稿** |
|------|------------|----------------|
| BTC 现价、Funding、盘口摘要 | ✓ | — |
| RSI/MACD/形态/支撑阻力 **教学法** | ✗ | [`technical-analysis.md`](./technical-analysis.md) |
| 社交媒体情绪、讨论热度 | ✗ | [`sentiment-summary.md`](./sentiment-summary.md) |
| 我的持仓/盈亏 | ✗ | [`portfolio-read.md`](./portfolio-read.md) |

---

## 3. 工具与事实（防幻觉）

- **声称具体数值来自交易所行情 API**：须在 **登记只读 skill** **成功闭环**后复述；否则 **标明推断/示意**或 **说明暂无法拉取** — [`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md)、[`hallucination`](../../observability/hallucination.md)。

---

## 4. 话术下限

- **非投顾**：[`system/system.md`](../system/system.md) **§1**。  
- **数据时效**：缓存/延迟视图 → 「仅供参考」类措辞（**不**编造延迟毫秒）。  
- **自然交易语言**：**优先** **Trader Narrative Anchors** — [`shared/common-phrases` §8/§8.7](../shared/common-phrases.md)；**Few-shot 登记示意** — [`narrative-few-shot-specimens.md`](./narrative-few-shot-specimens.md)；**有 **`marketPhase`/Facts** **时** **可** **润色盘感**；**无 Facts** **不得** **编造状态叙事 — **`FR-MI03`/`FR-MI05`**。  
- **与 trade 分流**：默认 **不**附带下单诱导；用户明确要求交易 → [`../intents/trade.md`](../intents/trade.md) → [`../trading/README.md`](../trading/README.md)。  
- **失败 / UNKNOWN**：[`shared/common-phrases` §2](../shared/common-phrases.md)、[`Runtime/unknown-state`](../../Runtime/unknown-state.md)。

---

**文档版本**：1.4.2-mvp · **维护**：产品 + Prompt owner · **本版**：**§1 范围补全 + Runtime Facts**。**承** 1.4.1。
