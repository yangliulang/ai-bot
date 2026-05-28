# Evals · Memory · Resume 分类器门控（GWT 正文）

**路径**：`specs/requirements/evals/resume-classifier-gate.md`。  
**登记**：[`scenarios.md`](./scenarios.md) **`eval.memory.resume_classifier_gate`** · **`SC-STM13`**。  
**SSOT**：[`memory-runtime` §14.6.3～§14.6.5](../Runtime/memory-runtime.md) · OpenAPI **`ResumeClassifierResult`** · **`RESUME_CLASSIFIER_MIN_CONFIDENCE`**。

---

## GWT · `eval.memory.resume_classifier_gate`

```text
Given：ClarifySessionSnapshot lifecycleState=stale
  WarmExecutionEpisode 含 resolvedSlotsHumanSummary「买入 BNB · 闪兑 · 缺数量」
  lastUserMessageAt 已 ≥ STM_IDLE_RESUME_PROMPT_SEC

When：Update.message.text = 「还是买 BNB，100U 闪兑」

Then：
  ResumeClassifierResult.decision = resume_prior_write（或规则层等价 · bypass 分类器）
  confidence ≥ RESUME_CLASSIFIER_MIN_CONFIDENCE（默认 0.75）
  观测 agent.memory.resume_classified（含 decision、confidence、executionId）
  merged resolvedSlotsSoFar 含 BUY/BNB/flash_convert + quoteQty 草案
  lifecycleState: stale → active · clarifyTurn 递增 · pendingClarifyKind 须 Resolver 重算
  须观测 Fresh 余额工具或 stale 声明 — 非 L0 旧 assistant 报价
  0 条 与 stale 前逐字相同的闪兑/限价模板 outbound
  0 次 silent call_exchange_write（INV-008 齐前）

When（负例 · ambiguous）：Update.message.text = 「买」

Then：
  decision = new_intent（默认 · confidence < 0.75 或未达阈）
  0 温摘要默认注入 Prompt（未过门控）

When（负例 · need_one_clarify）：Update.message.text = 「再来一笔」

Then：
  decision = need_one_clarify → 一条开放问
  0 盲续 stale 前 pendingClarifyKind 模板
  下条仍 ambiguous → 默认 new_intent
```

---

## GWT · `eval.memory.resume_classifier_need_one_clarify`（`resume_classifier_gate` 子场景）

```text
Given：lifecycleState=stale
  WarmExecutionEpisode「买入 BNB · 闪兑 · 缺数量」
  RESUME_CLASSIFIER_MODE=rules_then_llm

When：Update.message.text = 「再来一笔」

Then：
  decision = need_one_clarify
  confidence ≥ 0（可为任意 · 非 resume 阈值路径）
  outbound = 1 条开放问（须含 BNB 或「上一笔」指代 · 非 stale 前闪兑/限价模板全文）
  0 silent call_exchange_write
  观测 agent.memory.resume_classified decision=need_one_clarify

When（续）：Update.message.text = 「买」

Then：
  decision = new_intent（默认 · 仍 ambiguous）
  0 温摘要盲注入
```

---

**文档版本**：0.3.0 · **维护**：产品 + QA · **本版**：**need_one_clarify 专节 · episodePickReason**。承 0.2.0。
