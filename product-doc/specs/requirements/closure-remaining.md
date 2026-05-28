# 剩余关单与配置（执行索引）

**用途**：把 **[`contract-closure.md`](contract-closure.md)** **§2～§3** 的 **CC-P0 / CC-P1** 拆成 **「本 Git 仓库能推进」** 与 **「必须所内 / 实现 / 运维 / 财务完成」** 两列，降低「只改文档就算关单」的误读。**DoD 条文** **仍以** **`contract-closure`** **全文** **为准**；MR 粘贴稿 **§3.1～§3.4**。**三步收口（读 → 判 → 勾）**：[**§0 速链**](#closure-remaining-quicklinks) → **[§7.5 闭环路径](#cc-remaining-open-close-path)** → **[§7.6 MR 执行清单](#cc-closure-exec-checklist)**；**开工单/MR 前可贴** **[§6.4 问题→解决动作](#cc-problem-to-action)**（**`contract-closure` 文首/§10·§8 亦链入**）。

**与半页纸叙事**：对外话术 **仍以** **[`product/release-notes.md`](../../../product/release-notes.md)** **最新一节** **与** **[`LITE-MODE.md`](LITE-MODE.md) §3** **同窗**。

<a id="cc-unfinished-semantics"></a>

**未完成语义（统一口径）**：**别把三类「未完」混读** — **① 规格仍可演进**（仍可改 `specs` / OpenAPI / `design/api` / 互链；可称 **「规格已闭合」**，与 [§7.5 下方「状态语义」表](#cc-remaining-open-close-path) 同行 **同义**）；**② 契约未关**（[`contract-closure`](contract-closure.md) **§2～§3 CC**、**§9 六款**、**§2.1 会签** — **硬门禁**，**非**仅靠本文 §7.6 勾选即可）；**③ 执行层未落地**（所内 MR、Hosted、`openapi-ai` pin、Webhook/账务/合规实测、运维会签等），**须**见 [§6.1](#cc-remaining-61) **右列**、[§7.5](#cc-remaining-open-close-path) **OP-*** 行、[`contract-closure` §10](contract-closure.md#cc-section10-five) **五步** — **`product/`、`specs/` 内 Git 文档合并不代替** **证据与工单**。**A/B 分期** → [`contract-closure` §1.1](contract-closure.md#11-两阶段收口需求落地-vs-契约填链)；**分期叙事 / 对客承诺边界** → [`contract-closure` §3.0](contract-closure.md#cc-p1-doc-vs-b)。

<a id="closure-remaining-quicklinks"></a>

## 0. `contract-closure` 速链（合并描述用）

| 要做什么 | 锚点 |
|----------|------|
| **P0 会签证据表**（D-12 / D-5·D-7） | [§2.1](contract-closure.md#cc-p0-signoff-register) |
| **P1 MR 拆单** MR-A～E | [§3.1](contract-closure.md#cc-p1-batch-mr-split) |
| **P1 MR 描述粘贴稿** | [§3.2](contract-closure.md#cc-p1-mr-paste-templates) |
| **P1 GitHub 全稿** | [§3.3](contract-closure.md#cc-p1-mr-github-full) |
| **P0 GitHub 全稿** | [§3.4](contract-closure.md#cc-p0-mr-github-full) |
| **矩阵解冻** §4 + §7 | [§4](contract-closure.md#cc-section4-matrix) · [§7](contract-closure.md#cc-section7-template) |
| **`spec.md` 升格 gate** | [§5.1](contract-closure.md#cc-stage4-spec-gate) |
| **P0/P1 派工剩余表** | [§5.2](contract-closure.md#cc-exec-remaining) |
| **PRD §13 ↔ CC** | [§5.2.1](contract-closure.md#cc-521-prd-map) |
| **P1 首节 MR 骨架** | [§5.2.5](contract-closure.md#cc-p1-exec-mr-skeleton) |
| **CC-P1-07 · Canonical / Gateway（文档 A vs DoD B）** | [§3 · CC-P1-07](contract-closure.md#cc-p1-07)；评审速查 [`requirements-review` §7.5](../../product/requirements-review.md#cc-adr004-review-checklist)；**系统工程叙事** [`architecture.md`「与通用 Agent 栈之对照」](../design/architecture.md)（**§8 · 0.2.11** 登记） |
| **§1.2 可对签六款** 自检 | [§9](contract-closure.md#cc-section9-six) |
| **编排 · 对客三闸 / 评审检查单 / GWT** | [`implementation-alignment.md`](domains/agent/agent-orchestration/implementation-alignment.md) **§13** **·** **§6～§12**；**闸 1** **另须** **[`runtime-freeze` §3](domains/agent/agent-orchestration/runtime-freeze.md)** **↔** **[`routing-engine` 文首](domains/agent/agent-orchestration/routing-engine.md)** |
| **§10 五步节奏** | [§10](contract-closure.md#cc-section10-five) |
| **P1 文档 vs B** | [§3.0](contract-closure.md#cc-p1-doc-vs-b) |
| **「未完成」三类混读 · 统一口径 SSOT** | [篇首 · 未完成语义](#cc-unfinished-semantics) |
| **问题解决路径（谁能关闭什么）** | [§6 · 执行视图](#cc-exec-solve-path) · [§6.4 问题→解决动作](#cc-problem-to-action) |
| **剩余开放项总览（本文 §7）** | [§7 · 一键表](#cc-remaining-open-items) |
| **走读缺口粘贴模板** | [§7.1](#cc-remaining-gap-paste) |
| **未关闭项 · 闭环路径总表（DoD 对齐）** | [§7.5](#cc-remaining-open-close-path) |
| **闭环执行清单（MR / 工单可复制勾选）** | [§7.6](#cc-closure-exec-checklist) |
| **`contract-closure` §8.1 · 残余一行登记**（`CI：仅 GHA` / Timeline / OP-AvB） | [`contract-closure.md` §8.1 `#cc-section8-residual-paste`](contract-closure.md#cc-section8-residual-paste) |
| **PRS · 改什么去哪（Prompt / MNRA / skill-specs 派工）** | [`prompt-runtime/README` §4 `#prs-where-to-edit`](prompt-runtime/README.md#prs-where-to-edit) |
| **Skill L0 · 规格+原型对齐 SSOT** | [`skill-specs/requirements-closure.md`](skill-specs/requirements-closure.md) · **OP-SKILL** [**§7.5**](#cc-remaining-open-close-path) |
| **Skill MR-B · 所内 BFF/编排实现清单** | [`skill-specs/MR-B-BFF-IMPLEMENTATION.md`](skill-specs/MR-B-BFF-IMPLEMENTATION.md) |
| **概念管线 / Risk·Receipt·Timeline SSOT** | [`Runtime/domain-model.md`](Runtime/domain-model.md) **§1～§7** · [`pipeline-walkthrough-checklist.md`](Runtime/pipeline-walkthrough-checklist.md) |
| **所内 3 周冲刺 · MR 粘贴稿** | [`closure-internal-sprint.md`](closure-internal-sprint.md) **§1～§3**（**MR-RT-B4** / **SK-B01～B03** / **P0-01**） |
| **闭环完成度矩阵（绿/黄/红）** | [`closure-completion-matrix.md`](closure-completion-matrix.md) **§0 今日 W1** |
| **所内 Issue 模板** | [`closure-work-item-templates.md`](closure-work-item-templates.md) |
| **Staging 证据登记** | [`closure-staging-evidence-log.md`](closure-staging-evidence-log.md) |
| **规格仓 preflight** | [`scripts/closure-preflight.sh`](../../scripts/closure-preflight.sh) |
| **CC-P0-01 Hosted 运维勾选** | [`openapi/HOSTED-ROLLOUT-CHECKLIST.md`](../openapi/HOSTED-ROLLOUT-CHECKLIST.md) |
| **Prompt/Runtime §7.2 派工 · §7.4 AC-09 检核** | [§7.2](#cc-prompt-runtime-priority-close) · [§7.4](#cc-ac09-closure-matrix) |
| **Prompt/Runtime 闭环互引（同窗一览）** | [§7.3](#cc-prompt-runtime-closure-loop) |
| **Telegram 永续 SC ↔ `design/api`** | [`telegram/overview` §5 · `SC-CH-TG-FUT-01～03`](domains/agent/telegram/overview.md) · [`design/api` Telegram 专节 / 矩阵备注](../design/api.md) · [`contract-closure` §6](contract-closure.md) |

---

<a id="cc-remaining-p0"></a>

## 1. P0（系统性阻塞 · B 阶段生产承诺前）

| CC | A 阶段（文档）现状 | 本仓库可持续推进 | 所内 / 实现必做（关单必要条件） | 证据回填 |
|----|-------------------|------------------|----------------------------------|----------|
| **CC-P0-01** | `specs/openapi/*.yaml` + **`OWNERS`** + 登记表同窗 **(a)** | **合入 MR** 时保持 **`info.version`** **与** **`design/api` 第三列** **一致**；补链/勘误 | **(b) Hosted** Swagger/Redoc **或** **(c) `release-*` tag** **锚定合并**；**生产 PATH** **与矩阵** **终裁** | [`contract-closure` §8](contract-closure.md)、[`openapi/README` Hosted 段](../openapi/README.md) |
| **CC-P0-02** | 延期格已书面；非延期行与 `coobit-*.yaml` **已可 diff** | **矩阵解冻** MR：**递增** `design/api` 版本脚注 + **§4** **登记影响面** | **所内 PATH 冻结** **或** **更新延期备注与实现一致** | **§4、§7** 模板 |
| **CC-P0-03** | 账务三线 YAML + **`billing-schemas`** **骨架**；**`billing.md` §12.1** **模板** | **OpenAPI 字段** 与 **域 §7～§9** **同窗 MR**；**不手写生产 host 真值** | **生产 BFF/网关 baseUrl** **首填**；**shadow→enforce** **Runbook** | **`billing` §12.1**、实现 MR |
| **CC-P0-04** | **`billing` §10.6.1** **范式 A/B/C** + 检查单 | **仅维护文档与 schema 同窗**；**禁止**在仓内写 **真实专户 id** | **财务书面会签** + **配置首填** + **审计 id** | **[§2.1](contract-closure.md#cc-p0-signoff-register) `CC-P0-04` 行** |
| **CC-P0-05** | **`billing` §10.3.1** **检查单**；**PRD §11** **已锚** | **文档勘误/链** **随实现 MR 同窗** | **D-5 / D-7** **实现逐项勾选** + **`SC-OBS03` / UNKNOWN 计费** **终裁** | **[§2.1](contract-closure.md#cc-p0-signoff-register) `CC-P0-05` 行**；**禁止** **无 MR 预改** **PRD §13 `[x]`** |

---

<a id="cc-remaining-p1"></a>

## 2. P1（并行收口）

| CC | 文档侧 | 本仓库可推进 | 所内 / 实现必做 | 建议 MR |
|----|--------|--------------|-----------------|---------|
| **CC-P1-01** | OCO/bracket **已登记** + **矩阵延期**；[**`product.md`**](product.md) **§非目标：本阶段 Agent 不交付 OCO/bracket `call_exchange_write` 闭环（2026-05-20）** | **MR-D** **分支 B**：窄 MR 重申矩阵延期邻域；**分支 C**：与 **`product.md` / `trade-via-agent` / `telegram/overview` / `agent-coobit-api-allowlist` §3** 同窗 | **若宣称经 Agent 完成 OCO/bracket 写**：**须** **矩阵 PATH 冻结 + 解除 `product.md` §非目标 + §4·§7 同窗** | **MR-D** |
| **CC-P1-02** | ADR-003 + **`ToolRegistryEntry`** | Schema/域 **同窗 MR** | **生产 Enable C 类**：**`legalReviewTicketId`** + **法务工单**；**写闸** | **MR-A** |
| **CC-P1-03** | ADR-002 + **`tool-management`验收句** | **OpenAPI/域** **勘误** | **DB/镜像** **`toolId`/`skillId` 幂等** + **`SC-MCV1-05` / `SC-OBS01`** | **MR-E** |
| **CC-P1-04** | 域 **「评审中」**；**仓库内** [`admin/prompt-management.yaml`](../openapi/admin/prompt-management.yaml) **`design/api` Prompt 行** | **§1.4 核对表** **随 MR 更新** | **多模块会签** + **Hosted 生产实测**（若宣称 B） | **MR-B** |
| **CC-P1-05** | **architecture** **容器 mermaid** **已载** | 可选：外链高清图 | **非 P0 阻塞** | — |
| **CC-P1-06** | **`admin/telegram-channels.yaml`** + 域 | **YAML/域** **同窗 MR** | **setWebhook / getWebhookInfo / `secretRef`** **生产实测** + **SC-TAC / SC-TG-ADMIN** | **MR-C** |

---

## 3. 配置与示例（本仓库可对照）

| 主题 | 位置 |
|------|------|
| **账务三线生产 baseUrl 登记模板** | [`billing-management/overview.md`](domains/admin/billing-management/overview.md) **§12.1** |
| **`BILLING_*` / `configKey` SSOT** | [`trading-agent-config/keys.md`](domains/admin/trading-agent-config/keys.md) **§5**（含 **`BILLING_AGENT_REVENUE_ACCOUNT_REF`**） |
| **D-12 范式与检查单** | [`billing-management/overview.md`](domains/admin/billing-management/overview.md) **§10.6.1** |
| **D-5 / D-7 实现检查单** | [`billing-management/overview.md`](domains/admin/billing-management/overview.md) **§10.3.1** |
| **Demo 前端 env 占位（非生产）** | [`src/admin/.env.example`](../../src/admin/.env.example) |
| **逻辑部署与环境** | [`design/deployment.md`](../design/deployment.md) |
| **`openapi-ai` 制品 pin（对上 Coobit HTTP）** | [`integrations/exchange/overview.md`](integrations/exchange/overview.md)、[`design/deployment.md`](../design/deployment.md) **§3·§6** |

---

## 4. §1.2 六款（关单前自检一句话）

**单行能力** **宣称对客可用** **前** **须** **逐项** **满足** **[§1.2 与 §9](contract-closure.md#cc-section9-six)**：**`design/api` 行**、**`trade-assistance` §8**、**exchange-agent 分卷**、**编排与 ADR-001** **及** **`runtime-freeze` §3**（**§3.1～§3.11** **最小编排** **↔** **`routing-engine` 文首**）、**automation/Pull**、**（若依赖 WS）`Runtime/reconciliation` 矩阵**。**口语化三闸与 MR 门禁** **另见** [`implementation-alignment` §13.1](domains/agent/agent-orchestration/implementation-alignment.md)（**与** **§1.2** **同窗** **不替代**；**闸 1** **=** **寄存器 / §8** **之外** **还须** **§3**）。**永续 / 条件单从 Telegram 出站** **另须** **卡面与矩阵同窗**：[`telegram/overview` §5](domains/agent/telegram/overview.md) **`SC-CH-TG-FUT-01～03`** **↔** **[`design/api`](../design/api.md)** **Telegram 专节**（**§0 表末行**）。本文件 **不** **展开六款全文**。

---

## 5. 纪律（重复强调）

1. **`management-console-v1-prd` §13** **`D-12`、`D-5`/`D-7`**：**仅**在 **[§2.1](contract-closure.md#cc-p0-signoff-register)** **已填证据** **且** **实现 MR** **合并后** **`[ ]`→`[x]`**。  
2. **`spec.md` Status / 对外「生产契约已冻结」** **仅** **[§5.1 gate](contract-closure.md#cc-stage4-spec-gate)**。  
3. **本文件** **不** **替代** **§8 版本登记**；关单后 **仍须** **在** **`contract-closure` 文末** **递增文档版本** **（若团队惯例要求）**。

---

## 6. 问题解决路径（执行视图）

<a id="cc-exec-solve-path"></a>

**结论**：**任一 CC-P0 / CC-P1 的「DoD 全文关闭」** **都无法** **仅靠本仓库 Markdown** **独立完成**。上文 §1～§2 **已按列拆分** **「Git MR 可推进」** **vs** **「所内 / 实现 / 运维 / 财务必做」**；本节补充 **合并 MR 推荐阅读顺序**（**与** [`contract-closure` §3.1 MR-A～E](contract-closure.md#cc-p1-batch-mr-split) **同窗**），便于 **排期**，避免 **误以为「改了文档」** **即等价于关单**。

### 6.1 仅靠文档做不到的部分（必须所内收口）

<a id="cc-remaining-61"></a>

| 类别 | 代表 CC | 所内需交付的证据 |
|------|---------|------------------|
| **运维 / 发布** | **CC-P0-01** | **Hosted** Swagger/Redoc **或** **`release-*` tag** **锚定合并 MR**；**生产 PATH** **与矩阵一致** |
| **网关 / 账务 / Runbook** | **CC-P0-03** | **生产 baseUrl**（[`billing` §12.1](domains/admin/billing-management/overview.md) **模板首填**）、**`shadow→enforce`**、扣减 HTTP **与** **OpenAPI** **同窗实测** |
| **财务** | **CC-P0-04** | **`BILLING_AGENT_REVENUE_ACCOUNT_REF`**：**会签工单号**、**首填 MR**、**审计 id**（[`contract-closure` §2.1](contract-closure.md#cc-p0-signoff-register)） |
| **实现 / 观测** | **CC-P0-05** | **`billing` §10.3.1** **逐项勾选**、**`SC-OBS03`/UNKNOWN 计费** Runbook；**此后** **方可** **PRD §13 `D-5`/`D-7` `[x]`** |
| **法务** | **CC-P1-02** | **C 类工具 Enable**：**`legalReviewTicketId`** + **书面 PII/预算** |
| **工程 DB / 镜像** | **CC-P1-03** | **`toolId`/`skillId` 幂等**、**`SC-MCV1-05` / `SC-OBS01`** |
| **多模块会签 +（可选）实测** | **CC-P1-04** | Prompt **跨 billing/telegram/observability** **会签**；若宣称 **B** → **Hosted/生产** |
| **网关 Telegram** | **CC-P1-06** | **`secretRef`、Webhook CRUD、`getWebhookInfo`、自检** + **SC-TAC / SC-TG-ADMIN** |

<a id="cc-remaining-62-merge-order"></a>

### 6.2 推荐合并顺序（在 §10 五步之内切片）

1. **地基**：**CC-P0-01** **(b)(c)** **与** **登记表 `info.version`** **同窗**（**可与** OpenAPI 勘误 **同 MR**）。  
2. **账务主线**：**CC-P0-03** **实现 MR** **（常含** **billing 三线 BFF** **与** **`billing.md` §12.1 首填** **草稿）** → **再动** **shadow→enforce**。  
3. **观测耦合**：**CC-P0-05** **绑定** **账务/Agent 实现 MR**，**禁止** **单独改 PRD §13 勾选**。  
4. **财务专户**：**CC-P0-04** **独立工单/MR** **（财务门禁）**。  
5. **并行 P1**：**MR-C（Telegram 后台）** **常与** **网关首批** **同窗**；**MR-A（外网工具）** **独立合规评审**；**MR-B / MR-E** **按模块人力并行**。  
6. **OCO/bracket**：[**`product.md`**](product.md) **§非目标** — 若 **禁止 Agent 现货 OCO/bracket 写** → **MR-D 分支 C** 落档。若 **仅矩阵延期** → **MR-D 分支 B**。若 **宣称矩阵解冻且经 Agent 完成 OCO/bracket 实盘** → 须 **§4·§7** 且 **解除 §非目标**。

### 6.3 「解决」的验收口径

**对客宣称「已支持」** **仍须** **满足** [`contract-closure`](contract-closure.md) **§1.2** **六款齐备**（条文），并在 MR 中 **复制勾选** **[§9 自检表](contract-closure.md#cc-section9-six)**。**走小团队节奏时** **另附** [`LITE-MODE` §2](LITE-MODE.md) **条件第五块** **与** [`implementation-alignment` §13.1](domains/agent/agent-orchestration/implementation-alignment.md) **三闸**（**宣称闭环** **时**）。**需求文档冻结（A）** **≠** **本条意义上的「问题解决」** — **见** [`contract-closure` §3.0](contract-closure.md#cc-p1-doc-vs-b)。**若要逐项消灭上一轮盘点的问题** → **先排** **[§6.4 问题→解决动作](#cc-problem-to-action)**（可复制到工单/MR 首节），**再结合** **[§6.2 推荐合并顺序](#cc-remaining-62-merge-order)**。

---

<a id="cc-problem-to-action"></a>

### 6.4 问题 → 解决动作（工单 / MR 首节可复制）

**用途**：把「仍存在的主要问题」落成可派工、可认领的动词，避免只有叙述没有动作。**不** **替代** [`contract-closure`](contract-closure.md) **[§2](contract-closure.md)～[§3](contract-closure.md) DoD**；回填证据仍以 **[§2.1](contract-closure.md#cc-p0-signoff-register)**、**[§8](contract-closure.md)**、**[§9](contract-closure.md#cc-section9-six)** 为准。表中 **Owner** 为角色占位，所内可更名。

| 口语症状 | 关单最低证据 | 建议 Owner | 首节动作（可复制） | 主链入口 |
|----------|--------------|------------|-------------------|----------|
| 「文档齐了 = 可当生产」误读 | 若宣称 B：[§9 六款](contract-closure.md#cc-section9-six) 自检 + Hosted/tag/矩阵同窗 | 产品 + 接口 + 实现 | MR 首节按 [§10 五步](contract-closure.md#cc-section10-five)；[§8.1](contract-closure.md#cc-section8-residual-paste) 登记 OP-AvB / Timeline 等 | [§1.1](contract-closure.md#11-两阶段收口需求落地-vs-契约填链)、[§3.0](contract-closure.md#cc-p1-doc-vs-b)、[§7.5](closure-remaining.md#cc-remaining-open-close-path) |
| OpenAPI Hosted / `release-*` tag 缺口 | (b)(c) 与登记表 `info.version` 同窗；[§8](contract-closure.md) 顶行 | 运维 + 实现 | 搭建 Hosted 或打 `release-*` tag 的 MR；附合并 SHA/URL | [§6.1 · CC-P0-01](#cc-remaining-61)、[`openapi/README`](../openapi/README.md) |
| 账务网关 / shadow→enforce 未落地 | 生产 baseUrl 首填 + 扣减 HTTP 与 OpenAPI 同窗实测 | 网关 + 账务 + 实现 | [§6.2](closure-remaining.md#cc-remaining-62-merge-order) 顺序：CC-P0-03 实现 MR → 再动 shadow→enforce | [contract-closure §2](contract-closure.md)、[§6.1 · CC-P0-03](#cc-remaining-61) |
| 财务专户未会签 / 未首填 | 会签工单号 + MR + 审计 id | 财务 + 实现 | 独立工单/MR；填 [§2.1](contract-closure.md#cc-p0-signoff-register) CC-P0-04 行 | [§6.1 · CC-P0-04](#cc-remaining-61) |
| D-5·D-7 / 观测未勾选 | `billing` §10.3.1 逐项 + SC-OBS03/UNKNOWN Runbook | 实现 + 观测 | 绑定账务/Agent MR；禁止无实现 MR 预改 PRD §13 | [§6.1 · CC-P0-05](#cc-remaining-61) |
| 十步管线顺序错 / Risk 漏闸 / Receipt 与 Timeline 混读 | 所内编排 **对拍** [`domain-model` §4](Runtime/domain-model.md)；走读 **SC-OBS08/11** | 产品 + Runtime | MR 首节链 **domain-model**；实现自检 **R1～R4** 全时点 | [`domain-model`](Runtime/domain-model.md)、[`trade-via-agent`](flows/trade-via-agent.md) **S1～S10** |
| 编排 §3 实现未见证 | Runtime 轨迹或单测对拍 `runtime-freeze` §3 **且** [`domain-model` §4](Runtime/domain-model.md) 禁止项 | 实现 | 所内 Agent Runtime MR；抽检 [e2e Walkthrough](../../../flow/e2e-closed-loop.md#runtime-walkthrough) | [§7 一键表 · 编排 §3](#cc-remaining-open-items)、[`runtime-freeze` §3](domains/agent/agent-orchestration/runtime-freeze.md) |
| `openapi-ai` 宿主 / 制品未证 | PATH 断言 + `deployment` §6 回填 | 实现 + 运维 | 实现仓库同窗 MR + 设计部署文档回填 | [§7 · openapi-ai](#cc-remaining-open-items)、[`integrations/exchange/overview`](integrations/exchange/overview.md) |
| Prompt Runtime 拼装链（宣称 B） | MR-B 会签 + §9 样例 +（若 B）Hosted/生产 | 产品 + Runtime | 按 [§7.2～§7.4](#cc-ac09-closure-matrix) 派工；CC-P1-04 | [`runtime-injection`](domains/admin/prompt-management/runtime-injection.md)、[contract-closure CC-P1-04](contract-closure.md) |
| 计费轨 B（订阅/Capability/包）未接线 | OpenAPI 骨架 + `productionRuntime` 小样 + Admin 演示；**所内** BFF/账务 HTTP + staging | 账务 + Runtime + BFF | [`closure-internal-sprint` · MR-BILL-B1/B2](closure-internal-sprint.md)；**勿**误计入 **CC-P0-03** 关单 | [`commerce-model`](domains/admin/billing-management/commerce-model.md)、[§7 · Phase 2 商业轨 B](#cc-remaining-open-items) |
| 不知先做哪条 MR | 按周拆单 | 全员 | 打开 [`closure-internal-sprint` §1～§2](closure-internal-sprint.md)；W1 起 **MR-RT-B4** + **SK-B1/B2** | [§7.7](#cc-internal-sprint-dispatch) |

---

<a id="cc-remaining-open-items"></a>

## 7. 剩余开放项总览（需求与契约 · 一键表）

**用途**：把上文 **§1～§2、§6** **之外的「还容易漏」** **收成一张总检**，**不** **重复** **`contract-closure` §2～§3** **全文**。**关闭任一 CC** **仍以** **主表 DoD** **为准**。**每条「仍未关」如何收到唯一出口** → **[§7.5 闭环路径总表](#cc-remaining-open-close-path)**（**与下表对照读**）；**可复制勾选推进** → **[§7.6](#cc-closure-exec-checklist)**。

| 开放面 | 仍开放什么（需求口径） | 权威锚点 | 本仓 Markdown 能做的 | 须外部 / 实现关闭的 |
|--------|------------------------|----------|----------------------|---------------------|
| **A ≠ B** | **文档/需求路径齐（A）** **≠** **可对客承诺（B）** | [`contract-closure` §1.1](contract-closure.md#11-两阶段收口需求落地-vs-契约填链)、[§3.0](contract-closure.md#cc-p1-doc-vs-b) | **勘误叙述**、MR 描述 **显式** **标 A 或 B** | **Hosted/tag、矩阵终裁、§1.2 六款** |
| **P0 闸** | **OpenAPI 登记、矩阵延期格、账务三线、D-12、D-5/D-7** | [`contract-closure` §2](contract-closure.md)：CC-P0-01～05 | **OpenAPI/YAML/域文同窗 MR**；**§2.1** **证据表占位说明** | **§6.1** **表** **所列** **运维/网关/财务/实现** |
| **P1 闸** | **OCO 矩阵延期、C 类法务、Registry 幂等、Prompt 会签、Webhook 实测** | [`contract-closure` §3](contract-closure.md)：CC-P1-01～06 | **MR-A～E** **文档轨**、**MR-D** **窄 MR** **重申延期** | **§6.1** **表** **所列** **法务/DB/会签/网关** |
| **编排 §3** | **写路径最小编排** **已** **写在** **`runtime-freeze` §3**；**实现是否遵守** **未** **在本 Git 证完** | [`runtime-freeze` §3](domains/agent/agent-orchestration/runtime-freeze.md)；[`routing-engine` 文首](domains/agent/agent-orchestration/routing-engine.md)；[`planner-contract.md`](Runtime/planner-contract.md) | **抽检** **[`e2e` Walkthrough](../../../flow/e2e-closed-loop.md#runtime-walkthrough)**、**JV-07**、§13 **评审** | **所内 Agent Runtime**：Planner/恢复 **轨迹或单测** **对 §3** |
| **体验抽检** | **六款齐** **仍可能** **卡** **主态叙事/UNKNOWN/槽位** | [`contract-closure` §1.3](contract-closure.md#13-流程体验与卡点可解释抽检--建议与-12-同窗-mr) | **域/flows 补丁**、eval **登记** | **产品走查 / QA** |
| **`openapi-ai` 宿主** | **规格已纳**：**出站默认 `openapi-ai`（pin）**；**网关 PATH 断言 / 制品落地** **未在本 Git 证完** | [`integrations/exchange/overview`](integrations/exchange/overview.md)；[`design/deployment`](../design/deployment.md) §3·§6；[`api` 边界](../design/api.md) | **聚合索引** **`spec` / `Runtime` / `tools` / `domains`** **同窗链** | **实现仓库** **+** **`deployment` §6** **回填** |
| **Prompt Runtime 拼装链** | **§1～§4、§7** **条文已齐**；**对客 B** **须** **实现拼装 + Publish 闸 + 观测 join**（**不等价** **仅文档**） | [`runtime-injection`](domains/admin/prompt-management/runtime-injection.md)；[`observability` §2.3](observability/overview.md)；[`contract-closure` CC-P1-04](contract-closure.md) | **[§7.2～§7.4](#cc-ac09-closure-matrix)** **派工 · AC-09 勾表**；**里程碑** **须** **`/pm`** **切段** | **所内 Agent Runtime** **+** **CC-P1-04 Hosted/会签**（若宣称 B） |
| **Memory STM/LTM** | **§9～§16、`FEATURE_SEMANTIC_NARRATIVE`、四原则硬闸、`keys` §2.1 默认、§14.6 stale+Resume、意图/UX 分流** **条文已齐**；**OpenAPI `MemoryRuntimeConfigSnapshot` + `episodePickReason` + Eval GWT 已齐**；**`clarify-session` v1.6**（**§1.1 类型A×stale · §2.5 去重**）；**Prompt library L1 Memory/Facts + registry §1.2 已齐**；**LTM 契约仍草案 · 默认 OFF** | [`memory-runtime`](Runtime/memory-runtime.md)；[`clarify-session`](domains/agent/agent-orchestration/clarify-session.md)；[`memory-runtime-schemas.yaml`](../openapi/components/memory-runtime-schemas.yaml)；[`design/memory-runtime-injection`](../design/memory-runtime-injection.md)；[`keys` §2.1](domains/admin/trading-agent-config/keys.md)；[`evals/memory-runtime.md`](evals/memory-runtime.md)；[`evals/clarify-telegram.md`](evals/clarify-telegram.md)；[`evals/idle-default-stale.md`](evals/idle-default-stale.md)；[`evals/resume-classifier-gate.md`](evals/resume-classifier-gate.md)；[`evals/resume-classifier-multi-episode.md`](evals/resume-classifier-multi-episode.md) | **Eval 登记** **+** **§12/§16 自检** **+** **§7 Eval CI 登记（design）** | **STM 实现 MR**（**§16 硬闸 + §2.3 重意图 + §14.6 stale/Resume**）· **所内 CI 跑 P0 eval** · **LTM 全闭环（B）须解冻 + §1.2 · [§7.5 OP-MEM](#cc-remaining-open-close-path)** |
| **Session 并发（P0）** | **`session-concurrency-policy` v1.0** · **`FR-AO07`/`SC-AO-09～10`** · **`keys` §2.2 `SESSION_*`** · **Eval GWT 已齐** | [`session-concurrency-policy`](domains/agent/agent-orchestration/session-concurrency-policy.md)；[`keys` §2.2](domains/admin/trading-agent-config/keys.md)；[`evals/session-concurrency.md`](evals/session-concurrency.md)；[`locking`](Runtime/locking.md)；[`clarify-session` §1.1](domains/agent/agent-orchestration/clarify-session.md) | **互引 + eval 登记** | **所内 Runtime/BFF MR**（**inbound 队列 · 在途写上限 · D-1**）· **P0 eval 同窗 MR-MEM** |
| **只读澄清（P1）** | **`read-clarify-session` v1.0** · **`FR-AO08`/`SC-READ-CLARIFY-*`** · **`keys` §2.3** · **`rc:*`** | [`read-clarify-session`](domains/agent/agent-orchestration/read-clarify-session.md)；[`read-analyze`](flows/read-analyze-and-search-via-agent.md)；[`evals/read-clarify-telegram.md`](evals/read-clarify-telegram.md) | **互引 + eval 登记** | **所内 BFF/Parser MR** · **P1 eval** |
| **Fallback/Retry 决策树（P1）** | **`fallback-policy` v0.4** **§2 场景表** · **`SC-RT-FB-*`** · **`eval.fallback.*` GWT** | [`fallback-policy`](Runtime/fallback-policy.md)；[`recovery`](Runtime/recovery.md)；[`retry-policy`](domains/agent/agent-orchestration/retry-policy.md)；[`evals/fallback-retry-decision-tree.md`](evals/fallback-retry-decision-tree.md) | **互引 + eval 登记** | **所内 Runtime MR** · **P1 eval 同窗 MR-MEM** |
| **UNKNOWN 追问状态机（P1）** | **`unknown-stall-policy` v0.2** **§2** · **`SC-RISK-07*`** · **`keys` §2.4** · **`eval.unknown.*`** | [`unknown-stall-policy`](risk/unknown-stall-policy.md)；[`session-concurrency-policy` §5.3](domains/agent/agent-orchestration/session-concurrency-policy.md)；[`evals/unknown-followup-telegram.md`](evals/unknown-followup-telegram.md) | **互引 + eval 登记** | **所内 Runtime/BFF MR** · **P1 eval** |
| **Fallback/Retry 决策树（P1）** | **`fallback-policy` v0.4** **§2** · **`SC-RT-FB-*`** · **`eval.fallback.*`** | [`fallback-policy`](Runtime/fallback-policy.md)；[`recovery`](Runtime/recovery.md)；[`retry-policy`](domains/agent/agent-orchestration/retry-policy.md)；[`evals/fallback-retry-decision-tree.md`](evals/fallback-retry-decision-tree.md) | **互引 + eval 登记** | **所内 Runtime MR** · **P1 eval 同窗 MR-MEM** |
| **Market Narrative System** | **需求 + OpenAPI 骨架 + design 管线 v0 已齐**；**ANALYSIS Few-shot Git 镜像 + library registry §1.2 已齐**；**hints 仍草案 · 阈值 TBD** | [`market-intelligence` §4](domains/agent/exchange-agent/market-intelligence.md)；[`common-phrases` §8](prompts/shared/common-phrases.md)；[`market-runtime-payload`](domains/agent/exchange-agent/market-runtime-payload.md)；[`fewshot-narrative-analysis`](prompts/library/packs/fewshot-narrative-analysis.zh-CN.md) | **Eval `eval.market.narrative_*`** | **Runtime analytics MR + phase 规则数值冻结 + Publish 生效版** |
| **计费 · Phase 2 商业轨 B** | **OpenAPI + `design/api` + `productionRuntime` S2/S5 小样已入库**；**Admin 总览 Commerce 演示卡**；**不**扩写 **CC-P0-03 DoD** | [`commerce-model.md`](domains/admin/billing-management/commerce-model.md)；[`internal/billing-entitlements.yaml`](../openapi/internal/billing-entitlements.yaml)；[`consume-and-bill`](flows/consume-and-bill.md) | **勘误/链**、**closure 勾选**、**原型 mock** | **MR-BILL-B1/B2** 宿主接线 · **Hosted/生产** · **`contract-closure` §8 轨 B MR** |

---

<a id="cc-remaining-gap-paste"></a>

### 7.1 走读缺口纪要（粘贴块）

**用途**：[`product/roadmap.md`](../../product/roadmap.md) **A3**、[`flow/e2e-closed-loop.md`](../../flow/e2e-closed-loop.md)（文首 **「架构语言」** → [`architecture` §「与通用 Agent 栈之对照」](../design/architecture.md)）**自检** **或** **评审会** **产出「缺口清单」** 时 **整表复制到纪要/工单**；**行级关单** **仍以** [`contract-closure`](contract-closure.md) **§2～§3** **DoD** **与** **证据链** **为准**（**本表** **不** **替代** **§2.1**）。

| 缺口（一句话） | CC / 锚点（可点链接或 §） | Owner | 目标日期 | 闭环状态 |
|----------------|---------------------------|-------|----------|----------|
| **概念十步管线 / Risk·Receipt·Timeline 混读** | [`Runtime/domain-model.md`](Runtime/domain-model.md) **§1～§4** · [`trade-via-agent`](flows/trade-via-agent.md) **S1～S10** | 产品 + Runtime | — | **规格已闭合（A）** · **所内编排须对拍 §4 禁止项 · [§7.5 OP-AO3/SK-B02](#cc-remaining-open-close-path)** |
| _（示例 · 复制本行后改字）矩阵某格 TBD 且不宜宣称闭环_ | `contract-closure` CC-P0-02 · `design/api` 行 ___ | ___ | `YYYY-MM-DD` | _模板_ |
| _（示例 · 复制本行后改字）§3 写路径实现未见证_ | §7 表「编排 §3」· 所内 Runtime MR ___ | ___ | `YYYY-MM-DD` | _模板_ |
| Runtime §1～§4 拼装与发布闸在实现侧可审计、可对客 B | **[§7.2～§7.4](#cc-ac09-closure-matrix)** · **09a～09e** · **CC-P1-04** | ___ | ___ | **规格已闭合** · **须** **Runtime MR +（若宣称 B）MR-B 会签 + §9 样例 · [§7.5 行 OP-PR](#cc-remaining-open-close-path)** |
| `requires_main_site` 在 OpenAPI/编排路径非空可追溯 | **`runtime-injection` §2.4** · **`boundaries`** · **09l** | ___ | ___ | **规格已闭合** · **须** **`design`/OpenAPI 冻键 + 编排/错误归一 MR · [§7.5 行 OP-09L](#cc-remaining-open-close-path)** |
| 事件级 `promptPackVersion`：**要 / 不要** 已决；若要则 observability MR | **[§7.4](#cc-ac09-closure-matrix)** Timeline · [`observability` §2.3.1](observability/overview.md) | 产品 | ___ | **默认（执行级）规格已闭合**；**坚持事件级** → **须** **`observability` §2 MUST MR · [§7.5 行 OP-TML](#cc-remaining-open-close-path)** |
| Memory STM 召回 / LTM 解冻 / 四原则硬闸 / stale+Resume / budget 裁剪 | **`memory-runtime` §9～§16** · **`keys` §2.1** · **`memory-runtime-schemas.yaml`** · **`design/memory-runtime-injection` §2.4～§7** · **`clarify-session`** · **`evals/memory-runtime.md`** · **`evals/clarify-telegram.md`** · **`evals/idle-default-stale.md`** · **`evals/resume-classifier-gate.md`** · **`FEATURE_SEMANTIC_NARRATIVE`** · **`eval.memory.*`** | Runtime + 产品 | ___ | **规格已闭合（A）** · **OpenAPI/Eval GWT/配置默认齐** · **STM 须实现 MR + 所内 CI P0 eval** · **LTM 全闭环（B）须解冻 + §1.2 · [§7.5 OP-MEM](#cc-remaining-open-close-path)** |
| Session 并发 inbound 队列 / 多 execution / D-1 / 改单链 | **`session-concurrency-policy`** · **`FR-AO07`/`SC-AO-09～10`** · **`keys` §2.2** · **`eval.session.*`** | Runtime + 产品 | ___ | **规格已闭合（A）** · **须所内 BFF/Runtime MR + P0 eval · 同窗 MR-MEM** |
| 只读澄清 ReadClarify / `rc:*` / 写读对称分流 | **`read-clarify-session`** · **`FR-AO08`** · **`keys` §2.3** · **`eval.read_clarify.*`** | Runtime + 产品 | ___ | **规格已闭合（A）** · **须所内 Parser/BFF MR + P1 eval** |
| Fallback/Retry 场景决策树 · 504/确认门/澄清分流 | **`fallback-policy` §2** · **`SC-RT-FB-*`** · **`eval.fallback.*`** | Runtime + 产品 | ___ | **规格已闭合（A）** · **须所内 Runtime MR + P1 eval · 同窗 MR-MEM** |
| UNKNOWN 追问 · status/新写/重放/撤单 | **`unknown-stall-policy` §2** · **`SC-RISK-07*`** · **`keys` §2.4** · **`eval.unknown.*`** | Runtime + 产品 | ___ | **规格已闭合（A）** · **须所内 Runtime/BFF MR + P1 eval** |
| Market Narrative / `marketPhase` / Funding 锚句 | **`market-intelligence` §4** · **`common-phrases` §8/§8.7** · **`market-runtime-schemas.yaml`** · **`eval.market.narrative_*`** | Runtime + Prompt | ___ | **规格已闭合（A）** · **OpenAPI 骨架齐** · **phase 规则数值 + hints 注入 MR · [§7.5 OP-NAR](#cc-remaining-open-close-path)** |

---

<a id="cc-prompt-runtime-priority-close"></a>

### 7.2 Prompt / Runtime 闭环派工（按优先级）

**用途**：与 **内部 AC-09 族**（拼装链、`requires_main_site`、欢迎语、时间线粒度、Registry CI）**对齐派工顺序**。**改 Prompt / MNRA / skill 条文前先查** → **[PRS §4 改什么去哪](prompt-runtime/README.md#prs-where-to-edit)**。**闭环索引（已挂锚文档）** → **[§7.3](#cc-prompt-runtime-closure-loop)**。**本节** **不** **替代** [`contract-closure`](contract-closure.md) **DoD**；**B 阶段生产承诺** **仍须** **§1.2 六款** **+** **实现证据**；**关单 Prompt（CC-P1-04 / MR-B）** **须** **与** [`contract-closure` §3 **CC-P1-04**](contract-closure.md) **证据链同窗**（**含** **§7.2～§7.3**）。

| 优先级 | 闭环项 | 需求侧 DoD / 收口动作 | 权威锚点 | 本 Git 文档 | 须所内 / 实现 |
|:------:|--------|----------------------|----------|-------------|----------------|
| **高** | **完整 runtime 拼装链 + Tool JSON Schema + Few-shot + `variableSchema` + 白名单 / denylist** | 分段验收：**(1)** §1 **语义顺序**可审计 **(2)** §4 **仅 SSOT Tool Schema** **(3)** §2 **变量闸 + §2.3 denylist** **(4)** §3 **`resolvedPromptBinding` 冻结** **(5)** **观测** 能 join 绑定快照（**SC-OBS04**） | [`runtime-injection`](domains/admin/prompt-management/runtime-injection.md) **§1～§7**；[`observability` §2.3](observability/overview.md)；[`prompt-management/functions`](domains/admin/prompt-management/functions.md) **SC-PM-*** | **条文 SSOT 已齐** | **Runtime 实现 MR**；**CC-P1-04** **多模块会签**；**里程碑** **建议单独立项** |
| **中** | **`requires_main_site` / `user_visible_message` 结构化落地** | **OpenAPI / 编排信封** **显式挂键**；Runtime **禁止静默丢字段**；**`true`** **仅当** **`boundaries`** **已冻结** 且无 TG 闭环 | [`runtime-injection` §2.4](domains/admin/prompt-management/runtime-injection.md)；[`exchange-agent/boundaries`](domains/agent/exchange-agent/boundaries.md) | **键名 / 语义下限已写** | **`design`** **冻字段形状**；**编排 / 错误归一化** **同窗 MR** |
| **中** | **开通欢迎语 §2.1.1** | **`TELEGRAM_AGENT_ACTIVATION_WELCOME_*`** **+** **回退链** **+** **渠道运维可配** | [`telegram/overview` §2.1.1](domains/agent/telegram/overview.md)；[`keys` §4.2](domains/admin/trading-agent-config/keys.md)；[`admin-bot-config` FR-TG-ADMIN](domains/agent/telegram/admin-bot-config.md) | **条文齐** | **配置首填**；**SC-TG-ADMIN-05** **实测** |
| **中** | **Timeline：`promptPackVersion` 事件级 vs 执行级** | **产品先决**：若 **不需要** **每 NLU/LLM 事件** 单独版本 → **维持** **执行级** **`ResolvedPromptBinding`**（**与现 observability §2.3 一致**）。**若需要** → **须** **增补** **`observability` §2 MUST** **+** **编排事件 MR** | [`observability` §2.3](observability/overview.md)；[`runtime-injection` §3](domains/admin/prompt-management/runtime-injection.md) | **默认**：**执行级已规定**；**升级** **须** **规格同窗** | **埋点 / 时间线产品** |
| **低** | **`registry` ↔ `routing-engine` 一致性脚本进 CI** | 改 **`registry.md` / `routing-engine.md`** 时 **`FAIL=0`**；**GitHub：`pull_request` 全量跑 + `workflow_dispatch`** | [`prompts/library/README`](prompts/library/README.md)；[`check_registry_vs_routing_engine.py`](prompts/library/scripts/check_registry_vs_routing_engine.py) | **已挂** **[`.github/workflows/prompt-registry-consistency.yml`](../../.github/workflows/prompt-registry-consistency.yml)** | **非 GitHub** **宿主**：**.pipeline** **中跑同条命令** |

---

<a id="cc-prompt-runtime-closure-loop"></a>

### 7.3 闭环互引（同窗回链一览）

**用途**：把 **§7.2** **派工表** **与** **仓库内已挂锚** **之入口** **收成** **可追溯闭环**。**本表** **为导航**；**「可对签关闭」** **仍以** [`contract-closure`](contract-closure.md) **§2～§3** **主表 DoD**、**§9 六款** **为准**。**MR-B（CC-P1-04）** **证据链** **须** **含** **§7.2～§7.3**（**与** **本条** **对齐**）。

| 方向 | 位置 |
|------|------|
| **契约主链** | [`contract-closure` §3 · CC-P1-04](contract-closure.md) **；** **MR-B** **证据链** **（** [`§3.2`](contract-closure.md#cc-p1-mr-paste-templates) **/ ** [`§3.3`](contract-closure.md#cc-p1-mr-github-full) **）** |
| **编排实现对齐** | [`implementation-alignment` 文首互引](domains/agent/agent-orchestration/implementation-alignment.md)（同窗 **`closure-remaining`**：**§6**、**§6.4**、**§7.2～§7.4**、AC-09、**§7.5** / **§7.6**） |
| **首节派工 / 文档 vs 所内列** | **[§6](#cc-exec-solve-path) · [§6.4](#cc-problem-to-action) · [§6.1](#cc-remaining-61)** |
| **观测 · 绑定快照** | [`observability/overview` §2.3](observability/overview.md) **派工索引** |
| **Prompt 域** | [`prompt-management/overview`](domains/admin/prompt-management/overview.md) **小团队边界**；[`functions` 文首目录](domains/admin/prompt-management/functions.md)；[`runtime-injection` 维护](domains/admin/prompt-management/runtime-injection.md) |
| **PRS 总入口** | [`prompt-runtime/README`](prompt-runtime/README.md) |
| **PRS · 改什么去哪** | [`prompt-runtime/README` §4 `#prs-where-to-edit`](prompt-runtime/README.md#prs-where-to-edit)（**L1** `prompts/` · **块 5** MNRA · **L0** `skill-specs/`） |
| **MNRA 总入口** | [`market-narrative-runtime/README`](market-narrative-runtime/README.md)、[`scenario-matrix`](market-narrative-runtime/scenario-matrix.md) |
| **Skill Specs（L0）** | [**`requirements-closure.md`**](skill-specs/requirements-closure.md)（**A 闭环 SSOT**）· [`README` §6.1](skill-specs/README.md) · **OP-SKILL** [**§7.5**](#cc-remaining-open-close-path) |
| **需求 / Prompts 索引** | [`requirements/README` §布局与推荐阅读](README.md)；[`prompts/README` §4](prompts/README.md)；[`prompts/library/README` §2](prompts/library/README.md)；[`prompts/intents/README` · 关单派工](prompts/intents/README.md) |
| **Registry CI** | [`.github/workflows/prompt-registry-consistency.yml`](../../.github/workflows/prompt-registry-consistency.yml)（**§7.4 · AC-09q**） |
| **闭环路径总表（DoD）** | **[§7.5](#cc-remaining-open-close-path)** |
| **MR / 工单执行清单** | **[§7.6](#cc-closure-exec-checklist)** |
| **AC-09 一览** | **[§7.4](#cc-ac09-closure-matrix)** |

**宣称「Prompt Runtime 已闭环（B）」** **前** **建议自检**：§7.2 **五行** **在** **所内** **均有** **证据或工单**；**`functions` §1.4** **逐项勾选**；**登记表** **Prompt 行** **与** **§1.2** **同窗** — **仍** **不** **豁免** **Hosted/生产实测**（**若** **宣称 B**）。**AC-09 编号 ↔ 判据** → **[§7.4](#cc-ac09-closure-matrix)**。

---

<a id="cc-ac09-closure-matrix"></a>

### 7.4 AC-09 族闭环检核（内部派工编号）

**用途**：吸收 **「§8 仍未闭环」/ AC-09** 派工表；**分列** **规格仓可声明部分** **与** **须所内 Runtime/会签部分**。**不** **降低** [`contract-closure`](contract-closure.md) **§3 DoD**。

| 编号 | 优先级 | 主题 | **规格仓（本 Git）状态** | **仍须所内 / 产品** |
|:---:|--------|------|---------------------------|----------------------|
| **09a～09e** | **高** | **`runtime-injection` §1** 拼装链（SYSTEM→…→User）、Tool JSON Schema、Few-shot、`variableSchema` + 注入闸 | [`runtime-injection` §1～§7](domains/admin/prompt-management/runtime-injection.md) **已载**；[`functions`](domains/admin/prompt-management/functions.md) **SC-PM 系列** **已载** | **`/pm` 里程碑**；**Runtime 全链实现 MR**；**CC-P1-04 / MR-B**；[`contract-closure` §9](contract-closure.md) **六款** |
| **09f** | **高** | **白名单 / denylist / 发布修订号**（与 Few-shot、占位符同闸） | §2、§2.3、§7.1 **已载**；**`observability`** **修订号字段** **已链** | **Publish/Runtime 闸** **与** **配置中心** **生产对账** |
| **09l** | **中** | **`requires_main_site` / `user_visible_message` 结构化** | [`runtime-injection` §2.4](domains/admin/prompt-management/runtime-injection.md) **键名与语义** | **`design`/OpenAPI** **冻字段**；**编排/错误归一** **禁止静默丢键** |
| **09o** | **中** | **开通欢迎语 §2.1.1** | [`telegram/overview` §2.1.1](domains/agent/telegram/overview.md)；[`keys` §4.2](domains/admin/trading-agent-config/keys.md) | **渠道配置首填**；**SC-TG-ADMIN-05** |
| **Timeline** | **中** | **NLU/LLM 每事件 `promptPackVersion`** | [`observability` §2.3.1](observability/overview.md) **V1=执行级 MUST**；**事件级=可选** | **默认无额外规格债**；**若坚持事件级** → **§2 MUST MR**（**见 §2.3.1**） |
| **09q** | **低** | **Registry ↔ routing 对签脚本进 CI** | **[`.github/workflows/prompt-registry-consistency.yml`](../../.github/workflows/prompt-registry-consistency.yml)** **`pull_request` 全量 + `workflow_dispatch`**；脚本：**[`check_registry_vs_routing_engine.py`](prompts/library/scripts/check_registry_vs_routing_engine.py)**（**他仓若用 `product-doc/...` 路径** **须** **同步脚本或改调用路径**） | **若以 GitHub Actions 为惟一 MR 宿主：** **参见 [`§8.1`/OP-09Q](contract-closure.md#cc-section8-residual-paste)** **登记：** **CI：仅 GHA** **；并按照 [§10 · 步 4](contract-closure.md#cc-section10-five)** **写入 [`§8` 表格顶一行](contract-closure.md)** **；随后在 [§7.6 · 09q](#cc-closure-exec-checklist)** **勾选 N/A** **。** **另有 Jenkins/GitLab：** **`§8.1`** **表第二行。** |

**本 Git** **可宣告收口：** **09q**、**Timeline V1**（默认执行级 MUST，同窗 [`observability` §2.3.1](observability/overview.md)）。若以 **GitHub Actions（GHA）** 为惟一 MR 宿主：[**`contract-closure` §8.1**](contract-closure.md#cc-section8-residual-paste) **登记 **`CI：仅 GHA`** ，并按 [§10 · 步 4](contract-closure.md#cc-section10-five) 写入 **[`§8` 表格](contract-closure.md)** 顶一行；随后在 **[§7.6 · 09q](#cc-closure-exec-checklist)** 勾选 N/A。另有 Jenkins/GitLab：**`§8.1`** 表第二行。**其余 AC-09** 须按 [§7.5](closure-remaining.md#cc-remaining-open-close-path) 走所内 MR/会签。**本节不替代** [§7.4](closure-remaining.md#cc-ac09-closure-matrix) 末列 DoD。

---

<a id="cc-remaining-open-close-path"></a>

### 7.5 未关闭项 · 闭环路径总表（DoD 对齐）

**用途**：把 **仍可能标「未关」** 的项 **收束到「关单判据 + 证据形态 + 主 CC/MR」**，实现 **文档侧闭环**（**可追溯、无孤儿待办**）。**不等价** **替代** **[`contract-closure`](contract-closure.md) §2～§3** **主表 DoD**；**所内 MR 与 §2.1 证据** **仍为** **全闭环硬条件**。

**状态语义（替代笼统「待办」；与 [篇首 · 未完成语义 SSOT](#cc-unfinished-semantics) 同窗）**：

| 状态 | 含义 |
|------|------|
| **规格已闭合** | 本 Git **条文 / OpenAPI / CI（若有）** **已齐**；**未宣称** **对客 B** **亦可到此为止**。 |
| **全闭环（B）** | **§1.2 六款** + **[§9](contract-closure.md#cc-section9-six)** **勾选证据** + **适用 CC** **§2.1 回填** +（**若宣称对客 B**）**Hosted/生产实测 / 会签 MR** **同窗** [`contract-closure` §3.0](contract-closure.md#cc-p1-doc-vs-b)。 |

| ID | 主题 | 规格侧 | 全闭环（B）还须 | 主链（入口） |
|----|------|--------|-----------------|-------------|
| **OP-AvB** | **A≠B** 混读 | §1.1 / §3.0 叙述 + MR **显式标 A 或 B** | **宣称 B** → **Hosted/tag、矩阵、§1.2 六款** | [`contract-closure` §1.1](contract-closure.md#11-两阶段收口需求落地-vs-契约填链) · [§3.0](contract-closure.md#cc-p1-doc-vs-b) |
| **OP-P0** | **P0 闸** 未关 | §1 表 · OpenAPI **`info.version`** 同窗 | **§6.1** **运维/网关/财务/实现** **列证据** | [§1](#cc-remaining-p0) · [§6.1](#cc-remaining-61) · [`contract-closure` §2](contract-closure.md) |
| **OP-P1** | **P1 闸** 未关 | §2 表 · MR-A～E 文档轨 | **法务 / DB 幂 / Prompt 会签 / Webhook 实测** 等 | [§2](#cc-remaining-p1) · [§6.1](#cc-remaining-61) · [`contract-closure` §3](contract-closure.md) |
| **OP-AO3** | **编排 §3** 实现未见证 | `runtime-freeze` §3 / `routing-engine` 已写 | **所内 Agent Runtime**：Planner/恢复 **轨迹或单测** **对拍 §3** | [§7 一键表 · 编排 §3](#cc-remaining-open-items) · [`runtime-freeze` §3](domains/agent/agent-orchestration/runtime-freeze.md) |
| **OP-Xp** | **体验 / UNKNOWN / 主态** | §1.3 抽检叙事 + 域补丁 | **产品走查 / QA** + **§1.2** **同窗** | [`contract-closure` §1.3](contract-closure.md#13-流程体验与卡点可解释抽检--建议与-12-同窗-mr) |
| **OP-OAI** | **`openapi-ai` 宿主 / 制品** | `integrations` · `deployment` · `api` 边界已链 | **实现仓库** **PATH 断言** + **`deployment` §6** **回填** | [§7 一键表 · openapi-ai](#cc-remaining-open-items) · [`integrations/exchange/overview`](integrations/exchange/overview.md) |
| **OP-PR** | **Prompt Runtime 对客 B** | **`runtime-injection` / `functions` / `observability` §2.3 + §7.4 + 09q CI** | **Runtime 全链 MR** + **CC-P1-04 / MR-B** **多模块会签** +（**宣称 B**）**Hosted** + **[§9](contract-closure.md#cc-section9-six)** | **[§7.2～§7.4](#cc-ac09-closure-matrix)** · [`contract-closure` CC-P1-04](contract-closure.md) |
| **OP-09AB** | **AC-09a～09e** 拼装/Schema/Few-shot/变量闸 | §7.4 左列 **已载** | **Runtime 实现 + Publish 闸 + 观测 join** + **`/pm`** **切段** | [§7.4](#cc-ac09-closure-matrix) |
| **OP-09F** | **AC-09f** 白名单/denylist/修订号 | §7.4 左列 **已载** | **Publish/Runtime/配置中心** **生产对账** | [§7.4](#cc-ac09-closure-matrix) |
| **OP-09L** | **AC-09l** `requires_main_site` / `user_visible_message` | **`runtime-injection` §2.4** **已载** | **`design`/OpenAPI** **冻字段** + **编排非空可追溯** | [§7.4](#cc-ac09-closure-matrix) · [`runtime-injection` §2.4](domains/admin/prompt-management/runtime-injection.md) |
| **OP-09O** | **AC-09o** 开通欢迎语 | **telegram / keys** **已载** | **渠道配置首填** + **SC-TG-ADMIN-05** | [§7.4](#cc-ac09-closure-matrix) |
| **OP-TML** | **Timeline** 事件级 `promptPackVersion` | **§2.3.1 执行级 V1** **= 规格默认已闭合** | **仅当产品坚持事件级** → **`observability` §2 MUST MR** + **OpenAPI 同窗** | [`observability` §2.3.1](observability/overview.md) · [§7.4](#cc-ac09-closure-matrix) |
| **OP-09Q** | **AC-09q** registry ↔ routing | **GitHub workflow + 脚本** **已挂** | **另有** Jenkins/GitLab 等非 GitHub CI → **`python3 …`** **编入该流水线**。**若** **仅以 GitHub Actions 为 MR 门禁** → **[`contract-closure` §8](contract-closure.md)** **或** **本轮 MR 登记 **`CI：仅 GHA`** → **OP-09Q 视为闭合** | [§7.4 · 09q](#cc-ac09-closure-matrix) · [`check_registry_vs_routing_engine.py`](prompts/library/scripts/check_registry_vs_routing_engine.py) |
| **OP-MEM** | **Memory · STM/LTM · 四原则 · stale+Resume** | **`memory-runtime` §9～§16**、**§14.6**、**[`memory-runtime-schemas.yaml`](../openapi/components/memory-runtime-schemas.yaml)**（**`MemoryRuntimeConfigSnapshot` · `WarmExecutionEpisode` · `ResumeClassifierResult.episodePickReason`**）、**[`design/memory-runtime-injection` §2.4～§7](../design/memory-runtime-injection.md)**、**[`keys` §2.1](domains/admin/trading-agent-config/keys.md)**、**Telegram §2.7～§2.8 · §2.3.2 · §2.8.6**、**[`clarify-session` v1.6](domains/agent/agent-orchestration/clarify-session.md)**（**§1.1/§2.5**）、**Eval GWT 齐**（**含 `clarify-telegram` §12～§13 · `resume_classifier_multi_episode`**）、**Walkthrough Goal-MEM-STM stale 子束** | **STM**：**§16 硬闸 + clarify-session §2.3 重意图 + §14.6 stale/Resume** **实现** + **所内 CI：`eval.memory.stm_governance_regression`** + **`eval.clarify.*` P0** + **`eval.memory.idle_default_stale`/`resume_classifier_gate`/`resume_classifier_multi_episode`** + **`eval.memory.session_clear_stm`/`budget_trim`**。**LTM（若宣称）**：**`FEATURE_SEMANTIC_NARRATIVE` ON** + **FR-MEM09 写入** + **§2.7 UX** + **§1.2 六款** | [`memory-runtime`](Runtime/memory-runtime.md) · [`clarify-session`](domains/agent/agent-orchestration/clarify-session.md) · [`implementation-alignment` §6/§8](domains/agent/agent-orchestration/implementation-alignment.md) |
| **OP-NAR** | **Market Narrative · 盘感** | **`market-intelligence` §4**、**`common-phrases` §8/§8.7**、**`market-runtime-payload` §3.2.1/§3.4**、**[`market-runtime-schemas.yaml`](../openapi/components/market-runtime-schemas.yaml)**、**[`design/market-narrative-runtime`](../design/market-narrative-runtime.md)**、**[`fewshot-narrative-analysis`](prompts/library/packs/fewshot-narrative-analysis.zh-CN.md)**、**[`registry` §1.2](prompts/library/scenarios/registry.md)**、**Eval 已登记**、**Walkthrough Goal-MKT** | **确定性 `marketPhase` + hints 注入 + Funding/波动 Eval 对签**；**ANALYSIS 包 Few-shot Publish 生效**；**analytics 阈值数值 MR** | [`market-intelligence` §4](domains/agent/exchange-agent/market-intelligence.md) · [`implementation-alignment` §6](domains/agent/agent-orchestration/implementation-alignment.md) |
| **OP-BILL** | **计费 · Phase 2 轨 B（Commerce）** | **OpenAPI** · **`productionRuntime` S2/S5** · **Admin 三项 IA + 商业运营五 Tab**（overview/operations/ledger · MC509 双签在 **计费规则** · 执行详情核销摘要）· **API/BFF mock** · **`scripts/staging-mr-bill-probe.sh`** | **MR-BILL-B1/B2** **staging 宿主** · **Capability 映射真源** · **PSP** · **`contract-closure` §8** | [`commerce-model`](domains/admin/billing-management/commerce-model.md) · [`staging-mr-bill-runbook`](domains/admin/billing-management/staging-mr-bill-runbook.md) · [`closure-internal-sprint`](closure-internal-sprint.md) |
| **OP-SKILL** | **Skill Specs L0 + 登记镜像** | **规格+原型已对齐**：L0 正文、FR/SC、[`runtime-bundle.json`](skill-specs/published/runtime-bundle.json)、[`tool-registry-reconciliation` §0](domains/admin/tool-management/admin-console-tool-registry-reconciliation.md)、Prompt **`skillSpecRef` 门禁** | **所内**：DB/BFF/编排 **`eval.skill.*` 真跑**、**SC-TM-17～18** Publish UI、**CC-P1-03**、矩阵数值 | [`requirements-closure`](skill-specs/requirements-closure.md) · [`PUBLISH.md`](skill-specs/PUBLISH.md) |

**合并读法**：**CC-P0-xx / CC-P1-xx** **逐条** **仍以** **[§1](#cc-remaining-p0) / [§2](#cc-remaining-p1)** **与** **`contract-closure` §2～§3** **为准**；上表 **OP-P0 / OP-P1** **为总出口索引**。**Prompt 专项** **优先跟** **OP-PR + OP-09\*** **行**。

---

<a id="cc-closure-exec-checklist"></a>

### 7.6 闭环执行清单（MR / 工单可复制）

**用途**：把 **[§7.5](#cc-remaining-open-close-path)** **落成 MR/发版窗口内可勾选动作**。**勾选完成** **仍须** **满足** [`contract-closure`](contract-closure.md) **§2～§3 主表 DoD**、**[§9 六款](contract-closure.md#cc-section9-six)**（若宣称对客能力）、**§2.1 证据**（适用时）；**与 [篇首 · 未完成语义 SSOT](#cc-unfinished-semantics) 同窗** — **本条** **不** **替代** **法务/财务/运维门禁**。**小团队** **可优先** **只勾「A」组**；**宣称 B / 生产承诺** **须叠加 B + 相关 C**。

**A · 本仓库（文档 / CI 轨）**

- [x] **概念管线 SSOT**：[`Runtime/domain-model.md`](Runtime/domain-model.md) **§1～§7** · [`pipeline-walkthrough-checklist.md`](Runtime/pipeline-walkthrough-checklist.md) · **Eval** [`pipeline-write-order.md`](evals/pipeline-write-order.md) / **`eval.runtime.pipeline_write_order`**
- [x] **闭环矩阵 · 所外交付包**：[`closure-completion-matrix.md`](closure-completion-matrix.md) · [`closure-internal-sprint.md`](closure-internal-sprint.md) **§1～§3.6**
- [x] **写路径 Demo 时间线序**：`src/admin` **`writePathPipelineOrder`** + **`npm test`**（同窗 skill-contract GHA）
- [x] **OP-09Q / registry↔routing**：**`CI：仅 GHA`** — [`prompt-registry-consistency.yml`](../../.github/workflows/prompt-registry-consistency.yml) + [`contract-closure` §8.1](contract-closure.md#cc-section8-residual-paste)
- [ ] **本轮 MR** **显式标注** **A 或 B**（**与** [**OP-AvB**](#cc-remaining-open-close-path) **一致**，防 A≠B 误读）
- [ ] **OpenAPI `info.version`** **与** [`design/api.md`](../design/api.md) **第三列** **同窗**（**若** **动到** `specs/openapi/*.yaml` **或矩阵**）
- [ ] **`python3 specs/requirements/prompts/library/scripts/check_registry_vs_routing_engine.py`** **exit=0**（**若** **改** [`registry.md`](prompts/library/scenarios/registry.md) **/** [`routing-engine.md`](domains/agent/agent-orchestration/routing-engine.md)）— **09q**
- [ ] （**若动 Market Narrative Few-shot**）**[`fewshot-narrative-analysis.*`](prompts/library/packs/fewshot-narrative-analysis.zh-CN.md) **与** [`narrative-few-shot-specimens`](prompts/analysis/narrative-few-shot-specimens.md) **同窗** — **管理台 Publish 另轨**（**OP-NAR**）
- [ ] **[`prompt-management/functions` §1.4](domains/admin/prompt-management/functions.md)** **核对表** **本轮已对照**（**Prompt 域 MR**）
- [x] **Skill L0 · 需求层 A**：[`skill-specs/requirements-closure.md` §3](skill-specs/requirements-closure.md#3-需求层-dod-a-阶段--可勾选) **全勾**；**`check_skill_contract_complete.py`** + **`skill-contract-consistency.yml`**
- [x] **Skill · 控制台需求**：**FR-TM06**、**SC-TM-13～19**、[`page-specs` · `ai.tool-registry`](admin-console/page-specs.md)
- [x] **Skill · Production Runtime**：[`production-runtime.md`](skill-specs/production-runtime.md)、**SC-OBS11**、**SC-OM-05**、执行详情原型 · [`requirements-closure` §3.7](skill-specs/requirements-closure.md#37-production-runtime-读规范-read_skill_operation_spec--规格--原型)
- [x] **Admin 原型对齐**：**`/ai/tool-registry`** + Prompt **SC-PM-21**（**非** 生产 Publish / **非** Registry API）
- [x] **Memory · 需求层 A**：**`memory-runtime` §14～§16** · **§14.6 stale+Resume** · **`clarify-session`** · **`keys` §2.1** · **OpenAPI `memory-runtime-schemas`** · **Eval P0 登记**（[`evals/README` §5](evals/README.md) · [`idle-default-stale`](evals/idle-default-stale.md) · [`resume-classifier-gate`](evals/resume-classifier-gate.md) · [`design/memory-runtime-injection` §7](../design/memory-runtime-injection.md)）
- [ ] **Memory · 所内 CI P0**：**`eval.memory.stm_governance_regression`** + **`eval.clarify.*` P0** **真跑**（**OP-MEM 右列** — **非本 Git**）

**B · 对客宣称 / CC 收口（所内证据 · 按需勾选）**

- [ ] **[§9 六款](contract-closure.md#cc-section9-six)** **已粘贴进 MR** **并** **逐项勾选**（**宣称「已支持」** **时**）
- [ ] **[§2.1 会签/证据](contract-closure.md#cc-p0-signoff-register)** **行** **或** **工单号** **覆盖本轮涉及之** **CC-P0/P1**（**按** [**§6.1**](#cc-remaining-61) **类别**）
- [ ] **CC-P1-04 / MR-B**：**billing / telegram / observability · Prompt join** **会签轨迹** **或** **已登记排期工单**
- [ ] （**若宣称 B**）**Hosted/生产** **实测摘要** **或** **链接** **已挂载**（**与** [`contract-closure` §8](contract-closure.md) **同窗习惯**）

**C · AC-09 / Prompt Runtime（与 [§7.4](#cc-ac09-closure-matrix) 右列对齐 · 按需勾选）**

- [ ] **09a～09e**：**拼装链 + Publish 闸 + 观测 join（SC-OBS04）** **在所内可演示或附日志样例**
- [ ] **09f**：**白名单/denylist/修订号** **Publish/Runtime/配置** **对账无漂移**
- [ ] **09l**：**OpenAPI/编排** **`requires_main_site` / `user_visible_message`** **可追溯、禁止静默丢键**
- [ ] **09o**：**欢迎语** **渠道可配 + SC-TG-ADMIN-05 路径** **就绪或工单**
- [ ] **Timeline**：**默认执行级 V1** **无追加**；**若产品坚持事件级** → **`observability` §2 MUST MR** **已立项**
- [x] **09q**：**GHA** **[`prompt-registry-consistency.yml`](../../.github/workflows/prompt-registry-consistency.yml)** + 脚本 **exit=0**（**非 GHA 宿主** **另配** — 见 [`contract-closure` §8.1](contract-closure.md#cc-section8-residual-paste)）
- [x] **OP-SKILL · 规格+原型（Publish 叙事）**：bundle + 控制台/Prompt 原型 — [`requirements-closure` §3.6](skill-specs/requirements-closure.md#36-runtime-publish--原型与规格对齐非生产实现)
- [ ] **OP-SKILL · 所内实现（SK-B01～05）**：DB/BFF/编排、**`eval.skill.*` 真跑**、**CC-P1-03**、矩阵数值 — [`requirements-closure` §4](skill-specs/requirements-closure.md#4-b-阶段开放项不阻塞-a-但阻塞全闭环--对客-b) · [`MR-B-BFF-IMPLEMENTATION`](skill-specs/MR-B-BFF-IMPLEMENTATION.md)
- [ ] **OP-AO3 / 管线序**：所内 **§2.1～2.10** 走读勾选 + **`eval.runtime.pipeline_write_order`** staging — [`pipeline-walkthrough-checklist`](Runtime/pipeline-walkthrough-checklist.md) **§2** · **MR 粘贴** **§4**
- [ ] **OP-BILL · MR-BILL-B1**：**S2** **`evaluateCommerceEntitlementS2Gate`** 宿主 + **`GET …/entitlements/balance`** staging ______
- [ ] **OP-BILL · MR-BILL-B2**：**S5** **`executeConsumptionSettlement`** 宿主 + **`POST …/entitlements/debit`** staging（**仅轨 B** · **无** fallback **`/billing/charges`**）______

**OP-BILL · 规格仓 Admin / 探针（A 组 · 不替代 B 组 staging 关单）**

- [x] **Admin IA**：`/billing/overview` · `/billing/operations`（五 Tab）· `/billing/ledger`；遗留 **`/billing/commerce`** → **`operations?tab=rules`** · **`/billing/pricing`** → **overview** — [`admin-console/demo-routing`](admin-console/demo-routing.md)
- [x] **API 客户端 + hooks**：`billingCommerceClient` · `billingLedgerClient` — `VITE_USE_BILLING_COMMERCE_API` / `VITE_USE_BILLING_LEDGER_API` + 失败回退 mock（**无**运营台 **pricing** 页；**MC502** API 可 BFF 对读）
- [x] **Dev BFF mock**：`npm run dev` · internal **balance/debit** · admin **traces/commerce**（含 **pricing** 路径供探针，非 UI）
- [x] **FR-MC509 双签 Demo**：`CommerceCapabilityCatalogEditor` + `BillingDualSignModal` · **If-Match** · **409**（**计费规则** Tab）
- [x] **执行详情核销摘要** + **轨 B 时间线文案**
- [x] **Vitest**：`productionRuntime` S2/S5/host integration · commerce/pricing/ledger mappers
- [x] **走读脚本**：[`scripts/staging-mr-bill-probe.sh`](../../scripts/staging-mr-bill-probe.sh) — 回填 [`closure-staging-evidence-log` §2.4](closure-staging-evidence-log.md)
- [x] **Web 原型**：[`src/Web`](../../src/Web) **`/subaccount/billing`（账单与消耗）** · **`me/commerce` 摘要**（FR-B17 · **SC-WEB-14/15** 演示）
- [x] **BFF Worker 接线说明**：[`bff-worker-wiring.md`](domains/admin/billing-management/bff-worker-wiring.md)
- [ ] **探针在目标环境 exit=0**（粘贴 §2.4 · `ORIGIN=______` · 日期 ______）
- [ ] **UI 截屏**（commerce 双签 / pricing 双签 / ledger API Tag / 执行详情核销卡）______

**读完 §7.5 再勾 §7.6**：**[§7.5](#cc-remaining-open-close-path)**。**所内开工** → **[§7.7 执行冲刺](#cc-internal-sprint-dispatch)**。**`CI：仅 GHA` · Timeline · OP-AvB 等一行登记** → [`contract-closure` §8.1 `#cc-section8-residual-paste`](contract-closure.md#cc-section8-residual-paste)。

---

<a id="cc-internal-sprint-dispatch"></a>

### 7.7 所内执行冲刺（≈2 人 · 3 周）

**SSOT**：[`closure-internal-sprint.md`](closure-internal-sprint.md) — **周计划 §1**、**工单勾选 §2**、**GitHub MR 全文 §3**（**MR-RT-B4** · **SK-B01～B03** · **P0-01 链** [`contract-closure` §3.4](contract-closure.md#cc-p0-mr-github-full)）。

| 周 | 先做 | 关单证据 |
|:--:|------|----------|
| **W1** | **MR-RT-B4** + **SK-B1/B2** | 走读 [`pipeline-walkthrough-checklist` §2](Runtime/pipeline-walkthrough-checklist.md) **≥80%** 勾选 |
| **W2** | **SK-B3** + **Gateway（CC-P1-07）** | **`eval.runtime.pipeline_write_order`** staging |
| **W3** | **CC-P0-01** Hosted/tag · **eval.skill.*** | [`§7.6`](#cc-closure-exec-checklist) **B 组** **OP-AO3 / OP-SKILL** |

**W1 即可启动**：Runtime **可 Mock** `effective` **先对拍管线序**；**勿等** P0 Hosted。

---

**文档版本**：0.2.51 · **维护**：产品 + 收口 owner · **本版**：**OP-BILL · Admin A 组勾选** · **`staging-mr-bill-probe.sh`**。**承** **0.2.50**。
