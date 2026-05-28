# Runtime Truth Source 映射（生产级闭环 · 对照表）

**路径**：`specs/requirements/Runtime/runtime-truth-source-map.md`。

**职责**：把 **「Goal → 可计费执行 → 状态 → 失败/恢复 → 记忆/上下文」** **在生产需求里的真主与缺口** **打成一张对照表**，服务 **Runtime Freeze** 评审与关单勾选。**不**新增 FR/SC 编号；**不**抄写 OpenAPI；**不**替代 **[`execution.md`](./execution.md) §1**、**[`goal-and-execution-paths.md`](../domains/agent/agent-orchestration/goal-and-execution-paths.md)** **或** **`design/`** **实现稿**。

**何时读**：评估 **「Runtime 是否可生产化」**、**「是否 Undefined Behavior 过多」**；与外部 **Runtime-Oriented Review** **对拍**。

**一致性自检清单**（跨卷勾选）→ [`runtime-consistency.md`](./runtime-consistency.md)。

---

## 1. 评审对齐摘要（与「规则散落 vs 执行图」之辩）

**已具备的 Runtime-first 骨架**（**非** **纯页面 PRD**）包括但不限于：`executionId`、`Runtime/execution` §1 **九步管线**、**`scenarioId`** **寄存器**、**`runtime-freeze`** **DAG 冻结**、**unknown-state / reconciliation**、**recovery / retry-policy**、**persistence / locking**、**confirmation-flow / ADR-001**、**kill-switch**、**计费与观测 join** — **索引** **[`overview.md`](./overview.md) §1**。

**仍易导致「研发自行拼 Runtime」**的 **残余** gaps **（** **随 MR 收口** **）**：**DAG 节点级** **全图**（**实现仓库** **冻结**）；**交易所 `code`→`stableReason`** **逐码补全**（**GitBook + 映射 MR**）；**`stableReason` 新字面** **须** **同步** **[`design/api.md`](../../design/api.md)** **附录** **与** **`runtime-error-taxonomy`**。**Memory 默认 TTL** **v0** **见** **[`design/architecture.md`](../../design/architecture.md)**。**主态迁移矩阵**、**错误 Taxonomy**、**Planner 入口**、**Memory 类型学** **已** **见** **§2** **与本目录** **§1** **地图**。**§3 写路径** **实现是否遵守** **→** **所内 Runtime 证实**；**需求侧总检** **[`closure-remaining` §7](../closure-remaining.md#cc-remaining-open-items)** · **[§7.1](../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../closure-remaining.md#cc-closure-exec-checklist)**。

---

## 2. 建议冻结项 ↔ 当前宿主（您方「01～07」类文稿映射）

| **主题（建议独立卷名）** | **当前需求 SSOT（已有）** | **缺口 / 下一冻结动作（TBD）** |
|---------------------------|---------------------------|--------------------------------|
| **Runtime State Graph / 迁移契约** | **[`execution-transition-matrix.md`](./execution-transition-matrix.md) **§2～§9（** **§2.2** **逐边 +** **§2.2→`observability` §2.4** **映射** **）**；[`runtime-invariants.md`](./runtime-invariants.md)；[`runtime-state-machine.md`](./runtime-state-machine.md)；**[`execution.md`](./execution.md) §1**；**[`execution.md` 附录 A](./execution.md)**；[`runtime-state.md`](./runtime-state.md)；[`state-machine.md`](../domains/agent/agent-orchestration/state-machine.md) | **部成/在途** **→** [`../flows/trade-via-agent.md`](../flows/trade-via-agent.md) **S5.1**；**放宽矩阵 ✗→✓** **须** **同步** **附录 A、矩阵、状态机 §3 图、不变式（若触及）、`observability` §2.4（若触及 Trigger）**；**B 抽检** **`SC-OBS08`** |
| **Goal Definition（结构化目标）** | **[`goal-and-execution-paths.md`](../domains/agent/agent-orchestration/goal-and-execution-paths.md)**（**§5～§6**）；[`domains/agent/goals/README.md`](../domains/agent/goals/README.md)（**Intent/Goal/Scenario 分相 + 评审范例**）；[`intents.md`](../domains/agent/exchange-agent/intents.md)；[`implementation-alignment.md`](../domains/agent/agent-orchestration/implementation-alignment.md) **§8** | **生产 `goal_id` 寄存器** **在** **未与** **`routing-engine`** **对签前** **不得** **升格** **为** **契约 SSOT** |
| **Workflow DAG（依赖 / 并行 / 失败边）** | **`runtime-freeze` §2～§3**（**§2.3**、**§3.1～§3.11**：**现货/全仓/合约/条件/改单**、**OCO/bracket**、**`wealth.*` 写**、**`monitoring.*` 创建/取消写**）；[`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md)；各 **`flows/*.md`** **S{n}** | **全库拓扑** **仍** **以** **实现冻结 DAG** **为终裁**（**FR-AO03**）。**矩阵延期** **行** **须** **§3.x** **已** **落笔** **再** **宣称** **对客** **闭环** |
| **Planner Contract / 边界** | **[`planner-contract.md`](./planner-contract.md)**（**§1～§8**：**`PlannerPlanEnvelope`/`PlannerPlanStep`**、**线性计划**、**§6.1 禁嵌套分支**）；**FR-AO06** · [`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4～§5**；[`tool-management/runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md) | **B**：**OpenAPI 类型名** **`design`/`openapi` 专项 MR**；**可选** **`eval.runtime.planner_plan_linear`**；**全库 DAG 拓扑** **仍** **实现冻结** |
| **Failure / Error（处置）** | **[`failure-matrix.md`](./failure-matrix.md)**；[`runtime-error-taxonomy.md`](./runtime-error-taxonomy.md)；[`recovery.md`](./recovery.md)；[`unknown-state.md`](./unknown-state.md)；[`error-normalization.md`](./error-normalization.md)；[`reconciliation.md`](./reconciliation.md)；[`retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md)；**eval** **[`evals/scenarios.md`](../evals/scenarios.md)** | **Taxonomy** **为** **分类薄层**；**字段终裁** **与** **动作表** **以** **`failure-matrix`** **为准** |
| **Memory / Context 系统** | **[`memory-runtime.md`](./memory-runtime.md)**（**§2.0 STM/LTM**、**§10～§12 召回/裁剪/自检**、**§9 `FR-MEM*`**）；[`context-management.md`](./context-management.md) **§1～§3**；[`../domains/agent/agent-context/overview.md`](../domains/agent/agent-context/overview.md)；[`persistence.md`](./persistence.md) | **热/温/冷 数值**；**Semantic 闸**；**ticker→Facts** → [`market-runtime-payload` §3.3](../domains/agent/exchange-agent/market-runtime-payload.md) |
| **Canonical Runtime Path（主链路叙事）** | **[`execution.md`](./execution.md) §1**；[`goal-and-execution-paths.md`](../domains/agent/agent-orchestration/goal-and-execution-paths.md) **§3**；[`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md) **Walkthrough**；[`architecture`「与通用 Agent 栈之对照」](../../design/architecture.md)（与 **`e2e` 文首「架构语言」** **同窗**） | **已** **有** **九步 + `e2e`**；**提升点** **在** **每条 **`scenarioId`**** **JV-11** **八维** **勾满** |
| **写路径读技能规范（Production Runtime）** | **[`skill-specs/production-runtime.md`](../skill-specs/production-runtime.md)**；[`confirmation-flow` §1](../domains/agent/agent-orchestration/confirmation-flow.md)；[`observability` §2.1 · SC-OBS11](../observability/overview.md) | **规格+Admin 原型** **已对齐**（**`exec-aa11`** 时间线）；**所内** **`read_skill_operation_spec` 真链路** → **SK-B02** / **MR-B4** |

---

## 3. Failure Matrix（索引级 · 与 field 终裁对读）

**字段终裁、`stableReason` SSOT、处置链、错误 Taxonomy** → **[`failure-matrix.md`](./failure-matrix.md)**、[`runtime-error-taxonomy.md`](./runtime-error-taxonomy.md)；**下文** **为** **高频入口** **速查**。

| **失败/异常类（产品词）** | **Runtime 动作 / 叙事宿主** |
|---------------------------|-----------------------------|
| **工具 / 网关超时、可重试错误** | [`recovery.md`](./recovery.md) **Retry**；[`retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md)；观测区分终局 vs 可重试 |
| **Risk / 门禁 / Kill 拒答** | [`execution.md`](./execution.md) **§1 步 2**；[`kill-switch.md`](../risk/kill-switch.md)；**`FR-T05`** **族** |
| **UNKNOWN / 504、终局未决** | [`unknown-state.md`](./unknown-state.md)；[`reconciliation.md`](./reconciliation.md)；**`SC-OBS03`** **同窗** |
| **队列积压、实例崩溃、可恢复** | [`execution.md`](./execution.md) **§2 队列**；[`persistence.md`](./persistence.md)；[`locking.md`](./locking.md)；**不得静默丢最终态** |
| **重复 Update / Webhook** | [`persistence.md`](./persistence.md)；[`locking.md`](./locking.md)；**`eval.runtime.telegram_update_idempotent`** |

**扩容规则**：新增一行 **须** **指向** **既有** **`Runtime/` 或 `domains/` 分卷**，**禁止** **仅** **在本表** **发明** **无宿主** **处置**。

---

## 4. 「Golden Path」 checklist（与您八问对拍）

| **问** | **需求落点** |
|--------|----------------|
| **起点** | **`execution` §1 步 1～2**；**`e2e`** **阶段**；**flows 前置** — **`goal-and-execution-paths` §6-1** |
| **终点** | **`execution` §1 步 8**；**计费 `PER_EXECUTION_FINAL`**；**UNKNOWN 口径** — **§6-8** |
| **任务完整** | **flows 主路径 + §1×flow 模板** — **§6-2** |
| **依赖** | **FR-AO01～04、DAG、`confirmation-flow`** — **§6-3** |
| **状态** | **本篇 §2 第一行**（**`execution` vs `taskId` vs `agentState`** **分维**） |
| **失败路径** | **§3 矩阵 + flows 分支** — **§6-5** |
| **恢复路径** | **recovery / reconciliation / retry** — **§6-6** |
| **人审** | **ADR-001、类型 A、HITL 矩阵** — **§6-7** |

---

## 5. 维护

- **Runtime Freeze MR**：**更新** **本篇 §2～§3** **行** **与** **版本脚注**。  
- **对外承诺**：仍以 **[`contract-closure.md`](../contract-closure.md)** **为准**。

---

**文档版本**：1.3.5 · **维护**：产品 + Agent Runtime owner · **本版**：**§2** **Planner Contract** **行** **对齐** **`planner-contract` §5～§8**。**承** 1.3.4。
