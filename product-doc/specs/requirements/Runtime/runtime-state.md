# Runtime · 运行态与摘要

**职责**：门禁短路、Warm-up/Pause **技术态** 与 **用户摘要**（`agentState`、`lastProductBlockReason` 等）**对齐**的 **横切叙述**。**`agentState` 枚举真源**仍 **[`management-console-v1-prd` §9](../domains/admin/management-console-v1-prd.md)** — 本文 **不**另造码表。

**同窗**（短）：[`domains/agent/onboarding/activation-policy.md`](../domains/agent/onboarding/activation-policy.md)；[`runtime-provisioning.md`](../domains/agent/onboarding/runtime-provisioning.md) **§3** · Pause/Warm-up 话术；[`domains/admin/agent-management/rules.md`](../domains/admin/agent-management/rules.md)；[`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md)、[`trade-via-agent.md`](../flows/trade-via-agent.md)。**横向全表** → [`boundaries.md`](./boundaries.md)。

---

## 1. 产品下限（占位）

- **内部队列状态** 与 **产品态 `taskId` 生命周期** **映射**须在首版 **MR 冻结**（推荐 **ADR**），并与 [`domains/agent/agent-orchestration/state-machine.md`](../domains/agent/agent-orchestration/state-machine.md) **对签**。  
- **单笔 `executionId` 主态（产品词 ↔ 工程态）** **v0** → [`execution.md`](./execution.md) **附录 A**（**与** **`taskId` 表** **不同维**）。  
- **摘要不得长期与 Runtime 可观测事实矛盾**（同窗 onboarding **SC-ON-03** 精神）。  

**旧稿回迁**：承接原 **`state-machine.md`** 占位立意。

---

**文档版本**：1.0.2 · **维护**：产品 + Agent Runtime owner · **本版**：**§1** **链** **`execution` 附录 A**。**承** 1.0.1。
