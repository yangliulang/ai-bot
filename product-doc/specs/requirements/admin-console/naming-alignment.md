# 后台命名对齐 — 模块 / 功能域 / 页面

**本文档**为 **运营侧显示名** SSOT：**侧栏分组**、**页眉主标题** 以此为准。**页面 ID**（`*.x.y`）为稳定技术键；**不**随文案润色频繁改动（新增/弃用见变更说明）。

## 命名约定（v3）

| 触点 | 规则 |
|------|------|
| **侧栏一级（模块）** | **仅用中文**，偏 **交易所后台习惯用语**。 |
| **侧栏叶子（页面）** | **仅用中文**，4～8 字为主。 |
| **页眉 `Title`** | **中文**；`页面 ID` 放副标题 / `Text code`。 |
| **英文 / PRD / OpenAPI** | 见 **英文参考列**或子域正文；**不**进 Demo 菜单主文案。 |

## 三层定义

| 层级 | 含义 | 典型出现位置 |
|------|------|----------------|
| **后台模块** | 侧栏一级分组 **6** 组 | Antd Menu `group` |
| **功能域** | 模块下能力簇（文档/培训）；侧栏仍为扁平叶子 | 本子域、`sitemap` |
| **页面** | 路由级屏 | 菜单叶子、`Title` |

## 总表（模块 → 功能域 → 页面）

### 1. 运行运营

| 模块（侧栏中文） | 功能域（说明） | 页面 ID | 侧栏 / 页眉显示名 | 英文参考 |
|------------------|----------------|---------|---------------------|----------|
| 运行运营 | 编排 / 执行可见性 | `runtime.executions` | 执行记录 | Executions（主列表） |
| 同上 | 单条执行 | `runtime.execution-detail` | 执行详情（**内嵌** Overview / **Timeline**（**`FR-MC801` · `transitionTrigger`** **见** [page-specs](page-specs.md)）/ Queue / Events / Retries / Recovery） | Execution detail |

**说明（Trading Runtime MVP）**：**execution 为主实体**；任务队列与运行事件 **不** 拆独立运营页（避免按技术组件割裂信息），统一在 **执行详情** 分块查看；旧路径 `/runtime/tasks`、`/runtime/events` **重定向** 至执行列表。待 **Runtime Platform**（多 scheduler / 大规模队列与事件总线等）再评估独立 Queue Console / Event Stream Console。

**（非侧栏）**：`runtime.tasks`、`runtime.events` 页面 ID **不在 MVP 导航登记**；若书签命中旧路由，实现侧重定向至 `runtime.executions`。

### 2. AI 治理

| 模块（侧栏中文） | 功能域（说明） | 页面 ID | 侧栏 / 页眉显示名 | PRD §3 |
|------------------|----------------|---------|---------------------|--------|
| AI 治理 | Agent 生命周期 | `ai.agents-templates` | （**Demo 不重定向占位 ID** · 旧书签 `/agents/config` 等→ **`/agents/instances`**；无单独页眉） | 一 |
| AI 治理 | Agent 生命周期 | `ai.agents-instances` | **实例管理** · 路由 `/agents/instances` | 一 |
| AI 治理 | Prompt（治理语义） | `ai.prompt-strategy` | **提示词治理**（列表 · `/prompts/strategy`） | 二 |
| AI 治理 | 安全合规用语 | `ai.prompt-safety` | **安全防护**（SAFETY 类 · `/prompts/safety`） | 二 |
| AI 治理 | Runtime 场景与策略 | `ai.runtime-orchestration` | **运行场景**（`/ai/runtime-orchestration` · Tab：**场景目录** + **执行策略**；对齐 agent-orchestration） | 横切 |
| AI 治理 | 确认 | `ai.confirmation-rules` | 人工确认规则 | 横切 |
| AI 治理 | Tool / Registry | `ai.tool-registry` | **技能与工具** | 三 |

**`ai.tool-registry` 补充**：Tab 可帮用户下单 · 查询类 · 外部检索 · 变更记录；抽屉 **概览** · **对话与下单要求**；**无** Runtime 发布页顶统计 — [`tool-registry-reconciliation`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) §0。

**弃用对外菜单名（实现可保留重定向）**：~~系统提示词~~ / ~~场景提示词~~（对应旧 `ai.prompt-system` / `ai.prompt-scenarios`）— 收敛为 **`ai.prompt-strategy`** 内 Tab，避免 Prompt Engineering 术语直出。

### 3. 准入与风控

| 模块（侧栏中文） | 页面 ID | 侧栏 / 页眉显示名 | PRD |
|------------------|---------|-------------------|-----|
| 准入与风控 | `access.overview` | 准入管理 | 六 |

### 4. 计费与账务

| 模块（侧栏中文） | 页面 ID | 侧栏 / 页眉显示名 | PRD |
|------------------|---------|-------------------|-----|
| 计费与账务 | `billing.overview` | 计费总览 | 五 |
| 同上 | `billing.operations` | 商业运营 | 五 |
| 同上 | `billing.ledger` | 执行核销追踪 | 五 |

**说明**：`billing.operations` **Tab**：订阅套餐 · 资源管理 · 计费规则 · 订阅订单 · 用户消耗。**`billing.pricing`**、**`billing.commerce`** 为 **遗留 pageId**（重定向，无侧栏）。`billing.ledger` 内 **Tab**：核销列表 · 单笔追踪（**仅权益核销 · 无 Token 退款 UI**）。**`/billing` 重定向** → `/billing/overview`。

### 5. 日志与监控

| 模块（侧栏中文） | 页面 ID | 侧栏 / 页眉显示名 | PRD |
|------------------|---------|-------------------|-----|
| 日志与监控 | `obs.health` | **（Demo 无菜单）** 旧路径重定向 → **`/observability`**；页面 ID 保留 | — |
| 同上 | `obs.traces-logs` | **执行链路协查**（`/observability`） | 八 |
| 同上 | `obs.alerts` | **（Demo 无菜单）** 旧路径重定向 → **`/observability`**；页面 ID 保留 | — |

### 6. 全局参数

| 模块（侧栏中文） | 页面 ID | 侧栏 / 页眉显示名 | PRD |
|------------------|---------|-------------------|-----|
| 全局参数 | `sys.trading-config` | **全局交易参数**（**Demo**：`/trading-config` **重定向** → `/access`，**无**独立页；页面 ID 保留） | 七 |
| 同上 | `sys.channels` | 渠道管理 | 触达/渠道 |
| 同上 | `ai.settings` | 模型配置 | 四 |

**说明**：`ai.settings`（`/ai-settings`）页眉 **模型配置**；页内 **Tab**：**厂商与模型**（Provider 与下属模型台账 · 一行展开）· **使用策略**（Runtime 模型策略：默认 / 分场景 / Token / 降级 / 限流等；**模型类控件可选集** 绑定 **厂商与模型** 台账中启用项 — 产品叙事见 [`../domains/admin/ai-settings/overview.md`](../domains/admin/ai-settings/overview.md) §1.1）。

## 与 PRD §3「模块一～八」

PRD **按交付域编号**，此处 **按运营导航**。对冲映射见 [prd-ia-alignment.md](prd-ia-alignment.md)。

## 变更流程

1. **先改本文档**，再同步 [sitemap.md](sitemap.md)、[demo-routing.md](demo-routing.md)、`src/admin/src/layout/adminNavCatalog.ts`、各页页眉。  
2. **[runtime-to-ui-mapping.md](runtime-to-ui-mapping.md)**：「主页面」列与 **显示名** 一致。
