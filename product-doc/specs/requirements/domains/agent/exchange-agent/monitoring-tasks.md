# Exchange Agent · 条件监控与通知（Monitoring Tasks）

**路径**：`specs/requirements/domains/agent/exchange-agent/monitoring-tasks.md`。

**职责**：**Monitoring Capability** — **用户可创建的任务形态**（条件、价格、事件、定时 / Pull 复盘）、**用户价值** **与** **和 Risk Alerts 的产品边界**。**不写** **`taskId` 状态机**、**不写** **`executionId`/观测对齐细则**。**执行面** → [`../agent-orchestration/state-machine.md`](../agent-orchestration/state-machine.md)；**流程** → [`../../../flows/automation-alerts.md`](../../../flows/automation-alerts.md)。

---

## 1. 任务与通知类型（产品下限）

| 子主题 | 说明 | **能力依赖（概念）** | 与 **Risk Alerts** |
|--------|------|---------------------|---------------------|
| **条件监控** | **用户声明**的规则（到价、指标、盈亏阈值 **等**；**范围** **见** **`automation-alerts`** **流程）** | **行情读能力** **+** **Portfolio/账户** **私有读** | **单次** **vs** **订阅** **的执行语义** → [`../agent-orchestration/state-machine.md`](../agent-orchestration/state-machine.md) |
| **价格提醒** | **到价/穿价** **等** **离散事件** | **行情读能力** | **偏** **Monitoring**；**叠** **强平解读** **时** **叠** **Risk** **叙事** |
| **事件提醒** | **日历/宏观/项目方**（**可选**） | **研究/日历类** **只读** | **低敏** **—** **Disclaimer** |
| **定时任务** | **周期性拉取** **或** **复盘** | **仅** **已登记** **所内只读 PATH**（**工具宿主** [`trade-assistance.md §8.3`](trade-assistance.md)） | **非** **全量网格/DCA 机器人** |

**触发后写**：**须** **独立** **走** [`trade-assistance.md`](trade-assistance.md) **确认链**（**ADR-001**）。

---

## 2. FR / SC（能力域）

| ID | 陈述 |
|----|------|
| **FR-MT01** | **条件任务** **须** **可暂停/删除**；**用户** **须** **可见** **「因何触发」** **之** **最小说明**（**符号/阈值/时间** **等** — **产品文案层**）。 |

| ID | **验收要点**（可对签） |
|----|-------------------------|
| **SC-MT02** | **触发** **通知** **含** **符号/阈值/触发时间** **之一** **以上**（**`FR-MT01`**）。 |

**状态迁移、观测一致性、计费与终态** **—** **`FR-MT02`、`FR-MT03`、`SC-MT01`、`SC-MT03`** → [`../agent-orchestration/state-machine.md`](../agent-orchestration/state-machine.md)。

---

## 3. 互引

| 文档 | 关系 |
|------|------|
| [`market-intelligence.md`](market-intelligence.md) | 条件 **行情侧** |
| [`portfolio-insight.md`](portfolio-insight.md) | **PnL/持仓** **条件侧** |
| [`risk-alerts.md`](risk-alerts.md) | **瞬时风险** **vs** **订阅** **边界** |
| [`trade-assistance.md`](trade-assistance.md) | **触发后写** |
| [`../../../Runtime/execution.md`](../../../Runtime/execution.md)、[`../../../Runtime/overview.md`](../../../Runtime/overview.md) | **在途、D-1**（**横切**） |

---

**文档版本**：0.4.0 · **维护**：产品 + Agent Runtime owner · **本版**：**删除** **`taskId` 生命周期** **与** **执行向 FR/SC** — **迁至** [`state-machine.md`](../agent-orchestration/state-machine.md)。
