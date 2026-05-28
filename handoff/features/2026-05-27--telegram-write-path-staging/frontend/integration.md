# 前端对接

> **含页面：否** — 无 Admin/Deeplink 变更。`frontend.integrate` 空跑完成。

## 联调结论

| 项 | 值 |
|----|-----|
| 路由 | 无（brief 明确无页面） |
| 关键文件 | 无 |
| API 客户端 | 无；staging 走读可选用存量 Observability 执行详情页 **只读** 导出时间线 |
| Mock → 真实 API | 不适用 |
| 联调日期 | 2026-05-28 |
| 后端 Base URL | 预发 URL 记入 `staging/evidence-log.md` §1（本机代理见 `test/report.md`） |

## 接口映射（供走读参考，非 FE 实现）

| 场景 | Method | Path | 说明 |
|------|--------|------|------|
| 时间线对拍 | GET | `/api/v1/admin/observability/executions/{executionId}/timeline` | staging §2 `executionId`；可用 `scripts/verify_timeline_order.py` |
| 健康探活 | GET | `/health` | 走读前可选 |

Telegram 写路径 **无** HTTP path；见 `staging/walkthrough.md`。

## 联调自检

- [x] **主流程**：无 FE 路由；pytest 代理 **7 passed**（`test/report.md` TC-03）
- [x] **错误态**：不适用（无页面）
- [x] **加载态**：不适用
- [x] **Observability**：可走读存量执行详情页辅助导出；本包 **未改** `admin/`、`deeplink/` 源码

## 代码变更

无。`admin/`、`deeplink/` 未检出与本功能包相关的新路由、客户端或 Mock 页。

## 备注

- **Blockers**：`staging/evidence-log.md` 待所内预发填写 → **`product.accept` 前必清**。
- 下一步：test-agent **`/pipeline-test-e2e`**（E2E N/A）→ designer → product accept（须 evidence 完整）。
