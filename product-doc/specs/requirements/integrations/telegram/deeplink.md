# Integrations · Telegram · Deeplink

**上游职责（Telegram 平台）**：[Telegram Bot · Deep Linking](https://core.telegram.org/bots/features#deep-linking)：**`t.me/<botname>?start=<payload>`**、`startgroup` 等 **参数编码规则**与 **`start` payload 长度限制** — **以 Telegram 文档为准**。

**产品侧卡片 / Billing / H5 跳转**：[`telegram/overview` §2.2～§2.6、§2.5.x（类型 B · Deeplink；§2.6 · Bot API）](../../domains/agent/telegram/overview.md)；计费字段 [`../../domains/admin/billing-management/overview.md`](../../domains/admin/billing-management/overview.md)。

## 协议约束（摘要）

- **`start` payload**：Bot API 对 **`/start`** 参数有 **长度与字符集约束**（见官方文档）；超限 **由 Telegram 或客户端截断** — **平台拼装层须遵守上游限制**。
- **HTTPS 业务落地页**：域名、路径与查询参数 **不属于 Telegram Bot API** — **`design`** / **`flows`** / **`billing`**。

## 非目标

- **落地页签名校验、ticket 时效** — **`design`** / **`risk`**。
- **Universal Link / App Links 证书** — 移动端工程。

**Bot API**：[`bot-api.md`](bot-api.md)。
