# 编排域边界 · 非目标与分工

本卷描述 **`agent-orchestration/`（编排域）** 与 **相邻规格** **谁写什么**。**交易所产品合规边界、主站回退码** → [`../exchange-agent/boundaries.md`](../exchange-agent/boundaries.md)（**不同文件**）。

---

## 1. 邻域分工表

| 邻域 | **谁负责** | **编排域不写** |
|------|------------|----------------|
| [`../exchange-agent/`](../exchange-agent/overview.md) | 五 pillar **能力语义**、`skillId`/`toolId` **登记宿主**、**FR-T09/T11** 产品叙事 | **不**铺开 **用户价值 Capability 正文** |
| [`../../flows/`](../../../flows/README.md) | **逐步骤** 剧本权威 | **不** **复制** **流程全文** |
| [`../../../design/api.md`](../../../../design/api.md) | PATH **矩阵终裁** | **不重写** **契约表** |
| [`../../../Runtime/overview.md`](../../../Runtime/overview.md)（[**`execution.md`**](../../../Runtime/execution.md)、[**`freeze-policy.md`**](../../../Runtime/freeze-policy.md) **等 §1**） | 队列、Planner、D-1、冻结 **横切叙事** | **不把** DAG **实现细则** **提前写满** — **与本目录** **`runtime-freeze.md`** **对读** |
| [`../../observability/overview.md`](../../../observability/overview.md) | **`executionId`、`invocationState` 字段 SSOT** | **只** **锁** **`execution-lifecycle.md`** **产品下限** |

**研发误读高发时**：先读 [`implementation-alignment.md`](implementation-alignment.md)（**真源矩阵 / 术语 / 检查单**），再改本目录分卷或 `flows/`。

---

## 2. 会签提示（摘录）

| 变更类型 | **建议同窗** |
|----------|----------------|
| **改工具归因 / `executionId`** | `observability` + [`../../admin/tool-management/runtime-contract.md`](../../admin/tool-management/runtime-contract.md) |
| **改监控键 / `taskId` 语义** | [`../../flows/automation-alerts.md`](../../../flows/automation-alerts.md) + [`../exchange-agent/monitoring-tasks.md`](../exchange-agent/monitoring-tasks.md) |
| **改 `scenarioId` 全表** | **相关** **flows** + **`design/api`** |

---

**文档版本**：1.0.1 · **维护**：产品 + Agent Runtime owner · **本版**：**§1** **增** **`implementation-alignment`** **指引**。**承** 1.0.0。
