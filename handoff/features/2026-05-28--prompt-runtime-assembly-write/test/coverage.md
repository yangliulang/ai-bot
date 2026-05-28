# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-28--prompt-runtime-assembly-write` |
| 含页面（需 E2E） | 否（pytest + API 时间线 join；E2E N/A） |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | §1 拼装语义顺序 | TC-01 | — | `assemble_trading_llm_payload` |
| AC-2 | Tool JSON Schema SSOT | TC-02 | — | registry Schema 块 |
| AC-3 | Few-shot 在 User 前 | TC-03 | — | message 下标序 |
| AC-4 | effective TRADING 绑定 | TC-04 | — | `GET …/internal/prompts/effective` |
| AC-5 | trading_write prompt.snapshot | TC-05 | — | TG Type-A 时间线 |
| AC-6 | execution + timeline join | TC-06 | — | `GET …/execution/{id}` + timeline |
| AC-7 | pytest 写路径套件 | TC-07 | — | `test_prompt_assembly_write_path.py` |
| AC-8 | 证据模板 | TC-08 | — | `eval/evidence/prompt-runtime-assembly-write.md` |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/internal/prompts/effective | TC-04 |
| GET | /api/v1/agent/execution/{executionId} | TC-06 |
| GET | /api/v1/admin/observability/executions/{executionId}/timeline | TC-05, TC-06 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 含页面：否；E2E 列留空
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-28--prompt-runtime-assembly-write` 退出码 0
