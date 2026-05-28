# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-26--admin-observability` |
| 含页面（需 E2E） | 是 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 页面行为 |
|----|------|----------|----------|-------------------|
| AC-1 | tool-calls 有数据 | TC-01 | E2E-01 | `GET …/tool-calls` 200 · `items≥1` |
| AC-2 | 不存在 execution 404 | TC-02 | E2E-04 | `GET …/tool-calls` & `…/llm` 404 |
| AC-3 | llm calls 有数据且无全文 | TC-03 | E2E-02 | `GET …/llm` 200 · 无 messages |
| AC-4 | Admin tool Tab 表格 | TC-04 | E2E-01 | `/observability?tab=tool&executionId=` |
| AC-5 | Admin llm Tab 列表/空态 | TC-05 | E2E-02 | `/observability?tab=llm&executionId=` |
| AC-6 | 无 executionId 提示 | TC-06 | E2E-03 | 不请求 API · 引导文案 |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/admin/observability/executions/{executionId}/tool-calls | TC-01, TC-02, TC-04 |
| GET | /api/v1/admin/observability/executions/{executionId}/llm | TC-03, TC-02, TC-05 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 含页面时每个 AC 至少 1 条 P0 E2E（`test/e2e-cases.md`）
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-26--admin-observability` 退出码 0
