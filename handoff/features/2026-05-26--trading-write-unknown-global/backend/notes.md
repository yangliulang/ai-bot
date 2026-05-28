# 后端实现说明

> backend.implement · 2026-05-26

## 实现摘要

| 项 | 状态 |
|----|------|
| `raise_exchange_write_unknown` / `check_exchange_write_http_unknown` | ✅ `coobit_openapi.py` |
| 全部 `post_signed_*` 写（spot/futures/margin/condition/cancel）504+超时 | ✅ |
| 时间线 `exchangeOutcome=unknown` + `appErrorCode` | ✅ 各 `agent_*_trade` |
| HTTP `execution_finalize` → **UNKNOWN** | ✅ `agent_trade_http_finalize.py` + trade 路由 |
| `GET …/reconcile/status` 识别 payload unknown 写 | ✅ `agent_trading_reconcile.py` |
| pytest `test_trading_write_unknown_global.py` | ✅ |

## 启动

```bash
cd server && uv run chainup-agent-api
# health: http://127.0.0.1:8080/health
```

## 鉴权

- Agent trade / reconcile：Body/Query **`userId`**（tg_id）+ 托管绑定（`POST /api/v1/agent/api-binding/confirm`）。

## 错误码（写路径 UNKNOWN）

| HTTP | code | 说明 |
|------|------|------|
| 502 | `AGENT_EXCHANGE_WRITE_UNKNOWN` | 504 或写超时；`details.exchangeOutcome=unknown` |
| 400 | `AGENT_*_ORDER_REJECTED` | 交易所明确拒单（**非** UNKNOWN） |

## curl 示例（需已绑定用户）

```bash
# 现货限价写失败（UNKNOWN 时）
curl -s -X POST http://127.0.0.1:8080/api/v1/agent/trade/spot/limit-order \
  -H 'Content-Type: application/json' \
  -d '{"userId":"YOUR_TG_ID","symbol":"BTC-USDT","side":"BUY","volume":"0.01","price":"48000","timeInForce":"GTC"}'

# 对账状态（时间线含 unknown 写且尚无 reconcile 事件）
curl -s 'http://127.0.0.1:8080/api/v1/agent/trading/reconcile/status?userId=YOUR_TG_ID&executionId=exec-xxx'

# 发起对账
curl -s -X POST http://127.0.0.1:8080/api/v1/agent/trading/reconcile \
  -H 'Content-Type: application/json' \
  -d '{"userId":"YOUR_TG_ID","executionId":"exec-xxx"}'
```

## 自动化

```bash
cd server && uv run pytest \
  tests/test_trading_write_unknown_global.py \
  tests/test_trading_reconcile.py -q
```

## 关键文件

| 文件 | 说明 |
|------|------|
| `infrastructure/exchange/coobit_openapi.py` | 签名写 UNKNOWN |
| `application/agent_trade_http_finalize.py` | HTTP finalize UNKNOWN |
| `application/agent_trading_reconcile.py` | status 检测 payload unknown |
| `api/routers/v1/agent_trade_*.py` | 写路由 finalize |
| `tests/test_trading_write_unknown_global.py` | P0 回归 |
