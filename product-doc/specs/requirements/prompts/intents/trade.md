# Intent · Trade（条文）

**路径**：`specs/requirements/prompts/intents/trade.md`。  
**性质**：**意图识别侧下限** — `scenarioId` / 步骤 DAG **SSOT 不在本文**；终裁见 [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)、[`exchange-agent/intents`](../../domains/agent/exchange-agent/intents.md)。

**域宿主**：[`exchange-agent/intents` §1～§3](../../domains/agent/exchange-agent/intents.md)；[`trade-assistance` §2](../../domains/agent/exchange-agent/trade-assistance.md)；[`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)；[`agent-orchestration/overview`](../../domains/agent/agent-orchestration/overview.md)（**`FR-AO02`** 单轮主意图）。

---

## 1. 语义归属（示意）

**典型话术簇**（摘录）：买入/卖出、市价/限价、合约/杠杆、止盈止损、闪兑等 — **完整表** [`exchange-agent/intents` §1](../../domains/agent/exchange-agent/intents.md)。

**用户目标**：在 **确认链** 通过后完成 **子账户 scope** 侧 **写** — [`trade-assistance` §2](../../domains/agent/exchange-agent/trade-assistance.md)。

---

## 2. 与其它意图 / 流程的歧义

| 混淆 | 分流 |
|------|------|
| **「提醒我…」** vs **「马上买/卖」** | 前者 → [`monitoring.md`](./monitoring.md)；后者 → **本意图** → [`../trading/README.md`](../trading/README.md) |
| **「条件单 / 网格 / 全策略机器人」** | **非 MVP 全闭环** → **澄清 + `FR-T05` 式边界**，**不**假称已托管成交 |
| **行情追问** vs **下单** | 仅询价 → [`analysis.md`](./analysis.md)；出现 **委托参数 / 明确交易动词** → **本意图** |
| **理财申购赎回 / 活期定期**（[`intents` §1 理财行](../../domains/agent/exchange-agent/intents.md)） | **意图仍属「所内写」族**，但 **`scenarioId` / 步骤**走 [`wealth-via-agent`](../../flows/wealth-via-agent.md) 与 [`boundaries` §8.3](../../domains/agent/exchange-agent/boundaries.md)；**不**与现货 [`../trading/README.md`](../trading/README.md) 四条文 **混为一谈**，除非路由显式映射 |

---

## 3. 落地正文（`prompts/trading/`）

**索引**：[`../trading/README.md`](../trading/README.md)。

| 文件 | 用途 |
|------|------|
| [`buy.md`](../trading/buy.md) | 买入 / 市价或限价入口（[`§2`](../trading/buy.md) 执行下限同窗其它写场景） |
| [`sell.md`](../trading/sell.md) | 卖出 / 减仓 / 全仓澄清 |
| [`futures.md`](../trading/futures.md) | 合约开仓平仓 / 杠杆叙事 |
| [`cancel.md`](../trading/cancel.md) | 撤单 |

**写侧防幻觉**：未 **`call_exchange_write`（或等价写路径）成功闭环** → **不得声称已成交 / 已撤单** — [`../safety/privilege.md`](../safety/privilege.md)、[`hallucination`](../../observability/hallucination.md)。

---

## 4. 确认与路由（硬闸）

- **写路径**必经 [`confirmation`](../confirmation/README.md) 链（类型 A / 风险 / 高危以 [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md) 为准）。  
- **路由键**：[`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)。

---

## 5. 能力缺项 / 拒答

- **矩阵 `TBD` / 未开通** → **`FR-T05`** — [`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md)；句式锚 [`shared/common-phrases` §1](../shared/common-phrases.md)。

---

**文档版本**：1.6.0-mvp · **维护**：产品 + Prompt owner · **本版**：理财行同窗 **`trading/README`**。
