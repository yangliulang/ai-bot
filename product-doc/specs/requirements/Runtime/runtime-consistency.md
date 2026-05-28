# Runtime · 一致性自检（Consistency）

**路径**：`specs/requirements/Runtime/runtime-consistency.md`。

**职责**：汇总 Runtime 跨文档须同时成立的约束与易混点，供 MR / 实现评审勾选。不新增 FR/SC；条目不替代各卷正文。

**总索引**：[`runtime-truth-source-map.md`](./runtime-truth-source-map.md) · [`boundaries.md`](./boundaries.md)。

---

## 1. 主态与迁移（`executionId`）

| 检查 | 真主 |
|------|------|
| 主态词字面一致 | [`execution.md`](./execution.md) 附录 A（SSOT）；[`runtime-state-machine.md`](./runtime-state-machine.md) §2 须与之逐字一致 |
| 允许迁移以谁为准 | [`execution-transition-matrix.md`](./execution-transition-matrix.md) **§2** **格** + **§2.2** **逐边表**（**Trigger·Authority·Guard·副作用·计费**）；[`runtime-state-machine.md`](./runtime-state-machine.md) **§3** 图与 **§2** **对齐** |
| **Trigger→观测 / 时间线** | [`observability/overview.md`](../observability/overview.md) **§2.4**、**`SC-OBS08`**；**控制台** **`SC-OM-04`** — [`observability-management/functions.md`](../domains/admin/observability-management/functions.md)；**OpenAPI** `ObservabilityTimelineEvent.transitionTrigger` |
| 部成/在途不抬主行 | [`trade-via-agent.md`](../flows/trade-via-agent.md) S5.1 与附录 A 约束 |

---

## 2. 计费词 vs Runtime 主态

| 检查 | 说明 |
|------|------|
| `consume-and-bill` 之「accepted」 | 指可计费路径起票时分配 `executionId` 的产品叙事，与附录 A 主态 `accepted` 在起票瞬间同窗；附录 A 的 `accepted` 还覆盖其后管线未离终局的过程。 |

---

## 3. 错误与恢复

| 检查 | 真主 |
|------|------|
| `stableReason` 字面 + Taxonomy | [`design/api.md`](../../design/api.md) 附录；[`runtime-error-taxonomy.md`](./runtime-error-taxonomy.md)（Taxonomy 为类层；对外字面以 api 附录为准） |
| 处置动作表 | [`failure-matrix.md`](./failure-matrix.md) §2 |
| `exchangeOutcome=unknown` 不得冒充成功 | [`design/architecture.md`](../../design/architecture.md)、[`observability/overview.md`](../observability/overview.md) §2.2 |
| 工具重试 ≠ 主态从终局回退 | [`execution-transition-matrix.md`](./execution-transition-matrix.md) §3；[`retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md) |

---

## 4. Memory 与留存

| 检查 | 真主 |
|------|------|
| 热/温/冷 v0 | [`design/architecture.md`](../../design/architecture.md) Memory 留存；[`memory-runtime.md`](./memory-runtime.md) |
| 观测 §3 与 180d | [`observability/overview.md`](../observability/overview.md) §3 — 温层 ≥30d 与审计 ≥180d 取更长作对外承诺须 MR |

---

## 5. 已知 gap（非笔误，待工程收口）

| 项 | 动作 |
|----|------|
| **`stableReason` 进 observability 结构化 schema** | **[`design/architecture.md`](../../design/architecture.md)** **「观测事件 `stableReason`」**；**OpenAPI** `observability-schemas.yaml` **MR** **须** **与** [`design/api.md`](../../design/api.md) **附录 · Taxonomy**、[`observability/overview.md`](../observability/overview.md) **§2.2** **同窗** |
| **DAG 全图（实现终裁）** | **实现仓库** **与** [`runtime-freeze`](../domains/agent/agent-orchestration/runtime-freeze.md) **§2**；**产品侧** **九步** [`execution.md`](./execution.md) **§1**；**已承诺** **写路径** **最小编排** → **`runtime-freeze` §3**（**现货/全仓/合约/条件/改单/OCO/bracket**、**理财写**、**监控任务创建/取消**） |
| **UNKNOWN Δt / 键名落地** | [`../risk/unknown-stall-policy.md`](../risk/unknown-stall-policy.md) **§1** **→** **`keys.md` / `ai-settings` MR**；**评测** [`../evals/scenarios.md`](../evals/scenarios.md) **`eval.runtime.unknown_stall_resolution`** |

---

## 6. 八维深度自检（迁移完整度 · 权威 · 不变式 · 收口）

**用途**：实现 / 架构评审逐项勾选；**真主**见右列。**下列维度** **已** **在** **`locking` / `unknown-state` / `event-storage` / `persistence` / `recovery`** **补** **产品下限**；**数值键名 / 服务 RACI 细则** **仍** **`design` + 域 MR**。

| **维** | **结论摘要** | **真主 / 剩余工程宿主** |
|--------|--------------|-------------------------|
| **1 · Transition Completeness** | **§2.2** **逐边** **冻结**；**捷径** **仅** **✓†**。 | [`execution-transition-matrix`](./execution-transition-matrix.md) **§2～3**；[`runtime-state-machine`](./runtime-state-machine.md) |
| **2 · Transition Authority** | **§2.2 Authority** **列** + **§4** **总则**；**持久化** **仅宿主**。 | **同上** **§2.2**；[`locking.md`](./locking.md) **§2** |
| **3 · Runtime Invariants** | **INV-001～010**。**写参完备/血缘** → **§0、INV-008～010**。 | [`runtime-invariants.md`](./runtime-invariants.md)；[`execution-transition-matrix`](./execution-transition-matrix.md) **§7～8** |
| **4 · Unknown 收口** | **可观测** **推进 vs 卡死**；**须** **对账终局 / 超时终局 / 人工处置** **之一**；**阈值** **条文** [`unknown-stall-policy`](../risk/unknown-stall-policy.md)；**抽检** **`SC-RISK-06`**。 | [`unknown-state`](./unknown-state.md)；[`recovery`](./recovery.md)；[`reconciliation`](./reconciliation.md) **§2**；[`acceptance`](../risk/acceptance.md)；[`evals/scenarios`](../evals/scenarios.md) **`eval.runtime.unknown_stall_resolution`** |
| **5 · Replay vs Retry** | （不变） | [`runtime-contract`](../domains/admin/tool-management/runtime-contract.md) **§3**；[`execution-lifecycle`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4.1**；[`persistence`](./persistence.md) |
| **6 · Event 驱动** | **主态迁移** **须** **在保留期内** **可由** **步骤事件 / 显式迁移事件 / 检查点链** **之一复原**；**禁止** **长期无法互证**。**时间线** **还须** **可对签** **§2.4 · `transitionTrigger`**（**`SC-OBS08`**）。 | [`event-storage`](./event-storage.md) **§2·主态迁移之可证明性**；[`observability/overview`](../observability/overview.md) **§2～§2.4**；**评测** [`evals/scenarios`](../evals/scenarios.md) **`eval.obs.timeline_transition_contract`**；**事件名载荷** → **`observability-schemas`** |
| **7 · Settlement / Billing** | （不变） | [`billing-management/rules`](../domains/admin/billing-management/rules.md)；[`consume-and-bill`](../flows/consume-and-bill.md) **S3～S5**；[`execution`](./execution.md) **§1 步 8** |
| **8 · Crash Recovery** | **检查点放置** **相对** **主态迁移与 504/UNKNOWN** **+** **关停**；**DAG 节点映射** **runtime-freeze**。 | [`persistence`](./persistence.md) **§2·检查点放置**；[`runtime-state-machine`](./runtime-state-machine.md) **§5**；[`failure-matrix`](./failure-matrix.md) **§2**；[`locking`](./locking.md) |

---

## 7. 流程体验与用户副本（抽检 · 2026-05 增补）

**用途**：落实 **「卡点可解释 + 在途/UNKNOWN 不冒充终局」**；**不新增 FR/SC**。**发版 / 大 MR** **建议** **至少** **抽检** **其一**：[`evals/scenarios.md`](../evals/scenarios.md) **`eval.runtime.user_visible_phase_copy`**、**`eval.trade.slot_quote_base_clarify`**；**旅程** [`product/journey-validation.md`](../../../product/journey-validation.md) **JV-12**。

| **检查** | **真主** |
|----------|----------|
| **用户可见阶段** **与** **附录 A / MC801** **不矛盾** | [`telegram/overview.md`](../domains/agent/telegram/overview.md) **§3.1**；[`trade-via-agent.md`](../flows/trade-via-agent.md) **S5.1.1**；[`unknown-state.md`](./unknown-state.md) **用户可见副本下限** |
| **类型 A 字段** **与** **提交 API** **可对账** | [`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md)；[`design/api.md`](../../design/api.md) **矩阵**；**抽检** **JV-12** **Then** **b** |
| **槽位歧义（quote/base）** **澄清** **不** **静默下单** | [`trade-via-agent.md`](../flows/trade-via-agent.md) **S6**；[`routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)；**`eval.trade.slot_quote_base_clarify`** |

---

**维护**：产品 + Agent Runtime owner · **文档版本**：1.1.2 · **本版**：**INV-008～010** **自检表**。**承** 1.1.1。
