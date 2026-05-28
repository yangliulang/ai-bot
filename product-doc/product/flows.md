# 关键用户路径（人类阅读）

下面用「故事」串起主路径；实现上的顺序、错误码、与计费字段仍以 specs 为准。

**需要一篇讲全（含 Runtime-first 架构图、Canonical、Pre Gate）** → **[`end-to-end-guide.md`](./end-to-end-guide.md)**（**§2** 评审用；推荐新人首读）。本篇为 **更短的 §1～§7 提要**。

**一页提要**：§1 开户绑定 → §2 消息进入执行 → §3 **写前卡片（类型 A）** → §4 计费与账单（`/subaccount/billing` · `me/commerce`）→ §5 **504/对账** → §6 纯分析不写 → §7 自动化 / Pull 提醒。

**业务场景总图（预览）**：[`flow/e2e-closed-loop.html`](../flow/e2e-closed-loop.html) **Tab「业务场景总图」**（同窗 [`e2e-closed-loop.md`](../flow/e2e-closed-loop.md) **§业务场景** · 对齐本篇 **§0～§7**）。**技术鸟瞰（逻辑顺序 · 非步骤 SSOT）**：同页 **Tab「端到端鸟瞰」** → [`architecture` §「与通用 Agent 栈之对照」](../specs/design/architecture.md)；步骤级仍以 **[`specs/requirements/flows/`](../specs/requirements/flows/README.md)** 为准。**契约收口 / 未关闭项 MR 路径**（**不**替代 `contract-closure` DoD）：[`contract-closure.md`](../specs/requirements/contract-closure.md)、[`closure-remaining` §7](../specs/requirements/closure-remaining.md#cc-remaining-open-items) · [§7.5](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path) · [§7.6](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)。

> **原 [`user-scenarios.md`](./user-scenarios.md)** 已并入 **§0**；按 **时间顺序** 细读请直接看 **§1～§7**。

---

## 0. 按情境找入口（索引）

| 用户关心的问题 | 人类路径（本篇） | 契约 / 抽检 |
|----------------|------------------|-------------|
| 这产品能干什么？ | [`overview.md`](./overview.md) **§定位与愿景**、**§我们做什么** | [`product.md`](../specs/requirements/product.md)、[`design/api.md`](../specs/design/api.md) 矩阵 |
| 刚点进 Bot，想用起来 | **§1** | [`onboarding/overview`](../specs/requirements/domains/agent/onboarding/overview.md)、[`journey-validation` JV-01](./journey-validation.md) |
| 只问价/分析，不下单 | **§6** | [`read-analyze-and-search-via-agent`](../specs/requirements/flows/read-analyze-and-search-via-agent.md) |
| 买卖/合约/理财（会写交易所） | **§3** | [`trade-via-agent`](../specs/requirements/flows/trade-via-agent.md)、[`wealth-via-agent`](../specs/requirements/flows/wealth-via-agent.md)、[`telegram-and-cards`](./telegram-and-cards.md) |
| 扣了多少钱？余额不够？ | **§4** · [`end-to-end-guide` §9](./end-to-end-guide.md) | [`consume-and-bill`](../specs/requirements/flows/consume-and-bill.md)、**JV-05** [`journey-validation`](./journey-validation.md) |
| 配额用尽要升级/买包？ | **§4** · [`end-to-end-guide` §9.2](./end-to-end-guide.md#92-订阅与-crypto-结账demo--非-s5-主链) | **`?start=ab_up` / `ab_pk`** · **JV-15**；**FR-B18** 量产前不承诺到账即生效 |
| 运营配 Prompt / 看核销？ | [`end-to-end-guide` §10](./end-to-end-guide.md#10-阶段-g--运营台-demo-ia配置与协查) | **JV-13** · **JV-14** |
| 超时/不确定成没成交 | **§5** | [`unknown-state`](../specs/requirements/Runtime/unknown-state.md)、**JV-06** |
| 条件单/到期/风险提醒 | **§7** · [`overview` §自动化](./overview.md#自动化与提醒后台任务) | [`automation-alerts`](../specs/requirements/flows/automation-alerts.md) |
| 运营配置 Prompt/Skill/场景 | [`end-to-end-guide`](./end-to-end-guide.md) **§0～§2** | [`prompt-governance-checklist`](./prompt-governance-checklist.md) |
| 评审会 / 关单分工 | [`requirements-review`](./requirements-review.md) | [`closure-remaining`](../specs/requirements/closure-remaining.md) |

**被拦住时（类型 B）**：**下一步须分层** — 未绑定 → **产品线 Deeplink**；API/子账户 → **交易所 API 管理**；VIP/权益 → **交易所站内**；账单 → **`/subaccount/billing`（`me/commerce`）** — 见 [`telegram-and-cards`](./telegram-and-cards.md)、[`commerce-deeplink`](../specs/requirements/domains/web/commerce-deeplink.md)。

---

## 1. 从「有兴趣」到「能交易」

用户通过产品入口（例如 Bot 或宣传链）进入 **Telegram**，想使用交易 Agent。**首次在 Telegram 发消息**时，若 **该 Telegram 账号尚未绑定可用 Agent 实例**，应先收到 **产品线 Deeplink**，引导至 **Agent 绑定页**（**不须访问交易所主站**）：录入 **子账户 UID**（与交易所 **`subUid`** 同窗）、**API Key 与 Secret**，**点击保存**即触发 **`POST .../bindings/trading-api`** — **服务端经交易所 API 校验**：须满足 **`agentSubAccountUid` 与 Key 归属 `subUid` 一致**（否则 **`AGENT_BIND_SUBACCOUNT_UID_MISMATCH`**）、**子账户 Key（非主账户）**、**子账户已启用**、**API 交易及币币·杠杆·合约权限全开**（**[`FR-WEB06`](../specs/requirements/domains/web/agent-onboarding.md)** · **[§1.2](../specs/requirements/domains/agent/onboarding/initialization-flow.md)** · **[`TradingApiBindRejectCode`](../specs/openapi/components/onboarding-schemas.yaml)**）；**仅全部通过后**才 **创建实例并完成绑定**。探测 PATH 见 **[`design/api.md`](../specs/design/api.md)** **「绑定保存 · 交易所探测矩阵」**。

在 **真正碰到交易所私有接口** 之前，需要先满足 **一连串门禁**（可以记成：**先能拿到 Deeplink 并完成绑定页保存与 §1.2 下限校验**，再给 **子账户和 API「点火」**，再看 **母账号 VIP、子账户 USDT（交易侧）、Agent Capability/订阅额度**）。任一环节不满足，就应 **可读原因** 并给 **下一步**（常为 **产品线 Deeplink** 打开绑定页，或 **交易所站内** 处理划转/VIP/配额 — **`billing`/门禁条文为准**）。

**Agent 专用子账户**须在所内达到 **就绪**口径；**API 凭据**由用户在 **Agent 产品线绑定页**提交，**不要求**多步 onboarding 向导。细则见 `[specs/requirements/domains/agent/onboarding/overview.md](../specs/requirements/domains/agent/onboarding/overview.md)` 与 `[specs/requirements/domains/web/agent-onboarding.md](../specs/requirements/domains/web/agent-onboarding.md)`。

## 2. 用户发消息后：会先被拦住，或进入执行

用户在 Telegram 里发一条消息，就触发一次 **Agent 执行请求**。有的消息只是问答或公共行情；有的会牵动 **私有查询或下单**。

- **只读、且不需要子账户 Key 的路径**（例如纯 FAQ、仅公开行情）在部分 **子账户未就绪** 场景下仍可能放行 — 这是有意设计，避免「账户没开完就完全不能说话」。
- **一旦要查余额、持仓、委托，或要下单、撤单等写操作**，就必须 **子账户就绪 + 有效绑定 API + 对应产品线开关打开**，否则应 **拒答并给出可读原因与单一明确下一步**（例如：**产品线 Deeplink** → Agent 绑定页；**交易所 API 管理** → 子账户 Key/权限；**交易所站内** → 母账号 VIP、划转、Billing — 具体 **门禁与原因码** 以 [`exchange-agent/overview.md`](../specs/requirements/domains/agent/exchange-agent/overview.md)、[`billing-management/overview.md`](../specs/requirements/domains/admin/billing-management/overview.md) 为准），**不得**笼统等同于「必须登录主站才能完成 Key 绑定」，而不是编造成交。

**缺参与多轮**（流程图见 [`e2e-closed-loop` · 业务场景 Tab](../flow/e2e-closed-loop.html)）：

- **缺参 / 槽位不全**（**FR-T07** · **S6**）：须 **澄清追问**（**FR-AO02**），**禁止猜价猜量、禁止静默下单**；用户补充后在 **类型 A 之前** 继续同一写链。**跨轮澄清** **须** **沿用同一 **`executionId`** **并** **注入已确认槽位** — [`clarify-session`](../specs/requirements/domains/agent/agent-orchestration/clarify-session.md) · [`clarify-user-visible`](../specs/requirements/prompts/shared/clarify-user-visible.md)。
- **多轮对话**：同一会话可连续多条 Telegram 消息；写路径在 **`executionId` 起票（S5）后** 可处于 **待确认 / 澄清** 等状态，直至终局或用户改参/取消 — [`trade-via-agent`](../specs/requirements/flows/trade-via-agent.md) · [`end-to-end-guide` §2.7](./end-to-end-guide.md)。**澄清态** **每条 inbound** **仍须重跑意图** — **禁止** **盲复读上轮模板**（**§2.3**）。
- **记忆**：每轮先 **召回 STM（会话内 L0/L1）** 再拼装 Prompt；**LTM/语义记忆默认关**；应答后 **写回 STM** 供下轮连贯。**写澄清 idle/TTL 先达** → **默认 stale**（**退出活跃 L1**）→ **重意图 ± Resume 门控** — **非** **阻塞式「继续/新话题」卡** — [`memory-runtime` §14.6](../specs/requirements/Runtime/memory-runtime.md) · [`keys` §2.1](../specs/requirements/domains/admin/trading-agent-config/keys.md)。**「重新开始」** 清会话短期记忆，**≠** **「清空记忆」**（LTM）— 流程图 [`e2e-closed-loop` 业务场景 Tab](../flow/e2e-closed-loop.html)。

## 3. 要写交易所之前 — 卡片与「每笔确认」

**每一笔**落到交易所侧的 **写**（下单、撤单、改单、创建/取消条件单、借还等在 specs 里列尽的），**都必须**在用户 **明确点了确认** 之后才能发私有 API。**不允许**助手在对话框里用文字说「我已帮你买好」来代替真实确认。**卡片长什么样、按币币/合约/限价/市价有什么不同**，见 [Telegram 体验与卡片](./telegram-and-cards.md)；**§2.5 · 类型 A（§2.5.x 字段下限）与总则 §2～§2.6（Bot API）** 见 [**telegram/overview** §2.5 · 类型 A；§2～§2.6](../specs/requirements/domains/agent/telegram/overview.md)。

从 **问清买卖方向/标的/价/量** → **识别止盈止损组合** → … 的 **七段路径**，已写在 `[specs/requirements/flows/trade-via-agent.md](../specs/requirements/flows/trade-via-agent.md)`。**币币侧**：用户口中的 **「市价 / 即时成交」在产品上 统一走闪兑（`scenarioId`** 如 `**trade.spot.flash_convert**` 族），**不是**与闪兑并列的第二条「独立现货市价专线」；**限价挂单**走 **现货限价专节**；**卡片**上仍要让人看出是「市价」语义（字段下限见渠道 specs）。其中 **合约** **市价/限价开平仓** 另有 **「专节 · 合约交易」八步**（**意图分流、默认市价、参数追问、自检、后端预检、类型 A、确认/改参重跑、执行**），**止盈止损** **与强平解析** **走** **独立 scenario / 技能**。**现货限价专节** 亦在同文档。

### 理财（活期/定期、质押等）

先说清 **用户想干什么**：**直指某产品申购**就走该产品技能；要 **查持仓/赎回** 走查询或赎回链路；只说 **「推荐、收益最高、帮我配」** 等 **会先**按需看资产 **（结果不一条条晒给你）**，再给出 **APR 排序与稳健/进取分组**或 **总额守恒的组合方案**，**最多追问一轮**补齐关键缺的参数；敲定后每张产品 **单独一张卡片**（合规字段见 specs），你在卡片上选定 **再进入**该产品自己的 **申购**（活期/定期、金额、二次确认。**若交易所规定必须主站**：给你 **外链 +「须去网页完成」**的明确说明）。

完整八步契约见 `[specs/requirements/flows/wealth-via-agent.md](../specs/requirements/flows/wealth-via-agent.md)`。

## 4. 用完了怎么扣钱、怎么看账户

单次会话若走了 **可计费** 路径：须先满足 **`FR-T02` 门禁**（含 **VIP、子账户 USDT（交易侧）**，及 **订阅/Capability/包额度** — [`commerce-model.md`](../specs/requirements/domains/admin/billing-management/commerce-model.md)、[`consume-and-bill.md`](../specs/requirements/flows/consume-and-bill.md) **S2**）。系统在 **执行终局** 做 **权益核销**（**S5 · `ENTITLEMENT_DEBIT`** · **`POST …/entitlements/debit`** · [`billing-management/flow.md`](../specs/requirements/domains/admin/billing-management/flow.md)）。**用尽套餐内额度且无加购包** 时 **应拦截**，**不包含** 「超量继续扣子账户 Token/USDT」默认体验。

用户对 **消耗的理解**应以 **Capability / 档位**为主；**明细**可查 **核销状态** 与 **可选 Token Metering**。**理财申购/赎回** 若走交易所矩阵写，与 **其它写** 同属 **可计费执行 + 对账** **语义**；仅 **须去主站**（`WEALTH_ACTION_REQUIRES_WEB`）**而无矩阵写** 时，**不归因于该笔写**，细节见 **`billing` §7.3.1**。

**Capability 配额用尽** 时：应 **升级/买包**（见 [`commerce-model.md`](../specs/requirements/domains/admin/billing-management/commerce-model.md)）。**交易侧子账户 USDT 不足** 时：会 **拦新交易写**，并在 Telegram 里说清楚 **去给子账户币币 USDT 充值** — **勿**与 **Agent 消耗配额** 混为一谈。

用户在 **交易所主站 / H5**（**账单仍在交易所内部**）打开 **`/subaccount/billing`（账单与消耗 · Capability 核销流水）**；从 Telegram **`?start=ab` / `ab_ld` / `ab_up` / `ab_pk`** 等 **应能一键 Deeplink 跳进站内页**（[`commerce-deeplink`](../specs/requirements/domains/web/commerce-deeplink.md)）。本条 **不含**「账单迁出交易所」— **仅** **Agent 产品线 onboarding（Key 绑定 · `me/agent/*`）** **不须用户在交易所主站完成**，触点见 §1。

**升级 / 加购包（与 S5 核销分域）**：配额用尽时类型 B 引导 **`ab_up` / `ab_pk`** → **`/subscription/*`** 与 **Crypto 结账演示**（[`end-to-end-guide` §9.2](./end-to-end-guide.md#92-订阅与-crypto-结账demo--非-s5-主链) · [`web-billing-reconciliation` §0.1](../specs/requirements/domains/web/admin-console-web-billing-reconciliation.md)）。**PSP 到账前** **不得** 对用户说 **「套餐已生效」**（**FR-B18** · 量产 MR）。

## 5. 异常与信任：504、对账、别乱报成交

若交易所侧 **超时或响应不可判终态**，**不能**跟用户拍胸脯说「一定成交了」。要先 **按设计里的对账语义**处理，话术上要 **区分开「你这轮 Agent 核销/配额终局是否已定」与「订单在交易所是否终态」** — 这一条容易客诉，产品对外说明要稳重。详见 `[specs/design/architecture.md](../specs/design/architecture.md)` 与消费流程 `[specs/requirements/flows/consume-and-bill.md](../specs/requirements/flows/consume-and-bill.md)`。

## 6. 只要分析、舆情或翻译，不碰下单

同一条 Telegram 对话里，用户也可能 **只要实时价量、想让人解释一段走势、搜新闻/社媒情绪、或中英互译**。**这条路径默认没有**「交易二次确认卡」，**也** **不应**在后台 **静默走** **交易所写接口**；若用户 **话锋转到**「帮我买/卖/挂单」，再 **切换** 到 **§3** 的 **现货/合约写路径**（`trade-via-agent`）；**转去理财申购/赎回** 见 **§3** 小节 **理财** 与 `**wealth-via-agent`**。  
产品级步骤与 `**scenarioId` 建议** 见 `[specs/requirements/flows/read-analyze-and-search-via-agent.md](../specs/requirements/flows/read-analyze-and-search-via-agent.md)`；**工具 ID（B/C）与写技能（A）目录** 见 `[specs/requirements/domains/agent/exchange-agent/trade-assistance.md](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)` **§8**。

## 7. 条件单、到期提醒与 Pull 阈值（后台任务）

除了在对话里即时回答，产品线还允许用户 **预设条件**：例如 **合约计划/止盈止损委托**（矩阵 **非 TBD 且 PATH 冻结** 时）、理财 **到期、资金费率突变、保证金率/标记价阈值**（**仅以所内可用的只读 PATH 为依据**，见 specs 中对 `**tool.orders.*`、`tool.futures.funding_summary`、`tool.account.risk_snapshot`** **等登记名**。**首版不包含**网格/DCA **全策略机器人**。任务 **创建→触发→推 Telegram** 的契约见 `[specs/requirements/flows/automation-alerts.md](../specs/requirements/flows/automation-alerts.md)`，与 `**trade-assistance` §8.3～8.5** **矩阵门禁**对签：`design/api.md` **未冻结** 的路径 **不得在对外话术里承诺闭环**。