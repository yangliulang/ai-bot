# E2E / 页面验证用例

> 测试 Agent 维护。契约就绪后可预填骨架；`frontend_done` 后启动前后端执行。

## 前置条件

- 后端：`backend/notes.md` 中的启动命令，API 可访问
- 前端：`frontend/integration.md` 中的 dev 地址（默认 `http://localhost:5173`）

## 用例列表

> **本功能无页面**（`test/coverage.md` · `frontend/integration.md`）。E2E P0 **不适用**；由 test-agent 在 `test/e2e-report.md` 记 **N/A** 后可直接推进 `e2e_verified`（designer 已预填 `design/ui-review.md` N/A）。

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| — | — | N/A | 无 Admin/Deeplink 路由 | — | — |

## 验收对照（brief.md）

- [x] 主流程页面可访问 — **N/A（无页面）**
- [x] 成功态展示符合 AC — **已由 API 测试覆盖（test/report.md）**
- [x] 至少一种错误态 — **UNKNOWN 502 已在 API 层验证**

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| | | |
