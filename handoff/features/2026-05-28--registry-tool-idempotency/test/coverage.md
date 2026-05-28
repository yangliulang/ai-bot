# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-28--registry-tool-idempotency` |
| 含页面（需 E2E） | 否（Registry audit pytest + Admin API；E2E N/A） |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | 镜像加载 + 版本常量 | TC-01 | — | `registry_idempotency` 模块 |
| AC-2 | skillId 幂等 | TC-02 | — | `assert_skill_registry_idempotent` |
| AC-3 | toolId 幂等 | TC-03 | — | `assert_tool_registry_idempotent` |
| AC-4 | Enable matrix 门禁 | TC-04 | — | `assert_enable_allowed` |
| AC-5 | OBS scenario join | TC-05 | — | `assert_obs_tool_call_scenario_join` |
| AC-6 | Registry 列表 API | TC-06 | — | `GET …/admin/tools/registry` |
| AC-7 | 幂等审计 API | TC-07 | — | `GET …/idempotency-audit` |
| AC-8 | pytest 套件 | TC-08 | — | `test_registry_tool_idempotency.py` |
| AC-9 | 证据模板 | TC-09 | — | `eval/evidence/registry-idempotency-audit.md` |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/admin/tools/registry | TC-06 |
| GET | /api/v1/admin/tools/registry/idempotency-audit | TC-07 |
| GET | /api/v1/admin/observability/executions/{executionId}/timeline | TC-05（可选集成） |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 含页面：否；E2E 列留空
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-28--registry-tool-idempotency` 退出码 0
