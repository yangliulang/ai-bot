# Observability Management · 配置与 IA

## 1. 查询 IA

| 入口 | 默认列 / 筛选项（下限） | 互引 |
|------|-------------------------|------|
| **执行** | `executionId`、耗时、`userId`、可选 **`scenarioId`**、**深链 L01～L03** | `observability` **§2.1**、**FR-MC801** |
| **工具** | **`toolId`**、**`toolCallSeq`**、**`invocationState`**、**PATH/错误摘要**（**非**明文 body） | **FR-MC803**、**SC-OBS05** |
| **LLM** | **`modelId`**、`inputTokens`/`outputTokens`，**无 body 默认列** | **FR-MC804** |
| **计费 / 账务时间线（协查）** | **`billingTraceId`**、`idempotencyKey`、**`capabilitySkuId`**、**核销状态**（**SUCCESS/INSUFFICIENT/FAILED/skipped**）、**`commercialSettlementType=ENTITLEMENT_DEBIT`**；**可选 Metering**：`inputTokens`/`outputTokens`；**并排** **`trading.exchange_private.exchangeOutcome`**（若同源执行） | **`FR-MC503`**、**[`observability/overview.md`](../../../observability/overview.md) §2 · 计费表**；[`billing-management/functions.md`](../billing-management/functions.md) |
| **审计** | 时间、`actor`、`action`、`resource` | **FR-MC806**、[`audit-log.md`](../../../observability/audit-log.md) |

**Deep link**：实例详情 · **日志** Tab **须**能将 **`instanceId`→`userId`**（或等价）传给 **FR-MC802**（同窗 **`agent-management` `config`/详设**）。

### Demo（`src/admin`）与 §1

**对齐 SSOT**：[`admin-console-observability-reconciliation.md`](admin-console-observability-reconciliation.md) **§0**（协查页）· [`admin-console-runtime-executions-reconciliation.md`](admin-console-runtime-executions-reconciliation.md) **§0**（执行列表）。

| 项 | Demo |
|----|------|
| **协查路由** | `/observability` · 五 Tab + 顶栏三字段 + 协查抽屉 |
| **执行列表** | `/runtime/executions` · 运营主列表（**非** 本 §1 表的全量 API） |
| **运行健康 SLI** | **无** 页内看板；`obs.health` / `obs.alerts` **仅重定向** |

## 2. 保留与采样（展示）

**只读**：`hotRetentionDays`、`sampleRate`… 实际值 **以** **`observability` 域** infra 配置为准。

## 3. 嵌入

Grafana / CloudWatch **iframe** **须** SSO 与 **行级**权限产品评审后启用。

---

## 4. 执行检索键：`executionId` 与 `traceId` / `spanId`

| 主题 | 约定 |
|------|------|
| **默认主筛** | **`executionId`**：与 [`exchange-agent/overview.md`](../../agent/exchange-agent/overview.md) **FR-T01**、[`observability/overview` §2](../../../observability/overview.md) 事件下限对齐；时间线 **`FR-MC801`**。 |
| **`traceId` / `spanId`** | **可选**：排障或高级筛选；**仅 **L2+ / 排障 IAM**（[`rules.md`](rules.md)）；与 **[`tracing.md`](../../../observability/tracing.md)**、infra / OpenTelemetry **同窗**。 |
| **HTTP 契约** | [`design/api.md`](../../../../design/api.md) **`admin/observability/*`**：主查询锚定 **`executionId`**；**可选 **`traceId`** **query**（OpenAPI 冻结）。 |

---

**文档版本**：0.1.3 · **维护**：后台 + IA · **本版**：**§4** 执行键与 **`tracing.md`/`design` 同窗**；**顺延 0.1.2**。
