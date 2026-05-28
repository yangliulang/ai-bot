# 状态机 · `taskId` 与长驻任务

**职责**：**监控 / 自动化任务** 在 **产品侧可验收的 `taskId` 生命周期与状态词汇** — **不** **替代** [`../../../Runtime/execution.md`](../../../Runtime/execution.md)、[`../../../Runtime/runtime-state.md`](../../../Runtime/runtime-state.md) **所载** **内部队列状态**；**能力条**（用户能建什么任务）→ [`../exchange-agent/monitoring-tasks.md`](../exchange-agent/monitoring-tasks.md)。

**互引**：[`task-scheduler.md`](task-scheduler.md)；[`../../flows/automation-alerts.md`](../../../flows/automation-alerts.md)；[`../../contract-closure.md`](../../../contract-closure.md)；[`overview.md`](overview.md) **§3 `SC-AO-07`**。**契约开放面 / 走读缺口** → [`closure-remaining` §7](../../../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../../../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。

---

## 1. `taskId` 生命周期（原 overview §6.3）

| **状态（产品词）** | **含义（摘要）** | **与工程对齐** |
|--------------------|------------------|----------------|
| **`created`** | 用户已创建，**未** **首次满足执行条件** | 实现可映射 **Runtime** **pending** |
| **`active`** | **满足调度** **且** **可重复触发** | **与** **触发器** **对签** |
| **`triggered`**（可选 **子状态**） | **单次执行已派发** | **须** **可关联** **`executionId`** **（`FR-MT02` 方向）** |
| **`paused`** | 用户暂停 | **不得** **静默恢复** |
| **`completed`** | **终态** · 成功完成 | **计费/清理** **从** **计费域** |
| **`expired`** | **终态** · 过期 | 同上 |
| **`cancelled`** | **终态** · 用户撤销 | 同上 |

**冲突 / 未定义组合** → **以实现 `Runtime` + 本表** **同窗 MR** **冻结**；**首版** **不得** **对用户** **承诺** **未在** **`monitoring-tasks` / `automation-alerts`** **出现的** **任务形态**。

**实现映射表**：

- **`taskId`（长驻任务）** **产品词** **↔** **Runtime 队列/内部状态** **的一对一（或 N:1 显式枚举）** **须在首版落地 MR** 冻结，**推荐** **同窗 ADR** **或** **`Runtime/`** **专用附录**（**勿** **与** **`execution.md` 附录 A** **混写** **以免与 `executionId` 混维**），**并与本表对签**。
- **`executionId`（单笔可计费执行）** **主态 v0** **已** **叙事冻结** → **[`../../../Runtime/execution.md`](../../../Runtime/execution.md) 附录 A**（**与** **`taskId`** **不同维** **禁止** **混用一行映射**）。

---

## 2. 验收 **SC-MT01、SC-MT03**（归宿提示）

- **条文能力面** → [`../exchange-agent/monitoring-tasks.md`](../exchange-agent/monitoring-tasks.md)。  
- **状态 / 观测 / 终态一致性** → **抽检** **须** **能** **按上表** **映射** **到** **日志与指标**（详见 [`../../metrics/trading-metrics.md`](../../../metrics/trading-metrics.md)）。

---

## 3. `FR-MT03`（摘录）

- **任务删除 / 过期 / 取消** **须** **在用户可见语义上** **可解释** **且** **无重复触达**（与 **调度器** **对签**）；**细则** **不在** [`monitoring-tasks.md`](../exchange-agent/monitoring-tasks.md) **Capability 条重复** — **见** [`task-scheduler.md`](task-scheduler.md)。

---

**文档版本**：1.1.3 · **维护**：产品 + Agent Runtime owner · **本版**：**篇首** **`closure-remaining` §7.5 / §7.6** **互引**。**承** 1.1.2。
