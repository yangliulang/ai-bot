# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-26--futures-cancel` |
| 含页面（需 E2E） | 否 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | POST 撤单成功 | TC-01 | — | `POST …/futures/cancel` |
| AC-2 | 未绑定 403 | TC-02 | — | `AGENT_SUBACCOUNT_REQUIRED` |
| AC-3 | 功能关闭 403 | TC-03 | — | `FEATURE_AGENT_FUTURES_OFF` |
| AC-4 | 撤单拒单 400 | TC-04 | — | `AGENT_FUTURES_CANCEL_REJECTED` |
| AC-5 | 参数 422 | TC-05 | — | `VALIDATION_ERROR` |
| AC-6 | 意图 EXECUTE | TC-06 | — | `POST …/intent/recognize` |
| AC-7 | 场景 ready | TC-07 | — | `GET …/scenarios` |
| AC-8 | cancel body 领域 | TC-08 | — | `coobit_fapi_v1_cancel_body` |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| POST | /api/v1/agent/trade/futures/cancel | TC-01～TC-05 |

## 相关存量测试（非本包 path）

| 文件 | 说明 |
|------|------|
| `test_futures_cancel_condition_trade.py` | 同文件含条件单查/撤 — **本包** 仅映射 `…/cancel` 与意图/场景用例 |
| `test_condition_order_list_cancel.py` | 条件单 403/502 — 归 **condition-order-list-cancel** |
| `test_trading_write_unknown_global.py::test_futures_cancel_http_unknown_tc04` | UNKNOWN 全局 — 归 **trading-write-unknown-global** |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 无页面，E2E 列填「—」
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-26--futures-cancel` 退出码 0
