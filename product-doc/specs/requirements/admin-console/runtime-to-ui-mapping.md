# Runtime → Admin UI Mapping

**目的**：把 **Runtime 语义**（SSOT 在 [`Runtime/`](../Runtime/overview.md)）落到 **运营可操作页面**，避免「懂 Runtime 但不知道点哪」的断层。

**页面显示名**与 **[naming-alignment.md](naming-alignment.md) v3**、侧栏、页眉一致。

**约定**：

- 左列：概念或能力（可与需求文档术语一致）。
- 右列：**中文显示名**（见 naming-alignment）。

## 核心映射表

| Runtime / 运营概念 | 主页面 | 页面职责（运营视角） |
|--------------------|--------|----------------------|
| **execution**（一次执行实例） | 执行记录 | 列表检索（**用户/场景/业务终态**、预览抽屉）、进入详情 — [`runtime-executions-reconciliation`](../domains/admin/observability-management/admin-console-runtime-executions-reconciliation.md) §0 |
| **execution**（单条详情） | 执行详情 | **内嵌** Overview（**含** **Production Runtime · 技能规范卡** · **`SC-OM-05`**）· **Timeline**（**`FR-MC801`**：**`transitionTrigger`** · **`agent.skill.spec_read`** **写路径** · **`SC-OM-04`/`SC-OBS11`**）· Queue · Events · Retries · Recovery；[`production-runtime` §4](../skill-specs/production-runtime.md) |
| **`read_skill_operation_spec`（写路径）** | 执行详情 · 总览 + Timeline | **非** 独立页；**协查** **Publish** → **技能与工具**；**规格** [`production-runtime.md`](../skill-specs/production-runtime.md) |
| **task**（调度单元） | 执行详情 · 队列 | **从属于** execution；MVP **不**做跨 execution 队列总览页（避免技术视角割裂） |
| **runtime event**（事件流） | 执行详情 · Events + 日志检索 | 单条摘录在详情；**全量** / 联合搜索走 FR-MC802 |
| **retry**（重试策略与操作） | 执行详情 · Retries | 重试历史；触发重试（权限内）待接 API |
| **UNKNOWN** / 异常终态 | 执行详情 | 标红、对账提示、链日志检索 |
| **monitoring**（执行堆积、迟滞） | 执行链路协查 + 执行记录 | **Demo**：**无** 独立 SLI 页（`obs.health` 重定向）；堆积/迟滞 **P2** 或外链 Grafana |
| **session** | 执行详情 / 执行记录 | 详情节点含 sessionId；列表可按需扩展列 |
| **freeze**（全局/租户冻结） | 执行记录 + **agent-management G01**（横幅/叙事） | **`src/admin` Demo** **无** `sys.global-gate` 独立页；冻结语义见 Runtime / agent-management |
| **lock**（并发锁） | 执行详情 | 待 API 暴露 |
| **recovery / reconciliation** | 执行详情 · Recovery + 执行链路协查 / 核销 | MVP Recovery 占位；对账链 **billing.ledger** |
| **persistence**（落库失败等） | 执行详情 + 日志检索 | 详情标错；下钻 traces |

## 与 Observability 的边界

| 数据类型 | 首选页面 | 说明 |
|---------|----------|------|
| 业务/runtime 事件（领域事件、状态迁移） | 执行详情 · Events + **日志检索** / **Timeline** | MVP **不**设独立「运行事件」侧栏；**全量**走日志检索。**主态边**：**`Timeline`** **同窗** **`transitionTrigger`/`SC-OM-04`**（见上表 **execution 详情**） |
| **主态迁移（Transition Contract）** | 执行详情 · **Timeline** | **`transitionTrigger`** **列** **或** **事件展开区** **二选一（** **IA 冻结** **）**；**禁止** **吞字段** |
| 分布式 trace / 多实体联合检索 | **执行链路协查**（`obs.traces-logs`） | 五 Tab + 协查抽屉；**FR-MC801** 同窗执行详情 — [`observability-reconciliation`](../domains/admin/observability-management/admin-console-observability-reconciliation.md) §0 |
| 聚合健康与告警（FR-MC805） | **Demo 未交付** | 旧 `/observability/runtime-health`、`/alerts` **重定向** 至协查页；SLI **P2/MR** |

## AI 与工具（跨 Runtime 但常从执行详情跳转）

| 概念 | 主页面 | 备注 |
|------|--------|------|
| Tool 调用记录 | 执行详情 | 嵌入时间线或子 Tab |
| Tool 策略 / 预算 · **技能与工具登记** | **技能与工具**（`ai.tool-registry`） | Demo：**14** A 类 + B/C 镜像；三卡统计；Tab 可下单（搜索）/查询/外部/变更记录；抽屉 **概览+对话与下单要求**（§1～§6 六分节）；**localStorage** Enable/审计；**无** Runtime 发布 UI — [`tool-registry-reconciliation`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) · **生产** Registry/策略 **TBD** |
| **`scenarioId` / 路由寄存器 · 编排策略下限** | **运行场景**（`ai.runtime-orchestration`） | Demo：只读快照 + 执行策略摘要 |
| 确认门结果 | 执行详情 + 人工确认规则 | 详情看当次；规则页看配置 |
| 模型路由 / 参数 | **模型配置**（全局参数 · `ai.settings`）— **使用策略** Tab 承载 **Runtime 模型策略**；**模型可选集绑定** **厂商与模型** Tab 台账（启用厂商 × 启用未弃用模型 · 见 [`domains/admin/ai-settings/overview.md`](../domains/admin/ai-settings/overview.md) §1.1）；**Infra Provider 台账** 仍以 OpenAPI / 域 FR 拆面 | 与执行解耦 |

## 映射维护规则

1. **新增 Runtime 概念** 时：先在本表增一行，再增 [sitemap.md](sitemap.md) 页面或注明「复用某页 Tab」。
2. **禁止** 仅在 `domains/admin` 长文中描述导航而不更新本目录 — IA 变更以 **本目录** 为对接实现的入口。

## 后续：OpenAPI / 页面字段表

当接口稳定后，可在本目录增加 `api-surface.md`（按页面列必要端点），**不**替代 [`specs/design/api.md`](../../design/api.md) 全局契约。
