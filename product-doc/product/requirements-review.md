# 需求评审 · 团队用单一入口

**问题**：`specs/requirements/` 按域、主题、机器可对齐方式 **刻意拆分**（Speckit、工具链、归因），对 **评审会** 不友好——人需要在多文件间跳跃才能拼出「这一题要讲什么、决策落在哪」。

**本文用途**：**评审前准备与会中导航** 的 **人类入口**；**不**新增 FR/SC，**不**替代 [`specs/requirements/product.md`](../specs/requirements/product.md) 与域正文。**结论与验收条文**仍须写回对应 **`specs/`** 文件及（如涉及对外承诺）[`contract-closure.md`](../specs/requirements/contract-closure.md)。**Open 项排期 / MR 粘贴路径** **同窗** [`closure-remaining.md`](../specs/requirements/closure-remaining.md) **§0 / §7.5 / §7.6**（**不**替代 `contract-closure` DoD）。

---

## 1. 评审前速览（约同一屏）

| 顺序 | 读什么 | 目的 |
|------|--------|------|
| 1 | [`overview.md`](./overview.md) 或 [`positioning.md`](./positioning.md) | 本轮讨论是否仍在 **产品范围/非目标** 内 |
| 1b | [`requirements-spec-human.md`](./requirements-spec-human.md)（可选） | **一页表**：须/不得/边界 + **条文入口**；**不**新增 FR |
| 2 | [`specs/requirements/product.md`](../specs/requirements/product.md) 相关节 | **契约向**方向与范围（和 `product/` 冲突时以 specs 为准并回写叙事） |
| 3 | [`specs/requirements/spec.md`](../specs/requirements/spec.md) **主题索引**一段 | 从 **聚合索引** 跳到 **域 / Runtime / flows**（含 [`Runtime/boundaries.md`](../specs/requirements/Runtime/boundaries.md)「全表」） |
| 4 | 若涉及 **发布 / 矩阵 / OpenAPI** | [`contract-closure.md`](../specs/requirements/contract-closure.md)、[`specs/design/api.md`](../specs/design/api.md)；**余量关单** [`closure-remaining` §7.5](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path) · [§7.6](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist) |
| 4b | 若涉及 **交易语义 / 工具↔交易所映射 / 多所前置** | [`ADR-004`](../specs/design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`canonical-trading-model.md`](../specs/design/canonical-trading-model.md)、[`architecture.md`](../specs/design/architecture.md) **「与通用 Agent 栈之对照」**、[`trade-assistance` §2.6](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)、[`CC-P1-07`](../specs/requirements/contract-closure.md#cc-p1-07)；**实现验收（DoD B）** **在** **工程仓库** |
| 4c | 若要把 **端到端逻辑鸟瞰** 与 **七章叙事 / 步骤 specs** **同窗对齐** | [`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md) **（文首「架构语言」）**、[`flows.md`](./flows.md)、[`specs/requirements/flows/`](../specs/requirements/flows/README.md)；**对照** **`architecture` §「与通用 Agent 栈之对照」** [`architecture.md`](../specs/design/architecture.md) |
| 5 | **关单 / P0-P1 分工与 MR 速链** | [`closure-remaining.md`](../specs/requirements/closure-remaining.md) **§0**（`contract-closure` 锚点表）、**[§7 剩余开放项总表](../specs/requirements/closure-remaining.md#cc-remaining-open-items)** · **[§7.5 闭环路径](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 执行清单](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)**；与 **第 4 步** **`contract-closure` 主表 / §8** **对读** |
| 5b | **JV 抽检勾选 / W1 工单** | [`journey-validation-checklist.md`](./journey-validation-checklist.md) · [`internal-sprint-w1-issues.md`](./internal-sprint-w1-issues.md) |

深读顺序仍见 [`README.md`](./README.md) **建议阅读顺序**；**本目录有哪些文件、和 specs 怎么对照** → [`README.md` · 文档地图](./README.md#本目录文档地图)。本表只解决「**先打开哪几份**」。

---

## 2. 按议题打包（评审时按需展开）

以下 **每一行 = 一类议题**，从左到右：**人类叙事 → 步骤或横切 → 契约/矩阵**。会议材料可只投影 **第一列**，细节现场点开链接。**义务句式总览**（可选投影）：[`requirements-spec-human.md`](./requirements-spec-human.md)。**范围**与 [`product.md`](../specs/requirements/product.md) **非目标**、[`overview.md`](./overview.md) **本版明确不做什么** 对读；**按人设找故事**见 [`user-scenarios.md`](./user-scenarios.md)。

| 议题 | 人类叙事（产品） | 步骤 / 行为链 | SSOT / 设计 |
|------|------------------|---------------|-------------|
| 主路径、计费感知 | [`flows.md`](./flows.md)、[`user-scenarios.md`](./user-scenarios.md) | [`specs/requirements/flows/`](../specs/requirements/flows/README.md)、[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md) **（鸟瞰 · 文首架构语言）**、[`consume-and-bill`](../specs/requirements/flows/consume-and-bill.md) | 域内 FR/SC、`design/api`；**同窗** [`architecture` §对照](../specs/design/architecture.md) |
| Telegram 体验与确认 | [`telegram-and-cards.md`](./telegram-and-cards.md) | [`domains/agent/telegram/overview.md`](../specs/requirements/domains/agent/telegram/overview.md) **§2.5 · 类型 A、§2～§2.6** | ADR-001、[`admin-bot-config`](../specs/requirements/domains/agent/telegram/admin-bot-config.md) |
| 交易、工具、门禁 | `overview` / 场景篇 | [`exchange-agent/overview.md`](../specs/requirements/domains/agent/exchange-agent/overview.md)、[`trade-assistance.md`](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md) | [`boundaries.md`](../specs/requirements/domains/agent/exchange-agent/boundaries.md)、`design/api` |
| **统一交易语义 · Gateway→Adapter**（ADR-004） | [`overview` 硬前提 §5～§6](./overview.md)、[`requirements-spec-human` §3](./requirements-spec-human.md) | [`trade-assistance` §2.6](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md) | [`ADR-004`](../specs/design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`canonical-trading-model`](../specs/design/canonical-trading-model.md)、[`architecture.md`](../specs/design/architecture.md)（**「与通用 Agent 栈之对照」**）、[`api.md`](../specs/design/api.md) |
| 编排、重试、预算 | （按需） | [`agent-orchestration/overview.md`](../specs/requirements/domains/agent/agent-orchestration/overview.md)、[`retry-policy.md`](../specs/requirements/domains/agent/agent-orchestration/retry-policy.md) | `routing-engine`、`execution-lifecycle` |
| **运行时横切**（执行管线、504、对账、持久化） | [`README.md`](./README.md) § 系统如何运行 | **[`Runtime/overview.md`](../specs/requirements/Runtime/overview.md) §1 目录表** → 再点开单篇 | [`Runtime/boundaries.md`](../specs/requirements/Runtime/boundaries.md)、[`execution.md`](../specs/requirements/Runtime/execution.md) §1 |
| 观测、审计、风险 | （按需） | [`observability/overview.md`](../specs/requirements/observability/overview.md)、[`risk/README.md`](../specs/requirements/risk/README.md) | `SC-OBS*`、`risk/acceptance.md` |
| 路线图与节奏 | [`roadmap.md`](./roadmap.md)、[`roadmap/README.md`](./roadmap/README.md) | — | 与 `product.md` / `contract-closure` **不得**对外矛盾 |

**说明**：[`Runtime/README.md`](../specs/requirements/Runtime/README.md) 中各篇 **「同窗」为短列表**；跨域找谁权威 → **只看** [`Runtime/boundaries.md`](../specs/requirements/Runtime/boundaries.md) **全表** 即可，无需背全库路径。

---

## 3. 评审会 minimal 议程（可复制）

1. **议题与范围**：本轮是否动 FR/契约 / 仅叙事？  
2. **用户可见行为**：一句结论 + 对应 `flows/` 或域内用户故事是否已覆盖。  
3. **边界与异常**：504/UNKNOWN、重试、对账是否在 **Runtime / exchange-agent** 有闭合表述（或明确缺口登记）。  
4. **收口**：决策写入哪一文件（域正文 / `Runtime` 分卷 / `design/api` / ADR / `contract-closure` §8）；**谁** MR 跟踪。  
5. **规格仓 vs 工程仓**：若涉及 **Gateway/Adapter 可执行代码**、**对拍单测**，**派工到所内工程/Runtime 仓库**；**本 Git 仓** **MR** **只** **承载** **`product/`** **与** **`specs/`** 条文。**CC-P1-07 DoD B** **证据** **不以** **本文仓目录** **为准** — **见** **[ADR-004 后果句](../specs/design/adr/004-intent-centric-execution-and-canonical-trading-model.md)**、**[`§7.5` 检查表](#cc-adr004-review-checklist)**。

---

## 4. 与「机器开发」分工（避免两套真相）

- **分卷、`spec.md`、`FEATURE_DIR`**：继续服务工具链与逐条实现——**不要**为评审会再造第二套 SSOT。  
- **评审枢纽**：**只增加可执行的阅读路径与议程**，减少「找文件」成本。  
- 若团队希望 **周期性「评审包」PDF/Markdown 导出**，可从 **§2** 议题表固定字段生成目录，无需合并单一大文件。

---

**维护**：新增或搬迁 `specs/requirements/` 主题时，**同步**检查 **§2 表** 是否仍指向正确入口；大结构调整时更新本篇一行即可。**干系人逐条确认结论**见 **§5**；**MR 拆单**见 **§6**；**`product.md` 定稿自检**见 **§7**；**ADR-004 评审速查**见 **§7.5**；**实现波次备忘**见 **§8**（**不**替代正式回写 `specs/` 的 MR）。

---

## 5. 干系人逐条确认纪要（2026-05-09）

以下为会话中 **口述决策** 的逐条归档，供后续 **MR 回写** [`product.md`](../specs/requirements/product.md)、[`contract-closure.md`](../specs/requirements/contract-closure.md)、[`billing-management/overview.md`](../specs/requirements/domains/admin/billing-management/overview.md)、[`tool-management`](../specs/requirements/domains/admin/tool-management/) / OpenAPI 等时对照。**#1** 已与 [`product.md`](../specs/requirements/product.md) **方向/范围** **核对一致**（**Coobit 单所**、对客 **仅 Telegram**、**不含 App**；口述偶见 Coolbit 与仓库 **Coobit** 为同一所指）。

| # | 议题 | 确认结论 |
|---|------|----------|
| 1 | 单所与渠道 | **与 `product.md` 一致**：**仅 Coobit 单所**；对客 **仅 Telegram**；**不含 App**（[`mobile-app.md`](../specs/requirements/domains/agent/telegram/mobile-app.md) 暂缓口径不变）。 |
| 2 | 「承诺」口径 | **对客**：能力是否可用由 **规则与条件**（如白名单、VIP 门槛等）决定，**非营销式空口承诺**。**对内/契约**：规格中的「可承诺闭环」仍指 **工程与文档可对齐、不虚构能力** 的收口语义；二者分层，避免混读。 |
| 3 | P0-01 Hosted/tag | **是** — 由所内 MR 对 **Hosted / `release-*` 与仓库 spec 同窗** 终裁。 |
| 4 | P0-02 矩阵 | **是** — **已确定的需求** 对应矩阵能力 **须冻结**（PATH/登记表与实现一致），不搞「口头已支持、表仍飘」。 |
| 5 | P0-03 账务三线 baseUrl | **简化**：**不区分** 生产/测试标签下的多套叙事；**BASEURL 走配置文件**，能少则少。 |
| 6 | 收入账户（原 D-12 向） | **收入账户 UID** 由 **配置文件** 提供（**不**在纪要中展开与现行 §10.6.1 财务范式 A/B 的逐字对齐 —— 须 MR 与财务/合规对签后改域文）。 |
| 7 | P0-05 D-5/D-7 | **是** — **按检查单与规范** 关单后再动 PRD 勾选，禁止超前。 |
| 8 | P1-01 OCO/bracket | **是** — 须完成矩阵/PATH 与协议向收口（与 §4/§7 纪律一致）。 |
| 9 | P1-02 外网工具 | **产品规则**：**已配置且工具状态为激活** 则 **可用**；**未配置或不可用** 则 **不用**。**注意**：与现行 [`contract-closure` CC-P1-02](../specs/requirements/contract-closure.md)、OpenAPI **`legalReviewTicketId`** 生产闸、**ADR-003** 表述 **存在张力** —— 若采纳本条为最终产品律，**须** **合规/法务 MR** 显式修订 schema 与收口表，**不可**仅以本文纪要为准。 |
| 10 | P1-03 工具 SSOT | **当前阶段**：**以文档与需求管理为主**，**不涉及** 代码级关单 / DB 镜像验收（与 `contract-closure` **B 阶段** 生产闭链 **可分期** —— 回写时需写清「V1 需求冻结 vs 生产可对签」边界）。 |
| 11 | P1-04 Prompt | 同 **文档/需求阶段优先**，代码级全流程 **后序**。 |
| 12 | P1-06 Telegram | 同 **文档/需求阶段优先**，生产 Hosted/实测 **后序**。 |
| 13 | `spec.md` 升格 | **是** — 仍须 **`contract-closure` §5.1** gate 后再动 Status / 对外冻结叙事。 |
| 14 | `product.md` 冻结 | 当 **全量功能点需求梳理完成、可进入开发阶段** 时，可将 `product.md` **状态置为冻结/定稿**（具体措辞与版本脚注由 MR 改）。 |

**待办（工程/文档）**：**MR-1～4** **已登记** [`contract-closure` §8](../specs/requirements/contract-closure.md)；**实现 MR** **仍须** **逐 CC 关单**；**弱化 `legalReviewTicketId`** **须** **合规工单 + §8**。

---

## 6. 待办 MR 拆单（基于 §5）

| 顺序 | MR 主题 | 建议改动面 | 依赖 / 备注 |
|:----:|---------|------------|-------------|
| **MR-1** | **账务配置简化（#5/#6）** | [`billing-management/overview.md`](../specs/requirements/domains/admin/billing-management/overview.md) **§12.1**（baseUrl 仅配置、不维护规格内多环境表）、**§10.6.1**（收入专户 **UID 配置** 默认路径）；必要时 [`keys.md` §5](../specs/requirements/domains/admin/trading-agent-config/keys.md) **互引一句** | **可先合**；与实现「各环境各配置文件」一致 |
| **MR-2** | **对客准入 vs 对内收口语** | [`product.md`](../specs/requirements/product.md) **契约收口段** + 可选 [`contract-closure` §1.1](../specs/requirements/contract-closure.md) **一句分层** | 可与 MR-1 **并行** |
| **MR-3** | **外网工具：启用态 + Enable 写闸（#9）** | [`contract-closure` CC-P1-02 / MR-A](../specs/requirements/contract-closure.md)、[`ADR-003`](../specs/design/adr/003-external-tools-compliance-and-budget.md)、[`tool-management-schemas.yaml`](../specs/openapi/components/tool-management-schemas.yaml)、[`trade-assistance` §8.4](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md) | **本轮草案已合**；**豁免 `legalReviewTicketId` 仍须** **§8** **风险登记** |
| **MR-4** | **P1 文档阶段 vs 生产 B 阶段** | [`contract-closure` §3.0 `#cc-p1-doc-vs-b`](../specs/requirements/contract-closure.md#cc-p1-doc-vs-b)、[`product.md`](../specs/requirements/product.md) **P1 分期一句** | **本轮草案已合**；澄清 **#10～#12** |
| **MR-5** | **`product.md` 定稿** | [`product.md`](../specs/requirements/product.md) **篇首状态** **已定稿 2026-05-15**；[`contract-closure` §8](../specs/requirements/contract-closure.md) **0.1.72**；**自检** **[§7](#cc-mr5-product-freeze-checklist)** | **已合文档**；**实现** **仍按** **§5.2** |

**当前执行**：**MR-1～5** **文档链已闭合**（[`contract-closure` §8](../specs/requirements/contract-closure.md) **0.1.72**）。**下一步**：**实现 MR** **按** **[§5.2](../specs/requirements/contract-closure.md#cc-exec-remaining)** **关 CC** → **再** **走** **[§5.1](../specs/requirements/contract-closure.md#cc-stage4-spec-gate)** **`spec.md` 升格**。**合规豁免** **须** **工单 + §8**。

---

<a id="cc-mr5-product-freeze-checklist"></a>

## 7. `product.md` 定稿自检（MR-5）

**用途**：**产品 owner** **在** **首度将** **`product.md`「状态」** **定为** **已定稿** **或** **后续重大范围变更回改状态前** **过一遍**（**不**替代评审会；**结论** **仍须** **MR**）。

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | **范围表** | [`product.md` · 范围/非目标](../specs/requirements/product.md) **与** **V1 派工** **无** **未决「做不做」** |
| 2 | **域入口** | **`domains/`** **`flows/`** **主干** **已** **有** **可读 SSOT** **或** **显式缺口登记** |
| 3 | **契约索引** | **团队知悉** **[`contract-closure` §3.0](../specs/requirements/contract-closure.md#cc-p1-doc-vs-b)** — **定稿** **≠** **B 阶段关单** **≠** **§5.1 升格** |
| 4 | **登记** | **合并同时** **[`contract-closure` §8](../specs/requirements/contract-closure.md)** **顶行** **+** **`product.md` 更新日期** |

**执行记录（文档）**：**2026-05-15** **`product.md` 已定稿** **+** **§8** **0.1.72** — **实现关单** **仍以** **§5.2** **为准**。

---

<a id="cc-adr004-review-checklist"></a>

## 7.5 ADR-004 / CC-P1-07 评审速查（文档侧）

**何时用**：评审 **交易助手 / 工具映射 / 观测字段 `canonicalOp`/`venue` / 多所叙事** 等议题时，**会议出口** **除** **域 FR** **外** **须** **对齐** **本条**。

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | **能力名 vs REST** | 对客与登记表 **仍以** **`skillId`/`toolId`/`scenarioId`** **表意图**；**禁止** **把** **某一所专属 REST 串** **升格为** **产品唯一叙事真源** |
| 2 | **设计互引** | 结论是否需回写 **[`canonical-trading-model.md`](../specs/design/canonical-trading-model.md)**、**[`trade-assistance` §2.6](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)**、**[`architecture.md`](../specs/design/architecture.md)**（含 **「与通用 Agent 栈之对照」**：Runtime / Gateway / 意图中心；如涉及数据流/C4） |
| 3 | **矩阵与白名单** | **[`api.md`](../specs/design/api.md)** **+** **[`agent-coobit-api-allowlist`](../specs/requirements/integrations/exchange/agent-coobit-api-allowlist.md)** **仍为** **Coobit HTTP 契约真源**；**Canonical** **为语义真源** — **双轨** **至** **映射表填齐** |
| 4 | **DoD 分工** | **文档 A** **=** **本仓** `specs/` + `product/`；**DoD B**（Gateway/Adapter **对拍**、Runtime 接线）**=** **工程仓库 MR** — **[`CC-P1-07`](../specs/requirements/contract-closure.md#cc-p1-07)** |

---

<a id="cc-impl-wave-hint"></a>

## 8. 实现波次指引（摘自 [`contract-closure` §5.2](../specs/requirements/contract-closure.md#cc-exec-remaining)）

**用途**：**研发 / PMO** **派工** **时** **与** **规格** **逐字一致** **的** **建议顺序**（**权威** **仍为** **上文 §5.2** **全文**；**此处** **仅** **摘录**）。**≈1 需求 + 1 开发** 时 **日常** **请** **优先** **[`LITE-MODE.md`](../specs/requirements/LITE-MODE.md)**；下列 **1～5** **在** **扩编 / 多方关单 / 对外冻结叙事** 时使用。

1. **首包**：**CC-P0-04 + CC-P0-05** — **GitHub 稿** [`contract-closure` §3.4](../specs/requirements/contract-closure.md#cc-p0-mr-github-full)；**必须先** **[§2.1](../specs/requirements/contract-closure.md#cc-p0-signoff-register)** **再** **动** **PRD §13** **`[x]`**。  
2. **继而**：**P0-03** **与** **P0-01**（**顺序可** **与** **所内资源** **对齐** **）。  
3. **再后**：**P0-02**（**矩阵 / WS** **终裁**）。  
4. **P1**：**MR-A～E** **拆单** [`§3.1`](../specs/requirements/contract-closure.md#cc-p1-batch-mr-split) — **勿** **单 MR 堆满**。  
5. **收口**：**全部 P0 + 相交 P1** **闭链** **后** **[§5.1](../specs/requirements/contract-closure.md#cc-stage4-spec-gate)** **`spec.md` 升格**。

派工与 MR 粘贴稿以 **[`contract-closure.md`](../specs/requirements/contract-closure.md)**（§3.2～§3.4、§5.2.6）为准；本仓库 **不** 在运营后台 Demo 内提供契约收口索引页。