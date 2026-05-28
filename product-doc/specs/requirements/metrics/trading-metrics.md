# 交易指标（索引）

**SSOT**：Capability 总览 [`../domains/agent/exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md)；**编排执行面**：[`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md)、[`task-scheduler.md`](../domains/agent/agent-orchestration/task-scheduler.md)、[`state-machine.md`](../domains/agent/agent-orchestration/state-machine.md)、[`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md)；**总索引** [`agent-orchestration/overview.md`](../domains/agent/agent-orchestration/overview.md)；登记宿主 [`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md)；计费 [`billing-management/overview.md`](../domains/admin/billing-management/overview.md)。**与 UNKNOWN / `exchangeViewSource` 同窗 SLI**：[**`observability/metrics.md` §2**](../observability/metrics.md)。

建议在此文维护 **交易结果类指标** 的列表与数据源指向（撮合结果、订单终态、`toolId`/矩阵维度等），条目细节以 **`design/api`** 与域正文为准。

## 域验收 / SC 索引（便于聚合）

| 前缀 / 条目 | 文档 |
|-------------|------|
| **SC-PI\*** | [`exchange-agent/portfolio-insight.md`](../domains/agent/exchange-agent/portfolio-insight.md) |
| **SC-RA02、SC-RA03** | [`risk-alerts.md`](../domains/agent/exchange-agent/risk-alerts.md)（话术与数据锚）；**SC-RA01**（频控回放）[`task-scheduler.md`](../domains/agent/agent-orchestration/task-scheduler.md) |
| **SC-MT02** | [`monitoring-tasks.md`](../domains/agent/exchange-agent/monitoring-tasks.md)；**SC-MT01、SC-MT03** [`state-machine.md`](../domains/agent/agent-orchestration/state-machine.md) |
| **SC-MI\*** | [`market-intelligence.md`](../domains/agent/exchange-agent/market-intelligence.md) |
| **SC-TA01、SC-TA02** | [`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md) |
| **SC-RISK-01～05** | [`risk/acceptance.md`](../risk/acceptance.md)（**运营闸 / 护栏**；抽检 **可** 与 [`observability/overview.md`](../observability/overview.md) **§2 · `executionId`** 轴 **同窗**） |
