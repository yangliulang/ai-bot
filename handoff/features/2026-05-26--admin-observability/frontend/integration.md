# 前端对接说明

> 前端 Agent 在 tested 后对接真实接口，完成后推进 status 至 `frontend_done`（next: test-agent）。

## 页面与路由

| 页面 | 路由 | 说明 |
|------|------|------|
| 执行链路协查 | `/observability?tab=execution` | 列表 + 时间线（既有） |
| 工具调用 | `/observability?tab=tool&executionId={id}` | **本期** FR-MC803 |
| 大模型 | `/observability?tab=llm&executionId={id}` | **本期** FR-MC804 |

## 接口映射

| 页面/操作 | API | 方法 | 备注 |
|-----------|-----|------|------|
| 工具调用 Tab | `/api/v1/admin/observability/executions/{executionId}/tool-calls` | GET | `getAdminObservabilityToolCalls` |
| 大模型 Tab | `/api/v1/admin/observability/executions/{executionId}/llm` | GET | `getAdminObservabilityLlm` |
| 执行列表（同源） | `…/executions` | GET | 已有 `listAdminObservabilityExecutions` |

## 实现文件

| 文件 | 变更 |
|------|------|
| `admin/src/shared/api/admin-observability.ts` | 类型 + `getAdminObservabilityToolCalls` / `getAdminObservabilityLlm` |
| `admin/src/pages/observability/ObservabilityPage.vue` | tool/llm Tab 表格；无 `executionId` 引导；列表行「工具 / LLM」深链 |

## Mock 切换

- Mock 阶段：无（直接对接已测 API）
- 切换条件：`status.phase === tested` 后联调

## 联调结果

- [x] 主流程：`tab=tool|llm` + 有效 `executionId` 展示表格/汇总（依赖联调库有事件行）
- [x] 错误态：404 →「执行记录不存在」；其它 → message
- [x] 加载 / 空态：`UiTableEmptyRow` loading / filtered；无 `executionId` 不发起请求

## 联调环境

- Admin：`cd admin && npm run dev` → http://127.0.0.1:5173
- API 代理：`/api` → http://127.0.0.1:8080
- 鉴权：登录后 Bearer（与全站 `httpClient` 一致）

## 遗留问题

- 计费 / 审计 Tab 仍为占位（本期不做）
- 实例 I02/I04/I05 另包 `2026-05-26--admin-agent-instance-write`
