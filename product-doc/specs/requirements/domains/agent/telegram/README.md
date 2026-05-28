# `domains/agent/telegram/` — Telegram 渠道

**用户触达（本版）**：唯一会话渠道；与 **[`onboarding/telegram-binding.md`](../onboarding/telegram-binding.md)**、**[`exchange-agent/`](../exchange-agent/)**、**[`agent-orchestration/`](../agent-orchestration/)** 同窗。**契约收口 / MR 首节**：[`contract-closure.md`](../../../contract-closure.md) · [**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path)。

## 权威分流（读哪篇）

| 你要回答的问题 | 先打开的文档 |
|----------------|----------------|
| **渠道闸 / Bot API · §2.4 会话语言 **`effective_locale`**** · §2.5 锚点** | **[`overview.md`](overview.md)**（**§2.5.0a** **正文格式/设计规格**；**§2.5.2** **闪兑规范性示例**） |
| **绑定 · Deeplink · 阻断话术 · `TG-GWT-*`** | [`telegram-binding.md`](../onboarding/telegram-binding.md) |
| **后台 Bot / Webhook / `TELEGRAM_*` / `FR-TG-ADMIN-*`** | [`admin-bot-config.md`](admin-bot-config.md)、[`trading-agent-config/keys.md` §4](../../admin/trading-agent-config/keys.md) |
| **类型 A 卡面摘要（现货 · 杠杆 · 永续）** | **[`overview.md`](overview.md) §2.5.2～§2.5.4**；理财与逐字段终裁 [`trade-via-agent.md`](../../../flows/trade-via-agent.md)、[`wealth-via-agent.md`](../../../flows/wealth-via-agent.md) |
| **上游 Bot API / Webhook 协议** | [`integrations/telegram/bot-api.md`](../../../integrations/telegram/bot-api.md)、[`webhook`](../../../integrations/telegram/webhook.md)、[`deeplink`](../../../integrations/telegram/deeplink.md) |
| **类型 A～D · 一页场景↔版式索引** | **[`overview.md`](overview.md) §2.5.0**；[`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md) · **场景一页表** |

## 目录

| 文件 | 说明 |
|------|------|
| [`overview.md`](overview.md) | 渠道叙事、**§2.4 · 会话语言**、**§2.5 · 类型 A（§2.5.x）**、**§2.5.0a · 类型 A 正文格式与设计规格** · **§2～§7**、与 `CHANNEL_TELEGRAM` / `design/api` 对签 |
| [`admin-bot-config.md`](admin-bot-config.md) | **运营后台 · Telegram Bot 配置**（与 **模块七** [`trading-agent-config`](../../admin/trading-agent-config/overview.md) 对签） |
| [`mobile-app.md`](mobile-app.md) | **暂缓**；占位与 [`product.md`](../../../product.md) 互引 |

**上级导航**：[`../README.md`](../README.md) · [`../../README.md`](../../README.md)
