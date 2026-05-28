# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-26--trading-reconcile` |
| 含页面（需 E2E） | 否 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 页面行为 |
|----|------|----------|----------|-------------------|
| AC-1 | POST 改单半失败对账 200 | TC-01 | — | `POST …/trading/reconcile` |
| AC-2 | GET status 回显最近对账 | TC-02 | — | `GET …/reconcile/status` |
| AC-3 | GET status 待对账 UNKNOWN | TC-03 | — | `GET …/status` · unknown 时间线 |
| AC-4 | 未绑定 403 | TC-04 | — | `AGENT_SUBACCOUNT_REQUIRED` |
| AC-5 | execution 404 | TC-05 | — | `AGENT_RECONCILE_EXECUTION_NOT_FOUND` |
| AC-6 | 无查单目标 422 | TC-06 | — | `AGENT_RECONCILE_NO_QUERY_TARGETS` |
| AC-7 | 时间线 trading.reconcile | TC-07 | — | 事件 payload |
| AC-8 | 改单 502 reconcileSuggested | TC-08 | — | `POST …/amend-limit-order` 502 details |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| POST | /api/v1/agent/trading/reconcile | TC-01, TC-04, TC-05, TC-06, TC-07 |
| GET | /api/v1/agent/trading/reconcile/status | TC-02, TC-03, TC-05 |
| POST | /api/v1/agent/trade/spot/amend-limit-order | TC-08 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 无页面，E2E 列不适用
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-26--trading-reconcile` 退出码 0
