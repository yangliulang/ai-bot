# UI 走查 — 2026-05-26--futures-cancel

> designer.review · 2026-05-28

## 走查范围

- **无 Admin / Deeplink 页面**（`brief.md` · `test/coverage.md` `含页面: 否`）
- 用户触达经 **HTTP JSON**（`scenarioId` / `exchangeOrderPreview` / `AppError.code`）与 **Runtime/TG 编排**（`trade.futures.cancel_order` · `EXECUTE_FUTURES_CANCEL`）
- Admin 时间线 **`cancel_order`** 展示与现货撤单类似；无 `trade.futures.cancel_order` 专用路由（本包未改 `admin/`）

## 环境

- 浏览器走查：**未执行**（无目标路由）
- 依据：`test/e2e-report.md`（E2E N/A）、`test/report.md`（API P0 全通过）、`frontend/integration.md`

## 检查项

| # | 项 | 级别 | 结果 | 备注 |
|---|-----|------|------|------|
| 1 | brief 是否定义页面/路由 | P0 | N/A | 无界面说明，走查不适用 |
| 2 | 信息架构与路由一致 | P0 | N/A | — |
| 3 | 主流程组件状态（loading/空/错） | P0 | N/A | AC 在 API 层验收 |
| 4 | 撤单成功字段与 `scenarioId` | P0 | 委托 API | TC-01；`trade.futures.cancel_order` |
| 5 | 未绑定 / 功能开关 / 拒单 / 校验错误 | P0 | 委托 API | TC-02～05 |
| 6 | 意图 `EXECUTE_FUTURES_CANCEL` | P0 | 委托 API | TC-06 |
| 7 | 与设计规范 / tokens 一致 | P1 | N/A | 无 UI |

## 问题清单

| ID | 级别 | 摘要 | 负责人 |
|----|------|------|--------|
| — | — | 无 P0 | — |

## 结论

- [x] **通过**（无 UI，走查 N/A）
- [ ] 不通过

本包为 **存量合约普通撤单 HTTP 契约收口**（`POST …/trade/futures/cancel`）；视觉与交互门禁由 **API 测试 + 产品验收** 承接。无阻塞项。

## 下一棒

- **已收口** · `phase: done`（product.accept 2026-05-28）
