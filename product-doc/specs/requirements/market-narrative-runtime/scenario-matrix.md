# MNRA · `scenarioId` 配置矩阵

**路径**：`specs/requirements/market-narrative-runtime/scenario-matrix.md`。

**键 SSOT**：[`routing-engine` §1](../domains/agent/agent-orchestration/routing-engine.md)。**PRS 拼装字母** → [`registry` §1～§4](../prompts/library/scenarios/registry.md)。**架构总览** → [`README`](./README.md)。

**图例**：**PRS** = C / E / S / IA / IT 等（见 [`ASSEMBLY`](../prompts/library/ASSEMBLY.md)）；**Facts** = Runtime Context 块 5 宿主键。

---

## 1. 行情读侧（§1）

| `scenarioId` | 典型工具（§8 矩阵为准） | Facts 宿主 | Phase 派生（§4.1） | Hints | PRS 拼装 | PRS 延展条文 | Eval |
|--------------|-------------------------|------------|-------------------|-------|----------|--------------|------|
| `market.read_quote` | `tool.market.ticker` 等 | `userVisibleMarketData` | **Ticker-only** · 默认无深度/Funding phase | 可选 · primary only | C + S + IA + E* | [`market-analysis`](../prompts/analysis/market-analysis.md) | `eval.market.ticker_facts_mapping` · `eval.market.narrative_*` |
| `market.read_microstructure` | orderbook / trades | UVD + `marketInsightData` 微观段 | `wide_spread` / `thin_book` / `stable_liquidity` | ≤3 · §8.2 | C + S + IA + E* | 同上 | 微观 Eval（staging） |
| `market.read_deep_analysis` | ticker + analytics / K 线 | `marketInsightData` | 结构/动能/波动/事件 phase | ≤3 | C + S + IA + E* | [`technical-analysis`](../prompts/analysis/technical-analysis.md) | `eval.market.narrative_*` |
| `futures.read_funding` | `tool.futures.funding_summary` 等 | `marketInsightData.fundingRate` 等 | **`funding_*` only** · 须数值 | ≤3 · §8.2.5 | C + S + IA + E* | [`market-analysis`](../prompts/analysis/market-analysis.md)、[`futures`](../prompts/trading/futures.md) 只读 | `eval.market.narrative_funding` |

\* **E**：纯读可省略；**建议** 工具失败会话保留 — 与 [`registry` §1](../prompts/library/scenarios/registry.md) 及 [`ASSEMBLY` L2](../prompts/library/ASSEMBLY.md) 产品决选 **同窗**。

---

## 2. 研究读侧（§1 续）

| `scenarioId` | Facts 宿主 | Phase / Hints | PRS | 延展条文 | 备注 |
|--------------|------------|---------------|-----|----------|------|
| `research.rss_or_macro` | C 类工具结果 | 情绪锚须与来源 Facts 同窗 | C + S + IA + E* | [`sentiment-summary`](../prompts/analysis/sentiment-summary.md) | 外链 asOf |
| `research.sentiment_and_news` | 同上 | 同上 | C + S + IA + E* | 同上 | ADR-003 · 预算 |

---

## 3. 私读（非 MNRA 主引擎）

| `scenarioId` | Facts | MNRA | PRS | 延展 | Eval |
|--------------|-------|------|-----|------|------|
| `orders.read_activity` | 私有读快照 | **不** 用 ticker 顶替 | C + S + IA + E* | [`portfolio-read`](../prompts/analysis/portfolio-read.md) | `eval.read.market_portfolio_no_write` |
| `portfolio.read_pnl_exposure` | 同上 | Semantic **不得** 写余额 | C + S + IA + E* | 同上 | 同上 |

---

## 4. 横切（全读侧）

| 规则 | 说明 |
|------|------|
| **Facts 优先于 narrative** | ②④ 工具回填优先；**无 Facts 不得 phase/hints**（FR-MI05） |
| **LTM / 记忆叙事** | `semanticNarrativeBlock` · **默认 OFF** — [`memory-runtime` §6](../Runtime/memory-runtime.md) |
| **观测** | `agent.market.phase_computed` — [`design/market-narrative-runtime` §4](../../design/market-narrative-runtime.md) |
| **Few-shot** | ANALYSIS 包 · [`fewshot-narrative-analysis`](../prompts/library/packs/fewshot-narrative-analysis.zh-CN.md) · **须 Publish** |

---

**文档版本**：1.0.0 · **维护**：产品 + Agent Runtime owner · **本版**：**初版矩阵 · 对齐 registry §1.2**。
