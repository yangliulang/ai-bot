# Telegram 体验与卡片（人类阅读）

本版唯一会话渠道是 **Telegram**。这里用自然语言说清楚 **卡片**是什么、何时出现、用户要点什么；**段落号、必选能力编号、验收 ID** 仍以 **[telegram/overview §2.5 · 类型 A、§2～§2.6](../specs/requirements/domains/agent/telegram/overview.md)** 为准。**你用什么语言问，Bot 就应尽量用什么语言回答**——细则见 **[telegram/overview §2.4](../specs/requirements/domains/agent/telegram/overview.md)**（**`effective_locale`**：简繁英三桶；**`inline_keyboard` 字面与正文同语）。

## 为什么是「卡片」

在 Telegram 里，我们用 **一条结构化的气泡 + 底部按钮区**（实现上常用 `inline_keyboard`）来承载 **摘要 + 操作**。以后如果有 App，同一套语义应能映射成真正的卡片组件；现在不必纠结像素级稿，但要保证 **一眼能认出：这是要你确认的一笔交易，还是能点的链接**。

## 四条卡片类型（从用户视角）

1. **写操作确认（类型 A）**
  **在每一笔会改交易所状态的写请求发出之前** 出现。**你必须能点「确认」或「取消」**。**取消 = 绝对没有这笔交易所写**。  
   **禁止**：模型只在聊天里用文字说「下单成功」而事实上没经过你的确认按键。
2. **被拦住后的引导（类型 B）**
  例如子账户/API 未就绪。**重点是可以点的链接**跳到主站或 H5，而不是一行复制不了的长 URL。
3. **只读信息（类型 C）**
  例如近期扣费摘要、帮助。**不要求**你为「执行委托」做任何确认；最多给「去看完整流水」的按钮。
4. **通知（类型 D）**
  条件触发、到期、风险阈值等。**可以只是提醒**；若需要你再操作，会附带 **链接**。注意：**创建条件单这类写操作**，发 API 之前仍要再走 **类型 A**，不是光有通知就够。

## 写路径澄清键盘（≠ 类型 A）

**缺参或路由未定时**（如「买入 BNB」但还没选闪兑/限价），Bot 会发 **澄清键盘**（**`cl:*` 短键** · 如 **闪兑/限价/买入/卖出**）— **这是补槽与路由，不是授权下单**。**澄清钮** **不得** 使用 **「确认下单」** 类动词；**点澄清钮** **不会** 触发交易所写。

**跨轮**：同一条写路径 **沿用 **`executionId`** **并记住已选槽位** — [`clarify-session`](../specs/requirements/domains/agent/agent-orchestration/clarify-session.md)。**隔较久回来**：系统 **默认按新对话处理**（**stale**），**不会** 盲复读旧澄清；若要接着上一笔，**直接说**「继续买 BNB」等 — [`memory-runtime` §14.6](../specs/requirements/Runtime/memory-runtime.md)。**用户说「你好」「都不要了」** 等 → **须** **寒暄或放弃**，**不得** **再闪兑/限价盘问**。

**话术 SSOT**：[`clarify-user-visible`](../specs/requirements/prompts/shared/clarify-user-visible.md) · **Telegram 键盘** [`telegram/overview` §2.3](../specs/requirements/domains/agent/telegram/overview.md)。

## 开通完成后的一条欢迎语

在你 **走完 Agent 开通**并且 **Telegram 已与账户绑定**之后，Bot **可以**（由运营配置）自动给你发 **一条欢迎消息**（普通气泡正文，**不是**上面的「卡片类型」框架）。运营在后台 **分语言** 维护 **简体中文、繁体中文、英文** 三套模板（配置键见 [**keys** §4.2](../specs/requirements/domains/admin/trading-agent-config/keys.md)）；**运行时**结合你的语言偏好与 Telegram 客户端 `language_code` 等做 **locale 解析**，再按 **回退链** 选中一条非空正文，细则见 [**telegram/overview** §2.1.1 · §2～§2.6](../specs/requirements/domains/agent/telegram/overview.md)。若解析与回退后仍无正文，则不发送。相关验收见 [**FR-TG-ADMIN-06**](../specs/requirements/domains/agent/telegram/admin-bot-config.md)；**每条用户通常只发一次**（幂等），避免骚扰。

## 每笔交易都必须你同意

产品上我们压一条铁律：**任何交易所侧「写」，在到达你的账户前，都必须经过你明确授权的一次确认**（类型 A）。  
**独立意图**（**只下一笔单、只撤一单、只划一笔账**）= **一次确认绑定一笔 payload**。  
**逻辑改单**（**无交易所原生「改单」接口时**，系统在后台 **先撤掉旧挂单、再挂新挂单**）在用户看来仍是 **一件事**；**允许一张类型 A** 授权 **顺序两笔交易所写**，但卡面上 **必须** 写清「会先撤销再重挂」，且 **实现上** **两笔写都只能发生在** 你 **点过确认** **之后** — **详见** **[telegram/overview** §2.5.2 / §2.5.4 · 逻辑改单](../specs/requirements/domains/agent/telegram/overview.md)、**[trade-via-agent** 专节 · 逻辑改单](../specs/requirements/flows/trade-via-agent.md)、**[ADR-001** §5](../specs/design/adr/001-telegram-confirm-before-coobit-write.md)。**禁止**：**一张含糊卡片** **不说明两阶段** **却悄悄执行撤单+下单**；**禁止** **在** **你** **未点确认** **前** **发起任一对交易所写**。

若在实现里把 **彼此独立** 的多笔写 **拆成多次 API 调用**（**如下单与撤单无关、或** **改杠杆与下单分属不同用户决策**），则 **要么** **多张确认卡按顺序来**，**要么** **一步只绑定一笔 payload** — 总之 **不能** **一包多意图却无感执行**。**单笔限额、单日限额** 仍然会 **先于**弹出确认卡住；超限是 **拒绝**，不是你「确认了就能硬过」。

## 场景一页表（对齐 §2.5.0）

字段级下限与同窗 flows 仍以 **[telegram/overview §2.5 · 类型 A～§2.6](../specs/requirements/domains/agent/telegram/overview.md)** 为准（见该篇 **§2.5.0 场景索引表**）；这里用白话说明 **从上到下该长什么样**：实现上始终是 **结构化气泡正文 + `inline_keyboard`**。

| **场景（你的话术）** | **类型 · 版式从上到下** |
|---------------------|--------------------------|
| **现货闪兑 / 市价即刻** | **A** · 一眼 **闪兑/市价（非限价）** → **交易对与方向** → **按 base 数量或 quote 金额（单位写死）** → **流动性或滑点一句** → **`确认` / `取消`** |
| **现货限价挂单** | **A** · **限价 + 明码委托价** → **`timeInForce`（要让人看懂）** → **数量口径** · **若走偏离带第二张卡须有「建议价已调整」体感** → **确认 / 取消** |
| **限价在途 · 逻辑改单** | **A** · **`修改挂单` 语感** · **旧↔新对比** · **白话「先撤再挂」** · **「确认修改」/取消** · **点后分阶段话术** 见 **[logical-amend-copy](telegram-logical-amend-copy.md)** |
| **OCO / bracket** | **常为 A**；**矩阵 `TBD` 时只可拒答/Web，不可用假「确认下单」诱骗** |
| **全仓市价 / 限价** | **类型 A · 链路双卡** · **每笔都写明全仓杠杆** · **借还、计息、风险档位** · **第二张卡同样需要「确认/取消」** · **两卡链路都通过后**才可调交易所写 |
| **现货↔全仓 · 单笔划转** | **独立 · A** · **币种+数额+方向（如现货→全仓）** · **每笔一张** |
| **永续市价 / 限价** | **类型 A** · **开/平、多/空人话** · **张或币二选一（与撮合所一致）** · **杠杆/保证金、`reduceOnly` 可见** · **市价：滑点/流动性；限价：不保证成交一句** · **底部「确认」「取消」** |
| **永续 · 逻辑改单** | **A** · **同上「限价改单」版式**，字段替换为永续域 |
| **止盈止损 / 条件委托** | **A** · **单独的「触发条件」首屏语义块**，**不得伪装成即时限价** · **触发后走哪类单写清** |
| **理财申购赎回等** | **类型 A**，**或 Deeplink/Web 引导（同窗 **[wealth-via-agent](../specs/requirements/flows/wealth-via-agent.md)** 与 **`WEALTH_ACTION_REQUIRES_WEB`）——读来像理财产品说明，不得照搬内部 API 代号作主文案** |
| **子账户未就绪 · 阻断** | **类型 B** · **归因短** + **可点链接** |
| **流水/help 只读** | **类型 C** · **不出现「这笔委托确认」键盘** · 可有跳转 |
| **自动化提醒 / Push** | **多为类型 D**；**随后若还有一次真实交易所写，必须另行一条类型 A** |

自检顺序与控件纪律：**[interaction-flow-standard §8](../specs/requirements/standards/interaction-flow-standard.md)**、**telegram/overview §2.6 · Bot API**。

## 不同市场、不同订单，卡片上要「长得像那种单」

用户要能 **从卡片版式和内容上一眼分辨**：这是现货还是合约、限价还是市价、普通挂单还是触发后才下单的条件单。**具体字段下限**在产品与渠道 specs 里写成了表格（**[telegram/overview** §2.5](../specs/requirements/domains/agent/telegram/overview.md)），下面用人话归纳差异。

### 币币（现货）

产品与编排上：**用户侧的「市价 / 即时撮合、无委托价」不算第二条与闪兑并列的主线——统一走闪兑，`scenarioId`** 落在 `**trade.spot.flash_convert**` 一等族；限价挂单另走 `**trade.spot.limit_order**` 路径。**下文「市价」**仍指 **卡片上要露出的市价语义与字段下限**（与渠道 specs 对齐），不改变上述路由。**权威条文**：**[trade-via-agent**（开篇四轨、分流与专节）](../specs/requirements/flows/trade-via-agent.md)、**[telegram/overview** §2.5.2 段首](../specs/requirements/domains/agent/telegram/overview.md)。

- **限价**：要有 **明确的委托价**、**数量或金额口径（单位写清）**，以及需要时间策略时要把 **有效期类型**摆上卡面。  
- **市价**：要写明 **市价**，以及按 **币数量** 还是 **按报价币金额** 成交；给一句 **流动性/滑点** 类提示。不能做成「看起来像限价」却没有价。**需求 SSOT · 正文格式与闪兑示例骨架**：[`telegram/overview` §2.5.0a～§2.5.2（闪兑 · 规范性正文示例）](../specs/requirements/domains/agent/telegram/overview.md)。
- **止盈 / 止损类**：**触发价**要单独一行，和 **真正挂出去的限价** 区分开；若是「触发后走市价」，标题或首屏要说清。  
- **条件 / 计划委托（现货）**：**触发条件**要放在 **最显眼的位置**，下面再写触发后要下的是限价还是市价。**若交易所 API 还没对 Agent 冻结现货条件单路径**，则从体验上 **要么** 直接说明「Agent 暂不能挂这类单」并给主站入口，**要么** 拆成只挂普通限价等 **能力边界内** 路径 — **禁止**「确认了却调不了 API」的假象。**依据**：**[design/api** 子账户矩阵](../specs/design/api.md)（现货侧「计划/条件委托」**TBD**）、**[exchange-agent/overview** §5](../specs/requirements/domains/agent/exchange-agent/overview.md)（旧 §10.x → 分卷映射）、**[automation-alerts](../specs/requirements/flows/automation-alerts.md)**。

### 修改在途挂单（逻辑改单 · 人类可读）

当用户要 **改价 / 改量** **而系统只能「撤单 + 重新挂单」** 时：**一张确认卡** 代表 **你授权这一次整体操作**；卡上要让用户 **一眼看到「旧 → 新」对比**（**至少** 价、量），并有一句 **大白话** 说明 **会先撤掉旧单再挂新单**（**不要**假装交易所有一键「改单」若实际是两步 API）。**点确认之后**：客户端 **应尽快结束按钮转圈**（`answerCallbackQuery`），再用 **后续消息** 告知 **「正在处理撤单…」→「正在提交新委托…」→ 成功或失败**，避免 **长时间无反馈**。**若旧单已撤但新单失败**：回复里 **须诚实** — 例如说明「原挂单已撤销，新委托未挂上」，并给出 **下一步**（**在对话里重试 / 打开主站当前委托** **等**），**禁止** **说成「已改单成功」**。**细则与字段下限**：**[telegram/overview** §2.5.2 / §2.5.4 · 逻辑改单](../specs/requirements/domains/agent/telegram/overview.md)、**[trade-via-agent** 专节 · 逻辑改单](../specs/requirements/flows/trade-via-agent.md)。**i18n 模板（简中 + English）**：[telegram-logical-amend-copy.md](telegram-logical-amend-copy.md)。

### 杠杆

在 **和现货同一类订单**（限价/市价等）上，卡片要让人知道这是 **杠杆场景**，不是普通现货账户；若还有 **全仓/逐仓** 之类必选信息，也要在卡上能看见。  
**借币 / 还币** 不是「下单」：卡片应展示 **币种、金额、借/还方向** 等，而不是套用限价单的版式。

### 合约

- **限价 / 市价**：除了方向，还要有 **开/平、多/空** 等与用户决策一致的表述；**数量单位**（张还是币）要和交易所一致写清；**杠杆**建议展示；若是 **仅减仓**，要在卡面上 **能看见**。  
- **条件单**：版式上要 **有一块明显的「触发条件」区域**，和普通「立即挂单」区分开；触发后再是市价还是限价、价格与数量等，跟限价/市价行的要求一致。取消条件单则强调 **条件单身份 + 原触发概要**。

## Telegram 能做的边界（工程约束）

原生 Bot **没有**微信那种「整张卡片组件」；我们就是 **气泡里的文字（可加粗/列表） + 底下的按钮**。技术上 **足够**承载「确认 / 取消」和「打开 **交易所站内** **账单与消耗**（**`/subaccount/billing` · `me/commerce`** Deeplink，如 **`?start=ab`**）」。

工程上有几条 **Telegram 官方硬杠杠**，不按做会发不出消息：

- `**callback_data`**（点「确认」「取消」时带回给 Bot 的那段数据）总长只有 **64 字节（UTF-8）**。所以不能塞整单 JSON。**正确做法**：按钮里只带 **很短的一个 id**，**订单详情都存在你们自己服务器**，点了再查。
- **单条文字消息长度有上限**（常见四千多字量级）。单子参数特别长时要 **拆成两条消息**，或让用户 **跳到 H5 / 主站**看清再回会话。
- 点按钮后 Bot 一般需要尽快 `**answerCallbackQuery`**（按 Bot API 文档调用），否则客户端 **长时间转圈**。
- **更花哨的交互**可以用 **Mini App（Web App）**，属于升级路线，首版不强制。

**契约** 与技术自检见 **[telegram/overview** §2.5 · 类型 A / §2～§2.6](../specs/requirements/domains/agent/telegram/overview.md)（卡面 **§2.5.x**，Bot API **§2.6** 等）；**为何必须先点确认才能调交易所** 见设计 **[ADR-001](../specs/design/adr/001-telegram-confirm-before-coobit-write.md)** · [Telegram Bot API](https://core.telegram.org/bots/api)。

## 和设计文档的分工

- **「给用户看什么」**：以 **[telegram/overview §2.5 · 类型 A；§2～§2.6](../specs/requirements/domains/agent/telegram/overview.md)**（类型 A 卡面 **§2.5.x**，总则 / Bot API **§2～§2.6**）与人类阅读版本篇为主。  
- **「服务端能调用哪条 PATH」**：以 **[design/api](../specs/design/api.md)** 矩阵与所内 OpenAPI 为准；**Telegram 先于 Coobit 写、Bot API 硬约束** 见 **同书** **[api.md** ·「Telegram Bot API」专节](../specs/design/api.md) 与 **[telegram/overview** §2.5 · 类型 A / §2～§2.6](../specs/requirements/domains/agent/telegram/overview.md)。**API 没有的，卡片也不能假装有。**  
- **「运营侧怎么配 Bot / Webhook」**（**非**终端卡片文案）：见 **[admin-bot-config](../specs/requirements/domains/agent/telegram/admin-bot-config.md)**；**开通完成后的欢迎语** 同属 **渠道 · Telegram** 可配置项（**FR-TG-ADMIN-06**）。HTTP 登记表 **Telegram Bot / Webhook** 行与 **CC-P1-06** 见 **[design/api](../specs/design/api.md)**、**[contract-closure](../specs/requirements/contract-closure.md)**；**生产收口路径 / MR 勾选** [`closure-remaining` §7.5](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path) · [§7.6](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)。

---

*机器可读能力与验收：[telegram/overview §2.5 · 类型 A、§2～§2.6（含 Bot API 约束）](../specs/requirements/domains/agent/telegram/overview.md)；[overview-legacy-migration §2](../specs/requirements/domains/agent/exchange-agent/overview-legacy-migration.md)（回溯 **§10.5/产品线闸**）；[trade-assistance §2 · FR-T09/FR-T11](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)。*
