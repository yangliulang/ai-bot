# Global Risk · Kill switch / Pause

**职责**：**在用户已绑定且子账户就绪的前提下**，因 **运营配置或运维策略** **拒绝接受新的写意图**（或冻结编排语义）的 **横切叙事**。**单笔产品拒答码**（矩阵缺项、`FR-T05` 族）仍以 [`../domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md) **与** [`../flows/trade-via-agent.md`](../flows/trade-via-agent.md) **为准**。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. 配置与归因（下限）

| 概念 | 说明 | SSOT |
|------|------|------|
| **总开关 OFF** | `GLOBAL_AGENT_SWITCH` → `agentState` 可归因 **`GLOBAL_OFF`** 等（附录 A §9 语义） | [`keys.md` §1](../domains/admin/trading-agent-config/keys.md)、[`management-console-v1-prd.md`](../domains/admin/management-console-v1-prd.md) **附录 A** |
| **运维熔断** | `OPS_GLOBAL_AGENT_PAUSE` 与总开关 **并列语义**；`OPS_SUSPENDED` **由 `design` 冻结** | [`keys.md` §1](../domains/admin/trading-agent-config/keys.md)、[`trading-agent-config/flow.md`](../domains/admin/trading-agent-config/flow.md) **§3** |
| **实例 Pause** | **仅**影响 **该实例**调度；**须有**原因码与 **对用户可解释文案** | [`agent-management/rules.md`](../domains/admin/agent-management/rules.md) **§3** |
| **全局 vs 实例** | 两者 **独立**；UI **不得**混为一谈；OPS 仍 on 时 **Resume 实例** 也可能不可执行 | 同上 |

**编辑 UX**：`GLOBAL_AGENT_SWITCH` / 清空 `SYMBOL_ALLOWLIST` 等高危变更 → **二次确认** + 可选 **双人审批** — [`trading-agent-config/flow.md`](../domains/admin/trading-agent-config/flow.md) **§1**。

---

## 2. 运行时行为（产品下限）

- **有效配置快照** 后若命中 **Kill/Pause**：**拒新写** 且 **`FR-T05` 族** **可解释** — [`../Runtime/execution.md`](../Runtime/execution.md) **§1·2**、[`../domains/agent/exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md)。
- **验收**：**SC-RISK-01**（全局/运维/产品线闸）、**SC-RISK-02**（实例 Pause）、**SC-RISK-05**（高危配置审计）— [`acceptance.md`](acceptance.md)。
- **热修复** 改变用户已确认步骤语义 → **新版本号 + 兼容策略** — [`../Runtime/freeze-policy.md`](../Runtime/freeze-policy.md)、[`../domains/agent/agent-orchestration/runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md)。

---

## 3. 互引

| 文档 | 关系 |
|------|------|
| [`../observability/overview.md`](../observability/overview.md) | **`admin.audit`** 与 配置变更可观测 |
| [`../contract-closure.md`](../contract-closure.md) | 可对签矩阵与 **closure** 条目 |
| [`../domains/admin/prompt-management/runtime-injection.md`](../domains/admin/prompt-management/runtime-injection.md) | **会话绑定冻结**（PM-C10）— **热变更与 Kill 叙事同窗** |

---

**文档版本**：0.2.1 · **维护**：产品 + Agent Runtime owner · **本版**：**`acceptance` SC-RISK-01/02/05** 指针。**顺延 0.2.0** …
