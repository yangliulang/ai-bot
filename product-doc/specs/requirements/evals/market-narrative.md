# Evals · Market Narrative（GWT 构造专卷）

**职责**：**`eval.market.*`** **之** **Given/When/Then 可执行构造** **与** **Mock 下限**。**索引 SSOT** → [`scenarios.md`](scenarios.md)；**MNRA** → [`market-narrative-runtime/README`](../market-narrative-runtime/README.md)、[`scenario-matrix`](../market-narrative-runtime/scenario-matrix.md)；**FR 宿主** → [`market-intelligence` §4](../domains/agent/exchange-agent/market-intelligence.md)；**OpenAPI** → [`market-runtime-schemas.yaml`](../../openapi/components/market-runtime-schemas.yaml)。

**性质**：**规格层 fixture** — **脚本/断言** **可** **在所内 Runtime 仓实现**；**本条** **保** **构造要点与 Then 可观测键**。

---

## 1. 共用 Mock 基线

**`scenarioId`**：**`market.read_quote`**（Ticker）或 **`market.read_deep_analysis`** / **`futures.read_funding`**（按用例）。

**Runtime Context 注入宿主**（块 5 · 示意 JSON · **须** **对齐 OpenAPI**）：

```json
{
  "userVisibleMarketData": {
    "symbol": "BTCUSDT",
    "lastPrice": "67234.50",
    "bestBid": "67234.00",
    "bestAsk": "67235.00",
    "change24hPct": "-1.23",
    "volume24h": "12345.67",
    "asOf": "2026-05-25T14:30:00Z",
    "priceSource": "last_trade"
  }
}
```

**Stale 构造**：**`asOf`** **= now − Δt**，**Δt > `Δt_stale_market`**（**所内 config 冻结**）— **或** **工具 **`phase=fail`**。

**观测 join 键**：**`executionId`**、**`sessionId`**、**`symbol`**、**`agent.market.phase_computed`**（**若注入 phase/hints** — **`SC-OBS09`**）。

---

## 2. 用例 GWT

### 2.1 `eval.market.ticker_facts_mapping` → **`SC-MRP01`**

| 项 | 内容 |
|----|------|
| **Given** | Mock **`tool.market.ticker`** **响应含 **`last: "67234.50"`**（**及 bid/ask**） |
| **When** | Publish/Runtime 映射后问「BTC 现在多少？」 |
| **Then** | **`userVisibleMarketData.lastPrice`** **存在且 = 67234.50**；**用户可见** **含 last/现价语义**；**禁止** **仅复述 bid/ask 并声称「无最新价」** |
| **Then（负例）** | **若映射层丢弃 `last`** → **Eval 失败**（**根因在 Facts，非模型保守**） |

---

### 2.2 `eval.market.narrative_with_facts` → **`SC-MI04`**

| 项 | 内容 |
|----|------|
| **Given** | **Ticker 闭环** + **`primaryMarketPhase=sideways`**（**规则或 **`marketInsightData`** 同源**）；**可选 **`marketNarrativeHints`**：`recommendedNarratives` **≤2 条** **选自 §8.2.1** |
| **When** | 用户：「BTC 盘面怎么样？」 |
| **Then** | **含** **可读状态**（**如胶着/震荡意向** **或** **等价 natural language**）；**含 **`lastPrice`** **或 **`asOf`**；**禁止** **纯「根据数据显示」无 Facts** |
| **Then（观测）** | **`agent.tool.call`** **`toolId=tool.market.ticker`** **`phase=success`**；**若 hints 注入** → **`agent.market.phase_computed.primaryMarketPhase=sideways`** |

**Bad vs Good（单轮 · 评审用）**：

- **Bad**：「根据查询结果，BTC 当前买一 67234、卖一 67235。」（**客服腔、无盘感锚**）  
- **Good**：「BTC 现在在 67234 附近，盘面有点胶着，24h 量 1.23 万 BTC 左右（截至 14:30 UTC），仅供参考。」

---

### 2.3 `eval.market.narrative_stale_no_phase` → **`SC-MI05`**

| 项 | 内容 |
|----|------|
| **Given** | **(a)** **Ticker **`phase=fail`** **或** **(b)** **`asOf` stale** **或** **(c)** **无 **`userVisibleMarketData`** |
| **When** | 用户：「现在盘面什么感觉？」 |
| **Then** | **不得** **出现 §8.2 锚句**（**如「盘面胶着」「多头占上风」**）；**须** **`FR-T05`/UNKNOWN 或说明暂无法判断** |
| **Then（宿主）** | **Prompt/Context** **无 **`marketNarrativeHints`** **且无 **`marketPhase`** |

---

### 2.4 `eval.market.narrative_funding` → **`SC-MI06`**

| 项 | 内容 |
|----|------|
| **Given** | **`scenarioId=futures.read_funding`**；**`tool.futures.funding_summary` success**；**`marketInsightData`**：`fundingRate="0.0008"`、`primaryMarketPhase=funding_crowded_long` |
| **When** | 用户：「BTC 永续资金费率怎么样？」 |
| **Then** | **含数值** **0.08% 或等价小数/年化（与 Facts 一致）**；**含 **funding 锚意向**（**拥挤/偏正**）；**禁止** **仅锚句无率** |
| **Then（负例）** | **`funding_crowded_long`** **但无 **`fundingRate`** → **Eval 失败**（**`FR-MI07`**） |

---

### 2.5 `eval.market.narrative_high_volatility` → **`SC-MI07`**

| 项 | 内容 |
|----|------|
| **Given** | **`market.read_deep_analysis`**；**`marketInsightData.volatility="elevated"`**（**或登记字段**）；**`primaryMarketPhase=elevated_volatility`** |
| **When** | 用户：「最近波动大吗？」 |
| **Then** | **锚句与 volatility Facts 同窗**（**如「波动明显放大」+ 具体 vol 字段或区间描述**）；**非投顾 Disclaimer** |

---

### 2.6 `eval.market.phase_deterministic` → **`SC-MI08`** · **`FR-MI06`**

| 项 | 内容 |
|----|------|
| **Given** | **任意** **注入 **`marketNarrativeHints`** **之执行** |
| **When** | **抽检 Prompt 宿主 / 观测** |
| **Then** | **`primaryMarketPhase`（或 `marketPhase`）∈ [`market-runtime-payload` §3.2.1](../domains/agent/exchange-agent/market-runtime-payload.md) **枚举**；**`recommendedNarratives.length ≤ 3`**；**每条可追溯 §8.2/§8.7** |
| **Then（负例）** | **模型输出未登记 phase 字面**（**如 `super_bullish`**）→ **不得** **来自 Runtime hints**；**若出现** → **PhaseRules 或 Publish 闸缺陷** |

---

### 2.7 `eval.market.narrative_obs` → **`SC-OBS09`**

| 项 | 内容 |
|----|------|
| **Given** | **本轮** **注入 **`marketNarrativeHints`** **或 **`marketInsightData.marketPhase`** |
| **When** | **执行结束 / 时间线导出** |
| **Then** | **存在 **`agent.market.phase_computed`** **且** **`primaryMarketPhase`** **∈ 登记枚举**；**`marketPhaseSource=rules`** **时** **与** [`design/market-narrative-runtime`](../../design/market-narrative-runtime.md) **同窗** |

---

## 3. 最小回归束（Market · P2）

**建议 CI 子集**（**实现 MR 前可先文档抽检**）：

1. **`eval.market.ticker_facts_mapping`**  
2. **`eval.market.narrative_with_facts`**  
3. **`eval.market.narrative_stale_no_phase`**  
4. **`eval.market.phase_deterministic`**  

**Funding / 波动 / 观测** → **staging 全量** **或** **feature 开关 ON 后** **并入 nightly**。

---

## 4. 互引

- **流程** → [`read-analyze-and-search-via-agent.md`](../flows/read-analyze-and-search-via-agent.md) **Runtime 快照**  
- **Few-shot Git 镜像** → [`fewshot-narrative-analysis`](../prompts/library/packs/fewshot-narrative-analysis.zh-CN.md) · **评审索引** [`narrative-few-shot-specimens.md`](../prompts/analysis/narrative-few-shot-specimens.md)  
- **回归束总表** → [`implementation-alignment` §13.3](../domains/agent/agent-orchestration/implementation-alignment.md)  
- **Walkthrough** → [`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md#runtime-walkthrough-crosscut) **Goal-MKT**

---

**文档版本**：0.1.0 · **维护**：产品 + QA · **本版**：**初稿 · GWT + Mock 基线**。
