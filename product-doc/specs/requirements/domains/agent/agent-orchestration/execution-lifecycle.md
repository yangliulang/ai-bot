# 执行生命周期 · 工具链归因

**职责**：**同一用户回合/执行单元内** 工具调用 **如何挂到** **`executionId`**、**与 `scenarioId`/`orchestrationVersion` 的邻接关系** — **产品下限**；**字段级 SSOT** → [`../../observability/overview.md`](../../../observability/overview.md)。

**互引**：[`overview.md`](overview.md) **FR-AO05～06**、**§3 `SC-AO-05`/`SC-AO-08`**；[`routing-engine.md`](routing-engine.md)；[`retry-policy.md`](retry-policy.md)；[`../../../Runtime/planner-contract.md`](../../../Runtime/planner-contract.md)；[`../../../Runtime/execution-transition-matrix.md`](../../../Runtime/execution-transition-matrix.md) **§2.2**（**Planner 步→主态边**）；[`../../observability/overview.md`](../../../observability/overview.md) **§2.4 · `SC-OBS08`**；[`../../../risk/hitl-and-automation-matrix.md`](../../../risk/hitl-and-automation-matrix.md)。**私域工具 / `call_exchange_write` 同窗** **Intent→Canonical→Gateway** [`canonical-trading-model.md`](../../../../design/canonical-trading-model.md)、[`ADR-004`](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../exchange-agent/trade-assistance.md)、[`CC-P1-07`](../../../contract-closure.md#cc-p1-07)、[`requirements-review` §7.5](../../../../../product/requirements-review.md#cc-adr004-review-checklist)、[`Runtime/execution` §1 步 7](../../../Runtime/execution.md)。**契约开放面 / 走读缺口** → [`closure-remaining` §7](../../../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../../../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。

---

## 1. 总则（原 overview §6.1）

- **`agent.tool.call`**：**`toolId`** **须** 已在 [`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **§8.3～8.4**（或所内等价登记）**列名**。  
- **推荐**：**同条** **或** **时序紧邻** **`agent.orchestration.step`** **携带** **`scenarioId` + `orchestrationVersion`**，与 **FR-AO05** 一致；**落点二选一** **须在实现冻结** — **禁止** **无 `scenarioId`** **却** 已调 **外网 / B 类工具** **之** **整条链**。  
- **私有读/写** **协查** **须** 满足 **观测** **§2.1** **总则**（**不在此卷** **展开** **`invocationState` 字段表**）。

---

## 2. 与计费 / 终局

- **可计费路径** **`accepted`** **仍** **须** **`executionId` + 终局扣费**（见 [`../../flows/consume-and-bill.md`](../../../flows/consume-and-bill.md)）— **编排层** **不** **引入** **与** **计费域** **冲突的「免费成功」语义**。

---

## 3. `FR-MT02`（通知与工具结果一致性 · 摘录）

- **监控类触达** **若** **依赖** **工具链结果**：**须** **与** **同一次** **`executionId`（或所内规定的 join 键）** **可关联**，**细节** **见** [`../../observability/overview.md`](../../../observability/overview.md) **与** [`../exchange-agent/monitoring-tasks.md`](../exchange-agent/monitoring-tasks.md) — **本篇** **只** **锁** **「不得孤儿投递」** **下限**。

---

## 4. 单次执行预算（工具调用 · 编排步 · 可选模型回合）

**目的**：防止 **异常或模型行为** **导致** **同一 `executionId` 下** **无限重复工具调用或编排步**（例如失败路径反复下单预览、外网只读查询空转），**在生产中静默耗尽配额或放大错误面**。

### 4.1 `FR-AO06`（条文归宿 [`overview.md`](overview.md)）

- **同一 `executionId`** **内** **须** **强制执行** **可配置硬顶**（**具体键名、默认值、`ai-settings` / OpenAPI 落点** **`design` 冻结**），**至少** **包含**：  
  1. **工具调用次数上限**：按 **达** **`agent.tool.call`** **之** **终态**（`invocationState` **为** **SUCCESS/FAILED** **或** **`design` 冻结之等价口径**）**计数**；**同一 `toolCallSeq`** **内** **之** **RETRYING** **不** **增计** — **与** [`../../admin/tool-management/runtime-contract.md`](../../admin/tool-management/runtime-contract.md) **§3** **同窗**。  
  2. **编排步骤上限**：按 **`agent.orchestration.step`**（**或** **合并事件之等价 `stepSeq`**）**计数** **之** **单调步数** **上限** **`design` 冻结**。  
  3. **（可选）模型推理回合上限**：**Planner–模型–工具** **闭环** **之** **轮次** **上限** — **若产品启用** **须** **与** **计费** **同窗** **定义** **「回合」** **口径**。  
- **任一超限**：**须** **终止该执行** **之** **工具与外网 IO 扩张**；**向用户** **给出** **`FR-T05` 族** **可解释** **稳定码**（**建议名** **`ORCHESTRATION_BUDGET_EXCEEDED`** — **最终** **`billCode`/`stableReason`** **[`design/api.md`](../../../../design/api.md) **运营侧 AI Settings** **下设** **编排执行预算 · 用户触达** **小节** **冻结**）；**且** **须** **可观测**（**同窗** [`../../observability/overview.md`](../../../observability/overview.md) **§4 `SC-OBS07`**、[`overview.md`](overview.md) **`SC-AO-08`**）。  
- **与** **C 类外网** **分项池**：**ADR-003** **之** **外网步** **预算** **仍** **适用** — **本** **§4** **为** **「整条执行」** **之** **横切硬顶**，**二者** **同时命中** **以** **更严者** **或** **`design` 冻结之优先级** **为准**。

### 4.2 与 DAG 有向环（需求边界）

**产品句**：**`FR-AO06.2`（编排步上限）** **为** **防无限步进** **之** **必选兜底** — **不依赖** **实现** **事先证明** **图无环**。**是否在静态 DAG 定义上** **强制无环**、**或** **叠加** **环检测** — **见** [`runtime-freeze.md`](runtime-freeze.md) **§2.1** **（随 DAG MR 冻结）**。

### 4.3 互引

| 文档 | 关系 |
|------|------|
| [`../../../Runtime/execution.md`](../../../Runtime/execution.md) **§1** | 管线 **编排步** **与** **工具** **须** **落在** **本条硬顶** **内** |
| [`../../../risk/hitl-and-automation-matrix.md`](../../../risk/hitl-and-automation-matrix.md) | **HITL** **不** **替代** **预算顶**；**二者** **叠加** |

---

## 5. Planner Runtime Contract（再规划与禁忌 · 产品下限）

**目的**：把 **Planner** **从** **隐式行为** **收敛为** **可审计 Runtime 契约**，**与** **`FR-AO06`**、**确认门**、**工具登记** **叠加**，**降低** **LLM Runtime 漂移**。

**输出形态与控制流（V1）** → **[`../../../Runtime/planner-contract.md`](../../../Runtime/planner-contract.md) §5～§6**（**`PlannerPlanEnvelope` / `PlannerPlanStep`**、**线性计划**、**禁止嵌套条件 DAG**）；**本篇** **§5.2** **禁忌表** **与** **横切入口** **互引**。

### 5.1 再规划（`can_replan`）

- **允许** **在** **同一 `executionId`** **内** **补全/重排子步** **仅当** **不** **篡改** **用户** **已确认** **之** **写意图语义**（**热修复改 DAG** → [`runtime-freeze.md`](runtime-freeze.md) **§1**）。
- **`max_replan`/`max_depth` 数值与配置键** → **`design`/OpenAPI** **冻结**；**需求下限**：**须** **存在硬顶** **且** **越界行为** **同 §4**（**预算顶** **与** **可观测**）。

### 5.2 禁忌动作（`forbidden_actions` · 实现须拒答或等价中止）

| **标识（逻辑名）** | **含义** | **宿主** |
|--------------------|----------|----------|
| **`bypass_confirmation`** | **交易写** **绕过** **类型 A / ADR-001** **确认门** | **ADR-001**；[`confirmation-flow.md`](confirmation-flow.md) |
| **`skip_risk_or_kill_gate`** | **绕过** **Kill/Pause / 有效配置快照** | [`../../../Runtime/execution.md`](../../../Runtime/execution.md) **§1 步 2** |
| **`skip_tool_registry_or_fr_t02`** | **调用未登记工具** **或** **破坏** **`FR-T02`** **门禁顺序** | [`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) |
| **`assert_exchange_terminal_before_truth`** | **向用户断言成交/终局** **早于** **交易所/对账终局** | [`../../../Runtime/unknown-state.md`](../../../Runtime/unknown-state.md)；[`architecture.md`](../../../../design/architecture.md) |
| **`ignore_execution_budget`** | **无视** **`FR-AO06`** **编排步/工具顶** | **本篇 §4** |
| **`duplicate_bill_same_execution`** | **同一 `executionId`** **重复** **终局核销/计费** | [`../../flows/consume-and-bill.md`](../../../flows/consume-and-bill.md)（**`SC-B20`** **方向**） |
| **`emit_nested_conditional_plan`** | **Planner 输出** **含** **嵌套** **`if/else`/并行分叉** **等** **控制流节点**（**V1 禁止**） | [`../../../Runtime/planner-contract.md`](../../../Runtime/planner-contract.md) **§6.1**；**例外** **须** **ADR** |

**扩容**：新增禁忌 **须** **MR** **并** **回补** **本表** **与** **[`runtime-truth-source-map.md`](../../../Runtime/runtime-truth-source-map.md)** **§2** **及** **[`planner-contract.md`](../../../Runtime/planner-contract.md)**。

---

**文档版本**：1.3.5 · **维护**：产品 + Agent Runtime owner · **本版**：**§5** **互引** **`planner-contract` §5～§6**；**§5.2** **`emit_nested_conditional_plan`**。**承** 1.3.4。
