# E2E / 页面验证用例

> 测试 Agent 在 `frontend_done` 后执行。契约就绪后可预填骨架。

## 前置条件

- 后端：`cd server && uv run chainup-agent-api`（8080）
- 前端：`cd admin && npm run dev`（5173），已登录 Admin
- 路由：`/system/channels/telegram`（`TelegramChannelDetailPage`）

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| E2E-01 | AC-8 | 三语字段可见 | 打开 **4. 用户体验** 区块 | **简中 / 繁中 / 英文** 三个独立多行输入（或 Tab）；说明含「绑定成功 · 每用户一次」与 `{displayName}` | P0 |
| E2E-02 | AC-8 | 保存与回显 | 分别填入三语文案 → **保存体验配置** → 刷新页面 | 三字段仍显示刚保存内容；Network `PATCH …/bot` 含对应 `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_*` | P0 |
| E2E-03 | AC-3 | 绑定后 TG（可选） | 配置欢迎语 + 完成 Deeplink 绑定（测试 Bot） | Telegram 私聊收到 **一条** 欢迎语（所内环境；无 Bot 时记 **跳过** 并附注） | P1 |

## 验收对照（brief.md）

- [x] 主流程：Admin 三语配置可保存回显
- [x] 错误态：超长保存展示服务端 `message`（若 FE 已实现校验可先本地提示）
- [x] Deeplink 无欢迎语 UI（不测 onboarding 页文案）

| E2E-04 | AC-2 | 解析链 | — | **N/A** · API TC-02 | P0 |
| E2E-05 | AC-4 | 幂等 | — | **N/A** · API TC-05 | P0 |
| E2E-06 | AC-5 | 无模板 | — | **N/A** · API TC-06 | P0 |
| E2E-07 | AC-6 | 发送失败 | — | **N/A** · API TC-07 | P0 |
| E2E-08 | AC-7 | 占位符 | — | **N/A** · API TC-08 | P0 |

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| E2E-09 | PATCH 409 | 提示刷新后重试（P1） |
