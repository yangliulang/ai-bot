# Exchange Agent · 意图（Intents）

**路径**：`specs/requirements/domains/agent/exchange-agent/intents.md`。

**职责**：**用户意图语义层** — **自然语言簇、用户目标、与五域 pillar 的归属**、**歧义分流**。**不写** **`scenarioId` 寄存器**、**不写** **编排 DAG**。*Runtime 路由键* **SSOT** → [`../agent-orchestration/routing-engine.md`](../agent-orchestration/routing-engine.md)；*执行归因* → [`../agent-orchestration/execution-lifecycle.md`](../agent-orchestration/execution-lifecycle.md)；*任务状态机* → [`../agent-orchestration/state-machine.md`](../agent-orchestration/state-machine.md)；*告警投递策略* → [`../agent-orchestration/task-scheduler.md`](../agent-orchestration/task-scheduler.md)；**总索引** **[`overview.md`](../agent-orchestration/overview.md)**。

---

## 1. 意图簇 → 用户目标 / pillar / 延伸阅读

**原则**：**先** **判别** **是否触及** **所内私有读/写**（**子账户 scope**）。**私读/写** **的门禁条文** **见** [`trade-assistance.md`](trade-assistance.md) **§2**、[`boundaries.md`](boundaries.md) — **本文** **只** **做** **语义归类**。

| 意图簇（用户话术举例） | 用户目标（摘要） | **主要 pillar** | **延伸阅读**（流程 / 分卷） |
|-------------------------|------------------|-----------------|-----------------------------|
| **行情、涨跌、Funding、盘口、K 线/解读、要闻/舆情**（**默认不写**） | **了解市场** **与** **叙事** | **Market Intelligence** | [`read-analyze-and-search-via-agent`](../../../flows/read-analyze-and-search-via-agent.md)；**工具实现宿主** [`trade-assistance.md §8.3～8.4`](trade-assistance.md) |
| **我的余额、持仓、盈亏、保证金、挂单** | **理解账户** **与** **在途状态** | **Portfolio Insight** | [`portfolio-insight.md`](portfolio-insight.md)；**私读门禁** **同窗** **`FR-T02`** **（** **Runtime/onboarding** **）** |
| **提醒我爆仓、别太集中、异动、到价** | **获知风险** **或** **订阅条件** | **Risk Alerts** · **Monitoring Tasks** | [`risk-alerts.md`](risk-alerts.md)；[`monitoring-tasks.md`](monitoring-tasks.md)；[`automation-alerts`](../../../flows/automation-alerts.md) |
| **买入/卖出/限价/市价/合约/杠杆/止盈止损/闪兑** | **在确认后** **完成** **所内写** | **Trade Assistance** | [`trade-via-agent`](../../../flows/trade-via-agent.md)；[`trade-assistance.md §2·§4`](trade-assistance.md) |
| **理财申购赎回、活期定期、收益** | **理财** **读写/回退** | **Trade Assistance** | [`wealth-via-agent`](../../../flows/wealth-via-agent.md)；[`boundaries.md §8.3`](boundaries.md) |
| **条件单到期、定投、网格（若允许）— 澄清非目标** | **辨明** **是否在** **产品范围** | **Monitoring Tasks**（澄清） | [`automation-alerts`](../../../flows/automation-alerts.md)；**非目标** **`product/overview`** |

---

## 2. 编排与执行（链出 · 本文不展开）

| 主题 | **SSOT** |
|------|-----------|
| **`scenarioId` 全表** | [`../agent-orchestration/routing-engine.md`](../agent-orchestration/routing-engine.md) |
| **执行面分卷索引** | [`../agent-orchestration/overview.md`](../agent-orchestration/overview.md) **§1** |
| **单轮主意图收敛 · 槽位** | **同文 **`FR-AO02`** · **`trade-via-agent`** **分流** |
| **结构化意图草案（实现下限）** | [`implementation-alignment.md`](../agent-orchestration/implementation-alignment.md) **§8** |
| **写路径确认链** | [`trade-assistance.md`](trade-assistance.md) **§2**（**`FR-T09`/`FR-T11`**） |
| **工具归因 / 任务生命周期 / 风控类投递频控** | [`execution-lifecycle.md`](../agent-orchestration/execution-lifecycle.md)、[`state-machine.md`](../agent-orchestration/state-machine.md)、[`task-scheduler.md`](../agent-orchestration/task-scheduler.md) |

---

## 3. 歧义分流（语义层）

| 用户可能混说的两路 | **拆分** |
|--------------------|----------|
| **「盈亏/敞口」** **vs** **「现价多少」** | **前者** → **Portfolio Insight**（**聚合口径** **非** **轻量 ticker**）；**后者** → **Market Intelligence**。**不得** **用** **现货价** **冒充** **已实现盈亏** |
| **「提醒我…」** **vs** **「马上交易」** | **前者** → **Monitoring / automation 流程**（**订阅语义**）；**后者** → **`trade-via-agent`** **单笔写** |
| **条件单 / 网格 / DCA** **全策略** | **非目标** **或** **主站** — **澄清** **不** **承诺** **Agent 全闭环** |
| **全仓杠杆下单** **但** **保证金侧可用不足**、**同子账户币币有余额** | **主意图** **仍为** **`margin.cross.*`**；**币币 → 全仓划转** **为** **该轨前置子步骤**（**类型 A** **后** **编排自动执行**）— **同窗** [`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 第四步**、[`telegram/overview` §2.5.3](../telegram/overview.md) |

---

## 4. 互引

| 文档 | 关系 |
|------|------|
| [`market-intelligence.md`](market-intelligence.md) | 市场向 **意图归宿** |
| [`portfolio-insight.md`](portfolio-insight.md) | 账户向 **意图归宿** |
| [`risk-alerts.md`](risk-alerts.md) | 风险 **外显意图** |
| [`trade-assistance.md`](trade-assistance.md) | **写** **与** **技能登记** |
| [`monitoring-tasks.md`](monitoring-tasks.md) | **订阅/条件** **意图** |
| [`../agent-orchestration/goal-and-execution-paths.md`](../agent-orchestration/goal-and-execution-paths.md) | **Goal/黄金路径/失败·恢复** **与** **§1×flow** **映射** |
| [`boundaries.md`](boundaries.md) | **不可代理** **稳定码** |

---

**文档版本**：0.4.3 · **维护**：产品 + Agent Runtime owner · **本版**：**§4** **链** **`goal-and-execution-paths`**。**承** 0.4.2。
