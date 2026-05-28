# 发版说明（小团队 · 半页纸）

**用途**：与 [`specs/requirements/LITE-MODE.md`](../specs/requirements/LITE-MODE.md) **§3** 对齐；**对外交代**「本版能靠什么」时 **在「已发布版本」下追加新小节**（可复制文末 **模板**）。

**非第二套 FR**：细节仍以 [`specs/requirements/product.md`](../specs/requirements/product.md)、各 **`specs/requirements/domains/`**、**[`specs/design/api.md`](../specs/design/api.md)**、**`specs/openapi/`** 为准。下文 **「基线快照」** 仅反映 **截至本版文档仓** 的共识，**不**代替实现验收。

### 与「文档完整性」评估如何对齐（读法）

- **「完整」所指**：**[`product.md`](../specs/requirements/product.md)** **已定稿（需求阶段）** 所声明的 **范围与非目标** 内，需求叙事、域分层、**`design/api` + OpenAPI** 可索引、与 **`contract-closure`** 所列 **CC** 可派工 — **不** 表示 **`spec.md` Draft** 已等价于 **生产契约冻结**（须 **[`contract-closure` §5.1 gate](../specs/requirements/contract-closure.md#cc-stage4-spec-gate)**）。  
- **与收口表分工**：**[`contract-closure.md`](../specs/requirements/contract-closure.md)** 管 **关单条件与 MR 模板**；**本文「已发布版本」最新一节** 管 **半页纸对外话术**（与 [`LITE-MODE` §3](../specs/requirements/LITE-MODE.md) 同窗）。  
- **分仓与 Hosted**：生产 **Hosted URL / `release-*` tag / 业务服务实现** 若 **不在本 Git 仓库**，**不以** 本文或仓内 YAML **单独充当** **部署或对外签发**；以 **所内运维回填 + 实现 MR + `contract-closure` 勾选证据** 为准。  
- **目录规模**：评估材料中的 **「总文件数」「某目录分卷个数」** 会随 MR 变化；正式报告或对外引用前 **请以当前分支仓库实际清点为准**（同一目录常同时含 **`README` / `overview` 与专题分卷**，**计数口径可能不同**）。

- **关单执行**：**CC-P0/P1** **「本仓可推进 vs 须所内完成」** 见 **[`closure-remaining.md`](../specs/requirements/closure-remaining.md)**（**§0** **为** **`contract-closure` 锚点**；**§7** **为** **剩余开放项一页总表** `#cc-remaining-open-items`；**§7.1** **为** **走读缺口粘贴** `#cc-remaining-gap-paste`；**§7.5** **闭环路径** **`#cc-remaining-open-close-path`**、**§7.6** **MR 执行清单** **`#cc-closure-exec-checklist`**；**不**替代 **`contract-closure` DoD**）。

---

## 已发布版本（从新到旧）

> **`e2e` HTML 版本号**：下列各小节若写明 **`flow/e2e-closed-loop.html` v…**，均为 **该次修订当时的快照**；**当前 HTML 版本与双文件同步约定** 以 **[`flow/README.md`](../flow/README.md)** 为准。

> **排序**：**日期降序**（**同日多条** **自上而下** **为** **登记/合并** **先后**，**不** **表示** **业务优先级**）。

> **计费 / 商业（读法）**：**2026-05-26 及以后** **以** **最新一节「轨 B 权益核销」** **为准**；**2026-05-09 基线** **中** **「账务三线 / Token 扣费」** **为历史快照**，**已标对读**，**不** **再表示 Agent 消耗 S5 主链。

### 2026-05-27 · 澄清 v1.6 · 副文档对齐（**规格补丁 · 无生产 Runtime**）

- **本版承诺（文档）**
  - **[`clarify-session` v1.6](../specs/requirements/domains/agent/agent-orchestration/clarify-session.md)**：**§1.1** 类型 A×stale 优先级 · **§2.5** Normative 去重 · **v0 放弃终局 `cancelled`** · **`cl:*` V1 现货范围声明**。
  - **[`telegram/overview` §2.6.1](../specs/requirements/domains/agent/telegram/overview.md)**：Webhook **`update_id`** 幂等 × **`cl:*`/`cf:*`** 分层。
  - **OpenAPI**：[`MemoryRuntimeConfigSnapshot`](../specs/openapi/components/memory-runtime-schemas.yaml) · **`MemoryResumeClassifiedEventPayload`** · **`ResumeClassifierResult.episodePickReason`**。
  - **Admin/PRD**：[`trading-agent-config/config` §1](../specs/requirements/domains/admin/trading-agent-config/config.md) **Memory/STM Tab** · **PRD 附录 A §5.1** · **[`design/api`](../specs/design/api.md)** 全局配置 STM 键索引。
  - **Eval GWT 补全**：[`clarify-telegram` §12～§13](../specs/requirements/evals/clarify-telegram.md) · [`resume-classifier-multi-episode`](../specs/requirements/evals/resume-classifier-multi-episode.md) · **[`memory-runtime-injection` v0.5](../specs/design/memory-runtime-injection.md)**。
  - **走查/旅程**：**Goal-MEM-STM stale 子束** · **JV-13** 增补。

- **明确不承诺**（同前节 **2026-05-27 · stale+Resume**）：**生产 BFF/Runtime MR** · **所内 CI P0 真跑** · **LTM 默认 OFF**。

---

### 2026-05-27 · 澄清会话与 STM stale+Resume（**规格 + Admin Demo 小样**）

- **本版承诺（文档与仓内产物）**
  - **写路径澄清 SSOT**：[`clarify-session.md`](../specs/requirements/domains/agent/agent-orchestration/clarify-session.md) **v1.5** — **`ClarifySessionSnapshot`**、**`cl:*` 键盘**、**§2.3 每条 inbound 重意图**、**与类型 A 边界**（**`SC-CLARIFY-01～09`**）。
  - **用户可见话术**：[`clarify-user-visible` §0～§7](../specs/requirements/prompts/shared/clarify-user-visible.md) · Prompt 包 **`fragment-clarify-user-visible`**。
  - **记忆治理 · 隔较久回来**：[`memory-runtime` §14.6](../specs/requirements/Runtime/memory-runtime.md) **v1.8** — **默认 `stale_prior_write`**（**不依赖**用户说「继续/新话题」）；**idle/TTL 先达**（**1800s / 900s**）；**Resume 门控** + **`RESUME_CLASSIFIER_MIN_CONFIDENCE=0.75`**；**温索引 **`WarmExecutionEpisode`**。
  - **配置默认**：[`keys` §2.1](../specs/requirements/domains/admin/trading-agent-config/keys.md) · **设计管线** [`memory-runtime-injection` §2.4](../specs/design/memory-runtime-injection.md) **v0.4**。
  - **Telegram**：[`telegram/overview` §2.3～§2.8](../specs/requirements/domains/agent/telegram/overview.md)（**澄清键盘 · idle 非阻塞提示 · `cl:resume`/`cl:new` fallback only**）。
  - **Eval P0 登记**：[`clarify-telegram`](../specs/requirements/evals/clarify-telegram.md)、[`idle-default-stale`](../specs/requirements/evals/idle-default-stale.md)、[`resume-classifier-gate`](../specs/requirements/evals/resume-classifier-gate.md) · **[`roadmap` 横切](./roadmap.md)**。
  - **Admin Demo（非生产）**：`clarifyOrchestrationPipeline` · `clarifyKeyboard` · `telegramInboundFeedback` — [`productionRuntime/README`](../src/admin/src/productionRuntime/README.md)。

- **明确不承诺**
  - **生产 Telegram BFF / Agent Runtime** **须所内 MR** 实现 **§14.6 全序 + §16 四原则硬闸** — **本仓 Demo** **≠** **Hosted 行为**。
  - **LTM/Semantic 默认 OFF** — **禁止** **对客宣称跨会话「已记住你」** **无** **`contract-closure` §1.2** 证据。
  - **P0 eval 真跑** — **所内 CI**（**`eval.memory.stm_governance_regression`** · **`eval.clarify.*`**）— 见 [`closure-remaining` OP-MEM](../specs/requirements/closure-remaining.md#cc-remaining-open-items)。

- **已知负例（须避免）**
  - 澄清 session 锁死、**内部术语外泄**、**无 inline 按钮**、隔较久回来仍复读写澄清 — **规格已冻结对策**；**实现验收** **待** **所内 MR**。

### 2026-05-27 · 计费叙事与原型清扫（**文档 + `src/Web` / `src/admin`**）

- **本版承诺（文档与仓内产物）**  
  - **用户 H5**：**仅** **`/subaccount/billing`（账单与消耗）** · **`me/commerce`**；**已移除** **`me/billing` BFF/Tab/结账轨 A 残留**。  
  - **Admin Demo**：**执行核销** **仅 `ENTITLEMENT_DEBIT`**；**已移除** Token 扣费 adapter、Ledger **轨 A 退款/对读 UI**。  
  - **叙事 SSOT**：[`billing/overview` §0](../specs/requirements/domains/admin/billing-management/overview.md)、[`web-billing-reconciliation` §0](../specs/requirements/domains/web/admin-console-web-billing-reconciliation.md)、[`product/roadmap`](./roadmap.md) **横切 2026-05-27**。  
- **明确不承诺**  
  - **`user/billing-me.yaml` / `internal/billing-token.yaml`**：**OpenAPI 归档（CC-P0-03）** — **量产 BFF/网关 MR**，**非** 本仓 Demo 范围。

### 2026-05-27 · Prompt 治理 IA（**规格 + Admin Demo**）

- **本版承诺（文档与仓内产物）**  
  - **治理模型**：Prompt **四类正文** + **16 运营包**（`pp-system-core` / `pp-runtime-*` / `pp-trading-*` / **`pp-analysis-core`** / `pp-safety-global`）· **六段 Publish 正文** · **`skillSpecRef` = Runtime 技能范围（发布门禁指针）**，**非** Skill 宿主 — [`prompt-management/config` §1.1b](../specs/requirements/domains/admin/prompt-management/config.md)、[`prompts/governance-map`](../specs/requirements/prompts/governance-map.md)、[`admin-console/page-specs`](../specs/requirements/admin-console/page-specs.md)、**SC-PM-21～22**。  
  - **人类导读**：[`end-to-end-guide` §1.2](./end-to-end-guide.md) · [`prompt-governance-checklist`](./prompt-governance-checklist.md)。  
  - **Admin Demo**：Prompt 治理全链 + **执行详情**（Skill Scope · Prompt 追溯 · **Canonical Inspector**）+ **技能登记册适用场景反查** — [`src/admin/README`](../src/admin/README.md)、`executionCanonicalInspector.ts`、`skillScopeForScenario.ts`。

- **明确不承诺**  
  - **BFF 真值 Trace / 审计落库**（`admin.prompt.publish_blocked`）、Canonical Inspector — **所内 API** 待接。

### 2026-05-26 · 计费商业模型 · 轨 B 权益核销（**文档 + 契约骨架 + 小样**）

- **本版承诺（文档与仓内产物）**  
  - **商业 SSOT**：[`commerce-model.md`](../specs/requirements/domains/admin/billing-management/commerce-model.md) **v0.3.1** — **订阅档位 + Capability + 加购包**；**配额用尽即停**；**续用仅升级/买包**；**禁止套餐外按量后付（`FR-B21`）**。  
  - **Agent 消耗结算**：**S2 额度门禁** + **S5 仅 `ENTITLEMENT_DEBIT`（轨 B）**；**`BILLING_SETTLE_POLICY=ENTITLEMENT_ONLY`**（默认）；**不**在 S5 **再扣子账户 Token/USDT（轨 A）**。  
  - **执行 ↔ 计费 join**：[`commerce-model` §5.3](../specs/requirements/domains/admin/billing-management/commerce-model.md) — 每条可计费 **`executionId`** **须可 join** **至多一条成功核销**（**`billingTraceId`、`capabilitySkuId`、核销状态**）；执行详情/时间线 **同窗** [`observability/overview` §2](../specs/requirements/observability/overview.md)。  
  - **消费主路径**：[`consume-and-bill.md`](../specs/requirements/flows/consume-and-bill.md) **S2/S5/S6**、[`billing-management/`](../specs/requirements/domains/admin/billing-management/overview.md) **overview / flow / functions / rules**、[`product.md`](../specs/requirements/product.md) **计费方向节**。  
  - **用户触点**：**主链** **`me/commerce`**（**`/subaccount/billing` · 账单与消耗** · 配额/核销流水 · **纯数字执行 ID** · **FR-B17～B20**）— [`web-billing-reconciliation` §0](../specs/requirements/domains/web/admin-console-web-billing-reconciliation.md)、[`web/agent-billing.md`](../specs/requirements/domains/web/agent-billing.md)、Telegram **Deeplink** [`commerce-deeplink`](../specs/requirements/domains/web/commerce-deeplink.md)。**`me/billing`**：**OpenAPI 归档 only**（**见** **[2026-05-27 · 计费叙事清扫](#2026-05-27--计费叙事与原型清扫文档--srcweb--srcadmin)**）。  
  - **契约登记**：[`design/api.md`](../specs/design/api.md) **登记表分轨**；OpenAPI **[`internal/billing-entitlements.yaml`](../specs/openapi/internal/billing-entitlements.yaml)**（**SC-B20**）、**[`user/commerce-me.yaml`](../specs/openapi/user/commerce-me.yaml)**、**`admin/billing-admin` · `commerce_phase2`**、**[`billing-schemas.yaml`](../specs/openapi/components/billing-schemas.yaml)** Phase 2 扩展。  
  - **观测 / 控制台**：**`billing.entitlement_debit_*`** 主链、**`capabilitySkuId`**；Admin **执行核销追踪**（[`admin-console/page-specs`](../specs/requirements/admin-console/page-specs.md)）。  
  - **实现小样（本仓）**：[`src/admin/src/productionRuntime/`](../src/admin/src/productionRuntime/README.md) — S2/S5 门禁与 adapter 测试（**非生产 Hosted**）。  
  - **产品叙事同窗**：[`roadmap.md`](./roadmap.md) TL;DR、[`overview.md`](./overview.md)、[`flows.md`](./flows.md)、[`journey-validation.md`](./journey-validation.md)、[`user-scenarios.md`](./user-scenarios.md)。

- **明确不承诺 / 仍为 TBD**  
  - **生产闭环**：**所内** **MR-BILL-B1/B2**（S2/S5 宿主接线、账务 HTTP staging、**`contract-closure` §8 轨 B MR**）— 见 [`closure-remaining` §7 · OP-BILL](../specs/requirements/closure-remaining.md#cc-remaining-open-items)、[`closure-internal-sprint` · MR-BILL](../specs/requirements/closure-internal-sprint.md)。  
  - **CC-P0-03（历史 Token 三线 OpenAPI）**：**YAML 归档**；**不** **替代** **权益核销关单**；**本仓 Demo 不实现**；**生产网关/baseUrl 首填** **仍开放**。  
  - **CC-P0-04 / CC-P0-05**：**D-12 收入专户**、**D-5/D-7 观测 join 生产勾选** — **PRD §13 仍 `[ ]`**。  
  - **用户消耗明细 / CSV 导出 PATH**：**`me/commerce` 演进面** **待 implementation MR**（**FR-WEB09 / FR-B20**）；**非** **本文档仓单独冻结**。  
  - **PSP 买包 / 加购包支付链路** — **延后 design MR**（**FR-B18** 到账前 **不得** **展示为已生效**）。  
  - **Admin Demo · 执行详情**：**核销摘要** **对齐 `ENTITLEMENT_DEBIT` / `capabilitySkuId`**（**无** **`chargeStatus` 轨 A 字段**）；**Hosted 真值** **仍待所内 MR**。

- **已知风险或待补**  
  - **双轨读法**：**子账户 USDT** **仍承担交易/理财消耗**（**§7.4.1**）；**与 Agent 消耗配额** **须分开展示**（**不同 `billCode`/文案族**）。  
  - **UNKNOWN / 504**：**写路径未知终局** **下核销策略** **须与** [`consume-and-bill`](../specs/requirements/flows/consume-and-bill.md) **及 Runbook** **同窗**（**billing overview §10.3.1**）。  
  - **Hosted / 实现若在他仓**：**不以** 本仓 YAML + 文档 **单独签发** **「计费生产已收口」**。

- **计费 / 合规**  
  - **对客单元**：**Capability 配额**（**非 Token 后付为主叙事**）；Token **为 Metering/明细维**。  
  - **历史 Token/USDT 流水（OpenAPI）**：**CC-P0-03**；**收入专户** **以 §10.6.1 会签与生产配置为准**（**未关**）。

- **主态边 × 观测**  
  - [`execution-transition-matrix` §8.2](../specs/requirements/Runtime/execution-transition-matrix.md) **→** **`ENTITLEMENT_DEBIT` / SC-B20**；时间线 **不得** **伪造 `charge_success`**（**[`SC-OM-02`](../specs/requirements/domains/admin/observability-management/functions.md)**）。

- **关联**：文档修订 MR · 无 tag 绑定 · **登记** **[`contract-closure` §8](../specs/requirements/contract-closure.md)**（**轨 B 批次 · 待回填行级版本号**）。

---

### 2026-05-25 · 2026-05 规格批次（收口执行 · Skill L0 · MNRA/Memory · Runtime 管线）

> **读法**：本条为 **同日大批文档/契约入库** 的 **半页纸汇总**；**Gateway/Canonical 首登叙事** **亦见** **[2026-05-14 · 架构语言](#2026-05-14--架构语言--与通用-agent-栈对照文档)**。**计费轨 B** **见** **[2026-05-26](#2026-05-26--计费商业模型--轨-b-权益核销文档--契约骨架--小样)**（**非本批次**）。

- **本版承诺（文档与仓内产物 · A 可评审）**  

  **收口 · 派工 · 自检（W1 入口）**  
  - **[`closure-completion-matrix.md`](../specs/requirements/closure-completion-matrix.md)**：主链 **P-01～P-08**、横切 **OP-*** 绿/黄/红；**§0 今日 W1** 动作表。  
  - **[`closure-internal-sprint.md`](../specs/requirements/closure-internal-sprint.md)**：3 周节奏 · **MR-RT-B4 / SK-B1～B5 / MR-GW** 粘贴稿；**[`closure-work-item-templates.md`](../specs/requirements/closure-work-item-templates.md)**、**[`closure-staging-evidence-log.md`](../specs/requirements/closure-staging-evidence-log.md)**。  
  - **[`Runtime/pipeline-walkthrough-checklist.md`](../specs/requirements/Runtime/pipeline-walkthrough-checklist.md)** + **[`Runtime/domain-model.md`](../specs/requirements/Runtime/domain-model.md)** **§1～§7**（Risk · Receipt · Timeline · **spec_read 序**）。  
  - **本仓自检**：**[`scripts/closure-preflight.sh`](../scripts/closure-preflight.sh)**；**[`product/roadmap.md`](./roadmap.md)** **「规格体系快照」L1～L7** 与 **横切主题** 表。  

  **Skill L0 · Publish（需求 A 闭合 · OP-SKILL 绿）**  
  - **[`skill-specs/requirements-closure.md`](../specs/requirements/skill-specs/requirements-closure.md)** **§3 DoD 勾选**；**11** 篇 **`publishRequired`** + **2** 篇改单 **`contract-complete`** · **`skillSpecVersion` `0.2.0-contract`**。  
  - **[`published/runtime-bundle.json`](../specs/requirements/skill-specs/published/runtime-bundle.json)**（**`generatedAt` 2026-05-25**）+ **[`PUBLISH.md`](../specs/requirements/skill-specs/PUBLISH.md) v0.3.0** + **[`MR-B-BFF-IMPLEMENTATION.md`](../specs/requirements/skill-specs/MR-B-BFF-IMPLEMENTATION.md)**（**所内 MR-B1～B5 拆单**）。  
  - **OpenAPI**：[`skill-operation-spec-schemas.yaml`](../specs/openapi/components/skill-operation-spec-schemas.yaml) **`2026-05-25`**；Admin **`/ai/tool-registry`** 原型 + **GHA** **`.github/workflows/skill-contract-consistency.yml`**；**Vitest** **`skillContract` / `mock.timeline.contract`**。  

  **MNRA · 读侧盘感（OP-NAR · 文档 A）**  
  - **总入口**：[`market-narrative-runtime/README.md`](../specs/requirements/market-narrative-runtime/README.md)；**设计面**：[`design/market-narrative-runtime.md`](../specs/design/market-narrative-runtime.md)（**PhaseRules v0 占位**）。  
  - **Facts/Phase SSOT**：[`market-runtime-payload.md`](../specs/requirements/domains/agent/exchange-agent/market-runtime-payload.md)；**流程**：[`read-analyze-and-search-via-agent.md`](../specs/requirements/flows/read-analyze-and-search-via-agent.md) **v0.2.0**（**S4.1 phase 派生**）。  
  - **OpenAPI / Eval**：[`market-runtime-schemas.yaml`](../specs/openapi/components/market-runtime-schemas.yaml)；[`evals/market-narrative.md`](../specs/requirements/evals/market-narrative.md)。  

  **Memory · STM/LTM（OP-MEM · 文档 A）**  
  - **需求 SSOT**：[`Runtime/memory-runtime.md`](../specs/requirements/Runtime/memory-runtime.md)；**注入管线设计**：[`design/memory-runtime-injection.md`](../specs/design/memory-runtime-injection.md)。  
  - **OpenAPI / Eval**：[`memory-runtime-schemas.yaml`](../specs/openapi/components/memory-runtime-schemas.yaml)；[`evals/memory-runtime.md`](../specs/requirements/evals/memory-runtime.md)。  
  - **Telegram UX**：[`telegram/overview` §2.7～§2.8](../specs/requirements/domains/agent/telegram/overview.md)（**跨会话记忆查看/撤销** · **STM 清空本会话**）；[`interaction-flow-standard` §1](../specs/requirements/standards/interaction-flow-standard.md) **互链**。  
  - **（2026-05-27 增补）** **澄清 + stale+Resume** → **[2026-05-27 · 澄清会话与 STM stale+Resume](#2026-05-27--澄清会话与-stm-staleresume规格--admin-demo-小样)**。  

  **写路径管线 · Eval（SC-OBS08/11）**  
  - **[`evals/pipeline-write-order.md`](../specs/requirements/evals/pipeline-write-order.md)** · **`eval.runtime.pipeline_write_order`**（**spec_read → confirmation → write**）；[`evals/skill-contract.md`](../specs/requirements/evals/skill-contract.md) **P0 束扩展**。  

  **Gateway / Canonical（CC-P1-07 · 文档 A · 与本批次同窗登记）**  
  - **[`canonical-trading-model.md`](../specs/design/canonical-trading-model.md)**、**[`ADR-004`](../specs/design/adr/004-intent-centric-execution-and-canonical-trading-model.md)**、[`architecture.md`](../specs/design/architecture.md) **Gateway 插入**、[`trade-assistance` §2.6](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)。  
  - **[`contract-closure` §3 · CC-P1-07](../specs/requirements/contract-closure.md#cc-p1-07)**、**§8 · 0.2.0**；**MR-F（实现 B）** 建议。

- **明确不承诺 / 仍为 TBD**  
  - **CC-P1-07 DoD B**：Execution Gateway + Coobit Adapter **对拍**、Runtime 接线 — **所内工程仓**（**本规格仓无实现**）。  
  - **OP-SKILL 黄**：**SK-B01～B05** 生产 **`read_skill_operation_spec` / Publish 落库 / `eval.skill.*` 真跑**。  
  - **OP-MEM / OP-NAR 黄**：**LTM/Semantic 默认 OFF**；**MNRA 数值阈值** **TBD**（**须 analytics MR + 回测**）；**禁止** **对客宣称「已记住你」** **无** **`contract-closure` §1.2** 证据。  
  - **CC-P0 Hosted / 账务 / 观测**：**仍红/黄** — 见 **[`closure-completion-matrix` §2](../specs/requirements/closure-completion-matrix.md)**（**不** **因本批次** **升格** **生产契约冻结**）。

- **已知风险或待补**  
  - **走读 ≠ 关单**：**§2.1～2.10 勾选** **须** **staging 证据**（**[`closure-staging-evidence-log`](../specs/requirements/closure-staging-evidence-log.md)**）；**W1 完成定义** 见 **闭环矩阵 §0**。  
  - **双轨 HTTP**：**`design/api` 矩阵 + allowlist** **仍** **为 Coobit HTTP 真源**；**Canonical** **至** **映射表填齐** **前** **勿** **弱化为「仅 Skill 直连」**。

- **主态边 × 观测**  
  - **写路径序**：时间线 **须** **`agent.skill.spec_read` 早于 `confirmation.required`**（**[`SC-OBS11`](../specs/requirements/observability/overview.md)** · **走读 §2.4～2.6**）。

- **关联**：文档修订 MR · 无 tag 绑定 · **登记** **[`contract-closure` §8](../specs/requirements/contract-closure.md)**（**2026-05 批次 · 0.2.x / 0.1.x 矩阵行**）。

---

### 2026-05-24 · README 推荐阅读 + `e2e` 鸟瞰同窗 `spec`（文档）

- **[`requirements/README.md`](../specs/requirements/README.md)**：**小团队路径 · 第 4 条** — **[`spec.md`](../specs/requirements/spec.md)** **域段** · **[`domains/agent/exchange-agent/README.md`](../specs/requirements/domains/agent/exchange-agent/README.md)**（openapi-ai · 名录宿主）
- **`flow/e2e-closed-loop.{md,html}`**：文首 **`定位`** 行 **`spec.md`**；**HTML v1.5.6**，footer **Speckit 链**。**`e2e` 篇末** **`1.5.6`**  
- **登记**：[**`contract-closure` §8**](../specs/requirements/contract-closure.md) **0.1.99**。**不承诺**：**网关 **`deployment` §6**。

---

### 2026-05-23 · `spec` 域段落 + Capability README 宿主（文档）

- **[`spec.md`](../specs/requirements/spec.md)**：`exchange-agent` **overview**、`agent-orchestration` **overview**：同窗 **openapi-ai**、**integrations**、`design/api`，**allowlist**。  
- **[`exchange-agent/README`](../specs/requirements/domains/agent/exchange-agent/README.md)**：篇首 **`openapi-ai` pin、`integrations`、`overview`、`allowlist`。**  
- **登记**：[**`contract-closure` §8**](../specs/requirements/contract-closure.md) **0.1.98**。**不承诺**：**网关 **`deployment` §6**。

---

### 2026-05-22 · Capability + agent 索引 + 编排总览同窗（文档）

- **[`exchange-agent/overview`](../specs/requirements/domains/agent/exchange-agent/overview.md)**：篇首 **对上 Coobit 私网 HTTP**：默认 **`openapi-ai`（pin）**；同窗 **矩阵、allowlist、integrations**。**篇末** **`0.4.8`**。  
- **[`domains/agent/README.md`](../specs/requirements/domains/agent/README.md)**：一行 **`openapi-ai`/`integrations`**。  
- **[`agent-orchestration/overview`](../specs/requirements/domains/agent/agent-orchestration/overview.md)**：**篇首** **私网宿主**指向 **`routing-engine`/`runtime-freeze`** **与同窗链**。**篇末 **`1.4.3`**。  
- **[`web/agent-onboarding` §1](../specs/requirements/domains/web/agent-onboarding.md)**：保存链 openapi-ai **句读整理**。**篇末 **`1.4.3`**。  
- **登记**：[**`contract-closure` §8**](../specs/requirements/contract-closure.md) **0.1.97**。**不承诺**：**网关 **`deployment` §6**。

---

### 2026-05-21 · Web 总览 + 编排篇首同窗 · openapi-ai（文档）

- **[`domains/web/overview`](../specs/requirements/domains/web/overview.md)**：**对上 Coobit（配置页保存链）**，默认 **`openapi-ai`（pin）**；同窗 `initialization-flow`、`design/api`、`allowlist`、[`integrations/exchange/overview`](../specs/requirements/integrations/exchange/overview.md)。**篇末** **`1.2.1`**。  
- **[`runtime-freeze.md`](../specs/requirements/domains/agent/agent-orchestration/runtime-freeze.md)**、**[`routing-engine.md`](../specs/requirements/domains/agent/agent-orchestration/routing-engine.md)**：**篇首** **私网 HTTP / 实现对齐**，`openapi-ai` + **`integrations`/矩阵/allowlist**；**routing** **`1.2.8`**，**freeze** **`1.5.3`**。  
- **登记**：[**`contract-closure` §8**](../specs/requirements/contract-closure.md) **0.1.96**。**不承诺**：**网关 **`deployment` §6**。

---

### 2026-05-20 · 现货 OCO/bracket：Agent 本阶段不交付（**文档**）

- **[`specs/requirements/product.md` §非目标](../specs/requirements/product.md)**：`trade.spot.oco` / `trade.spot.bracket` **不须实现** **`call_exchange_write`**；**`FR-T05` / 主站 / 分步入场离场** **为** **唯一下沉**。  
- **邻域同窗**：`trade-assistance` §4、`routing-engine` §2、`trade-via-agent`（S12 · 专节 · 现货限价）、`runtime-freeze` §3.8～§3.9、`confirmation-flow` §1、`telegram/overview` §2.5.2、`integrations/exchange/agent-coobit-api-allowlist` §3、`contract-closure` **CC-P1-01**、**MR-D 分支 C**、`closure-remaining` §2、`prompts/library/scenarios/registry` §2。

---

### 2026-05-20 · Agent 产品线绑定 Web + 权限 + 确认流 · Coobit 宿主同窗（文档）

- **[`domains/web/agent-onboarding` §1](../specs/requirements/domains/web/agent-onboarding.md)**：保存链路 **对上 Coobit**：**默认 **`openapi-ai`（pin）**；同窗 **`initialization-flow`/`design/api`/`allowlist`/`integrations/exchange/overview`**。篇末 **`1.4.2`**。  
- **[`permission-authorization` 篇首](../specs/requirements/domains/agent/onboarding/permission-authorization.md)**：校验/运行时私域 **出站宿主**。**篇末 **`1.3.2`**。  
- **[`confirmation-flow`](../specs/requirements/domains/agent/agent-orchestration/confirmation-flow.md)**：**步骤 4** **HTTP**：**`openapi-ai` + integrations/allowlist**。**篇末 **`1.1.7`**。  
- **登记**：[**`contract-closure` §8**](../specs/requirements/contract-closure.md) **0.1.95**。**不承诺**：**网关 **`deployment` §6**。

---

### 2026-05-19 · 开通绑定 + Runtime 执行步 · Coobit HTTP 同窗（文档）

- **[`flows/activate-trading-agent.md`](../specs/requirements/flows/activate-trading-agent.md)**：**文首表** + **`参与文档`**，`openapi-ai`（pin）、**`design/api` 绑定探测矩阵**、**`allowlist`/`integrations/exchange/overview`** **同窗**。  
- **[`onboarding/overview` §1.1](../specs/requirements/domains/agent/onboarding/overview.md)**、**[`initialization-flow` §1.2](../specs/requirements/domains/agent/onboarding/initialization-flow.md)**：**绑定保存对上 Coobit 探测宿主**。**篇末**：onboarding `1.4.3` / init-flow `1.5.6`。  
- **[`Runtime/execution` §1 步 7](../specs/requirements/Runtime/execution.md)**：**工具调用**对上私网 **`openapi-ai`**。**篇末**：`execution` **`1.0.11`**。  
- **登记**：[**`contract-closure` §8**](../specs/requirements/contract-closure.md) **0.1.94**。**不承诺**：**网关 **`deployment` §6**。

---

### 2026-05-18 · 主流程与鸟瞰图同窗 · Coobit HTTP 宿主索引（文档）

- **`specs/requirements/flows/`**：`trade-via-agent`、`consume-and-bill`、`wealth-via-agent`、`read-analyze-and-search-via-agent`、`automation-alerts`、`README.md` **补** **`openapi-ai`（pin）+ `design/api` + allowlist** **链** **[`integrations/exchange/overview`](../specs/requirements/integrations/exchange/overview.md)**。  
- **`flow/e2e-closed-loop.md`**：**Prompt/Skill** 鸟瞰 **同窗** **`openapi-ai`/allowlist`。  
- **`flow/e2e-closed-loop.html`**：**v1.5.5** · header/footer **同上口径**。  
- **登记**：[**`contract-closure` §8**](../specs/requirements/contract-closure.md) **0.1.93**。  
- **不承诺**：**网关实现 / `deployment` §6** **仍** **所内 MR**。

---

### 2026-05-17 · 宿主对齐补链（人机入口 · 检阅勾选项 · 无业务契约状态变更）

- **读者入口**：[**`product/README`**](README.md) **文档地图**（`overview` ↔ `integrations/exchange`）；**推荐阅读 §10b**（契约 vs 宿主 **同窗**）。  
- **小团队**：[**`LITE-MODE.md`**](../specs/requirements/LITE-MODE.md) **§1 原则**，显式 **`openapi-ai` ≠ 删除 OpenAPI/矩阵/白名单**。  
- **索引**：[**`integrations/README.md`**](../specs/requirements/integrations/README.md) **exchange 行** **「出站默认 openapi-ai」（pin）+ 契约真源**。  
- **CR / 自检**：[**`implementation-alignment` §6**](../specs/requirements/domains/agent/agent-orchestration/implementation-alignment.md) **首勾** pin + allowlist。  
- **登记**：[**`contract-closure` §8**](../specs/requirements/contract-closure.md) **0.1.92**。  
- **不承诺**：**实现网关接线 / `deployment` §6** **仍须** **所内 MR**。

---

### 2026-05-16 · 设计续 · Coobit 官方 openapi-ai 对上 HTTP 宿主（无业务契约状态变更）

- **本版承诺（文档层面）**  
  - **[`design/architecture.md`](../specs/design/architecture.md)**：C4 **交易所适配**、语境 **Coobit** 条、**Agent 运行时数据流** — **默认经 `openapi-ai` 官方包出站**（pin 版本），矩阵与 **白名单不变**。  
  - **[`design/deployment.md`](../specs/design/deployment.md)**：**交易所出站** 单元与 **配置/密钥** — **`openapi-ai` 制品 pin**、密钥 **不经** Skill 静态资产。  
  - **[`design/tool-calling-sequence.md`](../specs/design/tool-calling-sequence.md)**：**§2** **真源表** **补** **Coobit HTTP** 行（**续** **前序** **`requirements/integrations/exchange` + `design/api` 规格**）。  
  - **聚合与横切索引（续）**：**[`spec.md`](../specs/requirements/spec.md)**（主题索引 `integrations`、`design/*` 补链）；[**`Runtime/overview.md`**](../specs/requirements/Runtime/overview.md)、[**`tools/README.md`**](../specs/requirements/tools/README.md)、[**`domains/README.md`**](../specs/requirements/domains/README.md)；[**`closure-remaining.md`**](../specs/requirements/closure-remaining.md) **§3 / §7**；[**`runtime-architecture.md`**](../specs/design/runtime-architecture.md)。  

- **明确不承诺 / 仍为 TBD**  
  - **无**：**不**改变 **`contract-closure` CC** **状态**；**实现 MR / Hosted** **仍** **所内**。  

- **已知风险或待补**  
  - **实现仓库** **须** **将** **运行时网关** **切** **至** **pin 后** **`openapi-ai`** **并** **保留** **白名单断言**；物理 **制品拉取** **见** **`deployment` §6** **回填**。  

- **关联**：文档修订 MR · 无 tag 绑定。

---

### 2026-05-15 · 产品文档 · 人话需求导读（无业务契约变更）

- **本版承诺（文档层面）**  
  - 新增 [`requirements-spec-human.md`](./requirements-spec-human.md)：**须 / 不得 / 边界** 表格式导读，链向 **`product.md`**、**`domains/`**、**`flows`**、**`contract-closure` / §2.1**；**不**新增 FR/SC，冲突以 **`specs`** 为准。  
  - [`product/README.md`](./README.md) **文档地图**与 **建议阅读顺序** 已纳入本篇入口；[`requirements-review.md`](./requirements-review.md) **§1** 增加可选速览 **1b**。  

- **明确不承诺 / 仍为 TBD**  
  - **无**：本条 **仅** 增补人类可读需求导读；**业务收口状态**仍以 **下文「2026-05-09 · 文档 / 设计基线」** **小节** **及** [`contract-closure.md`](../specs/requirements/contract-closure.md) **为准**。  

- **已知风险或待补**  
  - 导读 **须随 `specs` 变更同步修订** §2～§5 链接与措辞（产品例行见 `requirements-spec-human` **§6**）。  

- **关联**：文档修订 · 无 tag 绑定。

---

### 2026-05-14 · 架构语言 · 与通用 Agent 栈对照（**文档**）

- **[`architecture.md`](../specs/design/architecture.md)**：新增 **「与通用 Agent 栈之对照」** — Runtime / Gateway / 意图中心 vs Prompt+Tool-only；**`canonical-trading-model`** 配套链同窗。  
- **导航同窗**：[`product/overview` 硬前提 §6](./overview.md)、[`product/README`](./README.md)、[`spec.md`](../specs/requirements/spec.md)、[`design/adr/README`](../specs/design/adr/README.md)、[`requirements-review` §1（§4c）·§2·§7.5](./requirements-review.md)、[`ADR-004` 引用](../specs/design/adr/004-intent-centric-execution-and-canonical-trading-model.md)。  
- **`flow/e2e-closed-loop.{md,html}`**：文首摘要 **「架构语言」** 行；**HTML v1.5.7**（meta + footer 链）。  
- **索引同窗收口**：[`spec.md`](../specs/requirements/spec.md) **`e2e`→`architecture` §对照**；[`closure-remaining` §7.1](../specs/requirements/closure-remaining.md#cc-remaining-gap-paste)；根 [`README`](../README.md) **`flow/`**；[`roadmap` TL;DR](./roadmap.md)；[`requirements-spec-human` §2](./requirements-spec-human.md)；[`requirements/README` · `flows/` 表 + 推荐阅读 §5](../specs/requirements/README.md)；[`product/flows.md`](./flows.md) **技术鸟瞰**；[`product/README`](./README.md) **文档地图/步骤 5·10**、[`overview`](./overview.md) **鸟瞰段**、[`requirements-review` §1·§2](./requirements-review.md)；[`design/overview`](../specs/design/overview.md)、[`integrations/exchange/overview`](../specs/requirements/integrations/exchange/overview.md)、[`integrations/README`](../specs/requirements/integrations/README.md)、[`specs/README`](../specs/README.md)、[`requirements/domains/README`](../specs/requirements/domains/README.md)；本文 **§「已发布版本」历史 HTML 脚注**。  
- **登记**：[**`contract-closure` §8 · 0.2.11**](../specs/requirements/contract-closure.md)（**§8 表** **`requirements/domains/README`** **+** **上文同窗收口**）。**不承诺**：**Execution Gateway 实现**（DoD B 仍在所内工程仓）。

---

### 2026-05-14 · 文档索引 · 剩余开放项与编排验收互链（无业务契约状态变更）

- **本版承诺（文档层面）**  
  - **[`closure-remaining.md`](../specs/requirements/closure-remaining.md) §7**（`#cc-remaining-open-items`）：**A≠B、P0/P1、`runtime-freeze` §3 实现验收、体验抽检** 总检表 + 本仓可做事与须外部关闭列。  
  - **同文 §7.1**（`#cc-remaining-gap-paste`）：**走读 / A3 缺口** **纪要粘贴表**（**Owner / 日期 / 状态**）。  
  - **[`contract-closure.md`](../specs/requirements/contract-closure.md)** 文首、**[`LITE-MODE`](../specs/requirements/LITE-MODE.md)**、**[`implementation-alignment` §13.1](../specs/requirements/domains/agent/agent-orchestration/implementation-alignment.md)**、**[`Runtime/runtime-truth-source-map` §1](../specs/requirements/Runtime/runtime-truth-source-map.md)**、**[`journey-validation` JV-07](../journey-validation.md)** 互链 §7 / **§3** 抽检口径。  
  - **[`flows/trade-via-agent.md`](../specs/requirements/flows/trade-via-agent.md)** 文首摘要表 **链** **`closure-remaining` §7 / §7.1**；**`runtime-truth-source-map` §1** **补** **§7.1**；**[`state-machine`](../specs/requirements/domains/agent/agent-orchestration/state-machine.md)**、**[`task-scheduler`](../specs/requirements/domains/agent/agent-orchestration/task-scheduler.md)** **篇首** **同窗**；**[`spec.md`](../specs/requirements/spec.md)** **聚合索引** **补** **§7.1**。

- **明确不承诺 / 仍为 TBD**  
  - **无变更**：**业务收口状态**仍以 **「2026-05-09 · 文档 / 设计基线」** **与** **`contract-closure` §2～§3** **为准**；本条 **仅** 降低「漏读开放面」风险。  

- **已知风险或待补**  
  - **读法**：对外发版关门 **仍** 以 **本文最新一节 + `LITE-MODE` §3** 写「承诺/不承诺」；**排期 CC** **从** **§7 总表** **跳进** **`contract-closure` 主表**。  

- **关联**：文档修订 MR · 无 tag 绑定。

---

### 2026-05-14 · 规格仓边界澄清（**文档**）

- **本仓库**（**`product/`** + **`specs/`**）**不** **维护** **Execution Gateway / Adapter** **可执行代码**；**CC-P1-07 DoD B** **仅在** **所内工程/Runtime 仓库** **验收**。  
- **登记**：[`contract-closure` §8](../specs/requirements/contract-closure.md) **0.2.3 起**；设计叙事 **[`canonical-trading-model`](../specs/design/canonical-trading-model.md)** **0.1.4**（去除「本仓 TS 参考包」措辞）。
- **评审入口（续补）**：[`requirements-review` §7.5](../product/requirements-review.md#cc-adr004-review-checklist)、[`LITE-MODE` §1 边界](../specs/requirements/LITE-MODE.md)、[`closure-remaining` §0 · CC-P1-07](../specs/requirements/closure-remaining.md#closure-remaining-quicklinks)。

---

### 2026-05-09 · 文档 / 设计基线（仓库快照，非生产签发）

- **本版承诺（文档与产物层面）**  
  - [`product.md`](../specs/requirements/product.md) **已定稿（需求阶段）**：Coobit **单所**、对客 **仅 Telegram**、**不含 App**（与 [`mobile-app.md`](../specs/requirements/domains/agent/telegram/mobile-app.md) 暂缓一致）。  
  - **规格可索引**：`specs/requirements/` 域分层、[`spec.md`](../specs/requirements/spec.md) 聚合、**OpenAPI** 仓库内 YAML + [`OWNERS.md`](../specs/openapi/OWNERS.md) **具名**。  
  - **接口与矩阵**：[`design/api.md`](../specs/design/api.md) **A 阶段**路径示意 + **部分**矩阵行已与 `coobit-*.yaml` **同窗**；**延期格** **已** **书面标注**（见 `contract-closure` **CC-P0-02**）。  
  - **运营后台 Demo**：[`src/admin/README.md`](../src/admin/README.md) **非生产**、**无真实 API**，IA 与 [`demo-routing.md`](../specs/requirements/admin-console/demo-routing.md) 对齐。  
  - **需求补充（本次修订）**：[`Runtime/sessions.md`](../specs/requirements/Runtime/sessions.md)、[`locking.md`](../specs/requirements/Runtime/locking.md)、[`persistence.md`](../specs/requirements/Runtime/persistence.md)、[`event-storage.md`](../specs/requirements/Runtime/event-storage.md) **已**由「占位」扩展为 **可评审的行为与验收下限**（**实现/存储/锁选型**仍以 **ADR** 为准）；[`design/sub-account-isolation.md`](../specs/design/sub-account-isolation.md)、[`tool-calling-sequence.md`](../specs/design/tool-calling-sequence.md) **已**充实为 **设计切片索引**（**契约真源**仍 **`api.md` + OpenAPI**）。
  - **关单执行索引**：[`closure-remaining.md`](../specs/requirements/closure-remaining.md) **（P0/P1 · 本仓 vs 所内分工；不替代 DoD）**。

- **明确不承诺 / 仍为 TBD（与收口表一致；摘要以避免话术越界）**  
  - **子账户矩阵**：币币改单、杠杆借还、现货条件单、理财细分、**WS/listenKey** 等 **仍为延期或待生产/OpenAPI 终裁** — 详情见 [`design/api.md`](../specs/design/api.md) **矩阵与** **`contract-closure` CC-P0-02**。  
  - **账务（历史基线 · 已被 2026-05-26 小节 supersede 计费主链）**：**Token 三线 OpenAPI**（`me/billing/*` 等）**+ CC-P0-03** — **归档 only**；**Agent 消耗** **见** **[2026-05-26 · 权益核销](#2026-05-26--计费商业模型--轨-b-权益核销文档--契约骨架--小样)** 与 **[2026-05-27 · 叙事清扫](#2026-05-27--计费叙事与原型清扫文档--srcweb--srcadmin)**。  
  - **财务与观测关单**：`BILLING_AGENT_REVENUE_ACCOUNT_REF`（**D-12 / CC-P0-04**）、**D-5/D-7** 与 **`SC-OBS03`**（**CC-P0-05**）— **PRD §13 仍为 `[ ]`**，**禁止**无证据预勾。  
  - **OCO/bracket**：矩阵 PATH **未冻结** — **CC-P1-01**。  
  - **C 类外网工具**：Schema/ADR 已备；**生产启用写闸**（`legalReviewTicketId` 等）以 **实现 MR** 为准 — **CC-P1-02**。  
  - **工具/技能 SSOT 镜像与 Enable**：**CC-P1-03** / **MR-E**；**PRD `SC-MCV1-05`** 项 **仍为 `[ ]`**。  
  - **Prompt 管理**：域 **「评审中（V1）」**，**CC-P1-04** **全流程 DoD 未宣称已关** — 见 [`prompt-management/overview.md`](../specs/requirements/domains/admin/prompt-management/overview.md)。  
  - **控制台 Telegram Bot/Webhook 生产实测**：**CC-P1-06** **与** **文档已 `[x]` 子集** **区分**（见 `contract-closure` **§3.0**）。  
  - **聚合 `spec.md` Status**：仍为 **Draft**；**「生产契约已冻结」** **须** **`contract-closure` §5.1** **gate**。  

- **已知风险或待补**  
  - **叙事与矩阵**：对用户承诺 **自动闭环** 前 **必须** **对照** [`design/api.md`](../specs/design/api.md) **该行是否已冻结或已书面延期**。  
  - **`design/runtime-architecture.md`**：组件级图 **仍须** 与 `architecture` / `Runtime` **充实对签**（见 [`spec.md`](../specs/requirements/spec.md) 设计索引）。  

- **计费 / 合规**  
  - **计费（历史快照）**：**本小节撰写时** 叙事为 Token 按量子账户 USDT；**现行 Agent 消耗主链** **以** **[2026-05-26 · 轨 B 权益核销](#2026-05-26--计费商业模型--轨-b-权益核销文档--契约骨架--小样)** **为准**。  
  - **收入专户** **以 §10.6.1 会签与生产配置为准**。  
  - **外网工具**：**ADR-003**、**`enabledOperational`** **+** **`legalReviewTicketId`**（生产启用 C 类）— 实现须与 OpenAPI **同窗**。  

- **关联**：仓库 **文档修订**；业务后端若 **不在本仓**，不以本文为 **部署签发**。

---

### 模板 · `YYYY-MM-DD` · `<tag 或 MR 摘要>`

- **本版承诺能力**：  
  - …
- **明确不承诺 / 仍为 TBD**：  
  - …
- **已知风险或待补**：  
  - …
- **计费 / 合规（若触及）**：  
  - …
- **关联**：tag `…` · MR …（可选）
