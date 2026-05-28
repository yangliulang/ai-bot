# 运营台 · 执行记录对齐（`runtime.executions` / `runtime.execution-detail`）

**路径**：`specs/requirements/domains/admin/observability-management/admin-console-runtime-executions-reconciliation.md`  
**读者**：产品、后台、Runtime/观测联调  
**端到端鸟瞰**：[`flow/e2e-closed-loop.md`](../../../../flow/e2e-closed-loop.md) **阶段 F · `UI`**  
**映射**：[`admin-console/runtime-to-ui-mapping.md`](../../admin-console/runtime-to-ui-mapping.md)  
**低保真**：[`admin-console/page-specs.md`](../../admin-console/page-specs.md) · **路由**：[`demo-routing.md`](../../admin-console/demo-routing.md)

---

## 0. 执行列表 · Demo 对齐快照（2026-05-27 · `src/admin`）

| 项 | 原型 |
|----|------|
| **路由 · pageId** | `/runtime/executions` · `runtime.executions`（**默认落地页**） |
| **页眉 Tag** | **运行运营**；可选 **已连接运营观测 API** |
| **默认列** | 执行 ID · **用户 UID** · **场景 ID** · **意图摘要** · 运行状态 · 当前阶段 · **业务终态** · 重试次数 · 创建时间 · 操作 |
| **筛选 URL** | **`q`**（用户/执行 ID/场景 合并）· **`intent`** · **`scenario`** · **`status`** · **`from`** / **`to`**（日期） |
| **行交互** | **单击行** → 右侧 **预览抽屉**（摘要 + 工具摘录 + 链协查/详情）；「预览」「详情」按钮 |
| **API（可选）** | `VITE_USE_OBSERVABILITY_API` → `GET …/observability/executions`；`u-*`→userId、**纯数字 10～19 位**→executionId、点分串→scenarioId；**`nextCursor` 加载更多** |
| **MVP 约束** | **无** 独立任务队列/运行事件侧栏页；`/runtime/tasks`、`/runtime/events` → 本列表 |

**与执行链路协查分工**：本页 = **运营主列表 + 单条详情入口**；`/observability` = **多实体联合检索 + 协查抽屉**（见 [`admin-console-observability-reconciliation.md`](admin-console-observability-reconciliation.md)）。

---

## 1. 执行详情 · Demo 对齐快照

| 项 | 原型 |
|----|------|
| **路由** | `/runtime/executions/:executionId` · `runtime.execution-detail` |
| **Tab · `?tab=`** | `overview` \| `timeline` \| `queue` \| `events` \| `retries` \| `recovery` |
| **总览** | 场景 · Runtime 技能范围 · Prompt 拼装追溯（**SC-PM-22**）· 技能规范（**SC-OM-05**）· Canonical Inspector（演示）· 工具/LLM/计费镜像 |
| **时间线** | **FR-MC801** Steps + 精细 Timeline；**`transitionTrigger` 若 API 有则展示**；写路径演示含 **`agent.skill.spec_read`** |
| **Recovery** | MVP 占位 + 链 **执行链路协查** |
| **BFF** | 摘要 `GET …/executions`；时间线 `GET …/executions/{id}/timeline`（`observabilityExecutions.ts`） |

---

## 2. 维护约定

- **改列表列/筛选/预览**：先改 **本篇 §0～§1**，再改 [`page-specs.md`](../../admin-console/page-specs.md)、[`demo-routing.md`](../../admin-console/demo-routing.md)、`ExecutionListPage` / `opsPanelHints.EXECUTION_LIST`。
- **实质需求变更**：同窗 [`product/roadmap.md`](../../../../product/roadmap.md)。

---

**文档版本**：0.1.0 · **2026-05-27** · **维护**：后台 + Runtime owner
