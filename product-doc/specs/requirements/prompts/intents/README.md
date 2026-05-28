# `intents/` · 索引（MVP）

**路径**：`specs/requirements/prompts/intents/README.md`。

本目录三篇对应 **Runtime MVP** 下三路 **用户意图**：**交易写 / 只读分析 / 订阅式监控**。语义簇 **完整表** 仍以 [`exchange-agent/intents`](../../domains/agent/exchange-agent/intents.md) **为准**；本文 **仅**做 Git 侧条文锚点。

**Publish**：意图 **分类** 由 **Runtime 路由**；[`library/packs/fragment-intent-*`](../library/packs/fragment-intent-trade.zh-CN.md) 为 **拼装片段**，**非** `pp-intent-trade` 等独立运营包。映射见 [`governance-map.md` §2](../governance-map.md#2-全局与横切块非-scenarioid-独占)。

---

## 文件

| 文件 | 用途 |
|------|------|
| [`trade.md`](./trade.md) | 写路径意图 → [`../trading/README.md`](../trading/README.md) |
| [`analysis.md`](./analysis.md) | 只读分析意图 → [`../analysis/README.md`](../analysis/README.md) |
| [`monitoring.md`](./monitoring.md) | 告警 / 订阅意图（**无**独立 `prompts/monitoring/` 子树） |

---

## 阅读顺序（建议）

1. [`exchange-agent/intents`](../../domains/agent/exchange-agent/intents.md) **§1～§3**（语义与歧义 **SSOT**）  
2. [`trade.md`](./trade.md) ↔ [`confirmation/README.md`](../confirmation/README.md)  
3. [`analysis.md`](./analysis.md) ↔ [`../analysis/README.md`](../analysis/README.md) ↔ [`system/system.md`](../system/system.md) §2（**记忆管理意图** → **analysis §6**）

---

## 路由终裁

[`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)

---

## 关单派工 · AC-09 检核（索引）

[`closure-remaining` §7.2～§7.4](../../closure-remaining.md#cc-ac09-closure-matrix) · **[§7.5](../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../closure-remaining.md#cc-closure-exec-checklist)** — **与** [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)、[`implementation-alignment` §8～§13](../../domains/agent/agent-orchestration/implementation-alignment.md) **同窗**（**非**独立 DoD）。

---

## 实现向：结构化意图草案（评审）

**产品下限字段表**与 **识别→分类→路由** 实现约定 → [`../../domains/agent/agent-orchestration/implementation-alignment.md`](../../domains/agent/agent-orchestration/implementation-alignment.md) **§8～§9**；**GWT / 对客三闸 / eval 束** → **同文** **§12～§13**。

---

## 上级

[`../README.md`](../README.md)

---

**文档版本**：1.2.5 · **维护**：产品 + Prompt owner · **本版**：**关单链** **`closure-remaining` §7.2～§7.4 · §7.5 · §7.6（AC-09 + 闭环路径 + MR 勾选）**。**承** 1.2.4。
