# Metrics（指标体系索引）

本目录用于 **指标定义与验收条目的导航**；具体 FR/SC 仍以各 **`domains/`** 为准（尤其 **[`observability/overview.md`](../observability/overview.md)**、[`billing.md`](../domains/admin/billing-management/overview.md)、[`trading-metrics.md`](trading-metrics.md)（**SC-T*、`SC-RISK*`**）、[`exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md)）。

**跨主题 SLI 清单（控制台嵌入下限）**：[**`observability/metrics.md` §2**](../observability/metrics.md)。**契约矩阵 / 观测告警 / Open 项收口** **同窗** **[`design/api.md`](../../design/api.md)**、[`contract-closure.md`](../contract-closure.md)、[**§0 速链**](../closure-remaining.md#closure-remaining-quicklinks) · [**`closure-remaining` §6 / §6.4**](../closure-remaining.md#cc-exec-solve-path) · [**§7.5～§7.6**](../closure-remaining.md#cc-remaining-open-close-path)。

| 文件 | 用途 |
|------|------|
| [`ai-metrics.md`](ai-metrics.md) | Agent 侧：延迟、失败率、工具调用、Token 与对话质量类 **索引** |
| [`trading-metrics.md`](trading-metrics.md) | 交易侧：成交、撤单、滑点、与所内对账相关 **索引** |
| [`reliability.md`](reliability.md) | 可靠性：504/UNKNOWN、重试、幂等等 **索引** |
| [`../evals/README.md`](../evals/README.md) | **评测素材 / 场景集 / 数据集版本** 登记 — **与** 本条 **分工**（**非**指标定义 SSOT） |

新增指标时：优先在对应 **域文档** 写清 SC/监控名，再在此目录补链，避免双份 SSOT。评测用例 **不**在此堆积 — → **`evals/`**。
