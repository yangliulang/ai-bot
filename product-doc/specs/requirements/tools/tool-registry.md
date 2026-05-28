# Tool Registry（仓库级索引）

**真源优先级**：[`design/api.md`](../../design/api.md)（PATH / `operationId`） **>** [`trade-assistance.md` §4 / §8](../domains/agent/exchange-agent/trade-assistance.md)（`skillId`/`toolId` 叙事与类定义） **>** 本文件与 [`schemas/`](./schemas/)。**冲突时以前两者 MR 为准**，本目录只做对齐与导航。

**命名说明**：[`runtime-contract`](../domains/admin/tool-management/runtime-contract.md) 等文可用 **蛇形示例**（如 `get_balance`）说明 **风险与重试**；**登记名**仍以 **`trade-assistance` §8** 的 **`tool.*` / `skill.*`** 为准（或矩阵 **`operationId`** 终裁）。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. A 类写技能（`skillId`）

**类定义**：[§8.1](../domains/agent/exchange-agent/trade-assistance.md#ta-81) · **行级 SSOT**：§4「技能登记」· **与 §8.2 同行数 / 顺序**：[§8.2](../domains/agent/exchange-agent/trade-assistance.md#ta-82)。

| `skillId`（与 §8.2 一致） | 流程权威 |
|---------------------------|----------|
| `skill.spot.flash_convert`（族 · 可分子 `.buy` / `.sell`） | [`trade-via-agent.md` § 现货/闪兑](../flows/trade-via-agent.md) |
| `skill.spot.limit_order` | 同上 |
| `skill.spot.oco` / `skill.spot.bracket` | 同上 · **OCO/bracket**：[ **`product.md` §非目标](../product.md) **—** **本阶段 Agent **不交付写**；**`FR-T05`/主站/分步** |
| `skill.futures.market_order` / `skill.futures.limit_order` | 同上 |
| `skill.futures.take_profit_stop`（或 `condition_order_create`） | 同上 |
| `skill.margin.cross_market_order` / `skill.margin.cross_limit_order` | 同上 · 全仓 |
| `skill.margin.transfer_*`（如 `skill.margin.transfer_spot_to_cross`） | 同上 · 划转 |
| `skill.wealth.subscribe` / `skill.wealth.redeem` | [`wealth-via-agent.md`](../flows/wealth-via-agent.md) |

**用户确认**：A 类 **须** Telegram **类型 A**（[`ADR-001`](../../design/adr/001-telegram-confirm-before-coobit-write.md)）。

---

## 2. B 类只读工具（`toolId`）

**类定义**：[§8.1](../domains/agent/exchange-agent/trade-assistance.md#ta-81) · **登记表**：[§8.3](../domains/agent/exchange-agent/trade-assistance.md#ta-83) · **编排映射**：[`routing-engine.md` §1](../domains/agent/agent-orchestration/routing-engine.md)。

| `toolId`（§8.3 登记名） | 备注 | 片段 Schema（若有） |
|-------------------------|------|---------------------|
| `tool.market.ticker` | 实时价量 | — |
| `tool.analytics.symbol_deep_dive` | K 线/深度 + 解读 | — |
| `tool.market.orderbook` / `tool.market.recent_trades` | 盘口 / 公共成交 | — |
| `tool.orders.open_orders` / `tool.orders.history` 等 | **终名以矩阵为准** | — |
| `tool.account.risk_snapshot` | 保证金 / 风险输入 | — |
| `tool.futures.funding_summary` | Funding 摘要 | — |
| `tool.feed.rss_digest` / `tool.calendar.macro_window` | 可选只读 | — |
| `tool.futures.liquidation_context` | 爆仓语境 · **不写** `fapi` 开仓 | — |
| `tool.wealth.product_recommend` 等 | 理财只读 | — |
| *账户余额族（示意）* | 矩阵 **`operationId`** 锚定后与 **蛇形 `get_balance` 示例** 同窗 | [`get-balance.schema.json`](schemas/get-balance.schema.json) |
| *仓位/持仓只读（示意）* | 同上 | [`get-position.schema.json`](schemas/get-position.schema.json) |

---

## 3. C 类外网 / 分析（`toolId`）

**登记表**：[§8.4](../domains/agent/exchange-agent/trade-assistance.md#ta-84) · **ADR / 预算**：[`contract-closure` CC-P1-02](../contract-closure.md)、[`agent-context`](../domains/agent/agent-context/overview.md)（预算 **同窗** §8.4）。

| 示例 `toolId` |
|---------------|
| `tool.web.social_sentiment`、`tool.web.news_search`、`tool.web.search`、`tool.i18n.translate` |

---

## 4. 写路径片段 Schema（示意 · A 类背后 HTTP）

**仅**用于文档化常见 **写** 入参形状；**冻结字段**以 **OpenAPI + `trade-assistance` / 矩阵** 为准。

| 示意文件名 | 说明 |
|------------|------|
| [`create-order.schema.json`](schemas/create-order.schema.json) | 下单类（MEDIUM / 禁止无脑自动 Retry） |
| [`cancel-order.schema.json`](schemas/cancel-order.schema.json) | 撤单类 |

---

## 5. 自动化与 Pull

[§8.5](../domains/agent/exchange-agent/trade-assistance.md#ta-85) · [`automation-alerts.md`](../flows/automation-alerts.md)。**Pull** 只读 **须** 已登记 **§8.3** `toolId` + PATH。
