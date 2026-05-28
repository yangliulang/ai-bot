# 写路径 · 按 `scenarioId` 索引

**路径**：`specs/requirements/prompts/trading/by-scenario.md`  
**用途**：**一场景一包** 的快速对照表；**避免** 误以为须按 `buy.md` / `sell.md` 各发运营包。

**映射 SSOT**：[`governance-map.md` §3](../governance-map.md#3-写路径--scenarioid--promptpackid) · **拼装表**：[`library/scenarios/registry.md` §2](../library/scenarios/registry.md#2-现货与衍生品写路径2) · **产品清单**：[`product/prompt-governance-checklist.md`](../../../../product/prompt-governance-checklist.md) §三。

> **读侧 / 监控**（`market.read_*`、`research.*`、`monitoring.*` 等）→ **仅** `pp-analysis-core`，见 [`governance-map` §4](../governance-map.md#4-读侧--监控--统一分析包) · [`analysis/README.md`](../analysis/README.md)。

---

## 写路径 · `scenarioId` → `promptPackId`

| `scenarioId` | `promptPackId` | 延展条文（Git · 评审参考） |
|--------------|----------------|---------------------------|
| `trade.spot.limit_order` | `pp-trading-spot-limit` | [`buy.md`](./buy.md) |
| `trade.spot.flash_convert` | `pp-trading-spot-flash` | [`buy.md`](./buy.md)、[`sell.md`](./sell.md) |
| `trade.spot.amend_limit_order` | `pp-trading-spot-amend` | [`buy.md`](./buy.md)、[`cancel.md`](./cancel.md) |
| `trade.futures.market_order` | `pp-trading-futures-market` | [`futures.md`](./futures.md) |
| `trade.futures.limit_order` | `pp-trading-futures-limit` | [`futures.md`](./futures.md) |
| `trade.futures.amend_limit_order` | `pp-trading-futures-amend` | [`futures.md`](./futures.md)、[`cancel.md`](./cancel.md) |
| `trade.futures.take_profit_stop` | `pp-trading-futures-tpsl` | [`futures.md`](./futures.md) |
| `futures.condition.order_create` | `pp-trading-futures-tpsl` | 同上（**路由别名** · 与 TPSL 同窗包） |
| `margin.cross.market_order` | `pp-trading-margin-market` | [`buy.md`](./buy.md)、[`futures.md`](./futures.md)、[`confirmation/risk-disclosure`](../confirmation/risk-disclosure.md) |
| `margin.cross.limit_order` | `pp-trading-margin-limit` | 同上 |
| `wealth.subscribe` | `pp-trading-wealth-subscribe` | [`flows/wealth-via-agent`](../../flows/wealth-via-agent.md)、[`confirmation/high-risk-confirmation`](../confirmation/high-risk-confirmation.md) |
| `wealth.redeem` | `pp-trading-wealth-redeem` | 同上 |

---

## 不交付 / 主站（无运营 `promptPackId`）

| `scenarioId` | 说明 | 条文 |
|--------------|------|------|
| `trade.spot.oco` | **§非目标** · `FR-T05` 拒答 | [`buy.md`](./buy.md) |
| `trade.spot.bracket` | **§非目标** · `FR-T05` 拒答 | 同上 |
| `margin.cross.transfer_in`（示意） | **主站** · 无 Agent 写规范 | [`boundaries`](../../domains/agent/exchange-agent/boundaries.md) |

Registry 拼装表对 OCO/bracket 保留 **占位配方**（**禁止** 默认走完整写闭环）— 见 [`registry.md` §2](../library/scenarios/registry.md#2-现货与衍生品写路径2)。

---

## 横切块（全场景 · 非 `scenarioId` 独占）

| `promptPackId` | 类型 | 说明 |
|----------------|------|------|
| `pp-system-core` | SYSTEM | 全局行为 |
| `pp-runtime-clarify` | SYSTEM | 缺参澄清 |
| `pp-runtime-output-contract` | SYSTEM | clarify / intent 契约 |
| `pp-safety-global` | SAFETY | 护栏 |
| — | 拼装 | [`confirmation/`](../confirmation/README.md) · 类型 A / 风险披露 **不**单独占包编号 |

---

## 阅读顺序（建议）

1. **本表** 定位 `scenarioId` → 运营包  
2. [`buy.md`](./buy.md) §前置～§分流（**同窗基准**，非「只限买入」）  
3. 场景专属：[`sell`](./sell.md) / [`futures`](./futures.md) / [`cancel`](./cancel.md)  
4. Publish 六段：[`promptBodyTemplates.ts`](../../../../src/admin/src/data/promptBodyTemplates.ts)

---

## 上级

[`README.md`](./README.md) · [`../governance-map.md`](../governance-map.md)

---

**文档版本**：1.0.0 · **维护**：产品 + Prompt owner · **本版**：**按 scenario 索引初版**（P2）。
