# 后端备注 — 2026-05-26--admin-observability

## 实现位置（ChainUp · `server/`）

| 项 | 路径 |
|----|------|
| 路由 | `server/chainup_agent/api/routers/admin_observability.py` |
| 逻辑 | `server/chainup_agent/application/admin_observability_execution_detail.py` |
| Schema | `server/chainup_agent/api/schemas/admin_observability_tool_llm.py` |
| 文档 | `server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md` |

**本功能无新增迁移**；消费既有 **`agent_execution`** / **`agent_execution_event`** 行。

## 启动与 Base URL

```bash
cd server && uv run chainup-agent-api
```

- **Base URL**：`http://127.0.0.1:8080`
- **OpenAPI**：`http://127.0.0.1:8080/openapi.json`（搜索 `tool-calls`、`/llm`）

## 鉴权

- 路径前缀：`/api/v1/admin/observability/…`
- 生产/已配 **`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`**（≥16）时须 **`Authorization: Bearer <access_token>`**（`POST /api/auth/login` 或 `register`）。
- 未配 JWT Secret 的纯本地联调：部分环境 Admin 路由可不强制 Bearer（以当前 `.env` 为准）。

```bash
TOKEN="$(curl -s -X POST http://127.0.0.1:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"YOUR_USER","password":"YOUR_PASS"}' | jq -r .access_token)"
```

## 对外路径（与功能包 `api.openapi.yaml` 一致）

| Method | Path | 200 体要点 |
|--------|------|------------|
| GET | `/api/v1/admin/observability/executions/{executionId}/tool-calls` | `{ "items": [ { "toolId", "toolCallSeq", "invocationState", … } ] }` |
| GET | `/api/v1/admin/observability/executions/{executionId}/llm` | `{ "modelId", "inputTokens", …, "calls": [ { "eventName", "outcome", … } ] }`（**无** messages 全文） |

## 错误码

| HTTP | `code` | 场景 |
|------|--------|------|
| 401 | `ADMIN_CONSOLE_AUTH_REQUIRED` | 缺 Bearer |
| 401 | `ADMIN_CONSOLE_ACCESS_TOKEN_INVALID` | 令牌无效 |
| 404 | `AGENT_ADMIN_EXECUTION_NOT_FOUND` | `executionId` 不存在 |

## curl 示例

```bash
# 404 探针（需 TOKEN）
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/admin/observability/executions/exec_nonexistent_000/tool-calls"

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/admin/observability/executions/exec_nonexistent_000/llm"
```

造数后查真实 execution（pytest 同款）：

```bash
cd server && uv run pytest tests/test_admin_p1_ops.py::test_observability_tool_calls_and_llm -q
# 用例内 accept 返回的 executionId 代入下述路径
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/admin/observability/executions/{executionId}/tool-calls" | jq .

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8080/api/v1/admin/observability/executions/{executionId}/llm" | jq .
```

## 自测结论

| 检查项 | 结果 |
|--------|------|
| `pytest tests/test_admin_p1_ops.py::test_observability_tool_calls_and_llm` | **通过**（2026-05-26） |
| 功能包 OpenAPI 路径/字段 | 与运行实现 **一致** |
| 契约差异 | **无**（联合 search / 导出本期不做） |

## 交给 test-agent

- 按 `test/cases.md` P0 执行；可先复用上述 pytest，再补 HTTP 手工/脚本。
- 需有效 **`executionId`** + 时间线事件（`trading.exchange_private`、`llm.*`）。
