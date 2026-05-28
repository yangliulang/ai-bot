# 会话并发 · 单 session 多 execution / 在途 inbound（P0 SSOT）

**路径**：`specs/requirements/domains/agent/agent-orchestration/session-concurrency-policy.md`。

**职责**：定义 **同一 Telegram `sessionId`（绑定会话）** 内 **多条 inbound、多个 `executionId`、写路径在途（澄清 / 类型 A / UNKNOWN / 编排 in-flight）** 的 **产品优先级、串行/拒新/排队策略与用户可见下限**。**不**替代 [`locking.md`](../../../Runtime/locking.md) **分布式互斥实现**；**不**新增 OpenAPI 字段（形状 **B 阶段** **专项 MR**）。

**互引**：[`clarify-session.md`](clarify-session.md) **§1.1 类型 A×stale** · **§2.3 重意图**；[`memory-runtime.md`](../../../Runtime/memory-runtime.md) **§14.6 stale+Resume**；[`locking.md`](../../../Runtime/locking.md) **§2 主态单写**；[`sessions.md`](../../../Runtime/sessions.md)；[`unknown-state.md`](../../../Runtime/unknown-state.md)；[`execution-lifecycle.md`](execution-lifecycle.md) **§4 `FR-AO06`**；[`confirmation-flow.md`](confirmation-flow.md)；[`telegram/overview.md`](../telegram/overview.md) **§2.3.1 typing · §2.6 刷屏**；[`risk/exposure-limit.md`](../../../risk/exposure-limit.md)；[`overview.md`](overview.md) **FR-AO07 · SC-AO-09～10**。

**执行体分工**：**R** = 规则/编排/BFF 状态机；**B** = 渠道出站；**L** = LLM 润色。**用户可见句** **默认 L**，**分支走向** **以本篇 R 表为准** — 同窗 [`clarify-user-visible` §0](../../../prompts/shared/clarify-user-visible.md)。

---

## 1. 范围与术语

| 术语 | **本卷含义** |
|------|--------------|
| **`sessionId`** | **绑定 Telegram 聊天** 之 **稳定会话锚点**（**非** 单条 `message_id`）— [`sessions.md`](../../../Runtime/sessions.md) |
| **在途写 execution** | **主态** **∈** **`{active_clarify, waiting_confirmation, executing, unknown_pending, settling}`** **且** **拟触达或已触达** **写路径** **之** **`executionId`** |
| **编排 in-flight** | **自 inbound 接入至本轮 outbound 终局**（**含** **typing、Parser、工具、类型 A 待发**）**尚未完成** **之** **处理槽** |
| **D-1 挡新写** | **显式用户在途** **为真** **时** **拒绝** **第二笔** **新写起票** — [`locking.md`](../../../Runtime/locking.md) **§2**、[`exchange-agent/boundaries`](../exchange-agent/boundaries.md) |
| **只读 execution** | **无** **`call_exchange_write`** **意图** **或** **已终局** **之** **查询/分析** **轨迹** — **与** **写 execution** **可并存** **（§4）** |

**非目标（v0）**：**跨 `sessionId` 合并**；**群聊多用户**（**本版** **仅** **1:1 Bot**）；**Mini App 并行通道** — [`product.md`](../../../product.md) **§非目标**。

---

## 2. 单 session · inbound 队列（MUST）

**问题**：用户 **连发** **或** **Bot 处理中** **再发** **导致** **双 Parser、乱序出站、澄清丢槽**。

### 2.1 默认策略 · `SESSION_INBOUND_QUEUE_POLICY`

| 值 | **语义（v0 默认 **`serial_per_session`**）** |
|----|-----------------------------------------------|
| **`serial_per_session`** | **同一 `sessionId`** **同时** **最多** **1** **条** **inbound** **进入** **完整 Parser→编排→出站** **链**；**其余** **入队 FIFO** |
| **`coalesce_latest`** | **处理中** **若** **又来** **≤ `SESSION_INBOUND_COALESCE_WINDOW_MS`** **内** **多条** **text** → **合并为** **一条** **合成 inbound**（**空格连接** **或** **所内固定规则** **须** **可观测 `coalescedCount`**）**再** **入队** |
| **`reject_while_busy`** | **in-flight** **时** **新 inbound** **拒处理** **+** **短句请稍候**（**仅** **运维显式开启** **不推荐默认**） |

**MUST**：

1. **Webhook 幂等**（**同 `update_id`**）**优先于** **队列** — [`clarify-session` §1.1](clarify-session.md)、**`eval.runtime.telegram_update_idempotent`**。  
2. **`callback_query`（`cl:*` / `cf:*`）** **与** **`message`** **共用** **同一** **session 队列** **或** **等价互斥** — **禁止** **callback 与 message** **并行** **改** **同一** **`ClarifySessionSnapshot`**。  
3. **排队深度硬顶** **`SESSION_INBOUND_QUEUE_MAX_DEPTH`**（**默认 3**）：**超限** → **丢弃最旧** **或** **合并**（**须** **可观测 `queueDropReason`**）**+** **对用户** **一条** **「消息较多，我先处理你刚才说的…」**（**L 润色**）。  
4. **in-flight 超过 **`SESSION_BUSY_ACK_WITHIN_MS`**（**默认 800ms**）** **须** **已发** **typing** **或** **等价进度短句** — 同窗 [`telegram/overview` §2.3.1](../telegram/overview.md)。

**验收**：**`SC-AO-09`** · **`eval.session.inbound_serial_no_double_parse`**。

---

## 3. 多 `executionId` · 优先级总表（MUST）

**当** **同一 `sessionId`** **存在** **多个** **未终局** **`executionId`** **（** **含** **1 写 + N 只读** **）** **时** **本条 inbound** **须** **按下表** **裁决** **「服务哪条 / 挂起哪条 / 终局哪条」**。

| **优先级** | **条件（摘要）** | **Then（产品）** |
|:----------:|------------------|------------------|
| **P0** | **同 `update_id` 重投** | **幂等** **0** **副作用** — **先于** **一切** |
| **P1** | **类型 A **`pending_confirm`** 存活**（**`waiting_confirmation`**） | **本条** **须** **服务** **该 **`executionId`**：**改参/确认/取消 **`cf:*`** **或** **自然语言等价**；**禁止** **另起** **新写澄清** **覆盖卡面** — [`clarify-session` §1.1](clarify-session.md) |
| **P2** | **本条为 **`cf:*` / 类型 A 生命周期** **且** **`executionId` 匹配** | **仅** **消费** **匹配** **`executionId`** **之** **确认链** |
| **P3** | **写澄清 **`ClarifySession.active`** **且** **本条** **仍为写 follow-up** | **沿用** **该 **`executionId`** — **§2.3 全序** |
| **P4** | **写澄清 active · 本条** **只读/寒暄/放弃** | **clarify-session §2.3 步 2～3** — **abandon 写 session** |
| **P5** | **`unknown_pending`** **写 execution 存活** | **见** **§5.3** — **默认** **挡** **新写起票** **（D-1）** **；** **只读/查单** **允许** |
| **P6** | **`executing` / 逻辑改单两笔写 in-flight** | **见** **§6** — **挡** **冲突新写** **；** **允许** **只读查进度** |
| **P7** | **无在途写 · 本条新写意图** | **新起** **`executionId`** **（** **或** **Resume stale** **沿用** — **§14.6** **）** |
| **P8** | **无在途写 · 本条只读** | **可** **新起** **只读 **`executionId`** **或** **并入** **轻量只读轨**（**不计** **写互斥**） |

**禁止**：

- **同一 session** **> `SESSION_MAX_ACTIVE_WRITE_EXECUTIONS`**（**默认 1**）**个** **在途写 execution** **同时** **处于** **P1～P6** **活跃态**。  
- **silent** **切换** **用户** **以为** **仍在** **确认 A** **实则** **已** **新开 B** **写澄清**。

**验收**：**`SC-AO-10`** · **`eval.session.single_active_write_execution`**。

---

## 4. 写 execution 与只读 execution 并存（MUST）

| **场景** | **MUST** |
|----------|----------|
| **写澄清中 · 用户问价/余额** | **P4** → **只读应答** **+** **abandon 写澄清** — **`SC-CLARIFY-07`** |
| **类型 A 待确认 · 用户问价** | **先** **短答只读**（**可选**）**或** **提示「仍有待确认订单」** — **不得** **silent 消费类型 A** |
| **UNKNOWN 在途 · 用户问「成交了吗」** | **§5.3** — **须** **UNKNOWN 话术** **+** **可选** **只读查挂单/订单** **（** **Fresh 工具** **）** |
| **只读 execution 进行中 · 用户新写** | **只读轨** **可** **终局或挂起** → **P7** **新写** |

**STM**：**只读结果** **不得** **写入** **写 execution** **之 **`resolvedSlotsSoFar`** **除非** **用户** **明确** **用于** **当前写**（**如** ALL_IN 前查余额 — **INV-010**）。

---

## 5. 第二笔写意图 · 在途写已存在（MUST）

### 5.1 写澄清 active（无类型 A）

| **用户表达** | **Then** |
|--------------|----------|
| **同 symbol/同侧 follow-up**（补数量/改限价） | **P3** **沿用 **`executionId`** **合并槽位** |
| **明确新 symbol / 「另外买 ETH」** | **abandon 旧写澄清**（**或** **stale** **若 idle 已触发**）→ **新 **`executionId`** **或** **Resume 匹配 episode** |
| **「都不要了」** | **§2.3 步 3** · **`cancelled`** |
| **与旧单冲突的写**（**卖变买** **且** **未说改主意**） | **L 镜像确认** **「是要改买/卖方向吗？」** **一轮** **再** **Resolver** |

### 5.2 类型 A 待确认 · 第二笔写

| **Then** |
|----------|
| **须** **可读提示** **「你还有一笔待确认，请先确认或取消」** **+** **保留** **原类型 A 卡**（**edit 或重发** **同窗** **§2.6 刷屏**） |
| **禁止** **另发** **第二张** **无关** **类型 A** **冒充** **第二笔写已受理** |
| **用户** **明确** **「取消上一笔，买 ETH」** → **消费/过期 **`pending_confirm`** → **新写** **起票** |

### 5.3 `unknown_pending` · 用户 inbound（D-1 + 追问状态机）

**默认（v0 · `SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN=true`）**。**追问细表 SSOT** → [`unknown-stall-policy` §2](../../../risk/unknown-stall-policy.md) **（** **意图 **`unknownFollowupIntent`** **→ 动作** **）**。

| **用户表达 / 意图** | **Then** |
|---------------------|----------|
| **`status_query`**（「成交了吗」） | **有界 reconcile + 只读摘要** **+** **UNKNOWN 叙事** **—** **0 SUCCESS** |
| **`read_order_position`** | **允许** **只读 **`executionId`** **或** **E* 只读步** |
| **`cancel_request`** | **可撤** **→** **撤单 skill + 类型 A**；**否则** **Explain + 查单** |
| **`repeat_submit`** | **0** **同参自动重放** **+** **勿重复提交叙事** |
| **`new_write`** | **拒新写** **`FR-T05` 族** **—** **禁止** **新类型 A** |
| **`impatient_nudge` / `greeting_unrelated`** | **短答** **+** **可选** **一行 E* 状态** **（** **节流** **）** |

**配置**：**`UNKNOWN_*`** → [`keys` §2.4](../../admin/trading-agent-config/keys.md)。

**例外（须 config + 风控 MR）**：**`SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN=false`** **仅** **当** **运营** **与** **risk** **书面** **允许** **并行在途写** — **本版** **默认** **不启用**。

### 5.4 已达 `SESSION_MAX_ACTIVE_WRITE_EXECUTIONS`

**Then**：**同 5.2** **挡新写** **+** **列出** **在途摘要**（**symbol · 状态 · 待确认/待结果** **人话** **一行**）。

**Eval**：**`eval.session.second_write_while_clarify`** · **`eval.session.second_write_while_confirm`** · **`eval.session.new_write_blocked_on_unknown`** · **`eval.unknown.*`**。

---

## 6. 逻辑改单 · 两笔写 in-flight（MUST）

**上下文**：**`trade.spot.amend_limit_order` / `trade.futures.amend_limit_order`** **一张类型 A** **授权** **`cancel` → `order`** **顺序两笔 HTTP** — [`allowlist`](../../../integrations/exchange/agent-coobit-api-allowlist.md)、[`trade-via-agent`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单**。

| **阶段** | **并发策略** |
|----------|--------------|
| **类型 A 已确认 · cancel 已发 · order 未终局** | **P6** **挡** **同 symbol** **新写**；**用户** **「改主意不改了」** → **若 order 未发** **可** **abort 链** **（** **须** **观测 `planAborted=true`** **）** |
| **用户** **「改成 50000 卖」** **（** **又改价** **）** | **须** **等** **前链终局** **或** **显式** **撤链** **再** **新逻辑改单** — **禁止** **第三笔写** **叠在** **UNKNOWN 改单链上** |
| **用户只读「改单成功了吗」** | **进度话术** **区分** **已撤/已挂/UNKNOWN** — **禁止** **假称 amend API** |

**验收**：**`SC-AO-10`** **子项** · **`eval.session.amend_chain_blocks_parallel_write`**。

---

## 7. 与 stale / Resume / 类型 A 的叠层（MUST）

**优先级** **高于** **本篇** **一般 P 表** **之** **专用条** **已** **在** [`clarify-session` §1.1](clarify-session.md) **冻结**。**本篇** **补** **并发维**：

| **叠层** | **MUST** |
|----------|----------|
| **idle stale 与 in-flight 同时** | **in-flight 完成前** **不得** **对** **正在处理的 inbound** **触发 stale**；**stale** **仅** **在** **队列空且超时** **评估** |
| **stale 后 inbound** | **§14.6 + §2.3** **先于** **P7 新起** |
| **多 stale episode** | **Resume** **默认** **最近一条** — [`clarify-session` §2.4.3](clarify-session.md)；**并发** **禁止** **同时 active** **两条写澄清** |

---

## 8. 观测与配置（索引）

### 8.1 宜观测字段（逻辑名 · B 阶段 OpenAPI）

| 字段 | **说明** |
|------|----------|
| **`sessionQueueDepth`** | **当前排队 inbound 数** |
| **`sessionInboundPolicy`** | **生效 **`SESSION_INBOUND_QUEUE_POLICY`** |
| **`activeWriteExecutionId`** | **至多** **1** **个** **在途写** |
| **`concurrencyDecision`** | **枚举** **`served_execution` / `queued` / `blocked_new_write` / `abandoned_prior`** |
| **`blockedReason`** | **如** **`unknown_pending` / `waiting_confirmation` / `queue_full`** |

### 8.2 配置键

**SSOT**：[`trading-agent-config/keys` §2.2](../../admin/trading-agent-config/keys.md) — **`SESSION_*`** **族**。

---

## 9. 用户可见模式（宜 · L 润色方向）

| **触发** | **宜话术方向（zh-Hans 骨架）** |
|----------|----------------------------------|
| **排队中** | 「收到，我先处理你上一条…」 |
| **待确认挡新写** | 「你还有一笔待确认订单（BNB 买入），请先点确认或取消。」 |
| **UNKNOWN 挡新写** | 「上一笔结果还在确认中，我可以先帮你看订单状态。」 |
| **改单链 in-flight** | 「正在按你的确认修改委托，稍等我查一下进度。」 |

**禁止**：**内部词** **`executionId` / 队列 / scenarioId** — [`clarify-user-visible` §1](../../../prompts/shared/clarify-user-visible.md)。

---

## 10. 验收（`SC-AO-09`～`SC-AO-10`）

| ID | Then |
|----|------|
| **`SC-AO-09`** | **连发 2 条不同 inbound** **≤1s** → **观测** **仅** **1** **条** **完整 Parser 链** **或** **coalesce** **可观测**；**0** **双出站矛盾** |
| **`SC-AO-10`** | **任意时刻** **同一 session** **在途写 execution** **≤ `SESSION_MAX_ACTIVE_WRITE_EXECUTIONS`**；**第二笔写** **须** **挡或** **先终局前单** |
| **`SC-AO-10a`** | **类型 A 存活 + 新写** → **0** **第二张无关类型 A** |
| **`SC-AO-10b`** | **`unknown_pending` + 新写（默认 config）** → **`FR-T05` 族** **+** **0** **新 `call_exchange_write`** |
| **`SC-AO-10c`** | **逻辑改单链 executing + 同 symbol 新写** → **挡** **或** **显式 abort 后再写** |

**Eval 构造**：[`evals/session-concurrency.md`](../../../evals/session-concurrency.md)。

---

## 11. 后续 P1（索引）

**v0 P1 规格批次（session / clarify / fallback / unknown 追问）** **已闭合** — **实现 MR** **见** [`closure-remaining` §7](../../../closure-remaining.md#cc-remaining-open-items)。

---

**文档版本**：1.0.1 · **维护**：产品 + Agent Runtime owner · **本版**：**§5.3 扩为追问状态机索引 · P1 批次闭合**。**承** 1.0.0-mvp。
