# Runtime · 事件存储与关联

**职责**：与 **一次执行** 相关的 **领域事件**（步骤开始/结束、工具调用边界、计费挂钩点等）**留存、关联键、保留与可检索** **需求下限** — **审计字段 SSOT**仍 **observability**。

**同窗**（短）：[`observability/overview.md`](../observability/overview.md)；[`observability/audit-log.md`](../observability/audit-log.md)；[`execution.md`](./execution.md)；[`persistence.md`](./persistence.md)；[`contract-closure.md`](../contract-closure.md)。**横向全表** → [`boundaries.md`](./boundaries.md)。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. 原则摘要（下限）

- **同一 `executionId`（或等价）** **须**能在 **允许的保留期内** **串联** **计费摘录、审计、LLM/tool 计费点** **之一致视图**（**不含**明文 Secret）。  
- **冷热分层、合规删除** → **Risk/合规 SSOT**；本文 **只**锁 **产品上须能回答的问题**类型。  

---

## 2. 行为与验收下限

| 主题 | 要求 |
|------|------|
| **关联键下限** | **须**支持按 **`executionId`**、**`billingTraceId`**（若存在）、**`idempotencyKey` 前缀**（按 observability 定义）**协调查询**；**与** [`observability/overview.md`](../observability/overview.md) **§2** **事件名**同窗。 |
| **事件类型边界** | **步骤级生命周期**、**工具调用边界**、**计费锚点** **至少**须 **之一可区分**「未调用 / 已调用未终局 / 终局失败 / 终局成功 / UNKNOWN」中的实现约定态，**不得**全部坍缩为不可诊断的 **单条汇总日志**。 |
| **保留期** | **默认保留** **须**满足 **运营协查**与 **用户对账** 的 **产品承诺下限**；**数值** **同窗** **[`design/architecture.md`](../../design/architecture.md) **Memory 留存** **温/冷 v0** **与** **[`observability/overview.md`](../observability/overview.md) **§3**（**审计 ≥180d** **等**）；**超期删除** **不得**破坏 **已出具法务/财务**需要的 **导出快照**链条（**流程**见 **`billing` / `observability`**）。 |
| **与检查点** | **领域事件流** 与 **可恢复检查点** [`persistence.md`](./persistence.md) **须** **可对齐** **同一执行实例**，**禁止** **两个系统长期漂移**导致 **无法回答**「这笔钱为何扣」。 |
| **主态迁移之可证明性** | **实现** **须** **在** **`design`/架构 ADR** **提供** **对照说明**（**表或附录**）：**附录 A 主态** **之** **每一次** **单步迁移** **可** **由下列证据之一** **在保留期内复原**：**(a)** **`agent.orchestration.step` / `agent.execution.step`** **序列** **与** **约定** **`stepKind`** **；** **(b)** **宿主显式** **`execution` 状态迁移事件**（**事件名与载荷** **`observability-schemas` MR** **冻结**）；**(c)** **检查点版本链** **+** **幂等表** **与** **主态** **一致**。**禁止**：**用户可见主态** **与** **§2 事件 + 检查点** **长期无法互证** **且无** **纠偏作业**。 |

---

## 3. 明确不包含

- **完整 observability schema 枚举** — **见 `observability/` 分卷与 OpenAPI components**。  
- **日志采集代理、下游 SIEM 配置**。  

---

**文档版本**：1.0.4 · **维护**：产品 + Agent Runtime owner · **本版**：§2 **主态迁移可证明性**。**承** 1.0.3。
