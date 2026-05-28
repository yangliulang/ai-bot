# Integrations · Telegram · Bot API

**上游职责**：[Telegram Bot API](https://core.telegram.org/bots/api) 所定义的 **HTTP 方法**、请求/响应字段与 **硬性限制**。

**产品叙事 SSOT**：[`../../domains/agent/telegram/overview.md`](../../domains/agent/telegram/overview.md)（**类型 A 卡面** → **§2.5 · 类型 A**；**渠道闸 · Bot API 下限** → **总则 §2～§2.6**）。  
**对内登记表**：[`../../../design/api.md`](../../../design/api.md) **Telegram Bot API** 专节。

## 协议约束（摘要，以 Bot API 为准）

- **调用方式**：HTTPS POST 至 `https://api.telegram.org/bot<token>/<method>`（或文档指定的等价入口）。
- **常见限制（示例）**：**`callback_data`** 长度上限（文档定义为 **64 bytes**）；消息文本 / caption **最大长度**；文件大小上限等 — **逐项以 Bot API 为准**。
- **`sendChatAction`**：`action=typing` **等** — **客户端「正在输入…」** **须 Bot 主动发送**；**指示约 5s**，长任务 **须续发** — **产品** [`telegram/overview` §2.3.1](../../domains/agent/telegram/overview.md) · **`SC-CH-TG-09`**。
- **速率**：Bot API **全局与按方法**可能存在节流；返回 **429** 及 **`retry_after`** — **上游语义**。
- **错误**：响应 JSON **`ok`** / **`description`** / **`error_code`** — **载荷形状属上游**。

## 非目标

- **Webhook 重复 update 的幂等**、会话状态机、`answerCallbackQuery` 与编排 SLA — **`Runtime`**、**`sessions`**、**`agent-orchestration`**。
- **交易确认流** — [`../../domains/agent/agent-orchestration/confirmation-flow.md`](../../domains/agent/agent-orchestration/confirmation-flow.md)。

**Webhook**：[`webhook.md`](webhook.md)。**Deeplink**：[`deeplink.md`](deeplink.md)。
