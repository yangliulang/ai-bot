# 前端对接

> **含页面：否** — 无 Admin/Deeplink 变更。`frontend.integrate` 空跑完成。

## 联调结论

| 项 | 值 |
|----|-----|
| 路由 | 无（brief 明确无页面） |
| 关键文件 | 无 |
| API 客户端 | 无；Runtime/TG/HTTP 直连后端 |
| Mock → 真实 API | 不适用（未建 Mock 页） |
| 联调日期 | 2026-05-28 |
| 后端 Base URL | http://127.0.0.1:8080（见 `backend/notes.md`） |

## 接口映射（供调用方参考，非 Admin 实现）

| 场景 | Method | Path | 说明 |
|------|--------|------|------|
| 合约撤单 | POST | `/api/v1/agent/trade/futures/cancel` | Body: `userId`、`symbol`、`orderId`；200 含 `scenarioId=trade.futures.cancel_order` |

错误态（403 `AGENT_SUBACCOUNT_REQUIRED` / `FEATURE_AGENT_FUTURES_OFF`、400 `AGENT_FUTURES_CANCEL_REJECTED`、422 `VALIDATION_ERROR`）见 `api.openapi.yaml` 与 `backend/notes.md` curl 示例。

**边界**：条件单查/撤 **`GET …/condition-orders`**、**`POST …/cancel-condition`** 归属 **`2026-05-26--condition-order-list-cancel`**，本包不实现 Admin 对接。

## 联调自检

- [x] **主流程**：无 FE 路由；API P0 已由 test-agent 在 `test/report.md` 覆盖（pytest 9 passed，P0 TC-01～07）
- [x] **错误态**：同上（403/400/422）；无页面级错误 UI
- [x] **加载态**：不适用
- [x] **Observability**：`admin/` 无 `trade.futures.cancel_order` 专用页；时间线 `cancel_order` 展示与现货撤单类似，本包未改 `admin/`、`deeplink/` 源码

## 代码变更

无。`admin/`、`deeplink/` 未检出对 `POST …/trade/futures/cancel` 的新路由、API 客户端或 Mock 页面。

## 备注

- 用户触达：HTTP API、Runtime 意图（`EXECUTE_FUTURES_CANCEL`）、Telegram 绑定会话内直接撤单。
- 下一步：test-agent 执行 `test.e2e`，在 `test/e2e-report.md` 标 **N/A** 后推进 `e2e_verified`。
