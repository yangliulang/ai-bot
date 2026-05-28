# Admin Console — 页面对应 API 面（索引）

**SSOT**：[`specs/design/api.md`](../../design/api.md) 与各 `specs/openapi/**/*.yaml`。  
本表仅 **按页面 ID** 指向 **已存在** 或 **待补** 的契约，**不**重复 schema。

## 图例

| 标记 | 含义 |
|------|------|
| ✅ | OpenAPI 已有路径（或等价 tags） |
| TBD | 需求已定义但 admin 契约未登记 / 需 MR 另开 |
| 🔗 | 页面以 **跳转到** 另一运营 API 为主（如联合搜索） |

## Runtime Operations

| 页面 ID | 主要 operation / 说明 |
|---------|------------------------|
| `runtime.executions` | ✅ **`listObservabilityExecutions`**（[`admin/observability.yaml`](../../openapi/admin/observability.yaml)· **`ObservabilityExecutionSummary`** / [`observability-schemas`](../../openapi/components/observability-schemas.yaml)）；**详情** **`getObservabilityExecutionTimeline`** 等 **同窗** **`executionId`** |
| `runtime.execution-detail` | ✅ `getObservabilityExecutionTimeline` 等（[`admin/observability.yaml`](../../openapi/admin/observability.yaml)；**`ObservabilityTimelineEvent.transitionTrigger`** · [`observability-schemas`](../../openapi/components/observability-schemas.yaml)；**语义** [`observability/overview` §2.4](../observability/overview.md)、**`SC-OM-04`**）；**队列 / 运行事件** 为详情 **内嵌块**；全量事件检索以 **`searchObservabilityEvents`** · FR-MC802 / 日志检索为主 |

## AI Governance

| 页面 ID | 主要 OpenAPI 文件 |
|---------|-------------------|
| `ai.agents-templates` · `ai.agents-instances` | [`admin/agent-management.yaml`](../../openapi/admin/agent-management.yaml)（以 design/api 登记表为准）；**前端**：旧 **`/agents/config`**、**/templates** 等 **Demo** **重定向** → **`/agents/instances`**；实例列表 **`/agents/instances`** |
| `ai.prompt-strategy` · `ai.prompt-safety` | [`admin/prompt-management.yaml`](../../openapi/admin/prompt-management.yaml)（**策略页** + **护栏页**；旧 `ai.prompt-system` / `ai.prompt-scenarios` 若仍出现在契约中，视为实现细节或渐进废弃） |
| `ai.tool-registry` | ✅ **Demo** [`ToolRegistryPage`](../../../src/admin/src/pages/tools/ToolRegistryPage.tsx)（同窗 [`tool-registry-reconciliation`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) §0）；**生产** [`admin/tool-management.yaml`](../../openapi/admin/tool-management.yaml)（**TBD**） |
| `ai.confirmation-rules` | **TBD** |

## User & Access

| 页面 ID | OpenAPI |
|---------|---------|
| `access.overview` | [`admin/access-control.yaml`](../../openapi/admin/access-control.yaml)（[`admin/users-global-config.yaml`](../../openapi/admin/users-global-config.yaml) 等以域内 FR 为准）。**不设** `access.eligibility` 独立页；**不设**运营侧单用户「资格查询」专屏（规则与清单见同窗域条文） |

## Billing & Usage

| 页面 ID | OpenAPI |
|---------|---------|
| `billing.overview` · `billing.operations` · `billing.ledger` | [`admin/billing-admin.yaml`](../../openapi/admin/billing-admin.yaml)（**`commerce/*`** 由商业运营 / 总览 MC512 消费；**`billing/pricing`** API 保留 · **无**运营台定价页） |

## Observability

| 页面 ID | OpenAPI |
|---------|---------|
| `obs.health` | **Demo 无独立页**（重定向 `/observability`；SLI **TBD** · 见 [`observability-reconciliation`](../domains/admin/observability-management/admin-console-observability-reconciliation.md) §0） |
| `obs.traces-logs` | ✅ 与 `search` / timeline 系列同窗；导出见 `createObservabilityAuditExport` |
| `obs.alerts` | **Demo 无独立页**（重定向 `/observability`） |

## System Config（全局参数）

| 页面 ID | OpenAPI |
|---------|---------|
| `sys.trading-config` | **[`domains/admin/trading-agent-config/`](../domains/admin/trading-agent-config/overview.md)** 叙事；admin 契约以 [`design/api.md`](../../design/api.md) **keys** / **Trading** 登记表为准 · **部分 TBD** |
| `sys.channels` | **渠道管理**：列表层 + 分渠道详情；契约按渠道挂载，示例 **电报** → [`admin/telegram-channels.yaml`](../../openapi/admin/telegram-channels.yaml)。**不设** `integ.exchange-apis` / `integ.llm-providers` 独立运营页；**LLM 供应商与网关**归平台 Infra；**Agent 侧 Runtime 模型策略**见 `ai.settings`，交所上游叙事见 `specs/requirements/integrations/exchange/`（**非**本后台独立菜单） |
| `ai.settings` | [`admin/ai-settings.yaml`](../../openapi/admin/ai-settings.yaml)（**运营侧** **`/ai-settings`**：Demo 为 **Runtime 模型策略** 表单；Infra 级 Provider/密钥以 **`design`/网关** 为准） |

## 维护

OpenAPI 变更合并后，**更新本表一行**；若新增页面，先改 [sitemap.md](sitemap.md) 再补本表。
