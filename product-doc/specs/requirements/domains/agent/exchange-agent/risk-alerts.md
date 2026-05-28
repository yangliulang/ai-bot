# Exchange Agent · 风险提醒（Risk Alerts）

**路径**：`specs/requirements/domains/agent/exchange-agent/risk-alerts.md`。

**职责**：**Risk Capability** — **提醒类型、信号来源（概念）、严重度/呈现下限、与 Monitoring 的边界、话术与合规**。**不替代** **[`../../../risk/`](../../../risk/README.md)** **系统风控 SSOT**。**冷却窗/digest/投放参数** **与** **`FR-RA02`、`FR-RA03`、`SC-RA01`** → [`../agent-orchestration/task-scheduler.md`](../agent-orchestration/task-scheduler.md)（**通知策略** **不** **落在** **本条**）。

---

## 1. 提醒类型（产品下限）

| 类型（与 pillar 对齐） | 触发信号 **（数据源；细则随矩阵 / 引擎 MR）** | 用户侧呈现 **（下限）** | 与 **Monitoring** 边界 |
|------------------------|---------------------------------------------|-------------------------|-------------------------|
| **爆仓 / 强平风险** | **账户风险快照**、**合约仓位/标记价** **等** | **分级严重度 + 下一步选项**（**非** **个性化投资建议**）；**须** **标注**数据来源与时间 | **事件/瞬时** **偏** **risk**；**用户订阅的持续盯盘** **偏** **Monitoring** [`monitoring-tasks.md`](monitoring-tasks.md) |
| **异常波动** | **价格突破阈值**（**行情源**） | **「波动放大」** + **Disclaimer** | **阈值订阅** → **Monitoring** |
| **仓位过大 / 集中度过高** | **Portfolio 聚合** **（** **风险偏好** **若由用户声明** **）** | **客观集中度** **陈述**；**缺偏好** **不** **作** **隐含投顾** | **同类** **重复外显** **的** **频控策略** | [`../agent-orchestration/task-scheduler.md`](../agent-orchestration/task-scheduler.md) |
| **价格触发**（**到价**） | **用户/规则定义条件** | **命中** **后** **的** **一次或策略性重复** — **须** **产品定义** | **任务 SSOT** → [`monitoring-tasks.md`](monitoring-tasks.md) |

**强平语境只读**（工具能力宿主）：[`trade-assistance.md §8.3`](trade-assistance.md)。

---

## 2. FR / SC（能力与话术）

| ID | 陈述 |
|----|------|
| **FR-RA01** | **文案** **须** **区分** **「交易所/系统风控已执行的动作」** **与** **「Agent 仅展示可读信息」**；**不得** **暗示已代下单/减仓** **除非** **确有** **写回执** **与** **类型 A**。 |

| ID | **验收要点**（可对签） |
|----|-------------------------|
| **SC-RA02** | **文案审计**：**无** **「已替你减仓/挂单」** **类** **暗示**（**`FR-RA01`**）**—** **样本 ≥20**。 |
| **SC-RA03** | **严重度≥中** **抽检**：**须** **含** **数据来源** **或** **`asOf` 时间锚**。 |

---

## 3. 互引

| 文档 | 关系 |
|------|------|
| [`portfolio-insight.md`](portfolio-insight.md) | **仓位/集中度** **输入** |
| [`monitoring-tasks.md`](monitoring-tasks.md) | **订阅 vs 瞬时** |
| [`trade-assistance.md`](trade-assistance.md) | **提醒后用户选择写** |
| [`boundaries.md`](boundaries.md) | **Disclaimer · 硬边界** |
| [`../../../risk/README.md`](../../../risk/README.md) | **全局风险横切索引**（运营闸 + 对签指针）；**单笔/产品边界** **仍以** **`boundaries`** **为准** |

---

**文档版本**：0.4.1 · **维护**：产品 + 风控/交互 owner · **本版**：§3 **`risk/README`** 互引 **与** **横切索引** **措辞** **对齐**。**顺延 0.4.0** …
