# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-27
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · SQLite 测试库
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 8（P0）+ 1（P1） | 9 | 0 | 0 | 0 |

自动化：

```bash
cd server && uv run pytest tests/test_write_path_pipeline.py -v
```

→ **7 passed**（P0/P1 用例由下列测试函数覆盖；TC-03/05 与多条用例共用同一 timeline 断言）。

## 用例执行明细

| ID | 优先级 | 结果 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | 通过 | `test_runtime_skill_operation_spec_effective_200` |
| TC-02 | P0 | 通过 | `test_telegram_limit_webhook_type_a_emits_spec_read` — 完整 TG 回合至 Type-A 键盘 |
| TC-03 | P0 | 通过 | `assert_write_path_pipeline_order` — TC-02/07/08 及 `test_telegram_limit_confirm_write_path_timeline` |
| TC-04 | P0 | 通过 | `_assert_read_skill_orchestration_step` — TC-02/07/08 |
| TC-05 | P0 | 通过 | 各用例内 `GET …/admin/observability/executions/{id}/timeline` → 200 |
| TC-06 | P0 | 通过 | `test_invalid_skill_blocks_before_type_a_markup` — 空 bundle，无键盘、无 spec_read/写 |
| TC-07 | P0 | 通过 | `test_telegram_amend_confirm_write_path_timeline` — `smp` 回调 + mock 在途单/撤单/下单 |
| TC-08 | P0 | 通过 | `test_http_limit_order_write_path_timeline` — HTTP limit-order 五段序 |
| TC-09 | P1 | 通过 | `test_runtime_skill_operation_spec_unknown_404` — `PROMPT_SKILL_REF_INVALID` |

## 契约抽查

- [x] `GET …/runtime/skill-operation-spec/effective` 200 体 camelCase 与 `api.openapi.yaml` 一致
- [x] timeline `eventName` 五段序与 Admin `writePathPipelineOrder.ts` / `eval.runtime.pipeline_write_order` 对齐
- [x] 未知 skill **404** + `code=PROMPT_SKILL_REF_INVALID`

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- **无页面**（`test/coverage.md` 含页面：否）。下一步 **`/pipeline-frontend-integrate`** → frontend-agent **空跑** `frontend_done`，再 **`/pipeline-test-e2e`**（E2E N/A）、designer-review、product-accept。
- TG 限价确认路径另含 `test_telegram_limit_confirm_write_path_timeline`（手工 seed pending + `slp` 回调），补强 TC-03 在仅回调场景下的序。
