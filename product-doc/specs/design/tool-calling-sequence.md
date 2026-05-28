# Tool calling sequence（工具调用时序 — 设计切片）

**定位**：**写路径** 上 **类型 A 确认门**、**工具门禁顺序** 与 **失败可观测** 的 **时序化索引**。**`toolId` / 技能矩阵** 真源 **[`api.md`](./api.md)**、[`trade-assistance.md`](../requirements/domains/agent/exchange-agent/trade-assistance.md) **§8**；**单条请求逻辑序** **[`Runtime/execution.md`](../requirements/Runtime/execution.md) §1**（**步 7 · 统一交易语义链** **见** **§2 表**）。

**关单余量（MR 首节）**：[`closure-remaining` §0](../requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../requirements/closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../requirements/closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../requirements/contract-closure.md)。

---

## 1. 概念序（设计约束）

1. **Planner 与门禁**：工具选型 **须**满足 **[`FR-T02`](../requirements/domains/agent/exchange-agent/overview.md)** 等 **顺序与风险级**；**预算** **[`FR-AO06`](../requirements/domains/agent/agent-orchestration/execution-lifecycle.md)**；**计划输出形态** **[`Runtime/planner-contract` §5～§6](../requirements/Runtime/planner-contract.md)**（**线性 `steps[]`**、**禁嵌套条件 DAG**）。  
2. **类型 A 先于 Coobit 写**：**任何** **Coobit 私有写** **前** **须**完成 **用户确认**（[**ADR-001**](adr/001-telegram-confirm-before-coobit-write.md)）；**禁止**「先写再补确认」。  
3. **工具链失败**：**须**落 **`invocationState` / `stableReason`** 下限（[`Runtime/error-normalization.md`](../requirements/Runtime/error-normalization.md)）；**504/UNKNOWN** [`unknown-state.md`](../requirements/Runtime/unknown-state.md)。  
4. **计费挂钩**：**仅**在 **可计费执行终局** 后按 [`consume-and-bill.md`](../requirements/flows/consume-and-bill.md)、[`billing.md`](../requirements/domains/admin/billing-management/overview.md) **§10.1** — **不得**在编排中段 **预扣**误导用户。  

---

## 2. 真源分工

| 主题 | SSOT |
|------|------|
| 对上 Coobit 私有所内 HTTP | [`api.md`](./api.md)、[`integrations/exchange/overview.md`](../requirements/integrations/exchange/overview.md)、[`agent-coobit-api-allowlist.md`](../requirements/integrations/exchange/agent-coobit-api-allowlist.md)；**实现默认** **`openapi-ai` 官方包**（pin 版本） |
| 统一交易语义 / Gateway（文档 A；步 7） | [`canonical-trading-model.md`](./canonical-trading-model.md)、[`ADR-004`](./adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../requirements/domains/agent/exchange-agent/trade-assistance.md)；[`CC-P1-07`](../requirements/contract-closure.md#cc-p1-07)；[`requirements-review` §7.5](../../product/requirements-review.md#cc-adr004-review-checklist)；[`Runtime/execution` §1](../requirements/Runtime/execution.md) |
| 卡片与确认 UX | [`telegram/overview.md`](../requirements/domains/agent/telegram/overview.md) **§2.5 · 类型 A**（总则 **§2～§2.6**）、[`confirmation-flow.md`](../requirements/domains/agent/agent-orchestration/confirmation-flow.md) |
| 编排、重试、冻结 | [`agent-orchestration/overview.md`](../requirements/domains/agent/agent-orchestration/overview.md)、[`retry-policy.md`](../requirements/domains/agent/agent-orchestration/retry-policy.md) |
| C 类外网工具合规 | [ADR-003](adr/003-external-tools-compliance-and-budget.md)、[`tool-management/overview.md`](../requirements/domains/admin/tool-management/overview.md) |

---

## 3. 工程充实项

- **进程/队列级时序图**（多实例下工具调用）→ **[`runtime-architecture.md`](./runtime-architecture.md)** **充实后与本文对签**。  

---

**文档版本**：0.2.4 · **维护**：产品 + Agent Runtime owner · **本版**：**篇首补** **`closure-remaining` §0·§6/§6.4。** **承** **0.2.3**
