# 前端对接说明

> 前端 Agent · `frontend.integrate` · 2026-05-26  
> 本功能 **无 Admin / Deeplink 页面**（`brief.md` · `含页面: 否`）。联调阶段 **无 `admin/` / `deeplink/` 代码变更**。

## 页面与路由

| 页面 | 路由 | 说明 |
|------|------|------|
| — | — | **不适用**（本期仅 API + Telegram webhook；`/ai-settings` 九场景 narrate 开关属后续 FE 包） |

## 后续 FE（非本包）

| 页面 | 路由 | API | 说明 |
|------|------|-----|------|
| AI 使用策略 | `/ai-settings` · Tab「使用策略」 | `GET\|PATCH /api/v1/admin/ai/defaults` | 可增加 `telegramLlmNarrate.*` 九场景开关 UI |

## 接口映射（本包交付面）

无新控制台路由；行为经 **Admin API** 与 **Telegram 已绑定会话** 触达。

| 场景 | API | 方法 | 关键字段 |
|------|------|------|----------|
| 读取 narrate 策略 | `/api/v1/admin/ai/defaults` | GET | `telegramLlmNarrate`（九键，默认均 `false`） |
| 按场景开启 narrate | `/api/v1/admin/ai/defaults` | PATCH | `{ "telegramLlmNarrate": { "readMarketTicker": true } }` 等；嵌套深度合并；`If-Match` 与存量一致 |
| Telegram 只读 / Type-A | webhook 内联 | — | `resolve_effective_telegram_llm_narrate`；时间线 `summary.effectiveTelegramLlmNarrateEnabled` |

有效策略（每场景独立）：**env `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_*=true`** 优先于 **`gateway_defaults.telegramLlmNarrate.<field>`**。详见 `brief.md`、`backend/notes.md`。

## 实现文件

| 路径 | 变更 |
|------|------|
| `admin/` | **无** |
| `deeplink/` | **无** |

## Mock 切换

- Mock 阶段：无页面，未建 Mock。
- 联调：不适用；**API P0 已由 test-agent 验收**（`test/report.md` · `pytest tests/test_telegram_llm_narrate.py` 10 passed）。

## 联调结果

- [x] **主流程**：无 UI；Admin defaults 读写、TG ticker narrate 启用/关闭/回落/env 覆盖、depth spot-check、timeline effective 已在 API 测试覆盖（TC-01～TC-08）。
- [x] **错误态**：narrate LLM 失败仍为确定性文案 + webhook 200（TC-03）；Admin PATCH 422 未知键（TC-10 语境）与存量校验一致。
- [x] **门禁例外**：`brief` 无页面 → 不要求 Admin dev 可访问；`frontend_done` 表示 **联调任务 N/A 已收口**。

## 联调环境

- API：`cd server && uv run chainup-agent-api` → http://127.0.0.1:8080/health
- Admin dev：**未启动**（本包无联调页面；线上 Admin defaults 需 Bearer）

## 遗留问题

- `/ai-settings` 九场景 narrate UI：**后续 FE 包**（见 `brief.md` 本期不包含）。
