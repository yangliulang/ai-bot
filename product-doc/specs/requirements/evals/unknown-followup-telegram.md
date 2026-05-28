# Evals · UNKNOWN 用户追问 · GWT（构造正文）

**路径**：`specs/requirements/evals/unknown-followup-telegram.md`。  
**索引**：[`scenarios.md`](./scenarios.md) **登记行** · [`README.md`](./README.md)。

**SSOT**：[`unknown-stall-policy.md`](../risk/unknown-stall-policy.md) **§2** · [`session-concurrency-policy.md`](../domains/agent/agent-orchestration/session-concurrency-policy.md) **§5.3** · [`unknown-state.md`](../Runtime/unknown-state.md)。

---

## 1. 登记行 ↔ 本卷

| **`evalSetId`** | **Then（摘要）** | **SC** |
|-----------------|------------------|--------|
| **`eval.unknown.status_query_no_false_success`** | **504 后 `status_query`** → **reconcile/只读有界** · **0 SUCCESS 语气** | **`SC-RISK-07`** |
| **`eval.unknown.new_write_blocked_on_pending`** | **`unknown_pending` + 新写** → **0 写 · FR-T05** | **`SC-RISK-07a`** · **回归 `eval.session.new_write_blocked_on_unknown`** |
| **`eval.unknown.repeat_submit_no_auto_replay`** | **「再试一次/再买」** → **0 同参 create_order** | **`SC-RISK-07b`** |
| **`eval.unknown.cancel_request_type_a`** | **可撤 + 「取消」** → **类型 A** · **0 假撤成功** | **`SC-RISK-07c`** |
| **`eval.unknown.user_reconcile_cooldown`** | **连发 status_query** **≤ cooldown** → **reconcile 次数有界** | **`SC-RISK-07d`** |
| **`eval.unknown.copy_throttle_no_spam`** | **Throttle 窗内** **0 长模板复读** | **`SC-RISK-07e`** |
| **`eval.unknown.read_order_during_pending`** | **「查挂单」** → **只读答 + UNKNOWN 提醒** | **`SC-RISK-07`** |

**优先级**：**P1 所内 CI** — **建议** **与** **`eval.session.*`** **、** **`eval.fallback.write_504_*`** **同窗 MR**。

---

## 2. GWT · `eval.unknown.status_query_no_false_success`

```text
Given：executionId = E1 主态 unknown_pending（create_order 504 后）
  用户已收首条 UNKNOWN copy
  UNKNOWN_USER_RECONCILE_COOLDOWN_SEC = 30

When：用户 message = 「成交了吗」

Then：unknownFollowupIntent = status_query（或等价）
  且 若距上次 reconcile ≥ 30s 则 reconcile 尝试 +1 且 ≤ UNKNOWN_MAX_USER_FOLLOWUP_RECONCILE_PER_EXECUTION
  且 用户可见 0 「已买入成功/已成交完成」终局语气
  且 可含只读查单结果摘要（若工具成功）
  且 主态仍为 unknown_pending 直至对账终局（或观测终局迁移）
```

---

## 3. GWT · `eval.unknown.repeat_submit_no_auto_replay`

```text
Given：E1 unknown_pending · 原单 BNB 买入 100 USDT 已确认

When：用户 message = 「再试一次，买 100U BNB」

Then：unknownFollowupIntent = repeat_submit（或等价）
  且 0 第二条同 clientOrderRef 的自动 create_order
  且 0 新无关类型 A
  且 用户可见含勿重复提交/核对中类叙事
```

---

## 4. GWT · `eval.unknown.user_reconcile_cooldown`

```text
Given：E1 unknown_pending · lastReconcileAttemptAt = T0

When：T0+5s 用户 message = 「好了没」
  T0+10s 用户 message = 「查一下订单」

Then：T0+5s 轮 reconcile 增量 0（cooldown 内）
  且 T0+10s 轮 若仍 < 30s 则 reconcile 增量仍为 0（或仅只读 tool 无 reconcile）
  且 unknownUserReconcileCount 全程 ≤ 配置 max
```

---

## 5. GWT · `eval.unknown.cancel_request_type_a`

```text
Given：E1 unknown_pending · 交易所矩阵允许撤单 · 订单可识别为可撤

When：用户 message = 「取消上一笔」

Then：走撤单 skill 路径
  且 发出类型 A（或等价确认）— 0 无确认假撤成功 outbound
  若用户未确认 则 0 call_exchange_write 撤单成功终局
```

---

**文档版本**：0.1.0 · **维护**：产品 + QA · **本版**：**P1 首卷 — UNKNOWN 追问 GWT 束**。
