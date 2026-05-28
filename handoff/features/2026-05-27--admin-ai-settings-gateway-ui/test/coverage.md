# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-27--admin-ai-settings-gateway-ui` |
| 含页面（需 E2E） | 是（Admin `/ai-settings?tab=runtime`） |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | 网关策略分区可见 | TC-01 | E2E-01 | `/ai-settings?tab=runtime` |
| AC-2 | GET 回显开关 | TC-01 | E2E-01 | `GET …/admin/ai/defaults` |
| AC-3 | PATCH intentNluUseLlm | TC-02 | E2E-02 | `PATCH …/defaults` |
| AC-4 | PATCH narrate 部分合并 | TC-03 | E2E-03 | 嵌套 `telegramLlmNarrate` |
| AC-5 | PATCH 错误展示 | TC-04 | E2E-04 | 409/422 `AppError` |
| AC-6 | 分组 + env 说明 | TC-01 | E2E-01 | UI 文案 |
| AC-7 | 存量 Tab 不退化 | TC-05 | E2E-05 | catalog + scenario 模型 PATCH |
| AC-8 | 加载/保存态 | TC-01 | E2E-01 | loading / submitting |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/admin/ai/defaults | TC-01, E2E-01 |
| PATCH | /api/v1/admin/ai/defaults | TC-02～TC-05, E2E-02～E2E-05 |

## 后端回归（前序包）

| 包 | pytest（可选一并跑） |
|----|----------------------|
| `2026-05-26--nlu-llm-strategy` | `server/tests/test_intent_nlu_llm_policy.py`（或包内 report 所列） |
| `2026-05-26--telegram-llm-narrate` | `server/tests/test_telegram_llm_narrate_policy.py`（或包内 report 所列） |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 或 E2E 用例
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-27--admin-ai-settings-gateway-ui` 退出码 0
