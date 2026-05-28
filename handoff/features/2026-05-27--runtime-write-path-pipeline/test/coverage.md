# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-27--runtime-write-path-pipeline` |
| 含页面（需 E2E） | 否（Observability 存量页；E2E 以 API+时间线或 N/A） |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | Runtime 读 effective 规范 | TC-01 | — | `GET …/runtime/skill-operation-spec/effective` |
| AC-2 | TG 限价写 spec_read 事件 | TC-02 | E2E-01 | Telegram webhook + timeline |
| AC-3 | 五段因果序 | TC-03 | E2E-01 | timeline 断言 |
| AC-4 | orchestration read.skill 步 | TC-04 | — | `agent.orchestration.step` |
| AC-5 | Admin timeline API | TC-05 | — | `GET …/observability/executions/{id}/timeline` |
| AC-6 | 未发布 skill 写前阻断 | TC-06 | — | 无效 skillId / 无 spec_read |
| AC-7 | TG 改单路径 spec_read | TC-07 | — | amend confirm 回调 |
| AC-8 | HTTP limit-order 五段序 | TC-08 | — | `POST …/limit-order` |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/runtime/skill-operation-spec/effective | TC-01, TC-06 |
| POST | /api/v1/agent/trade/spot/limit-order | TC-08 |
| GET | /api/v1/admin/observability/executions/{executionId}/timeline | TC-03, TC-05 |
| — | Telegram webhook（无 OpenAPI path） | TC-02, TC-04, TC-07 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 含页面：否；E2E 列对 AC-2/3 填 E2E-01（时间线走查）或 N/A
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-27--runtime-write-path-pipeline` 退出码 0
