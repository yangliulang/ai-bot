# Global Risk · User confirmation（写前闸门）

**职责**：**任何 Coobit 私有写** 之前的 **用户明示确认** 与 **编排串联** 的 **横切指针**。**卡片语义、callback、`read_skill_operation_spec` 顺序** 的 **验收 SSOT** → [`../domains/agent/agent-orchestration/confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md)；**Telegram** → **[`overview` §2.5 · 类型 A](../domains/agent/telegram/overview.md)**（卡面条目）；**渠道闸 · Bot API** → **同文** **§2～§2.6**。

---

## 1. 硬约束（摘录）

| ID | 陈述 | 详文 |
|----|------|------|
| **FR-T11** | 任一 **`call_exchange_write`** **前** **须** **已完成** **`read_skill_operation_spec`** **且** **类型 A** **已通过** | [`trade-assistance.md` §2](../domains/agent/exchange-agent/trade-assistance.md) |
| **FR-T09** | **每笔** 私有写 **先发** **类型 A** 并 **得明示确认** 后方可调矩阵 **`R/W=W`**；**单笔/单日限额** **超限** **透明拒答** | 同上、[`ADR-001`](../../design/adr/001-telegram-confirm-before-coobit-write.md) |
| **类型 A** | **A 类**：经用户类型 A 后发起的 **`call_exchange_write`** | [`trade-assistance.md` §8.1](../domains/agent/exchange-agent/trade-assistance.md) |

**边界**：**禁止静默代用户确认**、**划转不得静默扣款** — [`../domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md) **§1、§8.4**。

---

## 2. Prompt / 滥用面

- **绕过确认、伪造类型 A** → **拒绝执行写路径叙事** — [`../prompts/safety/illegal-request.md`](../prompts/safety/illegal-request.md) **§2**。
- **写路径 Prompt** → [`../prompts/confirmation/README.md`](../prompts/confirmation/README.md)；类型 A 下限 — [`../prompts/confirmation/order-confirmation.md`](../prompts/confirmation/order-confirmation.md)。

---

## 3. 互引

| 文档 | 关系 |
|------|------|
| [`../Runtime/execution.md`](../Runtime/execution.md) **§1** | 管线中 **确认门** 步骤位 |
| [`../flows/automation-alerts.md`](../flows/automation-alerts.md) | 监控触发后的 **写** 仍须 **确认链** |
| [`hitl-and-automation-matrix.md`](hitl-and-automation-matrix.md) | **HITL** **与** **止损 / Kill / 自动化** **之** **术语与场景指针** |

---

**文档版本**：0.2.2 · **维护**：产品 + 交互 owner · **本版**：**职责段** **§2.5 · 类型 A** **与** **§2～§2.6** **分流**；**承 0.2.1**。
