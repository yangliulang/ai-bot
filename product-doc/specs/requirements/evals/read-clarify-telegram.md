# Evals · 只读澄清 · GWT（构造正文）

**路径**：`specs/requirements/evals/read-clarify-telegram.md`。  
**索引**：[`scenarios.md`](./scenarios.md) · [`README.md`](./README.md)。

**SSOT**：[`read-clarify-session.md`](../domains/agent/agent-orchestration/read-clarify-session.md) · [`read-analyze-and-search-via-agent.md`](../flows/read-analyze-and-search-via-agent.md) **S2**。

---

## 1. 登记行 ↔ 本卷

| **`evalSetId`** | **Then（摘要）** | **SC** |
|-----------------|------------------|--------|
| **`eval.read_clarify.multi_symbol_compare`** | **「BTC 和 ETH 哪个涨得多」** → **收敛后一次工具+答复** | **`SC-READ-CLARIFY-04`** |
| **`eval.read_clarify.scope_portfolio_vs_market`** | **「盈亏怎么样」** → **scope 澄清** · **portfolio 路径 FR-T02** | **`SC-READ-CLARIFY-06`** |
| **`eval.read_clarify.write_interrupts_read`** | **只读澄清中「买 100U BNB」** → **abandon 读 · 转写澄清** | **`SC-READ-CLARIFY-02`** |
| **`eval.read_clarify.rc_no_exchange_write`** | **点 `rc:scope:portfolio`** → **0 写** | **`SC-READ-CLARIFY-01`** |
| **`eval.read_clarify.reintent_each_inbound`** | **澄清态新 inbound** → **重跑意图 · 非复读** | **`SC-READ-CLARIFY-05`** |
| **`eval.read_clarify.monitoring_draft_then_type_a`** | **到价提醒草案齐** → **创建监控须独立类型 A** | **`SC-READ-CLARIFY-07`** |
| **`eval.read_clarify.abandon_on_cancel`** | **「不用了」** → **abandoned · 0 复读** | **`SC-READ-CLARIFY-02`**（**放弃支**） |

**优先级**：**P1** — **所内 CI** **建议** **与** **P0 `eval.session.*`** **同窗 MR**。

---

## 2. GWT · `eval.read_clarify.scope_portfolio_vs_market`

```text
Given：用户已绑定子账户 · FR-T02 通过
  sessionId = S1

When：用户 message = 「盈亏怎么样」
  且 首轮 pendingReadClarifyKind = scope_portfolio_vs_market

Then：outbound 含 scope 澄清（市场 vs 我的持仓）或 rc:scope:* 键盘
  且 0 call_exchange_write
  用户点 rc:scope:portfolio 后
  观测 tool.portfolio.* 或等价只读链
  且 答复不含未拉取的持仓数字
```

---

## 3. GWT · `eval.read_clarify.write_interrupts_read`

```text
Given：ReadClarifySession active
  pendingReadClarifyKind = multi_symbol_compare
  0 写 ClarifySession active

When：用户 message = 「算了直接买 100U 的 BNB」

Then：ReadClarifySession.abandoned = true
  且 观测写路径 Parser/澄清或 trade 路由
  且 0 条仍追问「BTC 还是 ETH 涨得多」
```

---

## 4. GWT · `eval.read_clarify.monitoring_draft_then_type_a`

```text
Given：用户 message = 「BTC 涨到 10 万提醒我」

When：经 rc:mon:spot + symbol 澄清 槽位齐

Then：0 在只读澄清阶段 call_exchange_write
  且 创建 monitoring 任务前 观测 confirmation.required 或类型 A 卡
  且 taskId/写 execution 与只读 read execution 可区分归因
```

---

**文档版本**：1.0.0-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**P1 eval 束**。
