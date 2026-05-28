# Prompt 治理映射（Git 条文 ↔ 运营发布包）

**路径**：`specs/requirements/prompts/governance-map.md`  
**性质**：**索引 SSOT** — 对齐 **Runtime `scenarioId`**、**`library/scenarios/registry.md` 拼装**、**Admin `promptPackId`**。**不**替代 [`prompt-management`](../domains/admin/prompt-management/overview.md) 发布契约。

**产品清单（非 SSOT）**：[`product/prompt-governance-checklist.md`](../../../product/prompt-governance-checklist.md) · **Demo 六段模板**：[`src/admin/src/data/promptBodyTemplates.ts`](../../../src/admin/src/data/promptBodyTemplates.ts)

---

## 1. 双层模型

| 层 | 载体 | 写什么 | 不写什么 |
|----|------|--------|----------|
| **运营发布包** | `pp-*`（Publish） | Identity、场景行为、澄清、输出契约（六段） | Tool API、Billing、Gateway、Canonical、FR 编号堆砌 |
| **Git 条文** | `prompts/*/*.md`、`library/packs/*` | 评审下限、FR/Skill 引用、拼装片段、对账话术 | 替代 Skill Spec 参数表、替代 Runtime 路由 |

**拼装顺序真源**：[`library/ASSEMBLY.md`](./library/ASSEMBLY.md) · [`library/PUBLISH-ALIGNMENT.md`](./library/PUBLISH-ALIGNMENT.md) · [`runtime-injection`](../domains/admin/prompt-management/runtime-injection.md)。

---

## 2. 全局与横切块（非 `scenarioId` 独占）

| `promptPackId` | 类型 | Git / library 对照 | 说明 |
|----------------|------|-------------------|------|
| `pp-system-core` | SYSTEM | [`system/system.md`](./system/system.md)、[`library/packs/core-runtime-root.*`](./library/packs/core-runtime-root.zh-CN.md) | 全局行为；**条文**可含 Tool 铁闸，**Publish 正文**取行为子集 |
| `pp-runtime-clarify` | SYSTEM | [`shared/clarify-user-visible.md`](./shared/clarify-user-visible.md)（**§0 执行体分工**）、[`library/packs/fragment-clarify-user-visible.*`](./library/packs/fragment-clarify-user-visible.zh-CN.md) | 缺参澄清 · **用户可见** · **LLM/规则/组合** · **INV-010** |
| `pp-runtime-output-contract` | SYSTEM | （无单文件；结构化输出边界） | clarify / intent |
| `pp-safety-global` | SAFETY | [`safety/*`](./safety/README.md)、[`fragment-safety.*`](./library/packs/fragment-safety.zh-CN.md) | §7.1 扫闸同窗 |
| — | 拼装注入 | [`confirmation/*`](./confirmation/README.md)、[`fragment-confirmation-type-a.*`](./library/packs/fragment-confirmation-type-a.zh-CN.md) | **不**单独占运营场景包编号 |
| — | 意图片段 | [`intents/*`](./intents/README.md)、`fragment-intent-{trade,analysis,monitoring}.*` | **路由**定意图；**非**各发一包 |

---

## 3. 写路径 · `scenarioId` → `promptPackId`

| `scenarioId` | `promptPackId` | 延展条文（Git · 评审参考） |
|----------------|----------------|---------------------------|
| `trade.spot.limit_order` | `pp-trading-spot-limit` | [`trading/buy.md`](./trading/buy.md) |
| `trade.spot.flash_convert` | `pp-trading-spot-flash` | [`buy.md`](./trading/buy.md)、[`sell.md`](./trading/sell.md) |
| `trade.spot.amend_limit_order` | `pp-trading-spot-amend` | [`buy.md`](./trading/buy.md)、[`cancel.md`](./trading/cancel.md) |
| `trade.futures.market_order` | `pp-trading-futures-market` | [`trading/futures.md`](./trading/futures.md) |
| `trade.futures.limit_order` | `pp-trading-futures-limit` | [`futures.md`](./trading/futures.md) |
| `trade.futures.amend_limit_order` | `pp-trading-futures-amend` | [`futures.md`](./trading/futures.md)、[`cancel.md`](./trading/cancel.md) |
| `trade.futures.take_profit_stop` | `pp-trading-futures-tpsl` | [`futures.md`](./trading/futures.md) |
| `futures.condition.order_create` | `pp-trading-futures-tpsl` | 同上（别名） |
| `margin.cross.market_order` | `pp-trading-margin-market` | [`buy.md`](./trading/buy.md)、[`futures.md`](./trading/futures.md)、[`confirmation/risk-disclosure`](./confirmation/risk-disclosure.md) |
| `margin.cross.limit_order` | `pp-trading-margin-limit` | 同上 |
| `wealth.subscribe` | `pp-trading-wealth-subscribe` | [`flows/wealth-via-agent`](../flows/wealth-via-agent.md)、[`confirmation/high-risk-confirmation`](./confirmation/high-risk-confirmation.md) |
| `wealth.redeem` | `pp-trading-wealth-redeem` | 同上 |
| `trade.spot.oco` / `trade.spot.bracket` | **—**（不交付） | [`buy.md`](./trading/buy.md)；[`product.md`](../product.md) **§非目标** |
| `margin.cross.transfer_in`（示意） | **—**（主站） | [`boundaries`](../domains/agent/exchange-agent/boundaries.md) |

**说明**：`buy.md` / `sell.md` 为 **买卖同窗基准条文**，**≠** 须各发 `pp-trading-buy` / `pp-trading-sell`。  
**按场景速查表**：[`trading/by-scenario.md`](./trading/by-scenario.md)。

---

## 4. 读侧 / 监控 · 统一分析包

| `scenarioId`（族） | `promptPackId` | 能力语义分卷（Git · 非独立发布包） |
|--------------------|----------------|-----------------------------------|
| `market.read_*`、`futures.read_funding` | `pp-analysis-core` | [`market-analysis.md`](./analysis/market-analysis.md)、[`futures.md`](./trading/futures.md)（只读） |
| `research.*` | `pp-analysis-core` | [`sentiment-summary.md`](./analysis/sentiment-summary.md) |
| `market.read_deep_analysis` | `pp-analysis-core` | [`technical-analysis.md`](./analysis/technical-analysis.md) |
| `orders.read_activity`、`portfolio.*`、`wealth.holdings_read`、`wealth.recommend` | `pp-analysis-core` | [`portfolio-read.md`](./analysis/portfolio-read.md) |
| `monitoring.*` | `pp-analysis-core` | [`intents/monitoring.md`](./intents/monitoring.md) |

**拼装**：§1 表仍用 **IA** 等字母；**Publish** 仅 **`pp-analysis-core`** 一份。MNRA Facts → [`market-narrative-runtime`](../market-narrative-runtime/README.md)。

---

## 5. 运营正文六段（Publish）

与 Demo 模板一致（详见 [`promptBodyTemplates.ts`](../../../src/admin/src/data/promptBodyTemplates.ts)）：

1. Identity  
2. Scenario Context（TRADING 必填 `scenarioId` 语义）  
3. Behavioral Rules  
4. Capability Awareness（可选）  
5. Clarify Rules（可选；亦可由 `pp-runtime-clarify` 横切）  
6. Output Contract（可选；亦可由 `pp-runtime-output-contract` 横切）

---

**文档版本**：1.0.1 · **维护**：产品 + Prompt owner · **本版**：**链** [`trading/by-scenario.md`](./trading/by-scenario.md)；CI [`check_governance_map_vs_registry.py`](./library/scripts/check_governance_map_vs_registry.py)；**承** 1.0.0。
