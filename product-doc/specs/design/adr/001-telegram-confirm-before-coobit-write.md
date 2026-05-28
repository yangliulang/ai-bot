# ADR-001：Telegram「类型 A」确认闸门先于 Coobit 写调用


| 项      | 内容                                                                        |
| ------ | ------------------------------------------------------------------------- |
| **状态** | **已采纳**（与需求 **已合并**；实现须对签）                                                |
| **日期** | 2026-04-30                                                                |
| **范围** | ChainUp AI Agent · 首版 · **Telegram** 触达 → Agent 网关 → **Coobit 子账户私有 API** |


## 上下文

- 产品要求 **每一笔**交易所侧 **写**在用户 **明示确认**后方可执行（`[trade-assistance.md` §2 · `FR-T09](../../requirements/domains/agent/exchange-agent/trade-assistance.md)`；`[trade-via-agent.md](../../requirements/flows/trade-via-agent.md)` **流程专节**；`[overview-legacy-migration.md](../../requirements/domains/agent/exchange-agent/overview-legacy-migration.md)` **§2** 供 **旧 §10.x → 分卷** 对读；`[domains/agent/telegram/overview.md](../../requirements/domains/agent/telegram/overview.md)` **必选能力 #7、§2.5 · 类型 A**（总则 **§2～§2.6**））。
- **Telegram Bot API** 对内联按钮的 `**callback_data` 限 1～64 字节（UTF-8）**，无法承载完整订单体；且 `**sendMessage`/caption** 有字数上限（见 `[api.md](../api.md)` **「Telegram Bot API」专节**、[官方文档](https://core.telegram.org/bots/api)）。
- **504 / 幂等**：Coobit 写与 **会话侧确认**是 **不同信任边界**；会话内「点过确认」与「交易所终态」不得混写进同一条用户话术（`[overview.md](../overview.md)`、`[overview.md](../../requirements/domains/agent/exchange-agent/overview.md)` **FR-T05**）。

## 决策

1. **编排顺序（硬）**
  `**Update.callback_query`（用户点「确认」）** → **服务端校验 `pending_confirm`（单次消费）** → **仅此之后**才可向下游发起 `**[api.md](../api.md)` 矩阵 `R/W=W`** 的请求（下单、撤单、条件单创建/取消等）。**禁止**：仅凭模型输出或上一轮自然语言推断即调 Coobit `W`。  
   *与 `[api.md](../api.md)` **通用契约表「Telegram 会话（交界）」**、`[telegram.md](../../requirements/domains/agent/telegram/overview.md)` **§2.6** 一致。*
2. `**callback_data` 形态**
  **仅短键**（前缀 + confirmId）；**confirmId** **映射到**己方存储中的一条 `**pending_confirm` 记录**（含 `**userId`、`executionId`/trace、意图摘要哈希、expiresAt、consumption 状态`** 等字段，以所内 schema 冻结为准）。**禁止**塞 **Secret**、整条 JSON。**幂等**：同一 confirmId `**answerCallbackQuery`/`消费`** **至多成功一次**。    *与 **`SC-CH-TG-05、SC-CH-TG-06、SC-CH-TG-08`** 对签。*
3. `**answerCallbackQuery` 策略**
  **须在收到 callback 后尽快应答**结束客户端 loading；若 Coobit 调用较慢：**先 answer**，再通过 `**sendMessage`/`edit_message_text`** 推送进度或终态，**不得以** 「不 answer」 **拖 Spinner**。**二次 answer**错误按 Bot API **容错**处理并打日志。
4. **正文超长**
  **§2.5** 类长摘要：**拆消息 / `edit_*` / 附 `url` 跳转主站 H5**，在 **出站前**自检长度 **避免 `MESSAGE_TOO_LONG`**。
5. **复合写（逻辑改单 · 无原生 amend API）**
  当 `**[api.md](../api.md)` 矩阵** **未提供** **单笔 HTTP amend**、**产品** **采用** **「撤单 + 重建」** **合成** **改价/改量** **时**：**一次** `**pending_confirm` / 类型 A** **可授权** **同一执行上下文内** **顺序发起** **多笔** `**R/W=W`**（**典型** **先** `cancel` **再** `order`）。**禁止** **在** **用户已消费该 `confirmId` 之前** **调用** **任一** **交易所写**；**禁止** **在** **顺序复合写中间** **再要求** **第二次** **类型 A** **unless** **前序写已明确失败且须用户改参重入**（**失败恢复** **见** `**[trade-via-agent.md](../../requirements/flows/trade-via-agent.md)`** **专节 · 逻辑改单**）。**与** **`[trade-assistance.md](../../requirements/domains/agent/exchange-agent/trade-assistance.md)` **§2 · `FR-T09`** **「独立写意图」** **区分** **同窗**。

## 后果


| 类别                 | 说明                                                                                                                                                                                                                                                                                                                                       |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **必须建设**           | **Confirm 持久化（或等价缓存 + 审计）**、TTL、**并发点按**单次消费语义；网关层 **Lint/单测** 校验待发键盘每条 `**callback_data` 字节长度**。**逻辑改单**：`**pending_confirm` 载荷** **须** **可复原** **原委托键**（`orderId` / `clientOrderId` **等**）**与** **新委托全量参数**；**顺序写** **须** **可观测** **同一 `executionId`**（**或** `**amendCorrelationId` 同窗**）**关联** **两笔** `**trading.exchange_private`**。 |
| **观测**             | `callback_query.id`（若落日志）、confirmId、`userId`、`executionId`、与后续 `**trading.exchange_private`** **可 join**（`[observability.md](../../requirements/observability/overview.md)`）。                                                                                                                                                            |
| **替代方案（未采纳为首版主线）** | **Mini App `/ web_app`** 做富确认页：**可**在后续 ADR **单列**；首版仍以 **inline_keyboard** 为满足 **必选能力 #7** 的 **默认路径**。                                                                                                                                                                                                                                  |


## 验证清单（可供 CI / Code Review）

- 所有 `**InlineKeyboardButton`（`callback` 类）** `callback_data` **UTF-8 字节长度 ∈ [1,64]**（对齐 `**SC-CH-TG-08`**）。
- **集成/冒烟**：在无「类型 A」确认路径的场景下，**不得**出现 `**trading.exchange_private`** 且 `**exchangeOutcome**` 已闭合为 `**success` 或 `fail**` 的交易所 **写**调用（对齐 `**SC-CH-TG-06`**）。
- **逻辑改单**：**单次** `**pending_confirm` 消费后** **顺序** `**cancel`→`order`** **无** **中间第二次类型 A**；**撤单失败** **不** **下单**；**两笔** `**trading.exchange_private`** **可** **join** **同一 `executionId`/`amendCorrelationId`**（**对齐** `**trade-via-agent`** **专节 · 逻辑改单**）。

## 参考

- `[domains/agent/telegram/overview.md](../../requirements/domains/agent/telegram/overview.md)` **§2.5 · 类型 A、§2～§2.6、§5（`SC-CH-TG-05～08`；永续/条件单 · `SC-CH-TG-FUT-01～03`）**  
- `[api.md](../api.md)` **通用契约 · Telegram、专节「Telegram Bot API」**  
- `[overview-legacy-migration.md](../../requirements/domains/agent/exchange-agent/overview-legacy-migration.md)` **§2**（旧 **§10.3～§10.5** 映射：`intents`/槽位、产品线闸/`keys`）；`**FR-T09`** **域内摘录**：`[trade-assistance.md` §2](../../requirements/domains/agent/exchange-agent/trade-assistance.md)；**流程专节**：`[trade-via-agent.md](../../requirements/flows/trade-via-agent.md)`  
- `[overview.md](../overview.md)` **504、幂等**

