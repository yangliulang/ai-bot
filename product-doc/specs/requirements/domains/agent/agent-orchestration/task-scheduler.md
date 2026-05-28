# 任务调度 · 风险触达与监控/Pull

**职责**：（1）**风险类通知** 的 **频控、合并、冷却窗** 产品下限（原 **§6.2**）；（2）**监控 / Pull `scenarioId`** 的 **调度与触发边界**（与 [`routing-engine.md`](routing-engine.md) **§4** **对读**）。

**互引**：[`overview.md`](overview.md) **§3 `SC-AO-07`**；[`../exchange-agent/risk-alerts.md`](../exchange-agent/risk-alerts.md)（话术/类型）；[`state-machine.md`](state-machine.md)；[`../../flows/automation-alerts.md`](../../../flows/automation-alerts.md)。**契约开放面 / 走读缺口** → [`closure-remaining` §7](../../../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../../../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。

---

## 1. 风险类触达 — `FR-RA02`、`FR-RA03`、`SC-RA01`（原 overview §6.2）

- **`FR-RA02`**：**同一信号源 / 用户 / 短窗内** **不得** **无节制** **重复 Push**；**须** **有** **冷却或 digest** **策略**（参数 **与** **运营配置** **对签**）。  
- **`FR-RA03`**：**可合并** **的** **同类提醒** **应** **合并为** **单条** **或** **摘要**（**不得** **藉合并** **隐藏** **须单独确认的** **风险动作**）。  
- **`SC-RA01`**：**抽检** **回放** **须** **见** **频控/合并** **生效** **痕迹**（**与** [`../../observability/overview.md`](../../../observability/overview.md) **指标** **同窗**）。

**能力类型与文案** → **`risk-alerts`**；**本篇** **只锁** **编排/通知策略** **下限**。

---

## 2. 监控与 Pull — 调度边界

- **触发器 → `taskId` → 执行** **步骤序** **须** **与** [`../../flows/automation-alerts.md`](../../../flows/automation-alerts.md) **及** [`../../contract-closure.md`](../../../contract-closure.md) **§1 第 5 款** **对签**。  
- **只读 Pull**：**须** **具备** **矩阵或公开 PATH 依据**（与 **读侧** **寄存器** **§1** **一致**）。  
- **与 `trade-assistance` §8.3～8.5** **写路径** **混编** **时** **须** **遵守** ADR-001（链 [`confirmation-flow.md`](confirmation-flow.md)）。

---

**文档版本**：1.1.2 · **维护**：产品 + Agent Runtime owner · **本版**：**篇首** **`closure-remaining` §7.5 / §7.6** **互引**。**承** 1.1.1。
