# Global Risk · HITL 与自动化的对照矩阵

**职责**：用 **产品语言** 区分 **人在回路（HITL）** 与 **触发后按策略自动执行** 的两类机制，并给出 **与现有条文的一对一指针**。**不**替代 [`user-confirmation.md`](user-confirmation.md)、[`kill-switch.md`](kill-switch.md)、[`../domains/agent/exchange-agent/trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **SSOT** — **冲突以域正文为准**，本文 **仅** **收束索引**。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. 术语

| 术语 | 含义（产品） |
|------|----------------|
| **HITL** | **须暂停** 编排或写路径，**等待用户明示动作**（类型 A / 二次确认 / Deeplink 等）**后** **方可** **继续** **对私有产地的写或等价高风险承诺**。 |
| **自动化 / 策略执行** | **命中规则后** **由系统按配置执行**（拒新写、Pause、频控拦截 **等**），**无需** **每笔** **再问用户** — **与** **「暂停等用户点确认再继续」** **不同**。 |
| **止损 / 护栏 / Kill** | **运营或风控键** **触发** **的** **拦截、拒答、熔断** — **同窗** [`kill-switch.md`](kill-switch.md)、[`exposure-limit.md`](exposure-limit.md) **等** **分卷**；**默认** **不** **等价于** **「AI 自主下单无确认」**。 |

---

## 2. 对照表（指针级）

| 场景（摘要） | 行为类型 | 主文档 |
|-------------|----------|--------|
| **普通现货/合约等私有写** | **HITL** — **每笔** **类型 A** **后再** `call_exchange_write` | [`user-confirmation.md`](user-confirmation.md)、[`../domains/agent/agent-orchestration/confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md)、[`../domains/agent/exchange-agent/trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§2**、[`telegram/overview` §2.5 · 类型 A；总则 §2～§2.6](../domains/agent/telegram/overview.md)、[`ADR-001`](../../design/adr/001-telegram-confirm-before-coobit-write.md) |
| **高龄高危路径**（大额市价、提杠杆、**全仓清仓语义** **等** — **以路由枚举为准**） | **HITL** — **在类型 A 之外** **须** **二次确认** **与** **关键数字重复** | [`../prompts/confirmation/high-risk-confirmation.md`](../prompts/confirmation/high-risk-confirmation.md)、[`confirmation-flow`](../domains/agent/agent-orchestration/confirmation-flow.md) |
| **条件单 / 自动化任务之「创建写」** | **HITL** — **创建 / 取消** **等写** **仍** **须** **类型 A** | [`../flows/automation-alerts.md`](../flows/automation-alerts.md) **S1**、[`trade-assistance`](../domains/agent/exchange-agent/trade-assistance.md) **§8.5** |
| **监听触发 → 推送通知**（无交所写） | **非 HITL 写** — **告警触达**；若后续 **引导到写** **仍** **走** **上表写行** | [`automation-alerts.md`](../flows/automation-alerts.md) **S5** |
| **全局 / 运维 / 实例 Pause、总开关** | **自动化策略** — **拒新写** **或** **冻结**，**按** [`kill-switch.md`](kill-switch.md) **与** [`../Runtime/execution.md`](../Runtime/execution.md) **§1** | [`kill-switch.md`](kill-switch.md)、[`../domains/agent/exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md) |
| **敞口 / 限额 / 符号闸** | **自动化策略** — **透明拒答** **或** **拦截**，**不** **依赖** **模型临场判断** | [`exposure-limit.md`](exposure-limit.md)、[`symbol-restriction.md`](symbol-restriction.md)、[`leverage-limit.md`](leverage-limit.md) |

**说明**：**「全仓出清」** **是否** **允许自动执行** **而** **不经类型 A** — **默认** **不允许** **作为** **Coobit 私有写**；**须** **落在上表「普通写 / 高危写」** **路径**。**若** **未来产品** **定义** **例外**（例如 **仅平仓类** **预授权长期任务**），**须** **单开 ADR + contract-closure** **与** **`trade-assistance` §8** **对签**，**并** **更新本表**。

---

## 3. 互引

| 文档 | 关系 |
|------|------|
| [`../domains/agent/agent-orchestration/execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4** | **防模型循环调用** **之** **硬顶** **与** HITL **并行** **降低资金与费率风险** |

---

**文档版本**：0.1.2 · **维护**：产品 + 风控 owner · **本版**：**§2** **对照表** **`telegram/overview` §2.5 · 类型 A；§2～§2.6**；**承 0.1.1**。
