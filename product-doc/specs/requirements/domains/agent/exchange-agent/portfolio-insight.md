# Exchange Agent · 资产/持仓理解（Portfolio Insight）

**路径**：`specs/requirements/domains/agent/exchange-agent/portfolio-insight.md`。

**职责**：**Portfolio Insight** 能力域：**余额、持仓、敞口、盈亏、风险偏好** 叙事所需的 **子账户 scope 下只读聚合** **与** **展示口径**。**不写** OpenAPI **字段拷贝**。

---

## 1. 只读条目（产品下限）

| 子主题 | 用户价值 | **读能力与编排锚** | 下限 / 门禁 |
|--------|----------|-------------------------------------|-------------|
| **下单与账户活动** | 在途委托、近期成交 **等** | **`tool.orders.*` **开集**；**编排场景** **`orders.read_activity`** **见** [`routing-engine`](../agent-orchestration/routing-engine.md) **§1 读侧表** | **私有读** **须** **`FR-T02`**；**协查** **须** **满足** [`observability` §2.1](../../../observability/overview.md) **总则**（**不** **本条** **复述** **`executionId`**） |
| **风险与保证金快照** | **杠杆率、爆仓距离、币种维度的风险提示输入** | **`tool.account.risk_snapshot`** · `account.read_risk` | **输出仅供用户理解** · **不等价** **[`../../../risk/`](../../../risk/README.md)** **运营规则 SSOT** |
| **盈亏 / 敞口叙事** | 「我赚了多少」「集中度过高吗」 **等** | **专用 **`scenarioId`**：`portfolio.read_pnl_exposure`**（**与 **`orders.read_activity` 并行** **、** **不复用 **`market.read_*`** **）**；数据来自 **§1.1 **`tool.orders.*`** 闭包** + 可选 **`tool.account.risk_snapshot`**（保证金语境），**不得**用 **`tool.market.ticker`** **顶替** **成交盈亏** | **首版粒度**：**(a)** **`asOf`/时间锚** 显式写出；**(b)** **`symbol`/账户粒度** ≤ 用户问句或更粗聚合；**(c)** **无**隐含投顾结论 → [`risk-alerts.md`](risk-alerts.md) **`FR-RA*`**；措辞与 **`billCode`** 以 **`design` `unknown`/`504`** 规则为准，**不**在本表展开 |
| **可买性 / 产品状态**（**理财相邻**） | 与 **`wealth`** **流程**衔接的 **只读核对** | **同窗** [`../../../flows/wealth-via-agent.md`](../../../flows/wealth-via-agent.md) **`asset/pnl` 步** **（若存在）** | **写路径** **`WEALTH_ACTION_REQUIRES_WEB`** → [`boundaries.md §8.3`](boundaries.md) |
| **子账户就绪** | **无就绪** **则无**可信私有读 | **无独立 `scenarioId`**；就绪与计费门禁见 onboarding / **`consume-and-bill`** | [`../onboarding/`](../onboarding/)、[`../../../flows/consume-and-bill.md`](../../../flows/consume-and-bill.md) |

### 1.1 `tool.orders.*` 最小闭包（首版登记 · 与子账户矩阵对签）

**目的**：[`trade-assistance.md §8.3`](trade-assistance.md) **写 **「`**tool.orders.*`（开集）**」——**本节** **钉** **`Portfolio`/`orders.read_activity`** **首版 **须** **覆盖 **之 **读能力上界**。**增删 **`toolId`** **须** **同一 MR** **改** **`trade-assistance §8.3`** **与下文** **`SC-PI01`**。

| `toolId`（登记名） | 用途（产品下限） |
|--------------------|------------------|
| **`tool.orders.open_orders`** | **当前在途委托**（**挂单**）|
| **`tool.orders.history`** **或同窗** **`tool.orders.recent`** | **近期委托/成交**（**粒度** **`24h`/用户窗** **以** **`read-analyze`** **分流**为准）|

**未定名**：交易所 **矩阵** **`operationId` **落定** **再** **`toolId`** **终裁**；**此前** **`tool.orders.open_orders`/`.history`** **为** **`§8.3`** **占位 **示意**。**不得** **以** **`tool.market.*`** **替代** **上述** **两行**。

---

## 2. FR / SC

| ID | 陈述 |
|----|------|
| **FR-PI01** | **私有持仓/订单类回答** **须** **子账户已绑定且** **`FR-T02`** **通过**；**否则** **稳定拒答** **或** **引导开通**（**条文与 Runtime/onboarding 对签**）。 |
| **FR-PI02** | **盈亏/敞口类结论** **不得** **冒充** **个性化投资建议**；**风险偏好** **仅** **可由用户声明或显式交互写入**（**不做**暗推断 **为** **默认事实**）。 |
| **FR-PI03** | **盈亏/敞口答复** **须** **明示** **`asOf`/时间锚** **与** **聚合粒度**（**全仓**/单 **`symbol`/组合）**；**缺**可信数据 → **`FR-T05` **族** **透明拒答** **禁止**编造数字。 |

| ID | **验收要点**（可对签） |
|----|-------------------------|
| **SC-PI01** | **`orders.read_activity`** **会话**：**未** **`FR-T02` **就绪** → **不出现** **`trading.exchange_private` **success** **`exchangeOutcome`**；**用户侧** **`FR-T05` **或可执行 **开通 Deeplink**。 |
| **SC-PI02** | **`portfolio.read_pnl_exposure`**：**同一** **应答** **含** **`asOf`/粒度** **元数据块** **或 **等价结构化字段**；**抽检** **10** **条** **无**裸数字 **无时标**。 |
| **SC-PI03** | **审计**：**无 **`read_skill`/投顾话术** **冒充** **`FR-PI02`** — **不出现** 「保证收益」「适合你」**默认**句式 **（对齐 **[`boundaries`](boundaries.md)** **Disclaimer**）。 |

---

## 3. 互引

| 文档 | 关系 |
|------|------|
| [`intents.md`](intents.md) | 账户/持仓类意图；**盈亏类** **叙事口径** **见** **本文 §1** |
| [`risk-alerts.md`](risk-alerts.md) | **输入信号**（仓位/保证金） |
| [`trade-assistance.md`](trade-assistance.md) | **只读校验 → 写** |
| [`../onboarding/`](../onboarding/) | **子账户/API 就绪** |
| [`boundaries.md`](boundaries.md) | **可读边界** **与** **授权展示** |

---

**文档版本**：0.4.0 · **维护**：产品 + Agent Runtime owner · **本版**：**弱执行面** **泄漏**（**`executionId` 直链**）**—** **改** **指** **`observability`/`agent-orchestration`**；**§1 能力** **保持** **0.3.2** **闭包**。
