# Evals · Clarify · Telegram GWT（构造正文）

**路径**：`specs/requirements/evals/clarify-telegram.md`。  
**索引**：[`scenarios.md`](./scenarios.md) **登记行** · [`README.md`](./README.md)。

**SSOT**：[`clarify-session.md`](../domains/agent/agent-orchestration/clarify-session.md) · [`telegram/overview` §2.3.1～§2.3.3](../domains/agent/telegram/overview.md) · [`clarify-user-visible`](../prompts/shared/clarify-user-visible.md)。

---

## 1. 登记行 ↔ 本卷

| **`evalSetId`** | **Then（摘要）** | **SC** |
|-----------------|------------------|--------|
| **`eval.telegram.typing_on_inbound`** | **`message` inbound** **后** **≤300ms** **观测** **`sendChatAction(typing)`** **或** **≤1s** **早失败短句** | **`SC-CH-TG-09`** |
| **`eval.telegram.clarify_keyboard_present`** | **写澄清 · 二选一** **须** **`inline_keyboard`** **同窗语** · **`callback_data` ≤64B** | **`SC-CH-TG-10`** |
| **`eval.telegram.clarify_callback_merges_slots`** | **点 `cl:fc`** → **`resolvedSlotsSoFar.tradeMode=flash_convert`** **且** **保留** **上轮 BNB/BUY** → **重跑 Resolver** | **`SC-CH-TG-11`** · **`SC-CLARIFY-02/04`** |
| **`eval.telegram.clarify_not_write_confirm`** | **澄清键盘** **无** **「确认下单」**；**`cl:*`** **0** **笔** **`call_exchange_write`** | **`SC-CLARIFY-01`** |
| **`eval.clarify.stm_resolved_slots_injected`** | **第 2 轮 Prompt/STM** **须** **含** **`resolvedSlotsSoFar` 摘要** | **`SC-CLARIFY-03`** |
| **`eval.clarify.no_internal_jargon`** | （**§12 GWT**） | **`SC-CLARIFY-09`** |
| **`eval.clarify.one_question_per_turn`** | （**§13 GWT**） | — |
| **`eval.clarify.reintent_each_inbound`** | **澄清态** **新 inbound** **须** **重跑意图** **且** **承接话术** | **`SC-CLARIFY-05`** |
| **`eval.clarify.abandon_on_cancel`** | **「都不要了」** → **`abandoned`** **且无** **写澄清复读** | **`SC-CLARIFY-06`** |
| **`eval.clarify.read_interrupts_write`** | **只读问句** **打断** **写澄清** | **`SC-CLARIFY-07`** |
| **`eval.clarify.no_repeat_outbound`** | **不同 inbound** **不得** **同字 outbound** | **`SC-CLARIFY-08`** |
| **`eval.clarify.greeting_no_write_clarify`** | **「你好」** **无** **闪兑/限价盘问** | **`SC-CLARIFY-07`** |
| **`eval.memory.stm_governance_regression`** | **生产僵尸澄清整链**（**§16.8**） | **`SC-STM10`** |

---

## 2. GWT · `eval.telegram.typing_on_inbound`

```text
Given：用户已绑定 · CHANNEL_TELEGRAM=ON
  sessionId = S1 · chat_id = C1

When：Webhook 收到 Update.message.text = 「买入 BNB」
  且 编排预期 >300ms

Then：观测 agent.channel.telegram.chat_action
  action=typing · chat_id=C1
  且 firstTypingMs ≤ 300
  或（早失败路径）≤1000ms 内 sendMessage 含可读归因
  且 不得 静默 >5s 无 typing 续发且无进度短句（长路径负例）
```

---

## 3. GWT · `eval.telegram.clarify_keyboard_present`

```text
Given：写路径 · 缺 spot 方式 · resolvedSlotsSoFar={ side:BUY, baseAsset:BNB }

When：BFF 发出澄清 outbound

Then：reply_markup.inline_keyboard 存在
  且 一行含 text∈{闪兑,閃兌,Flash} 与 {限价,限價,Limit}
  且 callback_data ∈ { cl:fc, cl:lo }
  且 用户可见正文 0 处 路由|写路径|INV-
```

---

## 4. GWT · `eval.telegram.clarify_callback_merges_slots`

```text
Given：ClarifySessionSnapshot
  executionId=E1 · clarifyTurn=1
  resolvedSlotsSoFar={ side:BUY, baseAsset:BNB }
  pendingClarifyKind=spot_trade_mode

When：callback_query.data = cl:fc

Then：answerCallbackQuery 已调用
  且 snapshot.clarifyTurn=2
  且 resolvedSlotsSoFar 含 tradeMode=flash_convert, type=MARKET
  且 仍含 side=BUY, baseAsset=BNB
  且 观测 Resolver 重跑 · missing 不含「仍问闪兑/限价」类逻辑错误
```

---

## 5. GWT · `eval.clarify.stm_resolved_slots_injected`

```text
Given：同上 · 用户第二轮 inbound 或 点按后生成 Prompt

When：拼装 Prompt / STM 块

Then：上下文含 人话摘要「已确认：买入 BNB」或等价
  且 仍缺项 仅 1 个主问句或 1 组二选一键盘
  且 不得 举例 BCH/BTC 等与 BNB 无关默认对
```

---

## 6. 负例 · 混淆澄清与类型 A

```text
When：澄清轮 outbound

Then：inline_keyboard 按钮 text 不得 匹配 /确认下单|Confirm/i
  且 callback_data 前缀 不得 为 cf:（写确认前缀 · design 冻结）
```

---

## 7. GWT · `eval.clarify.abandon_on_cancel`

```text
Given：ClarifySessionSnapshot active
  pendingClarifyKind=spot_trade_mode · clarifyTurn=1
  上轮 outbound 已问闪兑/限价

When：Update.message.text = 「都不要了」

Then：snapshot.abandoned = true（或 session 已清除）
  且 本轮 outbound 不得 再含 闪兑|限价|挂限价|flash_convert 类写澄清主问
  且 宜含 已取消/有需要再说 类短句
  且 0 次 call_exchange_write
```

---

## 8. GWT · `eval.clarify.read_interrupts_write`

```text
Given：同上写澄清 pending（缺 spot 方式）

When：Update.message.text = 「目前有哪些币可以买的」

Then：intent_family 不得 仍为 trade_write-only 盲复读
  且 outbound 须 只读 listing/说明方向（或 先答可查范围再问是否下单）
  且 clarify session abandoned 或 suspended
  且 不得 逐字重复 上轮「闪兑还是限价」全文
```

---

## 9. GWT · `eval.clarify.no_repeat_outbound`

```text
Given：澄清态 · 用户未点 cl:*

When：inbound1 = 「买入 BNB」→ outbound1
  inbound2 = 「目前有哪些币可以买」→ outbound2

Then：outbound1 与 outbound2 不得 逐字相同
  且 outbound2 须 体现 inbound2 语义（读/ listing）
```

---

## 10. GWT · `eval.clarify.greeting_no_write_clarify`

```text
Given：无活跃写意图 或 仅有残留 clarify session

When：Update.message.text = 「你好」

Then：outbound 含 问候或能力介绍
  且 0 处 要求用户「一句说明闪兑还是限价」
  且 0 处 路由|多主场景|须澄清后再路由
  且 若残留 session：须 abandoned 或 不触发写澄清出站
```

---

## 11. GWT · `eval.memory.stm_governance_regression`

```text
Given：ClarifySessionSnapshot active
  pendingClarifyKind=spot_trade_mode
  resolvedSlotsSoFar={ side:BUY, baseAsset:BNB }
  上轮 outbound 已问闪兑/限价（含内部词则为 fail）
  lastUserMessageAt = T0

When（序列 · 每条须重跑意图 §2.3）：
  1) sleep ≥ STM_IDLE_RESUME_PROMPT_SEC（默认 1800s）或 fixture 快进时钟 → lifecycleState=stale
  2) Update.message.text = 「你好」
  3) Update.message.text = 「目前有哪些币可以买的」
  4) Update.message.text = 「都不要了」

Then（逐步）：
  步 2：outbound 寒暄/能力 · clarify abandoned · lifecycleState=abandoned · 0 闪兑/限价写澄清
  步 3：只读/listing 方向 · 0 写澄清复读
  步 4：abandoned=true · 短句确认 · 0 写澄清
  全程：Prompt messages 0 处 routingHints/clarify JSON 原文（SC-STM07）
  全程：0 处 路由|写路径|须澄清后再路由|多主场景（SC-CLARIFY-09）
  全程：0 次 call_exchange_write
```

---

## 12. GWT · `eval.clarify.no_internal_jargon`

```text
Given：写路径 · 缺 spot 方式 · resolvedSlotsSoFar={ side:BUY, baseAsset:BNB }

When：BFF 发出首条或续轮写澄清 outbound（含 inline_keyboard 或纯文本）

Then：用户可见正文 0 处 匹配
  路由|写路径|禁止猜测|仅澄清|scenarioId|INV-|多主场景|须澄清后再路由|混用两种说法|orchestrationNextSteps|routingHints
  且 宜用人话：闪兑/限价/买入/数量 等
  且 inline_keyboard button text 亦 0 处 内部词
Negative：fixture 注入 routingHints 原文 → 出站前 须被 Normative 层剔除（SC-STM07）
```

---

## 13. GWT · `eval.clarify.one_question_per_turn`

```text
Given：首条写路径澄清（clarifyTurn=1）· 缺 tradeMode 与 quantity

When：BFF 发出澄清 outbound

Then：
  主问句计数 ≤1（句号/问号分隔 · 不含问候尾句）
  或 仅 1 组二选一 inline_keyboard（闪兑 vs 限价）
  且 同条不得列 ≥3 项待填 checklist（如「请提供：1…2…3…」）
  且 不得 同时 长段说明 + 多组键盘
Negative：缺参 ≥3 时 须 分轮 clarifyTurn 递增 而非 单条堆叠
```

---

**文档版本**：0.4.0-mvp · **维护**：产品 + QA · **本版**：**§12～§13 no_internal_jargon / one_question GWT**。承 0.3.0-mvp。
