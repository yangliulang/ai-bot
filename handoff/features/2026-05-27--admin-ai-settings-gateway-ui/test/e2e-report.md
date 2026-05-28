# E2E / 页面验证报告

> 测试 Agent 在 `frontend_done` 后执行并填写，通过后推进 status 至 `e2e_verified`（next: designer-agent）。

## 概要

- 执行时间：2026-05-27
- 执行人：test-agent
- 环境：
  - 前端：`http://127.0.0.1:5173`（`admin` dev · Vite proxy → API）
  - 后端 API：`http://127.0.0.1:8080`（`/health` → 200）
  - 登录态：浏览器已有 `tg_admin_access_token`（控制台已登录）
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 5（P0×4 + P1×1） | 4 | 0 | 1（P1） | 0 |

## P0 用例明细

| 用例 ID | 关联 AC | 场景 | 结果 | 实际 |
|---------|---------|------|------|------|
| E2E-01 | AC-1, AC-2, AC-6, AC-8 | 网关策略分区加载 | 通过 | `/ai-settings?tab=runtime` 可见 region **网关策略**、**意图 NLU**、**Telegram LLM 叙述**；9 行（5 只读 + 4 Type-A）；env 说明含 `CHAINUP_AGENT_INTENT_NLU_USE_LLM` 与 ticker narrate 示例；加载后开关可操作 |
| E2E-02 | AC-3 | NLU 开关保存 | 通过 | 切换 **意图 NLU 优先 LLM** → 出现「保存中…」→ 勾选保持；整页刷新后仍为开；API `intentNluUseLlm=true` |
| E2E-03 | AC-4 | 单场景 narrate 保存 | 通过 | 开启 **行情 · 最新价**（`readMarketTicker`）→「保存 readMarketTicker…」；**readMarketDepth** 仍为开、**readMarketTrades** 仍关；刷新后回显一致；API `telegramLlmNarrate.readMarketTicker=true` |
| E2E-04 | AC-5 | 错误展示 | 跳过（P1） | 未构造 422/409；网关 PATCH 成功路径已验；错误 Toast 逻辑与 `adminToastError` 一致（API 层 TC-04 已覆盖 422） |
| E2E-05 | AC-7 | 存量使用策略保存 | 通过 | **普通问答** 由 DeepSeek 改为 `Pro/moonshotai/Kimi-K2.6` → 点击底部 **保存**（submitting）→ API `scenarioChatModel` 已更新；保存过程中 **网关策略** 分区仍可见 |

## 验收对照（brief.md · 页面）

- [x] 主流程：加载 → 改 NLU / narrate → 保存 → 回显
- [x] 加载态：首屏 loading；网关/存量保存 submitting（禁用开关或保存按钮 busy）
- [ ] 错误态 PATCH 失败可见 `message`（P1 E2E-04 未跑；API TC-04/422 已覆盖）

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- E2E-05 前置：临时启用 catalog 模型 `Pro/moonshotai/Kimi-K2.6`（原 disabled）以便切换 **普通问答** 下拉；不影响网关字段验收。
- 下一 Chat：**`/pipeline-designer-review 2026-05-27--admin-ai-settings-gateway-ui`**（`design/ui-review.md` 走查）。
