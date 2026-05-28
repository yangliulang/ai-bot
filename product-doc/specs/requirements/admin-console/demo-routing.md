# `src/admin` 路由 ↔ 页面 ID

**实现根**：[`src/admin/README.md`](../../../../src/admin/README.md)  
**命名 SSOT**：[`naming-alignment.md`](naming-alignment.md) **v3**

## 约定

- **页面 ID** 为稳定键；**显示名** 为侧栏/页眉中文（v3）。
- 默认落地 **`/runtime/executions`**。

## 路由表

| 模块（中） | 功能域（中） | 页面 ID | 页面名称（中） | Path | 组件 / 说明 |
|------------|-------------|---------|----------------|------|-------------|
| 运行运营 | 编排执行 | `runtime.executions` | 执行记录 | `/runtime/executions` | `ExecutionListPage`：列含用户/场景/业务终态 · 筛选 `q`/`intent`/`scenario`/`status`/`from`/`to` · 行点击预览抽屉 · 可选 Observability API + cursor 加载更多 · 见 [`runtime-executions-reconciliation`](../domains/admin/observability-management/admin-console-runtime-executions-reconciliation.md) §0 |
| 运行运营 | 编排执行 | `runtime.execution-detail` | 执行详情 | `/runtime/executions/:executionId` | `ExecutionDetailPage`（Overview · **Timeline**（**`FR-MC801`**；**若响应含 **`transitionTrigger`** **须在 UI 可读** — [`runtime-to-ui-mapping.md`](runtime-to-ui-mapping.md)、[`observability` §2.4](../observability/overview.md)、**`SC-OM-04`**）· Queue · Events · Retries · Recovery；**可选** `?tab=`） |
| AI 治理 | Agent 生命周期（Demo） | `ai.agents-templates` | （重定向） | `/agents/config`、`/agents/config/:configId`、`/agents/templates`、`/agents/templates/:templateId` | → **`/agents/instances`**（单租户：无独立智能体配置页） |
| AI 治理 | Agent 生命周期 | `ai.agents-instances` | **实例管理** | `/agents/instances` | `InstancesPage`（G01 · R06 批量 · I08 导出演示 · 列表无模板/渠道/子账户列 · 见 [`agent-instances-reconciliation`](../domains/admin/agent-management/admin-console-agent-instances-reconciliation.md) §0） |
| AI 治理 | Agent 生命周期 | `ai.agents-instances` | 实例详情 | `/agents/instances/:instanceId` | `InstanceDetailPage` |
| AI 治理 | Prompt | `ai.prompt-strategy` | **提示词治理** | `/prompts/strategy` | `PromptStrategyPage`（`q`/`kind`/`life`/`pack` · 16 包 · 见 [`prompt-strategy-reconciliation`](../domains/admin/prompt-management/admin-console-prompt-strategy-reconciliation.md) §0） |
| AI 治理 | Prompt | `ai.prompt-safety` | **安全防护** | `/prompts/safety` | `PromptSafetyPage` |
| AI 治理 | Tool / Registry | `ai.tool-registry` | **技能与工具** | `/ai/tool-registry` | `ToolRegistryPage`：三卡统计 · Tab 可下单/查询/外部/变更记录 · 抽屉概览+规范分节；**无** Runtime 发布 UI · 见 [`tool-registry-reconciliation`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) §0 |
| AI 治理 | Runtime 编排 | `ai.runtime-orchestration` | **运行场景** | `/ai/runtime-orchestration` | `RuntimeOrchestrationPage`（Tab：**场景目录** / **执行策略**；**可选** `?tab=routing|policy`；**可选** `?scenario=`） |
| AI 治理 | 人机确认 | `ai.confirmation-rules` | 人工确认规则 | `/ai/confirmation-rules` | `ConfirmationRulesPage` |
| 准入与风控 | 准入 | `access.overview` | 准入管理 | `/access` | `AccessPage` |
| 计费与账务 | 计费 | `billing.overview` | 计费总览 | `/billing/overview` | `BillingOverviewPage`；运行四卡 + 趋势 + 健康 + **MC512**；**商业运营六宫格**入口 |
| 计费与账务 | 计费 | `billing.pricing` | ~~定价与策略~~ | `/billing/pricing` | **重定向** → `/billing/overview`（运营台已移除 **FR-MC502** 配置页；Token 费率由所内 keys/服务维护） |
| 计费与账务 | 计费 | `billing.operations` | 商业运营 | `/billing/operations` | `BillingOperationsPage`（`?tab=` subscriptions \| packs \| rules \| orders \| consumption） |
| 计费与账务 | 计费 | `billing.commerce` | ~~订阅与能力包~~ | `/billing/commerce` | **重定向** → `/billing/operations?tab=rules`（MC509 目录/场景映射迁入 **计费规则** Tab） |
| 计费与账务 | 计费 | `billing.ledger` | 执行核销追踪 | `/billing/ledger` | `BillingLedgerPage`（**可选** `?tab=` `ledger` / `correlate`、`?q=` 单笔预填）
| 日志与监控 | 检索 | `obs.traces-logs` | 执行链路协查 | `/observability` | `ObservabilityPage`：五 Tab + 联合筛选 + 协查抽屉 · **无** 页内 SLI 看板 · 见 [`observability-reconciliation`](../domains/admin/observability-management/admin-console-observability-reconciliation.md) §0 |
| 日志与监控 | ~~健康~~ | `obs.health` | ~~运行健康~~ | `/observability/runtime-health` | **重定向** → `/observability`（**Demo 无** FR-MC805 SLI 区块） |
| 日志与监控 | ~~告警~~ | `obs.alerts` | ~~告警~~ | `/observability/alerts` | **重定向** → `/observability` |
| 全局参数 | ~~交易 keys~~ | `sys.trading-config` | ~~平台默认策略 / 全局交易参数~~ | `/trading-config` | **重定向** → `/access`（**无独立页**；keys 见 `trading-agent-config`） |
| 全局参数 | 渠道 | `sys.channels` | 渠道管理 | `/system/channels`、`/system/channels/:channelId` | `ChannelConfigPage`（列表 + 分渠道详情：Telegram / Discord / WhatsApp 等） |
| 全局参数 | 模型 / 网关 | `ai.settings` | 模型配置 | `/ai-settings` | `AiSettingsPage`（Tab：**厂商与模型**（展开维护下属模型；新建合并接入底座与展示名、`providerId` 后台生成；模型仅从预置清单选）/ **使用策略**（模型下拉仅用台账启用模型）；**演示**非生产，契约真源 **`ai-settings/overview.md` §1.1** + **`admin/ai/*`**） |

## 重定向

| From | To |
|------|-----|
| `/` | `/runtime/executions` |
| `/agents/templates` | `/agents/instances` |
| `/agents/templates/:templateId` | `/agents/instances` |
| `/agents/config/:configId` | `/agents/instances` |
| `/agents/config` | `/agents/instances` |
| `/prompts` | `/prompts/strategy` |
| `/prompts/system` | `/prompts/strategy` |
| `/prompts/scenarios` | `/prompts/strategy` |
| `/tools` | `/ai/tool-registry` |
| `/tools/registry` | `/ai/tool-registry` |
| `/ai/tool-policies` | `/ai/tool-registry` |
| `/integrations` | `/system/channels` |
| `/integrations/telegram` | `/system/channels/telegram` |
| `/integrations/exchange-apis` | `/system/channels` |
| `/integrations/llm-providers` | `/ai-settings` |
| `/access/eligibility` | `/access` |
| `/trading-config` | `/access` |
| `/observability/runtime-health` | `/observability` |
| `/observability/alerts` | `/observability` |
| `/billing` | `/billing/overview` |
| `/runtime/tasks` | `/runtime/executions` |
| `/runtime/events` | `/runtime/executions` |
| `/system/feature-flags` | `/runtime/executions` |
| `/system/global-gate` | `/runtime/executions` |
| `/system/contract-closure` | `/runtime/executions`（**无** `sys.contract-closure` 索引页；契约收口派工见 [`contract-closure` §5.2.6](../../contract-closure.md#cc-526-progressive-order)；速链 [**`closure-remaining` §0**](../../closure-remaining.md#closure-remaining-quicklinks)） |

## 与侧栏

实现：`src/admin/src/layout/adminNavCatalog.ts`、`sideMenu.tsx`、`src/admin/src/copy/adminNaming.ts`。
