# Observability Admin 对齐（tool-calls / llm）

> 功能 ID：`2026-05-26--admin-observability`  
> 产品 Agent 定稿 · `contract_ready`

## 背景

运营需在 Admin **可观测性** 控制台按 **`executionId`** 协查 **工具调用**（`trading.exchange_*` / `agent.tool.call`）与 **LLM 计量**（`llm.*` 事件，**不含** messages 全文）。服务端 **FR-MC803 / FR-MC804** 已挂载（`server/chainup_agent/api/routers/admin_observability.py`）；`/observability` 的 **工具调用 / 大模型** Tab 仍为占位文案，需与 OpenAPI / `API_ADMIN_OBSERVABILITY_EXECUTIONS.md` 对齐接线。

## 用户故事

- 作为 **运营/排障**，我希望在 **`/observability`** 选定执行 ID 后查看 **tool-calls** 与 **llm** 明细，以便与 **时间线** Tab 交叉验证交易所写操作与 LLM 网关调用。
- 作为 **测试**，我希望用 API P0 用例断言 **`invocationState`**、**`calls[].eventName`** 等字段，以便回归不破坏契约。

## 验收标准

- [x] **AC-1**：对已存在且含 **`trading.exchange_private`**（或等价工具事件）的 **`executionId`**，`GET /api/v1/admin/observability/executions/{executionId}/tool-calls` 返回 **200**，**`items[]` 长度 ≥ 1**，首项含 **`toolId`**、**`invocationState`**（如 **`SUCCESS`**）。
- [x] **AC-2**：对不存在的 **`executionId`**，`GET …/tool-calls` 与 **`GET …/llm`** 均返回 **404**，**`code`** 为 **`AGENT_ADMIN_EXECUTION_NOT_FOUND`**（或文档等价错误码）。
- [x] **AC-3**：对已写入 **`llm.*`** 时间线事件的 **`executionId`**，`GET …/llm` 返回 **200**，**`calls[]` 长度 ≥ 1**，含 **`eventName`**、**`outcome`**；响应 **不得** 含 messages / prompt 全文字段。
- [x] **AC-4**：Admin **`/observability?tab=tool&executionId={id}`** 展示工具调用表格（**`toolId` / `invocationState` / `phase`** 等），加载中与列表失败有明确错误文案。
- [x] **AC-5**：Admin **`/observability?tab=llm&executionId={id}`** 展示 LLM 汇总（**`modelId`**）及 **`calls[]`** 列表；无 LLM 事件时展示空态（非报错占位「待 /be」）。
- [x] **AC-6**：**`tab=tool` 或 `tab=llm`** 且 URL **无** **`executionId`** 时，页面提示「请先选择执行记录」并提供跳转 **执行** Tab / 列表的入口（不发起 tool-calls/llm 请求）。

## 范围

### 本期包含

- 功能包 OpenAPI：**`GET …/tool-calls`**、**`GET …/llm`**（与存量实现对齐）。
- Admin：**`admin-observability.ts`** 客户端 + **`ObservabilityPage.vue`** **tool / llm** Tab 真实数据。
- API 测试（P0）与 E2E（P0）覆盖上列 AC。
- 与既有 **执行列表 / 时间线**、**`/runtime/executions/{id}`** 深链 **`executionId`** 参数一致。

### 本期不包含

- **`GET …/observability/search`**、审计导出、logs/traces/metrics 聚合（路线图 §6.1 余量）。
- **Agent 实例 I02/I04/I05**（另立 **`2026-05-26--admin-agent-instance-write`**）。
- **计费 / 绑定 / Deeplink** 改动。
- 修改 **`agent_execution_event`** 写入语义（仅消费既有事件）。

## 界面与交互（含页面）

| 路由 | 行为 |
|------|------|
| `/observability?tab=execution` | 已有：列表 + 时间线；从列表带入 **`executionId`** |
| `/observability?tab=tool&executionId=` | 拉取 tool-calls；表格 + 空态 / 错误态 |
| `/observability?tab=llm&executionId=` | 拉取 llm；汇总 + calls 列表 + 空态 / 错误态 |
| `/runtime/executions/{executionId}` | 可选：详情页增加跳转 tool/llm Tab 的链接（非必须，有则 AC-4 更易测） |

**加载态**：Tab 切换或 **`executionId`** 变化时展示 loading；**404** 展示「执行记录不存在」。

## 非功能要求

- 须带 Admin **Bearer**（与现有 Observability 列表一致）。
- 单执行 **tool-calls / llm** 请求超时与列表 API 同级；不在前端缓存敏感 **`summary`** 全文到 localStorage。

## 实现备注（存量）

| 层 | 状态 |
|----|------|
| **server** | 已实现 · `test_admin_p1_ops.py::test_observability_tool_calls_and_llm` + `test_admin_observability_pipeline_p0.py` |
| **admin** | 已对接 · `ObservabilityPage.vue` tool/llm Tab · `admin-observability.ts` |
| **契约 SSOT** | `product-doc/specs/openapi/admin/observability.yaml`、`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md` |

## 待确认问题

- [x] Q1：tool/llm Tab 在 **`ObservabilityPage`** 内嵌（与 FE_HANDOFF 2026-05-25 一致）；**`ExecutionDetailPage`** 增 Tab 非本期必须。
