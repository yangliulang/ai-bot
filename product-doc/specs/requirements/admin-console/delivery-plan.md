# Admin Console — 交付计划（Planning → 低保真落地）

**范围**：与本目录 [README §本轮明确不做](README.md) **一致**；**不**含用户中心、完整财务/RBAC/Prompt Studio。

## 原则

| 原则 | 说明 |
|------|------|
| IA 先入 | Sitemap / Mapping 收口后再扩写域 `domains/admin` FR 条目 |
| 契约 | OpenAPI **不**在本目录重复；见 [api-surface.md](api-surface.md) 索引 |
| Demo | `src/admin/` **路由与侧栏**与本目录 [demo-routing.md](demo-routing.md) 对齐；无真实 API |

## 阶段与出口

### Phase A — 文档收口（本仓库已完成目标）

| 交付物 | 出口 |
|--------|------|
| [sitemap.md](sitemap.md) | 全部分组 + 页面 ID + P0～P2 |
| [runtime-to-ui-mapping.md](runtime-to-ui-mapping.md) | Runtime 概念 ↔ 页 |
| [prd-ia-alignment.md](prd-ia-alignment.md) | PRD 八大模块 ↔ 新 IA |
| [api-surface.md](api-surface.md) | 页面 ↔ OpenAPI / TBD |
| [demo-routing.md](demo-routing.md) | 页面 ID ↔ `src/admin` path |
| [page-specs.md](page-specs.md) | 逐页信息块与筛选（低保真） |

### Phase B — 低保真 UI（`src/admin` Demo · 已挂载基线）

| 切片 | 内容 | 出口 |
|------|------|------|
| B1 P0 | Executions 列表 + Execution 详情（**Timeline** **`transitionTrigger`** **若 API 返回须可读** — **同窗** `observability` §2.4、[runtime-to-ui-mapping](runtime-to-ui-mapping.md)） | `/runtime/executions` · `/runtime/executions/:id`，可链到 Observability |
| B2 P1 | **模型配置**（`/ai-settings`，侧栏在 **全局参数**） | `/ai-settings` |
| B3 P2 | Runtime Health、**全局参数 · 渠道管理** 占位 | `/observability/runtime-health` · `/system/channels` |
| B4 全覆盖 | 其余占位 + 全部分组侧栏 | `ConsolePlaceholderPage` + 路由注册（见 [`demo-routing.md`](demo-routing.md)） |

### Phase C — 后端联调（非本目录职责）

| 项 | 说明 |
|----|------|
| `runtime.executions` **列表** | **OpenAPI** **`listObservabilityExecutions`**（**`ObservabilityExecutionsPage`**）已登记；**BFF** **实现与索引** **所内** **MR** 补链；时间线 **`transitionTrigger`** 见 **`getObservabilityExecutionTimeline`· [api-surface.md](api-surface.md) |
| 队列 / 事件（单条 execution） | 随 **`runtime.execution-detail`** 内嵌呈现；跨 execution 聚合 Console **非** MVP |

## 依赖关系（简图）

```text
Runtime/requirements + design/api
        ↓
admin-console（IA + page-specs + api-surface）
        ↓
src/admin（低保真 Demo）
```

## 变更门禁

1. **改导航或页面职责**：先改 [sitemap.md](sitemap.md) / [runtime-to-ui-mapping.md](runtime-to-ui-mapping.md)，再改 [demo-routing.md](demo-routing.md) 与 `src/admin`。  
2. **改契约**：OpenAPI SSOT；本目录 [api-surface.md](api-surface.md) 只做索引更新。
