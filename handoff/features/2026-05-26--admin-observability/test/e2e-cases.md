# E2E 测试用例 — 2026-05-26--admin-observability

> 前置：server 8080 + admin 5173；已登录；库中有含 tool 与 llm 事件的 executionId。

## P0

| ID | 关联 AC | 前置 | 步骤 | 预期 |
|----|---------|------|------|------|
| E2E-01 | AC-4 | 已登录 | 打开 observability tab=tool 并带 executionId | 展示工具表格；GET tool-calls 200；非占位文案 |
| E2E-02 | AC-5 | 已登录 | 打开 tab=llm 并带 executionId | 展示 modelId 或 calls；GET llm 200 |
| E2E-03 | AC-6 | 已登录 | 打开 tab=tool 且无 executionId | 提示先选执行记录；不发起 tool-calls |
| E2E-04 | AC-2 | 已登录 | tab=tool 且 executionId 不存在 | 页面展示 404 友好错误 |

## P1

| ID | 关联 AC | 前置 | 步骤 | 预期 |
|----|---------|------|------|------|
| E2E-05 | AC-4 | 已登录 | 从 execution Tab 列表进入 tool Tab | executionId 与列表行一致 |
