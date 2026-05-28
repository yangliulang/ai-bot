# Exchange Agent（业务能力分卷）

**入口总览**：[`overview.md`](overview.md) · **契约与工具宿主**：[`trade-assistance.md`](trade-assistance.md)

本目录承载 **交易所场景 AI Agent（AI Trading Companion）** 的 **需求叙事与产品下限**。**OpenAPI / `operationId` SSOT**：[`../../../../design/api.md`](../../../../design/api.md)；**跨域收口**：[`../../../contract-closure.md`](../../../contract-closure.md)；**关单余量** **[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks)** · **[§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)** · **[§7](../../../closure-remaining.md#cc-remaining-open-items)**。**对上 Coobit 私网 HTTP**：默认 **`openapi-ai`**（Skill 宿主，须 pin）；PATH 与白名单同窗 [`integrations/exchange/overview.md`](../../../integrations/exchange/overview.md)、[`overview.md`](overview.md) 篇「私网出站」、[allowlist](../../../integrations/exchange/agent-coobit-api-allowlist.md)。**端到端鸟瞰 · 架构语言**：[`flow/e2e-closed-loop.md`](../../../../../flow/e2e-closed-loop.md) **文首「架构语言」** → [`architecture` §「与通用 Agent 栈之对照」](../../../../design/architecture.md)。

---

## 0. 小团队速读（≈2 人）

1. [`overview.md`](overview.md) **Capability**  
2. [`trade-assistance.md`](trade-assistance.md) **§8 工具/技能**  
3. [`../../../../design/api.md`](../../../../design/api.md) **子账户矩阵（承诺上限）**  
4. [**实现对齐（编排）**](../agent-orchestration/implementation-alignment.md) **（§6 检查单 · §12 GWT · §13 对客三闸 / eval 束）**  
5. [`../../../../../product/release-notes.md`](../../../../../product/release-notes.md) **当前不承诺 / TBD 快照**（与 [`LITE-MODE`](../../../LITE-MODE.md) 同窗）  
6. 旧 §10 映射：[`overview-legacy-migration.md`](overview-legacy-migration.md)

---

## 1. 五类能力域与分卷

| 能力域 | 分卷（SSOT） | 当前成熟度（实施跟踪） |
|--------|----------------|------------------------|
| **Market Intelligence** | [`market-intelligence.md`](market-intelligence.md) | v0.3 骨架：条目已填，矩阵 PATH 仍为对签输入 |
| **行情 Runtime 快照与对客对齐** | [`market-runtime-payload.md`](market-runtime-payload.md) · **camelCase Facts、别名归一、`userVisibleMarketData` / `marketInsightData`** | **同窗** MI / `routing-engine` §1.1 / [`read-analyze`](../../../flows/read-analyze-and-search-via-agent.md) |
| **Portfolio Insight** | [`portfolio-insight.md`](portfolio-insight.md) | 同上 |
| **Risk Alerts** | [`risk-alerts.md`](risk-alerts.md) | 同上 |
| **Trade Assistance** | [`trade-assistance.md`](trade-assistance.md) | §8 **`toolId`/`skillId`** **宿主**；编排键 **`scenarioId`** → [`../agent-orchestration/routing-engine.md`](../agent-orchestration/routing-engine.md) |
| **Monitoring Tasks** | [`monitoring-tasks.md`](monitoring-tasks.md) | v0.3 骨架 |
| （横跨）**Intents** | [`intents.md`](intents.md) | **语义层**；**`scenarioId`** → [`routing-engine`](../agent-orchestration/routing-engine.md)；其余编排执行面 → [`agent-orchestration/overview.md`](../agent-orchestration/overview.md) **§1 文档地图** |
| （横跨）**Boundaries** | [`boundaries.md`](boundaries.md) | v0.3：稳定码与 §8.3/8.4 承接 |

---

## 2. 实施路线（阶段）

| 阶段 | 目标 | 主要产出 |
|------|------|----------|
| **P0 · 叙事闭环** | 五域 + intents + boundaries **可互引、无空表** | 各分卷 v0.3 能力/意图/边界表；本 README 跟踪 |
| **P1 · 编排对签** | `scenarioId` 见 [`routing-engine.md`](../agent-orchestration/routing-engine.md)；**`FR-AO*`** **[`overview.md`](../agent-orchestration/overview.md)**；DAG / `orchestrationVersion` **见** **[`runtime-freeze.md`](../agent-orchestration/runtime-freeze.md)** | 各分卷与邻域链 **自检** |
| **P2 · 契约冻结** | 对外承诺与验收 **贴矩阵 MR** | `design/api.md` 脚注与各域 FR/SC-ID；[`../../../metrics/`](../../../metrics/README.md) 选中 SC |
| **P3 · 回迁扫尾** | 旧稿外链（risk/runtime/§10.x）清零；维护 **[`overview-legacy-migration.md`](overview-legacy-migration.md)**、自检 [`spec.md`](../../../spec.md)、`product` | 回迁进度见 **同上** §1 |

**流程侧主链路**（编排输入）：[`../../../flows/read-analyze-and-search-via-agent.md`](../../../flows/read-analyze-and-search-via-agent.md)、[`../../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md)、[`../../../flows/wealth-via-agent.md`](../../../flows/wealth-via-agent.md)、[`../../../flows/automation-alerts.md`](../../../flows/automation-alerts.md)、[`../../../flows/consume-and-bill.md`](../../../flows/consume-and-bill.md)。

---

## 3. 维护角色

| _owned by_ | 范围 |
|-------------|------|
| 产品 + Agent Runtime owner | overview、trade-assistance、monitoring-tasks、market/portfolio（与矩阵） |
| 产品 + 风控/交互 owner | risk-alerts、boundaries |

**文档批次**：路线图见 **overview v0.2.5+**、编排见 **agent-orchestration v0.3.1+**、本分卷 pillar **v0.3** 起。
