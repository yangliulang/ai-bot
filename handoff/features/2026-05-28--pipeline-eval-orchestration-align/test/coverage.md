# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-28--pipeline-eval-orchestration-align` |
| 含页面（需 E2E） | 否（Eval pytest + API；E2E N/A） |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | 三场景 catalog read.skill 序 | TC-01 | — | `GET …/scenarios/{scenarioId}` |
| AC-2 | Eval 正例 assert | TC-02 | — | `eval_pipeline_write_order` 模块 |
| AC-3 | Eval 负例 P-N1 | TC-03 | — | 写早于确认 |
| AC-4 | Eval 负例 P-N2 | TC-04 | — | spec_read 晚于确认 |
| AC-5 | pytest eval 套件 | TC-05 | — | `test_eval_pipeline_write_order.py` |
| AC-6 | freeze §3 静态对拍 | TC-06 | — | `test_orchestration_freeze_align.py` |
| AC-7 | eval 证据模板 | TC-07 | — | `eval/evidence/eval-pipeline-write-order.md` |
| AC-8 | policy engineeringSpecRefs | TC-08 | — | `GET …/admin/orchestration/policy` |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/agent/scenarios/{scenarioId} | TC-01, TC-06 |
| GET | /api/v1/admin/orchestration/policy | TC-08 |
| GET | /api/v1/admin/observability/executions/{executionId}/timeline | TC-02（可选集成） |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 含页面：否；E2E 列留空
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-28--pipeline-eval-orchestration-align` 退出码 0
