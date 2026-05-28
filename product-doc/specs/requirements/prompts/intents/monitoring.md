# Intent · Monitoring（条文）

**路径**：`specs/requirements/prompts/intents/monitoring.md`。  
**性质**：**订阅 / 条件告警意图侧下限** — **不设**独立 `prompts/monitoring/` **目录**；任务生命周期 SSOT 在编排域。

**域宿主**：[`exchange-agent/intents` §1](../../domains/agent/exchange-agent/intents.md)；[`monitoring-tasks`](../../domains/agent/exchange-agent/monitoring-tasks.md)；[`risk-alerts`](../../domains/agent/exchange-agent/risk-alerts.md)；[`automation-alerts`](../../flows/automation-alerts.md)；[`task-scheduler`](../../domains/agent/agent-orchestration/task-scheduler.md)（投递 / 频控）；[`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)。

---

## 1. 语义归属（示意）

**典型簇**：提醒我爆仓风险、别太集中、到价通知、异动监控 — [`exchange-agent/intents` §1](../../domains/agent/exchange-agent/intents.md)。

---

## 2. 与其它意图的歧义

| 混淆 | 分流 |
|------|------|
| **「到价提醒我」** vs **「到了就买」** | 前者 → **本意图**（订阅语义）；后者 → [`trade.md`](./trade.md) |
| **Pull（用户主动问）** vs **Push（告警触发会话）** | 编排与投递见 [`automation-alerts`](../../flows/automation-alerts.md)、[`task-scheduler`](../../domains/agent/agent-orchestration/task-scheduler.md)；Prompt **须区分**「配置订阅」与「单笔执行」话术边界 |
| **全策略托管** | **澄清范围**；超出 MVP → **`FR-T05` 式边界**，**不**承诺无人值守全自动 |

---

## 3. Prompt 侧下限

- **触发条件可读**：标的、阈值、方向（涨破/跌破）、**频率 / 静音窗口**（若产品定义）须让用户 **可复述**，**不**用含糊「帮你盯着」替代 — [`monitoring-tasks`](../../domains/agent/exchange-agent/monitoring-tasks.md)。  
- **不替代写确认**：告警 **若引导用户成交**，仍须走完 confirmation 链 — [`confirmation/README`](../confirmation/README.md)；步骤同窗 [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)。
- **路由**：[`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)。

---

## 4. 失败 / 能力边界 / 幻觉

- **创建任务失败 / UNKNOWN**：[`shared/common-phrases` §2](../shared/common-phrases.md)、[`Runtime/unknown-state`](../../Runtime/unknown-state.md)。  
- **无任务闭环事实**：**不得声称「已替你挂上监控」** — [`hallucination`](../../observability/hallucination.md)。  
- **拒答模板**：[`shared/common-phrases` §1](../shared/common-phrases.md)、[`FR-T05`](../../domains/agent/exchange-agent/overview.md)。

---

## 5. 观测（可选同窗）

- 投递与健康 **不以 Prompt SSOT**；事件如 `agent.prompt.binding_resolved` — [`observability/overview` §2.3](../../observability/overview.md)（与 [`prompt-management`](../../domains/admin/prompt-management/overview.md) 对签时查阅）。

---

**文档版本**：1.4.0-mvp · **维护**：产品 + Prompt owner · **本版**：**确认链句 Markdown**。
