# Evals · Memory · 多 execution 温索引（GWT 正文）

**路径**：`specs/requirements/evals/resume-classifier-multi-episode.md`。  
**登记**：[`scenarios.md`](./scenarios.md) **`eval.memory.resume_classifier_multi_episode`** · **`SC-STM13`**。  
**SSOT**：[`memory-runtime` §14.6.1](../Runtime/memory-runtime.md) · [`clarify-session` §2.4.3](../domains/agent/agent-orchestration/clarify-session.md) · OpenAPI **`WarmExecutionEpisode`** · **`ResumeClassifierResult.episodePickReason`**。

---

## GWT · `eval.memory.resume_classifier_multi_episode`

```text
Given：同 sessionId=S1 · lifecycleState=stale
  WarmExecutionEpisode E_old：
    executionId=E1 · staleAt=T0 · resolvedSlotsHumanSummary「买入 BTC · 闪兑 · 缺数量」
  WarmExecutionEpisode E_new：
    executionId=E2 · staleAt=T0+600s · resolvedSlotsHumanSummary「买入 BNB · 限价 · 缺价格」
  RESUME_CLASSIFIER_MODE=rules_then_llm

When（ambiguous · 无显式 symbol）：Update.message.text = 「再来一笔，100U」

Then：
  分类器输入 episode = E_new（staleAt 最近）
  观测 agent.memory.resume_classified
    episodePickReason = most_recent_stale_at
    executionId = E2
  merged 草案方向 = BNB/限价（非 BTC）
  0 盲续 E_old 之 pendingClarifyKind 模板

When（显式指代 E_old）：Update.message.text = 「还是刚才那个 BTC，100U 闪兑」

Then：
  规则层 bypass 分类器 或 decision=resume_prior_write
  executionId = E1
  episodePickReason = explicit_reference_match（或 rules_bypass）
  merged 含 BTC/flash_convert

When（负例 · 两条均过期）：E_old/E_new expiresAt < now

Then：
  0 温摘要默认注入 Prompt
  decision = new_intent
```

---

**文档版本**：0.1.0 · **维护**：产品 + QA。
