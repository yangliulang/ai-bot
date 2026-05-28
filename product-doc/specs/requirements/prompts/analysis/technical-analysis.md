# Analysis · Technical（条文）

**路径**：`specs/requirements/prompts/analysis/technical-analysis.md`。  
**Publish SSOT**：[`prompt-management`](../../domains/admin/prompt-management/overview.md)。

**索引**：[`README`](./README.md)

> **Publish 正文**：统一 **`pp-analysis-core`**。**本文**为 **技术分析能力语义分卷**，**非**独立发布包。

---

## 1. 范围（本文）

- **指标解读**（RSI/MACD 等）、**K 线形态 / 趋势 / 支撑阻力** — **教育性、描述性**，**非**确定性预测。

---

## 2. 与其它 analysis 分卷（示意）

| 用户像在问 | **归本文** | **不归本文** |
|-------------|------------|---------------|
| 这根 K 像什么形态、均线怎么用 | ✓ | 纯「ETH 现在多少钱」→ [`market-analysis.md`](./market-analysis.md) |
| 论坛看多还是恐慌 | ✗ | [`sentiment-summary.md`](./sentiment-summary.md) |
| 我被套了多少 | ✗ | [`portfolio-read.md`](./portfolio-read.md) |

---

## 3. 域同窗（流程 / 工具）

- **流程**：[`read-analyze-and-search-via-agent`](../../flows/read-analyze-and-search-via-agent.md)（**含** **S4.1 phase 可选**）。  
- **能力宿主 / MI**：[`market-intelligence`](../../domains/agent/exchange-agent/market-intelligence.md) **§4**。  
- **Runtime Facts**：[`market-runtime-payload`](../../domains/agent/exchange-agent/market-runtime-payload.md) **`marketInsightData`**（**含 **`marketPhase`** **若 analytics 闭环**）。  
- **只读 skill**：[`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md)。

---

## 4. 工具与事实（防幻觉）

- **声称「刚拉了某周期 K 线/OHLC 精确值」**：须有 **登记只读工具成功闭环**；否则 **注明口径假设或未拉取** — [`hallucination`](../../observability/hallucination.md)。

---

## 5. 话术下限

- **自然交易语言**：**优先** **Trader Narrative Anchors** — [`shared/common-phrases` §8/§8.7](../shared/common-phrases.md)；**指标/形态描述** **可** **用 §8.2.1/8.2.3** **润色** **须** **有 K 线/指标/`marketInsightData` Facts**；**无 Facts/stale** **不得** **编造盘感 — **`FR-MI05`**。
- **禁止**：「必涨/必跌、保证止盈」— [`system/system.md`](../system/system.md) **§4**。  
- **参数歧义**（周期、复权、合约 vs 现货）须 **澄清或注明假设**。  
- **非投顾**：同窗 **§1**。  
- **与 trade 分流**：默认 **不**附带下单诱导；用户明确要求交易 → [`../intents/trade.md`](../intents/trade.md) → [`../trading/README.md`](../trading/README.md)。  
- **失败 / UNKNOWN**：[`shared/common-phrases` §2](../shared/common-phrases.md)、[`Runtime/unknown-state`](../../Runtime/unknown-state.md)。

---

**文档版本**：1.4.1-mvp · **维护**：产品 + Prompt owner · **本版**：**§3/§5 链 market-runtime + FR-MI05**。**承** 1.4.0。
