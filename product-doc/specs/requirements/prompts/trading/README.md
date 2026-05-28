# `trading/` · 索引（MVP）

**路径**：`specs/requirements/prompts/trading/README.md`。

本目录四篇为 **现货 / 合约 / 撤单** 等 **写路径 Prompt 条文**（[`buy`](./buy.md)、[`sell`](./sell.md)、[`futures`](./futures.md)、[`cancel`](./cancel.md)）。**意图宿主**：[`../intents/trade.md`](../intents/trade.md)。**工具 / skill SSOT**：[`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md)。

> **治理升级（2026-05）**：**运营发布** 按 **`scenarioId` → TRADING 包**，映射 [`governance-map.md` §3](../governance-map.md#3-写路径--scenarioid--promptpackid) · 产品清单 [`product/prompt-governance-checklist.md`](../../../../product/prompt-governance-checklist.md)。`buy`/`sell` 为 **条文同窗基准**，**≠** 须各发独立发布包。

---

## 写作约束（全局）

| 约束 | 文档 |
|------|------|
| **步骤序 · SC-TA** | [`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md)、[`trade-assistance` §2](../../domains/agent/exchange-agent/trade-assistance.md) |
| **类型 A / 风险 / 高危** | [`../confirmation/README.md`](../confirmation/README.md) |
| **`scenarioId`** | [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md) |
| **子账户 scope** | [`exchange-agent/overview` FR-T01/T02](../../domains/agent/exchange-agent/overview.md) |
| **Skill 操作契约（L0）** | [`skill-specs/README`](../../skill-specs/README.md) — 现货 / 合约 / 全仓 / 理财 **同窗** [`skill-specs` §2](../../skill-specs/README.md#2-目录与-mvp-清单s-01s-09) |

---

## 文件

| 文件 | 典型路由语义（示意） |
|------|----------------------|
| [`by-scenario.md`](./by-scenario.md) | **`scenarioId` → `pp-trading-*` 全表**（优先查此表，再读条文） |
| [`buy.md`](./buy.md) | 买入 / 市价或限价入口；**§2–§4 为其它写场景同窗基准** |
| [`sell.md`](./sell.md) | 卖出 / 减仓 / 全仓澄清 |
| [`futures.md`](./futures.md) | 合约开仓、平仓、杠杆调整叙事 |
| [`cancel.md`](./cancel.md) | 撤单 |

---

## 阅读顺序（建议）

1. [`by-scenario.md`](./by-scenario.md) — 确认 **运营包编号** 与 `scenarioId`  
2. [`buy.md`](./buy.md) §前置～§执行下限～§分流  
3. [`sell.md`](./sell.md) → [`futures.md`](./futures.md) → [`cancel.md`](./cancel.md) **同窗 buy §4**

---

## 上级

[`../README.md`](../README.md)

---

**文档版本**：1.0.1 · **维护**：产品 + Prompt owner · **本版**：**链** [`by-scenario.md`](./by-scenario.md)；**承** 1.0.0。
