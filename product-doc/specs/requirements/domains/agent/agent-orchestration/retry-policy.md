# 重试策略 · 编排层下限

**职责**：产品在 **网关未知 / 超时 / 可重试错误** **场景下**，**对用户可见语义** **与** **编排层重试边界** — **实现级退避 / 队列** → [`../../../Runtime/recovery.md`](../../../Runtime/recovery.md)、[`../../../Runtime/execution.md`](../../../Runtime/execution.md)、[`../../../Runtime/overview.md`](../../../Runtime/overview.md)；**`billCode`/`unknown`/504** → [`../../../design/architecture.md`](../../../../design/architecture.md)、[`../../../design/api.md`](../../../../design/api.md)。

**互引**：[`overview.md`](overview.md) **§3 `SC-AO-06`**；[`execution-lifecycle.md`](execution-lifecycle.md)、[`runtime-freeze.md`](runtime-freeze.md)；[`fallback-policy.md`](../../../Runtime/fallback-policy.md) **§2 场景表**（**Retry/Fallback/Reconcile/Stop**）。**交易所私域 IO / 重试与幂等** **须** **同窗** **Intent→Canonical→Gateway** **文档链** [`canonical-trading-model.md`](../../../../design/canonical-trading-model.md)、[`ADR-004`](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../exchange-agent/trade-assistance.md)、[`CC-P1-07`](../../../contract-closure.md#cc-p1-07)、[`requirements-review` §7.5](../../../../../product/requirements-review.md#cc-adr004-review-checklist)、[`Runtime/execution` §1 步 7](../../../Runtime/execution.md) — **不得** **借步骤重试** **弱化** **对账 / `unknown` 语义**。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 原则

- **禁止** **`UNKNOWN`/`504`/超时** **直接映射为** **用户可见** **`SUCCESS`/「已成交」**（**在与交易所真实终态对账之前**）。  
- **同一 `executionId` 下** **的** **tool 调用幂等语义** → **遵循** [`../../admin/tool-management/runtime-contract.md`](../../admin/tool-management/runtime-contract.md) **（若有）及** **`observability`** **Result envelope** — **本篇** **不** **复述** **字段**。

---

## 2. 与编排的配合

- **步骤级重试**：**不得** **跳过** **类型 A / 读技能** **等** **合规门**（见 [`confirmation-flow.md`](confirmation-flow.md)）。  
- **跨步骤重试**：**须** **保持** **`scenarioId` + `orchestrationVersion` 可追踪**（见 [`execution-lifecycle.md`](execution-lifecycle.md)、[`runtime-freeze.md`](runtime-freeze.md)）。

---

**编排执行预算**（**防循环调用之硬顶**）→ [`execution-lifecycle.md`](execution-lifecycle.md) **§4 `FR-AO06`**；**与** **本条** **步骤级重试** **计数对齐** → [`../../admin/tool-management/runtime-contract.md`](../../admin/tool-management/runtime-contract.md) **§3.1**。

---

**文档版本**：1.2.1 · **维护**：产品 + Agent Runtime owner · **本版**：**互引** **补** **ADR-004 / CC-P1-07 / §7.5 / `execution` 步 7**（**私域 IO 重试**）。**承** 1.2.0。
