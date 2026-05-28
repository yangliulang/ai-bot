# 产品概览与范围

## 我们做什么

**ChainUp AI Agent（Coobit 专版）** 让已是 Coobit 用户的客户，在 **Telegram** 里用自然语言完成 **行情与账户查询、委托与自动化相关能力**（以交易所 **已开放给「Agent 专用子账户 + 子账户 API」** 的能力为上限）。

下列 **硬前提**，产品对外沟通时要讲清楚：

1. **单所、单渠道（本版）**：只在 **Coobit** 落地；对客会话 **本版仅 Telegram**，没有 App 交付线。
2. **钱与交易走子账户**：用户同意开通后，**交易清算**挂在 **Agent 专用子账户**。**Agent 消耗计费**：**对客** **订阅 · Capability · 加购包**（用尽即停）；**S5 仅轨 B 权益核销** — 见 [`billing-management/commerce-model.md`](../specs/requirements/domains/admin/billing-management/commerce-model.md)。
3. **能力受 API 表格约束**：产品可以「想」覆盖币币、杠杆、合约、理财四线，但 **实际能写进合约里的接口** 以 `[specs/design/api.md](../specs/design/api.md)` 里 **已冻结** 的矩阵为准；表上 **TBD 或没有的一律首版不对用户承诺能自动完成**。
4. **出站 HTTP Prefer 官方宿主**：对上 Coobit 私网的 **出站实现默认**走 **ChainUp `openapi-ai`/Skill（须 pin 版本）**；**能调用哪些 PATH** 仍 **只认** **`design/api` 矩阵 + [`agent-coobit-api-allowlist`](../specs/requirements/integrations/exchange/agent-coobit-api-allowlist.md)** — 综述见 [`integrations/exchange/overview.md`](../specs/requirements/integrations/exchange/overview.md)。
5. **意图与多所语义（演进）**：对客叙事以 **能力/意图**（`skillId`/`scenarioId` 等）为主，**不把** **某一家交易所的 REST 字段名** **当作** **唯一产品真源**；**执行链** **须** **可收敛到** **Canonical 语义层与 Gateway→Adapter**（**设计** **[`ADR-004`](../specs/design/adr/004-intent-centric-execution-and-canonical-trading-model.md)**、**[`canonical-trading-model.md`](../specs/design/canonical-trading-model.md)**、**[`trade-assistance` §2.6](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)**、**[`CC-P1-07`](../specs/requirements/contract-closure.md#cc-p1-07)**）。**可执行代码** **在** **所内工程仓库** **交付**，**本规格仓** **不** **承载实现**。
6. **系统工程叙事（对内对齐）**：本产品 **不是**「聊天 + Tool Calling → 交易所 HTTP」一类 Demo 栈；**Agent 运行时 / Execution Gateway / Canonical / 确认门·对账·观测** 等下限 — **[`architecture.md`](../specs/design/architecture.md)** **「与通用 Agent 栈之对照」**。

**鸟瞰图（逻辑顺序 · 与人话七章不同粒度）**：[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md) **文首「架构语言」** → **`architecture` §对照**；七章叙事见 **[`flows.md`](./flows.md)**。

## 规格状态（契约 SSOT：`product.md`）

**已定稿（需求阶段 · 2026-05-15）**：[`specs/requirements/product.md`](../specs/requirements/product.md) **篇首状态** — **本版范围已可进开发排期**。**不表示** P0/P1 已关：生产侧关单仍以 [`contract-closure.md` §5.2](../specs/requirements/contract-closure.md#cc-exec-remaining) 为准；聚合索引 [`spec.md`](../specs/requirements/spec.md) **仍为 Draft**，升格见 [`contract-closure` §5.1](../specs/requirements/contract-closure.md#cc-stage4-spec-gate)。**建议实现波次**（备忘）：[`requirements-review` §8](./requirements-review.md#cc-impl-wave-hint)。

**当前能力与不承诺快照（小团队发版关门）**：[`release-notes.md`](./release-notes.md)（与 [`LITE-MODE` §3](../specs/requirements/LITE-MODE.md) 同窗；**不**替代 `product.md` / 域正文）。**「文档完整性」含义、分仓与文件数口径** 见 **同文件篇首** §「与「文档完整性」评估如何对齐」。**P0/P1 关单分工（本仓 vs 所内）**：[`closure-remaining.md`](../specs/requirements/closure-remaining.md)（**§0 速链**、**[§7 剩余开放项总表](../specs/requirements/closure-remaining.md#cc-remaining-open-items)** · **[§7.5 闭环路径](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 执行清单](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)**）。

## 面向不同读者（怎么读这个目录）


| 你是谁          | 建议从这里开始                                                 | 接着读                                                                                                                                                                |
| ------------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **产品 / 业务**  | `[positioning.md](./positioning.md)` → 本篇 → [`requirements-spec-human.md`](./requirements-spec-human.md)（须/不得导读） | [`flows.md`](./flows.md)、[`user-scenarios.md`](./user-scenarios.md)                                                                                                |
| **设计 / 文案**  | 本篇 + `[telegram-and-cards.md](./telegram-and-cards.md)` | `[telegram/overview.md](../specs/requirements/domains/agent/telegram/overview.md)` **§2.5（类型 A）· §2～§2.6**                                                                         |
| **研发 / 架构**  | `[README.md](./README.md)` 建议顺序                         | `[spec.md](../specs/requirements/spec.md)`、`[Runtime/overview.md](../specs/requirements/Runtime/overview.md)`、`[architecture.md](../specs/design/architecture.md)`、`[flow/e2e-closed-loop.md](../flow/e2e-closed-loop.md)` **（鸟瞰 · 文首架构语言）** |
| **评审 / PMO** | `[requirements-review.md](./requirements-review.md)`    | [`README.md` 文档地图](./README.md#本目录文档地图)、[`contract-closure.md`](../specs/requirements/contract-closure.md)、[`closure-remaining` §7/§7.5/§7.6](../specs/requirements/closure-remaining.md#closure-remaining-quicklinks)                                                         |


## 术语速览（人类版，非码表）

下列短语在 `**specs/`** 里往往有更细定义；此处 **仅帮助新人读懂 `product/` 叙事**。


| 说法                      | 人话含义                                                                                                                              |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Agent 专用子账户**         | 用户授权后由所内下发的、供 Agent 调私有 API 的隔离账户；**计费与交易扣款**与主账户区分。                                                                              |
| **类型 A / B / C / D 卡片** | Telegram 上四种交互：**写前确认**、**被拦引导**、**只读信息**、**通知** — 详见 `[telegram-and-cards.md](./telegram-and-cards.md)`。**写路径澄清键盘（`cl:*`）≠ 类型 A** — 同篇 **§澄清**。                         |
| **矩阵 / TBD**            | `[design/api.md](../specs/design/api.md)` 里 **哪些 PATH 已冻结**；**TBD** = 尚未可对客承诺闭环。                                                  |
| **504 / UNKNOWN**       | 上游超时或 **结果不可判定**；平台须保留 **未知态**，**不得**直接说成「已失败成交」— 见 `[Runtime/unknown-state.md](../specs/requirements/Runtime/unknown-state.md)`。 |
| **Agent 计费**            | **`executionId`** 对齐 **终局结算**；**S5 仅轨 B** **`ENTITLEMENT_DEBIT`**；**对客**：**订阅 · Capability · 加购包**（用尽即停，续用须升级或买包）— **`commerce-model`**、`consume-and-bill`、站内 **`me/commerce`**。                                                  |
| **执行 / executionId**    | 一次可对齐计费和审计的请求实例；真源字段以 `**design`/observability** 为准。                                                                              |


## 自动化与提醒（后台任务）

除 **会话内即时应答**之外，在满足 **契约与门禁**的前提下，本产品 **允许**用户使用 **预设条件类能力**：例如交易所 **矩阵已冻结 PATH** 的 **条件单/计划委托写**（仍须 `**design/api`** 放行），或由 **后台 Pull** 在满足 **只读接口依据** 时触发的 **到期、资金费率/保证金·标记价类阈值提醒**。**写路径**与用户对话里下单 **同属「须类型 A」与 ADR‑001**：**不得在未经用户点此确认的情形下**对 Coobit 落写。**网格 / 全量 DCA 机器人**仍为 **首版排除**。  
契约与 `**toolId`/矩阵门禁**：`**[specs/requirements/flows/automation-alerts.md](../specs/requirements/flows/automation-alerts.md)`**、`[specs/requirements/domains/agent/exchange-agent/trade-assistance.md](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)` **§8.3～8.5**。人类可读提要：`**[flows.md` §7](./flows.md)**。

## 用户侧消耗与 Billing

查 **Capability 配额/消耗、核销状态、导出本人 CSV** 等，在 **交易所内部** **主站 / H5** 完成 — **`/subaccount/billing`（账单与消耗 · `me/commerce`）** — **与 Agent 绑定配置页（onboarding、`me/agent/*`）外置无冲突**。Telegram 里要提供 **可点的 Deeplink** **跳进该页**，而不是只丢一长串不可点的文字。

## 会员与冻结

系统有多层 **开关与冻结**（全局、运营暂停、子账户/API 未就绪、VIP 不够、余额不够等）。用户看到的应是 **可读原因 + 能做什么（例如去主站开通、去充值）**，而不是含糊的「系统错误」。细节与原因码在 `[specs/requirements/domains/agent/exchange-agent/overview.md](../specs/requirements/domains/agent/exchange-agent/overview.md)` 与 `[management-console-v1-prd.md](../specs/requirements/domains/admin/management-console-v1-prd.md)` **附录 A** 里机器可读地定义。

## 本版明确不做什么

- 不做 **多租户商户 SaaS** 那一套对客经营后台。
- **网格** ：首版 **不做**（`[exchange-agent/overview](../specs/requirements/domains/agent/exchange-agent/overview.md)`、`[trade-assistance` §8.5](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)）。**≠**上文 **§「自动化与提醒」**中的条件单/到期 `**toolId` Pull**。
- 不在 `product/` 里写 **技术栈、库表、排期** — 那些归 design 与项目管理。

## 下一步读什么

- **长期方向**：[产品与边界](./positioning.md)、[里程碑](./milestones.md)、[路线图](./roadmap.md)。
- **按情境找故事**：[用户场景提要](./user-scenarios.md)；再走一遍业务顺序：[关键用户路径](./flows.md)（含 **§7 Pull/告警**）。
- 关心 **确认弹窗/卡片**：[Telegram 体验与卡片](./telegram-and-cards.md)。
- **本目录全貌（表格）**：[README · 文档地图](./README.md#本目录文档地图)。

---

*方向级 SSOT：`[specs/requirements/product.md](../specs/requirements/product.md)`*