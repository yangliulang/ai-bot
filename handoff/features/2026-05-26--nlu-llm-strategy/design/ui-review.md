# UI 走查 — 2026-05-26--nlu-llm-strategy

> designer.review · 2026-05-26

## 走查范围

- **无 Admin / Deeplink 本期页面**（`brief.md` · `含页面: 否`；`intentNluUseLlm` 经 **Admin API** / env 配置）
- **`/ai-settings`「意图 NLU 优先 LLM」开关** 属 **后续 FE 包**（见 `frontend/integration.md`）
- 用户触达：**HTTP `POST …/intent/recognize`**、**Telegram 已绑定文本**（时间线 `intentNluLlmEnabled` = effective）
- Admin Runtime 若展示 NLU 来源依赖既有观测组件，**非本包 UI 交付**

## 环境

- 浏览器走查：**未执行**（无目标路由）
- 依据：`test/e2e-report.md`（E2E N/A）、`test/report.md`（API P0 全通过）、`frontend/integration.md`

## 检查项

| # | 项 | 级别 | 结果 | 备注 |
|---|-----|------|------|------|
| 1 | brief 是否定义页面/路由 | P0 | N/A | 无界面说明，走查不适用 |
| 2 | 信息架构与路由一致 | P0 | N/A | — |
| 3 | 主流程组件状态（loading/空/错） | P0 | N/A | AC 在 API 层验收 |
| 4 | 策略开关文案与状态反馈 | P0 | 委托后续 FE | 本期无 `/ai-settings` 控件 |
| 5 | NLU 失败用户可感知（非 5xx） | P0 | 委托 API | TC-03/08：200 + `keyword_v1` 回退 |
| 6 | 与设计规范 / tokens 一致 | P1 | N/A | 无 UI |

## 问题清单

| ID | 级别 | 摘要 | 负责人 |
|----|------|------|--------|
| — | — | 无 P0 | — |

## 结论

- [x] **通过**（无 UI，走查 N/A）
- [ ] 不通过

本包为 **API + 运行时策略** 能力；视觉与交互门禁由 **API 测试 + 产品验收** 承接。后续 FE 包落地 `/ai-settings` 开关时建议 **单独走查** 开关文案、禁用态说明与保存反馈（If-Match 冲突提示与存量 defaults 页一致）。

## 下一棒

- **已收口** · `phase: done`（product.accept 2026-05-26）
