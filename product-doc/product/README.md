# ChainUp AI Agent · 人类阅读版需求说明

欢迎。本目录写的是 **面向人的产品叙事**：读起来像说明文档，不按机器验收表组织。

**小团队（≈1 需求 + 1 开发）**：日常管控与 MR 约定见 **[`specs/requirements/LITE-MODE.md`](../specs/requirements/LITE-MODE.md)**；发版关门半页纸见 **[`release-notes.md`](./release-notes.md)**。**关单本仓 vs 所内分工**见 **[`closure-remaining.md`](../specs/requirements/closure-remaining.md)**（**[§7 剩余开放项](../specs/requirements/closure-remaining.md#cc-remaining-open-items)** · **[§7.5 闭环路径](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 执行清单](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)**）。

**本 Git 仓库边界**：**`product/`** 与 **`specs/`** **仅** **需求与设计**；**Execution Gateway、Coobit Adapter 等可执行实现** **不在** **本仓维护**（**[`contract-closure` CC-P1-07 DoD B](../specs/requirements/contract-closure.md#cc-p1-07)** **在所内工程仓库验收**）。**统一交易语义与设计** → **[`ADR-004`](../specs/design/adr/004-intent-centric-execution-and-canonical-trading-model.md)**、**[`canonical-trading-model.md`](../specs/design/canonical-trading-model.md)**；**系统工程叙事（Runtime / Gateway / 意图中心）** → **[`architecture.md`](../specs/design/architecture.md)** **「与通用 Agent 栈之对照」**。

**从 `specs` / Speckit 过来**：契约与聚合索引见 **[`specs/requirements/spec.md`](../specs/requirements/spec.md)**；若要 **开会评审或讲清用户故事**，用 **[`requirements-review.md`](./requirements-review.md)** + 下文 **文档地图**。

与此相对，**可契约、可归因、可对测试绑定的条目**集中在仓库里的 **`specs/`**，供 Speckit、工具链与实现逐条对齐。二者关系可以理解为：

| 你给谁的 | 目录 | 说明 |
|----------|------|------|
| **产品经理、设计、管理层、新业务同学** | **`product/`**（这里） | 故事线、取舍、用户体验原则；链接到 specs 可查细节编号 |
| **研发、QA、Lint 工具、自动生成** | **`specs/requirements/`**、**`specs/design/`** | FR/SC、`design/api` 矩阵、门禁顺序等 SSOT |

**与 `specs/` 的关系**：本目录 **只承担人类可读的叙事与导航**；凡涉及 **FR/SC、接口 PATH、矩阵 TBD、验收 ID、幂等键** 等 **可契约条文**，以对应 **`specs/requirements/`**、**`specs/design/`** 正文为准。叙事与 specs 冲突时：**以 specs 为准**，并回写 `product/` 或标注日期。

## 本目录文档地图

| 文档 | 人类读者从中获得什么 | 查编号 / 矩阵 / 流程时的入口 | 维护角色（职能占位，可填花名/轮值） |
|------|----------------------|------------------------------|--------------------------------------|
| [release-notes.md](./release-notes.md) | **发版说明（半页纸）** · 小团队关门 | [`LITE-MODE` §3](../specs/requirements/LITE-MODE.md) | 产品 + 开发 |
| [closure-remaining.md](../specs/requirements/closure-remaining.md) | **剩余关单与配置**：CC-P0/P1 **本仓 vs 所内** · MR 速链 · 配置索引 · **[§7 开放项总表](../specs/requirements/closure-remaining.md#cc-remaining-open-items)** · **[§7.5 闭环路径](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 执行清单](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)** | [`contract-closure`](../specs/requirements/contract-closure.md) | 产品 + 收口 |
| [requirements-review.md](./requirements-review.md) | **评审会**议题打包、`product` ↔ `specs` 跳转 | [`spec.md`](../specs/requirements/spec.md)、[`Runtime/boundaries.md`](../specs/requirements/Runtime/boundaries.md)；**交易语义** **另见** **[§7.5 ADR-004 速查](./requirements-review.md#cc-adr004-review-checklist)** | 产品 + 规格 / 各域 **评审轮值** |
| [positioning.md](./positioning.md) | 愿景、原则、**不夸大契约** | [`product.md`](../specs/requirements/product.md) | 产品负责人 |
| [overview.md](./overview.md) | **做什么 / 不做什么**、计费与冻结提要 | `product.md`、[exchange-agent](../specs/requirements/domains/agent/exchange-agent/overview.md)、[`integrations/exchange/overview.md`](../specs/requirements/integrations/exchange/overview.md) **（Coobit · `openapi-ai` vs 矩阵契约）**、[`domains/web/overview.md`](../specs/requirements/domains/web/overview.md)（**绑定 onboarding / 站内账单 · FR-WEB**）、[`design/api.md`](../specs/design/api.md)、[`architecture.md`](../specs/design/architecture.md) **「与通用 Agent 栈之对照」** | 产品 + **交易域** owner |
| [requirements-spec-human.md](./requirements-spec-human.md) | **产品需求说明书（人话）**：须/不得/边界 **表格式导读**，链向 `specs` **不**替代 FR/SC | [`product.md`](../specs/requirements/product.md)、[`contract-closure`](../specs/requirements/contract-closure.md)、[`closure-remaining`](../specs/requirements/closure-remaining.md) | 产品负责人 |
| [prompt-governance-checklist.md](./prompt-governance-checklist.md) | **Prompt 治理清单（非 SSOT）**：16 包、六段正文、Skill 对照；替代已删 `Prompt/Prompt List.md` | [`prompts/README`](../specs/requirements/prompts/README.md)、[`prompt-management`](../specs/requirements/domains/admin/prompt-management/overview.md) | 产品 + Prompt owner |
| [`end-to-end-guide.md`](./end-to-end-guide.md) | **端到端一篇读懂** + **§2 Runtime-first**（Pre/Post Gate、Canonical、时序图、状态机、**§2.9 澄清+记忆**）；开通→S1～S10→计费→阶段 0 配置 | 同上 + [`canonical-trading-model`](../specs/design/canonical-trading-model.md)、[`Runtime/domain-model`](../specs/requirements/Runtime/domain-model.md)、[`clarify-session`](../specs/requirements/domains/agent/agent-orchestration/clarify-session.md) | 产品 + **flows** 条文 owner |
| [flows.md](./flows.md) | **主路径 1～7**（开通→会话→确认→计费→异常等）；**篇首技术鸟瞰** **`e2e`→`architecture` §对照** | [`flows/`](../specs/requirements/flows/README.md)、[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md)、[`architecture` · 与通用 Agent 栈之对照](../specs/design/architecture.md)、[`domains/web/`](../specs/requirements/domains/web/README.md) | 产品 + **flows** 条文 owner |
| [user-scenarios.md](./user-scenarios.md) | **按常见情境**拆故事，链回 `flows` | 同上 + `overview` | 产品 |
| [journey-validation.md](./journey-validation.md) | **端到端旅程正式验证**（Given/When/Then、**JV-01～JV-13** · **JV-13 澄清僵尸链**） | [`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md)（**架构语言**）、[`architecture` · 与通用 Agent 栈之对照](../specs/design/architecture.md)、[`evals/scenarios.md`](../specs/requirements/evals/scenarios.md) | 产品 + QA |
| [journey-validation-checklist.md](./journey-validation-checklist.md) | **JV-01～13 抽检勾选表**（staging/生产 **Pass/Fail**） | 同上 · **JV-13 逐步表** | 产品 + QA |
| [internal-sprint-w1-issues.md](./internal-sprint-w1-issues.md) | **W1 所内工单复制块**（含 **MR-MEM-01**） | [`closure-internal-sprint` §2](../specs/requirements/closure-internal-sprint.md) | 产品 + TL |
| [telegram-and-cards.md](./telegram-and-cards.md) | **卡片类型 A～D**、Telegram 硬约束（人话） | [`telegram/overview.md`](../specs/requirements/domains/agent/telegram/overview.md) **§2.5 · 类型 A、§2～§2.6** | 产品 + **渠道/交互** |
| [roadmap.md](./roadmap.md) | **篇首 TL;DR** · **规格体系快照（L1～L7 · 分批主轴）** · **横切主题** · **优先级与编号对照** · **P0、阶段 A～D** 与 **可选自检**；端到端业务 + 项目闭环 | `product.md`、`flow/e2e-closed-loop.md`（**架构语言**）、[`architecture` · 与通用 Agent 栈之对照](../specs/design/architecture.md)、[contract-closure](../specs/requirements/contract-closure.md)、[`closure-completion-matrix`](../specs/requirements/closure-completion-matrix.md)（自检 / W1；与 Roadmap **互链**）、[`roadmap/README`](./roadmap/README.md) | 产品 + **规格** owner |
| [roadmap/README.md](./roadmap/README.md) | **按季/主题** 拆分文档的 **放置约定** | 主文 [`roadmap.md`](./roadmap.md) | 同上 |
| [milestones.md](./milestones.md) | **里程碑叙事**（不做第二套验收表） | `roadmap.md`、`product.md` | 产品 |

**说明**：**维护角色** **≠** RACI；与某篇 `specs` 篇末脚注（如「产品 + Agent Runtime owner」）冲突时 **以域/Runtime 正文脚注为准**，并可在上表 **同步改一行**。

## 建议阅读顺序

0. **小团队日常**：[LITE-MODE](../specs/requirements/LITE-MODE.md) · [发版说明](./release-notes.md)（需对外交代时更新）。  
1. **团队需求评审（会议入口）**：[需求评审 · 单一入口](./requirements-review.md) — **按议题打包** `product/` 与 `specs/`，减少跨文件跳跃。  
2. [定位与边界](./positioning.md) — **长期方向与会坚持的原则**。
3. [产品概览与范围](./overview.md) — 我们是做什么的、做什么不做什么。
4. [产品需求说明书（人话导读）](./requirements-spec-human.md) — **须/不得/边界** 表格式入口；读完后按需跳入 `domains/` / `flows`。  
5. [**端到端全流程指南**](./end-to-end-guide.md) — **一篇串完** 配置面 + 用户路径 + Prompt/Skill/Tools/`scenarioId`（**推荐** 新人/评审首读）。
5b. [关键用户路径](./flows.md) — 从开通到会话、计费、回看流水（**更短提要**；**篇首** **逻辑鸟瞰图** **`e2e`→[`architecture` §对照](../specs/design/architecture.md)**）。
6. [用户场景提要](./user-scenarios.md) — 故事线与 flows 入口。
6b. [端到端旅程正式验证](./journey-validation.md) — Given/When/Then 抽检表（联调 / 发版前）。
7. [Telegram 体验与卡片](./telegram-and-cards.md) — 确认闸门、卡片类型与展示差异。
8. [路线图](./roadmap.md) — **规格体系快照（L1～L7）**、**横切**、**优先级与编号对照**、**P0～D**；**本仓自检 / W1** → [`closure-completion-matrix`](../specs/requirements/closure-completion-matrix.md)（与 Roadmap **互链**）；按季拆分见 [`roadmap/README.md`](./roadmap/README.md)。与 [里程碑叙事](./milestones.md) 对读（**不**替代 FR/SC）。  
8b. **需求日报（飞书）**：[模版与 Owner 口径](../specs/design/requirements-daily-report-feishu.md) · [本地发送脚本](../scripts/product-daily-brief/README.md)（`npm run brief:dry-run` / `brief:send`）。  
9. 若需查 **错误码、验收 ID、`executionId`** 等：从各篇文末链接进入 **`specs`** 对应域文档。  
10. **系统如何运行（逻辑架构 + 环境/发布）**：[`specs/design/architecture.md`](../specs/design/architecture.md)（**对内对齐**：**「与通用 Agent 栈之对照」** — Runtime / Gateway / 意图中心）、[`specs/design/deployment.md`](../specs/design/deployment.md)；**端到端逻辑鸟瞰图** [`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md) **（文首「架构语言」同窗 **`architecture` §对照**）**；单条请求步骤级叙事 [`specs/requirements/Runtime/execution.md` §1](../specs/requirements/Runtime/execution.md#1-执行管线概念序)、主流程 [`specs/requirements/flows/`](../specs/requirements/flows/README.md)。  
10b. **对上 Coobit 私网 HTTP（契约 vs 宿主）**：[`integrations/exchange/overview.md`](../specs/requirements/integrations/exchange/overview.md) **`openapi-ai`/Skill 同窗节**，与 [`specs/requirements/product.md`](../specs/requirements/product.md) **方向**、`design/api.md` **矩阵 +** [`agent-coobit-api-allowlist`](../specs/requirements/integrations/exchange/agent-coobit-api-allowlist.md) **同窗**。  
11. **（运营后台）Telegram Bot / Webhook 与 `TELEGRAM_*`**：契约见 [`admin-bot-config.md`](../specs/requirements/domains/agent/telegram/admin-bot-config.md)，`configKey` 见 [`trading-agent-config/keys.md` §4](../specs/requirements/domains/admin/trading-agent-config/keys.md)；发布前勾选 **[附录 A · 「发布 / 对齐检查清单」](../specs/requirements/domains/admin/management-console-v1-prd.md#mc-prd-appendix-a-release-checklist)**（勿与正文「§13 · 验收主题」混淆），缺口跟踪 [`contract-closure · CC-P1-06`](../specs/requirements/contract-closure.md)。

本文档集的 **主题级事实源仍以** [`specs/requirements/product.md`](../specs/requirements/product.md) **为原则**（方向裁决）；若在叙事与 specs 发生冲突，以 specs 正文为准并及时 **回改正文或在此目录注明日期**。**关键架构取舍（如 Telegram 先于交易所写）** 见 **[`specs/design/adr/`](../specs/design/adr/README.md)**。

**更新**：改 `specs` 时**同步**触及的 `product/` 篇章（至少 **文档地图** 与相关链接）；大调目录结构时**优先**更新本篇 **文档地图** 与 [`requirements-review.md`](./requirements-review.md) §2。
