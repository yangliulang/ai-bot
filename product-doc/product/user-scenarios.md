# 用户场景（叙事）

本篇把 **常见情境** 揉成可数的故事线，方便产品、设计、客服 **按「你是谁、你要干什么」** 找入口；**不写 FR/SC**。验收、门禁、工具 ID 仍以 **`specs/requirements/`** 与各 **`flows/`** 为准。**矩阵·关双表**：[`contract-closure.md`](../specs/requirements/contract-closure.md)；**剩余关单 · §7.5～§7.6** [`closure-remaining.md`](../specs/requirements/closure-remaining.md)。
> **与 [`flows.md`](./flows.md) 的分工**：`flows` 按 **时间顺序**（§1～§7）讲技术上一趟请求怎么走；本篇按 **用户脑子里的问题** 归类，并 **链回** `flows` 对应节。  
> **需要一条线讲全（含运营配置 Prompt/Skill/Tools/场景）** → **[`end-to-end-guide.md`](./end-to-end-guide.md)**。

---

## 我想先搞清楚：这产品能干什么？

读 **[`overview.md`](./overview.md)**（范围、三前提、不做清单）+ **[`positioning.md`](./positioning.md)**（愿景与原则）。  
若你要对外承诺「能自动完成某交易所动作」，上限以 **[`design/api.md`](../specs/design/api.md) 矩阵** 为准，表上 **TBD / 未登记** 的能力 **默认不能对客说死**。

---

## 我刚点进 Bot，想用起来（开户 / 绑定）

**故事**：用户第一次用，还没子账户或 API 未就绪。  
**人类路径**：[`flows.md` §1](./flows.md#1-从有兴趣到能交易)。  
**契约与步骤**：[`onboarding/overview.md`](../specs/requirements/domains/agent/onboarding/overview.md)、[`telegram-binding.md`](../specs/requirements/domains/agent/onboarding/telegram-binding.md)；[`telegram/overview` §2.2～§2.6（Deeplink / 阻断）；§2.5 · 类型 A](../specs/requirements/domains/agent/telegram/overview.md)。被拦住时卡片多半是 **[类型 B](./telegram-and-cards.md#四条卡片类型从用户视角)**：**下一步须分层** — **未绑定实例** → **产品线 Deeplink** 打开 Agent 绑定页（**不须在该页登录交易所网页**）；**API/子账户未就绪** → **交易所 API 管理或子账户设置**（Key 须先在所内创建）；**VIP / 计费 / 权益** → **交易所站内**（**母账号 `vipTier`** 等）；**账单流水** → **站内 `/subaccount/billing`（`me/commerce` 配额与核销流水）**。不要用一句「去主站」掩盖上述差别 — **正式抽检表**见 [`journey-validation.md`](./journey-validation.md)。

---

## 我只想问问价格、翻译、舆情，不下单

**故事**：纯问答、公网行情、分析检索 — **不应**静默调用交易所写接口。  
**人类路径**：[`flows.md` §6](./flows.md#6-只要分析舆情或翻译不碰下单)。  
**流程条文**：[`read-analyze-and-search-via-agent.md`](../specs/requirements/flows/read-analyze-and-search-via-agent.md)。

---

## 我要买卖币 / 合约 / 理财（会动交易所）

**故事**：一旦涉及 **余额、持仓、下单、撤单、申购赎回** 等，必须先满足 **子账户 + 绑定 + 产品线开关**；**每一笔写**前要 **[类型 A](./telegram-and-cards.md)** 卡片确认（**ADR-001**）。  
**人类路径**：现货/合约/理财分别见 [`flows.md` §3](./flows.md#3-要写交易所之前--卡片与每笔确认) 内小节。  
**步骤级契约**：[`trade-via-agent.md`](../specs/requirements/flows/trade-via-agent.md)、[`wealth-via-agent.md`](../specs/requirements/flows/wealth-via-agent.md)；工具与矩阵见 [`trade-assistance.md`](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)；[`telegram/overview` §2.5 · 类型 A；总则 §2～§2.6](../specs/requirements/domains/agent/telegram/overview.md)。

---

## 扣了多少钱？余额不够了怎么办？

**故事**：可计费路径在 **终局** **轨 B 权益核销**（**`ENTITLEMENT_DEBIT`**）；**配额与消耗摘要** 在 **交易所站内主站 / H5 · `me/commerce`** 看。**配额用尽** → **升级/买包**；**交易侧 USDT 可用** 不足 → **拦新交易写** 并提示充值。  
**人类路径**：[`flows.md` §4](./flows.md#4-用完了怎么扣钱怎么看账户)。  
**契约**：[`consume-and-bill.md`](../specs/requirements/flows/consume-and-bill.md)、[`billing-management/overview.md`](../specs/requirements/domains/admin/billing-management/overview.md)。

---

## 超时了、不确定成没成交 — 会不会乱报？

**故事**：**504 / 状态不明** 时 **不能**当用户面断言「一定成交」；须按 **对账与 UNKNOWN** 语义处理，话术中区分 **计费可能已发生** vs **订单是否终局**。  
**人类路径**：[`flows.md` §5](./flows.md#5-异常与信任504对账别乱报成交)。  
**展开**：[`architecture.md`](../specs/design/architecture.md)、[`Runtime/unknown-state.md`](../specs/requirements/Runtime/unknown-state.md)、[`Runtime/reconciliation.md`](../specs/requirements/Runtime/reconciliation.md)。

---

## 我想设条件单、到期或风险提醒（人不在对话框里）

**故事**：允许在满足 **矩阵与确认闸门** 的前提下做 **条件/计划委托** 与 **只读依据的 Pull 提醒**；**网格 / 全量 DCA 机器人首版排除**。  
**人类路径**：[`flows.md` §7](./flows.md#7-条件单到期提醒与-pull-阈值后台任务)；范围边界见 [`overview.md` §自动化](./overview.md#自动化与提醒后台任务)。  
**契约**：[`automation-alerts.md`](../specs/requirements/flows/automation-alerts.md)、`trade-assistance` §8.3～8.5；[`telegram/overview` §2.5 · 类型 A（所内创建写）；总则 §2～§2.6](../specs/requirements/domains/agent/telegram/overview.md)。

---

## 运营 / 评审：一表索引

| 你还关心 | 优先读 |
|----------|--------|
| 端到端 **步骤目录** | [`flows/README.md`](../specs/requirements/flows/README.md) |
| **交易门禁、冻结、原因码** | [`exchange-agent/overview.md`](../specs/requirements/domains/agent/exchange-agent/overview.md) |
| **会议导航** | [`requirements-review.md`](./requirements-review.md) |
| **本目录有哪些文件** | [`README.md` 文档地图](./README.md#本目录文档地图) |

---

*方向级 SSOT：[`specs/requirements/product.md`](../specs/requirements/product.md)*
