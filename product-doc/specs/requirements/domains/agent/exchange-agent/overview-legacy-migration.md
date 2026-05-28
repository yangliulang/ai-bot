# Exchange Agent · 旧稿回迁与 §10.x 锚点映射

**路径**：`specs/requirements/domains/agent/exchange-agent/overview-legacy-migration.md`。

**定位**：**迁移 / 契约对读用附录** — **非**五域 **Capability SSOT**。**产品能力总览** → [`overview.md`](overview.md)。

**收敛（2026-05-09）**：**工具/技能/写路径** **以** [`trade-assistance.md`](trade-assistance.md) **§4·§8** **与** [`design/api.md`](../../../../design/api.md) **子账户矩阵** **为现行真源**；**本文件** **仅** **对读旧 `§10.x`** — **新文请直链分卷与矩阵**，**避免双轨**。

**职责**：收录 **旧单行稿 → 分卷** 的回迁指引，以及 **原 `overview`/`runtime` §10.x** 的外链 **落点对照表**；供 `product.md`、`contract-closure`、`design/api`、流程文 **在改链前** 对签。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 旧稿 → 分卷（回迁工作指引）

| 旧文件名 / 口吻 | **优先**回迁目标 | 备注 |
|-----------------|------------------|------|
| **`trading-agent.md`（单行） / `exchange-agent/overview` FR 总入口** | [`overview.md`](overview.md) **§1～§2** + 下列分卷 | **FR-T01～T04** **计费/子账户**：与 [`../../flows/consume-and-bill.md`](../../../flows/consume-and-bill.md)、**`billing`** **同窗** |
| **`runtime.md` §10.x**（槽位、Push、产品线闸、`FR-T11` …） | [`trade-assistance.md`](trade-assistance.md)、[`monitoring-tasks.md`](monitoring-tasks.md)、[`../../../Runtime/execution.md`](../../../Runtime/execution.md)、[`../../../Runtime/overview.md`](../../../Runtime/overview.md)；**执行面 adjunct** → [`routing-engine.md`](../agent-orchestration/routing-engine.md) **及** **[`overview` 索引](../agent-orchestration/overview.md)** | **技术性状态机/D-1**：以 **`Runtime/`** + **`config.md` §11** 为正 |
| **`flow.md` / 主路径产品码** | [`trade-assistance.md`](trade-assistance.md)、[`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) | **`FR-T05`** **等话术**：流程文 **先于** [`overview.md`](overview.md) 补 **§** |
| **`risk.md` §8.x / `runtime-policy`** | [`boundaries.md`](boundaries.md)、[`risk-alerts.md`](risk-alerts.md) | **`WEALTH_ACTION_REQUIRES_WEB`** 等 → **`boundaries`** |
| **`trading-skills.md` / `tools.md` §10.4** | [`trade-assistance.md`](trade-assistance.md)、[`../../../tools/tool-registry.md`](../../../tools/tool-registry.md) | **`toolId`/`skillId`**：**能力登记** **见** **`trade-assistance` §4·§8**；**`scenarioId` 寄存器** → [`routing-engine.md`](../agent-orchestration/routing-engine.md) |
| **域内 `metrics.md`（SC-T*）** | [`../../../metrics/trading-metrics.md`](../../../metrics/trading-metrics.md) | 与用户域 **观测**同窗 |

---

## 2. 遗留锚点映射（原 `overview` / `runtime` **§10.x**）

分卷后 **[`overview.md`](overview.md) 正文不再使用 `§10` 编号**，但 **`product.md`、`contract-closure`、`flows/trade-via-agent`、`domains/admin/trading-agent-config`** 等仍可能引用旧号。**下表供对读**；**长期** **应** **将外链** **改指** **现行分卷 §** **或** **流程专节**。

| 旧引用（常见） | **现行**落点 |
|----------------|-------------|
| **`§10.2` / `FR-T06`（Push）** | [`monitoring-tasks.md`](monitoring-tasks.md)；[`../../flows/automation-alerts.md`](../../../flows/automation-alerts.md) |
| **`§10.3` / `FR-T07`（槽位 · 意图→场景）** | [`intents.md`](intents.md)；[`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md)；[`../agent-orchestration/overview.md`](../agent-orchestration/overview.md) **FR-AO02** |
| **`FR-T09`（每笔写须类型 A + 限额；与产品线闸同窗）** | [`trade-assistance.md`](trade-assistance.md) **§2**；[`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md)；[`../telegram/overview.md`](../telegram/overview.md) **§2.5 · 类型 A**（总则 **§2～§2.6**）；[**ADR-001**](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)；**验收摘录** → [`../agent-orchestration/confirmation-flow.md`](../agent-orchestration/confirmation-flow.md) |
| **`§10.5`（产品线闸 / `FEATURE_*`）** | [`../../admin/trading-agent-config/`](../../admin/trading-agent-config/) **`keys`/`functions`**；[`trade-assistance.md`](trade-assistance.md) **门闸对签** |
| **`§10.6`（长驻任务 / 自动化）** | [`monitoring-tasks.md`](monitoring-tasks.md)；[`../../flows/automation-alerts.md`](../../../flows/automation-alerts.md)；**`taskId` 生命周期** → [`../agent-orchestration/state-machine.md`](../agent-orchestration/state-machine.md) |
| **`§10.7` / `FR-T11`（写前 `read_skill`）** | [`trade-assistance.md`](trade-assistance.md) **§2、§4、§8.2** |
| **`§10.8` / `FR-T12`（限价偏离带）** | [`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 现货限价**（**第五步·偏离带**）；[`../../admin/management-console-v1-prd.md`](../../admin/management-console-v1-prd.md) **`FR-C08` / `AGENT_PRICE_*`** |

<span id="legacy-s10-mapping"></span>

---

**文档版本**：0.1.1 · **维护**：产品 + Agent Runtime owner · **本版**：**FR-T09** **现行落点** **补** **`telegram/overview` §2.5 · 类型 A**；**承 0.1.0**。
