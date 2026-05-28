# 后端说明 — 2026-05-26--trading-reconcile

> §6 存量实现 · 契约核对完成 · `backend_done`

## 启动与环境

| 项 | 值 |
|----|-----|
| 启动 | `cd server && uv run chainup-agent-api` |
| Base URL | http://127.0.0.1:8080 |
| 机器可读契约 | http://127.0.0.1:8080/openapi.json |
| 功能包 OpenAPI | `handoff/features/2026-05-26--trading-reconcile/api.openapi.yaml` |

## 实现位置

| 层 | 模块 |
|----|------|
| Router | `chainup_agent/api/routers/v1/agent_trading_reconcile.py` |
| 应用 | `chainup_agent/application/agent_trading_reconcile.py` |
| 领域 | `chainup_agent/domain/trading_reconcile.py` |
| 改单对账引导 | `chainup_agent/application/agent_spot_trade.py`（502 `details.reconcile*`） |

## 路由与错误码

| Method | Path | 成功 | 主要错误 |
|--------|------|------|----------|
| POST | `/api/v1/agent/trading/reconcile` | 200 camelCase body | 403 `AGENT_SUBACCOUNT_REQUIRED` · 404 `AGENT_RECONCILE_EXECUTION_NOT_FOUND` · 422 `AGENT_RECONCILE_NO_QUERY_TARGETS` / `VALIDATION_ERROR` |
| GET | `/api/v1/agent/trading/reconcile/status` | 200 | 404 `AGENT_RECONCILE_EXECUTION_NOT_FOUND` |

**200 响应**：直出 `reconcileId`、`caseKind`、`resolutionStatus`、`stillUnknown`、`neutralHint`、`userMessage`、`orderLookups[]`（非 `{ code:0, data }` 信封）。

**时间线**：成功对账写入 `trading.reconcile`（payload 含 `reconcileId`、`caseKind`、`resolutionStatus`）。

## curl 示例

```bash
# 待对账（时间线有 unknown 写、尚无 reconcile）
curl -s 'http://127.0.0.1:8080/api/v1/agent/trading/reconcile/status?userId=YOUR_TG_ID&executionId=YOUR_EXEC_ID'

# 发起对账
curl -s -X POST http://127.0.0.1:8080/api/v1/agent/trading/reconcile \
  -H 'Content-Type: application/json' \
  -d '{"userId":"YOUR_TG_ID","executionId":"YOUR_EXEC_ID"}'
```

## 自测（pytest）

```bash
cd server && uv run pytest tests/test_trading_reconcile.py tests/test_spot_amend_trade.py::test_spot_amend_cancel_ok_replace_fail -q
```

2026-05-26 本地：**9 passed**（`test_trading_reconcile.py` 8 + amend reconcileSuggested 1）。

## 与功能包 OpenAPI 差异

| 项 | 说明 |
|----|------|
| `reconcilePath`（改单 502） | 实现与契约均为 **`/api/v1/agent/trading/reconcile`**（无 `POST` 前缀；2026-05-26 自 `agent_spot_trade` 对齐 OpenAPI） |
| 其余 | 无 — 路径、字段 alias、错误码与 `api.openapi.yaml` 一致 |

## 关联文档

- `server/docs/BACKEND_SPEC.md` §6
- `server/docs/API_INTEGRATION_GUIDE.md` §4.3d
