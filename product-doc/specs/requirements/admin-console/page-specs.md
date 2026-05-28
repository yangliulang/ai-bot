# 逐页规格（低保真）

与 [`naming-alignment.md`](naming-alignment.md) **v3 显示名**、[sitemap.md](sitemap.md) **页面 ID** 对齐。

## `runtime.executions` — 执行记录（Runtime MVP · 主列表）

**对齐 SSOT（原型 ↔ 文档）**：[`observability-management/admin-console-runtime-executions-reconciliation.md`](../domains/admin/observability-management/admin-console-runtime-executions-reconciliation.md) **§0**。

**实现**：`ExecutionListPage` · `ExecutionListFilters` · `ExecutionListTableBlock` · `opsPanelHints.EXECUTION_LIST`。

| 块 | 内容 |
|----|------|
| **目的** | **execution 主实体** 的运营检索列表（**默认落地页** `/` → 本页） |
| **默认列** | `executionId`、**`userIdMasked`（用户 UID）**、**`scenarioId`（场景 ID）**、**`intent`（意图摘要）**、`status`（运行状态）、`currentStage`（当前阶段）、**`outcome`（业务终态）**、`retries`、`createdAt` |
| **筛选（URL）** | **`q`**（用户/执行 ID/场景 合并关键字）· **`intent`** · **`scenario`** · **`status`** · **`from`** / **`to`**（`createdAt` 日期窗） |
| **行交互** | **单击行** → 右侧 **预览抽屉**（摘要、工具摘录、链 **执行详情** / **执行链路协查**）；「预览」「详情」按钮 |
| **API（可选）** | `VITE_USE_OBSERVABILITY_API` + `VITE_API_BASE_URL` → `listObservabilityExecutions`；**cursor 加载更多**；合并检索规则见 `EXECUTION_LIST.apiEnabledTechnical` |
| **EMPTY** | 无数据时引导放宽筛选 |
| **MVP 约束** | **不**拆 **任务队列 / 运行事件** 独立运营页；旧路径重定向见 `demo-routing.md` |
| **与协查分工** | 单条深度 Timeline/多 Tab 检索 → **`obs.traces-logs`**（[`observability-reconciliation` §1](../domains/admin/observability-management/admin-console-observability-reconciliation.md)） |

## `runtime.execution-detail` — 执行详情（内嵌 Queue / Events）

**对齐 SSOT**：[`admin-console-runtime-executions-reconciliation.md`](../domains/admin/observability-management/admin-console-runtime-executions-reconciliation.md) **§1**。

| 块 | 内容 |
|----|------|
| **定位** | **Runtime traceability** 主入口：回答「为什么这条 execution 失败/卡住」 |
| **总览** | 主属性 + **场景 · Runtime 技能范围**（同窗运行场景 Skill Scope）+ **Prompt 拼装追溯**（**SC-PM-22**）+ **技能规范**（**`agent.skill.spec_read`** · **SC-OM-05**）+ **Canonical Inspector（演示）**（`canonicalOp` / payload / 确认快照 / Gateway 四断言 · `executionGatewayWriteBarrier`）+ 工具 / LLM / **计费镜像** |
| **时间线** | **Execution stages**（`Steps`：CREATED → …）+ **精细信号** `Timeline`（**`FR-MC801`**）；**写路径演示** **须** 含 **`agent.skill.spec_read`**（**早于** **类型 A**）— [`skill-specs/production-runtime` §4](../skill-specs/production-runtime.md)；**若 API 返回** **`transitionTrigger`** **须** **可读** — **`SC-OM-04`**、**`SC-OM-05`**、[`observability` §2.4](../observability/overview.md) |
| **任务队列** | 挂在本 execution 的调度单元表 |
| **运行事件** | `tool.*` / `retry.*` 等摘录 |
| **Retries** | 重试历史（演示）；与 orchestration 对签后接真数据 |
| **Recovery** | MVP 占位 + 链 **执行链路协查** |
| **操作** | 「重试」（TBD）、「打开日志检索」 |
| **URL** | 可选 **`?tab=`** = `overview` \| `timeline` \| `queue` \| `events` \| `retries` \| `recovery` |
| **BFF（联调）** | 开启 Observability 接入（Demo：`VITE_USE_OBSERVABILITY_API` + `VITE_API_BASE_URL`）时：**摘要行** 用 **`GET /api/v1/admin/observability/executions`**（`executionId` + `pageSize`，mock 无该行时补一行）；**FR-MC801 时间线** 用 **`GET /api/v1/admin/observability/executions/{executionId}/timeline`**。与 OpenAPI / Demo 对齐见 `src/admin/src/api/observabilityExecutions.ts`。 |

## `ai.agents-instances` — 实例管理

**对齐 SSOT**：[`agent-management/admin-console-agent-instances-reconciliation.md`](../domains/admin/agent-management/admin-console-agent-instances-reconciliation.md) **§0**。

**正式 FR 列/筛选全集**：[`agent-management/config.md`](../domains/admin/agent-management/config.md) **§3.1**；**Demo 列表列收窄** 以 **本篇 + reconciliation §0** 为准。

| 块 | 内容 |
|----|------|
| **路由** | `/agents/instances` · 详情 `/agents/instances/:instanceId`；旧 **`/agents/config`**、**`/agents/templates`** → 重定向 |
| **G01** | 页顶 **`AgentGlobalGateBanner`**（OFF 禁用 Start/Resume；批量 Pause/Stop **仍可用**） |
| **列表列（Demo）** | 实例 ID · 用户 UID · 运行状态（门禁+原因）· 实例状态（机电态）· 最近活跃 · 操作（预览/详情/协查） |
| **列表无列（Demo）** | 模板 · 渠道 · 子账户 → **仅详情** |
| **筛选** | 关键字 **`q`**（或旧 `user`/`id`）· URL **`gate`** / **`rt`**；增补用户 UID、最近活跃区间（**会话内**） |
| **批量** | 多选 → **批量 Pause / Stop**（**R06** 演示） |
| **导出** | **I08** 演示 Modal |
| **预览抽屉** | 实例 ID + userId → 详情 / observability 深链 |

## `ai.prompt-strategy` — 提示词治理

**对齐 SSOT**：[`prompt-management/admin-console-prompt-strategy-reconciliation.md`](../domains/admin/prompt-management/admin-console-prompt-strategy-reconciliation.md) **§0～§1**。

**治理模型（MUST）**：[`prompt-management/config.md` §1.1b](../domains/admin/prompt-management/config.md) · [`prompts/governance-map.md`](../prompts/governance-map.md) · [`product/prompt-governance-checklist.md`](../../product/prompt-governance-checklist.md)。

| 块 | 内容 |
|----|------|
| **路由** | `/prompts/strategy`（列表+编辑器）；`/prompts/safety` · **`ai.prompt-safety`**（SAFETY 类 **不在** 本列表） |
| **页顶** | `PromptGovernanceIntro`；Tag 数据源（本地/API/补齐） |
| **筛选 URL** | **`q`**（兼容 `id`/`title`）· **`kind`**（治理类型）· **`life`**（生命周期）· **`pack`**（详情抽屉） |
| **列表列** | Prompt ID · 名称 · 类型 · 版本/草稿/生效 · 状态 · **Runtime 技能范围** · **阶段** · 更新时间 · 操作 |
| **行交互** | 行点击 / 「详情」→ **`?pack=`** 抽屉；「编辑」→ `/prompts/strategy/:id/edit` |
| **编辑器** | `scenarioId` + `skillSpecRef` **只读**；**发布门禁**（**SC-PM-21**）；**发布校验追溯**；**拼装追溯**（**SC-PM-22**）；**禁止** UI 叙事 **Prompt = Skill 宿主** |
| **API** | 可选 `VITE_USE_PROMPT_API`；远端缺包时 mock **补齐 16 包** |

## AI 治理（其它页）

**边界、不纳入本组的职责、V1 交付顺序**：见 [README.md](README.md)（与 [`agent-management/config.md`](../domains/admin/agent-management/config.md) §1 对签）。**模型配置**主入口在 **全局参数**（`ai.settings`，`/ai-settings`）：Demo 为 **两 Tab** — **厂商与模型**（厂商行展开；**新建厂商**表单 **「厂商」** 合并 **接入底座 + 展示名**；**`providerId` 不展示**；**添加模型** 仅从底座预置清单选、`modelId` 全局唯一）与 **使用策略**（默认 / 分场景 / 降级等 **模型下拉仅引用台账内「启用厂商 × 启用未弃用模型」**，台账变更导致失效时自动校正）；**生产台账与 OpenAPI** 仍以 [`ai-settings/overview.md`](../domains/admin/ai-settings/overview.md) **§1.1** 与 **`design/api.md`** **`admin/ai/*`** 为 SSOT。

- **运行场景（`ai.runtime-orchestration`）**：`/ai/runtime-orchestration`，页眉 **运行场景**；Tab **场景目录**（含 `scenarioId` 筛选/深链 **`?scenario=` 自动打开详情**）、**执行策略**；场景详情抽屉 **Runtime 技能范围（只读）** — 主 write Skill · 登记册状态 · 场景策略 Prompt 包 / 发布门禁指针（**≠ Prompt 托管 Skill**）；列表列 **技能范围**；可选 URL `?tab=routing|policy`、`?scenario=`。
- **技能与工具**：见下节 **`ai.tool-registry`**（对齐 SSOT [`tool-management/admin-console-tool-registry-reconciliation.md`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) **§0**）。
- **人工确认规则**：`risk/hitl-and-automation-matrix.md` 等；表单 TBD。

## `ai.tool-registry` — 技能与工具

**对齐 SSOT（原型 ↔ 文档）**：[`tool-management/admin-console-tool-registry-reconciliation.md`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) **§0～§2**。

**需求**：[`tool-management/functions` FR-TM06](../domains/admin/tool-management/functions.md)、**SC-TM-13～19**；[`skill-specs/requirements-closure` §3.6](../skill-specs/requirements-closure.md#36-runtime-publish--原型与规格对齐非生产实现)、[`PUBLISH.md` §7.1](../skill-specs/PUBLISH.md#71-admin-原型--交付边界srcadmin)。

**路由**：`/ai/tool-registry` · `pageId` **`ai.tool-registry`**。旧 **`/tools/*`**、**`/ai/skill-specs`**、**`/ai/tool-policies`** → 本页（[`demo-routing.md`](demo-routing.md)）。

**实现文件**：`ToolRegistryPage` · `SkillRegistryTable` · `SkillOperationDrawer` · `SkillOperationOverview` · `skillRegistryCatalog` · `skillRegistryUiCopy`。

| 块 | 内容 |
|----|------|
| **页眉** | Tag **可下单技能** · **预览环境**；说明 + **恢复默认开关**（重置启用态与变更记录） |
| **统计** | **可下单技能 · 已启用** x/14 · **查询与外部工具 · 已启用** x/n · **开关变更记录** 条数 |
| **Tab · 可帮用户下单** | A 类表 + **搜索**（名称/流程/下单方式）；列见下表 |
| **Tab · 查询类 / 外部检索** | B/C 类工具表 |
| **Tab · 变更记录** | 启用/停用审计表（时间 · 类型 A/B/C · 名称 · 变更 · 操作人） |
| **抽屉** | **概览** · **对话与下单要求**；底栏复制技能编号；**无** Runtime 发布按钮 |

**A 类列表列**：技能（摘要 + `skillId`）· 用户怎么用 · 实际下单方式 · 适用场景（链运行场景）· 是否启用（**localStorage** · **SC-TM-16**）。**行点击** 打开抽屉（Switch 不触发行点击）。

**B/C 列表列**：工具 · 能做什么 · 状态（**已开放** / **暂未开放** / **规划中**）· 是否启用。

**抽屉 · 概览**：技能编号、规范版本、主场景、能力开放、预览启用、规范完整度；**适用 scenarioId 列表**；业务说明；必填/校验/确认/拒答指标与片段预览。

**抽屉 · 对话与下单要求**（**SC-TM-14**）：Segmented — **需要的信息** · **校验规则** · **确认内容** · **待澄清** · **不予办理** · **对接交易所**；可折叠 **Git 原文（研发对照）**。

**刻意不展示**：新建技能、**Runtime 已发布 x/n**、页顶 **说明就绪**（后者在 **运行场景** 抽屉）；**SC-TM-17～18** 归所内 MR-B（Vitest `skillPublish/*` 仅契约对签）。

**与 Prompt 分工**：Skill §1～§6 **在本页**；Prompt **仅** **`skillSpecRef` 发布门禁**（**SC-PM-21** · `promptPublishGate`）。

## 计费与账务（模块五 · 闭环七入口）

**轨 B 梳理（目标 / Demo 缺口 / 优先级）**：[`domains/admin/billing-management/admin-console-billing-pages-reconciliation.md`](../domains/admin/billing-management/admin-console-billing-pages-reconciliation.md)。

**侧栏 IA（`src/admin` · 2026-05-27）**：**三项** — **`billing.overview`** 计费总览 · **`billing.operations`** 商业运营 · **`billing.ledger`** 执行核销追踪。旧书签 **`/billing/pricing`** → overview；**`/billing/commerce`**、**`/billing/subscriptions`** 等 → **`/billing/operations?tab=…`**（见 [`demo-routing.md`](demo-routing.md)）。

**`billing.overview`**：角色分工 Alert；**商业运营六宫格**入口（含链 ledger）；**Runtime Usage** 四卡 + **7 日执行趋势**（分析/交易/Monitoring）；**MC501/506** 健康（`BILLING_MODE`、网关错误表）；**MC512** 配额阻断汇总（`PHASE2_COMMERCE_RAILS_ENABLED` 关时启用指引）。**不含** Usage Breakdown、商业到账四卡、页底 Capability 桶快照（mock 字段仍可对读，UI 未展示）。

**`billing.operations`**（`?tab=`）：**订阅套餐** · **资源管理**（可售资源 CRUD）· **计费规则**（扣减规则 + 场景映射双 Tab；session 可编辑显式映射/扣减；前缀/兜底只读；**FR-MC509** 目录 **PATCH + 双签** 在规则 Tab 内 **`CommerceCapabilityCatalogEditor`**）· **订阅订单**（`OrdersPanel` · Crypto 只读、筛选；**`CommerceOrderDetailDrawer`** 四段：**订单信息** / **支付信息**（含 **用户支付地址** 完整可复制 · 支付截止 · 链上确认）/ **链上到账**（付款方地址 · 交易哈希 · PSP）/ **权益入账**；pack-grant 演示按钮；字段 SSOT **[`admin-console-billing-pages-reconciliation` §3.2.1](../requirements/domains/admin/billing-management/admin-console-billing-pages-reconciliation.md)**）· **用户消耗**（MC510 协查）。页间深链 `?userId=` / `?sku=`。**运营台无 `billing.pricing` 页**；**FR-MC502** Token 费率由所内 **keys/服务** 维护，总览仅 **Token 今日消耗** 观测。

**`billing.ledger`**：Tab **核销列表** / **单笔追踪**；主筛 **executionId**、用户、**capabilitySkuId**、**核销状态**、执行状态；主列 **ENTITLEMENT_DEBIT**；`idempotencyKey` 等 **行展开**；链执行详情 / observability。**可选** `VITE_USE_BILLING_COMMERCE_API` · `VITE_USE_BILLING_LEDGER_API`（dev BFF · 失败回退 mock）。**执行详情总览**：核销摘要卡（Capability、核销状态、`billingTraceId`、链 ledger）。**MR-BILL** staging：[`staging-mr-bill-runbook.md`](../domains/admin/billing-management/staging-mr-bill-runbook.md)。

## `obs.traces-logs` — 执行链路协查

**对齐 SSOT**：[`observability-management/admin-console-observability-reconciliation.md`](../domains/admin/observability-management/admin-console-observability-reconciliation.md) **§0～§2**。

**实现**：`ObservabilityPage` · `opsPanelHints.OBSERVABILITY` · `Mc801TimelineAudit`。

| 块 | 内容 |
|----|------|
| **路由** | `/observability` · `obs.traces-logs` |
| **重定向** | `/observability/runtime-health`、`/observability/alerts` → 本页（**无** 独立「运行健康」「告警」Demo 页） |
| **顶栏筛选** | 执行 ID · 用户 UID · 计费链路 ID（`traceId` / `traceKey`）· **应用检索** / **复制链接** |
| **Tab** | 执行 · 工具调用 · 大模型 · 计费 · 审计（`?tab=execution|tool|llm|billing|audit`） |
| **时间线区** | 单 execution 锁定或列表筛至一条时：**叙事时间线** + **FR-MC801** 表 |
| **协查抽屉** | 执行 ID 点击 → 工具/Prompt/LLM/风控摘要 + 链 **执行详情** |
| **刻意无（Demo）** | **FR-MC805 SLI 卡片**、堆积/错误率大盘（**P2/MR** 或外链 Grafana） |

## 准入与风控

- **`access.overview`（准入管理，`/access`）**：单页集中灰度、名单、封禁、实名镜像、VIP 门槛等；**不包含**输入用户 ID 查询是否具备资格的运营功能（叙事与运行时评估仍见 `access-control/eligibility-runtime.md`）。

## 全局参数

| 页 | 说明 |
|----|------|
| 全局交易参数 | **PRD 模块七**；**Demo**：`/trading-config` **重定向** → `/access`，**无**独立运营页（keys 叙事仍见 `trading-agent-config`）；**含** **keys §2.1 Memory/STM** **（bundle/API · 无 Demo Tab）** |
| **模型配置** | PRD **模块四** · `ai.settings` · `/ai-settings` · **Demo**：**厂商与模型**（展开子表；厂商表单合并底座与名称；模型从预置清单接入 · `modelId` 全局唯一）+ **使用策略**（模型类下拉绑定台账可用集；默认/分场景、Token、降级、RPM）；**生产**仍以 **`ai-settings/overview.md` §1.1**、OpenAPI **`admin/ai/*`** 为准。 |
| **渠道管理** | `sys.channels` · `/system/channels` **（Agent Interaction Channel 列表）** + `/system/channels/:channelId` **分渠道详情**（业务字段：状态、规模演示、Bot/Webhook/语言/菜单/权限等；**不**以 configKey 为主表）；Telegram 契约见 [`admin/telegram-channels.yaml`](../../openapi/admin/telegram-channels.yaml)；**不设**独立「交所接口配置 / 大模型接入」运营页（后者归 **模型配置**） |
