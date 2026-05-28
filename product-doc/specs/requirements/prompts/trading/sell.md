# Trading · Sell（条文）

**路径**：`specs/requirements/prompts/trading/sell.md`。  
**性质**：**写路径 Prompt 下限（卖出）** — Publish [`prompt-management`](../../domains/admin/prompt-management/overview.md)；技能映射 [`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md)。

**索引**：[`README`](./README.md)

> **Publish 正文**：[`governance-map.md`](../governance-map.md)。**本文**为 **卖/减仓** 同窗评审条文，**≠** 独立运营包；写路径 Publish 见 **§3 映射表**（按 `scenarioId`）。

**域宿主**：同窗 [`buy.md`](./buy.md) **§2**；[`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)；[`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)。  
**操作契约**：市价/闪兑 → [`skill.spot.flash_convert`](../../skill-specs/spot/skill.spot.flash_convert.md)；限价 → [`skill.spot.limit_order`](../../skill-specs/spot/skill.spot.limit_order.md)。

---

## 1. 前置

- **交易对**、**卖方向**、**数量或名义**；「**全仓 / 清仓**」须映射为 **路由允许语义**，并触发 [**`high-risk-confirmation`**](../confirmation/high-risk-confirmation.md)、[**`risk-disclosure`**](../confirmation/risk-disclosure.md) **若域定义为高风险 / 大额**。  
- **可用余额 / 可卖数量 / 冻结**：不足时 **不得**编造可成交；错误复述同窗 [`error-normalization`](../../Runtime/error-normalization.md)。  
- **类型 A**：同窗 [`buy.md` §1](./buy.md)。

---

## 2. 执行下限

- **同窗** [`buy.md`](./buy.md) **§2**（写路径、工具登记、`FR-T09`/`FR-T11`）。  
- **卖出侧专有**：最小成交量、合约平仓 vs 减仓、`reduce-only` 语义 — **仅以** [`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md) **与** [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md) **为准**，话术 **不**发明参数名。

---

## 3. 拒答

- **`FR-T05`** / 矩阵 **`TBD`** — [`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md)；[`shared/common-phrases` §1](../shared/common-phrases.md)。

---

## 4. 其它同窗

- **与分析分流 / 防幻觉 / UNKNOWN**：同窗 [`buy.md` §4](./buy.md)。

---

**Publish**：同窗 [`prompt-management/config`](../../domains/admin/prompt-management/config.md)。

**文档版本**：1.5.0-mvp · **维护**：产品 + Prompt owner · **本版**：**§2 专有句 Markdown**。
