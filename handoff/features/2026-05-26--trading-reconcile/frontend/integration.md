# 前端对接

> **含页面：否** — 无 Admin/Deeplink 变更。`frontend.integrate` 空跑完成。

## 联调结论

| 项 | 值 |
|----|-----|
| 路由 | 无（brief 明确无页面） |
| 关键文件 | 无 |
| API 客户端 | 无；Runtime/TG/HTTP 直连后端 |
| Mock → 真实 API | 不适用（未建 Mock 页） |
| 联调日期 | 2026-05-26 |
| 后端 Base URL | http://127.0.0.1:8080（见 `backend/notes.md`） |

## 接口映射（供调用方参考，非 Admin 实现）

| 场景 | Method | Path | 说明 |
|------|--------|------|------|
| 发起对账 | POST | `/api/v1/agent/trading/reconcile` | Body: `userId`, `executionId`；200 camelCase 直出 |
| 对账状态 | GET | `/api/v1/agent/trading/reconcile/status` | Query: `userId`, `executionId` |
| 改单半失败引导 | — | `details.reconcilePath` | 502 `AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED` → 同上 POST 路径 |

错误态（403/404/422）见 `api.openapi.yaml` 与 `backend/notes.md` curl 示例。

## 联调自检

- [x] **主流程**：无 FE 路由；API P0 已由 test-agent 在 `test/report.md` 覆盖（pytest 9 passed）
- [x] **错误态**：同上（403/404/422）；无页面级错误 UI
- [x] **加载态**：不适用
- [x] **Observability**：Admin 时间线消费存量 `trading.reconcile` 事件，本包未改 `admin/` 源码

## 代码变更

无。`admin/`、`deeplink/` 未检出对 `trading/reconcile` 的对接或 Mock 页面。

## 备注

- 用户触达：HTTP API、Runtime/TG 编排；契约见功能包 `api.openapi.yaml`。
- 下一步：test-agent 执行 `test.e2e`，在 `test/e2e-report.md` 标 **N/A** 后推进 `e2e_verified`（与 `trading-write-unknown-global` 一致）。
