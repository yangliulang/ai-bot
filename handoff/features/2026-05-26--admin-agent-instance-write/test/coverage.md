# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-26--admin-agent-instance-write` |
| 含页面（需 E2E） | 是 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 页面行为 |
|----|------|----------|----------|-------------------|
| AC-1 | I02 创建 201 | TC-01 | E2E-01 | `POST …/instances` · 列表创建 |
| AC-2 | 重复 tg 422 | TC-02 | E2E-04 | `AGENT_QUOTA_EXCEEDED` · 创建失败文案 |
| AC-3 | I05 白名单 PATCH | TC-03, TC-04 | E2E-02 | merge / unknownKeys · 详情编辑 |
| AC-4 | I04 bind/unbind | TC-05, TC-06 | E2E-03 | POST/DELETE binding · 详情按钮 |
| AC-5 | BOUND → NONE | TC-07 | E2E-03 | 绑定态列（解绑后 NONE） |
| AC-6 | G01 关闸 422 | TC-08 | E2E-01 | `AGENT_GLOBAL_OFF` · API 断言为主；UI 同 smoke |
| AC-7 | 列表创建 UI | TC-01 | E2E-01 | `/agents/instances` |
| AC-8 | 详情 I05 编辑 | TC-03 | E2E-02 | `/agents/instances/:id` |
| AC-9 | 详情 I04 绑定/解绑 | TC-05, TC-06 | E2E-03 | 登记 + 解绑 |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| POST | /api/v1/admin/agents/instances | TC-01, TC-02, TC-08 |
| PATCH | /api/v1/admin/agents/instances/{instanceId} | TC-03, TC-04 |
| POST | /api/v1/admin/agents/instances/{instanceId}/binding | TC-05 |
| DELETE | /api/v1/admin/agents/instances/{instanceId}/binding | TC-06, TC-07 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 含页面时每个 AC 至少 1 条 P0 E2E（`test/e2e-cases.md`）
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-26--admin-agent-instance-write` 退出码 0
