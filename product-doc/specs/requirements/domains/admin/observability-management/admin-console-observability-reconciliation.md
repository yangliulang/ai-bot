# 运营台 · 执行链路协查对齐（`obs.traces-logs`）

**路径**：`specs/requirements/domains/admin/observability-management/admin-console-observability-reconciliation.md`  
**读者**：产品、后台、观测/账务联调  
**端到端鸟瞰**：[`flow/e2e-closed-loop.md`](../../../../flow/e2e-closed-loop.md) **阶段 F · `UI`**（与执行记录同窗）  
**域 IA**：[`config.md`](config.md) §1  
**低保真**：[`admin-console/page-specs.md`](../../admin-console/page-specs.md) · **路由**：[`demo-routing.md`](../../admin-console/demo-routing.md)

---

## 0. Demo 对齐快照（2026-05-27 · `src/admin`）

| 项 | 原型 |
|----|------|
| **路由 · pageId** | `/observability` · `obs.traces-logs` |
| **重定向** | `/observability/runtime-health`、`/observability/alerts` → 本页（**无** 独立侧栏） |
| **页眉** | 标题「执行链路协查」；Tag **执行协查**；**复制链接** + **应用检索** |
| **顶栏联合筛选** | **执行 ID** · **用户 UID** · **计费链路 ID**（`traceId`，别名 `traceKey`）→ 写入 URL |
| **Tab · `?tab=`** | `execution` \| `tool` \| `llm` \| `billing` \| `audit`（中文：执行 / 工具调用 / 大模型 / 计费 / 审计） |
| **执行 Tab 列** | 执行 ID（可点）· 用户 UID · 场景 · 终态 · 耗时 · 开始时间 |
| **工具 Tab** | 附加关键字筛选；列：执行 ID · 序号 · 工具 ID · 状态 · 路径摘要 · 时间 |
| **LLM Tab** | 附加筛选；列：执行 ID · 模型 ID · Token 合计 · 时间 |
| **计费 Tab** | 附加筛选 + 核销状态下拉；列与 **`billing.ledger`** 同窗（`obsBillingColumns`） |
| **审计 Tab** | 时间 · 操作者 · 动作 · 资源 |
| **时间线区（顶）** | 精确 **executionId** 或筛选至 **单条** 时展示 **业务叙事时间线** + **FR-MC801**（`Mc801TimelineAudit`） |
| **协查抽屉** | 执行 ID 点击 → 抽屉：叙事时间线 · MC801 表 · 工具 / Prompt / LLM / 风控摘要 · 链执行详情 |

### 刻意未交付（Demo）

| 项 | 说明 |
|----|------|
| **FR-MC805 运行健康 SLI** | **无** 页内 SLI 卡片/堆积看板；旧「运行健康」路由仅 **重定向** 至本页 |
| **独立告警运营页** | **无**；`obs.alerts` 重定向至本页 |
| **生产** | 全量 **FR-MC802** 联合检索 API 接线 **TBD**；当前 **mock 表** + 客户端筛选 |

---

## 1. 与执行记录 / 核销的分工

| 页面 | 运营问题 | 主锚 |
|------|----------|------|
| **执行记录** | 今天有哪些 execution、卡在哪 | 列表 + **详情 Tab** |
| **本页** | 跨工具/模型/计费/审计 **联合定位** | `executionId` + 协查抽屉 |
| **执行核销追踪** | 扣了哪笔 Capability、可否对账 | `billingTraceId` / 核销状态 |

---

## 2. Deep link 约定

| 参数 | 用途 |
|------|------|
| `executionId` | 执行 Tab 主筛 + 时间线锁定 |
| `userId` | 用户维度 |
| `traceId` / `traceKey` | 计费链路（同窗 `billingTraceId`） |
| `tab` | 默认 `execution` |

**分享**：「复制链接」序列化当前三字段 + `tab`。

---

## 3. 维护约定

- **改 Tab/列/抽屉**：先改 **本篇 §0**，再改 [`config.md`](config.md)、[`page-specs.md`](../../admin-console/page-specs.md)、`ObservabilityPage` / `opsPanelHints.OBSERVABILITY`。
- **若补 SLI 看板**：须 **MR** 更新本篇「刻意未交付」与 [`sitemap.md`](../../admin-console/sitemap.md)。
- **实质需求变更**：同窗 [`product/roadmap.md`](../../../../product/roadmap.md)。

---

**文档版本**：0.1.0 · **2026-05-27** · **维护**：后台 + 观测 owner
