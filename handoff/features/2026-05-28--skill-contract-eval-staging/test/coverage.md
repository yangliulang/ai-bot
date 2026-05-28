# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-28--skill-contract-eval-staging` |
| 含页面（需 E2E） | 否（Eval pytest + effective API；E2E N/A） |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | P0 evalSetId 常量 | TC-01 | — | `eval_skill_contract` 模块 |
| AC-2 | 缺数量不进类型 A | TC-02 | — | `assert_eval_skill_missing_qty_no_confirm` |
| AC-3 | 闪兑不得带限价 | TC-03 | — | `assert_eval_skill_flash_no_limit_price` |
| AC-4 | 全仓双确认 | TC-04 | — | `assert_eval_skill_margin_double_confirm` |
| AC-5 | 改单 cancel 先于 order | TC-05 | — | `assert_eval_skill_amend_cancel_before_order` |
| AC-6 | P0 fixture 同窗跑通 | TC-06 | — | `run_eval_skill_p0_fixture` |
| AC-7 | pytest 套件 | TC-07 | — | `test_eval_skill_contract.py` |
| AC-8 | effective 读 Given | TC-08 | — | `GET …/runtime/skill-operation-spec/effective` |
| AC-9 | eval 证据模板 | TC-09 | — | `eval/evidence/eval-skill-contract-p0.md` |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/runtime/skill-operation-spec/effective | TC-08 |
| GET | /api/v1/agent/scenarios/{scenarioId} | TC-06（可选 scenario 对照） |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 含页面：否；E2E 列留空
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-28--skill-contract-eval-staging` 退出码 0
