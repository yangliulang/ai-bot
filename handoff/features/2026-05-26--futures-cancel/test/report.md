# 测试报告（API）

> 测试 Agent 在 `backend_done` 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-28
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · SQLite 隔离库；API `http://127.0.0.1:8080/health` → **200**
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 7（P0）+ 1（P1） | 8 | 0 | 0 | 0 |

说明：pytest 功能包精选 **9** 条（P0 TC-01～07 + P1 TC-08）；`test_futures_cancel_condition_trade.py` 全文件 **14** 条含条件单回归（包外）。

自动化：

```bash
cd server && uv run pytest \
  tests/test_futures_cancel.py \
  tests/test_futures_cancel_condition_trade.py::test_futures_cancel_http_success \
  tests/test_futures_cancel_condition_trade.py::test_scenarios_futures_cancel_and_condition_read_ready \
  tests/test_futures_cancel_condition_trade.py::test_runtime_intent_futures_cancel_execute \
  tests/test_futures_cancel_condition_trade.py::test_coobit_fapi_cancel_body -v
# 9 passed in ~0.7s
```

## 用例执行明细

| ID | 优先级 | 结果 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | 通过 | `test_futures_cancel_http_success` — **200**；`scenarioId=trade.futures.cancel_order`；`orderIdString` |
| TC-02 | P0 | 通过 | `test_futures_cancel_tc02_unbound_user_403` — **403** `AGENT_SUBACCOUNT_REQUIRED` |
| TC-03 | P0 | 通过 | `test_futures_cancel_tc03_feature_futures_off_403` — **403** `FEATURE_AGENT_FUTURES_OFF` |
| TC-04 | P0 | 通过 | `test_futures_cancel_tc04_cancel_rejected_400` — **400** `AGENT_FUTURES_CANCEL_REJECTED` |
| TC-05 | P0 | 通过 | `test_futures_cancel_tc05_validation_empty_symbol_422` · `…_empty_order_id_422` |
| TC-06 | P0 | 通过 | `test_runtime_intent_futures_cancel_execute` — `EXECUTE_FUTURES_CANCEL` |
| TC-07 | P0 | 通过 | `test_scenarios_futures_cancel_and_condition_read_ready` — `trade.futures.cancel_order` **ready** |
| TC-08 | P1 | 通过 | `test_coobit_fapi_cancel_body` |

## 契约抽查

- [x] `POST …/futures/cancel` 200 camelCase 与 `api.openapi.yaml` 一致
- [x] 403/400/422 错误体 `code` 与 OpenAPI 示例一致
- [x] 与 **`condition-order-list-cancel`** 边界：`cancel-condition` 用例不在本包门禁内

`./scripts/check-test-coverage.sh handoff/features/2026-05-26--futures-cancel` → **0**

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- **含页面：否**；下一 Chat：**`/pipeline-frontend-integrate`**（空跑）→ E2E N/A → designer → product accept。
- TG 绑定会话直接撤单为 P1，不阻塞本包。
