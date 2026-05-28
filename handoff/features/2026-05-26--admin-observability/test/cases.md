# API 测试用例 — 2026-05-26--admin-observability

> 执行环境：`cd server && uv run chainup-agent-api`（8080）。自动化：`server/tests/test_admin_p1_ops.py::test_observability_tool_calls_and_llm`。

## P0

| ID | 关联 AC | 前置 | 步骤 | 预期 |
|----|---------|------|------|------|
| TC-01 | AC-1 | 联调库 | accept 得 executionId；造 trading.exchange_private 事件；GET tool-calls | 200；items 至少 1 条；invocationState 为 SUCCESS |
| TC-02 | AC-2 | 无 | GET tool-calls 与 GET llm，executionId 不存在 | 均 404；code 为 AGENT_ADMIN_EXECUTION_NOT_FOUND |
| TC-03 | AC-3 | 联调库 | 造 llm.chat.faq 事件；GET llm | 200；calls 至少 1 条；响应无 messages 全文字段 |
| TC-04 | AC-4 | 同 TC-01 | 检查 items[0].phase 与 summary | 字段符合 ToolCallsPageResponse |
| TC-05 | AC-5 | 无 LLM 事件 | GET llm | 200；calls 为空数组 |
| TC-06 | AC-6 | 无 | 不适用 HTTP | 见 E2E-03 |

## P1

| ID | 关联 AC | 前置 | 步骤 | 预期 |
|----|---------|------|------|------|
| TC-07 | AC-1 | JWT 已配 | GET tool-calls 无 Bearer | 401 ADMIN_CONSOLE_AUTH_REQUIRED |
