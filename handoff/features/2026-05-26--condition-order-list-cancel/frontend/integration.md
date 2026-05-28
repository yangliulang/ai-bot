# 前端对接

> **含页面：否** — 无 Admin/Deeplink 变更。`frontend.integrate` 空跑完成。

## 联调结论

| 项 | 值 |
|----|-----|
| 路由 | 无（brief 明确无页面） |
| 关键文件 | 无 |
| API 客户端 | 无；Runtime/TG/HTTP 直连后端 |
| Mock → 真实 API | 不适用（未建 Mock 页） |
| 联调日期 | 2026-05-27 |
| 后端 Base URL | http://127.0.0.1:8080（见 `backend/notes.md`） |

## 接口映射（供调用方参考，非 Admin 实现）

| 场景 | Method | Path | 说明 |
|------|--------|------|------|
| 条件单列表 | GET | `/api/v1/agent/trade/futures/condition-orders` | Query: `userId`、可选 `symbol`；200 含 `scenarioId=automation.condition_orders_read`、`orders`、`totalOpenOrders` |
| 撤销条件单 | POST | `/api/v1/agent/trade/futures/cancel-condition` | Body: `userId`、`symbol`、`orderId`；200 含 `scenarioId=automation.condition_order_cancel` |

错误态（403 `AGENT_SUBACCOUNT_REQUIRED` / `FEATURE_AGENT_FUTURES_OFF`、502 `AGENT_FUTURES_OPEN_ORDERS_FAILED`、400 `AGENT_FUTURES_CANCEL_REJECTED`）见 `api.openapi.yaml` 与 `backend/notes.md` curl 示例。

**边界**：普通合约撤单 **`POST …/futures/cancel`** 归属 **`2026-05-26--futures-cancel`**，本包不实现 Admin 对接。

## 联调自检

- [x] **主流程**：无 FE 路由；API P0 已由 test-agent 在 `test/report.md` 覆盖（pytest 13 passed，P0 TC-01～08）
- [x] **错误态**：同上（403/400/502）；无页面级错误 UI
- [x] **加载态**：不适用
- [x] **Observability**：`admin/` 未注册 `automation.condition_orders_read` / `automation.condition_order_cancel` 专用页；执行时间线走存量编排展示（本包未改 `admin/`、`deeplink/` 源码）

## 代码变更

无。`admin/`、`deeplink/` 未检出对 `condition-orders` / `cancel-condition` 的新路由、API 客户端或 Mock 页面。

## 备注

- 用户触达：HTTP API、Runtime 意图（`ROUTE_READ_SKILL` / `CONFIRM_TYPE_A`）、Telegram `ccp`/`ccx`；契约见功能包 `api.openapi.yaml`。
- 下一步：test-agent 执行 `test.e2e`，在 `test/e2e-report.md` 标 **N/A** 后推进 `e2e_verified`（与 `trading-reconcile` 一致）。
