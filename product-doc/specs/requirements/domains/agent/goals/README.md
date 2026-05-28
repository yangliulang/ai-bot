# 结构化 Goal（评审范例 · 非契约 SSOT）

**路径**：`specs/requirements/domains/agent/goals/`。

**职责**：存放 **`goal_id` 形制的评审用范例**，便于把 **用户 Goal** **从** **仅靠 intents 语义** **推进到** **可审计约束块**（成功标准、终止条件、风险上限），**与** **[`goal-and-execution-paths.md`](../agent-orchestration/goal-and-execution-paths.md)** **§5～§6** **对读**。**在** **未与** **[`routing-engine.md`](../agent-orchestration/routing-engine.md)** **寄存器键名会签前**，**本目录任一文件** **均不得** **单独** **作为** **对外契约或 FR/SC 真源**。

**真主链**：**路由与能力** → **`routing-engine`** **+** **对应 `flows/*.md`**；**执行管线** → **[`../../../Runtime/execution.md`](../../../Runtime/execution.md) §1** **与** **附录 A**；**主态迁移契约** → **[`../../../Runtime/runtime-state-machine.md`](../../../Runtime/runtime-state-machine.md)**。

---

## Goal Resolution Boundary（Intent / Goal / Scenario）

| **对象** | **含义（冻结口径）** | **SSOT 宿主** |
|----------|----------------------|----------------|
| **Intent** | **用户** **自然语言表达** **与** **语义簇/槽位** **（「怎么问」）** | [`../exchange-agent/intents.md`](../exchange-agent/intents.md) |
| **Goal** | **用户** **要达成的业务结果** **之** **结构化约束块**（**成功/终止/风险** **可审计**） | [`../agent-orchestration/goal-and-execution-paths.md`](../agent-orchestration/goal-and-execution-paths.md) **§5**；**生产寄存器** **须** **与** **`routing-engine`** **对签后** **升格** |
| **Scenario（`scenarioId`）** | **Runtime** **选用的** **已登记执行路径** **（「跑哪条能力/flow」）** | [`../agent-orchestration/routing-engine.md`](../agent-orchestration/routing-engine.md) |

**约束**：**Planner** **不得** **把** **Intent** **与** **`scenarioId`** **混为** **同一对象** **不交代** **收敛**；**范例 YAML** **之** **`primary_scenario_id`** **仅为** **评审键入** **直至** **会签**。

---

## 布局

| 路径 | 用途 |
|------|------|
| [`examples/review-only/`](examples/review-only/) | **仅评审 / 对齐叙事** **用的** **示例 `goal_id`**（**YAML**）；**复制到** **生产寄存器** **须** **走 MR** **并** **对签** **`scenarioId`** |

---

## 升格为 SSOT 的检查单（节选）

- [ ] **`goal_id`** **与** **至多一个主 `scenarioId`** **可在表中互相引用**（**或** **明确** **为何** **复合型** **须** **拆执行**）。  
- [ ] **约束** **不** **与** **`confirmation-flow` / ADR-001 / FR-T02`** **冲突**。  
- [ ] **Memory**：**注入序** **与** **L0～L3** **分层** **须** **不** **与** [`../../../Runtime/memory-runtime.md`](../../../Runtime/memory-runtime.md)、[`../../../Runtime/context-management.md`](../../../Runtime/context-management.md) **§2** **矛盾**；**Narrative Memory 对照** → [`memory-runtime` §8](../../../Runtime/memory-runtime.md)；**跨会话 Semantic** → [`memory-runtime` §9 `FR-MEM*`](../../../Runtime/memory-runtime.md)；**STM 清空** → **§13 `FR-STM*`**；**开关键** → [`trading-agent-config/keys` §2](../../../domains/admin/trading-agent-config/keys.md) **`FEATURE_SEMANTIC_NARRATIVE`**。

---

**文档版本**：1.0.2 · **维护**：产品 + Agent Runtime owner · **本版**：**升格检查单** **增** **Memory**。**承** 1.0.1。
