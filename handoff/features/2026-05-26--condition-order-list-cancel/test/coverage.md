# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-26--condition-order-list-cancel` |
| 含页面（需 E2E） | 否 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | GET 条件单列表过滤 | TC-01 | — | `GET …/condition-orders` |
| AC-2 | GET 可选 symbol | TC-02 | — | Query `symbol` |
| AC-3 | POST 撤销条件单 | TC-03 | — | `POST …/cancel-condition` |
| AC-4 | 未绑定 403 | TC-04 | — | `AGENT_SUBACCOUNT_REQUIRED` |
| AC-5 | 功能关闭 403 | TC-05 | — | `FEATURE_AGENT_FUTURES_OFF` |
| AC-6 | openOrders 502 | TC-06 | — | `AGENT_FUTURES_OPEN_ORDERS_FAILED` |
| AC-7 | 撤单拒单 400 | TC-07 | — | `AGENT_FUTURES_CANCEL_REJECTED` |
| AC-8 | 意图路由读/撤 | TC-08 | — | `POST …/intent/recognize` |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/agent/trade/futures/condition-orders | TC-01, TC-02, TC-04, TC-05, TC-06 |
| POST | /api/v1/agent/trade/futures/cancel-condition | TC-03, TC-04, TC-05, TC-07 |

## 相关存量测试（非本包 path）

| 文件 | 说明 |
|------|------|
| `test_condition_trade.py` | **创建** 条件单 `POST …/condition-order` — **不在** 本包 OpenAPI |
| `test_futures_cancel_condition_trade.py::test_futures_cancel_http_success` | 普通合约撤单 — 归 **`futures-cancel`** 包 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 无页面，E2E 列填「—」
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-26--condition-order-list-cancel` 退出码 0
