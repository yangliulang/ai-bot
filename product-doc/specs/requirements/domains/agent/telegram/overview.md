# Telegram 渠道（用户触达与会话）

**职责**：本版 **唯一** 用户会话入口；承载 **绑定 / Deeplink / 卡片与内联确认** 产品下限，并与 **全局 `CHANNEL_TELEGRAM`**、**准入与计费** 同源。

**HTTP / OpenAPI 真源**：[`design/api.md`](../../../../design/api.md) **登记表**、**「Telegram Bot API」** 专节；**运营侧 Bot 配置** **[`admin-bot-config.md`](admin-bot-config.md)**。

**互引**：[`onboarding/telegram-binding.md`](../onboarding/telegram-binding.md)；[`activate-trading-agent`](../../../flows/activate-trading-agent.md)、[`trade-via-agent`](../../../flows/trade-via-agent.md)、[`consume-and-bill`](../../../flows/consume-and-bill.md)；[`exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **确认与写门闸**；[`../../admin/trading-agent-config/keys.md`](../../admin/trading-agent-config/keys.md)（**`CHANNEL_TELEGRAM`**、§4 **`TELEGRAM_*`**）。

**契约收口**：[`contract-closure`](../../../contract-closure.md)；**关单余量 / MR 首节** [**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path)（**CC-P1-06 · 类型 A · §1.2 六款** **等同窗派工索引**）。

**端到端鸟瞰 · 架构语言**：[`flow/e2e-closed-loop.md`](../../../../../flow/e2e-closed-loop.md) **文首「架构语言」** → [architecture.md · 与通用 Agent 栈之对照](../../../../design/architecture.md)。

---

## 1. 渠道闸与摘要

- **`CHANNEL_TELEGRAM=OFF`** 时：频道侧须 **早失败** 或 **可读归因**（与 [`onboarding/activation-policy.md`](../onboarding/activation-policy.md)、[`access-control`](../../admin/access-control/overview.md) **同窗**）；**不得**伪造成其它阻断码。  
- **编排只读摘要**：运行时所消费的有效 **`configVersion`** 与 **模块七** 最近一次成功写入 **一致**（对应 **SC-TAC-04**、[`trading-agent-config/functions.md`](../../admin/trading-agent-config/functions.md) **§4**）。

---

## 2. 先于 Coobit 写（决策摘要）

交易与资金 **写动作** **须**满足 **「Telegram 确认先于子账户私有 API」** — **ADR**：[`design/adr/001-telegram-confirm-before-coobit-write.md`](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)。**编排**见 [`agent-orchestration/confirmation-flow.md`](../agent-orchestration/confirmation-flow.md)。

### 2.1 会话与绑定

绑定、换绑与吊销见 [`telegram-binding.md`](../onboarding/telegram-binding.md)。

#### 2.1.1 Agent 开通完成后的欢迎语（可配置 · **简中 / 繁中 / 英文**）

- **配置**（[`keys.md` §4.2](../../admin/trading-agent-config/keys.md)）：**主键** `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN`（简体）、`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_TW`（繁体）、`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_EN`（英文）；**兼容** `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT` **见** **keys** **表**（**迁移回退**）。运营在 **渠道管理 · Telegram** 维护 — [`admin-bot-config.md`](admin-bot-config.md) **FR-TG-ADMIN-06**。  
- **触发**：用户 **首次**同时满足 — **Agent 开通路径已达「可本会话使用」就绪**（与 [`activate-trading-agent.md`](../../../flows/activate-trading-agent.md) `S2～S5`、[`initialization-flow.md`](../onboarding/initialization-flow.md) **成功终态** **同窗叙事**）— 且 **Telegram 已绑定**该 `userId`。  
- **语言解析**（**首版下限**；**合并策略** 可由 **`design`** 细化为 ADR）：**①** **用户主档语言偏好**（若有）映射到 `zh-Hans` / `zh-Hant` / `en` **三桶之一**；**否则** **②** **Telegram** `language_code`（[`User` 辅字段](https://core.telegram.org/bots/api#user)）：`zh-hans`、`zh-cn`、`zh-sg`、`zh`（**缺省** **Hant** **不推断** **时**）→ **简体桶**；`zh-hant`、`zh-tw`、`zh-hk`、`zh-mo` → **繁体桶**；`en` 前缀或 `en` → **英文桶**；**③** **否则** **以** `TELEGRAM_DEFAULT_LOCALE`（[`keys.md` §4.2](../../admin/trading-agent-config/keys.md)）映射到 **同一** **三桶**；**④** **仍** **无法** **映射** → **英文桶**（**或** **简体桶**：以 **`design`** 终裁为准，且 **须** 与 **`TELEGRAM_DEFAULT_LOCALE`** **同窗**）。  
- **正文选取 · 回退链**（**对** **解析桶** **取** **对应** `configKey` **非空** **正文**）：**命中桶** → **桶空则** **简体** → **仍空则** **英文** → **仍空则** **繁体** → **仍空则** `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT`（遗留键）→ **仍空** → **不发送**（**不算失败**）。  
- **投递**：`CHANNEL_TELEGRAM=ON` 且 **回退链** **得到** **非空** **正文** 时，Bot **须**向该 **绑定会话** **发送一条**渲染后消息（**占位符** 以 **`design`/OpenAPI** 冻结为准）；须遵守 **§2.6** **消息长度**等 Bot API 下限。  
- **幂等**：**同一** `userId`（及当前绑定 **`chat` 锚点**；以 **`design`** 终裁）**仅发一次**；换绑后是否再发由 **`design`** **单列**（默认 **不**因模板改版对老用户自动重发，除非另增 **`FR`**/运维动作）。

### 2.2 卡片与 Deeplink

- **失败 / 阻断**须带 **稳定归因** + **可走通 Deeplink**（与 `initialization-flow` 失败表同窗）。  
- **Billing / Commerce（交易所站内 · H5）**：**对客** **`/subaccount/billing`（账单与消耗 · `me/commerce`）** — [`web-billing-reconciliation` §0](../../web/admin-console-web-billing-reconciliation.md)、[`commerce-deeplink` §3](../../web/commerce-deeplink.md)（**`?start=ab` / `ab_ld` / `ab_up` / `ab_pk`**）；域 FR [`web/agent-billing.md`](../../web/agent-billing.md) **FR-WEB07～11**、**FR-B17～B20**；与 **Agent 绑定** **`me/agent/*` 外置** **同窗** [`product.md`](../../../product.md)。

### 2.3 推送节奏、入站反馈与类型 A 超时（产品默认）

- **刷屏**：同一 `executionId` / **同一笔类型 A** **生命周期内**，**优先** **就地编辑**确认卡（`edit_`）**再发补充说明**；**禁止** **多张互不关联的类型 A** **冒充** **单笔写确认** — **同窗** [`interaction-flow-standard` §6](../../../standards/interaction-flow-standard.md)。  
- **类型 A 待确认超时**：超过 **`design`** 冻结 TTL **→** **确认失效**；**禁止** **超时后仍接受同一 `callback_data` 触发交易所写** — **`pending confirm` 分层** **同窗** **§2.6** 与 [`design/api`](../../../../design/api.md) **「Telegram Bot API」**、[`confirmation-flow`](../agent-orchestration/confirmation-flow.md)。

#### 2.3.1 入站后「正在输入」反馈（`sendChatAction` · MUST）

**现象**：用户发出 **`message` / 语音转写 inbound** 后，客户端 **长时间无**「正在输入…」**且无**首条 Bot 回复 → **焦虑、重复发送**。

**机制**（Telegram Bot API）：Bot **须** 对目标 `chat_id` 调用 **`sendChatAction`**，`action=typing`（**以** [Bot API](https://core.telegram.org/bots/api#sendchataction) **为准**）。

**产品默认时序**（**首版冻结 · `design` 可 ADR 微调数值**）：

| 参数 | **默认值** | **说明** |
|------|------------|----------|
| **客户端 typing 可见时长** | **~5s** | Telegram 行为；BFF **不得假设更长** |
| **首次 `typing` 截止** | **≤300ms**（自 Webhook 入队） | **SC-CH-TG-09** |
| **续发间隔** | **每 4500ms** | **在 5s 窗口过期前续发** |
| **续发停止条件** | **首条用户可见 `sendMessage`/`edit_*`** **或** **早失败短句** | — |

**长耗时编排须周期性续发**（**直至** **停止条件**）；**或** **并用** **类型 C 进度短句** — **同窗** [`clarify-user-visible` §6 P5](../../../prompts/shared/clarify-user-visible.md)。

| 触发 | **MUST** | **说明** |
|------|----------|----------|
| **`Update.message`（文本/命令等需编排回复）** | **Webhook 入队后尽快**（**宜** **≤300ms**）**首次** `typing` | **先于** LLM/Resolver **首 token**；**禁止** **静默至** **终态** **才** **首条** `sendMessage` — **同窗** [`trade-via-agent` S11 UX](../../../flows/trade-via-agent.md) **「等待与焦虑」** |
| **编排/LLM/只读仍进行中**（**>5s**） | **续发** `typing` **或** **先发** **一条** **短进度句**（**类型 C**，**非**类型 A） | **与** [`clarify-user-visible` §6 P5](../../../prompts/shared/clarify-user-visible.md) **同窗**；**二选一或并用** |
| **`callback_query`（点确认/澄清钮）** | **须** **尽快** `answerCallbackQuery` **结束 spinner** | **同窗** **§2.6**、**ADR-001**；**typing** **可选**（**慢路径** **宜** **answer 后** **再** **阶段消息**） |
| **早失败**（渠道 OFF、未绑定、纯拒答） | **可** **跳过** `typing` | **须** **≤1s** **内** **可读短句** **归因** |

**执行体**：**纯规则/BFF** — **非 LLM**；**不得** **依赖** **模型** **决定是否** **发 typing**。**观测**：**宜** **`agent.channel.telegram.chat_action`**（`action=typing`、latency）— **同窗** [`observability/overview`](../../../observability/overview.md)。

**参考小样**（所内 BFF **可选**）：[`telegramInboundFeedback.ts`](../../../../src/admin/src/productionRuntime/telegramInboundFeedback.ts) — **非需求 SSOT**。

**验收**：**`SC-CH-TG-09`**（**§5**）。

#### 2.3.2 澄清 · inline_keyboard（二选一 · MUST）

**适用**：写路径 **澄清轮**（**非**类型 A 确认）— **闪兑/限价**、**买/卖**、**默认交易对**、**数量口径** 等 **二选一/短选**。**禁止** **仅** **开放题** **让用户打长句** — **同窗** [`clarify-user-visible` §6 P2/P7](../../../prompts/shared/clarify-user-visible.md)。

**`callback_data` 与 session 语义 SSOT**：[`clarify-session.md`](../agent-orchestration/clarify-session.md) **§4**。

| 澄清种类 | **`callback_data`** | **按钮字面 · `zh-Hans`** | **`zh-Hant`** | **`en`** | 执行体 |
|----------|---------------------|--------------------------|---------------|------------|--------|
| **现货方式** | `cl:fc` · `cl:lo` | **闪兑** · **限价** | **閃兌** · **限價** | **Flash** · **Limit** | **R→B** + **L** |
| **方向** | `cl:buy` · `cl:sell` | **买入** · **卖出** | **買入** · **賣出** | **Buy** · **Sell** | 同上 |
| **默认交易对** | `cl:sym:ok` · `cl:sym:no` | **对的** · **换一个** | **對的** · **換一個** | **Yes** · **Change** | 同上 |
| **数量口径**（闪兑已选 · 非 ALL_IN） | `cl:qty:base` · `cl:qty:quote` | **按 BNB 数量** · **按 USDT 金额** | **按 BNB 數量** · **按 USDT 金額** | **By BNB size** · **By USDT amount** | 同上 |
| **隔较久 · 续/新**（**§14.6** · **类型 C**） | `cl:resume` · `cl:new` | **继续上一笔** · **新话题** | **繼續上一筆** · **新話題** | **Continue** · **New topic** | **BFF** **等同** **§2.8.2 STM 清空（`cl:new`）** **或** **合并槽+Fresh（`cl:resume`）** |

**说明**：**数量口径** 行 **占位** **`<base>`/`<quote>`** **由** **`resolvedSlotsSoFar.baseAsset`/quote 资产** **替换**（**如** BNB / USDT）。**`cl:resume`/`cl:new`** **禁止** **写确认动词** — **同窗** **`SC-CLARIFY-01`**。

**BFF MUST**：OpenAPI **`TelegramClarifyOutboundHints.clarifyInlineKeyboard`** **附在** **`sendMessage.reply_markup`**；**LLM 不得即兴增删按钮**。**点按后** **须** **§2.3.3** **全序**。

**验收**：**`SC-CH-TG-10`**（**§5**）。

#### 2.3.3 澄清 · `callback_query` 与 session（MUST）

**SSOT**：[`clarify-session.md`](../agent-orchestration/clarify-session.md) — **字段**、**`executionId` 沿用**、**`cl:*` 注册表**、**与类型 A 边界**。

**Telegram 侧 MUST（摘要）**：

1. **`cl:*` 点按** → **`answerCallbackQuery`** **先于** **慢路径**（**§2.3.1**）。  
2. **合并** **`resolvedSlotsSoFar`** → **重跑 Resolver** — **禁止** **跳过** **直接类型 A**。  
3. **澄清键盘** **禁止** **「确认下单」** **类动词** — **同窗** **`SC-CLARIFY-01`**。  
4. **类型 A `cf:*`/confirm 前缀** **与** **`cl:*`** **不得混键** **于同一语义**。

**验收**：**`SC-CH-TG-11`** · **`SC-CLARIFY-01～09`**（**§5** · [`clarify-session` §6](../agent-orchestration/clarify-session.md)）。

#### 2.3.4 澄清态 · `message` follow-up（MUST）

**SSOT**：[`clarify-session` §2.3](../agent-orchestration/clarify-session.md)。

- **每条** **`Update.message`** **须** **重跑意图** — **禁止** **盲复读** **上轮 **`pendingClarifyKind`** **澄清模板**。  
- **寒暄 / 只读 / 放弃** **须** **分流**；**连续 outbound** **不得** **逐字相同** — **`SC-CLARIFY-05～08`**。  
- **BFF** **不得** **将 **`routingHints`** **作正文** — **`SC-CLARIFY-09`**。

### 2.4 国际化与语言自适应（首版默认）

**目标**：同一会话里 **给用户看的 Telegram 正文**（类型 A～D、追问、`answerCallbackQuery` 短文案等）及 **`inline_keyboard` 按钮字面**，须与 **本节确立的 `effective_locale`**（`zh-Hans` / `zh-Hant` / `en` **三桶之一**）**一致** — **「跟谁说话用什么语言」**。**运营告示「首版仅 ×× 语」**同窗 [`interaction-flow-standard` §5](../../../standards/interaction-flow-standard.md)。

- **基线桶**：**未应用本条 inbound 覆盖时**的默认语言，**同窗 §2.1.1 语言解析链**（用户主档 → `User.language_code` → `TELEGRAM_DEFAULT_LOCALE`，[`keys.md` §4.2](../../admin/trading-agent-config/keys.md)）；**欢迎语** **仅** **以 §2.1.1 回退链为准**。**本节**在基线之上增加「本条用户输入」。  
- **`effective_locale`**：须在每轮对用户可见下发前 **解析并注入** **运行时与 Prompt**；**工程字段名**（**design**/OpenAPI）**可改名** — 同窗 [`prompts/system/system.md`](../../../prompts/system/system.md) §1、[`prompt-management/runtime-injection`](../../admin/prompt-management/runtime-injection.md)。

**优先级（数字小者优先，后者只在「无法满足」时使用）：**

1. **用户显式语言指令**（如「please reply in English」「接下來請用繁體」）：在 **`design`** 冻结的会话窗口内，**卡片与闲聊** **须按指令语种生成**，直至用户改写或会话策略重置。
2. **本条 inbound 自然语的语种 / 书写系统推断**（规则或小模型或服务，由 **`design`** 选型）：当置信度 **≥** **`design`** 冻结阈值 **且**可归入本节 **`zh-Hans` / `zh-Hant` / `en` 三桶之一** 时，**本条起**的 **`effective_locale`** **适用于**绑定在同一 **`executionId`** 下的编排产出（含多张 **`send`/`edit`**、第二张确认、**`answerCallbackQuery`**，以及与用户可见链路一致的短文片段）。**与本条推断冲突的基线** **须让路**。**低置信**或未判出 → **不启用本条**。
3. **§2.1.1** 基线桶。
4. **无法稳定映射入三桶**（如日、韩等）：回落至 **`TELEGRAM_DEFAULT_LOCALE`** **映射桶**（以 **`design`** 终裁）；可由 **`product`/运营** 给出单行可读支持语种说明。

**下限（与用户「输入语言自适应」对签）：**

- **同窗语**：同一类型 A **生命周期**内，**`effective_locale` 须同时作用于正文与 `inline_keyboard` 字面**。**禁止**在 **无本节策略依据**时，自然语言与按键长期混搭（例如正文为简体中文而按钮固定英文 **Confirm**）。
- **代码与枚举不变**：`symbol`、`timeInForce` **等与 [`design/api`](../../../../design/api.md) 登记一致**；**`effective_locale` 只约束自然语言解释与键盘标签**。
- **极短或混写**：不强行触发 **(2)**，回落 **(3)**；**`design`** **可细化**误判与混写防护。

**自检**：[`interaction-flow-standard` §5](../../../standards/interaction-flow-standard.md)。

### 2.5 类型 A 卡片 · 字段下限（§2.5.x **锚点保留 · SSOT 分流）

下列 **`§2.5.x`** 与 [`trade-via-agent`](../../../flows/trade-via-agent.md)、[`wealth-via-agent`](../../../flows/wealth-via-agent.md) **专节同窗**。**总则**：**§2.5.2～§2.5.5** **已写 Telegram 卡面摘要与 fenced 规范性示例骨架**；**理财字段细则与 `read_skill` 条文仍以 [`wealth-via-agent`](../../../flows/wealth-via-agent.md) 终裁**；**合约 / 现货步骤列表仍以 [`trade-via-agent`](../../../flows/trade-via-agent.md) 专节为正**。若 **overview 与 flows** **字面冲突** → **以 flows MR 修正 overview** **或** **回填 flows**，**禁止** **两套正文长期分叉**。

#### 2.5.0 场景 · 卡片类型 · 版式格式 · SSOT 索引（对表）

**用途**：把 **常见业务场景** 一次性映射到 **类型 A～D（以 A 为主）**、**建议正文自上而下区块顺序**、**本条或 flows 的终裁段落**。**人类可读增补**：[`product/telegram-and-cards.md`](../../../../../product/telegram-and-cards.md) **「场景一页表」**。**类型 B～D 总定义**：**同窗 [`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md) · 四条卡片类型**；阻断 Deeplink `TG-GWT-` **见 [`telegram-binding`](../onboarding/telegram-binding.md)。

##### 通用版式（类型 A · 单行消息 + `inline_keyboard`）

自上而下 **五段语义**（可与 **Markdown 粗体/列表** **混排**，**但不得在含义上缺一）：

1. **标题 / 业务线**：与 **本节各表「业务线」** **一眼可区分**（闪兑 vs 限价 vs 合约 vs cross 杠杆 vs 理财等）。
2. **决策参数**：`symbol`、`side`、数量口径、限价、`timeInForce` **等按场景**；**禁止** **裸英文字段名作主标签**。
3. **条件单 / OCO**：**须有** `「触发条件」`/`「计划条件」` **等与「即时挂单」可区分的首屏语义块** — **同窗** `product/telegram-and-cards` **§合约 · 条件单**、下文 **永续条件单专表**。
4. **风险 / 合规披露**：滑点、`autoBorrow`/计息、`reduceOnly`、预检档位 **等**，**以服务侧 §表最小集为准**。
5. **操作区**：`inline_keyboard` — `确认`/`取消` **或等价**；**逻辑改单** **宜 `「确认修改」` 类**，**同窗** `trade-via-agent` **· 逻辑改单**。`callback_data`/`answerCallbackQuery`：**§2.6**。

**正文格式 / 渲染 / 留白 / 键盘同窗语（需求下限）**：**§2.5.0a**。

**全仓杠杆写（`margin.cross.*`）**：首张类型 A **后** **须** **第二张摘要或等价再确认**，**同窗** **§2.5.3 · 强制二次确认**。**逻辑改单一张 A** **授权顺序两笔写**：**卡面须有** `「先撤原单再挂新单」` **及** `新旧` **可读对比**。


| **用户侧场景（简述）**               | **`scenarioId`（族 · 摘录）**                                                                                                                                          | **卡片类型**                                                                | **版式从上到下（摘录）**                                                                                                          | **正文锚点（本页 / flows）**                                                                                                                                                                   |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **现货即时 / 市价 / 闪兑**          | `trade.spot.flash_convert`                                                                                                                                    | **类型 A**                                                                | **业务线·闪兑** → **对与方向、名义口径** → **市价/滑点一句** → **✓ / ✗**                                                                    | **§2.5.2 闪兑**；[`trade-via-agent`](../../../flows/trade-via-agent.md) `S14` **等同窗**                                                                                                 |
| **现货限价挂单**                  | `trade.spot.limit_order`                                                                                                                                      | **类型 A**                                                                | **币币限价** → **委托价、`timeInForce`、数量口径** → **✓ / ✗**（**偏离带第二张卡须有「按建议价调整」等价语** — **同窗** `trade-via-agent` **`S15`**）    | **§2.5.2 限价**；[`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 现货限价 · 类型 A**                                                                                              |
| **现货在途限价改价改量（逻辑改单）**        | `trade.spot.amend_limit_order`                                                                                                                                | **类型 A**                                                                | `修改挂单` **类标题** → **旧 → 新全文可读** → **`先撤销再挂单` 大白话** → **`确认修改` / `取消`**                                               | **§2.5.2 逻辑改单**；[`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单**；[`product/telegram-logical-amend-copy.md`](../../../../../product/telegram-logical-amend-copy.md) |
| **OCO / bracket**           | `trade.spot.oco` / `trade.spot.bracket`                                                                                                                   | **类型 A 或 `FR-T05` 引导（拒答/Web）**                                          | **多腿意图与限价族可区分**；**矩阵 `TBD` → `FR-T05` 透明降级，禁止假确认卡**                                                                 | **§2.5.2 OCO/bracket**；[`routing-engine.md`](../agent-orchestration/routing-engine.md) **§2**                                                                                          |
| **全仓市价**                    | `margin.cross.market_order`                                                                                                                                   | **类型 A·链路（双确认）**                                                        | **`全仓` 标注** → **名义/数量、借还计息、风险档位** → **首张 ✓ ✗ → 第二张再摘要 ✓ ✗ → `POST` 写**                                                  | **§2.5.3**；[`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 全仓杠杆**                                                                                                        |
| **全仓限价**                    | `margin.cross.limit_order`                                                                                                                                    | **类型 A·链路（双确认）**                                                        | **上栏 + 明确委托价**                                                                                                          | **§2.5.3**；[`trade-via-agent`](../../../flows/trade-via-agent.md) **同窗**                                                                                                               |
| **现货 ↔ 全仓划转（独立写意图）**        | `universal_transfer` **族（`design`/矩阵终裁）**                                                                                                                     | **每笔独立 · 类型 A**                                                         | **币种 + 数额 + 方向（如 现货→全仓）可读** → **✓ / ✗**                                                                                 | **§2.5.3 · 划转**；[`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 第四步 · 划转**                                                                                               |
| **永续市价 / 限价**               | `trade.futures.market_order` / `trade.futures.limit_order`                                                                                                | **类型 A**                                                                | **合约业务线** → **开/平可读、`side` 可读** → **张或币口径一致** → **杠杆、保证金、`reduceOnly`、市价滑点或限价不成交披露** → **✓ / ✗**                        | **§2.5.4 永续市价限价**；[`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 合约第六步等**                                                                                               |
| **永续限价逻辑改单**                | `trade.futures.amend_limit_order`                                                                                                                             | **类型 A**                                                                | **同窗「现货逻辑改单」版式**；**域替换为永续**（开平、张币、`reduceOnly`）                                                                     | **§2.5.4 逻辑改单**                                                                                                                                                                        |
| **止盈止损 / 条件委托**             | `trade.futures.take_profit_stop` / `futures.condition.order_create`                                                                                        | **类型 A**（**独立于单笔 `order` 链路**）                                          | `触发条件` **语义块在先** → **与普通即时挂单首屏可读分离** → **触发后市价/限价语义** → **✓ / ✗**；`TBD` → `FR-T05`                          | **§2.5.4 止盈止损条件**；[`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 合约止盈止损分流**                                                                                             |
| **理财申购 / 赎回 / 档位等**         | **wealth** `scenarioId` **族**；同窗 [`routing-engine` §2](../agent-orchestration/routing-engine.md)、[`wealth-via-agent`](../../../flows/wealth-via-agent.md) | **类型 A 为主**；**`WEALTH_ACTION_REQUIRES_WEB` → Deeplink / Web（同窗 flows）** | **产品与 wealth flows、`FR-WEB*`一致**；**卡面须有可读摘要** → **✓ / ✗ 或「跳转 Web/H5」**；**禁止未冻结 PATH**                                   | **§2.5.5**；[`wealth-via-agent`](../../../flows/wealth-via-agent.md)                                                                                                                    |
| **就绪 / API / 绑定阻断（非本笔委托写）** | **（路由不产生交易 payload）**                                                                                                                                             | **类型 B**                                                                | **稳定归因短文 + 站内可点 Deeplink 或可点 `inline` URL** — **同窗 [`telegram-binding`](../onboarding/telegram-binding.md) `TG-GWT-*`** | [`telegram-binding.md`](../onboarding/telegram-binding.md)                                                                                                                         |
| **只读账单摘要 / Help**           | **—**                                                                                                                                                             | **类型 C**                                                                | **不要求「确认交易所写」的键盘**（可有「看流水」跳转）                                                                                           | [`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md)                                                                                                       |
| **跨会话记忆 · 查看 / 撤销**        | **（非 `scenarioId` 写路径）**；**宿主** [`memory-runtime` §9](../../../Runtime/memory-runtime.md)                                                                   | **类型 C**（**撤销** **含** **二次确认键盘** **·** **非类型 A**）                      | **人话摘要 + 清空二次确认**；**禁止** **账户真值/内部键** — **§2.7**                                                                      | **§2.7**；**`SC-CH-TG-MEM-*`**                                                                                                                            |
| **清空本会话（STM）**              | **（非 `scenarioId` 写路径）**；**宿主** [`memory-runtime` §13](../../../Runtime/memory-runtime.md)                                                                  | **类型 C**（**可选** **一次确认** **·** **非类型 A**）                               | **说明清 L0/活跃 L1、保留 LTM**；**未确认类型 A 须放弃** — **§2.8**                                                                      | **§2.8**；**`SC-CH-TG-STM-*`**                                                                                                                            |
| **条件触发告警 / Push**           | [`automation-alerts`](../../../flows/automation-alerts.md)；**同窗 `scenario` 族（`design` 终裁）**                                                                   | **多为类型 D**；**若须用户再做交易所写 → 另行类型 A**                                      | **提醒类口吻；`executionId` 或协查短链可查** — **同窗 本文 §3.1、[Runtime/execution](../../../Runtime/execution.md) 附录 A**                | [`execution`](../../../Runtime/execution.md)、[`unknown-state`](../../../Runtime/unknown-state.md)、[`observability/overview`](../../../observability/overview.md)           |


#### 2.5.0a 类型 A · 正文格式、渲染与设计规格（需求下限）

**性质**：约束 **单条类型 A 气泡正文**（由 Telegram Bot API `sendMessage` / `edit_message_text` 之 `text` 正文承载）之 **层级、Markdown/HTML 用法、留白与禁忌**；**字段语义下限仍以 §2.5.x 元素表为准**。**人类可读复述**：[`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md) **§Telegram 能做的边界**。**Prompt 侧**：[`prompts/shared/response-format`](../../../prompts/shared/response-format.md) **Markdown 降级** **同窗**。

##### 渲染与编码（MUST）

- `parse_mode`：**须**与 [`design/api`](../../../../design/api.md) **「Telegram Bot API」** **专节同窗**（**`Markdown` / `HTML` / `MarkdownV2` 三选一**，默认值由 **`design`** 冻结）。**渲染失败** → **降级纯文本须可观测**（**禁止静默丢消息**）；降级后 **仍须保留 §2.5.x 必选语义**（**允许失去粗体/链接**）。  
- **禁止**：以 **不可序列化之大块 JSON**、**内部网关载荷** **顶替** **用户可读摘要**；**REST PATH**、**堆栈** — **同窗** **§2.5.0 · 通用版式** **与** [`prompts/shared/response-format`](../../../prompts/shared/response-format.md)。

##### 版式与信息层级（MUST）

1. **分段留白**：**短标题 / 决策参数块 / 风险披露 / 操作提示（引导按键）/ 时效附注** **之间** **须有空行**（`\n\n`）。**唯有** **逼近 §2.6** **长度上限** **时** **允许压缩**：**压缩顺序** — **先缩短附注与套话** → **再合并次要空行** → **不得** **删除** `§2.5.x` **必选字段句**（**含** **流动性/滑点类风险一句** **等**）。
2. **标题**：**业务线** **须短**；**推荐** **单行粗体标题**（Markdown **粗体** **语法或** HTML `<b>`）；**不推荐** **以整行 ASCII 装饰线**（**如** `—— … ——`）**作为唯一主标题层级** **而无粗体标题**。
3. **决策参数呈现**：**禁止** **仅以裸 API 字段名**（`symbol`、`side`）**充当** **`effective_locale`** **语境下的用户主标签**。**须** **本地化标签 + 值**。**代码样式**（反引号包裹片段 **或** HTML `<code>`）**仅用于** **交易对、精确数值、必要枚举字面** **等需视觉区分的片段**；**禁止** **整块参数表滥用 monospace** **致可读性低于普通正文**。
4. **列表一致性**：**无序列表** **或** **「标签：值」** **行** **均可**；**同一** **`scenarioId`** **族内**同类确认卡须排版风格一致（**运营模板 / 控制台卡片模板 / Prompt Pack** 由 **`design`** 冻结）。
5. **风险披露**：**须有独立视觉段落**（**单独一段或独立列表块**），**与** **决策参数块** **勿混为同一 monospace 代码围栏**。
6. **核对语**：引导用户点击 **`inline_keyboard`** 的句子须置于风险段之后、按钮语义之上；**避免**「二次确认」等易被理解为「还有第三步」的措辞 — **除非**产品与 §2.4 另行冻结释义。

##### `inline_keyboard`（MUST）

- **同窗语**：按钮字面须与正文 **`effective_locale`** 一致（**§2.4**）。  
- `callback_data`：**≤64B（UTF-8）** — **§2.6**；**载荷** **仅存短 id**，**明细** **服务端解析**。

##### 规范性示例（性质）

- **§2.5.2～§2.5.5** **各场景所附「规范性正文示例」为骨架**：占位变量由运行时替换；运营可微调用词 **不得删除必选语义块**。表中 **`scenarioId`** 若未有独立 fenced 示例，须在同窗 MR 中按本节 MUST 补骨架或明示引用同类模板类推（类型 B/C/D 见 **`product/telegram-and-cards`** 与 **§2.5.5** Web 回退示例）。

#### 2.5.1 通则

- **类型 A～D 语义**（人类阅读）：[`../../../../../product/telegram-and-cards.md`](../../../../../product/telegram-and-cards.md)。  
- **内联键盘 / 撤回 / 暗色模式** 等 **交互自检**：[`interaction-flow-standard` §8](../../../standards/interaction-flow-standard.md)。  
- `callback_data` / 正文长度 / `answerCallbackQuery`：**§2.6**。

#### 2.5.2 现货（闪兑 / 限价 / OCO / bracket）

**流程 SSOT**：[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **「交易写 · 四业务线」**、`S11`～`S17`、**专节 · 现货限价**。

**路由**：**市价**（即时撮合、无委托价）→ **`trade.spot.flash_convert`** **族**（**非** **`margin.cross.*`**，**除非**用户明确杠杆借还语义 — **同窗** **专节 · 全仓杠杆 · 第一步**）。**限价挂单** → **`trade.spot.limit_order`**。**在途限价改价/改量**（无 amend API）→ **`trade.spot.amend_limit_order`**（[`routing-engine.md`](../agent-orchestration/routing-engine.md) §2；[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单**）。**OCO / bracket** → **`trade.spot.oco`** / **`trade.spot.bracket`**：[参见 [`product.md`](../../../product.md) **§非目标**] **本阶段 Agent 不交付现货 OCO/bracket 写**，**不须实现** **`call_exchange_write`**；**须** **`FR-T05` / 主站 / 分步入场离场**。**矩阵 PATH `TBD`** **同窗** — **禁止**类型 A **假双挂**。  

##### 闪兑 · 类型 A 卡面下限（`trade.spot.flash_convert`）

与 [`trade-via-agent`](../../../flows/trade-via-agent.md) **`S14`「生成确认卡片」** **同窗**；卡面 **须** **一目了然为「市价 / 闪兑」** **而非** **限价挂单**，**且** **非** **全仓杠杆单**（除非 **错误路由** — **须** `FR-T07` **纠偏**）。


| 元素                  | 下限                                                                                                                                                                                                      |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **产品线 / 门禁**        | `FEATURE_TRADING=ON` **且** `FEATURE_AGENT_SPOT=ON`；关 → **可读拒答**，**禁止** **静默走写**（同窗 `trade-via-agent` **专节 · 现货限价 · 前置** 精神）。                                                                |
| **编排锚**             | `scenarioId` `trade.spot.flash_convert` **族** — [`routing-engine.md`](../agent-orchestration/routing-engine.md) **§2**、[`trade-assistance.md`](../exchange-agent/trade-assistance.md) **§8.2**。 |
| **业务线**             | **币币 · 闪兑**（文案 **禁止** **冒充限价委托价**）。                                                                                                                                                                     |
| **symbol**、**side** | **交易对**、**买/卖**。                                                                                                                                                                                        |
| **成交口径**            | **base 数量** **或** **quote 金额（如 USDT）** **二选一**，**单位写清**（同窗 `S11` **槽位**）。                                                                                                                           |
| **市价语义**            | **须有** **可读「市价 / 即时 / 闪兑」等价表述**（[`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md) **§币币（现货）·市价**）。                                                                           |
| **风险一句**            | **须有** **流动性 / 滑点类提示**（篇幅 **遵守 §2.6** **长度上限**）。                                                                                                                                                        |
| **多腿 / 条件**         | **若**用户表达 **入场 + 离场组合**：同窗 `trade-via-agent` `S12` — **矩阵未冻结** **组合能力** **须** **分步或拒答**，**禁止** **单卡虚构「已全部挂好」**。                                                                                     |
| **写 API**           | **仅** **矩阵已登记** **现货市价/闪兑 PATH** — `TBD` **→** `FR-T05` **透明拒答**。                                                                                                                               |


##### 闪兑 · 规范性正文示例（`trade.spot.flash_convert`）

**须** **符合** **本节元素表** **与** **§2.5.0a**。以下为 **`zh-Hans` / `en` 骨架（变量位示意）**。

**`zh-Hans`（Markdown 示意 · `parse_mode` 以 `design` 为准）**：

```markdown
**现货闪兑（市价）**

请确认以下委托：

• **交易对**　BNB-USDT  
• **方向**　买入  
• **数量**　0.02 BNB（市价撮合，成交量以成交为准）

市价委托受盘口流动性影响，成交价可能与即时盘口略有偏离。

请核对无误后点击下方按钮操作。

（15 分钟内有效；重复发起以最近一次为准。）
```

**`en`（示意）**：

```markdown
**Spot flash convert (market)**

Please confirm:

• **Pair**　BNB-USDT  
• **Side**　Buy  
• **Size**　0.02 BNB (market fill; executed amount subject to fills)

Market orders may slip versus the current book.

Tap a button below to continue.

(Valid 15 minutes; latest request wins.)
```

**`inline_keyboard` 字面须与 `effective_locale` 同窗**：`zh-Hans`：**确认下单** · **取消**；`en`：**Confirm** · **Cancel**（**或**等价短动词，**须**产品与 §2.4 对签）。**TTL 文案数值**由 **`design`** **冻结**；**骨架结构同窗上文括号句**。

##### 闪兑 · 提交后 / 终局成功 / 失败用户可见（非类型 A）

**约束 SSOT**：[`trade-via-agent`](../../../flows/trade-via-agent.md) **S5.1.1**、**S9**；**本文 §3.1**；[`prompts/shared/response-format`](../../../prompts/shared/response-format.md)；[`unknown-state`](../../../Runtime/unknown-state.md)。**说明**：**非** **第二张类型 A**；**可无 `inline_keyboard`。

###### 总则（MUST）

1. **禁止含糊「成功」**：**不得** **仅用** **「已完成」「成功了」** **而不区分** **① 交易所已受理委托（撮合中，尚未等价于买入/卖出成交终局）** **与** **② 买入或卖出已在交易所成交且本笔执行终局闭合**。标题 **须** **让读者一眼看出是哪一种**（**见下表**）。
2. **失败与卡点**：**每条回复须** **结论（人话一句）+ 下一步怎么做**（**可执行** **≥1** **步**）；**禁止** **HTTP 状态码**、**上游 JSON `code`/`msg` 原文**、**REST PATH**、**堆栈**、**内部 `stableReason`/`AGENT_*`/英文拒码枚举** **整段甩给用户** — **同窗 `response-format` §2**。**运行时仍将上游归入下列「情境桶」再选话术**；**桶→文案映射**由 **`design` / copy deck** **冻结**。
3. **协查编号**：**仅在需要客服/运维协查时**，**宜**单行给出「协查编号：`executionId`」；**勿与错误码、内部枚举混在同一视觉块**。**`en`/`zh-Hant` 三桶须同窗对称**。

###### 阶段用词 · 标题与首句（MUST）


| **对内事实（示例）**                         | **标题须有之义（`zh-Hans` · 示意）**              | **首句须澄清（示意）**                                    |
| ------------------------------------ | --------------------------------------- | ------------------------------------------------ |
| **已拿到 `orderId`，撮合未完成或未闭合对账**           | **现货闪兑 · 委托已受理**                        | **交易所已受理你的委托，正在撮合；尚未视同「买入/卖出已经成交」终局。** |
| **市价闪兑成交终局已闭合（可对账成功）**               | **现货闪兑 · 买入已成交** **或** **现货闪兑 · 卖出已成交** | **本次买入/卖出已在交易所成交；本笔执行已收尾。**                      |


**禁止**：**单独使用**「已完成」类标题，且不标明 **委托已受理** 或 **买入/卖出已成交** 之一语义。


| **`effective_locale` / 版式** | **条文**                                                               |
| --------------------------- | -------------------------------------------------------------------- |
| **方向**                      | **`zh-Hans` 须** 使用 **买入 / 卖出**；**禁止** **仅以 **`BUY`/`SELL`** 展示**。 |
| **数值**                      | **须带单位** — **同窗** [`response-format`](../../../prompts/shared/response-format.md) **§2**。                                |
| **标题形态**                    | **宜**单行粗体 **`现货闪兑 · …`** — **同窗** §2.5.0a。                    |


**规范性示意 · 委托已受理（`zh-Hans` · Markdown）**：

```markdown
**现货闪兑 · 委托已受理**

交易所已受理你的委托，正在撮合；尚未视同买入已成交终局。

• **交易对**　BNB-USDT  
• **方向**　买入  
• **数量**　0.02 BNB  
• **订单号**　`3277924434867121367`

成交量与成交均价以交易所回报为准；若有成交更新，我会按同一链路告知你。
```

**规范性示意 · 买入已成交（`zh-Hans` · Markdown · 终局闭合后）**：

```markdown
**现货闪兑 · 买入已成交**

本次买入已在交易所成交，本笔执行已收尾。

• **交易对**　BNB-USDT  
• **买入数量**　0.02 BNB  
• **成交均价（若有）**　××× USDT  
• **订单号**　`3277924434867121367`

流水可在账单中核对。
```

（**卖出已成交** **同窗** **替换「买入」措辞**。）

###### 提交失败 / 拒答 · 情境桶与用户话术（MUST：结论 + 怎么做）

**下列「情境桶」为归类示意；对用户只输出右栏话术风格，不暴露桶名、错误码或上游原文。**


| **情境桶（对内 · 勿给用户）**            | **给用户的一句话结论（`zh-Hans` · 示意）** | **须包含的下一步（怎么做）**                                                          |
| ----------------------------- | ----------------------------- | ------------------------------------------------------------------------- |
| **余额 / 可用不足**                 | 这笔没能提交——当前可用余额不够完成这笔买入/卖出。    | 请先充值或换更小的金额；准备好后在**本对话**再说一次要买/卖多少，我再发起确认。                                |
| **数量·精度·最小名义·步进不符**           | 这笔没能提交——数量或金额不符合当前交易对的规则。     | 在**本对话**告诉我你想改成多少（可按提示单位），我再帮你走一张新的确认卡。                                   |
| **交易对不可用（下架、暂停等）**            | 这笔没法下单——这个交易对暂时不能交易。          | 换一个交易对试试，或到主站查看最新可交易列表。                                                   |
| **风控限额 · 单日上限 · 功能未开放（产品卡点）** | 这笔暂时不能通过助手提交——受当前规则或功能范围限制。   | 可先尝试在主站完成同类操作，或稍后再试；仍需要帮助可在对话里说明诉求。                                       |
| **确认超时 / pending 失效**         | 刚才的确认已过期，没能继续生效。              | 在本对话重新说清楚交易意图，我再发起一张新的确认卡。                                                |
| **短时重复点击 / 幂等冲突**             | 短时间内收到了重复提交，为避免重复下单已拦截后续一次。   | 先不要连点；等几秒让我在对话里帮你核对持仓或挂单，再决定是否重试。                                         |
| **UNKNOWN / 504 · 结果未决** | 这边还不能确定交易所最终有没有受理成功。 | **不要马上再下一笔同样的单**；过几分钟在对话里让我帮你查挂单/持仓，或再说一次操作意图。 — **同窗** [`unknown-state`](../../../Runtime/unknown-state.md) |
| **瞬时网络 / 网关失败（已判失败）** | 刚才网络不稳，委托没能送达交易所。 | 请在对话里重复一次同样操作，或稍后轻试；勿短时间内频繁连点。 |


**禁止（再声明）**：**不得在正文列出数字错误码、HTTP 状态字面**；**不得以内部稳定拒码或 `AGENT_*` 枚举作为主文案**；**不得照搬上游英文错误原文作主提示**。（**对内仍可映射 `stableReason`。**）

##### 限价 · 类型 A 卡面下限（`trade.spot.limit_order`）

**正文逐字段终裁**：[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 现货限价 · 「Telegram 类型 A 下限（现货限价）」**。摘要：


| 元素                  | 下限                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------- |
| **业务线**             | **币币**（与杠杆/合约 **版式可区分**）。                                                                   |
| **symbol**、**side** | **交易对**、**买/卖**。                                                                            |
| **订单类型**            | **限价**。                                                                                     |
| **委托价**             | **报价币单价**（**须有明确数字**）。                                                                      |
| **数量 / 名义**         | **base 数量** **或** **`quoteQty`/成交额** **二选一** **且** **单位写清**。                                |
| `timeInForce`   | **API 必选或用户已选** → **卡面须有**（GTC / IOC / FOK 等）。                                              |
| **建议价第二张卡**         | `S15` **路径** → **须** **明示「价格已按系统建议调整」或等价** — **同窗** [`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 偏离带**。 |


##### 限价 · 规范性正文示例（`trade.spot.limit_order`）

**须** **符合** **本节元素表** **与** **§2.5.0a**。`S15` **第二张卡** **须在标题或首段** **明示建议价调整**（**同窗** [`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 偏离带**）。

**`zh-Hans`（Markdown 示意）**：

```markdown
**币币限价挂单**

请确认以下委托：

• **交易对**　BTC-USDT  
• **方向**　卖出  
• **订单类型**　限价  
• **委托价**　65,000 USDT  
• **数量**　0.001 BTC  
• **有效期（timeInForce）**　GTC（成交前有效）

限价委托不保证即时全部成交；实际成交以订单簿与撮合结果为准。

请核对后点击下方按钮操作。

（15 分钟内有效；重复发起以最近一次为准。）
```

**`S15` · 建议价第二张卡（示意 · `zh-Hans`）**：

```markdown
**币币限价挂单 · 价格已调整**

系统已按可成交价带你调整了委托价，请再次确认：

• **交易对**　BTC-USDT · **卖出**  
• **委托价（已调整）**　64,950 USDT  
• **数量**　0.001 BTC · **有效期**　GTC

你也可以取消后在对话中改用自选价格。

（15 分钟内有效。）
```

**`en`（示意）**：

```markdown
**Spot limit order**

Please confirm:

• **Pair**　BTC-USDT  
• **Side**　Sell  
• **Order type**　Limit  
• **Limit price**　65,000 USDT  
• **Size**　0.001 BTC  
• **Time in force**　GTC

Limit orders are not guaranteed to fill immediately.

Tap a button below to continue.

(Valid 15 minutes; latest request wins.)
```

**`inline_keyboard`（同窗 `effective_locale`）**：`zh-Hans`：**确认下单** · **取消**；`en`：**Confirm** · **Cancel**。**`S15` 第二张卡**须同窗或明示「接受建议价」之第三钮 — **`design`** 冻结。

##### 限价 · 提交后 / 终局成功 / 部成 / 失败用户可见（非类型 A）

**同窗**：[`trade-via-agent`](../../../flows/trade-via-agent.md) **S5.1.1**（**部成/在途** **为子态，不抬主行**）；**上文 · 闪兑 · 总则（MUST）** **与** **「提交失败 / 拒答 · 情境桶」表** **全文适用**（**结论 + 怎么做**、**禁裸码**）。**本节仅补限价专有阶段词与增量桶。**

###### 阶段用词 · 标题与首句（MUST）

| **对内事实（示例）** | **标题须有之义（`zh-Hans` · 示意）** | **首句须澄清（示意）** |
|---------------------|--------------------------------------|-------------------------|
| **限价单已进入订单簿，尚无成交** | **币币限价 · 委托已挂单** | **单已挂上；尚未成交**，**不等于**「已经买到/卖到」终局。 |
| **部分成交，剩余仍在簿（部成）** | **币币限价 · 部分已成交** | **已有一部分按你的限价成交**；**剩余数量仍在挂单**，**可撤可改**（**以所内能力为准**）。 |
| **挂单数量全部成交，终局闭合** | **币币限价 · 已全部成交** | **挂单已全部成交**；本笔限价执行已收尾。 |
| **IOC / FOK 等即时尝试后未在盘口长期停留（含完全未成交）** | **币币限价 · 未成交（即时单）** | **按所选有效期**，**订单未按预期留在盘口或未完全成交**（**口径以交易所回报为准**）。 |

**禁止**：**单独使用「已完成」** **而不说明** **已挂单 / 部成 / 全成 / 即时单未成交** **之一**。

###### 限价 · 增量失败 / 认知情境桶（MUST：结论 + 怎么做）

**下列为限价** **增量** **桶；** **其余失败** **仍用** **闪兑失败总表**。

| **情境桶（对内 · 勿给用户）** | **给用户的一句话结论（`zh-Hans` · 示意）** | **须包含的下一步（怎么做）** |
|------------------------------|---------------------------------------------|------------------------------|
| **用户误以为「限价」会立刻成交** | 限价单是排队等成交——**价格没到就不会立刻买到/卖到**。 | 在对话里让我帮你**查当前挂单**；若要更快成交，可以说一个**更接近盘口**的价格，我再发起确认。 |
| **部成后用户不确定剩余** | 刚才成交了一部分，**还剩一部分在挂单**。 | 可以说「查挂单」或「全撤」等意图（**以助手支持的能力为准**），我在对话里帮你处理。 |

**规范性示意 · 委托已挂单（`zh-Hans` · Markdown）**：

```markdown
**币币限价 · 委托已挂单**

你的限价单已在交易所挂单；**尚未成交**，不等于已经买到/卖到终局。

• **交易对**　BTC-USDT  
• **方向**　卖出  
• **委托价**　65,000 USDT  
• **数量**　0.001 BTC · **有效期**　GTC  
• **订单号**　`…`

未到价前不会成交；有变化我会按链路更新你。
```

##### 逻辑改单 · 类型 A 下限（`trade.spot.amend_limit_order`）

**流程 SSOT**：[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单**。**须**在上表 **限价** **元素** **之外** **额外** **可见**：


| 元素            | 下限                                                                                                                                                                     |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **标题 / 首屏语气** | **宜** **顶层可读标题** **等价于** **「修改挂单」** / **「调整限价委托」** — **避免** **仅用** **内部** **`scenarioId`** **或** **「撤单+下单」** **充当用户第一眼文案**（**实现** **可** **放在** **气泡首行** **或** **加粗首句**）。 |
| **操作语义**      | **可读「修改在途挂单」** **而非** **冒充单笔交易所 amend**。                                                                                                                               |
| **原委托**       | **可追溯键**（**`orderId` 或 `clientOrderId` 摘要**）**+** **原 symbol/side** **摘要**。                                                                                        |
| **新旧对比**      | **须** **让用户** **无需心算** **能看出** **变更点**：**至少** **原价→新价**、**原数量→新数量**（**可用** **两行对照** **「原为 … → 调整为 …」**；**篇幅** **受 §2.6** **约束** **可** **压缩** **为小表格** **或** **项目符号**）。 |
| **新委托**       | **与** **新开限价单** **同等级** **的价、量**、**`timeInForce`**（若适用） — **须为拟提交之最终参数**。                                                                           |
| **两阶写披露**     | **正文须** **含** **「确认后将先撤销原单，再提交新单」**（**或** **等价表述**）。                                                                                                                   |
| **主按钮标签**     | **宜** **区分** **于** **普通下单**：例如 **「确认修改」** / **「取消」** — **禁止** **仅** **「确认」** **且** **标题** **不** **提示** **系** **改单** **致** **与** **首单** **混淆**。                         |


##### 现货限价 · 逻辑改单 · 规范性正文示例（`trade.spot.amend_limit_order`）

**须** **符合** **本节元素表** **与** **§2.5.0a**；**长文案 / 分阶段话术** **同窗** [`product/telegram-logical-amend-copy.md`](../../../../product/telegram-logical-amend-copy.md)。

**`zh-Hans`（Markdown 示意）**：

```markdown
**修改挂单（限价）**

将按「先撤销原单，再提交新单」处理（并非交易所原生一键改单）。

• **原委托**　`orderId …7821` · BTC-USDT · 卖出  
• **原价 → 新价**　65,000 → 64,800 USDT  
• **原数量 → 新数量**　0.001 → 0.002 BTC  
• **有效期**　GTC  

确认后系统将先撤掉原限价单，再挂上新委托。

请核对后点击下方按钮。

（15 分钟内有效。）
```

**`en`（示意）**：

```markdown
**Amend limit order**

This uses cancel-then-replace (not a native amend).

• **Working order**　`orderId …7821` · BTC-USDT · Sell  
• **Price**　65,000 → 64,800 USDT  
• **Size**　0.001 → 0.002 BTC  
• **Time in force**　GTC  

Confirm to cancel the working order and submit the new limit.

(Valid 15 minutes.)
```

**`inline_keyboard`（同窗 `effective_locale`）**：`zh-Hans`：**确认修改** · **取消**；`en`：**Confirm change** · **Cancel**。

##### 逻辑改单 · 确认后体验（`trade.spot.amend_limit_order`）


| 阶段          | UX 下限                                                                                                                                                                                                                                                                            |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **点按后即时反馈** | **遵守** **§2.6**：**尽快** `answerCallbackQuery` **结束** **客户端** **loading**；**忌** **十数秒** **无** **应答**。                                                                                                                                                                          |
| **进行中**     | **可** `edit_message_text` **或** **追加** **一条** **短消息**：**阶段 1** **等价** **「正在撤销原委托…」**；**阶段 2** **等价** **「正在提交新委托…」**（**总耗时长时** **宜** **一句** **「交易所处理可能需数秒」** **管理预期**）。**若** `edit_*` **因消息过旧等原因失败** **须** `sendMessage` **兜底**，**忌** **用户** **看不到** **进度**。 |
| **成功**      | **一句** **可核对摘要**（**新** **委托价/量/单号摘要**）**+** **不提** **「交易所替你改了一笔 amend」** **若** **实际** **为** **两阶写**。                                                                                                                                                                             |
| **撤单失败**    | **说明** **原单** **仍在**（**或** **UNKNOWN** **须** **引导** **主站/查单**）**+** **未** **提交** **新单**；**给** **下一步**（**重试 / 主站**）。                                                                                                                                                              |
| **撤成单败**    | **须** **明确** **「原挂单已撤，新委托未挂上」** **类** **表述** **+** **建议** **在** **对话中重试** **或** **主站下单** — **禁止** **「已改好」**。                                                                                                                                                                     |


**i18n 模板（简中 + English）**：[`product/telegram-logical-amend-copy.md`](../../../../product/telegram-logical-amend-copy.md)。

###### 逻辑改单 · 确认后 · 总则（MUST）

**同窗** **§2.5.2 · 闪兑 · 总则（MUST）**：**结论 + 可执行下一步**；**禁止** **对用户裸露错误码/上游 `msg`/HTTP 字面**。逻辑改单 **对内为撤单→再挂单两笔写**，**对用户** **不得称「交易所原生一键改单已成功」** **除非** **产品与网关叙事已单列闭合**。

###### 逻辑改单 · 确认后 · 阶段话术 · 规范性示意（`zh-Hans` · Markdown）

**进行中（宜短，可合并为一句）**：

```markdown
正在处理：先撤销原挂单，再提交新挂单（可能需要几秒）。
```

**成功（新委托已在交易所侧就绪 · 示例：限价已挂上）**：

```markdown
**修改挂单 · 新委托已挂上**

原挂单已撤销，新的限价委托已在交易所侧就绪（**尚在簿或未立即全部成交** **以交易所为准**）。

• **交易对**　BTC-USDT · **卖出**  
• **委托价**　64,800 USDT · **数量**　0.002 BTC · **有效期**　GTC  
• **新订单号**　`…`

若要看是否已有成交，可在对话里让我帮你查挂单与成交明细。
```

**撤单失败（原单仍在 · 新单未提交）**：

```markdown
**修改挂单 · 没能完成**

没能撤销原来的挂单，**新的委托也没有提交**，你当前的挂单状态应以交易所为准。

请在对话里让我帮你**查当前挂单**，或稍后轻试；不要假定价格已经改好。
```

**撤单成功但新单失败（「撤成单败」）**：

```markdown
**修改挂单 · 仅完成了一半**

原来的挂单已撤掉，但**新的委托没能挂上**。

请在对话里**再说一遍你想委托的价格和数量**，我再帮你走一张新的确认卡。
```

###### 逻辑改单 · 增量失败 / 拒答情境桶（MUST：结论 + 怎么做）

**下列为改单** **增量** **桶；** `UNKNOWN`/504、余额、精度、确认超时等** **仍优先套用 §2.5.2 闪兑失败总表**。

| **情境桶（对内 · 勿给用户）** | **给用户的一句话结论（`zh-Hans` · 示意）** | **须包含的下一步（怎么做）** |
|------------------------------|---------------------------------------------|------------------------------|
| **原单状态已变（已成交/已撤/不存在）** | 没法按刚才那张卡改单——**原来的挂单状态已经变了**。 | 在对话里让我**查当前挂单/成交**，再说你想怎么调整，我再发起新的修改流程。 |
| **新单参数与交易所规则冲突（步进/最小名义等）** | 旧单撤掉了，但**新价格或数量不符合规则**，没能挂上。 | **告诉我改后的数量或价格**，我重新生成确认卡（**勿甩错误码**）。 |
| **改单途中会话过期** | 确认已过期，**撤单/挂单可能没有按预期全部走完**。 | **不要乱点历史按钮**；在对话里让我**查单**，再根据真实状态重试。 |

##### OCO / bracket（`trade.spot.oco` / `trade.spot.bracket`）

- **意图路由**：**独立 `scenarioId` — [`routing-engine.md`](../agent-orchestration/routing-engine.md) **§2**。  
- **矩阵 PATH 未冻结**：**须** `FR-T05` **透明降级** — **不得** **类型 A 暗示已双挂/已 bracket 成交杠**。详情同窗 `trade-via-agent` **专节 · 现货限价 · 「与 S12…及现货条件单的交界」**。

##### OCO / bracket · `FR-T05` 降级 · 用户可见正文示例（**非**写确认类型 A）

**当** **矩阵 PATH `TBD`** **或** **能力未闭合**：**禁止** **下发可触发写 API 之类型 A**。以下为 **`zh-Hans` / `en` 可读拒答骨架**（**无** **「确认下单」写意图按钮**，**或** **仅** **「打开主站」「我知道了」** — **`design`** **冻结**）。

**`zh-Hans`（示意）**：

```markdown
**暂无法在 Telegram 完成该组合挂单**

OCO / bracket 相关接口仍在矩阵冻结或扩容中，Agent 当前不能替你完成双挂或括号单闭环。

请先在交易所主站或App「现货委托」中操作，或在对话中改为单笔限价/市价等已开放能力。

如需协查，可提供 executionId。
```

**`en`（示意）**：

```markdown
**This combo order isn’t available in Telegram yet**

OCO/bracket paths aren’t enabled for Agent in the current API matrix.

Please use the exchange web/app order screen, or switch to a supported single-leg flow in chat.
```

#### 2.5.3 杠杆（全仓 cross · `FEATURE_AGENT_MARGIN`）

**流程 SSOT**：[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 全仓杠杆交易**。**门禁**：`FEATURE_TRADING` + `FEATURE_AGENT_MARGIN`、**FR-T02 / FR-T01**、**写前** `read_skill_operation_spec`（FR-T11）**。**路由**：**仅当用户明确杠杆/借还语义** → `margin.cross.market_order` / `margin.cross.limit_order`；**划转** → `margin.cross.transfer_in`（[`routing-engine.md`](../agent-orchestration/routing-engine.md) **§2**）。**逐仓（isolated）** **另立法**，**禁止**与本节 **cross** **混路由**。

##### 全仓市价 · 类型 A 卡面下限（`margin.cross.market_order`）

**正文逐字段与预检档位** — [`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 第六步**。摘要：


| 元素                  | 下限                                                                                                                                        |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **业务线**             | **全仓杠杆（cross）** — **须与现货闪兑 / 现货限价 / 合约** **一眼可区分**（[`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md) **§杠杆**）。 |
| **symbol**、**side** | **交易对**；**买（借买）/卖（卖还）** **等口语** **映射为可读 `side` 文案**（**禁止** **裸字段名**）。                                                                     |
| **订单类型**            | **市价**。                                                                                                                                   |
| **名义或数量**           | **USDT 金额** **或** **标的数量** — **二选一须写清**；**含糊** → **追问**（同窗 **专节 · 第三步**）。                                                                 |
| **借币与计息**           | `autoBorrow` **默认 true** **时** **须有** **计息 / 浮动利率可读披露**（口径 **所内 / OpenAPI 冻结**）。                                                      |
| `autoRepay`     | **若 API 与用户意图启用** → **卡面须有** **可读说明**（卖出顺带还款）。                                                                                            |
| **风险档摘要**           | **预检后低/中/高** — **中、高档** **须有** **加码风险提示**（**禁止** **仅展示内部枚举码**）。                                                                           |


##### 全仓限价 · 类型 A 卡面下限（`margin.cross.limit_order`）


| 元素      | 下限                                          |
| ------- | ------------------------------------------- |
| **委托价** | **须有明确限价数字**（**同窗** **专节 · 第三步** **限价语义**）。 |
| **其余**  | **同窗** **上表「全仓市价」** **各行**（订单类型改为 **限价**）。  |


##### 全仓杠杆 · 规范性正文示例（首张 · `margin.cross.market_order` / `margin.cross.limit_order`）

**须** **符合** **§2.5.3** **元素表** **与** **§2.5.0a**。**首张与第二张** **按钮字面** **由 `design`/运营模板** **冻结**；**下示 `zh-Hans` **市价 / 限价** **两套首张 + 第二张骨架**（字段与 `trade-via-agent` **专节对签**）。

**首张 · `zh-Hans`（市价 · Markdown 示意）**：

```markdown
**全仓杠杆 · 市价（首张核对）**

• **模式**　全仓（cross）  
• **交易对**　ETH-USDT  
• **方向**　买入（借币买入）  
• **名义**　100 USDT  
• **借币计息**　启用借币时将按平台规则计息（口径以产品说明为准）  
• **风险档位（预检）**　中 — 请注意杠杆与强平风险  

市价成交受流动性影响，成交价可能与盘口略有偏离。

下方确认后，**还将有一张摘要卡进行二次确认**，再向交易所提交下单。
```

**第二张 · `zh-Hans`（市价 · 再次确认 · 示意）**：

```markdown
**全仓杠杆 · 市价 · 再次确认**

即将提交：

• **ETH-USDT** · **买入** · **市价** · **名义**　100 USDT · **风险档位**　中  

确认即发起下单请求。
```

**首张 · `zh-Hans`（限价 · Markdown 示意）**：

```markdown
**全仓杠杆 · 限价（首张核对）**

• **模式**　全仓（cross）  
• **交易对**　ETH-USDT  
• **订单类型**　限价  
• **方向**　买入（借币买入）  
• **委托价**　3,500 USDT  
• **数量**　0.10 ETH（口径与所内登记一致）  
• **借币计息**　启用借币时将按平台规则计息（口径以产品说明为准）  
• **风险档位（预检）**　中 — 请注意杠杆与强平风险  

限价委托不保证成交；撮合结果以交易所为准。

下方确认后，**还将有一张摘要卡进行二次确认**，再向交易所提交挂单。
```

**第二张 · `zh-Hans`（限价 · 再次确认 · 示意）**：

```markdown
**全仓杠杆 · 限价 · 再次确认**

即将提交：

• **ETH-USDT** · **买入** · **限价** · **委托价**　3,500 USDT · **数量**　0.10 ETH · **风险档位**　中  

确认即发起挂单请求。
```

`inline_keyboard`：**首张** `zh-Hans`：**继续** · **取消**（**或** **下一步** / **取消** — `design` **冻结）；第二张：确认下单 · 取消。`en` **同窗三桶** **自拟对称文案**。

##### 划转（现货 ↔ 全仓）· 规范性正文示例（`margin.cross.transfer_in` / `universal_transfer` **族**）

**每笔划转** **独立类型 A**。**`zh-Hans`（示意）**：

```markdown
**账户划转 · 现货 → 全仓**

• **币种**　USDT  
• **金额**　50 USDT  
• **方向**　现货钱包 → 全仓杠杆账户  

确认后即发起划转；完成后编排可继续后续下单（若本链路包含）。

（每笔划转单独确认。）
```

**`en`（示意）**：

```markdown
**Transfer · Spot → Cross margin**

• **Asset**　USDT  
• **Amount**　50 USDT  

Confirm to submit this transfer.
```

##### 强制二次确认（全仓写）

**首张类型 A 后** **须** **第二张摘要或等价交互** **再** `POST …/margin/order` — **同窗** `trade-via-agent` **专节 · 第七步**；**禁止** **单次确认** **覆盖下单写**。

##### 全仓杠杆 · 第二张确认后 / 终局 / 部成 / 失败用户可见（非类型 A）

**同窗**：[`trade-via-agent`](../../../flows/trade-via-agent.md) **S5.1.1**；**§2.5.2 · 闪兑** **总则（MUST）** **与** **失败情境桶总表**；[`unknown-state`](../../../Runtime/unknown-state.md)。**说明**：用户在 **连续两张类型 A** **均已确认** **之后**，结果气泡 **仍须** **区分** **「交易所已受理委托」** **与** **「借买/借卖成交终局」**，**禁止** **含糊「已完成」**。**市价** **对齐闪兑** **受理 vs 成交**；**限价** **对齐** **§2.5.2 · 现货限价** **已挂单 / 部成 / 全成**。**划转** **独立写** **的成功/失败** **同窗** **闪兑总表** **并见下文一句增量**。

###### 阶段用词 · 标题与首句（MUST）

| **对内事实（示例）** | **标题须有之义（`zh-Hans` · 示意）** | **首句须澄清（示意）** |
|---------------------|--------------------------------------|-------------------------|
| **全仓市价：`POST` 后已受理，撮合/终局未闭合** | **全仓杠杆 · 市价 · 委托已受理** | **交易所已受理你的全仓市价委托**；**正在撮合或待闭合**；**尚未** **视同「借买/借卖已经成交」终局。 |
| **全仓市价：成交终局已闭合** | **全仓杠杆 · 买入已成交（借买）** **或** **卖出已成交（卖还）** | **本次借买/卖还已在交易所成交**；本笔执行已收尾（**计息与风险仍以持仓页为准**）。 |
| **全仓限价：已在簿未成交** | **全仓杠杆 · 限价 · 委托已挂单** | **挂单已挂上**；**尚未成交**。 |
| **全仓限价：部成 / 全成** | **全仓杠杆 · 限价 · 部分已成交** / **已全部成交** | **同窗** **§2.5.2 · 现货限价** **部成/全成首句**。 |

###### 全仓 · 增量失败 / 拒答情境桶（MUST：结论 + 怎么做）

**下列为全仓** **增量** **桶；** **余额、精度、`UNKNOWN`/504、确认超时、风控入口关闭等** **仍优先套用 §2.5.2 闪兑总表**。

| **情境桶（对内 · 勿给用户）** | **给用户的一句话结论（`zh-Hans` · 示意）** | **须包含的下一步（怎么做）** |
|------------------------------|---------------------------------------------|------------------------------|
| **可借额度不足 / 借币未放行** | 这笔没能提交——**当前规则下借不到足够的币**完成这笔借买。 | 换更小名义、补充抵押资产，或先在主站调整杠杆/风险档位后再来对话重试。 |
| **全仓保证金率 / 风险档位拦截** | 这笔没能提交——**全仓风险档位或保证金率**不满足下单要求。 | 减仓、追加保证金，或换更小名义；准备好后在**本对话**再说一次意图。 |
| **划转已确认但未到账导致仍不可用** | 资金划转已发起，但**全仓侧可用还没跟上**，下单没能继续。 | **稍等片刻**让我在对话里帮你**再查可用**，或重新发起更小名义试单。 |

**规范性示意 · 全仓市价 · 委托已受理（`zh-Hans` · Markdown）**：

```markdown
**全仓杠杆 · 市价 · 委托已受理**

交易所已受理你的全仓市价委托；正在撮合或待闭合，尚未视同借买已成交终局。

• **交易对**　ETH-USDT · **方向**　买入（借买）  
• **名义**　100 USDT · **风险档位（预检）**　中  
• **订单号**　`…`

成交与计息以交易所回报为准。
```

###### 划转 · 提交后一句（`universal_transfer` / `margin.cross.transfer_in` **族**）

**成功（示意）**：「划转已提交；到账可能有短暂延迟，下单前可在对话里让我再查一次可用。」**失败**：**同窗** **§2.5.2 闪兑失败总表**，**勿暴露网关码**。

##### 首版禁止在卡面暗示的能力

**Agent 经 Telegram 闭环（全仓 cross）**：**撤单/改单**、**杠杆委托上止盈止损**、**自定义名义杠杆档位** → **须** **`FR-T05` + 主站 Deeplink**；**禁止** **类型 A 假装已执行** — **同窗** **专节 · 「本条首版 · 不向用户经 Agent 承诺」**。**币币/永续限价** **逻辑改单**（`trade.spot.amend_limit_order` / `trade.futures.amend_limit_order`）**不适用** **本条禁止** — **见** **§2.5.2 / §2.5.4** **逻辑改单** **专表** **与** `trade-via-agent` **专节 · 逻辑改单**。

##### 划转（现货 ↔ 全仓）

**典型用户只表述「杠杆买入/卖出」**：若 **全仓可用不足** **且** **同子账户币币可调拨**，**仍走** `margin.cross.*` **主意图**；**划转** **为** **前置子步骤** — **系统计算** **建议** **「币币 → 全仓」** **数额**（**同窗** `trade-via-agent` **专节 · 第四步**），**无须** **用户改口说「划转」**。**每笔**（`universal_transfer` / 划转写）→ **独立类型 A**；卡面 **须有** **币种 + 数额 + 方向可读**（**如** **现货 → 全仓**）。

#### 2.5.4 合约（永续 · 市价 / 限价 · 止盈止损 / 条件单）

**流程 SSOT**：[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 合约交易**、**合约止盈止损 · 分流**。**门禁**：`FEATURE_TRADING=ON` **且** `FEATURE_AGENT_FUTURES=ON`；**FR-T02 / FR-T01**（`fapi` **子账户 scope**）；**写前** **`read_skill_operation_spec`（FR-T11）**。  
**路由**：**永续开平仓单笔市价/限价** → `trade.futures.market_order` / `trade.futures.limit_order`（[`routing-engine.md`](../agent-orchestration/routing-engine.md) **§2**）；**在途永续限价改价/改量** → `trade.futures.amend_limit_order`（[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单**）；**触价离场 / 条件委托链** → `trade.futures.take_profit_stop` **或** `futures.condition.order_create`（**独立 `read_skill` + 类型 A**，**不得** **与本专节单笔 `order` 混为未声明多腿**）。

##### 通则 · 歧义与现货分流

- **须 0 或 1 主 **`scenarioId`**（FR-AO02）；冲突时 → **澄清或显式分步**。  
- **「现货、闪兑、币币」** **不得默认走 **`fapi`** — **同窗** `trade-via-agent` **专节 · 第一步**。  
- **歧义未消** → **严禁生成类型 A**（**同窗** **专节 · 第三步**）。

##### 永续市价 / 限价 · 类型 A 卡面下限（`trade.futures.market_order` / `trade.futures.limit_order`）

**正文逐字段终裁**：[`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 第六步**。摘要：


| 元素               | 下限                                                                                                                                                                                     |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **业务线**          | **合约 / 永续** — **须与现货闪兑、现货限价、全仓杠杆** **一眼可区分**（[`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md) **§合约**）。                                                    |
| **方向与开平**        | **开多 / 开空 / 平多 / 平空** **等可读语义**（**禁止** **裸 `side`/`positionSide` 字段名**）。                                                                                                               |
| **市价 / 限价**      | **市价** **不得** **展示用户委托限价**（**除所内滑点保护说明外**）；**限价** **须有明确委托价**。                                                                                                                         |
| **数量与单位**        | **张（CONTRACT）/ 币（BASE）** **二选一** **且** **卡面单位与 OpenAPI 一致** — **禁止** **混用观测语义**。                                                                                                       |
| **杠杆**           | **若与账户当前不一致且将先 **`edit_lever`** **等写** → **卡面须明示将先调杠杆再下单**。**与逻辑改单无关**：**当 **`edit_*` **与 **`order` **在同一编排链路为多意图时**，**仍须各自独立类型 A** — **同窗** **专节 · 第五步**；**逻辑改单见下文专表**。 |
| **保证金模式**        | **逐仓 / 全仓** **可读**；**若将 `edit_*` 调模式** → **同杠杆**，**须在确认链路明示**。                                                                                                                         |
| `reduceOnly` | `true` **时须在卡面可见**（**平仓语义**）。                                                                                                                                                      |
| **风控摘要**         | **预估保证金占用**；**市价** **单行滑点风险**；**限价** **说明不保证成交**。                                                                                                                                      |
| **禁止**           | **PATH**、**内部字段名**、**错误堆栈** — **同窗** **专节 · 第六步**。                                                                                                                                     |


##### 永续 · 市价/限价 · 规范性正文示例（`trade.futures.market_order` / `trade.futures.limit_order`）

**须** **符合** **本节元素表** **与** **§2.5.0a**。**市价** **替换限价相关行** **并** **保留滑点风险一句**；**限价** **保留「不保证成交」**。**杠杆若将单独 **`edit_*`** **须另卡** — **同窗** **上文「杠杆」行**。

**限价 · `zh-Hans`（示意）**：

```markdown
**永续合约 · 限价**

• **合约**　BTCUSDT  
• **方向与持仓**　开多  
• **委托价**　65,000 USDT  
• **数量**　0.01 BTC（单位与登记矩阵一致）  
• **杠杆**　10x  
• **仅减仓（reduceOnly）**　否  

限价委托不保证成交；撮合结果以交易所为准。

请核对后点击下方按钮。
```

**市价 · `zh-Hans`（示意）**：

```markdown
**永续合约 · 市价**

• **合约**　BTCUSDT · **开多**  
• **数量**　0.01 BTC · **杠杆**　10x · **仅减仓**　否  

市价成交受流动性影响，成交价可能与盘口略有偏离。

请核对后点击下方按钮。
```

**`en`（示意）**：**同窗** **字段** **英文化** **且** **单位与** [`design/api`](../../../../design/api.md) **登记表一致**。`inline_keyboard`：Confirm · Cancel（`zh-Hans` **同窗** **上文闪兑约定**）。

##### 永续 · 市价/限价 · 提交后 / 终局成功 / 部成 / 失败用户可见（非类型 A）

**同窗**：[`trade-via-agent`](../../../flows/trade-via-agent.md) **S5.1.1**；**§2.5.2 · 闪兑** **总则（MUST）** **与** **失败情境桶总表**；[`unknown-state`](../../../Runtime/unknown-state.md)。**市价** **语义对齐** **闪兑** **「委托受理 vs 成交终局」**；**限价** **对齐** **现货限价** **「已挂单 vs 部成 vs 全成」**。**本节补** **开平 / 合约域** **与** **合约增量失败桶**。

###### 阶段用词 · 标题与首句（MUST）

| **对内事实（示例）** | **标题须有之义（`zh-Hans` · 示意）** | **首句须澄清（示意）** |
|---------------------|--------------------------------------|-------------------------|
| **永续市价：已受理，撮合/终局未闭合** | **永续合约 · 市价 · 委托已受理** | **交易所已受理**；**正在撮合或待闭合**；**尚未** **等同「开/平仓已成交终局」**（**除非** **对内已采信终局**）。 |
| **永续市价：开/平仓成交终局已闭合** | **永续合约 · 开多已成交** **等**（**按开平替换**） | **本次开/平仓已在交易所成交**；本笔执行已收尾。 |
| **永续限价：已在簿未成交** | **永续合约 · 限价 · 委托已挂单** | **挂单已挂上**；**尚未成交**。 |
| **永续限价：部成** | **永续合约 · 限价 · 部分已成交** | **已有一部分成交**；**剩余仍在挂单**。 |
| **永续限价：全成终局** | **永续合约 · 限价 · 已全部成交** | **挂单已全部成交**；本笔已收尾。 |

**须**：标题或首屏 **带出可读「开多 / 开空 / 平多 / 平空」**（**禁止** **仅以英文 `LONG` / `SHORT` **枚举作主标签对用户呈现**）；`reduceOnly` **为 true** **时在成交类正文仍宜可见**。**数值单位（张 / 币）** **同窗** **§2.5.4** **元素表**。

###### 永续 · 增量失败 / 拒答情境桶（MUST：结论 + 怎么做）

**下列为合约** **增量** **桶；** **余额不足、精度、交易对不可用、`UNKNOWN`/504、确认超时等** **仍优先套用 §2.5.2 闪兑总表**。

| **情境桶（对内 · 勿给用户）** | **给用户的一句话结论（`zh-Hans` · 示意）** | **须包含的下一步（怎么做）** |
|------------------------------|---------------------------------------------|------------------------------|
| **保证金不足 / 可用保证金不够** | 这笔没能提交——**保证金不够用**，挡不住所需的持仓占用。 | 可先**减仓**、**充值**，或在对话里让我帮你改用**更小数量/更低杠杆**（**若链路支持**）再走确认。 |
| **杠杆超限或未先在链路内完成调杠杆** | 这笔没能提交——当前**杠杆或档位**不符合规则。 | 在对话里说你想用的**杠杆倍数**，若流程会先走调杠杆确认，**按提示一步一步确认**。 |
| **仅减仓（reduceOnly）与持仓不一致** | 这笔没能提交——**平仓数量超过你可平仓位**，或与「只减仓」规则冲突。 | 在对话里让我帮你**查当前持仓**，你再决定要平多少；或直接说更小的平仓数量重试。 |
| **持仓模式 / 保证金模式冲突（逐仓·全仓等）** | 这笔没能提交——**持仓或保证金模式**暂不支持这样下单。 | 可先在主站调整账户模式，或告诉我你只做的是「开仓」还是「平仓」，我再帮你对齐意图。 |

**规范性示意 · 市价委托已受理（`zh-Hans` · Markdown）**：

```markdown
**永续合约 · 市价 · 委托已受理**

交易所已受理你的市价委托；正在撮合或待闭合，尚未视同「开多已成交」终局。

• **合约**　BTCUSDT · **开多**  
• **数量**　0.01 BTC · **杠杆**　10x · **仅减仓**　否  
• **订单号**　`…`

成交均价与持仓变化以交易所回报为准。
```

##### 逻辑改单 · 类型 A 下限（`trade.futures.amend_limit_order`）

**流程 SSOT**：[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单**。**须** **同窗** **§2.5.2** **「逻辑改单」** **表** **之** **披露原则**（**原委托键**、**新参数全文**、**「先撤原单再挂新单」**、**新旧对比**、**「确认修改」类按钮**、**标题宜用「修改挂单」**），**域** **替换为** **合约**（**开平**、**张/币单位**、`reduceOnly`、**杠杆/保证金模式摘要** **等** **与** **上文永续限价表** **一致**）。

##### 永续限价 · 逻辑改单 · 规范性正文示例（`trade.futures.amend_limit_order`）

**`zh-Hans`（示意）**：

```markdown
**修改永续限价挂单**

将按「先撤销原单，再提交新单」处理。

• **原委托**　`orderId …5510` · BTCUSDT · 开多  
• **委托价**　65,000 → 64,500 USDT  
• **数量**　0.01 → 0.015 BTC  
• **仅减仓**　否 · **杠杆**　10x  

确认后系统将先撤掉原单，再挂新限价委托。
```

**`inline_keyboard`**：**确认修改** · **取消**（`en` **同窗**）。

##### 永续限价 · 逻辑改单 · 确认后体验（`trade.futures.amend_limit_order`）

**同窗** **§2.5.2 · 逻辑改单 · 确认后体验** **表**（**点按即时反馈 / 进行中 / 成功 / 撤败 / 撤成单败** **与** **`answerCallbackQuery`** **纪律**）；**§2.5.2 · 逻辑改单 · 确认后 · 总则（MUST）**、**规范性 fenced 示意**、**增量失败情境桶** **全文适用**，**仅须将示例中的「交易对 / 现货字段」** **替换为** **合约名、开平、张或币单位、`reduceOnly`、杠杆摘要**。**成功标题宜** **「修改永续限价挂单 · 新委托已挂上」** **类**，**禁止** **单独「已完成」** **不谈挂单状态**。

##### 止盈止损 / 条件委托 · 类型 A 卡面下限（`trade.futures.take_profit_stop` / `futures.condition.order_create`）

与 [`trade-via-agent`](../../../flows/trade-via-agent.md) **「合约止盈止损 · 分流」** **同窗**：**不覆盖** **`POST /fapi/v1/order`** **单笔链路第二～五步**；**须** **独立技能链** → **`POST /fapi/v1/conditionOrder`**（**矩阵 PATH 终裁**）。


| 元素           | 下限                                                                                                                           |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **版式**       | **「触发条件」区块** **须与「即时挂单」版式视觉分离**（[`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md) **§合约 · 条件单**）。 |
| **触发条件**     | **触发价 / 逻辑** **须在卡面最先可读区域之一**（**禁止** **藏在次要折叠感文案里冒充即时单**）。                                                                   |
| **触发后**      | **市价 / 限价** **离场语义** **可读**（与 `skill` **登记分型一致**）。                                                                       |
| **矩阵 PATH `TBD`（`conditionOrder` 未冻结）** | **`FR-T05` 透明拒答**，**禁止** **类型 A 已确认却无 API**。                                                  |


##### 止盈止损 / 条件委托 · 规范性正文示例（`trade.futures.take_profit_stop` / `futures.condition.order_create`）

**须** **「触发条件」** **块视觉置顶**（**§2.5.0a** **独立段**）。**矩阵 PATH `TBD` 时** **同窗** **上文 OCO · `FR-T05` 降级骨架** **改写语义**。

**`zh-Hans`（示意）**：

```markdown
**永续 · 条件委托**

**触发条件（请先阅读）**  
• 当标记价格 ≤ 60,000 USDT 时触发  

**触发后将提交的委托**  
• **类型**　市价减仓（示例）  
• **合约**　BTCUSDT · **数量**　0.01 BTC  

条件单与即时挂单不同；触发前不会在盘口展示为普通挂单。

请核对后点击下方按钮。
```

**`en`（示意）**：**同窗** **Trigger block first**, **Then triggered order**。`inline_keyboard`：**Confirm** · **Cancel**。

#### 2.5.5 理财与划转

**流程 SSOT**：[`wealth-via-agent.md`](../../../flows/wealth-via-agent.md)；**路由键摘录**：[`routing-engine.md`](../agent-orchestration/routing-engine.md) `wealth.holdings_read` / `wealth.recommend` / `wealth.subscribe` / `wealth.redeem`。**总则**：理财 **不得**套用现货限价/市价委托版式；**卡面须有** **产品业务线标题**、**金额或份额口径**、**SKU/产品编码可读摘要**（以 **`read_skill_operation_spec`** **当期条文为准**）、**期限/APR 或收益口径**（**若适用**）、**申购/赎回方向** **及** **独立风险须知段** — **皆须** **同窗** **§2.5.0a**。**矩阵未闭合** **或** **`WEALTH_ACTION_REQUIRES_WEB`** **→** **类型 B + 主站 Deeplink**；**禁止** **类型 A 冒充已写交易所** — **同窗** [`exchange-agent/boundaries.md`](../exchange-agent/boundaries.md) **§8.3**。

**现货 ↔ 全仓划转** **类型 A** **骨架** **见** **§2.5.3 · 划转**（**与** `trade-via-agent` **第四步 · 划转** **同窗**）。

##### 理财申购 · 类型 A 卡面下限（`wealth.subscribe`）


| 元素          | 下限                                                                                                              |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| **业务线**     | **理财 / 申购** **等** **一眼可区分于交易四轨**（[`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md)）。 |
| **产品与金额**   | **产品名或可读昵称 + SKU/编码摘要**；**申购金额或份额** **与用户意图一致**。                                                                |
| **期限与收益口径** | **活期/定期/锁仓** **可读**；**APR 或所内等价收益率** **若展示则须与只读目录一致**。                                                          |
| **资金出处**    | **从哪一类余额划出**（**现货/理财户等**）**若技能要求须可见**。                                                                          |
| **风险披露**    | **独立段**：**收益非承诺、提前赎回规则、费用口径** **等**；**须与 **`skill`** **模板一致**。                                                   |
| **禁止**      | **PATH**、**内部枚举裸漏**、**假装已成功成交**（**确认前**）。                                                                       |


##### 理财申购 · 规范性正文示例（`wealth.subscribe`）

**`zh-Hans`（示意）**：

```markdown
**理财 · 申购**

• **产品**　稳健活期 · `SKU-WLTH-001`（示例编码）  
• **币种**　USDT  
• **申购金额**　500 USDT  
• **期限**　活期 · **参考 APR**　≈ 4.5%（**非承诺收益**）  

收益与费用规则以产品页及交易所公示为准；赎回规则见持仓说明。

请核对后点击下方按钮确认申购。
```

**`en`（示意）**：**同窗** **字段英文化**。`inline_keyboard`：**Confirm** · **Cancel**（与 **§2.4** **同窗**）。

##### 理财赎回 · 类型 A 卡面下限（`wealth.redeem`）


| 元素        | 下限                                         |
| --------- | ------------------------------------------ |
| **业务线**   | **理财 / 赎回** **可读**。                        |
| **标的持仓**  | **哪一只产品/SKU**；**可赎份额或金额** **与用户表述一致**。     |
| **到账与费用** | **预计到账时间或规则摘要**（`skill` **模板为准**）。     |
| **风险披露**  | **独立段**：**惩罚性费率、锁定期未结束** **等** **若适用须明示**。 |


##### 理财赎回 · 规范性正文示例（`wealth.redeem`）

**`zh-Hans`（示意）**：

```markdown
**理财 · 赎回**

• **产品**　稳健活期 · `SKU-WLTH-001`  
• **赎回金额**　200 USDT（或全部可赎余额 — 以校验结果为准）  

到账时间与费用规则以产品说明为准。

请核对后点击下方按钮确认赎回。
```

**`en`（示意）**：**同窗**。`inline_keyboard`：**Confirm** · **Cancel**。

##### 推荐类前置卡片（`wealth.recommend` · 导向写）

**性质**：[`wealth-via-agent`](../../../flows/wealth-via-agent.md) · **S7** **探索推荐 / 对比 / 组合方案** **场景下**，**每张推荐卡前可有短文由 Agent 生成**；**卡片正文仍须** **单列理财模板**，**不得** **谎称用户已申购**。**用户选定 SKU 后** **下一屏** **须** **转入** `wealth.subscribe` **（或 `WEALTH_ACTION_REQUIRES_WEB`）** **之** **单独确认链路**。**`zh-Hans`（推荐条目 + 类型 A 预备 · 示意）**：

```markdown
**理财 · 推荐 · 稳健活期**

• **参考 APR**　≈ 4.5%（**非承诺**） · **期限**　活期  
• **起购**　10 USDT  

以下为预览摘要；确认申购须在下一步卡片中提交金额并再次确认。
```

（**组合方案** **多张卡** **金额预填** **须** **总额守恒** — **同窗 [`wealth-via-agent`](../../../flows/wealth-via-agent.md) · S7**。）

##### 主站回退（`WEALTH_ACTION_REQUIRES_WEB` · 多为类型 B）

**当** [`boundaries.md`](../exchange-agent/boundaries.md) §8.3 **强制 Web** **或** **矩阵无闭合写 PATH**：**发送** **短文说明 + 可点 Deeplink**（**类型 B**），**禁止** **含「确认即提交交易所写」之 `inline_keyboard` 冒充闭环。**

**`zh-Hans`（示意）**：

```markdown
**理财 · 需在 App/Web 完成**

该操作当前须在 **Coobit 主站**完成开通或签署（示例口径）。

请点击下方按钮前往官方页面继续；完成后可回到本会话查询持仓。
```

`inline_keyboard`：**打开官方页面**（**URL inline 或 Deeplink — `design` 冻结）· 取消。`en` **同窗**。

### 2.6 Bot API 硬约束（下限）

与 [`design/api.md`](../../../../design/api.md) **「Telegram Bot API」专节** **逐条对签**（含 **`callback_data` ≤64B**、`sendMessage`/caption **上限**、`answerCallbackQuery`、幂等与 **`pending confirm`** 分层）。

#### 2.6.1 Webhook 幂等 × 澄清 callback（MUST）

**SSOT 互引**：[`clarify-session` §1.1](../agent-orchestration/clarify-session.md) · [`persistence`](../../../Runtime/persistence.md) · [`locking`](../../../Runtime/locking.md) · **`eval.runtime.telegram_update_idempotent`**。

| **场景** | **MUST** |
|----------|----------|
| **同一 `update_id` 重复投递** | **须** **幂等**：**不** **二次** **`clarifyTurn` 递增**、**不** **重复出站**、**不** **二次** **`call_exchange_write`** / **计费成功** |
| **`callback_query` · `cl:*`** | **须** **校验** **`ClarifySessionSnapshot`**（**未 abandoned/未过期**；**stale 态** **仅允许** **`cl:resume`/`cl:new`** **或** **先走 §2.3 message 重意图**）— **非法/过期** → **§4.2 拒收** |
| **与类型 A 分层** | **`cl:*`** **0** **笔写**；**`cf:*`** **仅** **类型 A 存活路径** — **同窗** **`SC-CLARIFY-01`** |
| **观测** | **宜** **可 join** **`update_id`**（**或同窗幂等键**）**与** **`executionId`** **于** **Timeline** |

**验收**：**`eval.runtime.telegram_update_idempotent`** · **`eval.telegram.clarify_callback_merges_slots`** · **`eval.telegram.clarify_not_write_confirm`**。

---

**契约**：[`memory-runtime.md` §9](../../../Runtime/memory-runtime.md) **`FR-MEM*`/`SC-MEM*`**；**默认** **功能 OFF** — **本节** **仅在** **`semanticNarrativeEnabled=true`（或等价开关）** **且** **产品解冻后** **适用**。**非** **交易所写**；**不得** **使用** **类型 A「确认下单」** **版式** **冒充** **记忆操作**。

**卡片类型**：**类型 C**（只读摘要 + **可选** **二次确认键盘**）；**同窗** [`product/telegram-and-cards`](../../../../../product/telegram-and-cards.md) **类型 C**。**禁止**：REST PATH、`scenarioId`、`semanticNarrativeBlock` **等** **内部键名** **作主文案。

#### 2.7.1 触发（自然语言 · 示意）

Runtime **须** **识别** **下列意图簇**（**具体路由** **以** **`intents`/NLU MR** **为准**），**在** **Telegram** **内闭环** **完成** **查看或撤销** — **禁止** **默认** **导流** **独立 App**：

| **用户意图（示意）** | **动作** |
|----------------------|----------|
| 「你记得什么」「我的偏好」「查看记忆」 | **查看摘要**（§2.7.2） |
| 「清空记忆」「忘记我的偏好」「不再记住」 | **撤销流程**（§2.7.3） |
| 「关闭记忆功能」（若产品提供总开关入口） | **能力边界说明** + **运营/主站入口**（**仅** **`requires_main_site` 冻结时** **附 Deeplink**） |

**与交易分流**：**记忆查看/撤销** **不得** **隐式触发** **`call_exchange_write`** — **同窗** [`prompts/intents/analysis`](../../../prompts/intents/analysis.md) **与** **trade** **分流**。

#### 2.7.2 查看摘要（类型 C · MUST）

**须** **发送** **一条** **用户可读气泡**，**结构**（**自上而下 · 空行分段 · 同窗 §2.5.0a**）：

1. **短标题**（粗体）：如 **「对话记忆摘要」** / **Memory summary**  
2. **状态一句**：**已启用跨会话偏好** **或** **当前无已记住偏好**（**二选一** **须** **与** **Runtime 事实一致**）  
3. **条目列表**（**仅** **allowlist 内** — **同窗** **FR-MEM02**）：**每条** **一行** **人话**（**如** **关注：BTC-USDT**；**回复风格：简短**；**风险自述：偏保守**）  
4. **时效附注**（**若有** **`semanticNarrativeAsOf`**）：**「更新于 …（仅供参考）」** — **禁止** **编造** **延迟毫秒**  
5. **下一步**（**Telegram 内**）：**「若要清空，直接说 **清空记忆** **或点下方按钮。」**

**MUST NOT 出现在查看摘要中**：

- **余额、持仓、订单、最新价** **等** **须** **工具闭环** **之数值**（**即** **不得** **把** **Semantic** **块** **扩写为** **账户真值**）  
- **Secret、API Key、完整** **PII**  
- **内部** **`executionId`** **除非** **用户** **正在协查** **且** **单行附带**

**可选 `inline_keyboard`**（**非写确认**）：**清空记忆** · **知道了**（**或** **Close**）— **`callback_data`** **≤64B**，**载荷** **短 id**，**明细** **服务端解析**（**§2.6**）。

**`zh-Hans` 骨架（示意）**：

```text
**对话记忆摘要**

目前已记住的偏好（仅供参考）：
· 关注：BTC-USDT
· 回复风格：简短

更新于 2026-05-25 14:30（UTC）。

若要清空，直接说「清空记忆」，或点下方按钮。
```

**`en` 骨架（示意）**：

```text
**Memory summary**

Saved preferences (for reference only):
· Watchlist: BTC-USDT
· Reply style: brief

As of 2026-05-25 14:30 UTC.

To clear, say “forget my preferences” or tap below.
```

#### 2.7.3 撤销记忆（二次确认 · MUST）

**须** **两步** **在** **Telegram** **内完成**，**防止误触**：

1. **说明卡（类型 C）**：**将清除** **哪些层** — **至少** **L2 + Semantic 叙事块**（**同窗** **FR-MEM05**）；**明示** **不删除** **法定账单/审计留存**（**一句** **人话** **即可**）  
2. **确认键盘**：**确认清空** / **取消** — **禁止** **使用** **「确认下单」** **等** **交易动词**

**用户点「确认清空」或等效自然语言确认后**：

- Runtime **须** **写入** **`userMemoryRevokedAt`**（**或等价**）**并** **停止注入** **`semanticNarrativeBlock`**  
- **须** **回一条** **短确认**（**结论 + 下一步**）：**「已清空对话记忆；之后我会按新对话来。你可以继续在这里问价或查单。」**

**撤销后** **若** **用户问**「你还记得吗」→ **须** **如实** **说明** **已无** **跨会话偏好** **除非** **用户重新明示** — **同窗** **`SC-MEM04`**、**`eval.memory.semantic_user_revoke`**。

**`zh-Hans` 撤销确认卡（示意）**：

```text
**确认清空对话记忆？**

将清除：已记住的偏好与关注列表（如交易对、回复风格等）。
不会删除：账单与合规要求的留存记录。

清空后需你重新说明，我才会再次记住。
```

`inline_keyboard`：**确认清空** · **取消**

#### 2.7.4 功能未启用 / 无摘要

| **状态** | **对用户 Then** |
|----------|-----------------|
| **开关 OFF** | **短句**：**当前未启用跨会话记忆**；**下一步** **仍在对话内**（**可继续询价/查单**）— **禁止** **假称** **「我已记住你」** |
| **开关 ON 但无块** | **「目前还没有已记住的偏好。」** + **如何添加**（**如** **「你可以说：以后默认只看 BTC」**） |

#### 2.7.5 Prompt 互引

- **话术锚**：[`prompts/shared/common-phrases` §6](../../../prompts/shared/common-phrases.md)  
- **用户问题解决面**：[`response-format` §1](../../../prompts/shared/response-format.md) — **查看/撤销** **均** **在** **本对话完成**  
- **观测**：记忆查看/撤销 **须** **可关联** **`userId`/`sessionId`**（**不必** **向用户展示**）— **同窗** **FR-MEM07**

### 2.8 清空本会话（STM · 与 §2.7 分流）

**契约**：[`memory-runtime` §13](../../../Runtime/memory-runtime.md) **`FR-STM*`/`SC-STM*`**。**与** **§2.7 跨会话记忆** **MUST NOT** **混为** **同一意图或同一按钮**。

**卡片类型**：**类型 C**（**说明 + 可选** **一次确认**）；**非** **类型 A** **交易确认**。

#### 2.8.1 触发（自然语言 · 示意）

| **用户意图（示意）** | **动作** |
|----------------------|----------|
| 「重新开始」「新话题」「清空本次对话」 | **STM 清空**（§2.8.2） |
| 「清空记忆」「忘记偏好」 | **LTM 撤销** — **§2.7.3**（**非本节**） |

**NLU SSOT**：[`prompts/intents/analysis` §6](../../../prompts/intents/analysis.md)。

#### 2.8.2 清空本会话（MUST）

1. **说明**（**可** **与** **确认** **合并为** **一条**）：**将清除** **本会话内** **刚才聊的内容**；**不会** **删除** **已记住的跨会话偏好**（**若 LTM 已启用**）；**若有** **未确认下单/操作** **将一并放弃** — **同窗** **FR-STM03**  
2. **用户确认后**（**自然语言「好」/ 按钮**）：**执行** **L0 + 活跃 L1 清空**（**§13**）  
3. **短确认**：**「好的，我们重新开始。你可以直接说想查什么。」** — **禁止** **假称** **已删除** **跨会话偏好** **除非** **用户** **走了** **§2.7.3**

**`zh-Hans` 示意**：

```text
**重新开始？**

将清除本会话里刚才聊的内容；不会删除已记住的偏好（如有）。
若有未确认的操作，也会一并取消。

回复「好」或点下方按钮继续。
```

`inline_keyboard`（**可选**）：**重新开始** · **取消**

#### 2.8.3 验收互引

| ID | 要点 |
|----|------|
| **`SC-CH-TG-STM-01`** | **STM 清空后** **不** **再引用** **旧轮**；**LTM 摘要** **仍可查看**（**开关 ON**） |
| **`SC-CH-TG-STM-02`** | **与** **§2.7.3** **分流** — **「清空记忆」** **不得** **仅清 STM** |

**Eval**：**`eval.memory.session_clear_stm`**。

#### 2.8.4 常驻入口 · 「新话题」（MUST · 补偿无线程 UI）

**问题**：Telegram **无** **操作级「开新话题」**；**仅依赖 NLU** **识别** **「重新开始」** **不足**。

**须** **至少一种** **非类型 A** **常驻入口**（**同窗** [`memory-runtime` §14.5](../../../Runtime/memory-runtime.md) · **`design` MR 冻结**）：

| **形态（示例）** | **行为** |
|------------------|----------|
| **BotCommand** **`/new`** **或** **`/restart`** | **触发** **§2.8.2** **STM 清空流程**（**可** **跳过二次确认** **若** **无** **pending 写** — **`design` 终裁**） |
| **ReplyKeyboard / Bot Menu** **「新话题」** | **同上** |
| **首条欢迎/长时间未聊后** | **宜附** **「新话题」** **快捷钮** — **非** **交易确认动词** |

**与 §2.7 分流**：**「新话题」** **仅** **STM（§2.8）**；**「清空记忆」** **仅** **LTM（§2.7.3）** — **禁止** **同一按钮混两种删除**。

**隔较久回来**：**同窗** **§14.6** — **主路径** **默认 stale**（**退出活跃写 L1**）；**`cl:resume`/`cl:new`** **仅** **fallback**（**`STM_IDLE_DEFAULT_POLICY=prompt_resume_or_new`** · OpenAPI **`ClarifyCallbackData`**）。

#### 2.8.6 空闲后 · 非阻塞提示（宜）

**适用**：**空闲 ≥ `STM_IDLE_RESUME_PROMPT_SEC`** **且** **写路径已 stale**。

**宜** **一条短句**（**L 润色 · 非类型 A**），例如：「距上次较久，已按新对话处理；若要接着上一笔，可直接说『继续买 BNB』。」

**禁止**：**强制等待** **续/新二选一** **才继续对话** — **须** **仍接受** **任意 inbound** **走 §2.3**。

**Eval**：**`SC-STM12`** · **`eval.memory.idle_default_stale`**。

#### 2.8.5 验收互引（增补）

| ID | 要点 |
|----|------|
| **`SC-CH-TG-STM-03`** | **存在** **`/new` 或等价常驻入口**；**触发后** **FR-STM01** **可观测** |
| **`SC-CH-TG-STM-04`** | **空闲超过阈值** → **默认 stale + §2.3 重意图**；**模糊 inbound 默认 new** — **§14.6**（**非强制续/新卡**） |

---

- `executionId`、`agent.tool.call`、频道投递失败等见 [`observability/overview.md`](../../../observability/overview.md) **§2**。  
- **504 / UNKNOWN** 与用户话术见 [`exchange-agent/boundaries.md`](../exchange-agent/boundaries.md)、[`unknown-state`](../../../Runtime/unknown-state.md) **「用户可见副本下限」**。

### 3.1 用户可见「执行阶段」副本下限（对齐 `execution.md` 附录 A）

**用途**：**长链路** **S2～S10** **任一点** **用户** **须** **大致** **知道** **卡在哪**；**非** **技术枚举** **照搬** — **文案** **可温和** **但** **不得** **误导终局**。


| **附录 A 主态（摘要）**            | **对用户副本 Then（下限）**                                                                                                                                                                                                                                                            |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `waiting_confirmation` | **明示** **待用户** **确认** **（** **类型 A** **）**；**禁止** **暗示已下单**。                                                                                                                                                                                                                  |
| `executing`（含在途/部成子态） | **区分** **「已送交易所/撮合中」** **与** **「已达成功终局」**；**宜** **订单摘要** **可核对** — **同窗** [`trade-via-agent.md`](../../../flows/trade-via-agent.md) **S5.1.1**。                                                                                                                               |
| `settling`             | **终局或计费在途**；**在无产品与 billing 域单列对齐前**，**禁止** **与 **`completed`** **的成功措辞混用**。                                                                                                                                                                                             |
| `unknown_pending`      | **同** [`unknown-state.md`](../../../Runtime/unknown-state.md) **「用户可见副本下限」**；**禁止** **成交断言**。                                                                                                                                                                                 |
| **卡点（`FR-T05`）**           | **对用户** **须** **自然语言归因 + 明确下一步**（**改参重试 / 充值或换额 / 主站入口 / 稍后查单**）；**禁止** **照搬 HTTP 状态码、上游 `code`/`msg`、`stableReason`/`AGENT_*` 等内部字面** — **同窗** [`response-format`](../../../prompts/shared/response-format.md) **§2**。**内部** **`FR-T05`** **分桶与观测不变**。协查时宜在单行附上 **`executionId`**，勿与错误码并列堆砌。 |


**运营/审计**：**`FR-MC801`** 时间线 **须** **可与** **上述阶段叙事** **交叉验证**（[`observability-management/functions.md`](../../admin/observability-management/functions.md)、**`SC-OM-04`**）。

---

## 4. 运营配置（Bot）

**功能项 SSOT**：[`admin-bot-config.md`](admin-bot-config.md)（**FR-TG-ADMIN-01～06**、**SC-TG-ADMIN-***）；**`configKey` 枚举** 与 **模块七** [`keys.md` §4](../../admin/trading-agent-config/keys.md) **同窗**。

---

## 5. 验收（节选）


| 编号                     | 说明                                                                                                                                                                                                                                                                                                                                                                                                             |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SC-CH-TG-08**        | **`callback_data` 越界 / 非法** **时**：**不得** **静默丢单**；须 **可观测** **拒绝路径**（与 **`design/api`** **专节** **同窗单测**）                                                                                                                                                                                                                                                                                                                         |
| **SC-CH-TG-09**        | **用户 `message` inbound** **后**：**≤300ms** **内** **须** **观测到** **`sendChatAction(typing)`** **（或等价）** **或** **≤1s** **内** **首条可读回复**（早失败）；**>5s** **无终态** **须** **续发 typing** **或** **进度短句** — **§2.3.1**                                                                                                                                                                                                                                                                                  |
| **SC-CH-TG-10**        | **写路径澄清 · 二选一**（**如** **闪兑/限价**）：**须** **`inline_keyboard`** **同窗语**；**`callback_data` ≤64B**；**禁止** **仅** **开放题** — **§2.3.2** · **`clarify-user-visible` §7.1**                                                                                                                                                                                                                                                                                                                          |
| **SC-CH-TG-11**        | **澄清 `cl:*` 点按**：**须** **`answerCallbackQuery` → 合并 `resolvedSlotsSoFar` → 重跑 Resolver**；**禁止** **写确认动词** **与** **直接写** — **§2.3.3** · [`clarify-session` §4.2](../agent-orchestration/clarify-session.md)                                                                                                                                                                                                                                                                                              |
| **SC-CLARIFY-05**      | **澄清态** **每条 **`message` inbound** **须** **重跑意图**；**outbound** **须** **承接 inbound** — **§2.3.4** · [`clarify-session` §2.3](../agent-orchestration/clarify-session.md)                                                                                                                                                                                                                                                                                                                                    |
| **SC-CLARIFY-06**      | **放弃话术** → **`abandoned`**；**不得** **再发** **写澄清** **或** **复读同句** — **§2.3.4** · [`clarify-session` §2.1.1](../agent-orchestration/clarify-session.md)                                                                                                                                                                                                                                                                                                                                                    |
| **SC-CLARIFY-07**      | **澄清中** **只读/寒暄** → **须** **分流应答**；**写 session abandoned** — **§2.3.4**                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **SC-CLARIFY-08**      | **连续两轮** **outbound** **不得** **逐字相同**（**不同 inbound**） — **§2.3.4**                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **SC-CLARIFY-09**      | **出站** **不得** **含** **`routingHints`/编排/Prompt 条文** **原文** — **§2.3.4** · [`clarify-user-visible` §1](../../../prompts/shared/clarify-user-visible.md)                                                                                                                                                                                                                                                                                                                                                          |
| **SC-CH-TG-FMT-01**    | **类型 A** **正文** **须** **遵守** **§2.5.0a**：**分段留白**、**短粗体标题**、**禁止整块 monospace 堆砌决策参数**、**风险披露独立段**、**核对语不误导步骤数**；`parse_mode` **渲染失败** **须** **可观测降级纯文本**                                                                                                                                                                                                                                                     |
| **SC-CH-TG-SPOT-01**   | **`trade.spot.flash_convert`** **类型 A**：卡面满足 **§2.5.2 · 闪兑** **必选元素**，且 **明示市价 / 闪兑语义**（**禁止** **无限价的限价单冒充**）；**卡面不得冒充 **`margin.cross.*`**。**版式** **同窗** **§2.5.0a** **及** **§2.5.2 · 闪兑 · 规范性正文示例**                                                                                                                                                                                                    |
| **SC-CH-TG-SPOT-02**   | **`trade.spot.limit_order`** **类型 A**：满足 **§2.5.2 · 限价** **摘要表** **及** [`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 现货限价** **列表**；**缺少委托价 / 数量口径 / 必选 **`timeInForce`** **时** → **不得发写**                                                                                                                                                                                                               |
| **SC-CH-TG-SPOT-03**   | `trade.spot.oco` / `trade.spot.bracket`：`design/api` 矩阵 PATH `TBD` **时** **类型 A** **不得承诺双挂/bracket 闭环**；须 `FR-T05` **可测降级** — **同窗** `trade-via-agent` **专节交界**                                                                                                                                                                                                                                |
| **SC-CH-TG-SPOT-04** | `trade.spot.flash_convert` **提交后气泡**：须区分委托已受理（撮合中）与买入/卖出已成交（终局）；禁止含糊「已完成」；失败须结论 + 可执行下一步；禁止对用户暴露 HTTP 状态、`code`/`msg`、内部拒码头 — 同窗 §2.5.2 · 闪兑 · 提交后/终局/失败 与 §3.1 |
| **SC-CH-TG-SPOT-05** | `trade.spot.limit_order` **提交后气泡**：须区分委托已挂单（未成交）、部分成交（剩余在簿）、已全部成交（终局）及 IOC/FOK 即时单语义；禁止仅用「已完成」；失败情境同窗 §2.5.2 闪兑总表并叠加 §2.5.2 · 限价 · 增量桶 |
| **SC-CH-TG-SPOT-06** | `trade.spot.amend_limit_order` **确认后气泡**：须同窗 §2.5.2 · 逻辑改单 · 确认后体验表及 fenced 示意（进行中/成功/撤败/撤成单败）；成功标题须避免含糊「已完成」；禁止对用户裸露错误码 |
| **SC-CH-TG-MARGIN-01** | `margin.cross.market_order` / `margin.cross.limit_order`：**须** **两次类型 A（或等价二次确认）** **后方** **可** **提交杠杆下单写** — **同窗** **§2.5.3** **与** `trade-via-agent` **第七步**                                                                                                                                                                                                                                        |
| **SC-CH-TG-MARGIN-02** | **全仓杠杆类型 A**：卡面满足 **§2.5.3** **必选元素**，**明示 cross / 借还语义**，**禁止** **与现货闪兑版式混淆**；**限价单** **缺委托价** → **不得发写** |
| **SC-CH-TG-MARGIN-03** | `margin.cross.*` **第二张确认触发写之后**：须区分市价委托已受理与借买/借卖成交终局；限价须区分已挂单、部成、全成；失败同窗 §2.5.2 闪兑总表并叠加 §2.5.3 · 全仓增量桶；划转提交后同窗 §2.5.3 · 划转一句 |
| **SC-CH-TG-FUT-01**    | `trade.futures.market_order` / `trade.futures.limit_order` **类型 A**：满足 **§2.5.4 · 永续市价/限价** **摘要表** **及** [`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 第六步**；**缺方向·开平·数量单位·限价价（限价）·`reduceOnly` 可见性（若 true）** → **不得发写**                                                                                                                                                                  |
| **SC-CH-TG-FUT-02**    | **`take_profit_stop`** / **`condition.order_create`**：**触发条件区块独立版式**（**§2.5.4 · 止盈止损/条件**）；**矩阵 **`conditionOrder`** PATH **`TBD`** **时** **不得假闭环**                                                                                                                                                                                                                                                                                 |
| **SC-CH-TG-FUT-03** | **合约第三步歧义未消**：**不得** **下发类型 A**（**同窗** `trade-via-agent` **专节 · 第三步**） |
| **SC-CH-TG-FUT-04** | `trade.futures.market_order` / `trade.futures.limit_order` **提交后气泡**：市价须区分委托已受理与开/平仓成交终局；限价须区分已挂单、部成、全成；须可读开平与张/币单位、`reduceOnly`（若为 true）；失败同窗 §2.5.2 闪兑总表并叠加 §2.5.4 · 永续 · 增量桶；禁止对用户裸露错误码 |
| **SC-CH-TG-FUT-05** | `trade.futures.amend_limit_order` **确认后气泡**：同窗 **SC-CH-TG-SPOT-06** 口径；示例字段须为合约开平、张/币、`reduceOnly`、杠杆 |
| **SC-CH-TG-WLTH-01**   | **`wealth.subscribe`** / **`wealth.redeem`** **类型 A**：满足 **§2.5.5** **元素表** **及** [`wealth-via-agent`](../../../flows/wealth-via-agent.md) **S8** **之前确认链路**；**版式** **同窗** **§2.5.0a** **及** **§2.5.5 · 规范性正文示例**；**当 **`WEALTH_ACTION_REQUIRES_WEB`** **时**：**不得** **用类型 A 假冒闭环写** — **须** **§2.5.5 · 主站回退（类型 B）** **或** **`FR-T05`** — **同窗** [`exchange-agent/boundaries.md`](../exchange-agent/boundaries.md) **§8.3** |
| **SC-CH-TG-MEM-01**    | **跨会话记忆开关 ON** · **用户触发查看**：**须** **§2.7.2** **结构**（**标题/状态/allowlist 条目/下一步**）；**禁止** **余额持仓订单价** **与** **内部键字面** — **同窗** **`SC-MEM02`** |
| **SC-CH-TG-MEM-02**    | **用户触发撤销**：**须** **§2.7.3** **说明卡 + 二次确认键盘**（**非类型 A 交易动词**）；**确认后** **短确认** **且** **下一回合不注入已清块** — **同窗** **`SC-MEM04`**、**`eval.memory.semantic_user_revoke`** |
| **SC-CH-TG-MEM-03**    | **开关 OFF 或空块**：**须** **§2.7.4** **口径**；**禁止** **假称跨会话记忆已启用** — **同窗** **`SC-MEM01`** |
| **SC-CH-TG-STM-01**    | **用户「重新开始」**：**须** **§2.8.2**；**下一回合不引用旧轮**；**LTM ON 时偏好仍可查看** — **同窗** **`SC-STM01`/`SC-STM02`** |
| **SC-CH-TG-STM-02**    | **「清空记忆」** **须** **走** **§2.7.3** **而非** **仅** **§2.8** — **同窗** **`SC-STM02`** |
| **SC-TG-ADMIN-01～05**  | 见 [`admin-bot-config.md`](admin-bot-config.md) **§4**（含 **Webhook · SC-TG-ADMIN-04**、**开通欢迎语 · SC-TG-ADMIN-05**）                                                                                                                                                                                                                                                                                               |


---

## 6. 自检（用起来）

重大改动后对照 [`interaction-flow-standard.md`](../../../standards/interaction-flow-standard.md) **§8**；**新增 **`configKey` **或运营 API** 时**，须在同窗 MR 中补齐 **`keys`**、产品附录 A §5.1（若有）、[`design/api`](../../../../design/api.md) **登记表**。

---

## 7. 需求自检与已知缺口（维护）


| 主题 | 状态 | 说明 |
| --- | --- | --- |
| **§2.5.x 与 flows** | **§2.5.2～§2.5.5 已摘要 + 示例骨架** | **现货 · 全仓 · 永续 · 理财**卡面元素与 fenced 示例以本节为索引；字段级 `read_skill` 细则与 [`wealth-via-agent`](../../../flows/wealth-via-agent.md)、[`trade-via-agent`](../../../flows/trade-via-agent.md) 步骤叙事仍以 flows 终裁。冲突须在同窗 MR 中消除。 |
| **§2.4 / `effective_locale`** | **首版已定优先级** | **显式语种指令**优于本条 inbound 推断（≥ **design** 冻结置信阈值，同窗 §2.4）；不满足则用 §2.1.1 基线桶。**三桶外**语种回落 **`TELEGRAM_DEFAULT_LOCALE`**（**design** 终裁）。阈值、选型与 `effective_locale` 注入以 **design**/OpenAPI 冻结为准，同窗 [`runtime-injection`](../../admin/prompt-management/runtime-injection.md)。 |
| **频道侧 SC 矩阵** | **节选** | 本文 §5 含 `SC-CH-TG-FMT-01`、`SC-CH-TG-SPOT-01～06`、`SC-CH-TG-MARGIN-01～03`、`SC-CH-TG-FUT-01～05`、`SC-CH-TG-WLTH-01`、**`SC-CH-TG-MEM-01～03`**、**`SC-CH-TG-STM-01～02`**、`SC-CH-TG-08`、`SC-TG-ADMIN-*`（节选）；全量频道 Given/When/Then 宜随实现合并扩写或归入 `telegram-binding` `TG-GWT-*`。 |
| **类型 A 正文示例 / 格式** | **已定（主干齐全）** | §2.5.0a 设计规格；§2.5.2～§2.5.5 已与 §2.5.0 表 `scenarioId` 族对齐之 fenced 骨架；监控告警（类型 D）等仍可按 §2.5.0a 类推或单列 MR。 |
| **用户侧 HTTP PATH** | **`design`/OpenAPI** | Inbound webhook / BFF PATH 不以 `requirements` 正文冻结 — 见 [`design/api`](../../../../design/api.md) 登记表与 [`integrations/telegram/webhook.md`](../../../integrations/telegram/webhook.md)。 |
| **跨会话记忆 UX** | **§2.7～§2.8 已定（LTM 解冻前 TBD）** | **LTM 查看/撤销** **§2.7**；**STM 清空** **§2.8**；**依赖** **`FEATURE_SEMANTIC_NARRATIVE` 默认 OFF**、**[`memory-runtime` §9～§13](../../../Runtime/memory-runtime.md)**。 |
| **Mini App / Payments** | **非目标** | 原生 TG Payments、Mini App 深度集成未在本版 FR 正式立项 — 与 [`mobile-app.md`](mobile-app.md) 暂缓同窗。 |
| **`telegram.md` 文件名** | **历史别名** | **design/api** 偶见以 `telegram.md` 指代本文；以仓库路径 `overview.md` 为准。 |

---

**文档版本**：0.6.6 · **维护**：产品 + Channels owner · **本版**：**§2.6.1 Webhook 幂等 × clarify callback**。**承** 0.6.5。
