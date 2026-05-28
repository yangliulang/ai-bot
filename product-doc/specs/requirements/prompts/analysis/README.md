# `analysis/` · 索引（MVP）

**路径**：`specs/requirements/prompts/analysis/README.md`。

本目录为 **PRS · L6 场景条文**（Narrator 规则与分流），**不是** 行情分析运行时本体 — **Facts / phase / hints** → **[MNRA](../../market-narrative-runtime/README.md)**。

> **治理升级（2026-05）**：**运营发布** 仅 **`pp-analysis-core`**，见 [`governance-map.md` §4](../governance-map.md#4-读侧--监控--统一分析包)。下列四篇为 **Git 能力语义分卷**，**不** 表示须拆成四个 `promptPackId`。

四篇主条文：[`market-analysis`](./market-analysis.md)、[`technical-analysis`](./technical-analysis.md)、[`sentiment-summary`](./sentiment-summary.md)、[`portfolio-read`](./portfolio-read.md)。**意图宿主**：[`../intents/analysis.md`](../intents/analysis.md)。**事实口径**：无登记工具闭环不编造 — [`hallucination`](../../observability/hallucination.md)、[`../safety/privilege.md`](../safety/privilege.md)。

---

## 写作约束（全局）

| 约束 | 文档 |
|------|------|
| **读优先 · 不写 `call_exchange_write`** | [`system/system` §2](../system/system.md)、[`exchange-agent/intents`](../../domains/agent/exchange-agent/intents.md) |
| **路由 / `scenarioId`** | [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md) |
| **流程宿主（公开 vs 私读）** | [`read-analyze-and-search-via-agent`](../../flows/read-analyze-and-search-via-agent.md)、[`market-intelligence`](../../domains/agent/exchange-agent/market-intelligence.md)、[`portfolio-insight`](../../domains/agent/exchange-agent/portfolio-insight.md) |
| **MNRA（盘感运行时）** | [`market-narrative-runtime/README`](../../market-narrative-runtime/README.md)、[`scenario-matrix`](../../market-narrative-runtime/scenario-matrix.md)、[`common-phrases` §8/§8.7](../shared/common-phrases.md)、[`market-runtime-payload` §3](../../domains/agent/exchange-agent/market-runtime-payload.md)、[`evals/market-narrative`](../../evals/market-narrative.md) |
| **PRS** | [`prompt-runtime/README`](../../prompt-runtime/README.md)、[`library/scenarios/registry` §1.2](../library/scenarios/registry.md) |

---

## 文件

| 文件 | 典型语义（示意） |
|------|------------------|
| [`market-analysis.md`](./market-analysis.md) | 公开行情 / Funding / 盘口 |
| [`technical-analysis.md`](./technical-analysis.md) | 指标 / 形态 / 支撑阻力 |
| [`sentiment-summary.md`](./sentiment-summary.md) | 舆情 / 情绪摘要 |
| [`portfolio-read.md`](./portfolio-read.md) | 账户只读（余额 / 持仓 / 盈亏聚合） |
| [`narrative-few-shot-specimens.md`](./narrative-few-shot-specimens.md) | **Few-shot 评审索引**（**Publish 正文** → [`library/packs/fewshot-narrative-analysis.*`](../library/packs/fewshot-narrative-analysis.zh-CN.md)） |

---

## 阅读顺序（建议）

1. [`../intents/analysis.md`](../intents/analysis.md)（意图分流）  
2. [`market-analysis.md`](./market-analysis.md) → [`technical-analysis.md`](./technical-analysis.md) → [`sentiment-summary.md`](./sentiment-summary.md)  
3. [`portfolio-read.md`](./portfolio-read.md)（私读；[`§3`](./portfolio-read.md) 工具闭环）

---

## 上级

[`../README.md`](../README.md)

---

**文档版本**：1.3.1 · **维护**：产品 + Prompt owner · **本版**：**Few-shot Git 镜像链**。**承** 1.3.0。
