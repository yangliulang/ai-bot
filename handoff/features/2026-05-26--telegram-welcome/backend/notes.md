# 后端实现说明

## 实现摘要

| 项 | 位置 |
|----|------|
| 语言桶 + 回退链 | `server/chainup_agent/application/telegram_activation_welcome.py` → `resolve_activation_welcome_text` |
| `{displayName}` 渲染 | 同上 → `render_activation_welcome` |
| 幂等（每 tg_id 一次） | `agent_instance.activation_welcome_sent_at`；迁移 `0028_agent_instance_activation_welcome` |
| 绑定后发送 | `confirm_agent_trading_api_binding` commit 后 `dispatch_activation_welcome`（best-effort） |
| 响应字段 | `ConfirmAgentApiBindingResponse` / `MeAgentTradingApiBindingResponse`：`bindingRowCreated`、`activationWelcomeSent`、`activationWelcomeSkipReason` |
| Admin 三语键 | 已有 `telegram_runtime_config` + `PATCH/GET …/admin/channels/telegram/bot`（4096 → `ADMIN_TELEGRAM_WELCOME_TEXT_TOO_LONG`） |

`skip_reason` 枚举：`no_telegram_context` | `channel_off` | `already_sent` | `no_template` | `send_failed`

## 自测

```bash
cd server && uv run pytest tests/test_telegram_activation_welcome.py -q
```

6 passed（含 TC-02/03/05/06/08 单元与 confirm 集成）。

## 未在本阶段

- **AC-8 Admin 三语 UI**（`admin/` 单框拆三语）→ 交 `frontend-agent` / `frontend.integrate`

## 启动

```bash
cd server && uv run chainup-agent-api
```
