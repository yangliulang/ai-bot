# Runtime · 冻结与 Kill 政策

**职责**：**编排定义、DAG、版本戳** 与 **Kill/会话冻结** **政策层** 横切 — **实现细则**在 **`Runtime`/Planner 仓库** 冻结；**产品**要求 **可观测、可回滚、不静默改用户已确认语义**。

**同窗**（短）：[`domains/agent/agent-orchestration/runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md) · **`orchestrationVersion`、SC-AO-03**；[`domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md)；[`contract-closure.md`](../contract-closure.md)；[`recovery.md`](./recovery.md)。**横向全表** → [`boundaries.md`](./boundaries.md)。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. 产品下限（占位）

- **热修复** **改变**用户已确认步骤语义 → **新版本号 + 兼容策略**（同窗 **`runtime-freeze` §1**）。  
- **冻结范围**（全局/租户/会话）**须**与 **运营台规则** [**`agent-management` rules §3**](../domains/admin/agent-management/rules.md) **可对用户解释**且不混淆 **狭义 onboarding**。  

---

**文档版本**：1.0.1 · **维护**：产品 + Agent Runtime owner · **本版**：**同窗短列表**。**顺延 1.0.0**。
