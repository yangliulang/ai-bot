# Evals · Session 并发 · GWT（构造正文）

**路径**：`specs/requirements/evals/session-concurrency.md`。  
**索引**：[`scenarios.md`](./scenarios.md) **登记行** · [`README.md`](./README.md)。

**SSOT**：[`session-concurrency-policy.md`](../domains/agent/agent-orchestration/session-concurrency-policy.md) · [`clarify-session.md`](../domains/agent/agent-orchestration/clarify-session.md) · [`locking.md`](../Runtime/locking.md)。

---

## 1. 登记行 ↔ 本卷

| **`evalSetId`** | **Then（摘要）** | **SC** |
|-----------------|------------------|--------|
| **`eval.session.inbound_serial_no_double_parse`** | **1s 内连发 2 条不同 text** → **≤1 完整 Parser 链或 coalesce 可观测** | **`SC-AO-09`** |
| **`eval.session.single_active_write_execution`** | **任意时刻** **在途写 execution ≤1** | **`SC-AO-10`** |
| **`eval.session.second_write_while_clarify`** | **写澄清 active + 新 symbol 写** → **abandon 旧或挡 + 仅 1 活跃写澄清** | **`SC-AO-10`** |
| **`eval.session.second_write_while_confirm`** | **类型 A 存活 + 新写** → **0 第二张无关类型 A + 可读挡新写** | **`SC-AO-10a`** |
| **`eval.session.new_write_blocked_on_unknown`** | **`unknown_pending` + 新写（默认 config）** → **0 新写 + FR-T05 族** | **`SC-AO-10b`** |
| **`eval.session.amend_chain_blocks_parallel_write`** | **逻辑改单 cancel 已发 + 同 symbol 新写** → **挡或 abort 后可写** | **`SC-AO-10c`** |
| **`eval.session.read_during_write_clarify`** | **写澄清 + 只读问句** → **只读答 + 写澄清 abandoned** | **`SC-CLARIFY-07`**（**回归**） |
| **`eval.session.callback_serial_with_message`** | **in-flight 处理 message 时到达 `cl:*`** → **串行、槽位一致** | **`SC-AO-09`** |

**优先级**：**P0 所内 CI** — **上表全行** **与** **`eval.memory.stm_governance_regression`** **同窗 MR** **登记**。

---

## 2. GWT · `eval.session.inbound_serial_no_double_parse`

```text
Given：用户已绑定 · sessionId = S1
  SESSION_INBOUND_QUEUE_POLICY = serial_per_session

When：T0 用户 message = 「买入 BNB」
  T0+200ms 用户 message = 「100 USDT」
  （同一 Webhook 批次或快速连发）

Then：观测 Parser/意图 完整链 次数 ≤ 1（或 coalescedCount=2 且单次处理）
  且 最终 resolvedSlotsSoFar 含 side=BUY · base=BNB · quoteQty=100（或等价澄清后合并）
  且 0 条互相矛盾的并发 outbound（如同时闪兑+限价各一问）
  且 sessionQueueDepth 峰值 ≤ SESSION_INBOUND_QUEUE_MAX_DEPTH
```

---

## 3. GWT · `eval.session.second_write_while_confirm`

```text
Given：sessionId = S1 · executionId = E1 处于 waiting_confirmation
  类型 A 卡已发（BNB 买入 100 USDT）

When：用户 message = 「算了，改买 ETH」

Then：0 第二张无关 symbol 的类型 A 直接发出
  且 用户可见含「待确认」或等价提示（须先确认/取消）
  或 观测 pending_confirm consumed/expired 后再起 E2 写 ETH
  且 同一时刻 activeWriteExecutionId 至多 1 个写路径
```

---

## 4. GWT · `eval.session.new_write_blocked_on_unknown`

```text
Given：executionId = E1 主态 unknown_pending（504 后）
  SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN = true

When：用户 message = 「再帮我买 0.1 BTC」

Then：0 新 call_exchange_write
  且 用户可见 FR-T05 族（上一笔结果待确认/查单）
  且 可选只读 tool 查订单/持仓 可观测
```

---

## 5. GWT · `eval.session.amend_chain_blocks_parallel_write`

```text
Given：用户已确认 trade.spot.amend_limit_order
  cancel 已 POST · order 尚未终局 · executionId = E1 executing

When：用户 message = 「不买 BNB 了，改买 SOL」

Then：0 并行第二笔 spot 写 call_exchange_write
  且 concurrencyDecision = blocked_new_write 或 planAborted 后可新起
  且 用户可见区分「改单进行中」vs「新下单」
```

---

## 6. GWT · `eval.session.callback_serial_with_message`

```text
Given：写澄清 active · 键盘 闪兑/限价 已展示
  Parser 正在处理用户 text inbound（in-flight）

When：同一 session 到达 callback_query cl:fc

Then：callback 处理 在 message 链完成后 或 互斥锁内串行
  且 resolvedSlotsSoFar 无 lost update（BNB/BUY 保留 + tradeMode=flash_convert）
  且 clarifyTurn 单调递增
```

---

**文档版本**：1.0.0-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**P0 eval 束**。
