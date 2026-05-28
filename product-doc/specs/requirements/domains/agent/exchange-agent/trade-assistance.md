# Exchange Agent · 交易辅助（Trade Assistance）

**路径**：`specs/requirements/domains/agent/exchange-agent/trade-assistance.md`。

**职责**：**交易 Capability**：**下单/撤单/改单/理财写** **与紧邻只读** 的 **用户确认顺序、写边界、`skillId`/`toolId` 能力登记表**。**`scenarioId` 编排寄存器** → **[`routing-engine.md`](../agent-orchestration/routing-engine.md)**；**`executionId`/`agent.tool.call` 归因下限** → [`execution-lifecycle.md`](../agent-orchestration/execution-lifecycle.md)；**写路径验收 `SC-TA*`** → [`confirmation-flow.md`](../agent-orchestration/confirmation-flow.md)（**不与本文混层**）。

**矩阵与 ADR**：[`../../../../design/api.md`](../../../../design/api.md)、[`../../../../design/adr/001-telegram-confirm-before-coobit-write.md`](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)。**承接**原 **`trading-skills.md` / `tools.md`** 之 **§8 登记形态**。

**对上 Coobit HTTP · 官方 Skill 宿主**：**`skillId`/`toolId`** **能力与 §4·§8 登记不变**。**实现上**优先 **经由** ChainUp **`openapi-ai` 官方包**（`skills/*/SKILL.md`、CLI、可选 MCP）**调用** **`design/api`** **与白名单所载 PATH**，**替代**本产品侧 **同源重复的 OpenAPI 薄封装**。**网关白名单 · 矩阵 · FR-T0x · 计费** — **`integrations/exchange/overview.md`**（**§ Coobit 官方 openapi-ai 采纳**）、**[`agent-coobit-api-allowlist.md`](../../../integrations/exchange/agent-coobit-api-allowlist.md)**、`Runtime/*`、`consume-and-bill`。**Cursor `.cursor/skills/`** vs **`skillId`** **仍见 [`overview.md`](overview.md) §2**.

**端到端鸟瞰 · 架构语言**：[`flow/e2e-closed-loop.md`](../../../../../flow/e2e-closed-loop.md) **文首「架构语言」** → [`architecture` §「与通用 Agent 栈之对照」](../../../../design/architecture.md)。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 范围

| 属于本文 | 不属于本文（链向） |
|----------|-------------------|
| **A/B/C** 类能力 **定义**、**写前读规范**、**§8 工具/技能登记** **形态** | **子账户就绪 / VIP / 计费阻断** → [`../../../flows/consume-and-bill.md`](../../../flows/consume-and-bill.md)；**旧 **`§10.x`/`FR-*`** 回迁表** → [`overview-legacy-migration.md`](overview-legacy-migration.md) |
| **自然语言成交** **七段**/专节 **产品顺序** 的 **技能引用** | **逐步骤 S{n}** **权威** → [`../../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) |
| **理财八步** 中的 **技能与类型 A** **引用** | **理财专节 SSOT** → [`../../../flows/wealth-via-agent.md`](../../../flows/wealth-via-agent.md) |
| **条件单 / Pull / 任务** 与 **工具 §8.3～8.5** **对签** | **触发→通知→写** → [`../../../flows/automation-alerts.md`](../../../flows/automation-alerts.md) |

---

## 2. 硬约束（摘录）

| ID | 含义（下限） |
|----|----------------|
| **FR-T11** | **任一** **`call_exchange_write`** **前** **须** **已完成** **`read_skill_operation_spec`** **且** **类型 A** **已通过**（**Telegram** 等渠道 **先于写**，见 [`../telegram/overview.md`](../telegram/overview.md) **§2.5 · 类型 A**（总则 **§2～§2.6**））。 |
| **FR-T09** | **每个须单独呈给用户的「写意图」** **须先发** **[`../telegram/overview.md`](../telegram/overview.md) §2.5 · 类型 A** 并得到 **明示确认** 后方可调 **[`design/api.md`](../../../../design/api.md)** **矩阵** **`R/W=W`**。**例外（逻辑改单）**：**一次** **类型 A** **可授权** **顺序** **多笔** **`R/W=W`**（**先撤后下**），**中间** **不** **再** **插入** **第二次** **类型 A** — **须** **同窗** [**ADR-001 §5**](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)、[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单**、**§8.1** **类 A 定义**。**单笔/单日限额**，超限 **透明拒答**（**禁止静默写**）；**`FEATURE_TRADING`/`FEATURE_AGENT_*`** **同窗**。**七步流程与验收表**：[`trade-via-agent.md`](../../../flows/trade-via-agent.md)；**同窗** **FR-T11** 与 [**ADR-001**](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)。 |
| **FR-TS07** | **每一条** **A 类写** **`skillId`** **在登记表中** **单行可查**：**`skillId`**、**PATH 摘要**（或 **`design`** **矩阵锚**）、**`skillSpecVersion`** **初值/变更规则** — **行级 SSOT**：**§4**；**可读索引**：**§8.2**；**脚注**：**[脚注 · FR-TS07](#footnotes-fr-ts07)**。 |
| **FR-T07**（槽位 · 产品与编排交界） | **必填槽位/澄清** **`FR-AO02`** **同窗** [`../agent-orchestration/overview.md`](../agent-orchestration/overview.md)；本文 **不写** **`scenarioId` 寄存器** **正文**。 |

**验收**：**`FR-T09`/`FR-T11` 抽检** **`SC-TA01`、`SC-TA02`** → [`../agent-orchestration/confirmation-flow.md`](../agent-orchestration/confirmation-flow.md)。

---

## 2.5 Runtime 对齐（交易所视图）

**订单/余额视图真相源**：**须** **同窗** **[`Runtime/reconciliation.md`](../../../Runtime/reconciliation.md)** §1 **冻结矩阵**（**WS 优先 / REST 兜底** **由矩阵赋值**，**不在** **`design`** **正文重复承诺**）。  
**市价单无 WS / UNKNOWN**：**须** **同窗** **[`Runtime/unknown-state.md`](../../../Runtime/unknown-state.md)**、**[`Runtime/error-normalization.md`](../../../Runtime/error-normalization.md)**；**REST 查单 PATH** **登记** → **[`design/api.md`](../../../../design/api.md)** **「REST ↔ WebSocket 对账」专节** **与** **endpoint 矩阵** **同行**。  
**下限**：**依赖私有 WS** **刷新订单态** 的 **工具/Capability**，**未列入** **矩阵 + `design` 对账表** **且** **矩阵仍为 `TBD`** 时 — **不承诺** **闭环终态**。

---

## 2.6 与 Execution Gateway（统一交易语义 · ADR-004）

**`skillId` / `toolId` 登记** **表达「产品能力与意图面」**；**对交易所 HTTP 的落地** **须** **经由** **Canonical 命令与 Adapter**（**不** **在 Skill 正文或 Prompt 中** **固化** **某一交易所专有字段名为唯一真源**）。

**设计 SSOT**：[**`canonical-trading-model.md`**](../../../../design/canonical-trading-model.md) · **ADR**：[**`004-intent-centric-execution-and-canonical-trading-model.md`**](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)。**V1 `venue`** **仅** **`coobit`**；**§4 矩阵 PATH 列** **在过渡期** **仍为 Coobit Adapter 实现索引** **直至** **同窗填 `canonicalOp` 列**（**[`contract-closure` CC-P1-07](../../../contract-closure.md#cc-p1-07)**）。

---

## 3. 标识符（宿主本文者）

| 字段 | 说明 |
|------|------|
| **`skillId`** | **A 类写** **登记名**；**须** **`read_skill_operation_spec`** **可解析**。 |
| **`toolId`** | **B/C** **调用** **稳定名**；**须** **`design/api`** **或** **§8.3～8.4** **有锚**。 |
| **`skillSpecVersion`** | **技能《操作规范》** **版本戳** — [**`prompt-management`**](../../admin/prompt-management/overview.md)。 |

**编排键 `scenarioId`（全表 SSOT）**：[`../agent-orchestration/routing-engine.md`](../agent-orchestration/routing-engine.md)。

---

## 4. 技能（Skill）· 登记结构（A 类写）

**目的**：满足 **契约收口** [`../../../contract-closure.md`](../../../contract-closure.md) **§1 第 2 款**（**`FR-TS07` 单行登记**）。**对应 **`scenarioId` **寄存器**：[`routing-engine.md`](../agent-orchestration/routing-engine.md) **§2～§3**。**OpenAPI** **仍以** [`../../../../design/api.md`](../../../../design/api.md) **为准**。**若有 **`skill.spot.flash_convert.buy` / `.sell`** **等细分子名**，**须** **同一 MR** **更新 §4 **与 **§8.2**。

**`read_skill_operation_spec` 操作规范 SSOT**：[`skill-specs/README.md`](../../../skill-specs/README.md) — **与下表同序**；**金样** [`skill.spot.limit_order`](../../../skill-specs/spot/skill.spot.limit_order.md)。

| `skillId` | 业务线 / 说明 | `design` 矩阵锚（PATH 摘要） | 操作规范 | `skillSpecVersion` |
|-----------|----------------|------------------------------|----------|--------------------|
| **`skill.spot.flash_convert`**（**族**；可分子 `*.buy` / `*.sell`） | **现货市价 / 闪兑**（**无**合约/全仓借措辞） | **写**：以矩阵 **币币现货市价/闪兑** 行 **为准**（**非**独立「第二条市价写」） | [**`skill.spot.flash_convert`**](../../../skill-specs/spot/skill.spot.flash_convert.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.spot.limit_order`** | **现货限价** | **`POST /sapi/v2/order`**；撤单 **`POST /sapi/v2/cancel`** | [**`skill.spot.limit_order`**](../../../skill-specs/spot/skill.spot.limit_order.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.spot.amend_limit_order`** | **现货限价 · 逻辑改单**（**无 amend API**：**单次类型 A 后** **`cancel`→`order`**） | **同窗** **币币行**；**流程** [`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单** | [`skill.spot.amend_limit_order`](../../../skill-specs/spot/skill.spot.amend_limit_order.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.spot.oco`** | **现货 OCO**（**一腿成交或撤销另一腿**；**分型以矩阵为准**；**本产品阶段 Agent 不写闭环**，见 **[`product.md`](../../../product.md) §非目标**） | **矩阵 OCO 行** · **`PATH` `TBD`** **≠** **须实现** · **`FR-T05`/`主站`/分步** **必选** | **拒答** · 无 MVP 正文 | **0.1.0-draft** |
| **`skill.spot.bracket`** | **现货 bracket**（**入场 + 保护腿**；**分型以矩阵为准**；**本产品阶段 Agent 不写闭环**，见 **`product.md` §非目标**） | **矩阵 bracket 行** · **`FR-T05`/`主站`/分步** **必选** | **拒答** · 无 MVP 正文 | **0.1.0-draft** |
| **`skill.futures.market_order`** | **合约市价** | **`POST /fapi/v1/order`** | [**`skill.futures.market_order`**](../../../skill-specs/futures/skill.futures.market_order.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.futures.limit_order`** | **合约限价** | **`POST /fapi/v1/order`** | [`skill.futures.limit_order`](../../../skill-specs/futures/skill.futures.limit_order.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.futures.amend_limit_order`** | **合约限价 · 逻辑改单**（**无对称 amend 时**：**单次类型 A 后** **`cancel`→`order`**） | **同窗** **合约行**；**流程** [`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单** | [`skill.futures.amend_limit_order`](../../../skill-specs/futures/skill.futures.amend_limit_order.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.futures.take_profit_stop`**（**或** **`condition_order_create`**） | **合约止盈止损 / 条件离场** | **`POST /fapi/v1/conditionOrder`**（**以矩阵为准**） | [`skill.futures.take_profit_stop`](../../../skill-specs/futures/skill.futures.take_profit_stop.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.margin.cross_market_order`** | **全仓杠杆 · 市价** | **`POST /sapi/v2/margin/order`**（**与** **`design`** **cross 行** **对签**） | [`skill.margin.cross_market_order`](../../../skill-specs/margin/skill.margin.cross_market_order.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.margin.cross_limit_order`** | **全仓杠杆 · 限价** | 同上 | [`skill.margin.cross_limit_order`](../../../skill-specs/margin/skill.margin.cross_limit_order.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.margin.transfer_*`**（**示意** **`skill.margin.transfer_spot_to_cross`**） | **全仓 · 现货↔全仓划转** | **`universal_transfer` / `asset/transfer`**（**矩阵与** [`boundaries.md`](boundaries.md) **`TRANSFER_REQUIRES_WEB`**） | 主站 · 无 Agent 写规范 | **随首版登记 MR** |
| **`skill.wealth.subscribe`** | **理财申购** | **理财矩阵**（**缺项** → **主站回退码**） | [`skill.wealth.subscribe`](../../../skill-specs/wealth/skill.wealth.subscribe.md) · **contract-complete** | **随首版登记 MR** |
| **`skill.wealth.redeem`** | **理财赎回** | 同上 | [`skill.wealth.redeem`](../../../skill-specs/wealth/skill.wealth.redeem.md) · **contract-complete** | **随首版登记 MR** |

---

## 5. 工具（Tool）· 与矩阵关系

- **B 类**（子账户/所内 **只读**）：**须** **`design/api.md`** **矩阵** **已列 PATH** **或** **等价公开契约**。**`toolId`** **见 §8.3**。  
- **C 类**（外网等）：**须** **`toolRiskLevel`**、速率、Disclaimer、**`agent-context`** **预算** **同窗** §8.4 **与** **CC-P1-02**。  
- **运营镜像**：[`../../admin/tool-management/overview.md`](../../admin/tool-management/overview.md) — **不**另造 **`toolId`**。

---

## 6. 登记表 SSOT 形态（CC-P1-03）

**裁断**：[`../../../../design/adr/002-tool-skill-registry-ssot.md`](../../../../design/adr/002-tool-skill-registry-ssot.md)（**ADR-002**）。**closure** **[CC-P1-03](../../../contract-closure.md)** **跟踪矩阵 MR 与 DB 镜像同窗**。  
**本版**：**以** **`design/api.md` + 本文 §4/§8 表** **为写入入口**；**实现 registry** **须** **与** **上述** **幂等对齐**。

---

## 7. 互引

| 文档 | 关系 |
|------|------|
| [`intents.md`](intents.md) | 成交类意图 **进入**本域 |
| [`market-intelligence.md`](market-intelligence.md) | 从洞察 **升级写**的分流 |
| [`portfolio-insight.md`](portfolio-insight.md) | 私有读校验 |
| [`monitoring-tasks.md`](monitoring-tasks.md) | **条件触发**后的 **落地写**衔接 |
| [`boundaries.md`](boundaries.md) | **`WEALTH_ACTION_REQUIRES_WEB`** 等 **主站回退** |
| [`../../../tools/tool-registry.md`](../../../tools/tool-registry.md) | **仓库级**工具索引（**不替代** §8） |

---

## 8. 工具与能力分卷（**`toolId` / B·C · A**）

**`toolId`/`skillId` 能力登记 SSOT**。**编排路由** → [`routing-engine.md`](../agent-orchestration/routing-engine.md)；**`agent.tool.call`/`executionId` 归因下限** → [`execution-lifecycle.md`](../agent-orchestration/execution-lifecycle.md)。**flows / tool-management** **仍引** **`trade-assistance` §8.x**。**例名** **可**来自 **`trade-via-agent`** **`read_skill_operation_spec`** **列**。

<span id="ta-81"></span>

### 8.1 类定义（A / B / C）

| 类 | 定义 | **须**确认的写？ |
|----|------|------------------|
| **A** | **经用户类型 A（[`telegram/overview` §2.5](../telegram/overview.md)）** 后发起的 **Coobit 私有写**（下单/撤单/改单/理财写/划转写等 **`call_exchange_write`**） | **是** — **以「用户授权单元」计**：**单笔写意图** **各** **须** **一次** **类型 A**；**逻辑改单**（**先撤后下**）**为** **单次** **类型 A** **授权下** **顺序多笔** **`call_exchange_write`** — [`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单**、[**ADR-001 §5**](../../../../design/adr/001-telegram-confirm-before-coobit-write.md) |
| **B** | **子账户 scope** 或 **`design`** **已冻结** **之所内只读**（行情/挂单/持仓/盘口等 **`call_exchange_read`** **族**） | **否** |
| **C** | **外网检索、舆情、通用搜索、翻译** 等 **不经所内撮合** **之能力** | **否**（**须有**合规/速率/**上下文**下限） |

**默认**：用户 **仅询价/分析** **不得** **静默升格为 A**；**升格写** → **切入** **`trade-via-agent`** **专节** **（编排键见 [`routing-engine.md`](../agent-orchestration/routing-engine.md)）**。

<span id="ta-82"></span>

### 8.2 A 写 · 理财 · 现货 / 合约 / 杠杆（与 §4 对签）

**行数** **与** **§4** **一一对应**（**每行** **一个** **主** **`skillId`** **登记项**；**止盈止损** **二选一** **分型** **与** **§4** **同格**）。

| `skillId` | 流程权威 |
|-----------|----------|
| **`skill.spot.flash_convert`（族）** | [`../../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) **开篇四轨** |
| **`skill.spot.limit_order`** | 同上 **专节 · 现货限价** |
| **`skill.spot.amend_limit_order`** | 同上 **专节 · 逻辑改单**（**币币**） |
| **`skill.spot.oco`** | 同上 · **OCO**（**矩阵载行前** **仅登记** **不承诺**） |
| **`skill.spot.bracket`** | 同上 · **bracket**（**矩阵载行前** **仅登记** **不承诺**） |
| **`skill.futures.market_order`** | 同上 **专节 · 合约交易** |
| **`skill.futures.limit_order`** | 同上 |
| **`skill.futures.amend_limit_order`** | 同上 **专节 · 逻辑改单**（**永续限价**） |
| **`skill.futures.take_profit_stop`**（**或** **`condition_order_create`**） | 同上 **合约止盈止损 · 分流** |
| **`skill.margin.cross_market_order`** | 同上 **专节 · 全仓杠杆（cross）** |
| **`skill.margin.cross_limit_order`** | 同上 |
| **`skill.margin.transfer_*`**（**示意** **`skill.margin.transfer_spot_to_cross`**） | 同上 **§第四步 · 划转** |
| **`skill.wealth.subscribe`** | [`../../../flows/wealth-via-agent.md`](../../../flows/wealth-via-agent.md) |
| **`skill.wealth.redeem`** | 同上 |

**FR-TS07**：**§4** **为** **`FR-TS07` 行级 SSOT**；**§8.2** **与** **§4** **须** **同序、同行数**。**OCO/bracket** **已** **单列** **`skill.spot.oco` / `skill.spot.bracket`**（**CC-P1-01** **文档登记**）；**PATH 冻结** **仍属** **矩阵 MR / [`contract-closure`](../../../contract-closure.md) §1.2**。**本产品阶段**：**不向用户交付** **这两类现货组合写**，**条文真源**：**[`product.md`](../../../product.md) §非目标**。**`scenarioId`** **路由分居** → [`routing-engine.md`](../agent-orchestration/routing-engine.md) **§2** **`trade.spot.oco` / `trade.spot.bracket`**。

<span id="ta-83"></span>

### 8.3 B 类 · 交易所只读工具（登记表）

**读能力上界**：**每条** **`toolId`** **须** **有** **`design`** **PATH** **锚**。**与 read 流程、编排键的逐项映射** → [`../agent-orchestration/routing-engine.md`](../agent-orchestration/routing-engine.md) **§1** · [`../../../flows/read-analyze-and-search-via-agent.md`](../../../flows/read-analyze-and-search-via-agent.md)。**PATH 未冻结** → **不对用户承诺闭环**。

| `toolId`（登记名） | 产品用途 / 备注 |
|--------------------|----------------|
| **`tool.market.ticker`** | 实时价量摘要 |
| **`tool.analytics.symbol_deep_dive`** | K 线/深度 + 解读（Disclaimer） |
| **`tool.market.orderbook`** / **`tool.market.recent_trades`** | 盘口 **与** **公共成交** |
| **`tool.orders.open_orders`** · **`tool.orders.history`**（**或** **`tool.orders.recent`；终名以矩阵 **`operationId`** 为准） | **在途/近期委托与成交**；**Portfolio 最小闭包** **同窗** [`portfolio-insight.md §1.1`](portfolio-insight.md) |
| **`tool.orders.*`**（**开集** · **上列以外扩展**） | **矩阵 MR** **须** **与** [`portfolio-insight.md §1.1`](portfolio-insight.md) **同步闭包** |
| **`tool.account.risk_snapshot`** | 保证金/爆仓距离等 **风险提示输入** |
| **`tool.futures.funding_summary`** | Funding 摘要 |
| **`tool.feed.rss_digest`** / **`tool.calendar.macro_window`** | RSS / **宏观日历** **（可选）** |
| **`tool.futures.liquidation_context`** | **合约 · 爆仓/强平语境只读** — **不写** **`fapi` 开仓** |
| **`tool.wealth.product_recommend`** **等** | **理财推荐只读链路** — **同窗** **`wealth-via-agent`** **`§8.2` B** **类** |

**矩阵未冻结**：**禁止**对用户承诺 **可查/可下单**。**Pull 触发器** **仅可用** **已登记 `toolId` + PATH**（**§8.3～8.5**）。

<span id="ta-84"></span>

### 8.4 C 类 · 外网与分析工具（下限表）

| `toolId`（示例） | 说明 |
|------------------|------|
| **`tool.web.social_sentiment`**、**`tool.web.news_search`**、**`tool.web.search`**、**`tool.i18n.translate`** | **合规/预算**：[`../../../../design/adr/003-external-tools-compliance-and-budget.md`](../../../../design/adr/003-external-tools-compliance-and-budget.md)（**ADR-003**）**与** **`agent-context`** **预算对签**（**CC-P1-02**）。**OpenAPI**：**C 类** 参数/速率/PII 元数据 **须** **可载** 于 [`tool-management-schemas.yaml`](../../../../openapi/components/tool-management-schemas.yaml) **（Registry/Schema 视图）**；**字段终裁 + 法务书面登记** **为** **`CC-P1-02`** **关闭条件**。 |

**（§8.4 续）** **登记、启用态与合规写闸**：**运行时** **仅** **运营登记表** **已登记** **且** **启用态为真**（**同窗** [`tool-management-schemas.yaml`](../../../../openapi/components/tool-management-schemas.yaml) **`ToolRegistryEntry.enabledOperational`**）**之 C 类** **可被调用**；**未配置或停用** **则不使用**。**将 C 类标为可对生产启用** **（文档/OpenAPI 生产就绪 + Registry 写闸）** **仍须** **schema MR** **合并** **且** **法务对签** **登记** / **`legalReviewTicketId`** **同窗** — **见** [`contract-closure.md`](../../../contract-closure.md) **CC-P1-02**、**ADR-003**。


<span id="ta-85"></span>

### 8.5 自动化 · Pull · 与非目标

- **条件监控、触发器、到期、风险阈值**：**同窗** **[`../../../flows/automation-alerts.md`](../../../flows/automation-alerts.md)** — **Pull 只读** **须 §8.3 PATH 依据**。  
- **非目标**：全量 **网格/DCA 机器人**，**对齐** [`../../../../../product/overview.md`](../../../../../product/overview.md) **与市场叙事** — **本条** **不扩展** **`skillId`** **承诺**。

---

<span id="footnotes-fr-ts07"></span>

### 脚注 · FR-TS07

**`FR-TS07`**：**对签** [`../../../contract-closure.md`](../../../contract-closure.md) **§1·§4·§6** — **矩阵解冻 MR** **须** **更新** **§4 表 + §8.2 行** **且** **递增** **`design/api.md` 脚注**。**OpenAPI `operationId` / PATH** **以** **矩阵** **为终裁**。

---

**文档版本**：0.4.12 · **维护**：产品 + Agent Runtime owner · **本版**：**flash_convert / futures.market_order mvp-ready 状态**。**承** 0.4.11。
