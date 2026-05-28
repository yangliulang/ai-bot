# Evals · Memory · 空闲续/新（GWT 正文 · fallback）

**路径**：`specs/requirements/evals/idle-resume-or-new-topic.md`。  
**登记**：[`scenarios.md`](./scenarios.md) **`eval.memory.idle_resume_or_new_topic`** · **`SC-STM11`**。  
**SSOT**：[`memory-runtime` §14.6](../Runtime/memory-runtime.md) · **仅当 **`STM_IDLE_DEFAULT_POLICY=prompt_resume_or_new`**（**非默认**）。

---

## GWT · `eval.memory.idle_resume_or_new_topic`

```text
Given：STM_IDLE_DEFAULT_POLICY=prompt_resume_or_new
  ClarifySessionSnapshot active · pendingClarifyKind=spot_trade_mode
  lastUserMessageAt = T0

When：sleep ≥ STM_IDLE_RESUME_PROMPT_SEC
  Update.message.text = 「继续」（模糊）

Then：
  outbound 须含 cl:resume / cl:new 类型 C 二选一（inline_keyboard）
  或 明确解析为新意图 — 非过期模板逐字复读
  0 次 call_exchange_write

Note：默认策略 stale_prior_write 下本 eval 不适用 — 改用 eval.memory.idle_default_stale / resume_classifier_gate
```

---

**文档版本**：0.2.0 · **维护**：产品 + QA · **本版**：**标注 fallback-only · 非默认主路径**。**承** 0.1.0。
