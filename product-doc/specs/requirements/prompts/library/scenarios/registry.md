# Scenario Registry · `scenarioId` → 拼装配方

**路径**：`specs/requirements/prompts/library/scenarios/registry.md`。  
**键 SSOT**：[`routing-engine` §1～§4](../../../domains/agent/agent-orchestration/routing-engine.md)。  
**PRS 总入口**：[`prompt-runtime/README`](../../../prompt-runtime/README.md)。**读侧行情 MNRA**：[`market-narrative-runtime/README`](../../../market-narrative-runtime/README.md) · [`scenario-matrix`](../../../market-narrative-runtime/scenario-matrix.md)。

**图例**（[`ASSEMBLY.md`](../ASSEMBLY.md)）：

- **C** = [`core-runtime-root`](../packs/core-runtime-root.zh-CN.md)（**`en` 桶** → [`.en`](../packs/core-runtime-root.en.md)）  
- **E** = [`fragment-errors-user-visible`](../packs/fragment-errors-user-visible.zh-CN.md)（**`en` 桶** → [`.en`](../packs/fragment-errors-user-visible.en.md)）  
- **S** = [`fragment-safety`](../packs/fragment-safety.zh-CN.md)（**`en`** → [`.en`](../packs/fragment-safety.en.md)）  
- **IT** = [`fragment-intent-trade`](../packs/fragment-intent-trade.zh-CN.md)（**`en`** → [`.en`](../packs/fragment-intent-trade.en.md)）  
- **IA** = [`fragment-intent-analysis`](../packs/fragment-intent-analysis.zh-CN.md)（**`en`** → [`.en`](../packs/fragment-intent-analysis.en.md)）  
- **IM** = [`fragment-intent-monitoring`](../packs/fragment-intent-monitoring.zh-CN.md)（**`en`** → [`.en`](../packs/fragment-intent-monitoring.en.md)）  
- **A** = [`fragment-confirmation-type-a`](../packs/fragment-confirmation-type-a.zh-CN.md)（**`en`** → [`.en`](../packs/fragment-confirmation-type-a.en.md)）

**说明**：**E** **专职**「工具失败 / **上游错误** / **平台报错** → **`effective_locale` 用户可见句」」四类分型与禁令 — **简中** [`packs/fragment-errors-user-visible.zh-CN.md`](../packs/fragment-errors-user-visible.zh-CN.md) / **英文桶** [`packs/fragment-errors-user-visible.en.md`](../packs/fragment-errors-user-visible.en.md) **≥ library-0.2.3**（**Telegram 为用户问题解决唯一面**，**`requires_main_site`** **窄口子**）。

**延展条文**：运行时可选注入摘要；权威条文仍在 **`prompts/trading/*`、`prompts/analysis/*`** 等。  
**运营发布包映射 SSOT**：[`governance-map.md`](../../governance-map.md)。

---

## 0. 运营发布包与 Git 条文

| 主题 | 文档 |
|------|------|
| **`scenarioId` ↔ `promptPackId` 全表** | [`governance-map.md`](../../governance-map.md) |
| **16 包清单（产品侧）** | [`product/prompt-governance-checklist.md`](../../../../product/prompt-governance-checklist.md) |
| **全局 SYSTEM / SAFETY / 横切** | [`governance-map.md` §2](../../governance-map.md#2-全局与横切块非-scenarioid-独占) |

下文 **§1～§4** 在拼装表增加 **`promptPackId`** 列；**读侧/监控** 均为 **`pp-analysis-core`**（不按主题拆包）。

---

## 1. 读侧与分析（§1）

| `scenarioId` | `promptPackId` | 拼装（建议） | 延展条文（索引） |
|----------------|----------------|--------------|------------------|
| `market.read_quote` | `pp-analysis-core` | C + S + IA + E* | [`market-analysis.md`](../../analysis/market-analysis.md) |
| `market.read_microstructure` | `pp-analysis-core` | C + S + IA + E* | 同上 |
| `market.read_deep_analysis` | `pp-analysis-core` | C + S + IA + E* | [`technical-analysis.md`](../../analysis/technical-analysis.md) |
| `futures.read_funding` | `pp-analysis-core` | C + S + IA + E* | [`market-analysis.md`](../../analysis/market-analysis.md)、[`futures.md`](../../trading/futures.md)（只读叙事） |
| `research.rss_or_macro` | `pp-analysis-core` | C + S + IA + E* | [`sentiment-summary.md`](../../analysis/sentiment-summary.md) |
| `research.sentiment_and_news` | `pp-analysis-core` | C + S + IA + E* | [`sentiment-summary.md`](../../analysis/sentiment-summary.md) |
| `orders.read_activity` | `pp-analysis-core` | C + S + IA + E* | [`portfolio-read.md`](../../analysis/portfolio-read.md)、[`cancel.md`](../../trading/cancel.md)（只读上下文） |
| `portfolio.read_pnl_exposure` | `pp-analysis-core` | C + S + IA + E* | [`portfolio-read.md`](../../analysis/portfolio-read.md) |

\* **E** 在纯读回合可省略；若同会话曾出错或调用外网工具失败 **建议保留**。

### §1.2 读侧 · Runtime Context 块 5（拼装器 · 示意）

**MNRA 全表** → [`market-narrative-runtime/scenario-matrix`](../../../market-narrative-runtime/scenario-matrix.md)。

**OpenAPI SSOT**：[`market-runtime-schemas.yaml`](../../../../openapi/components/market-runtime-schemas.yaml)、[`memory-runtime-schemas.yaml`](../../../../openapi/components/memory-runtime-schemas.yaml)。**注入序** → [`memory-runtime` §5](../../../Runtime/memory-runtime.md)、[`runtime-injection` §2.4.1](../../../domains/admin/prompt-management/runtime-injection.md)。

| **`scenarioId`** | **典型 Facts 宿主** | **叙事 / 记忆（可选）** | **抽检 Eval** |
|------------------|---------------------|-------------------------|---------------|
| **`market.read_quote`** | **`userVisibleMarketData`**（**§3.3 `lastPrice`**） | **Ticker-only** **默认无** **Funding/深度 phase**；**可选 **`marketNarrativeHints`** | **`eval.market.ticker_facts_mapping`**、[`market-narrative` §3](../../../evals/market-narrative.md) |
| **`market.read_microstructure`** | **同上** + 盘口/成交 Facts | **可 **`wide_spread`/`thin_book`/`stable_liquidity`** phase** | **同上** + **微观 Eval（staging）** |
| **`market.read_deep_analysis`** | **`marketInsightData`**（**含可选 **`marketPhase`**） | **结构/动能/波动 phase**；**hints ≤3** | **`eval.market.narrative_*`** |
| **`futures.read_funding`** | **`marketInsightData.fundingRate`** **等** | **Funding phase 须带费率数值**（**`FR-MI07`**） | **`eval.market.narrative_funding`** |
| **`research.*`** | **C 类工具结果**（**非** ticker 顶替） | **情绪锚句须与来源 Facts 同窗** | **ADR-003 / 外网 Eval（所内）** |
| **`orders.read_activity`** / **`portfolio.read_pnl_exposure`** | **私有读工具快照** | **须 **`FR-T02`**；**Semantic 不得写余额/持仓** | **`eval.read.market_portfolio_no_write`** |
| **（全读侧 · 横切）** | **②④ 工具 Facts 优先于 narrative** | **LTM 默认 OFF** — **`semanticNarrativeBlock`** **见** **`FEATURE_SEMANTIC_NARRATIVE`** | [`memory-runtime` §6](../../../evals/memory-runtime.md)、[`e2e#crosscut`](../../../../flow/e2e-closed-loop.md#runtime-walkthrough-crosscut) |

**Few-shot（ANALYSIS 包 · 非 SYSTEM）**：Git 镜像 → [`fewshot-narrative-analysis.zh-CN.md`](../packs/fewshot-narrative-analysis.zh-CN.md)（**`en`** → [`.en`](../packs/fewshot-narrative-analysis.en.md)）· **须 Publish** · 评审索引 [`narrative-few-shot-specimens.md`](../../analysis/narrative-few-shot-specimens.md)。

---

## 2. 现货与衍生品写路径（§2）

**`skill_spec` 列** → [`skill-specs/README`](../../../skill-specs/README.md) §3。

**拼装 · E 片段**：**写路径** 表内 **`C + E + …`** **为默认**（同窗 [`ASSEMBLY.md`](../ASSEMBLY.md) L2 — **IT/IM + 写** **建议始终带 E**）。**读路径** §1 之 **E\*** **可省略**；**同会话曾工具失败** **建议保留**。

**OCO / bracket（§非目标）**：下表 **`IT + A`** **仅** 表 **Publish 配方占位**；**运行时 MUST** 在 **类型 A 之前** **`FR-T05` 拒答** — **禁止** 默认走完整写闭环（[`product.md`](../../../product.md) **§非目标**）。

| `scenarioId` | `promptPackId` | 拼装（须） | `skill_spec` | 延展条文 |
|----------------|----------------|------------|--------------|----------|
| `trade.spot.flash_convert` | `pp-trading-spot-flash` | C + E + S + IT + A | [`skill.spot.flash_convert`](../../../skill-specs/spot/skill.spot.flash_convert.md) | [`buy.md`](../../trading/buy.md)、[`sell.md`](../../trading/sell.md) |
| `trade.spot.limit_order` | `pp-trading-spot-limit` | C + E + S + IT + A | [**`skill.spot.limit_order`**](../../../skill-specs/spot/skill.spot.limit_order.md) | [`buy.md`](../../trading/buy.md) |
| `trade.spot.amend_limit_order` | `pp-trading-spot-amend` | C + E + S + IT + A | [`skill.spot.amend_limit_order`](../../../skill-specs/spot/skill.spot.amend_limit_order.md) | [`buy.md`](../../trading/buy.md)、[`cancel.md`](../../trading/cancel.md) |
| `trade.spot.oco` | **—** | C + E + S + IT + A（**占位 · 禁默认写闭环**） | **不交付** · `FR-T05` | [`buy.md`](../../trading/buy.md)；[`product.md`](../../../product.md) **§非目标** |
| `trade.spot.bracket` | **—** | C + E + S + IT + A（**占位 · 禁默认写闭环**） | **不交付** · `FR-T05` | 同上 · **§非目标** |
| `trade.futures.market_order` | `pp-trading-futures-market` | C + E + S + IT + A | [`skill.futures.market_order`](../../../skill-specs/futures/skill.futures.market_order.md) | [`futures.md`](../../trading/futures.md) |
| `trade.futures.limit_order` | `pp-trading-futures-limit` | C + E + S + IT + A | [`skill.futures.limit_order`](../../../skill-specs/futures/skill.futures.limit_order.md) | [`futures.md`](../../trading/futures.md) |
| `trade.futures.amend_limit_order` | `pp-trading-futures-amend` | C + E + S + IT + A | [`skill.futures.amend_limit_order`](../../../skill-specs/futures/skill.futures.amend_limit_order.md) | [`futures.md`](../../trading/futures.md)、[`cancel.md`](../../trading/cancel.md) |
| `trade.futures.take_profit_stop` / `futures.condition.order_create` | `pp-trading-futures-tpsl` | C + E + S + IT + A | [`skill.futures.take_profit_stop`](../../../skill-specs/futures/skill.futures.take_profit_stop.md) · **contract-complete** | [`futures.md`](../../trading/futures.md) |
| `margin.cross.market_order` | `pp-trading-margin-market` | C + E + S + IT + A | [`skill.margin.cross_market_order`](../../../skill-specs/margin/skill.margin.cross_market_order.md) | [`buy.md`](../../trading/buy.md)、[`futures.md`](../../trading/futures.md)、[`risk-disclosure`](../../confirmation/risk-disclosure.md) |
| `margin.cross.limit_order` | `pp-trading-margin-limit` | C + E + S + IT + A | [`skill.margin.cross_limit_order`](../../../skill-specs/margin/skill.margin.cross_limit_order.md) | 同上 |
| `margin.cross.transfer_in`（示意） | **—** | C + E + S + IT + A | 主站 · 无 Agent 写规范 | [`buy.md`](../../trading/buy.md)、[`boundaries`](../../../domains/agent/exchange-agent/boundaries.md) |

---

## 3. 理财（§3）

| `scenarioId` | `promptPackId` | 拼装 | `skill_spec` | 延展条文 |
|----------------|----------------|------|--------------|----------|
| `wealth.holdings_read` | `pp-analysis-core` | C + S + IA + E* | —（只读） | [`portfolio-read.md`](../../analysis/portfolio-read.md)、[`wealth-via-agent`](../../../flows/wealth-via-agent.md) |
| `wealth.recommend` | `pp-analysis-core` | C + S + IA + E* | —（只读） | 同上 |
| `wealth.subscribe` | `pp-trading-wealth-subscribe` | C + E + S + IT + A | [`skill.wealth.subscribe`](../../../skill-specs/wealth/skill.wealth.subscribe.md) | [`wealth-via-agent`](../../../flows/wealth-via-agent.md)、[`high-risk-confirmation`](../../confirmation/high-risk-confirmation.md) |
| `wealth.redeem` | `pp-trading-wealth-redeem` | C + E + S + IT + A | [`skill.wealth.redeem`](../../../skill-specs/wealth/skill.wealth.redeem.md) | 同上 |

---

## 4. 监控与自动化（§4）

| `scenarioId` | `promptPackId` | 拼装 | 延展条文 |
|----------------|----------------|------|----------|
| `monitoring.price_condition` | `pp-analysis-core` | C + S + IM + E | [`monitoring.md`](../../intents/monitoring.md) |
| `monitoring.scheduled_pull` | `pp-analysis-core` | C + S + IM + E | 同上 |
| `monitoring.event_trigger` | `pp-analysis-core` | C + S + IM + E | 同上 |

---

## 5. i18n · 英文桶（`effective_locale` = **en**）

**拼装字母与上表一致**（C + E + S + …）；仅 **按语种换文件后缀**：

| 字母 | 英文桶选用 |
|------|------------|
| **C** | [`core-runtime-root.en.md`](../packs/core-runtime-root.en.md) |
| **E** | [`fragment-errors-user-visible.en.md`](../packs/fragment-errors-user-visible.en.md) |
| **S** | [`fragment-safety.en.md`](../packs/fragment-safety.en.md) |
| **IT** | [`fragment-intent-trade.en.md`](../packs/fragment-intent-trade.en.md) |
| **IA** | [`fragment-intent-analysis.en.md`](../packs/fragment-intent-analysis.en.md) |
| **IM** | [`fragment-intent-monitoring.en.md`](../packs/fragment-intent-monitoring.en.md) |
| **A** | [`fragment-confirmation-type-a.en.md`](../packs/fragment-confirmation-type-a.en.md) |

**简中 / 繁中**：**C** + 上表各 **`*.zh-CN.md`**；**繁中** 可在发布管线微调用词，Git **仍以 zh-CN 文件为基底**。

**键对签**：**每增删** **`scenarioId`** — [`routing-engine` §1～§4](../../../domains/agent/agent-orchestration/routing-engine.md) **与本表同窗**。**MR 前自检**（自仓库根目录，**均须** exit=0）：[`check_registry_vs_routing_engine.py`](../scripts/check_registry_vs_routing_engine.py)、[`check_governance_map_vs_registry.py`](../scripts/check_governance_map_vs_registry.py)。

---

**文档版本**：1.3.0 · **维护**：产品 + Prompt owner · **本版**：**§0 治理映射 · 全表 `promptPackId` 列 · 对齐 16 运营包**。**承** 1.2.1。
