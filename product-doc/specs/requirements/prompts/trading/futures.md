# Trading · Futures（条文）

**路径**：`specs/requirements/prompts/trading/futures.md`。  
**性质**：**写路径 Prompt 下限（合约 / 杠杆族）** — Publish [`prompt-management`](../../domains/admin/prompt-management/overview.md)。

**索引**：[`README`](./README.md)

> **Publish 正文**：[`governance-map.md`](../governance-map.md)（如 `pp-trading-futures-market` / `pp-trading-futures-limit`）。**本文**为 Git **评审下限**，**勿**抄 API/FR 进六段运营正文。

**域宿主**：[`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md)；[`boundaries`](../../domains/agent/exchange-agent/boundaries.md)；[`../confirmation/README`](../confirmation/README.md)；[`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)。  
**操作契约**：合约市价 → [`skill.futures.market_order`](../../skill-specs/futures/skill.futures.market_order.md)；合约限价 → [`skill.futures.limit_order`](../../skill-specs/futures/skill.futures.limit_order.md)；条件离场 → [`skill.futures.take_profit_stop`](../../skill-specs/futures/skill.futures.take_profit_stop.md)。

---

## 1. 前置（在 Spot 之上）

- **开仓 / 平仓 / 加减杠杆 / 调整保证金模式** 等，须 **先**完成域定义的 [`risk-disclosure`](../confirmation/risk-disclosure.md) 与 [`high-risk-confirmation`](../confirmation/high-risk-confirmation.md) **串联**，顺序以 [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md) 为准。  
- **杠杆倍数 / 保证金模式 / 持仓模式** 未说明时：**澄清**或 **保守默认**（**以产品与路由为准**），**禁止**话术隐蔽抬杠杆 — [`illegal-request` §绕过闸门](../safety/illegal-request.md)。  
- **类型 A**：同窗 [`buy.md` §1](./buy.md)。

---

## 2. 执行下限

- **同窗** [`buy.md`](./buy.md) **§2**（写路径、工具、`FR-T09`/`FR-T11`）。  
- **止盈止损 / 条件离场**：**独立** `scenarioId` + [`skill.futures.take_profit_stop`](../../skill-specs/futures/skill.futures.take_profit_stop.md) — **触发条件卡** **与** 即时开平仓 **分离**；**矩阵 `conditionOrder` TBD** → **`FR-T05`**（**禁止** 类型 A 假闭环）。  
- **PNL / 强平距离 / 资金费率**：**只读解释**须 **免责声明**，**不得承诺不死仓或固定收益** — [`exchange-agent/boundaries`](../../domains/agent/exchange-agent/boundaries.md)、[`system/system` §1](../system/system.md)。  
- **爆仓价等数字**：若无接口事实 **不得捏造** — [`risk-disclosure` §2](../confirmation/risk-disclosure.md)、[`hallucination`](../../observability/hallucination.md)。

---

## 3. 拒答

- 合约矩阵缺项 / 所不支持合约 → **`FR-T05`** — [`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md)；[`shared/common-phrases` §1](../shared/common-phrases.md)。

---

## 4. 其它同窗

- **与分析分流 / 防幻觉 / UNKNOWN**：同窗 [`buy.md` §4](./buy.md)。

---

**Publish**：同窗 [`prompt-management/config`](../../domains/admin/prompt-management/config.md)。

**文档版本**：1.5.1-mvp · **维护**：产品 + Prompt owner · **本版**：**§2 条件离场 · 链 S-05**。**承** 1.5.0-mvp。
