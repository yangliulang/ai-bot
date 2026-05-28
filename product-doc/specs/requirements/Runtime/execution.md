# Runtime · 执行与投递（调度 / Planner / 队列）

**职责**：从 **接单** 到 **一次可计费、可观测执行** 的 **横切叙事**：Planner/工具选择与 **门禁顺序**宿主、异步队列、在途与 **D-1**（实现定义）等与 **计费**同窗的下限。**不**穷尽 DAG 节点类型 **实现枚举** — **产品与契约**仍以域内为准。**契约开放面 / 走读缺口** → [`closure-remaining` §7](../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../closure-remaining.md#cc-closure-exec-checklist)**。

**同窗**（短）：[`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md) **（Walkthrough · 文首「架构语言」）**；[`architecture.md`](../../design/architecture.md) **§「与通用 Agent 栈之对照」**；[`domains/agent/agent-orchestration/routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)、[`overview.md`](../domains/agent/agent-orchestration/overview.md)；[`domains/agent/agent-orchestration/goal-and-execution-paths.md`](../domains/agent/agent-orchestration/goal-and-execution-paths.md)（**Goal/黄金路径/§1×flow**）；[`domains/agent/exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md)；[`flows/consume-and-bill.md`](../flows/consume-and-bill.md)；[`domains/admin/billing-management/overview.md`](../domains/admin/billing-management/overview.md)；[`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md)；[`failure-matrix.md`](./failure-matrix.md)；[`runtime-state-machine.md`](./runtime-state-machine.md)；[`execution-transition-matrix.md`](./execution-transition-matrix.md) **§2.2**；[`observability/overview.md`](../observability/overview.md) **§2.4**。**横向全表** → [`boundaries.md`](./boundaries.md)。

---

## 1. 执行管线（概念序）

**评审口语「十步管线」对照表**（**Scenario Router → Skill Runtime → … → Timeline**、**风险闸束**、**三轨分界**）→ **[`domain-model.md`](./domain-model.md) §1～§4**（**不** 新造 FR）。

从 **渠道一条用户消息 / 回调** 到 **一次可计费、可观测执行** 的 **逻辑顺序**（实现可拆解为多队列/多阶段；**本条不约束组件边界**）。**编号**仅表达 **因果**，与 [`architecture.md`](../../design/architecture.md) 数据流、[`flows/`](../flows/README.md) 业务步骤 **对读**。

1. **接入与归因**：接收 `Update`，绑定 **用户 / Agent 实例 / 会话** 摘要（[`sessions.md`](./sessions.md)、[`telegram-binding.md`](../domains/agent/onboarding/telegram-binding.md)）。
2. **有效配置快照**：读取 **当前生效** 的 **`configVersion`** 与全局/产品线闸（[`trading-agent-config/flow.md`](../domains/admin/trading-agent-config/flow.md)）；命中 Kill/Pause 则 **拒新写** 并按 FR-T05 可解释（[`exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md)）。
3. **一次可计费执行起票**：分配 **`executionId`**（[`exchange-agent` FR-T01](../domains/agent/exchange-agent/overview.md)、[`consume-and-bill.md`](../flows/consume-and-bill.md)）；**禁止**用 Telegram message id **直接替代**。**ID 形态与字符默认** → [`standards/naming-standard.md`](../standards/naming-standard.md) **§1**（`executionId` / `scenarioId` / `sessionId` / 用户标识）。
4. **编排与 Planner**：`scenarioId` / 步骤寄存器与路由（[`agent-orchestration/overview.md`](../domains/agent/agent-orchestration/overview.md)、[`routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)）；工具选型 **须**满足 **FR-T02** 等门禁顺序；**须** **满足** **`FR-AO06`** **单次执行预算**（工具次数 / 编排步 / 可选模型回合 — [`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4**）。
5. **上下文装配**：预算、压缩、爆炸边界（[`agent-context/overview.md`](../domains/agent/agent-context/overview.md)）；Prompt 版本由 **后台** 注入策略决定（[`prompt-management/overview.md`](../domains/admin/prompt-management/overview.md)）。
5b. **写路径读技能规范（若适用）**：**A 类写** **须** **`read_skill_operation_spec`** **先于** **步 6**（**FR-T11** / **FR-AO04**）；**观测** **`agent.skill.spec_read`** — [`skill-specs/production-runtime.md`](../skill-specs/production-runtime.md)、[`confirmation-flow` §1](../domains/agent/agent-orchestration/confirmation-flow.md) **步骤 1**。
6. **确认门（写前）**：交易写 **前** 用户确认与卡片语义（[`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md)、[`telegram/overview.md`](../domains/agent/telegram/overview.md) **§2.5 · 类型 A**（总则 §2～§2.6）、[ADR-001](../../design/adr/001-telegram-confirm-before-coobit-write.md)）。**产出** **携带写参** **之** **类型 A** **之前** **须**满足 [`runtime-invariants.md`](./runtime-invariants.md) **INV-008、INV-009** — **同窗** **确认流** **步骤 2**。
7. **工具与外部调用（Write Barrier）**：只读/写技能走 **trade-assistance** 与 **`design/api` 矩阵**（[`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md)、[`api.md`](../../design/api.md)）。**在** **构造** **Intent→Canonical** **写载荷** **并** **触及** **Gateway / `call_exchange_write`** **之前** **须** **再次** **断言** **INV-008、INV-009**（**与** **用户** **已确认** **包** **逐项** **一致**，**无** **占位/非法血缘**）；**违例** **Stop**，**典型** **`WRITE_PARAMS_INCOMPLETE`** / **`INVALID_PARAMETER_SOURCE`** → **Taxonomy [`WRITE_PARAMETER_CONTRACT`](./runtime-error-taxonomy.md)**。**统一交易语义**（Intent→Canonical→Gateway→Adapter）**文档真源**：[**`canonical-trading-model`**](../../design/canonical-trading-model.md)、[**ADR-004**](../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[**`trade-assistance` §2.6**](../domains/agent/exchange-agent/trade-assistance.md)；契约 [**CC-P1-07**](../contract-closure.md#cc-p1-07)；人类评审 [**`requirements-review` §7.5**](../../../product/requirements-review.md#cc-adr004-review-checklist)；**Execution Gateway 可执行实现 / DoD B** **在** **所内工程仓** **验收**（同窗 **ADR-004** **后果段**）。**对上 Coobit 私网 HTTP**：出站默认 **`openapi-ai`/Skill（pin）**；PATH 仍以 **`design/api` 矩阵** 与 [`agent-coobit-api-allowlist.md`](../integrations/exchange/agent-coobit-api-allowlist.md) **为界** — [`integrations/exchange/overview.md`](../integrations/exchange/overview.md)。**504/UNKNOWN** 见 [`unknown-state.md`](./unknown-state.md)，**REST↔WS 对账**见 [`reconciliation.md`](./reconciliation.md)；**终态前** **不得** 向用户断言成交（[`architecture.md`](../../design/architecture.md)）。
8. **终局与权益核销**：**accepted / 可计费** 边界按 [`consume-and-bill.md`](../flows/consume-and-bill.md)、[`billing.md`](../domains/admin/billing-management/overview.md) **§10.1**；**S5 `ENTITLEMENT_DEBIT`** **晚于** 终局判定之 **产品叙事** 以 billing 域为准。
9. **观测与留存**：`agent.tool.call`、`trading.exchange_private`、`billing.*` 等见 [`observability/overview.md`](../observability/overview.md) **§2**；**主态迁移** **须** **与** [`execution-transition-matrix.md`](./execution-transition-matrix.md) **§2.2** **可对签**，**事件侧映射** **见** [`observability/overview.md`](../observability/overview.md) **§2.4** **与** **`SC-OBS08`**；与 **检查点/幂等** 同窗见 [persistence.md](./persistence.md)。

**异步与队列**：若某步异步化，**仍须**保证 **与用户承诺一致的最终态** 可到达或可解释（**不得**静默丢弃）；**退避/重试**平台级叙事见 [recovery.md](./recovery.md)。

---

## 2. 产品下限（验收指针）

| 片段 | `Runtime` 侧重 |
|------|----------------|
| **Planner / 选型** | 与 **FR-T02** **顺序同窗**的失败 **须**可追溯至 **摘要/观测**字段（不写具体组件名）。 |
| **队列** | 核销前置、推卡、异步后置任务 **排队** **不得**静默丢失 **与用户承诺一致**的最终态；**租户/实例隔离**见 [locking.md](./locking.md)。 |
| **在途 · D-1** | 「上一笔未完是否挡下一笔」**须**产品与 **risk / exchange-agent** 对签后，在此处 **收敛为可测试叙述**（与 **`monitoring-tasks`**、`Runtime` **实现 MR** **映射表**同窗）。 |

**旧稿回迁**：本文合并原 **`orchestration.md` / `planning.md` / `queue.md`** 占位立意。

---

## 附录 A · 单笔 `executionId` 生命周期（产品词 ↔ 工程态 · v0 冻结）

**分维**：本附录 **仅** **锁** **单笔可计费执行** **`executionId`** **之主轨迹**；**`taskId` 长驻任务** → [`../domains/agent/agent-orchestration/state-machine.md`](../domains/agent/agent-orchestration/state-machine.md)；**会话级摘要 `agentState`** → [`runtime-state.md`](./runtime-state.md)。**与** **计费 accepted/终局** **同窗** [`consume-and-bill.md`](../flows/consume-and-bill.md)：**计费叙事里「accepted」（起票 / 分配 `executionId`）与本表主态 `accepted` 在起票瞬间同窗**，本表 `accepted` 还覆盖其后至离终局前的整段管线。

| **产品词（对运营/审计可引用）** | **含义（摘要）** | **工程态（实现须可枚举映射）** |
|--------------------------------|------------------|----------------------------------|
| **`accepted`** | **`executionId` 已分配**，九步管线 **进行中**（含 **步 1～2** **之后**） | **`queued` / `pending_dispatch`** **等** |
| **`planning`** | **编排与 Planner**（§1 **步 4**） | **`planning` / `orchestrating`** |
| **`waiting_confirmation`** | **写前确认门未完成**（§1 **步 6**、类型 A / ADR-001） | **`blocked_on_user` / `confirm_pending`** |
| **`executing`** | **工具与外网 IO**（§1 **步 7**） | **`tool_invocation` / `external_io`** |
| **`settling`** | **终局判定与轨 B 核销在途**（§1 **步 8**） | **`finalizing` / `billing_in_flight`** |
| **`completed`** | **终态成功** — **可计费终局** **以** **计费域** **为准** | **`terminal_success`** |
| **`failed`** | **终态失败** — **须** **可解释** **`stableReason` / `FR-T05` 族** | **`terminal_failure`** |
| **`unknown_pending`** | **504 / UNKNOWN**，**真相未决** — [`unknown-state.md`](./unknown-state.md) | **`reconciliation_pending`** |
| **`cancelled`** | **用户撤销** **于** **产品定义之安全点** **之前** | **`terminal_cancelled`** |

**约束**：

- **同一 `executionId`** **对外的「当前主态」** **同一时刻** **至多一个**；实现可有 **子状态**，**不得** **与用户可见承诺矛盾**。
- **部分成交、在途订单** **等** **交易所中间态**：**落在** **`executing` / `settling`** **下** **之子状态或观测维度**。**升格附录 A 主行** **须** **独立 MR** **同步** **[`trade-via-agent.md`](../flows/trade-via-agent.md) **S5.1** **与本表**。
- **队列与恢复**：§2 **不得静默丢最终态**、[`persistence.md`](./persistence.md)、[`locking.md`](./locking.md) **叠加适用**。

---

**文档版本**：1.0.15 · **维护**：产品 + Agent Runtime owner · **本版**：**步 6～7** **同窗** **`runtime-invariants` INV-008/009** · **Write Barrier**。**承** **1.0.14**。
