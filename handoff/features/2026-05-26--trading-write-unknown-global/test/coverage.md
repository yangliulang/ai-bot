# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-26--trading-write-unknown-global` |
| 含页面（需 E2E） | 否 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | `post_signed_*` 写 504/超时 → UNKNOWN | TC-01 | — | `AppErrorExchangeWriteUnknown` |
| AC-2 | 现货 HTTP 写 + 时间线 unknown | TC-02 | — | `POST …/spot/limit-order` 502 |
| AC-3 | 现货撤单 unknown | TC-03 | — | `POST …/spot/cancel` 502 |
| AC-4 | 合约下单/撤单 unknown | TC-04 | — | `POST …/futures/order` · `…/cancel` |
| AC-5 | 杠杆下单 unknown | TC-05 | — | `POST …/margin/order` |
| AC-6 | 条件单写/撤 unknown | TC-06 | — | `…/condition-order` · `…/cancel-condition` |
| AC-7 | UNKNOWN 后可对账 / status | TC-07 | — | `POST|GET …/trading/reconcile*` |
| AC-8 | 拒单 ≠ UNKNOWN | TC-08 | — | `AppErrorRejected` |
| AC-9 | execution finalize UNKNOWN | TC-09 | — | HTTP 写失败终态 |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| POST | /api/v1/agent/trade/spot/limit-order | TC-02 |
| POST | /api/v1/agent/trade/spot/cancel | TC-03 |
| POST | /api/v1/agent/trade/futures/order | TC-04 |
| POST | /api/v1/agent/trade/futures/cancel | TC-04 |
| POST | /api/v1/agent/trade/margin/order | TC-05 |
| POST | /api/v1/agent/trade/futures/condition-order | TC-06 |
| POST | /api/v1/agent/trade/futures/cancel-condition | TC-06 |
| POST | /api/v1/agent/trading/reconcile | TC-07 |
| GET | /api/v1/agent/trading/reconcile/status | TC-07 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 无页面，E2E 不适用
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-26--trading-write-unknown-global` 退出码 0
