# Exchange Agent · 市场洞察（Market Intelligence）

**路径**：`specs/requirements/domains/agent/exchange-agent/market-intelligence.md`。

**职责**：**Market Intelligence** — **可读市场信息类型**、**用户价值**、**与 Portfolio/Trade 拼装时的边界**。**逐 `toolId` 登记宿主** **`trade-assistance`§8**；**编排路由键 **`scenarioId` **寄存器**：[`../agent-orchestration/routing-engine.md`](../agent-orchestration/routing-engine.md) **§1 读侧表**。**不写** `design/api.md` **PATH 逐项复述**。

---

## 1. 能力条目（产品下限）

| 子主题 | 用户价值 | **链出（宿主 / 键）** | 下限 / 门禁 |
|--------|----------|------------------------|-------------|
| **实时价量摘要** | 涨跌、24h、标记价 **等** | **行情读**：[`trade-assistance.md §8.3`](trade-assistance.md)（ticker）；编排键 **`market.read_quote`** | **矩阵未冻结** → **不承诺闭环** [`boundaries.md`](boundaries.md) |
| **深度与微观结构** | 盘口 **与** **公共成交** | **`§8.3`** orderbook/recent trades；键 **`market.read_microstructure`** | **私有成交** → **Portfolio** **`tool.orders.*`** **不可用** ticker **顶替** |
| **K 线 / 模型解读** | **指标 + 解读（Disclaimer）** | **`§8.3`** symbol deep dive；键 **`market.read_deep_analysis`** | **非投资建议** [`boundaries.md`](boundaries.md) |
| **资金费率 · 合约摘要** | Funding **摘要** | **`§8.3`** funding summary；键 **`futures.read_funding`** | **写** **分流** **`trade-via-agent`** |
| **波动 · 摘要 · RSS/宏观（可选）** | **简报** | **`§8.3`** RSS/日历 **行；** **`research.rss_or_macro`** | **外链** **须** **标明** **来源** **与** **`asOf`** |
| **社媒 · 新闻 · 搜索 · 翻译** | **外网叙事** | [`trade-assistance.md §8.4`](trade-assistance.md)、编排键 **`research.sentiment_and_news`** **等** → [`routing-engine` §1](../agent-orchestration/routing-engine.md) | **ADR-003** · **context 预算** |

---

## 2. FR / SC

| ID | 陈述 |
|----|------|
| **FR-MI01** | **`toolId`/PATH** **未** **在所内冻结** **前** → **不向用户承诺**可查 **或** **隐式升格为写**。 |
| **FR-MI02** | **从洞察升级到写** **须** **显式** **切入** **`trade-via-agent`** **专节** **并** **完成** **类型 A** **pipeline**。 |
| **FR-MI03** | **源故障 / SLO 超时** → **禁止** **静默** **捏造** **最新价/K 叙事** **；须** **`FR-T05`/Stale+`asOf`**。 |

| ID | **验收要点**（可对签） |
|----|-------------------------|
| **SC-MI01** | **未冻结 PATH**：**不出现** **假成功实时价** — **须有** **`FR-T05`/Stale**（**`FR-MI01`**）。 |
| **SC-MI02** | **读→写**：**跳转** **均** **重入** **类型 A**（**`FR-MI02`**）。 |
| **SC-MI03** | **504/超时注入**：**无** **编造**最新价 **；** **有** **`asOf`/不可用**声明（**`FR-MI03`**）。 |

---

## 3. 互引

| 文档 | 关系 |
|------|------|
| [`intents.md`](intents.md) | **市场类**语义 |
| [`portfolio-insight.md`](portfolio-insight.md) | **拼装** **边界** |
| [`trade-assistance.md`](trade-assistance.md) | **`toolId`§8** |
| [`../agent-orchestration/routing-engine.md`](../agent-orchestration/routing-engine.md) | **§1**：读侧 **`scenarioId`** |
| [`../../../flows/read-analyze-and-search-via-agent.md`](../../../flows/read-analyze-and-search-via-agent.md) | **读流程建议表** |
| [`market-runtime-payload.md`](market-runtime-payload.md) | **MNRA Facts SSOT** — 键名、phase 枚举、hints；**同窗** **`routing-engine` §1.1、[read-analyze](../../../flows/read-analyze-and-search-via-agent.md)** |
| [`market-narrative-runtime/README`](../../../market-narrative-runtime/README.md) | **MNRA 架构总入口** · [`scenario-matrix`](../../../market-narrative-runtime/scenario-matrix.md) |
| [`prompt-runtime/README`](../../../prompt-runtime/README.md) | **PRS** — 消费 MNRA Context 块 5 |

---

## 4. Market Narrative Runtime Architecture（MNRA · 产品能力层）

**架构总入口**：[`market-narrative-runtime/README.md`](../../../market-narrative-runtime/README.md) · per-`scenarioId` 矩阵 [`scenario-matrix.md`](../../../market-narrative-runtime/scenario-matrix.md) · **拼装消费** [`prompt-runtime/README.md`](../../../prompt-runtime/README.md)。

**定位**：解决 **「有 Prompt / Few-shot / common-phrases，仍 AI 味重」** — **缺的是 Market State → Trader Narrative 运行时映射**，**不是** 另立 **「Trader Phrase Library」** SSOT。**本篇 §4** 为 **FR/SC 宿主**；**管线与开放项** 以 **MNRA README** 为准。

**分层 SSOT（禁止分裂）**：

| 层 | SSOT | 职责 |
|----|------|------|
| **Market State** | [`market-runtime-payload` §3](market-runtime-payload.md) | **Facts**：价量、深度、**`marketPhase`** 等 **确定性字段** |
| **Narrative Anchors** | [`common-phrases` §8](../../../prompts/shared/common-phrases.md) | **原则级锚句** — **润色，非真值** |
| **Few-shot** | [`prompt-management`](../../admin/prompt-management/overview.md) **FR-PM05** | **口吻/节奏示例** |
| **Prompt Rules** | [`market-analysis`](../../../prompts/analysis/market-analysis.md)、[`fragment-intent-analysis`](../../../prompts/library/packs/fragment-intent-analysis.zh-CN.md) | **短规则**（**勿塞千句**） |
| **Runtime Hints（草案）** | [`market-runtime-payload` §3.4](market-runtime-payload.md) · [`market-runtime-schemas.yaml`](../../../../openapi/components/market-runtime-schemas.yaml) · [`design/market-narrative-runtime`](../../../../design/market-narrative-runtime.md) | **`marketNarrativeHints`** — **从 State 派生推荐锚句** |

**产品导向权重**（**非硬编码执法条**）：Market State ~40% · Narrative Anchors ~30% · Few-shot ~20% · Prompt Rules ~10% — **详** [`common-phrases` §8.1](../../../prompts/shared/common-phrases.md)。

**FR 下限（草案）**：

| ID | 陈述 |
|----|------|
| **FR-MI04** | **行情只读答复** **在** **有 **`marketPhase`/等价状态** **且** **工具 Facts 闭环** **时** **SHOULD** **优先** **自然交易语言**（**§8 锚句或 Runtime hints**）；**仍须** **复述关键数值** **且** **非投顾 Disclaimer**。 |
| **FR-MI05** | **无 Market State 或 stale** **时** **MUST NOT** **用叙事锚** **编造盘感** — **同窗** **`FR-MI03`**。 |
| **FR-MI06** | **`marketPhase`** **MUST** **由** **Runtime 确定性规则/analytics/工具回填** **产出** — **禁止** **主模型无源推断或自造未登记 phase**。 |
| **FR-MI07** | **`marketPhase` ∈ `funding_*`** **时** **MUST** **同窗存在** **`fundingRate`（或等价）Facts** **且** **用户可见答复须复述费率** — **锚句不得替代数值**。 |
| **FR-MI08** | **`marketNarrativeHints.recommendedNarratives`** **MUST** **≤3 条** **且** **须** **可追溯到** **§8.2 锚表**；**默认仅 **primaryMarketPhase** 之锚句**。 |

| ID | **验收要点** |
|----|-------------|
| **SC-MI04** | **Given** **`marketPhase=sideways`** **+ ticker 闭环** · **When** **用户问「盘面怎么样」** · **Then** **含** **可读状态描述** **且** **含价/量或 asOf**；**禁止** **纯客服套话无 Facts** |
| **SC-MI05** | **Given** **工具失败/stale** · **When** **问盘面** · **Then** **不得** **用 §8 锚句** **假装** **已知市场状态** |
| **SC-MI06** | **Given** **`futures.read_funding` 闭环** **+ **`funding_crowded_long`** · **When** **问资金费率** · **Then** **含费率数值 + §8.2.5 锚意向**；**禁止** **仅锚句无率** |
| **SC-MI07** | **Given** **`elevated_volatility` + volatility 字段** · **When** **问「最近波动大吗」** · **Then** **锚句与 volatility Facts 同窗** |
| **SC-MI08** | **Given** **观测/Prompt 宿主** · **When** **注入 hints** · **Then** **`marketPhase` ∈ §3.2.1**；**无登记 phase 字面**；**recommendedNarratives ≤3** |

**Eval（登记宿主）** — [`evals/scenarios.md`](../../../evals/scenarios.md)：

| `evalSetId` | 映射 |
|-------------|------|
| **`eval.market.narrative_with_facts`** | **SC-MI04** |
| **`eval.market.narrative_stale_no_phase`** | **SC-MI05** |
| **`eval.market.narrative_funding`** | **SC-MI06** |
| **`eval.market.narrative_high_volatility`** | **SC-MI07** |
| **`eval.market.phase_deterministic`** | **SC-MI08**、**FR-MI06** |
| **`eval.market.narrative_obs`** | **SC-OBS09** |

**GWT 构造专卷** → [`evals/market-narrative.md`](../../../evals/market-narrative.md) · **Walkthrough** [`e2e-closed-loop#runtime-walkthrough-crosscut`](../../../../flow/e2e-closed-loop.md#runtime-walkthrough-crosscut) **Goal-MKT**。

### 4.1 `marketPhase` 派生原则（Runtime · 需求下限）

**职责**：**把 Facts 映射为 §3.2.1 枚举** — **数值阈值** **`design`/analytics MR**；**本节** **只** **冻结原则**。

1. **只读链路**：**Ticker-only**（**`market.read_quote`**）**默认** **不产出** **深度/突破/Funding phase** — **除非** **另有工具回填**。  
2. **深度/analytics**：**`market.read_deep_analysis`** **方可** **产出** **结构/动能/波动/事件** phase。  
3. **Funding**：**仅 **`futures.read_funding`**（或矩阵等价）**闭环后** **方可** **`funding_*`**。  
4. **微观**：**`market.read_microstructure`** **或** **orderbook 工具** **闭环后** **方可** **`wide_spread`/`thin_book`/`stable_liquidity`**。  
5. **Stale**：**Facts **`asOf`** **超阈** → **不得** **注入 phase/hints**（**`FR-MI05`**）。

**观测建议**：**`agent.market.phase_computed`** **携带** **`primaryMarketPhase`、`factSources[]`、`sessionId`、`executionId`**。

### 4.2 Prompt / Few-shot 分工（同窗）

- **Prompt 规则**：**短** — **见** [`market-analysis`](../../../prompts/analysis/market-analysis.md)、[`fragment-intent-analysis`](../../../prompts/library/packs/fragment-intent-analysis.zh-CN.md)。  
- **Few-shot**：**§8.6** **登记下限** — **Git 镜像** [`fewshot-narrative-analysis`](../../../prompts/library/packs/fewshot-narrative-analysis.zh-CN.md)（**须 Publish 才生效**；**评审索引** [`narrative-few-shot-specimens.md`](../../../prompts/analysis/narrative-few-shot-specimens.md)）。  
- **禁止**：**`TRADER_PHRASE` pack**、**Phrase Library 独立卷**。

**禁止**：**`promptPackKind=TRADER_PHRASE`**、**独立 Trader Phrase Library 卷** — **Phrase ≠ Prompt**；**超长对白库** **违背** [`library/ASSEMBLY` §3](../../../prompts/library/ASSEMBLY.md)。

---

**文档版本**：0.7.0 · **维护**：产品 + Agent Runtime owner · **本版**：**§4 升格 MNRA · 链总入口**。**承** 0.6.0。
