# Runtime · Planner Contract（编排入口）

**路径**：`specs/requirements/Runtime/planner-contract.md`。

**职责**：作为 **Planner 行为契约** **的** **横切入口**（**可审表** **与** **互引**），避免 **LLM Runtime** **与** **`scenarioId`/确认门/预算** **脱节**。**条文真源** **不** **重复** **抄写** — **以** **域内分卷 + 设计冻结** **为准**。**契约开放面 / 走读缺口** → [`closure-remaining` §7](../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../closure-remaining.md#cc-closure-exec-checklist)**。

**本版增量（§5～§8）**：冻结 **Planner 输出形态** 与 **V1 控制流下限**，降低 **实现仓各自解释 ReAct/隐式 DAG** 之漂移；**OpenAPI 字段名** **仍** **由** **`design` 专项 MR** **收束**（**§7**）。

---

## 1. 能做什么（摘要）

| **能力** | **宿主** |
|----------|----------|
| **在** **`FR-AO06`** **内** **选择** **已登记** **工具与编排步** | [`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4**；[`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) |
| **在** **不篡改** **用户已确认写意图** **前提下** **`can_replan`（有界）** | [`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§5.1**；[`runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md) **§1** |
| **遵守** **`orchestrationVersion` / DAG** **冻结与可观测** | [`runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md) **§2～§3**（**§3.1～§3.11** **写** **路径** **下限**） |
| **状态机主态** **不** **从** **终局** **非法回退** | [`runtime-state-machine.md`](./runtime-state-machine.md)；[`execution-transition-matrix.md`](./execution-transition-matrix.md)；**逐边 Trigger→观测** [`observability/overview.md`](../observability/overview.md) **§2.4** |
| **产出** **§5** **之** **可审计计划信封** **并** **按序物化** **`agent.orchestration.step`** | **本篇 §5～§6**；[`observability/overview.md`](../observability/overview.md) **§2.1** |

---

## 2. 禁止做什么（`forbidden_actions`）

**详表** → [`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§5.2**（**bypass_confirmation**、**skip_risk_or_kill_gate**、**emit_nested_conditional_plan** **等**）。

---

## 3. 深度与配置

**`max_depth` / `max_replan` / 默认数值** → **`design`/OpenAPI** **冻结**；**需求下限** → **§5.1**（**有硬顶** **且** **可观测**）。**计划步数硬顶** **与** **`maxOrchestrationStepsPerExecution`** **同窗** — [`design/api.md`](../../design/api.md) **AI Settings · 编排执行预算**。

---

## 4. 工具与调用契约

**工具运行时边界**（**重试计数** **等**）→ [`admin/tool-management/runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md)。

**Planner 不替代工具契约**：**`toolId`** **须** **登记**；**写路径** **参数** **执法** **仍** **以** [`runtime-invariants.md`](./runtime-invariants.md) **INV-008～010** **与** **`eval.gateway.*`** **为准** — [`evals/scenarios.md`](../evals/scenarios.md)。

---

## 5. Planner 输出形态（产品下限 · V1）

**目的**：同一 **`executionId`** **内**，编排宿主 **须** **能** **回答**「**Planner 本回合打算做什么、顺序如何、与已登记工具是否一致**」，**不** **依赖** **日志反推隐式 ReAct 环**。

### 5.1 计划信封（`PlannerPlanEnvelope` · 逻辑名）

**每一** **编排回合**（**含** **首次规划** **与** **`can_replan` 补步**）**须** **在** **执行前或同步** **落盘/发射** **等价结构**（**所内 JSON Schema / OpenAPI 收束** — **§7**）：

| **字段（逻辑）** | **须（MUST）** | **说明** |
|------------------|----------------|----------|
| **`executionId`** | ✓ | **与** **起票** **一致** |
| **`scenarioId`** | ✓ | **与** [`routing-engine`](../domains/agent/agent-orchestration/routing-engine.md) **路由结果** **一致** |
| **`orchestrationVersion`** | ✓ | **同窗** [`runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md) |
| **`planRevision`** | ✓ | **单调整数**；**每次** **`can_replan`** **产出** **新修订** **须** **递增** |
| **`steps`** | ✓ | **有序数组**；**见** **§5.2** |
| **`planKind`** | 推荐 | **`initial` \| `replan`** — **便于** **审计** **区分** **首规划** **与** **补步** |

### 5.2 计划步（`PlannerPlanStep` · 逻辑名）

**`steps[]`** **每一项** **须** **至少** **包含**：

| **字段（逻辑）** | **须（MUST）** | **说明** |
|------------------|----------------|----------|
| **`stepId`** | ✓ | **在** **本** **`planRevision`** **内** **唯一**；**稳定** **可引用**（**观测** **`stepSeq`** **映射** **见** **§6.3**） |
| **`stepKind`** | ✓ | **枚举** **见** **§5.3** |
| **`toolId`** | 条件 | **`stepKind=tool_call`** **时** **必填**；**须** **为** **登记工具** |
| **`dependsOn`** | 可选 | **`stepId[]`**；**仅** **表达** **顺序依赖**（**见** **§6.1**） |
| **`inputRef`** | 推荐 | **指向** **槽位/只读结果/确认回显** **之** **逻辑引用**（**非** **明文 Secret**）；**写参经济字段** **不得** **仅** **存在于** **`inputRef`** **而无** **`provenance`** **链** — **同窗** **INV-009** |

**禁止** **在** **`steps[]`** **内** **嵌入** **任意代码、SQL、或未登记** **`toolId`**。

### 5.3 `stepKind` 枚举（V1 · 封闭集）

| **`stepKind`** | **含义** | **Runtime 物化** |
|----------------|----------|------------------|
| **`gate`** | **风险/配置/Kill** **等** **门禁**（**无** **外网写**） | **`agent.orchestration.step`** **`stepKind=gate`** **或** **等价** |
| **`read_skill_spec`** | **写路径** **`read_skill_operation_spec`** | **须** **早于** **含** **交易所写** **之** **`tool_call`** — **SC-OBS11** |
| **`slot_fill`** | **槽位补全/校验**（**FR-T07**） | **可** **与** **模型回合** **交织** **但** **须** **可观测** |
| **`confirm_gate`** | **类型 A / 确认门** | **对齐** [`confirmation-flow`](../domains/agent/agent-orchestration/confirmation-flow.md) |
| **`tool_call`** | **登记工具调用**（**含** **只读** **与** **写**） | **`agent.tool.call`** + **编排步** |
| **`terminal_narrative`** | **用户可见终局话术**（**无** **新写**） | **须** **满足** **终局可采信** — **禁** **`assert_exchange_terminal_before_truth`** |

**扩容** **新** **`stepKind`**：**须** **MR** **同步** **本篇**、[`observability/overview.md`](../observability/overview.md) **§2.4**（**若** **新** **Trigger**）、[`runtime-truth-source-map.md`](./runtime-truth-source-map.md) **§2**。

### 5.4 与「模型自然语言计划」之分

- **允许** **模型** **输出** **自然语言摘要** **供** **用户阅读**；**但** **编排宿主** **对外** **承诺** **之** **工具顺序** **以** **`PlannerPlanEnvelope`** **为准**。  
- **禁止** **仅** **依赖** **模型** **口头** **「我将调用 X」** **而无** **§5.1** **结构** **即** **触发** **`call_exchange_write`**。

---

## 6. 控制流与再规划（V1 下限）

### 6.1 线性计划 · 禁止嵌套条件 DAG（产品）

- **V1** **`steps[]`** **须** **为** **单一有序列表**；**依赖** **仅** **通过** **`dependsOn`** **表达** **先后**（**无环** **须** **在** **落盘前** **校验** **或** **拒收计划** — **同窗** **`FR-AO06.2`**）。  
- **禁止** **在** **计划** **内** **嵌入** **`if/else`/`switch`/`parallel_fork`** **等** **嵌套控制流节点** **作为** **Planner 一等输出**（**标识** **`emit_nested_conditional_plan`** — **§5.2 禁忌表**）。  
- **需要** **分支**（**如** **市价/限价** **二选一**）**须** **在** **路由层** **收敛为** **不同** **`scenarioId`** **或** **用户显式选择** **后** **再** **起** **新** **`planRevision`**，**而非** **单计划内动态分支**。  
- **例外**：**须** **独立 ADR** **并** **同步** [`runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md) **§2.1**、**本篇**、**矩阵**（**若** **触及** **主态**）。

### 6.2 `can_replan` 与写意图

- **再规划** **仅** **允许** **追加/重排** **尚未** **触及** **用户已确认写包** **之** **步骤** **或** **只读/澄清步** — **同窗** **§5.1** **与** [`execution-lifecycle` §5.1](../domains/agent/agent-orchestration/execution-lifecycle.md)。  
- **禁止** **用** **`replan`** **替换** **已确认** **之** **经济敏感字段**（**INV-003/008** **仍** **适用**）。

### 6.3 物化与观测

- **每** **执行** **一步** **须** **发射** **`agent.orchestration.step`**（**或** **合并事件** **之** **等价键**）**且** **携带** **`stepId`/`stepSeq`/`stepKind`/`scenarioId`/`orchestrationVersion`** — [`observability/overview.md`](../observability/overview.md) **§2.1**。  
- **计划拒收**（**未登记工具、环、超步数、嵌套分支**）**须** **`plan.abort`** **或** **等价** **且** **映射** **`FR-T05`/`ORCHESTRATION_BUDGET_EXCEEDED`** **族** — **同窗** **INV-004**。

---

## 7. B 阶段收束（OpenAPI · 实现 · 不阻塞 A 阶段评审）

| **交付** | **宿主** | **说明** |
|----------|----------|----------|
| **JSON Schema / OpenAPI 类型** | **`design` 或 `openapi/components/` 专项 MR** | **字段名** **以** **所内登记** **为准**；**语义** **不得** **弱于** **§5～§6** |
| **编排宿主校验器** | **所内 Runtime 实现** | **拒收** **§6.1** **违例计划**；**计数** **纳入** **`FR-AO06`** |
| **可选 Eval** | [`evals/scenarios.md`](../evals/scenarios.md) | **`eval.runtime.planner_plan_linear`**（**草案 ID** — **B** **落地** **时** **登记** **构造** **与** **`SC-AO-*`** **映射**） |

**A 阶段（本 MR）**：**需求** **已** **可评审** **§5～§6**；**不** **宣称** **Hosted/OpenAPI** **已发布**。

---

## 8. MR 检查清单（粘贴块）

```text
Planner Contract MR
- [ ] planner-contract.md §5～§8 与 execution-lifecycle §5.2 新增禁忌对读
- [ ] runtime-truth-source-map §2「Planner Contract」行已更新
- [ ] product/roadmap.md TL;DR 或 L1 快照已择要补丁
- [ ] 未引入与 domains 矛盾的 FR 编号（横切叙事 only）
- [ ] B 阶段：design/OpenAPI 类型 MR 已排期（若宣称实现就绪）
- [ ] 若放宽 §6.1 嵌套分支：已附 ADR + runtime-freeze §2.1 同步
```

---

**文档版本**：1.1.0 · **维护**：产品 + Agent Runtime owner · **本版**：**§5 Planner 输出形态 · §6 控制流 · §7 B 收束 · §8 MR 清单**。**承** 1.0.6。
