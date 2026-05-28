# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-26--nlu-llm-strategy` |
| 含页面（需 E2E） | 否 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | defaults.intentNluUseLlm 读写 | TC-01 | — | `GET|PATCH …/admin/ai/defaults` |
| AC-2 | 启用时 llm_structured_v1 | TC-02 | — | `POST …/intent/recognize` |
| AC-3 | LLM 失败回退 keyword | TC-03 | — | mock gateway/parse fail → 200 |
| AC-4 | 关闭时仅 keyword | TC-04 | — | defaults false + env false |
| AC-5 | env=true 覆盖 admin false | TC-05 | — | `INTENT_NLU_USE_LLM` |
| AC-6 | effectiveIntentNluUseLlm | TC-06 | — | 响应字段 |
| AC-7 | Telegram timeline 一致 | TC-07 | — | `intentNluLlmEnabled` effective |
| AC-8 | PROMPT_INJECTION 回退 | TC-08 | — | 200 + keyword_v1 |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/admin/ai/defaults | TC-01 |
| PATCH | /api/v1/admin/ai/defaults | TC-01 |
| POST | /api/v1/agent/intent/recognize | TC-02～TC-08 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 无页面，E2E 不适用
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-26--nlu-llm-strategy` 退出码 0
