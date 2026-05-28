# 前端对接说明

> 前端 Agent · `frontend.integrate` · 2026-05-26  
> 本功能 **无 Admin / Deeplink 页面**（`brief.md` · `含页面: 否`）。联调阶段 **无 `admin/` / `deeplink/` 代码变更**。

## 页面与路由

| 页面 | 路由 | 说明 |
|------|------|------|
| — | — | **不适用**（本期仅 API + Telegram；`/ai-settings` 开关属后续 FE 包） |

## 后续 FE（非本包）

| 页面 | 路由 | API | 说明 |
|------|------|-----|------|
| AI 使用策略 | `/ai-settings` · Tab「使用策略」 | `GET|PATCH /api/v1/admin/ai/defaults` | 可增加「意图 NLU 优先 LLM」→ body `intentNluUseLlm` |

## 接口映射（本包交付面）

无新控制台路由；行为经 **Admin API**、**Agent intent** 与 **Telegram 已绑定会话** 触达。

| 场景 | API | 方法 | 关键字段 |
|------|-----|------|----------|
| 读取网关默认 | `/api/v1/admin/ai/defaults` | GET | `intentNluUseLlm`（合并默认 `false`） |
| 开启 Admin 侧 LLM NLU | `/api/v1/admin/ai/defaults` | PATCH | `{ "intentNluUseLlm": true }`；`If-Match` 与存量一致 |
| 意图识别（HTTP） | `/api/v1/agent/intent/recognize` | POST | `nluSource` / `nlu.source`；`effectiveIntentNluUseLlm` |
| Telegram 已绑定文本 | `recognize_intent_full`（webhook 内联） | — | 时间线 `prompt.snapshot` · `intentNluLlmEnabled` = **effective** |

有效策略：**env `CHAINUP_AGENT_INTENT_NLU_USE_LLM=true`** 优先于 **`gateway_defaults.intentNluUseLlm`**。详见 `brief.md`、`backend/notes.md`。

## 实现文件

| 路径 | 变更 |
|------|------|
| `admin/` | **无** |
| `deeplink/` | **无** |

## Mock 切换

- Mock 阶段：无页面，未建 Mock。
- 联调：不适用；**API P0 已由 test-agent 验收**（`test/report.md` · `pytest tests/test_nlu_llm_strategy.py` 9 passed）。

## 联调结果

- [x] **主流程**：无 UI；`intentNluUseLlm` 读写、recognize LLM/keyword/回退/env 覆盖、TG timeline effective 已在 API 测试覆盖（TC-01～TC-08）。
- [x] **错误态**：NLU 失败均为 200 + `keyword_v1`（TC-03/08）；Admin PATCH 422/409 与存量 defaults 一致（TC-01 语境）。
- [x] **门禁例外**：`brief` 无页面 → 不要求 Admin dev 可访问；`frontend_done` 表示 **联调任务 N/A 已收口**。

## 联调环境

- API：`cd server && uv run chainup-agent-api` → http://127.0.0.1:8080/health
- Admin dev：**未启动**（本包无联调页面；线上 Admin defaults 需 Bearer）

## 遗留问题

- `/ai-settings` UI 开关与文案：**后续 FE 包**（见 `brief.md` 本期不包含）。
