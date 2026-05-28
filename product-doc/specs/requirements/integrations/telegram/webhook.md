# Integrations · Telegram · Webhook

**上游职责**：[Telegram Bot API · setWebhook / Webhook 更新结构](https://core.telegram.org/bots/api)：**HTTPS POST** 投递 **`Update`** JSON；可选配置 **`secret_token`**（请求头 **`X-Telegram-Bot-Api-Secret-Token`**）。

**控制台配置叙事**：[`../../domains/agent/telegram/admin-bot-config.md`](../../domains/agent/telegram/admin-bot-config.md)；密钥 [`../../domains/admin/trading-agent-config/keys.md`](../../domains/admin/trading-agent-config/keys.md)；**对内 URL 登记**：[`../../../design/api.md`](../../../design/api.md)。**Inbound `Update` 与会话边界**（产品）：[`../../domains/agent/telegram/overview.md`](../../domains/agent/telegram/overview.md) **§2～§2.6**；**写前确认卡** → **§2.5 · 类型 A**；**澄清 callback** → [`clarify-session.md`](../../domains/agent/agent-orchestration/clarify-session.md)。

## 协议约束（摘要）

- **载荷**：请求体为 **`Update`** 对象（内含 **`update_id`**、`message`、`callback_query` 等可选字段）— **schema 以 Bot API 为准**。
- **TLS**：Webhook URL **须 HTTPS**（Telegram 文档要求）。
- **secret_token**：若设置，Telegram **每次请求携带该头**；未携带则 **可依平台策略拒绝** — **拒绝逻辑归属 `design`/安全**，非 Telegram 语法。

## 入站处理 · 产品下限（`requirements` · 非 PATH SSOT）

**PATH / 队列 / 幂等表** **在** [`design/api.md`](../../../design/api.md) **登记**；**本节** **只** **冻结** **对用户可见行为** **之** **需求**。

| **`Update` 类型** | **MUST（摘要）** | **需求 SSOT** |
|-------------------|------------------|---------------|
| **`message`（写/读意图）** | **≤300ms** **`sendChatAction(typing)`**（**或** **≤1s** **早失败短句**） | [`telegram/overview` §2.3.1](../../domains/agent/telegram/overview.md) · **`SC-CH-TG-09`** |
| **`message`（澄清态 follow-up）** | **须** **重跑意图**（**§8**）**后** **再出站**；**放弃/只读/寒暄** **分流** | [`clarify-session` §2.3](../../domains/agent/agent-orchestration/clarify-session.md) · **`SC-CLARIFY-05～07`** |
| **`message`（写路径澄清）** | **出站** **须** **符合** **澄清话术 + 可选键盘** | [`clarify-user-visible`](../../prompts/shared/clarify-user-visible.md) · **§2.3.2** |
| **`callback_query` · `cl:*`** | **澄清 session 全序** | [`clarify-session.md`](../../domains/agent/agent-orchestration/clarify-session.md) · **`SC-CH-TG-11`** |
| **`callback_query` · 写确认** | **ADR-001 · `pending_confirm`** | [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md) · **§2.6** |

## 非目标

- **分布式幂等表、租户路由防注入、异步队列** — **`Runtime`**、**`design`**、实现架构。
- **长轮询 getUpdates** — 若未在 **`design`** 登记为非目标。

**Bot 方法 limits**：[`bot-api.md`](bot-api.md)。
