# Admin Console — 后台信息架构（IA）

本目录是 **管理后台视图层 / 映射层** 的事实入口：**Runtime Semantics → 运营可操作的页面与导航**。  
**不替代** `[domains/admin/](../domains/admin/README.md)` 中的业务能力与 FR 条文；也不在本文重复 Runtime 语义 SSOT — **Runtime** 仍以 `[Runtime/overview.md](../Runtime/overview.md)` 为准。

**契约收口 / MR 派工**：[`contract-closure.md`](../contract-closure.md)；**缺锚首节** [**`closure-remaining` §0 速链**](../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../closure-remaining.md#cc-exec-solve-path)。

## 为何独立目录


| 层级                                           | 职责                           |
| -------------------------------------------- | ---------------------------- |
| `Runtime/`、`domains/agent/`、`domains/admin/` | 运行时与域 **语义 / 契约**            |
| `**specs/requirements/admin-console/`（本目录）** | **菜单 IA、页面清单、Runtime→UI 映射** |
| `src/admin/`（实现）                             | 在 IA 收口后 **按映射生成原型与页面**      |


## 推荐顺序（当前阶段）

1. **[Sitemap](sitemap.md)** — 先定菜单与页面清单，不搞高保真。
2. **[Runtime → UI Mapping](runtime-to-ui-mapping.md)** — 概念与可操作页面对齐。
3. **低保真原型** — 仅 P0→P2 所列页面顺序。
4. **再** 基于本目录 IA 让工具生成 UI — **而非**直接从 Domains 长文推导导航。

## 当前目标一句话

把 **Runtime 概念**映射成 **运营可观测、可操作的页面**（可视化执行与异常；**执行详情 Timeline** **与** [`observability` §2.4](../observability/overview.md) **`transitionTrigger`/`SC-OM-04`** **见** [`runtime-to-ui-mapping.md`](runtime-to-ui-mapping.md)），而非一次性「完整企业后台」。

## 本轮明确不做（防范围漂移）

以下 **不进入** 当前里程碑与低保真优先级：

- 用户中心（C 端画像式后台）
- 财务 / 账务后台完整建设
- 商户系统
- 完整 RBAC / 权限矩阵产品化
- Prompt Studio（高阶编排工作台）

## AI 治理：页面边界与交付建议

本节是 **产品/IA 收口建议**（与 [sitemap.md](sitemap.md) 叶子页、[prd-ia-alignment.md](prd-ia-alignment.md)、[`domains/admin/agent-management/config.md`](../domains/admin/agent-management/config.md) 一致），用于防「智能体」菜单膨胀与职责串味。

### 应放进「AI 治理」侧栏页的能力（Agent 配置 / Prompt / 工具 / 确认 + G01）

「AI 治理」回答：**实例与能力目录、Prompt 治理与合规边界、场景与策略（`scenarioId`、执行策略 Tab）与确认门如何约束**（**不含** **Infra 级** Provider/密钥/模型目录台账；**Agent Runtime 模型策略**见下「模型配置」）。

| 归类 | 典型能力 | 文档锚点 |
|------|----------|----------|
| （多租户预留） | Template 默认包；当前 **Demo** 不显式交付 | PRD 模块一 · 旧路由重定向 **`/agents/instances`** |
| 实例管理 | 实例列表、详情 | PRD 模块一 · **`/agents/instances`** · 对齐 [`agent-instances-reconciliation`](../domains/admin/agent-management/admin-console-agent-instances-reconciliation.md) §0 |
| 提示词 | **提示词治理** + **安全防护**（SAFETY）独立页 | PRD 模块二 · `prompt-management/*` · 对齐 [`prompt-strategy-reconciliation`](../domains/admin/prompt-management/admin-console-prompt-strategy-reconciliation.md) §0 |
| 技能与工具 | **`/ai/tool-registry`**（`ai.tool-registry`）· 对齐 [`tool-registry-reconciliation`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) §0；PRD 模块三 · `tool-management/*` |
| 运行场景 | **场景目录**（`scenarioId`）+ **执行策略**（`ai.runtime-orchestration`） | `domains/agent/agent-orchestration/*` |
| 人工确认 | 确认规则入口（表单可分期落地） | `risk/*`、`hitl` 相关 SSOT |
| 横向 | **G01 全局门禁**（`GLOBAL_AGENT_SWITCH` 等；**无** Demo 独立页，叙事见 agent-management / Runtime） | `agent-management/config.md` §1.1 |

**模型配置**：统一在 **[全局参数](sitemap.md#全局参数)** · **`ai.settings`**（`/ai-settings`）— **Demo** **两 Tab**：**厂商与模型**（台账）+ **使用策略**（Runtime 模型策略：**模型下拉选项绑定**上一 Tab **启用台账**，见 [`domains/admin/ai-settings/overview.md`](../domains/admin/ai-settings/overview.md) §1.1）；**不是**「仅策略表单」替代 Infra OpenAPI。

**触达渠道（渠道管理 / Agent Interaction Channel）**：统一在 **[全局参数](sitemap.md#全局参数)** · **`sys.channels`**（`/system/channels` 列表 + `/system/channels/:channelId` 详情）。**不设**一级「外部对接」；**不设**独立「交所接口配置」运营页；**大模型 Infra 接入**归平台网关，**与**本页 **Runtime 策略**拆面。

### 不放进「AI 治理」独立页的能力（收口到其它一级导航或真源）

| 能力 | 归口 |
|------|------|
| 修改 `GLOBAL_AGENT_SWITCH` **真源** | **agent-management**、**design/api**、配置 bundle（**`src/admin` Demo** **无**总闸页） |
| 计费改价、流水、单笔协查主屏 | **计费与账务** |
| 深度观测、联合检索、告警闭环主屏 | **日志与监控** |
| **Agent Runtime 模型策略**（主入口 · Demo） | **全局参数** · **模型配置**（`ai.settings`） |
| **平台模型目录、Provider、网关地址、密钥与 KMS** | **平台 Infra / AI Gateway**（控制台形态可与 `ai.settings` OpenAPI 拆面；**不**以本 Demo 页为台账真源） |
| 密钥 **明文**、Secret 本体 | **不**进运营 UI（`secretRef` 等见域规格与 Infra 流程） |
| 工具 OpenAPI **矩阵终裁**真源 | 以 `design/api.md` 与各域契约为准；控制台 **单页** 以列表 + 策略 Tab **可解释呈现** |
| Runtime 单独一级菜单、Agent 日志一级聚合 | **不设**：与 [`agent-management/config.md`](../domains/admin/agent-management/config.md) §1 **「明确不做」** 一致 |
| **`ai.tool-registry` 技能与工具运营页** | **原型 SSOT** [`admin-console-tool-registry-reconciliation.md`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md)；**非**生产 Registry API / **非** Runtime Publish UI；Prompt 门禁在 **提示词治理** |

### V1 交付顺序（与优先级一致，可迭代实现）

1. **先**：**运行运营**（执行记录 + **执行详情**「内嵌 Queue / Events」）+ **模型配置**（至少 **可读**），保证可查、可止血（**Runtime traceability**，非基础设施大盘）。
2. **再**：**实例管理**、**运行场景**、**提示词治理** + **安全防护**、**技能与工具**（见 [sitemap.md](sitemap.md)）。
3. **人工确认规则**：与交易写路径强相关时 **做全或不进可执行环境**。

与 [sitemap.md](sitemap.md) 中 P0/P1/P2 表述可同时使用。

### IA 与交互承诺

- **不设** 一级 `/agents/runtime`；编排执行收口 **`runtime.execution-detail`**。
- **不设** 一级 `/agents/logs`；聚合检索走 **日志检索**。
- 实例与 Template 收口用 **单列实例**（单租户 **`/agents/config`→`/agents/instances`**）；**技能与工具** 见 **`/ai/tool-registry`**（旧 `/tools/*` **重定向**，见 `demo-routing.md`）；**场景与策略** 为 **运行场景**页（只读/demo 可先上）。
- **执行记录 / 执行链路协查 / 执行核销**：分别见 [`runtime-executions-reconciliation`](../domains/admin/observability-management/admin-console-runtime-executions-reconciliation.md) §0、[`observability-reconciliation`](../domains/admin/observability-management/admin-console-observability-reconciliation.md) §0、[`billing-reconciliation`](../domains/admin/billing-management/admin-console-billing-pages-reconciliation.md) §0。
逐页低保真块见 [page-specs.md](page-specs.md)「AI 治理」节。

## 文档索引

| 文档 | 说明 |
|------|------|
| [sitemap.md](sitemap.md) | 一级导航结构与页面 ID；**页面中文名摘要** |
| [naming-alignment.md](naming-alignment.md) | **命名 v3 SSOT**：模块/功能/页面；**侧栏与页眉中文** |
| [runtime-to-ui-mapping.md](runtime-to-ui-mapping.md) | Runtime 概念 ↔ 页面 |
| [prd-ia-alignment.md](prd-ia-alignment.md) | PRD §3 八大模块 ↔ 本 IA |
| [delivery-plan.md](delivery-plan.md) | 阶段、出口、变更门禁 |
| [api-surface.md](api-surface.md) | 页面 ↔ OpenAPI / TBD |
| [demo-routing.md](demo-routing.md) | 页面 ID ↔ `src/admin` 路由 |
| [page-specs.md](page-specs.md) | 逐页低保真信息块与筛选 |



