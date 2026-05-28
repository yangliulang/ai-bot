# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-26
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · SQLite 测试库 · API health `http://127.0.0.1:8080/health` → 200
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 8（P0）+ 1（P1） | 9 | 0 | 0 | 0 |

自动化：

```bash
cd server && uv run pytest tests/test_trading_reconcile.py \
  tests/test_spot_amend_trade.py::test_spot_amend_cancel_ok_replace_fail -v
```

→ **9 passed**（含领域单测 2 条 + HTTP P0/P1 7 条）。

## 用例执行明细

| ID | 优先级 | 结果 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | 通过 | `test_reconcile_http_with_execution` — POST 200、`caseKind`、必填字段、`orderLookups` |
| TC-02 | P0 | 通过 | 同上 — GET status `lastReconcileAtSeq` 非空 |
| TC-03 | P0 | 通过 | `test_reconcile_status_pending_unknown` — `UNKNOWN` / `stillUnknown=true` / `SUBMIT_UNKNOWN` |
| TC-04 | P0 | 通过 | `test_reconcile_unbound_user_403` |
| TC-05 | P0 | 通过 | `test_reconcile_execution_not_found_404` — POST + GET |
| TC-06 | P0 | 通过 | `test_reconcile_no_query_targets_422` |
| TC-07 | P0 | 通过 | `test_reconcile_http_with_execution` — 时间线 `trading.reconcile` payload |
| TC-08 | P0 | 通过 | `test_spot_amend_cancel_ok_replace_fail` — 502 + `reconcileSuggested` / `reconcilePath` |
| TC-09 | P1 | 通过 | `test_reconcile_invalid_case_kind_422` |

## 契约抽查

- [x] `POST|GET …/reconcile*` 200 体 camelCase，与 `api.openapi.yaml` 一致（pytest 断言字段名）
- [x] 403/404/422 错误体 `code` 与 OpenAPI 示例一致
- [x] `userMessage` / `neutralHint` 存在；`stillUnknown=true` 时 status 为 `UNKNOWN`（TC-03），无假终态成功文案

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- **无页面**（`test/coverage.md` 含页面：否）。下一步 **`/pipeline-frontend-integrate`** 建议 frontend-agent **空跑** `frontend_done`（见 `frontend/integration.md`），再 **`/pipeline-test-e2e`** 填 E2E **N/A**。
- 领域辅助：`test_infer_amend_cancel_ok_replace_fail`、`test_map_coobit_status` 已绿，支撑 case 推断与查单映射。
