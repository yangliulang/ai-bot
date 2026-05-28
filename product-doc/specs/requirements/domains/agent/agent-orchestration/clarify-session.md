# 澄清会话 · Session / Callback / STM（写路径 SSOT）

**路径**：`specs/requirements/domains/agent/agent-orchestration/clarify-session.md`。  
**职责**：写路径 **澄清轮**（**非**类型 A **`pending_confirm`**）的 **会话状态**、**`callback_query` 点按语义**、**STM 注入字段**、**与 `executionId` 关系**。**用户可见话术** → [`prompts/shared/clarify-user-visible.md`](../../../prompts/shared/clarify-user-visible.md)；**Telegram 键盘与 typing** → [`../telegram/overview.md`](../telegram/overview.md) **§2.3.1～§2.3.3**。

**互引**：[`confirmation-flow.md`](confirmation-flow.md) **§1 步骤 2**；[`implementation-alignment.md`](implementation-alignment.md) **§8.1～§8.2**；[`session-concurrency-policy.md`](session-concurrency-policy.md) **（inbound 队列 · 多 execution · 与 §1.1 叠层 §7）**；[`memory-runtime.md`](../../../Runtime/memory-runtime.md) **§10.2～§10.5**、**§16 四原则**；[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **S11**；OpenAPI **`ClarifySessionSnapshot`** · [`orchestration-runtime-schemas.yaml`](../../../../openapi/components/orchestration-runtime-schemas.yaml)。

---

## 1. 与类型 A · `pending_confirm` 的边界（MUST）

| 维度 | **澄清轮**（本篇） | **类型 A 写确认**（ADR-001） |
|------|-------------------|------------------------------|
| **目的** | 补齐 **路由/槽位**；**不得** 扩张交易所写 | 用户 **授权** **`call_exchange_write`** |
| **键盘动词** | **闪兑/限价/买入/卖出/对的** 等 **澄清短动词** | **确认下单/确认修改/取消** 等 **写确认动词** |
| **`callback_data` 前缀** | **`cl:`**（clarify · ≤64B） | **`cf:`** 或 **`design` 冻结之 confirm 前缀** + **`confirmId`** |
| **持久化记录** | **`ClarifySessionSnapshot`**（本篇） | **`pending_confirm`**（ADR-001 · §2.6） |
| **点按后** | **写槽 / 改路由** → **继续澄清或进类型 A** | **单次消费** → **交易所写** |
| **禁止** | **澄清钮** **冒充** **「确认下单」**；**禁止** **`cl:*` 触发写** | **类型 A** **不得** **仅** **补槽而不经 INV-008** |

**验收**：**`SC-CLARIFY-01`**（**§6**）· **`SC-CH-TG-11`**（**同窗** [`telegram/overview` §5](../telegram/overview.md)）。

### 1.1 类型 A × 澄清 × stale · 优先级（MUST）

**当 **`pending_confirm`**（**类型 A**）**与 **`ClarifySessionSnapshot`** **并存或先后出现时**：

| **优先级** | **条件** | **Then** |
|------------|----------|----------|
| **1 · 类型 A 存活** | **`executionId`** **处于 **`waiting_confirmation`** **且 **`pending_confirm`** **未过期/未消费** | **澄清 snapshot 冻结**（**§2.1 表**）；**§14.6 idle/TTL** **不得** **使 **`pending_confirm`** **失效** **或** **改写类型 A 载荷** |
| **2 · 类型 A 优先应答** | **idle 后 inbound** **且** **类型 A 仍存活** | **须** **类型 A 生命周期**（**改参/取消/确认**）**或** **可读说明「仍有待确认订单」** — **禁止** **再发写澄清模板** **覆盖类型 A** |
| **3 · 类型 A 终局后** | **用户取消/过期/已消费 **`cf:*`** | **可** **恢复澄清** **自 **`resolvedSlotsSoFar`**（**§2.1**）；**若 idle 已先达** → **须** **§14.6 stale + Resume** **后再恢复** |
| **4 · STM 清空** | **用户「重新开始/新话题」**（**FR-STM01**） | **须** **取消/过期 **`pending_confirm`** **且** **`ClarifySession.abandoned`** — **同窗** **`FR-STM03`** |
| **5 · 仅澄清无类型 A** | **无 **`pending_confirm`** | **§14.6 stale** **全序适用** |

**类型 A 超时后恢复澄清（v0 默认）**：**用户点取消或 TTL 到达** → **`ClarifySession` 若未 `abandoned`** → **可 **`lifecycleState=active`** **自 **`resolvedSlotsSoFar`** **续澄清**；**若 idle/TTL 亦先达** → **须** **Resume 门控** **后** **再注入槽位** — **禁止** **盲续 **`pendingClarifyKind`** 模板**。

**放弃写路径终局（v0 默认）**：**§2.1.1 / §2.3 步 2～3** **命中** → **`abandoned=true`** **`lifecycleState=abandoned`** **且** **`executionId` 主态 **`cancelled`**（**计费/观测可 join** — **同窗** [`consume-and-bill` S3](../../../flows/consume-and-bill.md)）。

**`callback_query` 与 stale**：**`lifecycleState=stale`** **时 **`cl:resume`** **等同** **§4.1.1** **显式续单**；**过期/非法 **`cl:*`** → **§4.2 拒收** — **不得** **silent 写**。

**Webhook 幂等 × clarify**：**同一 **`update_id`** **重复投递** **须** **不二次递增 **`clarifyTurn`** **或** **重复出站** — **同窗** **`eval.runtime.telegram_update_idempotent`** **+** **§4.2**。

**并发 × message/callback**：**in-flight 处理 **`message`** **时到达 **`cl:*`** **须** **与** [`session-concurrency-policy` §2](session-concurrency-policy.md) **串行** — **0** **槽位 lost update** — **`SC-AO-09`** · **`eval.session.callback_serial_with_message`**。

---

## 2. 生命周期与 `executionId`（MUST）

### 2.1 何时沿用 / 何时新开

| 事件 | **`executionId`** | **`ClarifySessionSnapshot`** |
|------|-------------------|------------------------------|
| 用户 **首次** 表达写意图（如「买入 BNB」） | **分配** **新** `executionId`（**同窗** [`consume-and-bill` S3](../../../flows/consume-and-bill.md)） | **创建** snapshot · **`clarifyTurn=1`** |
| **同 session** 内 **澄清 follow-up**（自然语言或 **`cl:*` 按钮**） | **沿用** **同一** `executionId` | **递增** **`clarifyTurn`** · **合并** **`resolvedSlotsSoFar`** |
| 用户 **明确放弃**（**同窗** **§2.1.1 放弃话术**）或 **切只读** / **寒暄无写意图** | **终局** **`cancelled`** **或** **不进入写路径**（**所内终裁**） | **清除** **或** **标记 `abandoned=true`** |
| **类型 A 已发出** | **沿用** | **澄清 session 冻结** — **后续仅** **类型 A 生命周期**（**§1.1**） |
| **类型 A 超时 / 用户取消确认** | **沿用**（**v0 默认**） | **可** **恢复澄清** **自** **`resolvedSlotsSoFar`** — **若已 stale** **须** **Resume 门控**（**§1.1**） |
| **空闲 / 澄清 TTL 达阈**（**§2.4** · **先达者**） | **沿用或新开**（**Resume 门控后**） | **`lifecycleState=stale`** · **退出活跃 L1** · **写温索引** |

**禁止**：**每轮澄清** **新建** `executionId` **导致** **STM 丢槽**（**同窗** **`SC-CLARIFY-02`**）。

#### 2.1.1 放弃写路径 · 话术示例（非穷举）

**命中任一类** **且** **无** **同期** **明确写动词/委托参数** → **MUST** **`abandoned=true`** **`lifecycleState=abandoned`** **并** **停止** **写澄清复读**：

| 类别 | 示例（`zh-Hans`） |
|------|-------------------|
| **放弃** | 「不买了」「取消」「算了」「都不要了」「先不买了」「不用了」 |
| **切只读** | 「只查价」「先看看行情」「有哪些币可以买」「多少钱」**（无下单参数）** |
| **寒暄** | 「你好」「在吗」「你能做什么」**（无写意图）** |

**Then**：**可读短句** **确认已取消或未进入下单**（**如**「好的，有需要再说」）；**不得** **再发** **闪兑/限价** **写澄清** — **`SC-CLARIFY-06`**。**若当前为 **`stale`** **亦须 **`abandoned`** **终局** — **不得** **长期 stale+abandoned 双态并存**。

### 2.2 澄清轮次预算

**同窗** [`clarify-user-visible` §6](../../../prompts/shared/clarify-user-visible.md)：**宜 ≤2 轮** 用户可见澄清后进 **只读补槽或类型 A**；**`clarifyTurn > 3`** **且仍缺参** → **须** **收束为一句总结 + 一个最关键问题**（**禁止** checklist）。

### 2.3 澄清态下 · 每条 `message` inbound（MUST）

**适用**：**存在** **未 **`abandoned`** 之 **`ClarifySessionSnapshot`**（**含 **`lifecycleState=stale`** **仍须 §2.3**）**时**，**每条** **`Update.message`** **仍须** **走** **[`execution.md` §1 步 1～4](../../../Runtime/execution.md) **意图识别** — **禁止** **「session 有 pending → 跳过 Parser → 盲发上轮澄清模板」**。**stale** **时** **活跃 L1 已退出注入**（**§2.4**）。

| **步** | **MUST** |
|--------|----------|
| **1 重读 inbound** | **L→R**：**本条** **自然语言** **参与** **意图分类**；**不得** **仅** **凭** **`pendingClarifyKind`** **复读 outbound** |
| **2 分流** | **`intent_family`** **为** **`market_read` / `portfolio_read` / `analysis` / `chitchat`** **且无写意图** → **只读/寒暄应答**；**写澄清 session** **`abandoned=true`** **`lifecycleState=abandoned`**（**含原 **`stale`** **态**）— **`SC-CLARIFY-07`** · **若** **ReadClarifySession active** → **同窗** [`read-clarify-session` §2.3](read-clarify-session.md) |
| **3 放弃** | **命中** **§2.1.1** → **`abandoned=true`** **`lifecycleState=abandoned`** · **`executionId` 主态 `cancelled`**（**v0 默认** · **§1.1**）— **`SC-CLARIFY-06`** |
| **4 仍写 follow-up** | **合并** **本条槽位草案** → **`resolvedSlotsSoFar`** · **`clarifyTurn++`** → **重跑 Resolver** → **L 润色** **须** **镜像 inbound** — **`SC-CLARIFY-05`** |
| **5 出站硬闸** | **禁止** **连续两轮** **用户可见正文** **逐字相同**（**§2.5 Normative 去重**）；**禁止** **`routingHints` / `orchestrationNextSteps` / Prompt 条文** **作正文** — **`SC-CLARIFY-08`** · **`SC-CLARIFY-09`** |

**负例叙事（须避免）**：用户「你好」→ **不得** **闪兑/限价盘问**；用户「有哪些币可买」→ **须** **只读/listing** **或** **等价说明**；用户「都不要了」→ **不得** **复读** **同一条** **写澄清**。**同窗** [`memory-runtime` §16.8](../../../Runtime/memory-runtime.md) **生产回归链**。

### 2.4 空闲 / TTL · 默认 stale + Resume（MUST）

**SSOT**：[`memory-runtime` §14.6](../../../Runtime/memory-runtime.md) · [`design/memory-runtime-injection` §2.4](../../../../design/memory-runtime-injection.md)。

#### 2.4.1 触发（统一 · 先达者）

**当** **下列任一成立** **且** **存在未 `abandoned` 写路径上下文**：

| **条件** | **说明** |
|----------|----------|
| **A · session 空闲** | **距上次用户消息 ≥ `STM_IDLE_RESUME_PROMPT_SEC`**（**默认 1800**） |
| **B · 澄清 TTL** | **`ClarifySessionSnapshot.expiresAt` 到达**（**默认 **`STM_CLARIFY_SESSION_TTL_SEC=900`**） |
| **C · 无 snapshot 之写 L1** | **存在未终局 **`executionId`** 写路径 L1**（**如无 ClarifySession 之 Planner 草稿**）**且** **满足 A 或 B 之 idle/TTL 等价策略** |

**写路径上下文** **=** **未 `abandoned` 之 **`ClarifySessionSnapshot`** **或** **同 session 未终局写 **`executionId` L1**（**类型 A 草稿 / 未确认写参 · 同窗 **`memory-runtime` §14.6**）。

#### 2.4.2 步序（MUST）

| **步** | **BFF/Runtime MUST** |
|--------|----------------------|
| **0 stale** | **`lifecycleState=stale`** · **`staleAt=now`** · **写/更新 **`WarmExecutionEpisode`**（**§2.4.3**） |
| **1 装配** | **活跃 L1 不含** **该写澄清/写 L1 摘要** — **默认新话题** |
| **2 意图** | **§2.3 全序** — **本条 inbound 优先** |
| **3 Resume** | **规则层显式续单** **或** **Resume 分类器 **`confidence ≥ RESUME_CLASSIFIER_MIN_CONFIDENCE`**（**[`memory-runtime` §14.6.4](../../../Runtime/memory-runtime.md)**）→ **温召回** → **§2.4.4** |
| **4 禁止** | **不得** **跳过 §2.3** **盲发 **`pendingClarifyKind`** 模板** |

**用户可见（宜）**：**非阻塞短句** — **Telegram §2.8.6**；**非** **强制 **`cl:resume`/`cl:new`** 卡**（**fallback only**）。

#### 2.4.3 温索引 · 多条 stale（MUST）

**同 **`sessionId`** **下** **允许多条 **`WarmExecutionEpisode`**。**Resume 门控** **默认** **仅召回** **`staleAt` 最近一条** **写路径 episode**。**若 inbound 显式指代 symbol/侧** **与** **非最近一条匹配** **且** **规则层高置信** → **可召回** **匹配 **`executionId`** **之 episode**（**须可观测 **`episodePickReason`**）。

#### 2.4.4 stale → active 恢复（MUST）

**仅当** **Resume 门控允许召回** **且** **本条仍为写路径**：

| **项** | **MUST** |
|--------|----------|
| **`lifecycleState`** | **`stale` → `active`** |
| **`executionId`** | **沿用** **温索引 **`executionId`**（**除非** **用户明确新 symbol/新任务** → **新开**） |
| **`clarifyTurn`** | **递增** **`++`**（**不重置**） |
| **`pendingClarifyKind`** | **须** **重跑 Resolver 后** **由 **`missing[]`** **重算** — **禁止** **恢复 stale 前 **`pendingClarifyKind`** 模板** |
| **失败** | **Resolver 仍缺参且非明确续单** → **保持/回 **`stale`** **或** **`abandoned`** — **禁止** **silent 类型 A** |

### 2.5 Normative 去重 · 连续 outbound（MUST · v0）

**适用**：**同一 **`sessionId` + `executionId`** **下** **连续两轮** **用户可见 assistant 正文**（**含** **澄清/进度句** **不含** **类型 A 卡字段块**）。

| **项** | **MUST** |
|--------|----------|
| **比较域** | **归一化后逐字比较**（**trim 首尾空白** · **折叠连续空白** · **可选忽略末尾标点差异** — **所内实现须固定一种** **并** **可观测 **`dedupeCompared=true`**） |
| **触发** | **上一轮 outbound 与本轮候选** **归一化后相同** **且** **本轮 inbound 与上轮 inbound 不同** |
| **Then** | **须** **至少其一**：**(a)** **重跑 Parser/Resolver 后改写话术** **镜像 inbound**；**(b)** **追加非空进度微句**（**如**「收到，…」）；**(c)** **改 **`edit_message`** **更新上一轮**（**若 **`lastClarifyMessageId`** 可用**） |
| **豁免** | **用户连续发送** **同义/相同** **inbound** **且** **仍缺同一槽** → **可** **等价复述** **但** **宜** **缩短** |
| **禁止** | **不得** **因去重失败** **跳过** **§2.3 重意图** **或** **直接 silent** |

**验收**：**`SC-CLARIFY-08`** · **`eval.clarify.no_repeat_outbound`**。

---

## 3. `ClarifySessionSnapshot` · 字段下限（产品 · OpenAPI 同窗）

**性质**：**BFF/Runtime 持久化或缓存** 之 **结构化快照**；**须** **注入 Parser/Prompt**（**L0/STM**）**与** **Resolver**。**Observability** **宜** **可 join** **`sessionId` + `executionId` + `clarifyTurn`**。

| 字段 | **必填** | **说明** |
|------|----------|----------|
| **`sessionId`** | MUST | Telegram **聊天锚点** |
| **`executionId`** | MUST | **本条写路径** **主轨迹** |
| **`clarifyTurn`** | MUST | **从 1 起** **递增** **之** **澄清轮次**（**含** **按钮点按轮**） |
| **`resolvedSlotsSoFar`** | MUST | **已确认槽位** **键值**（**如** `symbol`、`side`、`tradeMode`、`semanticIntent`）；**供 STM **§4** |
| **`pendingClarifyKind`** | 推荐 | **当前等待** **用户补** **之** **项**（**枚举** **同窗** **`ClarifyKeyboardKind`** / **`missing[]` 首项**） |
| **`effectiveLocale`** | 推荐 | **`zh-Hans` / `zh-Hant` / `en`** — **键盘与正文同窗** |
| **`lastClarifyMessageId`** | 推荐 | **可选** **`edit_message`** **就地更新** **之** Telegram `message_id` |
| **`expiresAt`** | 推荐 | **澄清 session TTL**（**默认 **`STM_CLARIFY_SESSION_TTL_SEC`** · [`keys` §2.1](../../../domains/admin/trading-agent-config/keys.md)） |
| **`lifecycleState`** | 推荐 | **`active` \| `stale` \| `abandoned`** — **stale** **= 空闲默认策略 · 退出活跃 L1**（**§2.4**） |
| **`staleAt`** | 可选 | **标记 stale 时刻** — **可观测 / Resume 门控** |
| **`abandoned`** | 可选 | **用户放弃** **或** **超时** **或** **终局后不再恢复** |

**STM 注入块（Prompt 下限）**：**须** **含** **可读摘要** **`resolvedSlotsSoFar` 人话列表** + **「仍缺：…」**（**来自** **`missing[]`** **或** **`pendingClarifyKind`**）— **禁止** **仅** **裸 JSON ** **无** **说明**。

**验收**：**`SC-CLARIFY-02`**、**`SC-CLARIFY-03`**。

---

## 4. `callback_data` · 澄清短键注册表（MUST）

**约束**：UTF-8 **≤64B**；**载荷** **仅** **短键** — **明细** **自** **`ClarifySessionSnapshot` + `executionId`** **解析**（**同窗** **ADR-001 精神** · **非** **`pending_confirm`**）。

### 4.1 键 → 槽位 / 路由（现货写 · 首版）

| **`callback_data`** | **用户动作** | **BFF MUST 写入 `resolvedSlotsSoFar`** | **下一跳（规则）** |
|---------------------|--------------|----------------------------------------|-------------------|
| **`cl:fc`** | 选 **闪兑/市价** | `tradeMode=flash_convert` · `type=MARKET` | **若** **仍缺数量** → **数量澄清**（§4.2）；**若 ALL_IN** → **只读补槽**（INV-010）；**否则** **Resolver** |
| **`cl:lo`** | 选 **限价** | `tradeMode=limit_order` · `type=LIMIT` | **若缺 price/qty** → **对应澄清**；**否则** **Resolver** |
| **`cl:buy`** | 选 **买入** | `side=BUY` | **继续** **缺项澄清** |
| **`cl:sell`** | 选 **卖出** | `side=SELL` | 同上 |
| **`cl:sym:ok`** | **确认** 默认交易对 | **固化** **`symbol`**（**如** `BNBUSDT`） | **继续** **缺项澄清** |
| **`cl:sym:no`** | **换一个** | **清除** **`symbol`** **或** **置** **`pendingClarifyKind=symbol`** | **追问** **标的/交易对** |
| **`cl:qty:base`** | **按 base 数量**（如 BNB） | `qtyKind=base` | **追问** **数量（base）** — **开放问或下条 inbound** |
| **`cl:qty:quote`** | **按 quote 金额**（如 USDT） | `qtyKind=quote` | **追问** **quoteQty** |

**V1 范围（MUST）**：上表 **现货写路径** **为** **首版冻结集**。**杠杆/合约/理财** **澄清键盘** **须** **另 MR** **扩展 **`callback_data`** **注册表** **与** **Resolver 槽位** — **禁止** **在未登记键上** **静默发 **`inline_keyboard`**。**`FEATURE_AGENT_MARGIN|FUTURES|WEALTH=OFF`** **时** **不得** **暴露对应 **`cl:*`**。

### 4.1.1 会话控制 · 续/新（`cl:resume` / `cl:new` · MUST）

**适用**：**§14.6** — **fallback only**（**`STM_IDLE_DEFAULT_POLICY=prompt_resume_or_new`**）**或** **用户主动点按**；**默认策略下** **不依赖** **阻塞式二选一**。

| **`callback_data`** | **用户动作** | **BFF MUST** | **下一跳** |
|---------------------|--------------|--------------|------------|
| **`cl:resume`** | **继续上一笔** | **沿用** **`executionId`** · **合并** **`resolvedSlotsSoFar`** · **Facts 须 Fresh 或 stale 声明** | **重跑 Resolver** → **澄清/类型 A** — **禁止** **盲复读过期模板** |
| **`cl:new`** | **新话题** | **等同** **FR-STM01** · **`ClarifySession.abandoned=true`** · **清 L0/活跃 L1** | **短句确认** → **等待新意图** |

**OpenAPI**：**`ClarifyCallbackData`** · **`ClarifyKeyboardKind=idle_resume_or_new`**。

**i18n 按钮字面**：**同窗** [`telegram/overview` §2.3.2](../telegram/overview.md) **续/新行**。

**禁止**：**`cl:resume`/`cl:new`** **触发** **`call_exchange_write`** **或** **冒充类型 A**。

### 4.2 点按处理序（MUST）

1. **`answerCallbackQuery`** — **尽快** **结束** **客户端 spinner**（**§2.3.1**）。  
2. **校验** **`ClarifySessionSnapshot` 未过期、未 abandoned**；**`lifecycleState=stale`** **时** **仅允许** **§4.1.1 **`cl:resume`/`cl:new`** **或** **须** **先走 §2.3 message 重意图**；**非法/过期** → **可读短句 + 可选** **「重新开始」**（**非**类型 A）。  
3. **按 §4.1 合并槽位** → **写回** **`resolvedSlotsSoFar`** · **`clarifyTurn++`**。  
4. **重跑** **Resolver**（**R**）**与** **编排**（**只读补槽** **若 INV-010**）。  
5. **出站**：**LLM 润色**（**L**）**或** **规则进度句** + **下一张澄清键盘** **或** **类型 A**（**仅当** **INV-008 齐**）。

**禁止**：**跳过 Resolver** **直接** **发类型 A**；**禁止** **`cl:*` 调** **`call_exchange_write`**。

---

## 5. 端到端示例 · 「买入 BNB」（需求叙事）

| 轮次 | 用户 | **`resolvedSlotsSoFar` 增量** | **对用户（L 润色方向）** | **键盘（R→B）** |
|------|------|-------------------------------|--------------------------|-----------------|
| 1 | 「我想买入 BNB」 | `side=BUY` · `baseAsset=BNB` | 买入 BNB。闪兑还是限价？ | **闪兑 · 限价** |
| 2 | 点 **闪兑** | `tradeMode=flash_convert` | （**宜** **edit** 上轮或新消息）明白，BNB/USDT 闪兑买入… | **按 BNB · 按 USDT**（**若仍缺数量**） |
| 3a | 「100 USDT」 | `quoteQty=100` · `provenance=user_input` | → **类型 A** | — |
| 3b | 「全部买入」 | `semanticIntent=ALL_IN` | 查 USDT 余额…（**B 只读**） | — → **类型 A** |

**同窗** [`clarify-user-visible` §7](../../../prompts/shared/clarify-user-visible.md)。

---

## 6. 验收（节选）

| ID | Then |
|----|------|
| **`SC-CLARIFY-01`** | **澄清键盘** **不得** 使用 **「确认下单」** **类** **写确认动词**；**`cl:*` 不触发** **交易所写** |
| **`SC-CLARIFY-02`** | **同** **`executionId`** **内** **按钮点按后** **`resolvedSlotsSoFar` 含** **上轮已选**（**如** 点闪兑后 **仍保留** BNB/BUY） |
| **`SC-CLARIFY-03`** | **Prompt/STM 注入** **须** **含** **`resolvedSlotsSoFar` 摘要**；**不得** **下轮举例无关币对** |
| **`SC-CLARIFY-04`** | **`cl:fc` 后** **Resolver `mode`/槽** **须** **反映** **闪兑** **而非** **仍按限价缺参** |
| **`SC-CLARIFY-05`** | **澄清态** **每条 **`message` inbound** **须** **重跑意图/Parser**；**follow-up** **须** **镜像 inbound** **后** **再出站** — **§2.3** |
| **`SC-CLARIFY-06`** | **放弃话术（§2.1.1）** → **`abandoned=true`**；**不得** **再发** **写澄清** **或** **复读** **上轮同句** |
| **`SC-CLARIFY-07`** | **澄清中** **只读/寒暄 inbound** → **须** **只读应答或寒暄**；**写澄清 session** **须** **abandon** — **§2.3 步 2** |
| **`SC-CLARIFY-08`** | **连续两轮** **用户可见 outbound** **不得** **逐字相同**（**除非** **用户重复同义未补槽**） |
| **`SC-CLARIFY-09`** | **BFF 出站** **不得** **含** **`routingHints`/`orchestrationNextSteps`/Prompt 条文** **原文或近义** — **同窗** [`clarify-user-visible` §1](../../../prompts/shared/clarify-user-visible.md) |
| **`SC-CH-TG-11`** | **点按澄清钮** **须** **§4.2 全序**；**非法 `cl:*`** **可观测拒收** — **同窗** **§5** |

**Eval 构造**：[`evals/clarify-telegram.md`](../../../evals/clarify-telegram.md) **§7～§10**。

---

**文档版本**：1.6.1-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**互引 session-concurrency §2 callback 串行**。承 1.6.0-mvp。
