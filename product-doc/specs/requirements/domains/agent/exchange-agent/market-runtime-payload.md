# Exchange Agent · 行情运行时快照与用户可见对齐（Market Runtime Payload）

**路径**：`specs/requirements/domains/agent/exchange-agent/market-runtime-payload.md`。

**职责**：把编排寄存器 **`scenarioId`**（[`routing-engine` §1](../agent-orchestration/routing-engine.md)）、读流程（[`read-analyze-and-search-via-agent`](../../../flows/read-analyze-and-search-via-agent.md)）、Prompt **FACT SOURCE**（`RUNTIME_CONTEXT_JSON` …）与 **Telegram 对客下限** 收口为可对齐叙述。**MNRA · Facts 层 SSOT** — 架构总览 [`market-narrative-runtime/README`](../../../market-narrative-runtime/README.md)。**不替代** [`design/api`](../../../../design/api.md) 字段真源、[`trade-assistance`](trade-assistance.md) **`toolId` §8** 矩阵。OpenAPI / `agentContext` / `executionEnvelope` 中与下述键等价或超集之形状仍**以所内契约为 SSOT**，本文列为产品与 Prompt 同窗下限。

**互引**：[`market-intelligence.md`](market-intelligence.md) **§4**；[`market-narrative-runtime/scenario-matrix`](../../../market-narrative-runtime/scenario-matrix.md)；[`telegram/overview`](../telegram/overview.md)；[`prompt-runtime/README`](../../../prompt-runtime/README.md)；[`prompt-management/runtime-injection`](../../admin/prompt-management/runtime-injection.md) **§2.4**；[`prompts/shared/response-format`](../../../prompts/shared/response-format.md)。

---

## 1. 编排键：canonical SSOT 与实现别名

| **canonical `scenarioId`**（`routing-engine` §1） | 典型能力与 Prompt 档位 |
|--------------------------------|------------------------|
| **`market.read_quote`** | **轻量**：公开 ticker / 价量摘要；Facts → 仅限 **§3.1 · `userVisibleMarketData`**。 |
| **`market.read_deep_analysis`** | **深度**：K 线 / 多维行情 + NL 解读（Disclaimer）；Facts → 准许 **`marketInsightData`** 子集（须有矩阵与工具回填）。**不得**仅凭 ticker 冒充深度解读。非投资建议 [`boundaries.md`](boundaries.md)。 |
| **`market.read_microstructure`** | 盘口 / 公共成交叙事；Facts 宿主可挂靠 **`marketInsightData`** 之微观结构分段（所内契约命名可不同）；条目见 [`market-intelligence.md`](market-intelligence.md)。 |

**实现别名（倒置域段示例 · MUST 归一）**：若 Runtime / 日志沿用 **`read.market.ticker`** 等键名 — **不得在** Telegram **用户气泡展示**该类字面 **`scenarioId`**；**观测归因**里 **`scenarioId` 须写入 canonical**，可选用 **`implementationScenarioAlias`**（所内信封键）保留原值。**映射下限**：

| 实现别名（示例） | **canonical** |
|------------------|----------------|
| **`read.market.ticker`**（或等价） | **`market.read_quote`** |
| 其它 **`read.market.*`** 若语义为 K 线 / 多维简报 | **`market.read_deep_analysis`**（以路由 MR 冻结为准） |

**禁止**：为别名再向 **`routing-engine` §1** 主表追加独立行作为第二 SSOT — 须上文映射或所内别名表 MR 同窗本节。**[`prompts/library/scenarios/registry`](../../../prompts/library/scenarios/registry.md)** 仍只登记 **`market.read_*`**。

---

## 2. 用户可见通道：MUST / MUST NOT

**MUST**：

- `sendMessage` / `edit` 等对用户正文以**自然语言简报**为主；数值须可追溯至 §3 或等价 OpenAPI 回填，遵守 **`FR-MI03`** — 无数据则不编（[`market-intelligence.md`](market-intelligence.md)）。
- **canonical `scenarioId`**、`operationId`、`GET /…/ PATH`：仅用于观测 / 日志（B 面）。

**MUST NOT**（与 [`telegram/overview`](../telegram/overview.md)、[`response-format`](../../../prompts/shared/response-format.md) 同窗）：

- 用户正文出现 **REST PATH**、裸 **HTTP 方法**、完整 URL、openapi host 详情、内部 **`scenarioId` / `read.market.*` 字面**、`RUNTIME_*` / Prompt / JSON Schema 整段倾泻。
- 以「调试模版」整块顶替可读摘要 — **Deterministic Formatter** 若仍存在，须有「无 PATH 的人话模版」支路或走 LLM（Facts 仍须 §3 白名单）。

**托管 / 绑定**：若产品须陈述 — 用人话单独一句；**勿**把「免 Key / 公开 GET」等技术说明当作主文案。

---

## 3. Runtime Context 键下限：`userVisibleMarketData` vs `marketInsightData`

以下键名为 Prompt 宿主常用 **camelCase 下限**；字段是否出现以 **`trade-assistance` §8** 工具成功回填与 **`design/api`** 冻结为准。**未出现时** Facts Prompt **不得虚构**。

### 3.1 `userVisibleMarketData`（轻量 · 典型绑定 `market.read_quote`）

| 字段（可选 · 按需存在） | 说明 |
|-------------------------|------|
| `symbol` | 交易对（与交易所一致） |
| `lastPrice` | 最新成交或等价 mid（若矩阵提供） |
| `bestBid` / `bestAsk` | 买一 / 卖一（`design` 可等价映射字段名） |
| `change24hPct`、`high24h`、`low24h`、`volume24h` | 仅当快照有 |
| `timestamp` / `asOf` | 时间锚；Stale 见 **`FR-MI03`** |

### 3.2 `marketInsightData`（深度 · 典型绑定 `market.read_deep_analysis` / 编排聚合）

须有 **`market.read_deep_analysis`**（或等价 MR 登记能力）与矩阵回填。子字段**全部为可选**：

| 分组 | 字段示例（工程可改 snake_case 对齐 OpenAPI） |
|------|---------------------------------------------|
| OHLC 序列 | `candles1m`、`candles5m`、`candles1h` 或统一 `candlesByInterval` |
| 成交量 | `volumeSeries`、`avgVolume`、`volumeSpike` |
| 特征 / 摘要 | `trend`、`volatility`、`intradaySummary`、`marketPhase` — **仅允许**后端确定性算出或由 **`tool.analytics.*`** 回填；Prompt **禁止无源推断**。**`support`、`resistance` 同上** |
| 事件 | `unusualMove`、`breakoutEvent` … |
| **Funding（合约）** | `fundingRate`、`fundingRateAnnualized`、`nextFundingTime` — **典型绑定 **`futures.read_funding`** / **`tool.futures.funding_summary`**；**`marketPhase` 为 **`funding_*`** 时 **须** **同窗存在** |

#### 3.2.1 `marketPhase` 登记枚举（SSOT · v0）

**用途**：**Market Narrative System** 之 **状态键** — **锚句映射** [`common-phrases` §8.2](../../../prompts/shared/common-phrases.md)；**禁止** **模型无源自造 phase**（**`FR-MI06`**）。

**命名**：**snake_case**；**增删** **须** **MR** **同窗** **本节 + §8.2 + Eval**。

| **族** | **`marketPhase` 值** | **典型事实源（下限）** | **备注** |
|--------|----------------------|------------------------|----------|
| **结构** | `sideways` | `marketInsightData.trend` **或** analytics 规则 | 震荡/区间 |
| | `trending_up` | 同上 + 价量方向一致 | **非** 投顾 |
| | `trending_down` | 同上 | **非** 投顾 |
| **量能** | `low_volume` | `volumeSeries`/`avgVolume`/`volume24h` | 相对均量偏低 |
| | `volume_spike` | `volumeSpike` **或** 规则算出 | 须 **asOf** |
| | `stable_liquidity` | orderbook 深度/价差规则 | 微观结构 |
| **动能** | `weak_momentum` | `trend`/动量指标 **确定性** | |
| | `strong_momentum` | 同上 | Disclaimer |
| **波动** | `elevated_volatility` | `volatility` **或** analytics | |
| | `volatility_compression` | 波动率收缩规则 | 「挤压」叙事 **须** **有依据** |
| **微观** | `wide_spread` | `bestBid`/`bestAsk` 价差规则 | 常与 `low_volume` 并存 |
| | `thin_book` | 深度档位不足规则 | |
| **事件** | `breakout` | `breakoutEvent` **或** 规则 | **须** **带 asOf** |
| | `breakdown` | 同上 | |
| | `unusual_move` | `unusualMove` | |
| **Funding** | `funding_crowded_long` | **`fundingRate`** 超阈（**`design`/ADR**） | **须** **复述费率数值** |
| | `funding_crowded_short` | 同上（负向） | 同上 |
| | `funding_neutral` | **`fundingRate`** 近零 | |

**复合 phase**：**Runtime** **宜** **输出 **`primaryMarketPhase`** + **可选 **`secondaryMarketPhases[]`（≤2）** — **同窗** [`common-phrases` §8.5](../../../prompts/shared/common-phrases.md)；**`marketNarrativeHints`** **默认只带 **primary** 之锚句**（**`FR-MI08`**）。

**阈值数值**：**不在 requirements 冻结** — **[`design`/ADR](../../../../design/architecture.md) **或** **analytics MR**；**须** **可观测 **`marketPhaseSource=rules|tool`**（键名 **`design` 终裁**）。

**对齐规则**：任一叙事 Prompt 声明「仅依据 **`marketInsightData`**」— **Runtime MUST**：

1. 本 **`execution`** 路由到 **canonical**：**`market.read_deep_analysis`**（或同窗登记键）。  
2. 注入 JSON 须裁剪：**不得**混入 §2 MUST NOT 类键（REST PATH、`rawExchangeResponse` 等），除非 **`design`** 对白名单放行。

**缺数据**：短文降级，说明「当前快照不支持该解读」，勿用 ticker 充数。**禁止**：仅 **`market.read_quote`** 却挂载「深度解读」类 System 且无 **`marketInsightData`** 事实 — **须**分拆 Prompt Pack。

### 3.3 `tool.market.ticker` → `userVisibleMarketData` 映射（MUST · 实现对签）

**问题类**：上游 **ticker 含 `last`**，注入后 **仅 `bestBid`/`bestAsk`** → 模型 **合规拒答「无最新价」**。**本节** **冻结 Publish/Runtime 映射下限**（**OpenAPI 形状仍 SSOT**）。

**HTTP 真源（现货公开）**：`GET /sapi/v2/ticker`（[`design/api`](../../../../design/api.md)、Coobit 公档 **`last`/`bidPrice`/`askPrice`** 等）。

| **上游字段（Coobit ticker · 示意）** | **`userVisibleMarketData`（MUST 若上游有值）** | **说明** |
|--------------------------------------|-----------------------------------------------|----------|
| `symbol` | `symbol` | 与请求一致 |
| **`last`** | **`lastPrice`** | **最新成交**；**禁止** **有 `last` 却不映射** |
| `bidPrice` | `bestBid` | 买一 |
| `askPrice` | `bestAsk` | 卖一 |
| `high` / `low` / `vol` / `change` 等 | `high24h` / `low24h` / `volume24h` / `change24hPct` | **按矩阵** **有则映** |
| 时间字段 | `asOf` / `timestamp` | **Stale** **同窗** **`FR-MI03`** |

**降级（确定性 · 仅当上游无 `last` 且有 bid/ask）**：

- **允许** **Runtime** **算** **`mid = (bestBid + bestAsk) / 2`** **写入 **`lastPrice`**，**并** **在 **`asOf`** **或等价元数据标注 **`priceSource=mid_from_book`**（键名 **`design` MR**）；**禁止** **把** **该 mid** **标注为** **「最新成交」** **而不披露口径**（Prompt **须** **可区分** **或** **用户话术用「参考价/中间价」**）。

**MUST NOT**：

- **用** **`GET /sapi/v2/depth`** **顶栏** **冒充** **ticker** **却** **登记为 **`tool.market.ticker`** / **`read.market.ticker`**（**无 `last`** → **不得** **伪称 ticker 闭环**）。  
- **静默丢弃** **§3.1 已存在之上游字段** — **同窗** [`runtime-injection` §2.4.1](../../admin/prompt-management/runtime-injection.md) **勿静默丢字段**。

**验收**：**`SC-MRP01`**、**`eval.market.ticker_facts_mapping`**（[`evals/scenarios.md`](../../../evals/scenarios.md)）。

### 3.4 `marketNarrativeHints`（市场叙事提示 · 草案 · 解冻前 TBD）

**定位**：**Runtime 从 Market State 派生** 的 **推荐叙事锚** — **供块 5 · Runtime Context 注入**；**不是** **第二套 Phrase Library SSOT**。**锚句真源** → [`common-phrases` §8](../../../prompts/shared/common-phrases.md)；**体系** → [`market-intelligence` §4](market-intelligence.md)。

**契约状态**：**草案 · 默认可不注入** — **OpenAPI 形状 SSOT** → [`market-runtime-schemas.yaml`](../../../../openapi/components/market-runtime-schemas.yaml)（**`MarketNarrativeHints`/`MarketPhase`**）；**phase 派生管线** → [`design/market-narrative-runtime.md`](../../../../design/market-narrative-runtime.md)。**数值阈值** **仍** **TBD** **至** **analytics MR**。

**形状下限（示意 · camelCase · 与 OpenAPI 同窗）**：

| 字段（可选） | 说明 |
|--------------|------|
| `marketPhase` / `primaryMarketPhase` | **须** **∈** **§3.2.1 登记枚举**；**与 **`marketInsightData`** **同源** |
| `secondaryMarketPhases` | **0～2** **个** **登记枚举值**；**可选** |
| `recommendedNarratives` | **1～3 条** **短句** — **须** **选自** [`common-phrases` §8.2](../../../prompts/shared/common-phrases.md)；**禁止** **自由扩库** |
| `narrativeAsOf` | **与 Facts **`asOf`** 同窗** |
| `requiredFactsPresent` | **示意**：**`lastPrice`/`fundingRate`/…** **布尔或列表** — **便于 Eval 对账**（**OpenAPI 终裁**） |

**示例（非契约 JSON · 评审用）**：

```json
{
  "marketPhase": "sideways",
  "recommendedNarratives": [
    "盘面有点胶着",
    "市场还在拉扯"
  ],
  "narrativeAsOf": "2026-05-25T14:30:00Z"
}
```

**MUST**：

- **注入序**：**低于** **Fresh 工具 Facts（`userVisibleMarketData`/`marketInsightData`）** — **同窗** [`memory-runtime` §5](../../../Runtime/memory-runtime.md) **④ 之前仅作润色**。
- **无 **`marketPhase`** **且无 Facts** → **不注入** **`recommendedNarratives`**。

**MUST NOT**：

- **用 hints 替代** **`lastPrice`/Funding 等数值**。
- **把 hints 登记为** **独立 **`promptPackKind`** **或** **Few-shot 包**。

**验收同窗**：**`SC-MI04`～`SC-MI08`**、**`eval.market.narrative_*`**（[`evals/scenarios.md`](../../../evals/scenarios.md)）。

---

## 4. `observability` 与用户面分离

| 维度 | **`scenarioId` 字面** | **`toolId` / PATH** |
|------|----------------------|---------------------|
| **用户 Telegram** | **禁止** | **禁止** |
| **日志 / 链路** | **canonical**；可选用 **`implementationScenarioAlias`** | **可** |

---

## 5. MR / 实现对签清单（摘录）

- [ ] **归因**：观测/信封中 **`scenarioId`** **须为** [`routing-engine` §1](../agent-orchestration/routing-engine.md) **登记之 canonical（**`market.read_*`**）；实现别名须有 **`implementationScenarioAlias`**（或等价键）— **§1.1** **同文**。  
- [ ] **出站 `text`**：用户通道不得以 `/sapi/`、`GET /`、`scenarioId`、`场景 ID` 等技术串作为主文案（建议 CI / 对账脚本拦截）。  
- [ ] **`marketInsightData`**：深度类 Prompt **仅**在 §3.2 至少一项事实源回填时挂载。  
- [ ] **Ticker 映射**：**§3.3** **`last`→`lastPrice`** **`bidPrice`/`askPrice`→`bestBid`/`bestAsk`**；**有 last 不得仅注入 bid/ask**；**depth 不得冒充 ticker** — **`SC-MRP01`** / **`eval.market.ticker_facts_mapping`**。
- [ ] **叙事 hints（若解冻）**：**§3.4** **`marketNarrativeHints`** **与** **§3.2.1 `marketPhase`** **同源**；**锚句** **链** **`common-phrases` §8** — **`SC-MI04`～`08`**、**`eval.market.narrative_*`**。

---

## 6. 验收 · `SC-MRP*`

| ID | **Then（摘要）** |
|----|------------------|
| **SC-MRP01** | **Given** **`tool.market.ticker`** **成功** **且** **上游 JSON 含 **`last`** · **When** **注入 **`userVisibleMarketData`** · **Then** **`lastPrice`** **存在且数值一致**；**用户问现价** **不得** **仅因缺 **`lastPrice`** **反复降级** |
| **SC-MRP02** | **Given** **路由 **`market.read_quote`** · **When** **出站 Telegram** · **Then** **无** **`read.market.*`/PATH/`scenarioId` 字面**（**§2**） |

---

**文档版本**：0.4.2 · **维护**：产品 + Agent Runtime owner · **本版**：**篇首 MNRA/PRS 互链**。**承** 0.4.1。
