# Risk · 验收（`SC-RISK*`）

**路径**：`specs/requirements/risk/acceptance.md`。

**职责**：**运营闸与数值护栏** 的 **横切抽检口径**。**类型 A / `SC-TA*`** → [`../domains/agent/agent-orchestration/confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md)、[`../domains/agent/exchange-agent/trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md)；**结构化事件字段** → [`../observability/overview.md`](../observability/overview.md)。

**通则**：`SC-RISK*` **不替代** 域内 **`FR-T09` / `FR-T11` / `FR-T05`** 条文。**违例** 默认 **契约或发布阻断**；若剪裁 **须** 书面登记并 **在** [`../contract-closure.md`](../contract-closure.md) **脚注** 可检索。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. `SC-RISK*` 表

| ID | 陈述（下限） | 抽检 / DoD |
|----|----------------|------------|
| **SC-RISK-01** | 当 **`GLOBAL_AGENT_SWITCH=OFF`**、**`OPS_GLOBAL_AGENT_PAUSE`** 有效、或 **用户意图为某产品线写** 而对应 **`FEATURE_AGENT_*`** 关闭时：**不得** 出现 **成功的交易所私有写终态**（含 HTTP 2xx 且业务判成功）**却** 无用户侧 **`FR-T05` 族** 等价可读摘要与归因线索 | **≥3** 构造场景（建议 **现货写 / 合约或杠杆写 / 理财写** 各 ≥1），或 **书面豁免**；归因 **须** 指向 **`agentState`** 或 **配置快照** 之一（字段名 **`design`/OpenAPI** 冻结） |
| **SC-RISK-02** | **实例级 Pause**（`RUNTIME_PAUSE` 或同窗码）生效时，**该实例** 新写 **满足** 与 SC-RISK-01 **相同的否定式结论**。**OPS 全局** 与 **实例 Pause** 同时生效时，用户可见说明 **须** 可区分两层原因 | **同窗** [`../domains/admin/agent-management/rules.md`](../domains/admin/agent-management/rules.md) **§3**；**≥1** 双闸构造用例 |
| **SC-RISK-03** | **`SYMBOL_*`** 或 **`PRICE_REJECTED_AGENT_BAND`** 拦截时：**不得** 调用矩阵 **`R/W=W`** PATH；用户侧语义 **须** 与 [`boundaries` §2](../domains/agent/exchange-agent/boundaries.md) 或 **相关** `flows` 专节 **一致** | **≥2** 用例（**越权 symbol**、**限价越偏离带** 各 ≥1） |
| **SC-RISK-04** | **[`keys` §3](../domains/admin/trading-agent-config/keys.md)** 已登记之 **`AGENT_*` 敞口/集中度/会话亏损/冷却/高频窗/大额阈** 等，在 **命中构造** 下：**不得** 静默成交；**须** 可读拒答或与产品冻结一致的 **降参/澄清** 路径 | **发布前** **须** 有一份 **覆盖矩阵**（**每键** 至少 **0 或 1** 构造用例，**0** 须 **书面排除**） |
| **SC-RISK-05** | **`GLOBAL_AGENT_SWITCH` 切换**、**`OPS_GLOBAL_AGENT_PAUSE` 切换**、**清空 `SYMBOL_ALLOWLIST`** 等高危编辑 **须** 落 **`admin.audit`**（diff、`configSnapshotId` 或等价），与 [`trading-agent-config/flow` §1](../domains/admin/trading-agent-config/flow.md) 二次确认叙事 **一致** | **抽检** ≥1 条审计流水可 **回放** 至操作者与前后值 |
| **SC-RISK-06** | **`504`/UNKNOWN** **致** **Runtime** **`unknown_pending`** **停留** **超过** [`unknown-stall-policy.md`](unknown-stall-policy.md) **§1** **所冻结** **无进展阈值 Δt**：**须** **存在** **可观测告警**（**或** **`design` 冻结** **之** **等价升级路径**）；**用户侧** **须** **可得** **`FR-T05` 族** **可读状态**（**不** **假终局成交**）；**禁止** **无退避、无轮次上界** **的** **查单热循环** **单独** **充当** **「处置」** | **同窗** [`evals/scenarios.md`](../evals/scenarios.md) **`eval.runtime.unknown_stall_resolution`**；**≥1** **构造用例** **或** **书面豁免**（**豁免须** [`contract-closure`](../contract-closure.md) **可检索**）。**溯源** **建议** **拼接** [`observability/overview.md`](../observability/overview.md) **§2.4 · `SC-OBS08`** **之** **`executionId` 时间线**（**与** **矩阵** **[`execution-transition-matrix.md`](../Runtime/execution-transition-matrix.md) **§2.2** **对读**）**—** **不** **弱化** **本条** **Δt** **判据** |
| **SC-RISK-07** | **`unknown_pending` 存活期间** **用户追问 inbound** **须** **按** [`unknown-stall-policy` §2](unknown-stall-policy.md) **分类处置**：**`status_query`/只读** **→** **有界 reconcile + 0 SUCCESS 假终局**；**`new_write`/`repeat_submit`** **→** **0 新写/0 同参自动重放**（**D-1 默认**）；**`cancel_request`（可撤）** **→** **类型 A 撤单** **0 假撤成功**；**用户触发 reconcile** **须** **cooldown + 次数上界** | **`eval.unknown.*`** · **回归** **`eval.session.new_write_blocked_on_unknown`** · **`eval.fallback.write_504_unknown_no_auto_replay`**；**≥1** **GWT** [`unknown-followup-telegram.md`](../evals/unknown-followup-telegram.md) **或** **书面豁免** |

---

## 2. 互引

| 文档 | 关系 |
|------|------|
| [`kill-switch.md`](kill-switch.md) | SC-RISK-01 / 02 / 05 **叙事宿主** |
| [`symbol-restriction.md`](symbol-restriction.md) | SC-RISK-03 **部分** |
| [`exposure-limit.md`](exposure-limit.md) | SC-RISK-04 **部分** |
| [`../contract-closure.md`](../contract-closure.md) **§4、§7** | 矩阵解冻 MR 与护栏变更 **同窗核对** |
| [`unknown-stall-policy.md`](unknown-stall-policy.md) | **SC-RISK-06** **阈值与键语义宿主** · **SC-RISK-07** **追问状态机 §2** |

---

**文档版本**：0.2.2 · **维护**：产品 + 风控/QA owner · **本版**：**SC-RISK-07** **UNKNOWN 追问状态机 DoD**。**承** 0.2.1。
