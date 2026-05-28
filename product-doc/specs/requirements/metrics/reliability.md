# 可靠性指标（索引）

**SSOT**：HTTP 504、UNKNOWN、幂等与查单对账见 [`../../design/architecture.md`](../../design/architecture.md)、[`../../design/api.md`](../../design/api.md)；用户可见失败与 UNKNOWN 语义见 [`../observability/overview.md`](../observability/overview.md)。**控制台 SLI 命名下限**：[**`observability/metrics.md` §2**](../observability/metrics.md)。**编排执行预算顶** **之** **观测与** **`SC-OBS07`** → [`../observability/overview.md`](../observability/overview.md) **§4**、[`../domains/agent/agent-orchestration/execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4**。

建议在此文维护 **可用性 / 长尾错误 / 对账一致率** 等指标的命名与监控入口链接，不重复展开设计细节。
