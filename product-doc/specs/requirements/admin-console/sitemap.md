# Admin Console — Sitemap

**状态**：IA v3 · 与 **`src/admin` Demo** 路由同步（见 [`demo-routing.md`](demo-routing.md)）。  
**命名 SSOT**：[`naming-alignment.md`](naming-alignment.md) **v3**（侧栏 **纯中文**）。  
**原则**：先 **菜单与页面存在性**，再交互与高保真。

## 一级导航（结构与模块名）

```text
Admin Console
├── 运行运营
├── AI 治理
├── 准入与风控
├── 计费与账务
├── 日志与监控
└── 全局参数
```

## 二级页面（叶子路由）

以下为 **页面 ID · 页眉/侧栏显示名**；详表见 [naming-alignment.md](naming-alignment.md)。

### 运行运营

| 页面 ID | 页面名称 |
|---------|----------|
| `runtime.executions` | 执行记录 |
| `runtime.execution-detail` | 执行详情（仅路由；**内嵌** Overview / **Timeline**（**`transitionTrigger`/§2.4** **同窗** [`runtime-to-ui-mapping.md`](runtime-to-ui-mapping.md)）/ Queue / Events / Retries / Recovery） |

### AI 治理

| 页面 ID | 页面名称 |
|---------|----------|
| `ai.agents-instances` | 实例管理 |
| `ai.prompt-strategy` | 提示词治理 |
| `ai.tool-registry` | 技能与工具（A/B/C 登记 · 抽屉规范 · Enable/审计） |
| `ai.runtime-orchestration` | 运行场景 |
| `ai.confirmation-rules` | 人工确认规则 |
| `ai.prompt-safety` | 安全防护 |

**说明**：`/agents/config`、旧 `/agents/templates` 路由 **Demo 现状**为重定向 → **`/agents/instances`**（单租户阶段无独立「模板」运维面；多租户时再接 Template）。**`ai.tool-registry`**：详见 [`tool-management/admin-console-tool-registry-reconciliation.md`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) **§0**；旧 **`/tools/*`** → 同页。

### 准入与风控

| 页面 ID | 页面名称 |
|---------|----------|
| `access.overview` | 准入管理 |

### 计费与账务

| 页面 ID | 页面名称 |
|---------|----------|
| `billing.overview` | 计费总览（运行观测 + 商业运营入口 + MC512 摘要） |
| `billing.operations` | 商业运营（Tab：订阅套餐 / 资源管理 / 计费规则 / 订阅订单 / 用户消耗） |
| `billing.ledger` | 执行核销追踪（Tab：核销列表 / 单笔追踪） |

**遗留 pageId（无侧栏）**：`billing.pricing` · `billing.commerce` — 路由 **重定向**，见 [`demo-routing.md`](demo-routing.md)。

### 日志与监控

| 页面 ID | 页面名称 |
|---------|----------|
| `obs.traces-logs` | 执行链路协查 |

**说明**：`obs.health`、`obs.alerts` **无** Demo 侧栏入口；旧路径 **重定向** → `/observability`（**页内无** FR-MC805 SLI 看板），见 [`demo-routing.md`](demo-routing.md) · [`observability-reconciliation`](../domains/admin/observability-management/admin-console-observability-reconciliation.md) §0。

### 全局参数

| 页面 ID | 页面名称 |
|---------|----------|
| `sys.trading-config` | 全局交易参数（**Demo**：无独立页，`/trading-config` → `/access`） |
| `sys.channels` | 渠道管理 |
| `ai.settings` | 模型配置 |

## 实施优先级（与产品一致）

### P0

- **执行记录**、`runtime.execution-detail`（队列 / 事件等 **仅** 在详情内嵌）

### P1

- **`ai.settings`**（模型配置，菜单位于全局参数）

### P2

- **触达渠道**在 **全局参数 · 渠道管理**（`sys.channels`）维护；**运行健康 / 告警** **无**独立 Demo 页，并入 **执行链路协查**（`/observability`）

## 与 `src/admin/`

**执行详情 · Timeline**：**`FR-MC801`** **响应** **若含** **`transitionTrigger`** **须** **在 UI 可读**（**`SC-OM-04`**）；**映射 SSOT** [`observability` §2.4](../observability/overview.md)、[`runtime-to-ui-mapping.md`](runtime-to-ui-mapping.md)。

侧栏与页眉与 **[naming-alignment.md](naming-alignment.md)** 同源；路由见 [demo-routing.md](demo-routing.md)。
