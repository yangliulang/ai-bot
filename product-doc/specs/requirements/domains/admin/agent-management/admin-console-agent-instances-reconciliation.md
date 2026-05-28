# 运营台 · 实例管理对齐（`ai.agents-instances`）

**路径**：`specs/requirements/domains/admin/agent-management/admin-console-agent-instances-reconciliation.md`  
**读者**：产品、后台、Agent 生命周期联调  
**端到端鸟瞰**：[`flow/e2e-closed-loop.md`](../../../../flow/e2e-closed-loop.md) **阶段 F · `INST`**  
**域规格（正式 FR）**：[`config.md`](config.md) · [`functions.md`](functions.md)  
**低保真**：[`admin-console/page-specs.md`](../../admin-console/page-specs.md) · **路由**：[`demo-routing.md`](../../admin-console/demo-routing.md)

---

## 0. Demo 对齐快照（2026-05-27 · `src/admin`）

| 项 | 原型 |
|----|------|
| **路由 · pageId** | `/agents/instances` · `ai.agents-instances`；`/agents/instances/:instanceId` 详情 |
| **重定向** | `/agents/config`、`/agents/templates` 及带 id 变体 → **`/agents/instances`**（**无** 模板列表/编辑向导） |
| **G01** | `AgentGlobalGateBanner`：OFF 时告警 +「当日不再显示」；列表 **Start/Resume** 禁用；**批量 Pause/Stop 仍可用** |
| **列表列（Demo 收窄）** | 实例 ID · 用户 UID · **运行状态**（`agentState` + block 原因）· **实例状态**（机电态）· 最近活跃 · 操作 |
| **列表刻意无列** | **模板** · **渠道** · **子账户**（**仅详情** 绑定 Tab 可见） |
| **筛选** | 单行关键字（`q` 或旧 `user`/`id`）→ `instanceId`/`userId`/`agentSubAccountUid`；**`gate`** / **`rt`**（URL 可读）；增补 **用户 UID**、**最近活跃日期区间**（**会话内**，不写 URL） |
| **批量** | 多选 → **批量 Pause / Stop**（**FR-AM-R06** 演示 Modal） |
| **导出** | **I08** 演示 Modal（应用当前筛选结果条数） |
| **预览抽屉** | 实例 ID + userId；链详情 · **执行链路协查**（`userId` 深链） |
| **详情** | 页头副区 **仅 `userId`**；Tab 不外显模板；日志三子 Tab + `?tab=` 深链 |

**与 §3.1 正式列之差**：[`config.md`](config.md) **§Demo** 为 **有意收窄**；**正式验收** 仍以 §3.1 / §1.1 为准。

---

## 1. 详情页 Tab（Demo）

| Tab | 要点 |
|-----|------|
| **概览** | 创建时间、创建者、配额/门禁摘要 |
| **绑定** | 子账户/交易 API 绑定；**无** 顶层运营 Alert |
| **参数** | `instanceOverrides` + Effective JSON |
| **日志** | Conversation / Tool / Error；链 observability |
| **审计** | 最近 N 条（若有） |

---

## 2. 与其它面对位

| 模块 | 关系 |
|------|------|
| **执行记录 / 协查** | 列表/详情「协查」→ `/observability?userId=` 或 `executionId` |
| **运行场景** | `scenarioId` 在场景页只读；**非** 实例列表列 |
| **全局闸真源** | `GLOBAL_AGENT_SWITCH` **无** Demo 独立配置页 |

---

## 3. 维护约定

- **改 Demo 列/筛选**：先改 **本篇 §0**，再改 [`page-specs.md`](../../admin-console/page-specs.md) **`ai.agents-instances`** 与 [`config.md`](config.md) §Demo。
- **实质需求变更**：同窗 [`product/roadmap.md`](../../../../product/roadmap.md)。

---

**文档版本**：0.1.0 · **2026-05-27** · **维护**：后台 + Agent owner
