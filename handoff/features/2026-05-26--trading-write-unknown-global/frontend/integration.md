# 前端对接说明

> 前端 Agent · `frontend.integrate` · 2026-05-26  
> 本功能 **无 Admin / Deeplink 页面**（`brief.md` 不含界面说明）。联调阶段 **无 `apps/web/` / `admin/` 代码变更**。

## 页面与路由

| 页面 | 路由 | 说明 |
|------|------|------|
| — | — | **不适用**（纯 API / Telegram 话术；Admin Runtime 展示依赖既有组件，非本包交付） |

## 接口映射（用户触达面）

本包行为经 **Agent HTTP 写** 与 **`AppError`** 返回；无控制台新路由。

| 场景 | API | 方法 | 成功 | UNKNOWN（502） |
|------|-----|------|------|----------------|
| 现货限价写 | `/api/v1/agent/trade/spot/limit-order` | POST | 200 | `AGENT_EXCHANGE_WRITE_UNKNOWN` |
| 现货撤单 | `/api/v1/agent/trade/spot/cancel` | POST | 200 | 同上 |
| 合约下单/撤单 | `/api/v1/agent/trade/futures/order` · `…/cancel` | POST | 200 | 同上 |
| 杠杆下单 | `/api/v1/agent/trade/margin/order` | POST | 200 | 同上 |
| 条件单/撤 | `/api/v1/agent/trade/futures/condition-order` · `…/cancel-condition` | POST | 200 | 同上 |
| 对账（存量） | `/api/v1/agent/trading/reconcile` · `…/status` | POST · GET | 200 | 回归 AC-7 |

OpenAPI 与 curl 见 `api.openapi.yaml`、`backend/notes.md`。

## 实现文件

| 路径 | 变更 |
|------|------|
| `admin/` | **无** |
| `deeplink/` | **无** |
| `apps/web/` | **无** |

## Mock 切换

- Mock 阶段：无页面，未建 Mock。
- 联调：不适用；**API P0 已由 test-agent 在 `test/report.md` 覆盖**（`pytest` 19 passed）。

## 联调结果

- [x] **主流程**：无 UI；HTTP UNKNOWN / 时间线 / reconcile / finalize 已在 API 测试验收（TC-01～TC-09）。
- [x] **错误态**：502 + `exchangeOutcome=unknown` 与拒单对照（TC-08）已在 API 层验证。
- [x] **门禁例外**：`brief` 无页面 → 不要求 Admin dev 可访问；`frontend_done` 表示 **联调任务 N/A 已收口**。

## 联调环境

- API：`cd server && uv run chainup-agent-api` → http://127.0.0.1:8080/health
- Admin dev：**未启动**（本包无联调页面）

## 遗留问题

- Telegram callback 写路径话术 **P1**（见 `brief.md` Q2），不在本包 Admin 范围。
