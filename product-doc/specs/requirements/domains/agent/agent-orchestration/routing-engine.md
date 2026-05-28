# 编排路由 · `scenarioId` 寄存器

**职责**：**Runtime 路由键 `scenarioId` 的产品 SSOT** — 表格式登记 **与** [`../exchange-agent/intents.md`](../exchange-agent/intents.md) **语义层**、[`../../flows/`](../../../flows/README.md) **逐步骤剧本** **对签**。**不写** 意图簇话术全文、**不写** OpenAPI。

**互引**：[`overview.md`](overview.md) **FR-AO02**；[`execution-lifecycle.md`](execution-lifecycle.md)（归因）；[`task-scheduler.md`](task-scheduler.md)（监控键的调度面）。**结构化 Goal 评审范例**（**非** **契约 SSOT**）→ [`../goals/README.md`](../goals/README.md)。

**与 Prompt Management**：**业务能力路由第一维为 `scenarioId`（本文表）**；**`promptPackKind` / `PromptPackType`** 仅表 **拼装与治理大类**。Orchestration 命中 **`scenarioId`** 后解析 **`promptPackId`/`promptPackVersion`（含模板 `promptPackRef` 绑定）** — 详 **`admin/prompt-management`** **[`overview.md`](../../admin/prompt-management/overview.md)**、[**`functions.md`](../../admin/prompt-management/functions.md)** **§1.2～§1.3**、[**`config.md` §1.1a](../../admin/prompt-management/config.md)。

**占位键与对外承诺**：表中 **族名占位** / **占位** 行 **不得** **单独** 作为「已支持」承诺 — **须在 MR 冻结键名并会签 `flows` / `trade-assistance`** 后再纳入 [`../../contract-closure.md`](../../../contract-closure.md) **闭环**；口径见 [`overview.md`](overview.md) **§6**。

**写路径 · 编排下限对签**：[`runtime-freeze.md`](runtime-freeze.md) **§3** — **本篇 §2** **登记键** **对应** **§3.1～§3.9**（**现货/全仓/合约/改单/OCO/bracket**）；**§3** **`wealth.subscribe` / `wealth.redeem`** → **§3.10**；**§4** **`monitoring.*`** → **§3.11**。**读键**（**§1**、**§3** **`wealth.holdings_read` / `wealth.recommend`**）**无** **§3 专表**，**与写混编** **仍受** **`runtime-freeze` §2.3** **串行默认** **与** **门禁**。

**对上 Coobit HTTP（实现对齐）**：**§2 写键** 与 **§1 读键** 出站为交易所私网时，默认 **`openapi-ai`**（Skill 宿主），制品须 pin；契约面同窗 [`integrations/exchange/overview.md`](../../../integrations/exchange/overview.md)、[`design/api`](../../../design/api.md)、[`agent-coobit-api-allowlist`](../../../integrations/exchange/agent-coobit-api-allowlist.md)。**不**在此处扩 PATH。

**统一交易语义（写键经 Gateway 文档链）**：[`canonical-trading-model.md`](../../../../design/canonical-trading-model.md)、[`ADR-004`](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../exchange-agent/trade-assistance.md)；[`CC-P1-07`](../../../contract-closure.md#cc-p1-07)；[`requirements-review` §7.5](../../../../../product/requirements-review.md#cc-adr004-review-checklist)；[`Runtime/execution` §1 步 7](../../../Runtime/execution.md)。**Gateway 代码** **在所内工程仓** **验收**（**CC-P1-07 DoD B**）。

**同窗 · 架构语言**：[`architecture` §「与通用 Agent 栈之对照」](../../../../design/architecture.md)；[`flow/e2e-closed-loop`](../../../../../flow/e2e-closed-loop.md) **文首「架构语言」**。

---

## 1. 读侧与分析 / B·C 类（原 overview §5.1）

| **`scenarioId`（键）** | **典型用户目标** | **流程 / 能力锚点** |
|------------------------|------------------|---------------------|
| **`market.read_quote`** | 实时价量摘要 | [`../exchange-agent/market-intelligence.md`](../exchange-agent/market-intelligence.md)、[`../../flows/read-analyze-and-search-via-agent.md`](../../../flows/read-analyze-and-search-via-agent.md) |
| **`market.read_microstructure`** | 盘口、公共成交 | 同上 + [`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **§8.3** |
| **`market.read_deep_analysis`** | K 线 / 指标 + 解读 | 同上 |
| **`futures.read_funding`** | 资金费率摘要 | 同上；**写** → `trade-via-agent` |
| **`research.rss_or_macro`** | 简报 / 外链研究 | **来源与 `asOf` 须可见** |
| **`research.sentiment_and_news`** | 社媒情绪 **+/** 新闻 **等** **C 类** 编排收口 | 与 [`../../flows/read-analyze-and-search-via-agent.md`](../../../flows/read-analyze-and-search-via-agent.md) **§ 映射表**、**`trade-assistance` §8.4** **同窗**；**合规** **ADR-003** |
| **`orders.read_activity`** | 在途委托、近期成交 **等** | [`../exchange-agent/portfolio-insight.md`](../exchange-agent/portfolio-insight.md)、**`FR-T02`** |
| **`portfolio.read_pnl_exposure`** | 盈亏 / 敞口叙事（**非** ticker 顶替成交） | 同上 · **SC-PI01/02** |

### §1.1 编排键别名（实现归一 · 不向主表增发第二 SSOT）

**canonical** **仍仅为**上表第一列。**实现**若现 **`read.market.ticker`** 等 **倒置域段**别名 — **归因与 contract 对签 MUST 映射**：**Ticker 轻读**→ **`market.read_quote`**（[`market-runtime-payload` §1](../exchange-agent/market-runtime-payload.md)）。**不得在** Telegram **用户正文**复述 REST PATH、`scenarioId` 字面、`read.market.*` — **`market-runtime-payload` §2**、[`../telegram/overview.md`](../telegram/overview.md)。

**Pull / 只读自动化**：须 **有矩阵或公开 PATH 依据**（[`../../contract-closure.md`](../../../contract-closure.md) **§1**）；槽位意图映射见 [`../exchange-agent/overview-legacy-migration.md`](../exchange-agent/overview-legacy-migration.md) **§2**。

---

## 2. 现货与衍生品写路径（原 overview §5.2）

| **`scenarioId`（键）** | **说明** | **流程 / 登记锚点** |
|------------------------|----------|---------------------|
| **`trade.spot.flash_convert`** | 闪兑（含用户侧 **现货市价** 买卖 **族**） | [`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md)、[`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **§8.2** |
| **`trade.spot.limit_order`** | 现货限价写入 **主路径** | 同上 · **FR-AO01** |
| **`trade.spot.amend_limit_order`** | **现货限价 · 逻辑改单**（**单次类型 A · `cancel`→`order`**） | [`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单**；[`../../../design/adr/001-telegram-confirm-before-coobit-write.md`](../../../../design/adr/001-telegram-confirm-before-coobit-write.md) **§5** |
| **`trade.spot.oco`** | 现货 **OCO** 写入（**独立** `scenarioId`，**勿**与 **`trade.spot.limit_order`** **混路由**） | 同上 · **`skill.spot.oco`**。**矩阵/PATH**：[`../../../design/api.md`](../../../../design/api.md) · **CC-P1-01**。**本产品阶段**：**不向用户放开写**，**不须实现**，见 **[`product.md`](../../../product.md) §非目标** |
| **`trade.spot.bracket`** | 现货 **bracket**（入场 + 保护腿） | 同上 · **`skill.spot.bracket`**；**矩阵/PATH** **同窗 OCO**。**本产品阶段**：**不须实现**，见 **`product.md` §非目标** |
| **`trade.futures.market_order`** / **`trade.futures.limit_order`** | 合约 **单笔** 市价/限价写（矩阵已载能力） | 同上 |
| **`trade.futures.amend_limit_order`** | **永续限价 · 逻辑改单**（**单次类型 A · `cancel`→`order`**） | [`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 逻辑改单** |
| **`trade.futures.take_profit_stop`** / **`futures.condition.order_create`** | 合约 **止盈止损 / 条件委托**（**独立 `scenarioId`**；**`POST /fapi/v1/conditionOrder`** **链**） | [`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 合约止盈止损 · 分流**；[`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **§8.2**；[`../../../design/api.md`](../../../../design/api.md) **矩阵 · 自动化 · `conditionOrder`** |
| **`margin.cross.market_order`** / **`margin.cross.limit_order`** · **`margin.cross.transfer_in`**（**示意**） | **全仓杠杆写 / 划转** | [`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 全仓**；**矩阵** [`../../../design/api.md`](../../../../design/api.md) |

**技能子名**（如闪兑 buy/sell）与 **OpenAPI** → [`../../../design/api.md`](../../../../design/api.md)；**细分子名** **须** **同窗** 更新 **`trade-assistance` §8.2**。

---

## 3. 理财（原 overview §5.3）

| **`scenarioId`** | **模式** | **互引** |
|------------------|----------|----------|
| **`wealth.holdings_read`** | 只读持仓/到期/收益 | [`../../flows/wealth-via-agent.md`](../../../flows/wealth-via-agent.md)、[`../../observability/overview.md`](../../../observability/overview.md) |
| **`wealth.recommend`** | 推荐/排序（只读 **或** 导向写） | 同上 |
| **`wealth.subscribe`** / **`wealth.redeem`** | 申购 / 赎回 | 同上 + **类型 A** · **FR-AO04** |

**`FEATURE_AGENT_WEALTH=OFF`** **负例** → [`../../admin/management-console-v1-prd.md`](../../admin/management-console-v1-prd.md) **TC-26**、[`../exchange-agent/boundaries.md`](../exchange-agent/boundaries.md)。

---

## 4. 监控与自动化（原 overview §5.4）

| **`scenarioId`（键）** | **说明** | **互引** |
|------------------------|----------|----------|
| **`monitoring.price_condition`** | 到价/指标类 **条件**（概念键；实现可映射 `taskId` 类型） | [`../../flows/automation-alerts.md`](../../../flows/automation-alerts.md)、[`task-scheduler.md`](task-scheduler.md) |
| **`monitoring.scheduled_pull`** | 定时 / Pull 复盘 | 同上 |
| **`monitoring.event_trigger`** | 事件类触发（**子类型** **与** **`task-scheduler` / `automation-alerts` MR** **扩展枚举**） | [`../../flows/automation-alerts.md`](../../../flows/automation-alerts.md)、[`task-scheduler.md`](task-scheduler.md) |

**`taskId` 状态与 SC-MT\*** → [`state-machine.md`](state-machine.md)。

**契约开放面**（**A≠B、P0/P1、§3 实现验收**）：[`closure-remaining` §7](../../../closure-remaining.md#cc-remaining-open-items) · **[§7.1 缺口粘贴](../../../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。

**Walkthrough（九步）**：**本表** **每增删** **`scenarioId`** **须** **同窗** 更新 [`flow/e2e-closed-loop.md`](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough-scenarios) **§** **索引行**。

---

**文档版本**：1.2.13 · **维护**：产品 + Agent Runtime owner · **本版**：**§2** **OCO/bracket **与 **`product.md` §非目标** **同窗**。**承** **1.2.12**。
