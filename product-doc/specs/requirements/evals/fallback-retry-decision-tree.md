# Evals · Fallback/Retry 场景决策树 · GWT（构造正文）

**路径**：`specs/requirements/evals/fallback-retry-decision-tree.md`。  
**索引**：[`scenarios.md`](./scenarios.md) **登记行** · [`README.md`](./README.md)。

**SSOT**：[`fallback-policy.md`](../Runtime/fallback-policy.md) **§2** · [`retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md) · [`recovery.md`](../Runtime/recovery.md) · [`unknown-state.md`](../Runtime/unknown-state.md)。

---

## 1. 登记行 ↔ 本卷

| **`evalSetId`** | **Then（摘要）** | **SC** |
|-----------------|------------------|--------|
| **`eval.fallback.llm_timeout_bounded_retry`** | **LLM 超时** → **Retry ≤ 上界** → **仍失败 Stop** · **0 假类型 A** | **`SC-RT-FB-01`** |
| **`eval.fallback.provider_degrade_no_confirm_bypass`** | **主 Provider 5xx** → **备用 Provider** **可观测** · **0 确认门跳过** | **`SC-RT-FB-02`** |
| **`eval.fallback.parse_missing_slot_write_clarify`** | **写意图缺 qty** → **Clarify** · **0 write** | **`SC-RT-FB-03`** |
| **`eval.fallback.parse_missing_slot_read_clarify`** | **只读 scope 歧义** → **ReadClarify `rc:*`** | **`SC-RT-FB-04`** |
| **`eval.fallback.write_504_unknown_no_auto_replay`** | **create_order 504** → **unknown_pending** · **0 同参自动重放** | **`SC-RT-FB-05`** |
| **`eval.fallback.retry_blocks_confirmation_bypass`** | **构造 Retry 跳过类型 A** → **Stop/ blocked** | **`SC-RT-FB-06`** |
| **`eval.fallback.read_tool_retry_budget_once`** | **get_balance 超时 Retry** **计一次预算** **≤ 上界** | **`SC-RT-FB-07`** |

**优先级**：**P1 所内 CI** — **建议** **与** **`eval.session.*`** **同窗 MR** **登记**。

---

## 2. GWT · `eval.fallback.write_504_unknown_no_auto_replay`

```text
Given：用户已通过类型 A 确认 BNB 现货限价买入
  executionId = E1 · 主态 executing
  Mock 交易所 create_order 返回 HTTP 504

When：Runtime 处理 tool 结果

Then：主态迁移 unknown_pending（或等价）
  且 0 第二条同 clientOrderRef 的自动 create_order 无用户新确认
  且 用户可见含「确认中/核对中」类副本 — 0 「已买入成功」终局语气
  且 可选 reconcile_query 可观测且次数有上界
  且 SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN=true 时 新写被挡（回归 eval.session.new_write_blocked_on_unknown）
```

---

## 3. GWT · `eval.fallback.retry_blocks_confirmation_bypass`

```text
Given：executionId = E1 处于 waiting_confirmation
  类型 A 未点确认

When：Planner/Executor 因 tool 超时触发步骤级 Retry
  且 Retry 路径试图直接 call_exchange_write（无 confirmation_echo provenance）

Then：0 call_exchange_write 成功
  且 观测 confirmationBypassBlocked=true（或等价 stableReason）
  且 类型 A 仍存活或明确 expired — 用户仍须显式确认
```

---

## 4. GWT · `eval.fallback.parse_missing_slot_read_clarify`

```text
Given：用户 inbound = 「盈亏怎么样」（scope 未明）
  无 active 写澄清

When：Parser 判定 scope_portfolio_vs_market

Then：ReadClarifySession 创建或更新
  且 outbound 含 rc:* 或等价 scope 澄清 — 0 call_exchange_write
  且 0 写澄清槽位（side/qty）混入 STM 摘要
```

---

## 5. GWT · `eval.fallback.llm_timeout_bounded_retry`

```text
Given：LLM_MAX_RETRIES = 2（或 mock 等价）
  写路径 planning 阶段

When：第 1、2 次 llm_call 超时 · 第 3 次仍超时

Then：retryAttempt 可观测且 ≤ 2 后 Stop
  且 0 类型 A 卡发出
  且 fallbackDecision 终值为 stop 或 provider_fallback（若第 2 次切换）
```

---

**文档版本**：0.1.0 · **维护**：产品 + QA · **本版**：**P1 首卷 — 决策树 GWT 束**。
