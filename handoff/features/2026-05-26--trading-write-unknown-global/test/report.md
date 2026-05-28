# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-26
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · SQLite 测试库 · `CHAINUP_AGENT_FEATURE_*` 默认开启
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 10（P0×9 + P1×1） | 10 | 0 | 0 | 0 |

自动化：`uv run pytest tests/test_trading_write_unknown_global.py tests/test_trading_reconcile.py -q` → **19 passed**（含对账回归与扩面用例）。

## 用例执行明细

| ID | 优先级 | 结果 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | 通过 | `test_post_signed_spot_order_json_504_raises_unknown`；`test_post_signed_writes_504_param_tc01_ac4_ac6`（futures order/cancel、margin、condition Coobit 写） |
| TC-02 | P0 | 通过 | `test_spot_limit_order_http_unknown_timeline_and_finalize`（502、`exchangeOutcome=unknown` 时间线、finalize `UNKNOWN`） |
| TC-03 | P0 | 通过 | `test_spot_cancel_http_unknown_tc03` |
| TC-04 | P0 | 通过 | `test_futures_order_http_unknown_tc04`、`test_futures_cancel_http_unknown_tc04` + Coobit 参数化 |
| TC-05 | P0 | 通过 | `test_margin_order_http_unknown_tc05`（需 mock 行情 `fetch_spot_public_ticker_json_with_fallbacks`） |
| TC-06 | P0 | 通过 | `test_futures_condition_order_http_unknown_tc06` + Coobit 参数化含 `post_signed_futures_cancel_json`（条件单撤与普通撤同 PATH） |
| TC-07 | P0 | 通过 | TC-02 内 reconcile + `test_trading_reconcile.py` 状态 `UNKNOWN` |
| TC-08 | P0 | 通过 | `test_spot_limit_order_rejected_not_unknown` |
| TC-09 | P0 | 通过 | TC-02 内 `execution_finalize` outcome=`UNKNOWN` |
| TC-10 | P1 | 通过 | `test_post_signed_spot_cancel_timeout_raises_unknown` |

## 契约抽查

- **502 错误体**：HTTP 用例断言 `code=AGENT_EXCHANGE_WRITE_UNKNOWN`、`status=502`；Coobit 层断言 `details.exchangeOutcome=unknown` 与 `path` 与 OpenAPI 示例一致。
- **中性文案**：`raise_exchange_write_unknown` / HTTP 响应 `message` 不含「已成功」「已失败」终态断言（人工对照 `coobit_openapi.py` 与 TC-02 响应）。

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- **无 Admin/Deeplink 页面**（`frontend/integration.md` 标明不适用）。流程上 `status.yaml` 仍按标准置 `next: frontend-agent`；建议指挥官执行 **`/pipeline-frontend-integrate`** 时由 frontend-agent **空跑标记 `frontend_done`**（无代码变更），再 **`/pipeline-test-e2e`** 对 E2E 矩阵记 **N/A** 或仅 API 回归，最后 **designer / product** 收口。
- 本轮回补 `server/tests/test_trading_write_unknown_global.py` 中 TC-03～TC-06 HTTP 与多品种 Coobit 504 参数化用例。
