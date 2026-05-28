# Billing Management（`admin/billing-management/`）

**聚合 PRD**：[`../management-console-v1-prd.md` · 模块五 §8](../management-console-v1-prd.md) · **实施对位**（**v0.2.1-impl**）：[`design/api`](../../../../design/api.md) **模块五登记行**、[`keys` §5](../trading-agent-config/keys.md) **`BILLING_*`**、[`contract-closure`](../../../contract-closure.md) **§8（轨 B 关单）**

**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

| 文件 | 说明 |
|------|------|
| [`commerce-model.md`](commerce-model.md) | **商业分层 SSOT**：Capability、**仅轨 B 清算**、用尽即停（**v0.3.0**） |
| [`overview.md`](overview.md) | 域定位、**§7～§12** 契约锚点、里程碑、FR-B **/** SC-B **占位** |
| [`functions.md`](functions.md) | **FR-MC501～508**、**§5 Phase 2**（**FR-B17～B21 / SC-B20/B21**）、`SC-B*` **联考** |
| [`flow.md`](flow.md) | 资格、**S5 轨 B 核销**、冲正、导出概念序 |
| [`config.md`](config.md) | **`BILLING_MODE`、`PHASE2_COMMERCE_RAILS_ENABLED`、IA** |
| [`rules.md`](rules.md) | **`PER_EXECUTION_FINAL`、轨 B 幂等、权限** |

**建议阅读顺序**：`commerce-model` → overview → functions → rules → flow → config（与 overview §5 **一致**）。
