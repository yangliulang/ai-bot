# Evals · Memory · 空闲默认 stale（GWT 正文）

**路径**：`specs/requirements/evals/idle-default-stale.md`。  
**登记**：[`scenarios.md`](./scenarios.md) **`eval.memory.idle_default_stale`** · **`SC-STM12`**。  
**SSOT**：[`memory-runtime` §14.6](../Runtime/memory-runtime.md) · [`clarify-session` §2.4](../domains/agent/agent-orchestration/clarify-session.md)。

---

## GWT · `eval.memory.idle_default_stale`

```text
Given：ClarifySessionSnapshot lifecycleState=active
  pendingClarifyKind=spot_trade_mode
  resolvedSlotsSoFar={ side:BUY, baseAsset:BNB }
  lastUserMessageAt = T0

When：sleep ≥ STM_IDLE_RESUME_PROMPT_SEC（或 fixture 快进）
  且 Update.message.text = 「你好」

Then：
  snapshot.lifecycleState = stale（staleAt 可观测）
  Prompt 活跃 L1 不含 pendingClarifyKind / 写澄清摘要
  outbound 寒暄 · snapshot.abandoned=true · lifecycleState=abandoned
  0 闪兑/限价写澄清
  0 处 routing/写路径内部词
  宜含非阻塞 idle 提示（§2.8.6 · 可选断言）
  0 次 call_exchange_write
```

---

**文档版本**：0.2.0 · **维护**：产品 + QA · **本版**：**stale 后寒暄 → abandoned**。承 0.1.0。
