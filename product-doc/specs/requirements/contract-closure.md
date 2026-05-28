# 契约收口与闭环（Gap → Freeze → 可对签）

**定位**：本条为 **FEATURE_DIR** 内 **「何时算对外承诺可闭环」** 的 **操作索引**：把 **`design/api.md` 矩阵 TBD**、**登记表空白**、**技能/工具登记**与 **验收/观测**串成可追溯闭环。**不替代**任一域正文；细节仍以各 `domains/<业务域>/*.md`、`flows/*.md`、`design/*.md` 为准。

**产品方向 SSOT**：[`product.md`](product.md)。

**小团队模式（≈1 需求 + 1 开发）**：**日常** **不** 必按本条 **§2～§5.2** 逐项派工；请 **优先** **[`LITE-MODE.md`](LITE-MODE.md)**（三件事 + MR 常规四块 + 条件第五块 + `product/release-notes.md` 发版关门）。**本条全文保留**：**扩编**、**对外宣称生产契约冻结**、**法务/审计/多方验收** 时 **再启用** 本节及以下 §2～§10。

**编排域 · 对客「已支持」三闸（口语化速查；不替代 §1.2 六款）**：[`domains/agent/agent-orchestration/implementation-alignment.md`](domains/agent/agent-orchestration/implementation-alignment.md) **§13.1** — **闸 1** **在** **寄存器 / §8** **之外** **还须** **`runtime-freeze` §3** **最小编排** **可对签**（**详** **§13.1 表**、**§1.2 款 4**）** — **与** **[`LITE-MODE`](LITE-MODE.md) §2、[`evals/scenarios.md`](evals/scenarios.md)** **同窗 MR/发版时** **抽检**。

**剩余关单「谁在仓库 vs 谁在所内」** **速查**（**不**替代本条表格 DoD）：**[`closure-remaining.md`](closure-remaining.md)** · **[§0 速链](closure-remaining.md#closure-remaining-quicklinks)** · **[PRS 改什么去哪](prompt-runtime/README.md#prs-where-to-edit)** **；** **问题→首节动作（工单/MR 可复制）** → **[§6.4](closure-remaining.md#cc-problem-to-action)** · **`§6`** **执行视图** **[`closure-remaining` §6](closure-remaining.md#cc-exec-solve-path)** · **仅靠文档做不到的列** **[§6.1](closure-remaining.md#cc-remaining-61)**；**开放项一页总表** → **[§7](closure-remaining.md#cc-remaining-open-items)** · **走读缺口粘贴** **[§7.1](closure-remaining.md#cc-remaining-gap-paste)** · **未关闭项闭环路径** **[§7.5](closure-remaining.md#cc-remaining-open-close-path)** · **MR 闭环执行清单** **[§7.6](closure-remaining.md#cc-closure-exec-checklist)** · **Prompt/Runtime §7.2～§7.4（派工 · AC-09）** **[§7.2～§7.4](closure-remaining.md#cc-ac09-closure-matrix)** · **闭环互引** **[§7.3](closure-remaining.md#cc-prompt-runtime-closure-loop)**。

**用户触点分界（复盘必读 · 与 [`product.md`](product.md) 同窗）**：**用户账单（流水、`billCode`、`me/billing`、月度汇总）产品与账务均在交易所内部**；[`domains/web/agent-billing.md`](domains/web/agent-billing.md) **只冻结交易所主站/H5 壳内 UX**。**Agent 绑定 onboarding** **由 Agent 项目（产品线 Web）承载**：用户 **不须访问交易所主站** 配置 Key；**`POST .../bindings/trading-api`** **服务端经交易所 API** 校验（同窗 **`initialization-flow` §1.2**）。**勿将 CC-P0-03「账务三线 OpenAPI」误读为「账单 UI 迁出交易所」** — 三线仍为所内契约；分界见 **`product.md`**。

**未完成语义（别把「文档推送」当关单）**：**条文齐 / §7.6 勾选** **不** **等价** **于** **CC DoD 已满** **或** **对客生产闭环**；三类「未完」 **[`closure-remaining` 统一口径](closure-remaining.md#cc-unfinished-semantics)** **与 §1.1～§1.2、§7.5 同窗**。

---

## 1. 闭环定义（收口即「可承诺」）

### 1.1 两阶段收口：需求落地 vs 契约填链

历史上 **`design/api.md`** 部分段落标为「占位」。本仓库**区分**下列两阶段，避免「只有登记表 TBD」被误读为「需求未写」：

| 阶段 | 含义 | 完成判据（文档侧） |
|------|------|-------------------|
| **A · 需求路径与能力面** | 各模块 **PATH 示意**、**运营/账务/内部扣减** 专节、**子账户 endpoint 矩阵**、与 FR/域正文 **对齐**，并对 **仍不可得之公档 PATH** 写入 **书面延期**（与 **§2 · CC-P0-02** 一致） | **`design/api.md` 正文**可独立作为 **需求下限 / 验收 Then** 追溯；**不依赖** Swagger 已上架 |
| **B · 契约填链** | **所内 OpenAPI 登记表** 每行 **可访问 Spec**（URL 或仓库内 `openapi.yaml` / tag）+ **Owner**，且 **矩阵 PATH** 已 **冻结为真实 path** 或 **延期备注与实现一致** | 下文 **§1 主条** 六款 **全开**；**§2 · CC-P0-01～CC-P0-03** 可按 DoD **勾选关闭** |

**原则**：**A** 可支撑 **BFF 契约先行 / 控制台 UI 占位**（与 **`management-console-v1-prd`** 模块一等叙事一致）；**对用户承诺「该能力已在生产可用」** 仍须 **B**。**禁止**「实现已上线但矩阵格长期 **无说明之 TBD**」— 无 Spec 时 **须** 保留 **书面延期 + 备注** 或 **在 MR/登记表登记 Owner 缺省原因**（见 **§7 模板**）。

### 1.2 可对签必要条件（六款齐备）

在 **不向用户虚构能力** 的前提下，**单行能力**具备 **产品可承诺闭环**，当且仅当同时满足：

**归档口径（2026-05-09 · CC-P0-01 · P0 文档轨批次）**：**六款** **逐项** **关闭** **时** **须在 MR/工单** **附** **可点链接**（**域 §、`design/api` 行、OpenAPI 路径**）；**登记表** **`info.version`（日期）** **须** **与** **同窗 spec 文件** **一致**（**本批次** **19 根 spec + `billing-schemas` 已同窗 `2026-05-09`** **与** **登记表第三列**）；**对外 Hosted** **与** **仓库 `release-*` tag** **终裁** **见** [`openapi/README.md`](../openapi/README.md)。

1. **`design/api.md`**：**所内 OpenAPI 登记表** 对应行 **可访问 spec**（URL / `openapi.yaml` 提交或 tag）；**endpoint 矩阵** 中 **本条 PATH 非 `TBD`** **或** 有 **书面延期**与 **矩阵备注**对齐（禁止「已实现但表仍为 TBD」长期并存）。
2. **`trade-assistance.md`**：§8 **A 写** 已 **`FR-TS07` 单行登记**（含 `skillSpecVersion` 初值）；§8 **B/C** 若有工具暴露，**注册表已有稳定 `toolId`**（与 [`observability.md`](observability/overview.md) **§2.1 B/C、`SC-OBS01`** **可对签**）。
3. **`exchange-agent` 分卷（[`overview.md`](domains/agent/exchange-agent/overview.md)、[`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md)、[`overview-legacy-migration.md`](domains/agent/exchange-agent/overview-legacy-migration.md)）**：**门禁/拒答语义**与本能力一致（典型 **`FR-T05`**）；**旧 §10.x** 见 **`overview-legacy-migration`** **§2**；若涉 **卡片**，[`domains/agent/telegram/overview.md`](domains/agent/telegram/overview.md) **§2.5 · 类型 A（§2.5.x 字段下限）** **及** **总则 §2～§2.6** **已对齐** **`design/api` 不写超边界**；**永续/条件单 Telegram 验收** **另见** **同文 §5 **`SC-CH-TG-FUT-01～03`** **与** **[`design/api.md`](../design/api.md)** **「Telegram Bot API」专节 / 子账户矩阵备注**。
4. **编排**（若有 **`scenarioId`**）：[`domains/agent/agent-orchestration/routing-engine.md`](domains/agent/agent-orchestration/routing-engine.md) **寄存器** 与 [`runtime-freeze.md`](domains/agent/agent-orchestration/runtime-freeze.md) **§1～§2**（**`orchestrationVersion` / DAG**）**上文** **无冲突**；**已登记写键** **须** **与** **同文** **§3.1～§3.11** **最小编排表** **同窗**（**依赖 / 并行 / 失败出口** **下限**；**映射** **见** **`routing-engine` 文首** **「写路径 · 编排下限对签」**）；**写路径**遵守 **ADR-001**：**类型 A → Coobit 写**（见 **`design/adr/001-telegram-confirm-before-coobit-write.md`**）。
5. **自动化/Pull**：[`flows/automation-alerts.md`](flows/automation-alerts.md) **`taskId`/触发器** 与 **`trade-assistance`** **§8.3～§8.5**、[`domains/agent/agent-orchestration/state-machine.md`](domains/agent/agent-orchestration/state-machine.md) **`taskId` 生命周期** **对签**；**只读 Pull** **须有矩阵或公开 PATH 依据**（[`intents.md`](domains/agent/exchange-agent/intents.md)；槽位映射 [`overview-legacy-migration.md`](domains/agent/exchange-agent/overview-legacy-migration.md) **§2**）；[`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **`FR-T02`**。
6. **若**本条能力 **依赖私有 WS 刷新订单/余额视图** **且** **对外承诺 REST 兜底闭合**：[`Runtime/reconciliation.md`](Runtime/reconciliation.md) **§1 矩阵** **须与** **[`../design/api.md`](../design/api.md)** **「REST ↔ WebSocket 对账」专节** **及** **endpoint 矩阵** **同窗登记 PATH**；[`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **§2.5** **须可读链出**；观测 **须可对签 **`exchangeViewSource`**（[`observability/overview.md`](observability/overview.md) **§2 · §2.2 · `SC-OBS06`**）。

**加码（主态 × 观测 · 与上表同窗）**：若本条能力 **改动或依赖** **`executionId` 主态递进**（**写路径** **或** **编排宿主归并主态**），[`observability/overview.md`](observability/overview.md) **§2.4** **须** **与** **[`Runtime/execution-transition-matrix.md`](Runtime/execution-transition-matrix.md) **§2.2** **可对签**；**B 阶段 / 关单** **建议** **附** **`SC-OBS08`** **抽检链接**（**同窗** **`admin/observability` · `FR-MC801`**）。

**与 [`implementation-alignment` §13](domains/agent/agent-orchestration/implementation-alignment.md) 的分工**：**§1.2** **为** **单行能力** **逐款** **权威条文**（审计/关单 **以此为 SSOT**）；**§13** **为** **编排 + MR/发版** **可用的三闸摘要**（**闸 1**：**寄存器 + §8 + `runtime-freeze` §3** **（** **详** **§13.1** **）**；**闸 2**：**矩阵**；**闸 3**：**六款或 `release-notes` 等价**）— **两项须同窗**，**不得以 §13 替代 §9 勾选**。

**不满足 1**：需求仍可有「意图」，**实现**侧须 **`FR-T05` 透明拒答 / 主站**，与 **`trade-assistance` §8.5**、**[`product/overview.md`](../../product/overview.md)** 叙事一致。

### 1.3 流程体验与卡点可解释（抽检 · 建议与 §1.2 同窗 MR）

**用途**：**六款** **齐备** **仍** **可能** **出现** **「用户不知卡在哪」** **或** **504 冒充成交** — **下列** **为** **体验下限** **抽检**（**不** **替代** **任一 SC 正文**）。

| **须能展示证据** | **索引** |
|------------------|----------|
| **用户侧** **阶段叙事** **与** **`executionId` 主态 / 子态** **一致** | [`telegram/overview.md`](domains/agent/telegram/overview.md) **§3.1**；[`trade-via-agent.md`](flows/trade-via-agent.md) **S5.1.1** |
| **UNKNOWN** **话术** **符合** **非成交断言** | [`Runtime/unknown-state.md`](Runtime/unknown-state.md) **用户可见副本下限**；**`eval.obs.504_unknown_write`** |
| **类型 A** **与** **实际提交** **字段级** **可对账**（**或** **同窗单测**） | [`confirmation-flow.md`](domains/agent/agent-orchestration/confirmation-flow.md)；[`product/journey-validation.md`](../../product/journey-validation.md) **JV-12** |
| **槽位歧义** **走** **澄清** **非** **静默落写** | [`trade-via-agent.md`](flows/trade-via-agent.md) **S6**；**`eval.trade.slot_quote_base_clarify`** |

**勾选宿主**：[`Runtime/runtime-consistency.md`](Runtime/runtime-consistency.md) **§7**；**编排抽检** **仍** **[`implementation-alignment.md`](domains/agent/agent-orchestration/implementation-alignment.md) §6**。

---


## 2. P0 · 系统性阻塞（收口前不向用户承诺「已支持」）

| ID | 缺口 | 权威文档锚点 | 收口条件（DoD） |
|----|------|----------------|----------------|
| **CC-P0-01** | 所内 OpenAPI **登记表全行业 TBD** | [`../design/api.md`](../design/api.md) 「所内 OpenAPI / 契约登记」表 · [`specs/openapi/`](../openapi/README.md) | **每行**：Spec 可访问 + Owner + **与矩阵同 PR（或可合并窗口内）替换矩阵 `TBD`**。**解读**：**A 阶段（§1.1）** **登记表第 2～4 列** **可** **沿用** **`design/api`「填链占位」** **之 `TBD` 模板**；**本仓库** **亦可** **以** **`specs/openapi/*.yaml`（MR 可审）** **满足「可访问 Spec」直至 Hosted Swagger 上架**。**闭环 §1.2** 仍须 **矩阵/实现/Hosted** **终裁对签**。**（2026-05-12·文档进展）** **[`OWNERS.md`](../openapi/OWNERS.md)** **行级主** **已具名** **Jesson@chainup.com**（**备** **「同主」**）；**根 spec** **`info.contact.email`** **已同窗** — **`info.version`（日期）** **须** **与** **登记表第三列 + 同窗 YAML** **一致**；**Hosted URL** **与** **`release-*` tag** **终裁** **见** [`openapi/README.md`](../openapi/README.md) **「Hosted」** — **不豁免** **§1.2** **六款** **逐项 MR** **归档** **与** **矩阵 PATH** **生产一致性**。**（2026-05-09·P0 文档轨批次）** **19 根业务 spec**、**`components/*.yaml` 全量** **与** **`billing-schemas.yaml`** **`info.version` 已同窗至 `2026-05-09`** **与** **登记表第三列**；**`openapi/README` Hosted 段** **已载** **(a)(b)(c) 与本文档轨索引** |
| **CC-P0-02** | 子账户 **endpoint 矩阵** 仍 **`TBD` 或占位 PATH**（现货改单、杠杆借还、现货条件单、理财细分、`WebSocket` 等） | [`../design/api.md`](../design/api.md) 「子账户 scope · endpoint 矩阵」「待补充」 | **逐格**：冻结 PATH **或** **书面延期 + 矩阵备注**；**须递增** **`design/api.md` 文档版本脚注**并于 **本节 §4** **登记解冻影响面**。**（本版）** 矩阵已为 **币币改单 / 杠杆借还 / 理财细分 / 现货条件单** 补 **书面延期（CC-P0-02）** — **满足 A 阶段** 文档要求；**B 阶段** 仍须 **所内 PATH 冻结或替换备注**。**（2026-05-12·文档）** **非延期** **矩阵行** **已** **与** **`specs/openapi/exchange/coobit-*.yaml`** **`paths`** **键** **同窗** **`info.version` 2026-05-09** — **不豁免** **延期行** **与** **WS/WebSocket 专节** **的** **实现/OpenAPI** **终裁**。**（2026-05-09·P0 文档轨批次）** **`design/api`** **矩阵节后** **已增** **WebSocket / listenKey** **与** **[`stream/user-private-ws.yaml`](../openapi/stream/user-private-ws.yaml)** **登记表同窗及 §1.2 第 6 款口径** |
| **CC-P0-03** | **账务三线 OpenAPI 骨架** **已在仓库**（**`user/billing-me`、`internal/billing-token`、`admin/billing-admin`**，同窗 **`billing-schemas`**）；**缺口** **=** **`design/api` 登记表占位符 → 生产锚点**（**Hosted/tag/host**）、**`shadow→enforce` Runbook**、**矩阵与实现终裁** — **非** **「未写 spec」** | [`../design/api.md`](../design/api.md) **「模块五」「用户侧 Billing API」「内部 · Token 账务扣减 API」「运营侧 Billing API（`admin/billing/*`）」「账务 · Token 扣费」登记表行** · [`billing-management/functions.md`](domains/admin/billing-management/functions.md) **§2·§3·M1** · [`billing-management/rules.md`](domains/admin/billing-management/rules.md) **流水形态** · [`billing-schemas.yaml`](../openapi/components/billing-schemas.yaml) | 所内 **真实 path + OpenAPI**（**可**拆 **用户 / 运营 / 内部扣减 / 聚合 BFF** 多 spec，**字段语义须同窗**）**替换示意表**；与 [`billing.md`](domains/admin/billing-management/overview.md) **§7～§9**、**`FR-B11`～`FR-B16`**、**`SC-B13`**、**`SC-B14`/`SC-B15`** 及 **`FR-MC501～508`**（费率、流水、导出、退款、月度 rollup、对账）**同窗对签**。**解读**：**`design/api` 三表** 已载 **PATH 示意（A）**。**本仓库** **`specs/openapi`** **已挂** **账务三线** **`$ref` 同窗骨架**（**B 文档子集**）。**（2026-05-12·文档）** **`OWNERS.md` + 根 spec `contact`** **已与** **§8** **对签**；**`billing.md` §12** **已索引** **D-5/D-12 同窗字段**；**§12.1** **已列** **三线** **`paths`** **键** **与** **OpenAPI** **同窗** — **生产/Hosted** **仍须** **终裁 schema + host/网关** **MR** **与** **实现** **对签**。**（2026-05-09·P0 文档轨批次）** **`billing.md` §12.1** **已增** **生产 baseUrl（scheme + host）登记模板** **（关闭全流程 DoD 时首填）** |
| **CC-P0-04** | **生产计费** **`BILLING_AGENT_REVENUE_ACCOUNT_REF` 模板未落地** | [`management-console-v1-prd.md`](domains/admin/management-console-v1-prd.md) **附录 A · §11 `D-12`** · [`billing-management/overview.md` §10.6.1](domains/admin/billing-management/overview.md) | Coobit/财务 **格式冻结**并完成 **配置项首填 + 审计**。**（2026-05-12·文档）** **§10.6.1** **已载** **V1 值格式范式 A/B** **与** **首填检查单** — **不替代** **财务书面会签** **与** **生产首填**。**（2026-05-09·P0 文档轨批次）** **§10.6.1** **已增** **财务会签工单号 / 会签日期** **检查项**（**关闭 DoD 时** **必填链**）。**（2026-05-10）** **PRD §13** **已增** **`D-12`/`CC-P0-04`** **`[ ]`** **（与 `D-5`/`D-7` 同发布纪律）**。**关单证据登记** **见** **[§2.1](#cc-p0-signoff-register)** |
| **CC-P0-05** | **`config` 附录 A §11 `D-5`、`D-7`** **叙事分散** | [`management-console-v1-prd.md`](domains/admin/management-console-v1-prd.md) §11、[`billing.md`](domains/admin/billing-management/overview.md) §10.3 · **§10.3.1** | **文档**：**§11** **已锚** **`billing` §10.3** **与** **`observability`**；**§10.3.1** **已载** **D-5/D-7** **实现/观测 MR 检查单**（**2026-05-12**）。**仍须**：**实现** **按** **§10.3.1** **逐项勾选** **+** **`SC-OBS03`** **等** **同窗** **关闭** **未知终局耦合** **争议**；**联动** **[§13](domains/admin/management-console-v1-prd.md)** **`D-5`/`D-7`** **`[ ]` 项**。**（2026-05-09·P0 文档轨批次）** **`billing` §10.3.1** **已注** **PRD §13 `D-5`/`D-7`** **仅于** **实现 MR** **逐项勾选后** **由 `[ ]` 改 `[x]`**（**禁止** **文档超前勾选**）。**关单证据登记** **见** **[§2.1](#cc-p0-signoff-register)** |

---

<a id="cc-p0-signoff-register"></a>

### 2.1 P0 会签与证据登记（**CC-P0-04 · CC-P0-05**）

**用途**：**财务 / 工程** **合并关单 MR** **时** **集中回填** **可点工单号、MR、`executionId` 样例、审计 id**，与 [`billing-management/overview.md`](domains/admin/billing-management/overview.md) **§10.6.1**、**§10.3.1** **检查单** **同窗**。**[`management-console-v1-prd.md`](domains/admin/management-console-v1-prd.md) §13** **`D-12` 与** **`D-5`/`D-7`** **自 `[ ]` 改 `[x]`** **仅允许** **在下表对应行已填证据且与本 MR/工单互链一致之后** — **禁止** **仅改 PRD** **或** **无证据预勾选**。

| CC | 域检查单 | 关单证据（**于合并 MR 填入**） |
|----|-----------|--------------------------------|
| **CC-P0-04** | [`billing` §10.6.1](domains/admin/billing-management/overview.md) | **财务工单号**：（所内） · **会签日期**：（`YYYY-MM-DD`） · **范式选用**：A / B / 同窗 JSON（删未选项） · **配置首填 MR**：（URL 或 `#`） · **审计 id**：（所内台账） |
| **CC-P0-05** | [`billing` §10.3.1](domains/admin/billing-management/overview.md) | **实现 MR**：（URL 或 `#`） · **`executionId` 协查样例**：（片段或脱敏链接） · **`SC-OBS03` / UNKNOWN 计费策略**：（Runbook 或设计链接） |

**闭合后（建议同一 MR）**：**(1)** **PRD §13** **勾选** **已达标的** **`D-12` / `D-5`/`D-7`**；**(2)** **§8** **顶行追加** **一行**；**(3)** **递增** **本文** **文末「文档版本」**。

---

## 3. P1 · 能力/治理收口（并行推进）

| ID | 缺口 | 权威文档锚点 | 收口条件（DoD） |
|----|------|----------------|----------------|
| **CC-P1-01** | **OCO/bracket** **`skillId`** **登记** | [`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **§8.2 · §4** | **文档**：**已登记** **`skill.spot.oco` / `skill.spot.bracket`**；**`design/api` 子账户矩阵** **已载** **书面延期行**（2026-05-09）。**`routing-engine` §2** **`trade.spot.oco` / `trade.spot.bracket`** **已与** **`trade.spot.limit_order`** **路由分居**（2026-05-09）。**`runtime-freeze` §3.8～§3.9** **最小编排** **已** **落笔** — **解冻对客** **时** **须** **与** **矩阵 PATH** **同窗** **无** **漂移**。**§4 邻域**：**矩阵** **`TBD/延期→冻结 PATH`** **时** **须** **同窗** **`trade-assistance` §8.2**、**`routing-engine` §2**、**[`confirmation-flow.md`](domains/agent/agent-orchestration/confirmation-flow.md)**、**[`trade-via-agent.md`](flows/trade-via-agent.md)** — **2026-05-12** **维持** **书面延期** **产品边界** **不变** **直至** **所内 PATH MR**。**（2026-05-20 [`product.md`](product.md) §非目标）**：本阶段 Exchange Agent **不交付 / 不须实现** **`trade.spot.oco` / `trade.spot.bracket`** **`call_exchange_write`** **闭环** — **与矩阵是否载 PATH **独立**。**宣称** **经 Agent 实盘 OCO/bracket 写** **尚须** **产品** **解除** **`product.md` §非目标** **与** **本节 DoD** **同窗 MR**。**仍须**：**矩阵 PATH 冻结** **同窗 MR**（**矩阵解冻路径**） |
| **CC-P1-02** | **C 类外网工具**（`tool.web.social_sentiment` 等）参数与合规 | [`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **§8.4** | **ADR-003**：[`../design/adr/003-external-tools-compliance-and-budget.md`](../design/adr/003-external-tools-compliance-and-budget.md)。**OpenAPI**：**`ToolRegistryEntry`**（[`tool-management-schemas.yaml`](../openapi/components/tool-management-schemas.yaml)）**含** **`externalToolCompliance`**、**`enabledOperational`**。**运行时选用**：**仅** **已登记且启用态为真** **之 C 类** **可调用**；**未配置或停用** **则不使用**。**生产将 C 类置为启用（写闸）** **默认** **`legalReviewTicketId` 非空** + **法务 PII/预算** **对签** **与** **工单号** **进** **Registry**（**或** **`contract-closure` §8** **合规豁免登记**） |
| **CC-P1-03** | **技能/工具登记表 SSOT 形态**（DB vs `design/` registry） | [`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) §4～6、`FR-TS07` | **ADR-002**：[`../design/adr/002-tool-skill-registry-ssot.md`](../design/adr/002-tool-skill-registry-ssot.md)。**`tool-management/functions`** **已载** **实现镜像验收句**（2026-05-09）。**文档子集（2026-05-12）**：**关闭** **全流程** **MR** **建议** **勾选** — **(1)** **DB/镜像** **`toolId`/`skillId`** **与** **`trade-assistance` §8** **幂等**；**(2)** **回归** **Enable** **`matrixStatus`/`SC-MCV1-05`**；**(3)** **观测** **`SC-OBS01`** **可 join**。**仍须**：**实现镜像** **与** **表** **幂等验收** |
| **CC-P1-04** | **Prompt 域**：**条文** **「评审中」** **与** **仓库内** **[`admin/prompt-management.yaml`](../openapi/admin/prompt-management.yaml)** **已齐**；**缺口** **=** **多模块会签** **+** **§1.2 六款逐项归档** **+（若宣称 B）** **Hosted/生产实测** | [`prompt-management/overview.md`](domains/admin/prompt-management/overview.md) 文首「状态」；**PATH 专节** [`../design/api.md`](../design/api.md) **「运营侧 Prompt Management API」**；**详规** [`prompt-management/functions.md`](domains/admin/prompt-management/functions.md) **§1.4、§2～§5**，[`prompt-management/runtime-injection.md`](domains/admin/prompt-management/runtime-injection.md)，[`observability/overview.md`](observability/overview.md) **§2.3 · SC-OBS04**；**PRS 体系 · 改什么去哪** [`prompt-runtime/README` §4](prompt-runtime/README.md#prs-where-to-edit)；**§7.2～§7.4 派工·AC-09 · 同窗回链** [`closure-remaining` §7.2～§7.4](closure-remaining.md#cc-ac09-closure-matrix) · [§7.3](closure-remaining.md#cc-prompt-runtime-closure-loop) | **关闭 CC-P1-04（全流程）**：**多模块会签**（**`management-console` 模块二**、**`billing`/`telegram`/`observability` Prompt join**）**+** **登记表** **Prompt 行**：**可访问 spec + Owner**（**§1.2**）**或** **外链终稿**。**核对表** **§1.4**（2026-05-10）。**A 阶段** PATH **已载** **`design/api` v0.1.29+**。**（2026-05-12）** **§1.4** **核对表** **须** **同窗** **本文** **§1.2** **六款归档** — **仍须** **会签 MR** **逐项勾选** |
| **CC-P1-05** | **架构 C4 容器图** **`architecture`「待补充」历史表述** | [`../design/architecture.md`](../design/architecture.md) | **文档**：**语境 + 容器** **mermaid + 表** **已载**。**可选**：**外链高清图** / **更细组件图** — **非** **P0** **阻塞** |
| **CC-P1-06** | **运营后台 Telegram Bot / Webhook**：**仓库内** **[`admin/telegram-channels.yaml`](../openapi/admin/telegram-channels.yaml)** **已载 PATH（B 文档子集）**；**缺口** **=** **网关实现** **`secretRef`/setWebhook/deleteWebhook/`getWebhookInfo`/自检** **生产实测** **与** **`TELEGRAM_*` bundle·乐观锁** **同窗** **SC-TAC / SC-TG-ADMIN** | [`../design/api.md`](../design/api.md) **「运营侧 Telegram 渠道运维 API」专节**、**登记表「Telegram Bot / Webhook」行**，[`telegram/admin-bot-config.md`](domains/agent/telegram/admin-bot-config.md)，[`trading-agent-config/keys.md` §4](domains/admin/trading-agent-config/keys.md)，[`trading-agent-config/functions.md` §2.6～§2.10 / §4](domains/admin/trading-agent-config/functions.md) | **A 阶段（文档）**：**专节 PATH 示意** **已齐**（**[`design/api`](../design/api.md) §「运营侧 Telegram…」**）。**B 阶段（仓库内）**：**`admin/telegram-channels.yaml`** **+** **`OWNERS.md`** **+** **`info.contact`（Jesson@chainup.com）** **已链**。**（2026-05-12）** **`admin-bot-config`** **已链** **§13** **`CC-P1-06`** **一致口径**。**仍须**：**Hosted/生产**、**`secretRef`、setWebhook/deleteWebhook、`getWebhookInfo`、自检** **与** **SC-TAC-11～13**、**SC-TG-ADMIN-*** **可对签**；**同窗** **`management-console`** **附录 A §5.1** |
| <span id="cc-p1-07">**CC-P1-07**</span> | **统一交易语义层**：**Intent → Canonical → Execution Gateway → Adapter** **文档与架构收口**（**多所演进前置**） | [`canonical-trading-model.md`](../design/canonical-trading-model.md)、[`ADR-004`](../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`architecture.md`](../design/architecture.md)、[`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **§2.6**、本条 **§8** | **文档 A（本 MR 可达）**：上列 **已链** **且** **`trade-assistance` §2.6** **显式** **ADR-004**。**实现 B（后续 MR）**：**Execution Gateway + `venue` 解析 + CoobitAdapter** **与** **现网工具路径** **行为对拍**；**观测** **可选** **`canonicalOp`/`venue`** — **关闭 B** **须** **独立 MR** **登记** **单测/对拍证据**。**本条** **不** **豁免** **`api.md` 矩阵** **与** **allowlist**。 |

<a id="cc-p1-doc-vs-b"></a>

### 3.0 **P1 · 需求文档冻结 vs B 阶段（生产可对签）分期**

**用途**：对齐 **干系人节奏** — **团队可** **先** **以** **域正文 + OpenAPI 文档子集** **冻结「可进开发」之需求**（**或** **§1.1 A 阶段** **下限**），**不** **自动等同** **[`§1.2` 六款](#cc-section9-six)** **全开**、**§2～§3** **P1 DoD 全流程关闭** **或** **PRD §13 生产勾选**。**CC-P1-03 / P1-04 / P1-06** 等 **「文档先行」** **时**：**MR/§8** **须** **区分** **「需求已冻结」** **与** **「B 阶段 / 实现与 Hosted 实测未闭」** — **禁止** **仅用文档改动** **冒充** **契约收口关单**。**升格 [`spec.md`](spec.md) Status / 对外冻结叙事** **仍** **仅** **[§5.1](#cc-stage4-spec-gate)**。**人类评审入口**：[`product/requirements-review.md`](../../product/requirements-review.md) **§5～§6**、**[§7.5 · ADR-004 / CC-P1-07 速查](../../product/requirements-review.md#cc-adr004-review-checklist)**。

<a id="cc-p1-batch-mr-split"></a>

### 3.1 P1 批量推进 · 建议 MR 拆单（**文档索引 · 2026-05-14**）

**原则**：**勿** **单 MR 堆满** **P1**；**CC-P1-02** **（外网工具 + 法务）** **宜独立 MR** **便于合规评审**。合并窗口 **仍须** **§10** **五步**、**§9** **六款** **可链锚点**、**§8** **一行登记**。**MR 描述首节粘贴稿** **见** **[§3.2](#cc-p1-mr-paste-templates)**。**P0 单条关单** **GitHub 补充稿** **见** **[§3.4](#cc-p0-mr-github-full)**。

| 建议 MR | 主要 CC | 邻域与证据链（**关闭 DoD 时附链**） |
|--------|---------|--------------------------------------|
| **MR-A** | **CC-P1-02** | ADR-003、[`trade-assistance` §8.4](domains/agent/exchange-agent/trade-assistance.md)、[`tool-management-schemas.yaml`](../openapi/components/tool-management-schemas.yaml)、**`enabledOperational`（仅启用可选）** **+** 生产 **Enable** 写闸 + **`legalReviewTicketId`** |
| **MR-B** | **CC-P1-04** | [`prompt-management/functions` §1.4](domains/admin/prompt-management/functions.md)、PRD 模块二、[`observability` §2.3](observability/overview.md)、[`closure-remaining` §7.2～§7.4](closure-remaining.md#cc-ac09-closure-matrix)、[`closure-remaining` §7.6](closure-remaining.md#cc-closure-exec-checklist)、[`design/api`](../design/api.md) **Prompt** **登记表行** |
| **MR-C** | **CC-P1-06** | [`admin/telegram-channels.yaml`](../openapi/admin/telegram-channels.yaml)、[`telegram/admin-bot-config`](domains/agent/telegram/admin-bot-config.md)、PRD §13、`SC-TAC-11～13` / **`SC-TG-ADMIN-*`** **实测** |
| **MR-D** | **CC-P1-01** | **分支 A**：解冻矩阵 PATH → §4 + §7。**分支 B**：窄 MR 重申矩阵延期邻域。**分支 C**：[`product.md`](product.md) §非目标 — 本阶段 Agent 不交付 OCO/bracket 写；**同窗** `trade-via-agent`、`telegram/overview`、`agent-coobit-api-allowlist` §3、`runtime-freeze` §3.8。 |
| **MR-E** | **CC-P1-03** | [`ADR-002`](../design/adr/002-tool-skill-registry-ssot.md)、[`tool-management/functions.md`](domains/admin/tool-management/functions.md)（**镜像幂等验收**）、[`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **§4～§8 · `FR-TS07`**、[`admin/tool-management.yaml`](../openapi/admin/tool-management.yaml)、**`SC-MCV1-05`**、**`SC-OBS01`** |
| **MR-F** | **CC-P1-07（实现 B）** | [`ADR-004`](../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`canonical-trading-model.md`](../design/canonical-trading-model.md) — **Execution Gateway + CoobitAdapter** **对拍**、**观测 `venue`/`canonicalOp`（可选）** |

<a id="cc-p1-mr-paste-templates"></a>

### 3.2 P1 MR 描述粘贴稿（MR-A～E · **组织轨模板**）

**用途**：与 **§3.1** **拆单表** **一一对应**；**合并描述** **首节** **须** **含** **上文** **§10** **五步** +（**拟对客宣称之能力**）**§9** **六款勾选**。**派工表同屏镜像** **见** **[§5.2.5](#cc-p1-exec-mr-skeleton)**（**与下文同文**）；**修订骨架** **须** **与** **§5.2.5** **同窗** **（见 §5.2.5 编辑纪律）**。**合入后** **§8** **顶行登记** **+** **递增本文档版本**。**GitHub** **可勾选全稿**：**P1** **[§3.3](#cc-p1-mr-github-full)** · **P0** **[§3.4](#cc-p0-mr-github-full)**。

---

#### MR-A — **CC-P1-02**（C 类外网工具 · 合规独立 MR）

**建议标题**：`feat(compliance): external tools registry — legalReviewTicketId + CC-P1-02`

**正文骨架**（**复制后补链接/工单号**）：

1. **本轮 CC**：**CC-P1-02**（见 **§3** 主表）。
2. **§10 五步**：**①** CC-P1-02 **②** §9（**若** **Enable 之 `toolId` 涉及对客宣称**）**③** §7 登记 **`admin/tool-management` + `tool-management-schemas`** **④** **§8** **+** **版本脚注** **⑤** **邻域**：[`trade-assistance` §8.4](domains/agent/exchange-agent/trade-assistance.md)、ADR-003、观测 **`SC-OBS01`**。
3. **证据链**：[`../design/adr/003-external-tools-compliance-and-budget.md`](../design/adr/003-external-tools-compliance-and-budget.md)；[`tool-management-schemas.yaml`](../openapi/components/tool-management-schemas.yaml) **`ToolRegistryEntry.externalToolCompliance` / `legalReviewTicketId`**；[`trade-assistance` §8.4](domains/agent/exchange-agent/trade-assistance.md)。
4. **关闭 DoD**：**运行时** **审计** — **仅** **`enabledOperational=true`** **之 C 类** **可出现在工具选用路径**；**生产将 C 类置为启用** **时**：**法务** **书面** **PII/预算** **对签** **+** **工单号** **写入** **生产 Registry**；**`legalReviewTicketId` 非空**（**或** **等价豁免登记 §8 风险**）。

---

#### MR-B — **CC-P1-04**（Prompt · 多模块会签）

**建议标题**：`feat(docs/spec): prompt-management sign-off — CC-P1-04 + §1.4 checklist`

**正文骨架**：

1. **本轮 CC**：**CC-P1-04**。
2. **§10 五步** + **§9**（**模块二 Prompt** **对客承诺范围** **逐项**）。
3. **证据链**：[`prompt-management/functions` §1.4](domains/admin/prompt-management/functions.md)；[`prompt-management/runtime-injection.md`](domains/admin/prompt-management/runtime-injection.md)；[`observability/overview` §2.3](observability/overview.md)；[`closure-remaining` §7.2～§7.4](closure-remaining.md#cc-ac09-closure-matrix)；[`closure-remaining` §7.6](closure-remaining.md#cc-closure-exec-checklist)；[`design/api` Prompt 登记表行](../design/api.md)；[`admin/prompt-management.yaml`](../openapi/admin/prompt-management.yaml)。
4. **关闭 DoD**：**`functions` §1.4** **核对表** **逐项 MR 勾选**；**登记表 Prompt 行** **spec + Owner** **与** **§1.2** **同窗**。

---

#### MR-C — **CC-P1-06**（Telegram 渠道运维 · Hosted/生产实测）

**建议标题**：`feat(ops): admin telegram channels — webhook lifecycle + CC-P1-06`

**正文骨架**：

1. **本轮 CC**：**CC-P1-06**。
2. **§10 五步** + **§9**（**渠道类型 A**、**Telegram 卡片**）。
3. **证据链**：[`admin/telegram-channels.yaml`](../openapi/admin/telegram-channels.yaml)；[`telegram/admin-bot-config.md`](domains/agent/telegram/admin-bot-config.md)；PRD **§13**；**`SC-TAC-11～13` / `SC-TG-ADMIN-*`** **实测记录链接**。
4. **关闭 DoD**：**Hosted 或生产** **`setWebhook` / `getWebhookInfo` / `deleteWebhook`** **与** **`secretRef`** **可对签**；**附录 A §5.1** **同窗**。

---

#### MR-D — **CC-P1-01**（**OCO/bracket** · **解冻或延期重申**）

**分支 A · 解冻矩阵 PATH**：**须** **§4** **全文核对** + **§7** **登记** + **`trade-assistance` §8.2**、**`routing-engine` §2**、[`runtime-freeze.md`](domains/agent/agent-orchestration/runtime-freeze.md) **§3.8～§3.9**、[`confirmation-flow`](domains/agent/agent-orchestration/confirmation-flow.md)、[`trade-via-agent`](flows/trade-via-agent.md) **同窗 MR**。

**分支 B · 维持书面延期（窄 MR）**：**建议标题** `docs(spec): reaffirm OCO/bracket matrix deferral — CC-P1-01`；**正文** **重申** **§3** **P1-01** **产品边界** **与** **邻域**（**`trade-assistance` §8.2、`routing-engine` §2、`runtime-freeze` §3.8～§3.9、`confirmation-flow`、`trade-via-agent`**）**链接** **无漂移**；**不** **伪装** **矩阵已冻结**。

**分支 C · `product.md` §非目标（本阶段 Agent 不交付 OCO/bracket 写）**：**建议标题** `docs(spec): product off — Agent spot OCO/bracket + CC-P1-01同窗` — **对齐** **[`product.md`](product.md) §非目标** **与** **`trade-assistance`/`trade-via-agent`/`telegram/overview`/`agent-coobit-api-allowlist` §3**；**明确** **`FR-T05`/`主站`/分步**。**不与矩阵 PATH 解冻混读**。若 **日后** **同时解除 §非目标** **且矩阵 PATH 已冻结** → **走分支 A**。

---

<a id="cc-p1-mr-e"></a>

#### MR-E — **CC-P1-03**（**技能/工具登记表 SSOT · DB 与镜像幂等**）

**建议标题**：`feat(registry): tool skill SSOT mirror idempotency — CC-P1-03`

**正文骨架**：

1. **本轮 CC**：**CC-P1-03**（见 **§3** 主表 · ADR-002）。
2. **§10 五步** + **§9**（**若** **对客宣称** **新** **`toolId`/`skillId` 或控制台矩阵 Enable** — **须** **款 1·2·3** **可链**；**纯实现幂等 MR** **可** **多款 N/A** **附理由**）。
3. **证据链**：[`../design/adr/002-tool-skill-registry-ssot.md`](../design/adr/002-tool-skill-registry-ssot.md)；[`tool-management/functions.md`](domains/admin/tool-management/functions.md)（**实现镜像验收句**）；[`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **§4～§6 · §8 · `FR-TS07`**；[`admin/tool-management.yaml`](../openapi/admin/tool-management.yaml)；[`observability/overview.md`](observability/overview.md) **§2.1 · `SC-OBS01`**。
4. **关闭 DoD**：**(1)** **DB/镜像** **`toolId`/`skillId`** **与** **`trade-assistance` §8** **幂等**（**同窗登记或抽检链接**）；**(2)** **回归** **Enable** **`matrixStatus` / `SC-MCV1-05`**；**(3)** **观测** **`SC-OBS01`** **`toolId`/`skillId` 可 join**。

<a id="cc-p1-mr-github-full"></a>

### 3.3 P1 MR · GitHub 描述全稿（**复制即用**）

**用法**：**整段复制** 到 MR Description；将 **`【MR_ID】`**（`MR-A`～`E`）、**`【CC_ID】`**、**`【一句能力】`**、**`【§7 登记摘要】`**、**`【邻域第五步一句】`** 及 **不适用款** 的 **N/A 理由** 填齐。**矩阵若解冻** **须** **另贴** **§4 核对清单** **全文**（**§7** **表** **勾选**）。**P0** **关单** **请用** **[§3.4](#cc-p0-mr-github-full)** **（** **同窗** **[§5.2](#cc-exec-remaining)** **）**。

```markdown
## 契约收口 · 【MR_ID】· 【CC_ID】· 【一句能力】

### contract-closure §10 · 五步

- [ ] **1** 本轮关闭/部分关闭 CC：`【CC_ID】`（§3 主表 DoD 句已对齐）
- [ ] **2** 下文 §9 六款已逐项填写链接或 **N/A（理由）**；若变更 `design/api` 矩阵格 → §4 清单已跑完
- [ ] **3** §7 已登记：`【§7 登记摘要】`（Spec 路径或 URL、`design/api` 新版本脚注、关联实现 PR）
- [ ] **4** 合并前将追加 contract-closure **§8** 顶行 + 递增 **contract-closure** / **design/api** 等 **版本脚注**
- [ ] **5** 邻域同窗：`【邻域第五步一句】`

### contract-closure §1.2 · 六款（仅对 **拟对客宣称** 能力全勾；否则标 N/A）

**本 MR 对客宣称范围（无则写「无 — 文档/实现/Registry 内部」）**：

- [ ] **1** `design/api` 登记表 + 矩阵（链接：               ） / N/A：
- [ ] **2** `trade-assistance` §8 · `FR-TS07` · `toolId`（链接：               ） / N/A：
- [ ] **3** exchange-agent + Telegram 卡片（链接：               ） / N/A：
- [ ] **4** 编排 **`scenarioId`** **+** **ADR-001** **+** **`runtime-freeze` §3**（**§3.1～§3.11** **最小编排** **同窗** **`routing-engine` 文首** **「写路径 · 编排下限对签」**；链接：               ） / N/A：
- [ ] **5** 自动化 / Pull（链接：               ） / N/A：
- [ ] **6** REST↔WS / `SC-OBS06`（链接：               ） / N/A：

### MR 专用 · 证据与关单

**（以下为 §3.1 对应行；保留本 MR 一项，删去其余）**

**MR-A · CC-P1-02**

- 证据：ADR-003；`tool-management-schemas`；`trade-assistance` §8.4
- 关单：**启用态** **与路由一致**（**仅 true 可调**）______
- 关单：法务工单号 ______；生产 **`legalReviewTicketId`** **（Enable 写闸）** ______

**MR-B · CC-P1-04**

- 证据：`prompt-management/functions` §1.4；`runtime-injection`；`observability` §2.3；`closure-remaining` §7.2～§7.4 · §7.6；`design/api` Prompt 行；`admin/prompt-management.yaml`
- 关单：§1.4 核对表 MR 内逐项勾选截图或链接 ______

**MR-C · CC-P1-06**

- 证据：`admin/telegram-channels.yaml`；`admin-bot-config`；PRD §13；SC 实测 Runbook ______
- 关单：Hosted 或生产 webhook 生命周期可对签证据 ______

**MR-D · CC-P1-01**

- **解冻**：§4 全文 + §7 + `trade-assistance` §8.2 / `routing-engine` §2 / `runtime-freeze` §3.8～§3.9 / `confirmation-flow` / `trade-via-agent` MR 链接 ______
- **延期窄 MR**：邻域（**含** **`runtime-freeze` §3.8～§3.9**）无漂移声明 + 矩阵仍为书面延期（附 `design/api` 行锚）______

**MR-E · CC-P1-03**

- 证据：ADR-002；`tool-management/functions`；`trade-assistance` §4～8 · `FR-TS07`；`admin/tool-management.yaml`；`SC-OBS01`
- 关单：DB/镜像幂等验收记录 ______；`matrixStatus`/`SC-MCV1-05` 回归 ______；观测 join 证据 ______
```

<a id="cc-p0-mr-github-full"></a>

### 3.4 P0 MR · GitHub 描述补充稿（**CC-P0-01～05**）

**用法**：**在** **[§5.2 主表](#cc-exec-remaining)** **选定** **一行** **`CC-P0-xx`**；**将** **[§5.2.2](#cc-exec-remaining)** **对应格** **权威锚点** **复制** **进** **下文「证据链」**；**建议 MR 标题** **见** **[§5.2.4](#cc-exec-remaining)**。**CC-P0-04 / P0-05** **须** **先** **[§2.1](#cc-p0-signoff-register)** **再** **动** **PRD §13** **`[x]`**（**映射** **[§5.2.1](#cc-exec-remaining)**）。**推荐首包**：**P0-04 + P0-05** **同窗** §2.1。

```markdown
## 契约收口 · P0 · 【CC_P0_ID】· 【一句能力】

### contract-closure §10 · 五步

- [ ] **1** 本轮关闭/部分关闭 CC：`【CC_P0_ID】`（§2 主表 DoD 已对齐）
- [ ] **2** 下文 §9 六款已逐项填写链接或 **N/A（理由）**；若变更 `design/api` 矩阵格 → §4 核对已跑完 + §7 已登记
- [ ] **3** §7 已登记：`【§7 登记摘要】`（Spec 路径或 URL、Hosted/tag、`design/api` 新版本脚注、关联实现 PR）
- [ ] **4** 合并前将追加 contract-closure **§8** 顶行 + 递增 **contract-closure** / **design/api** / 域文档 **版本脚注**
- [ ] **5** 邻域同窗：`【邻域第五步一句】`

### contract-closure §1.2 · 六款（仅对 **拟对客宣称** 能力全勾；否则标 N/A）

**本 MR 对客宣称范围（无则写「无 — 内部契约/实现」）**：

- [ ] **1** `design/api` 登记表 + 矩阵（链接：               ） / N/A：
- [ ] **2** `trade-assistance` §8 · `FR-TS07` · `toolId`（链接：               ） / N/A：
- [ ] **3** exchange-agent + Telegram 卡片（链接：               ） / N/A：
- [ ] **4** 编排 **`scenarioId`** **+** **ADR-001** **+** **`runtime-freeze` §3**（**§3.1～§3.11** **最小编排** **同窗** **`routing-engine` 文首** **「写路径 · 编排下限对签」**；链接：               ） / N/A：
- [ ] **5** 自动化 / Pull（链接：               ） / N/A：
- [ ] **6** REST↔WS / `SC-OBS06`（链接：               ） / N/A：

### P0 · 证据链（contract-closure §5.2.2）

- **§5.2 主表行**：`【CC_P0_ID】`
- **权威锚点（粘贴本仓库路径或可点 URL）**：

### P0 · §2.1 会签回填（**仅** CC-P0-04、**CC-P0-05**；不适用删本节）

- [ ] **CC-P0-04**：财务工单号 ______ · 会签日期 ______ · 范式 A/B/JSON · 配置首填 MR ______ · 审计 id ______
- [ ] **CC-P0-05**：实现 MR ______ · `executionId` 协查样例 ______ · `SC-OBS03` / UNKNOWN 策略链 ______

### PRD §13（若有；须与 §2.1 / 实现同窗）

- [ ] **D-12**（**CC-P0-04**）/ **D-5·D-7**（**CC-P0-05**）：**仅于** 上表与工单/MR **一致后** **由 `[ ]` 改 `[x]`**
```

---

<a id="cc-section4-matrix"></a>

## 4. 矩阵解冻后的「必做 MR 核对」（防止文档漂移）

任一 **`design/api.md` 矩阵格** **从 `TBD` → 冻结 PATH** **或** **延期备注变更** 后，同一变更窗口 **建议至少核对**：

- [`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **§8** **对应行 + `FR-TS07`** 登记行是否 **补上锚点 PATH**；
- [`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **（原 `tools.md` §10.4 叙事）**、[`monitoring-tasks.md`](domains/agent/exchange-agent/monitoring-tasks.md)、[`automation-alerts.md`](flows/automation-alerts.md)、[`overview-legacy-migration.md`](domains/agent/exchange-agent/overview-legacy-migration.md) **§2**（旧 **§10.6** Push/自动化）与 **SC-T08**（若牵涉自动化/E2E）是否 **仍可测**；
- [`domains/agent/telegram/overview.md`](domains/agent/telegram/overview.md) **类型 A** 是否与 **新业务线字段**矛盾；[**`telegram/admin-bot-config.md`**](domains/agent/telegram/admin-bot-config.md) **`TELEGRAM_*`/Webhook** 与 **新网关 host / 签名**是否一致；
- [`observability.md`](observability/overview.md) **`toolId`/`skillId`/§2 · §2.3（Prompt binding）**、**§2.2 · `exchangeViewSource`**、**`SC-OBS06`** **是否与新工具、对账通路解冻**一致；**同窗** **[`../design/api.md`](../design/api.md)** **「REST ↔ WebSocket 对账」**、[`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **§2.5**、[`Runtime/reconciliation.md`](Runtime/reconciliation.md) **§3**；
- [`risk/README.md`](risk/README.md) **与** [`risk/acceptance.md`](risk/acceptance.md) **及** [`domains/admin/trading-agent-config/keys.md`](domains/admin/trading-agent-config/keys.md) **§1～§3**：**Kill、Feature、交易护栏** **`configKey`** **变更**是否仍 **与** [`domains/agent/exchange-agent/boundaries.md`](domains/agent/exchange-agent/boundaries.md) **§9**、[`Runtime/execution.md`](Runtime/execution.md) **§1·2** **同窗**；**`SC-RISK-01～05`** **仍** **可测**（**或** **书面剪裁已登记** **本节脚注**）；
- [`flows/trade-via-agent.md`](flows/trade-via-agent.md)、[`automation-alerts.md`](flows/automation-alerts.md) **步骤是否与矩阵一致**；
- **`design/api.md` 版本号** — **须有变更脚注**（与邻域 **`v0.1.x+` 对签** 对齐）。

---

## 5. 发布前文档联动（与 **`management-console-v1-prd.md` §13** 发布勾选对齐）

[`management-console-v1-prd.md`](domains/admin/management-console-v1-prd.md) **§「发布 / 对齐检查清单」** 中 **`[ ]`** 项，与本文件 **§2～§3** **交叉引用**；**升格 `spec.md` Status** **之** **操作 gate** **见** **下文** **§5.1**。**未闭项派工表** **见** **[§5.2](#cc-exec-remaining)**。**不得在** **`D-12`、矩阵核心 `TBD`、收入专户模板** **未收口**情况下，将 **`spec.md` Feature** 状态标为 **已冻结生产承诺**。

**聚合索引**：本目录 [`spec.md`](spec.md)。

<a id="cc-stage4-spec-gate"></a>

### 5.1 升格 `spec.md` Status / 对外「生产契约已冻结」叙事 gate（计划阶段 4）

**用途**：与 **需求层契约收口执行计划 · 阶段 4** **操作定义** **同窗** — **锚点在本仓库**（**勿** **仅依赖** **外部 plan 文件**）。

**同时满足** **方可** **审慎** **改写** **[`spec.md`](spec.md) Feature Status** **或** **对外宣称** **全能力/production 冻结**：

1. **上文** **§2** **五条 CC-P0** **DoD** **均已** **在 MR/工单勾选** **（** **或** **已** **书面剪裁** **并** **登记风险于** **§4/§8** **）**。
2. **上文** **§3** **与 V1 对外承诺相交** **之 P1**（**至少** **CC-P1-01 / P1-02 / P1-04 / P1-06** **相关句**）**DoD** **已勾选** **或** **[`product.md`](product.md)** **非目标** **已** **裁剪承诺** **并** **互引** **§2～§3**。
3. **[`management-console-v1-prd.md`](domains/admin/management-console-v1-prd.md) §13** **发布清单** **与** **D-12**、**矩阵**、**收入专户**、**账务/观测** **叙事** **无矛盾**。
4. **拟** **对客宣称** **之** **每条能力** **须** **附** **上文** **§9** **六款** **自检** **可点链接**（**域 §、`design/api`、OpenAPI path**）。

<a id="cc-exec-remaining"></a>

### 5.2 关单剩余项 · 执行矩阵（**派工索引**）

**用途**：把 **§2 · §3** **DoD** **未闭项** **收束为** **可开 MR 的粒度**；**本表** **不替代** **主表** **—** **任一行「完成」** **仍须** **工单/MR 证据**（**禁止** **仅编辑本表** **或** **超前勾选** **PRD §13**）。**P1** **MR-A～E** **首节粘贴短骨架** **与** **§5.2** **主表同屏** **见** **[§5.2.5](#cc-p1-exec-mr-skeleton)**（**详版 SSOT** **仍** **[§3.2](#cc-p1-mr-paste-templates)**）。

| ID | 依赖类型 | 下一动作（建议 **单 MR** 或 **可合并窗口**） | 回填/勾选 |
|----|----------|----------------------------------------------|-----------|
| **CC-P0-01** | 所内 Spec 已齐 | **(b)** Hosted **或** **(c)** `release-*` **与** **`design/api` 登记表 + (a)** **同窗**；**§1.2 六款** **归档** | [`openapi/README`](../openapi/README.md)、**§7**、**§8** |
| **CC-P0-02** | 矩阵 B | **延期格**：**PATH 冻结** **或** **书面延期终版**；**WS/listenKey**：**OpenAPI·实现** **终裁** **同窗** **矩阵** | **§4**、**§7**、**`design/api` 脚注** |
| **CC-P0-03** | 生产网关 | **`billing.md` §12.1** **三线 baseUrl** **首填**；**模块五 / `me` / internal** **登记表** **B 填链** **与实现同窗** | **`billing` §12.1**、**§8** |
| **CC-P0-04** | 财务会签 | **`billing` §10.6.1** **1～6**；**[§2.1](#cc-p0-signoff-register)** **填工单/MR**；**PRD §13 `D-12` → `[x]`** | **§2.1**、[PRD §13](domains/admin/management-console-v1-prd.md#mc-prd-appendix-a-release-checklist) |
| **CC-P0-05** | 实现 + 观测 | **`billing` §10.3.1** **1～5** + **`SC-OBS03`**；**[§2.1](#cc-p0-signoff-register)**；**PRD `D-5`/`D-7` → `[x]`** | **§2.1**、PRD §13 |
| **CC-P1-01** | 矩阵 OCO | **MR-D**：**解冻** **§4+§7** **或** **延期窄 MR** **邻域同窗**（**含** **`runtime-freeze` §3.8～§3.9**） | **[§3.3](#cc-p1-mr-github-full)** |
| **CC-P1-02** | 法务 | **MR-A**：**启用态** **+** **PII/预算** **工单 +** **`legalReviewTicketId`** **（生产 Enable 写闸）** | **[§3.3](#cc-p1-mr-github-full)** |
| **CC-P1-03** | 实现 | **MR-E**：**DB/镜像** **`toolId`/`skillId` 幂等** **验收**（ADR-002）；**同窗** **[§3.2 · MR-E](#cc-p1-mr-e)** | **[§3.3](#cc-p1-mr-github-full)**、**[`tool-management/functions`](domains/admin/tool-management/functions.md)**、**§8** |
| **CC-P1-04** | 会签 | **MR-B**：**`functions` §1.4** **+** **§1.2 六款** | **[§3.3](#cc-p1-mr-github-full)** |
| **CC-P1-05** | （可选） | **外链高清图** — **非 P0 阻塞** | — |
| **CC-P1-06** | 生产 | **MR-C**：**webhook 生命周期** **Hosted/实测** **+ SC** | **[§3.3](#cc-p1-mr-github-full)** |

**推荐顺序**：**首包 MR**（**P0-04 + P0-05**）**可直接复制** **[§3.4](#cc-p0-mr-github-full)**；继而 **P0-03 / P0-01** → **P0-02**；**P1** **与** **MR-A～E** **可并行** **（** **勿** **单 MR 堆满** **）**。**全部 P0 + 相交 P1 闭合后** **方** **审慎** **走** **[§5.1](#cc-stage4-spec-gate)** **升格 `spec.md`**。

<a id="cc-521-prd-map"></a>

#### 5.2.1 **PRD §13** **映射**（**发布勾选同窗**）

| §5.2 行 | [`management-console-v1-prd` §13](domains/admin/management-console-v1-prd.md#mc-prd-appendix-a-release-checklist) **直接相关项** |
|---------|----------------------------------------------------------------------------------------------------------------------------------|
| **CC-P0-04** | **`D-12` / `BILLING_AGENT_REVENUE_ACCOUNT_REF`** **`[ ]`→`[x]`**（**与** **[§2.1](#cc-p0-signoff-register)** **同窗**） |
| **CC-P0-05** | **`D-5` / `D-7`** **`[ ]`→`[x]`**（**与** **[§2.1](#cc-p0-signoff-register)** **同窗**） |
| **CC-P0-01～03** | **无独占 bullet**；**关单后** **须** **满足** **[§5.1](#cc-stage4-spec-gate)** **条款 1·3**（**矩阵 / Hosted / 账务叙事** **一致**） |
| **CC-P1-06** | **Telegram / Webhook** **项**：**文档子集** **已为** **`[x]`**；**全流程 DoD** **仍须** **Hosted/生产实测** **同窗** **本条** **与** **§3** |
| **CC-P1-03** | **不** **独占** **§13** **单条** **`[ ]`** **作为** **关单** **唯一** **凭据**；**MR-E** **闭链** **须** **与** **[PRD §6 模块三 — Tool](domains/admin/management-console-v1-prd.md)**（**FR-MC301～305**）、**§13** **`SC-MCV1-05`/`CC-P1-03`** **核对项** **`[x]`**（**与实现同窗**）、**[`tool-management/overview`](domains/admin/tool-management/overview.md)** **及** **`trade-assistance` §8** **无矛盾**（**组织轨** **[MR-E · §3.2](#cc-p1-mr-e)**） |
| **CC-P1-02 / P1-04** | **不** **映射** **§13** **单条** **`[ ]`**；**合规/Prompt** **发布叙事** **须** **与** **模块二/三** **及** **§2～§3** **无矛盾** |

#### 5.2.2 **MR 证据链 · 锚点速查**（**粘贴至描述**）

| ID | 权威锚点（**按需复制**） |
|----|--------------------------|
| **CC-P0-01** | [`openapi/README` · Hosted / `release-*`](../openapi/README.md) · [`design/api.md` · 登记表](../design/api.md) |
| **CC-P0-02** | [`design/api.md` · 子账户矩阵 / REST↔WS](../design/api.md) · [`stream/user-private-ws.yaml`](../openapi/stream/user-private-ws.yaml) |
| **CC-P0-03** | [`billing` · §12.1 生产 base 表](domains/admin/billing-management/overview.md) · [`internal/billing-token.yaml`](../openapi/internal/billing-token.yaml) · [`user/billing-me.yaml`](../openapi/user/billing-me.yaml) · [`admin/billing-admin.yaml`](../openapi/admin/billing-admin.yaml) |
| **CC-P0-04** | **[§2.1](#cc-p0-signoff-register)** · [`billing` · §10.6.1](domains/admin/billing-management/overview.md) · [PRD §11 `D-12`](domains/admin/management-console-v1-prd.md)（**附录 A**） |
| **CC-P0-05** | **[§2.1](#cc-p0-signoff-register)** · [`billing` · §10.3.1](domains/admin/billing-management/overview.md) · [`observability/overview.md`](observability/overview.md)（**`traceKey` / `SC-OBS03`**） · [`consume-and-bill.md`](flows/consume-and-bill.md) |
| **CC-P1-01～06** | **[§3.1](#cc-p1-batch-mr-split)** · **[§3.2](#cc-p1-mr-paste-templates)** · **[§5.2.5](#cc-p1-exec-mr-skeleton)**（**派工同屏短骨架**）· 域表 **§3** **主行** |

#### 5.2.3 **合入纪律**（**与 §10 / §9 对齐**）

- **任一** **§5.2 行关单 MR**：**首节** **建议** **含** **[§10](#cc-section10-five)** **五步节奏**；**P1** **可** **整段复制** **[§3.3](#cc-p1-mr-github-full)** **或** **首节要点** **[§5.2.5](#cc-p1-exec-mr-skeleton)**；**P0** **可** **整段复制** **[§3.4](#cc-p0-mr-github-full)**（**均含** **§10 + §9** **结构**）；**拟** **对外** **宣称** **本条能力** **时** **另附** **[§9](#cc-section9-six)** **六款** **可点自检**。
- **矩阵格** **`TBD`→冻结** **或** **延期备注变更**：**同一 MR** **跑** **[§4](#cc-section4-matrix)** **+** **[§7](#cc-section7-template)**（**典型** **CC-P0-02、CC-P1-01 解冻**）。
- **禁止**：**仅改** **PRD §13** **`[ ]`→`[x]`** **而不** **同窗** **[§2.1](#cc-p0-signoff-register)**（**P0-04/05**）**或** **实现 MR** **证据**。

#### 5.2.4 **建议 MR 标题前缀**（**可选**）

| ID | 前缀示例 |
|----|----------|
| **CC-P0-01** | `feat(docs): openapi Hosted or release tag — CC-P0-01` |
| **CC-P0-02** | `feat(docs/spec): matrix + WS path finalize — CC-P0-02` |
| **CC-P0-03** | `feat(docs/spec): billing prod baseUrl + registry B — CC-P0-03` |
| **CC-P0-04** | `feat(config/compliance): D-12 revenue account sign-off — CC-P0-04` |
| **CC-P0-05** | `feat(obs/billing): D-5 D-7 traceKey unknown — CC-P0-05` |
| **CC-P1-03** | `feat(registry): tool skill SSOT mirror idempotency — CC-P1-03` |
| **P1（其余）** | **MR-A～E** **见** **[§3.2](#cc-p1-mr-paste-templates)** **与** **[§5.2.5](#cc-p1-exec-mr-skeleton)** |

<a id="cc-p1-exec-mr-skeleton"></a>

#### 5.2.5 **P1 · MR-A～E 组织轨短骨架**（**派工表同窗** **[§3.2](#cc-p1-mr-paste-templates)**）

**用途**：与 **§5.2** **主表** **同屏** **复制首节要点**；**若有歧义** **以** **[§3.2](#cc-p1-mr-paste-templates)** **全文为准**（**本节** **为** **§3.2** **之** **同文镜像** **供派工检索**）。**编辑纪律**：**同一 MR** **内** **须** **同窗修订** **§3.2** **与** **本节** **之** **MR-A～E** **正文骨架**。**建议**：在 **`contract-closure.md`** **内** **检索** **`#### MR-`** **共五段**（A～E）**或** **节选 diff 双栏对照**。**禁止** **只改一处**。

---

**MR-A — CC-P1-02**（**C 类外网工具 · 合规独立 MR**）

**建议标题**：`feat(compliance): external tools registry — legalReviewTicketId + CC-P1-02`

**正文骨架**（**复制后补链接/工单号**）：

1. **本轮 CC**：**CC-P1-02**（见 **§3** 主表）。
2. **§10 五步**：**①** CC-P1-02 **②** §9（**若** **Enable 之 `toolId` 涉及对客宣称**）**③** §7 登记 **`admin/tool-management` + `tool-management-schemas`** **④** **§8** **+** **版本脚注** **⑤** **邻域**：[`trade-assistance` §8.4](domains/agent/exchange-agent/trade-assistance.md)、ADR-003、观测 **`SC-OBS01`**。
3. **证据链**：[`../design/adr/003-external-tools-compliance-and-budget.md`](../design/adr/003-external-tools-compliance-and-budget.md)；[`tool-management-schemas.yaml`](../openapi/components/tool-management-schemas.yaml) **`ToolRegistryEntry.externalToolCompliance` / `legalReviewTicketId`**；[`trade-assistance` §8.4](domains/agent/exchange-agent/trade-assistance.md)。
4. **关闭 DoD**：**运行时** **审计** — **仅** **`enabledOperational=true`** **之 C 类** **可出现在工具选用路径**；**生产将 C 类置为启用** **时**：**法务** **书面** **PII/预算** **对签** **+** **工单号** **写入** **生产 Registry**；**`legalReviewTicketId` 非空**（**或** **等价豁免登记 §8 风险**）。

---

**MR-B — CC-P1-04**（**Prompt · 多模块会签**）

**建议标题**：`feat(docs/spec): prompt-management sign-off — CC-P1-04 + §1.4 checklist`

**正文骨架**：

1. **本轮 CC**：**CC-P1-04**。
2. **§10 五步** + **§9**（**模块二 Prompt** **对客承诺范围** **逐项**）。
3. **证据链**：[`prompt-management/functions` §1.4](domains/admin/prompt-management/functions.md)；[`prompt-management/runtime-injection.md`](domains/admin/prompt-management/runtime-injection.md)；[`observability/overview` §2.3](observability/overview.md)；[`closure-remaining` §7.2～§7.4](closure-remaining.md#cc-ac09-closure-matrix)；[`closure-remaining` §7.6](closure-remaining.md#cc-closure-exec-checklist)；[`design/api` Prompt 登记表行](../design/api.md)；[`admin/prompt-management.yaml`](../openapi/admin/prompt-management.yaml)。
4. **关闭 DoD**：**`functions` §1.4** **核对表** **逐项 MR 勾选**；**登记表 Prompt 行** **spec + Owner** **与** **§1.2** **同窗**。

---

**MR-C — CC-P1-06**（**Telegram 渠道运维 · Hosted/生产实测**）

**建议标题**：`feat(ops): admin telegram channels — webhook lifecycle + CC-P1-06`

**正文骨架**：

1. **本轮 CC**：**CC-P1-06**。
2. **§10 五步** + **§9**（**渠道类型 A**、**Telegram 卡片**）。
3. **证据链**：[`admin/telegram-channels.yaml`](../openapi/admin/telegram-channels.yaml)；[`telegram/admin-bot-config.md`](domains/agent/telegram/admin-bot-config.md)；PRD **§13**；**`SC-TAC-11～13` / `SC-TG-ADMIN-*`** **实测记录链接**。
4. **关闭 DoD**：**Hosted 或生产** **`setWebhook` / `getWebhookInfo` / `deleteWebhook`** **与** **`secretRef`** **可对签**；**附录 A §5.1** **同窗**。

---

**MR-D — CC-P1-01**（**OCO/bracket** · **解冻或延期重申**）

**分支 A · 解冻矩阵 PATH**：**须** **§4** **全文核对** + **§7** **登记** + **`trade-assistance` §8.2**、**`routing-engine` §2**、[`runtime-freeze.md`](domains/agent/agent-orchestration/runtime-freeze.md) **§3.8～§3.9**、[`confirmation-flow`](domains/agent/agent-orchestration/confirmation-flow.md)、[`trade-via-agent`](flows/trade-via-agent.md) **同窗 MR**。

**分支 B · 维持书面延期（窄 MR）**：**建议标题** `docs(spec): reaffirm OCO/bracket matrix deferral — CC-P1-01`；**正文** **重申** **§3** **P1-01** **产品边界** **与** **邻域**（**`trade-assistance` §8.2、`routing-engine` §2、`runtime-freeze` §3.8～§3.9、`confirmation-flow`、`trade-via-agent`**）**链接** **无漂移**；**不** **伪装** **矩阵已冻结**。

**分支 C · `product.md` §非目标（本阶段 Agent 不交付 OCO/bracket 写）**：**建议标题** `docs(spec): product off — Agent spot OCO/bracket + CC-P1-01同窗` — **对齐** **[`product.md`](product.md) §非目标** **与** **`trade-assistance`/`trade-via-agent`/`telegram/overview`/`agent-coobit-api-allowlist` §3**；**明确** **`FR-T05`/`主站`/分步**。**不与矩阵 PATH 解冻混读**。**日后** **解除 §非目标 **且** **矩阵 PATH 冻结** → **分支 A**。

---

**MR-E — CC-P1-03**（**技能/工具登记表 SSOT · DB 与镜像幂等**）

**建议标题**：`feat(registry): tool skill SSOT mirror idempotency — CC-P1-03`

**正文骨架**：

1. **本轮 CC**：**CC-P1-03**（见 **§3** 主表 · ADR-002）。
2. **§10 五步** + **§9**（**若** **对客宣称** **新** **`toolId`/`skillId` 或控制台矩阵 Enable** — **须** **款 1·2·3** **可链**；**纯实现幂等 MR** **可** **多款 N/A** **附理由**）。
3. **证据链**：[`../design/adr/002-tool-skill-registry-ssot.md`](../design/adr/002-tool-skill-registry-ssot.md)；[`tool-management/functions.md`](domains/admin/tool-management/functions.md)（**实现镜像验收句**）；[`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) **§4～§6 · §8 · `FR-TS07`**；[`admin/tool-management.yaml`](../openapi/admin/tool-management.yaml)；[`observability/overview.md`](observability/overview.md) **§2.1 · `SC-OBS01`**。
4. **关闭 DoD**：**(1)** **DB/镜像** **`toolId`/`skillId`** **与** **`trade-assistance` §8** **幂等**（**同窗登记或抽检链接**）；**(2)** **回归** **Enable** **`matrixStatus` / `SC-MCV1-05`**；**(3)** **观测** **`SC-OBS01`** **`toolId`/`skillId` 可 join**。

<a id="cc-526-progressive-order"></a>

#### 5.2.6 **渐进执行顺序**

**用途**：把 **[§5.2 主表](#cc-exec-remaining)** **落为** **固定轮次**；**本轮** **不** **改变** **DoD** **判据**，**仅** **降低** **派工遗漏**。P0/P1 **MR 粘贴稿** **见** **[§3.4](#cc-p0-mr-github-full)**、**[§3.2](#cc-p1-mr-paste-templates)**、**[§3.3](#cc-p1-mr-github-full)**；**首节短骨架** **[§5.2.5](#cc-p1-exec-mr-skeleton)**。

| 轮次 | 建议关单包 | 说明 |
|------|------------|------|
| **A** | **CC-P0-04** + **CC-P0-05** | **`billing` §10.6.1 / §10.3.1** **逐项** **+** **[§2.1](#cc-p0-signoff-register)** **回填** **后** **方** **允许** **PRD §13** **`D-12` / `D-5`·`D-7`** **`[x]`**。**MR 稿** **[§3.4](#cc-p0-mr-github-full)** |
| **B** | **CC-P0-03** + **CC-P0-01** | **§12.1 生产 baseUrl** **首填** **与** **三线登记表 B**；**(b) Hosted** **或** **(c) `release-*`** **与 (a) 同窗**（[`openapi/README`](../openapi/README.md)）。**MR 稿** **[§3.4](#cc-p0-mr-github-full)** |
| **C** | **CC-P0-02** | **矩阵延期格** **终裁** **或** **PATH 冻结**；**WS/listenKey** **OpenAPI·实现**；**须** **[§4](#cc-section4-matrix)** **+** **[§7](#cc-section7-template)** **（若解冻/变更延期）**。**MR 稿** **[§3.4](#cc-p0-mr-github-full)** |
| **D** | **P1 · MR-A～E** | **勿** **单 MR 堆满**；**首节** **§10 + §9** **+** **[§3.2](#cc-p1-mr-paste-templates)** / **[§5.2.5](#cc-p1-exec-mr-skeleton)**。**Telegram 全流程** **MR-C** **与** **文档已 `[x]`** **叙述** **区分**（见 **[§5.2.1](#cc-521-prd-map)**）。**MR 稿** **[§3.3](#cc-p1-mr-github-full)** |
| **E** | **§5.1 升格 gate** | **全部 P0** **+** **与 V1 相交 P1** **闭合后** **方** **审慎** **升格** **[`spec.md`](spec.md)** **或** **对外** **「生产契约已冻结」**。**自检** **[§5.1](#cc-stage4-spec-gate)** |

---

## 6. 已挂接入口一览（本版）

以下为 **本条**与仓库内规格的 **双向互引**；**新增入口**时 **本节**与本条 **脚注**一并维护。

| 文档 | 挂接要点 |
|------|-----------|
| [`spec.md`](spec.md)、[`README.md`](README.md)、[`../README.md`](../README.md)、[`../design/README.md`](../design/README.md) | 契约收口索引、**P1** **§3.1** **拆单** **+**  **[§3.2](#cc-p1-mr-paste-templates)** **+** **[§5.2.5](#cc-p1-exec-mr-skeleton)** **派工同屏** **+**  **[§3.3](#cc-p1-mr-github-full)** **+** **[§3.4 P0 全稿](#cc-p0-mr-github-full)**、**关单派工** **[§5.2](#cc-exec-remaining)**、**Status 升格** **§5.1**、设计侧入口 |
| [`admin-console/demo-routing.md`](admin-console/demo-routing.md)、[`src/admin/README.md`](../../src/admin/README.md) | **运营后台 Demo** **不** **提供** **契约收口索引页**；`/system/contract-closure` **仅** **重定向**（见 `demo-routing` **重定向表**）；派工与粘贴稿 **以** **本条** **§3.2～§3.4、§5.2.6** **为准** |
| [`product.md`](product.md) | 范围表一行 |
| [`domains/admin/management-console-v1-prd.md`](domains/admin/management-console-v1-prd.md) **§13** | **发布勾选**与 **§2～§5.1** 交叉引用；**§5.2.1** **PRD 映射**；**P0** **`D-5`/`D-7`/`D-12`** **证据** **[§2.1](#cc-p0-signoff-register)** |
| [`domains/agent/exchange-agent/trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md) §8.5 · 脚注 | **`FR-TS07`**、收口操作索引 |
| [`../design/api.md`](../design/api.md)、[`../design/architecture.md`](../design/architecture.md) | **矩阵 / MR**、**待补充**首条、`overview` **页脚** |
| [`flows/automation-alerts.md`](flows/automation-alerts.md)、[`flows/trade-via-agent.md`](flows/trade-via-agent.md)、[`flows/consume-and-bill.md`](flows/consume-and-bill.md) | **参与文档** |
| [`flows/README.md`](flows/README.md)、[`flows/activate-trading-agent.md`](flows/activate-trading-agent.md)、[`flows/wealth-via-agent.md`](flows/wealth-via-agent.md)、[`flows/read-analyze-and-search-via-agent.md`](flows/read-analyze-and-search-via-agent.md) | **索引 / 开通 / 理财 / B·C** **与收口互引** |
| [`domains/agent/exchange-agent/overview.md`](domains/agent/exchange-agent/overview.md) 表头 | **契约收口**行；脚注 |
| [`domains/admin/billing-management/overview.md`](domains/admin/billing-management/overview.md)、[`domains/admin/billing-management/rules.md`](domains/admin/billing-management/rules.md)、[`domains/admin/observability-management/overview.md`](domains/admin/observability-management/overview.md)、[`observability/overview.md`](observability/overview.md) | **CC-P0-03～05**、流水 **ledger 枚举**、**模块八 `design` 登记表**、**§4**、**`SC-OBS*`**（**含 `SC-OBS06` · `exchangeViewSource`**）邻域脚注；[`Runtime/reconciliation.md`](Runtime/reconciliation.md) **同窗** |
| [`domains/agent/agent-orchestration/runtime-freeze.md`](domains/agent/agent-orchestration/runtime-freeze.md) · [`routing-engine.md`](domains/agent/agent-orchestration/routing-engine.md) | **矩阵解冻**、**`scenarioId` 寄存器** **与** **`runtime-freeze` §3** **写路径最小编排** **对签**（**`routing-engine` 文首** **映射**） |
| [`domains/agent/agent-orchestration/implementation-alignment.md`](domains/agent/agent-orchestration/implementation-alignment.md) | **对客三闸 §13**、**评审 §6～§12**、**意图草案 §8～§9**、**eval 束 §13.3** — **与** **§1.2 / §9** **同窗** **不替代** |
| [`domains/agent/telegram/overview.md`](domains/agent/telegram/overview.md)、[`domains/agent/telegram/admin-bot-config.md`](domains/agent/telegram/admin-bot-config.md)、[`README.md`](domains/agent/telegram/README.md) | **§1§2.1.1§4、类型 A**；**§5 **`SC-CH-TG-FUT-01～03`**（**永续卡面/条件块 · 同窗 [`design/api.md`](../design/api.md) 矩阵备注、`trade-via-agent`）**；**控制台 Bot/Webhook `FR-TG-ADMIN-01～06`、`configKey §4`（含 **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN|ZH_TW|EN`** **与** **遗留键**）、`FR-MC709～711`**；**渠道 README 索引** |
| [`domains/admin/trading-agent-config/`](domains/admin/trading-agent-config/) **`keys/functions`** | **`TELEGRAM_*`、`CHANNEL_TELEGRAM`**；**附录 A §5.1** 同窗 |
| [`domains/agent/onboarding/overview.md`](domains/agent/onboarding/overview.md)、[`domains/agent/agent-context/overview.md`](domains/agent/agent-context/overview.md)、[`domains/admin/prompt-management/overview.md`](domains/admin/prompt-management/overview.md)、[`domains/admin/prompt-management/functions.md`](domains/admin/prompt-management/functions.md)、[`domains/admin/prompt-management/runtime-injection.md`](domains/admin/prompt-management/runtime-injection.md) | **§1 Deeplink/`FR-T05`** · **CC-P1-02**（**`tool.web.*`、上下文预算**）· **CC-P1-04**（**评审中（V1）** · **`functions` §2～§5 · `runtime-injection` · `observability` §2.3** · **OpenAPI B**） |
| [`domains/admin/tool-management/overview.md`](domains/admin/tool-management/overview.md)、[`domains/admin/tool-management/functions.md`](domains/admin/tool-management/functions.md) | **`SC-MCV1-05`**（**矩阵未冻结不得假开**）· **CC-P1-01～03**（**`toolId`/登记表 SSOT**；**闭链 MR** **[MR-E · §3.2](#cc-p1-mr-e)**）· **§4 矩阵解冻核对** |
| [`domains/admin/access-control/overview.md`](domains/admin/access-control/overview.md)、[`domains/admin/access-control/functions.md`](domains/admin/access-control/functions.md) | **模块六** · **I02 `code`**（**`AGENT_ROLLOUT_BLOCKED` 等**）· **`design/api` 登记表/待补充 · 用户摘要归因** |
| [`risk/README.md`](risk/README.md) **及** [`risk/kill-switch.md`](risk/kill-switch.md)、[`risk/exposure-limit.md`](risk/exposure-limit.md) 等 | **全局风险横切**；**与** **`trading-agent-config/keys`、`boundaries` §9、`Runtime/execution`、ADR-001** **对签**；**不替代** **域内 FR/SC** |
| [`risk/acceptance.md`](risk/acceptance.md) | **`SC-RISK-01～05`** **抽检口径**（**Kill / Pause / symbol·带 / `AGENT_*` / 高危审计**） |

---

<a id="cc-section7-template"></a>

## 7. 矩阵解冻 MR 登记模板（复制至 MR）

**MR 标题**：`feat(docs/spec): thaw design/api matrix — <能力简述>`

| 项 | 填写 |
|----|------|
| **矩阵格（或登记表行）** | `design/api.md` **锚文本 / 行间描述** |
| **OpenAPI** | Spec URL 或 **`openapi.yaml` 提交/tag** |
| **`design/api` 脚注** | **新版本号** · **本条变更一句** |
| **§4 核对清单**（勾选） | `trade-assistance §8`、`trade-assistance §2.5`、`exchange-agent`、`telegram` **类型 A**、**`telegram/admin-bot-config` / `design/api` Telegram 登记表行、`keys` §4**、`design/api` **「REST ↔ WebSocket 对账」**、`Runtime/reconciliation` **§3**、`observability` **`toolId`/`skillId`/§2.3**、**§2.2/`exchangeViewSource`/`SC-OBS06`**、**§2.4/`SC-OBS08`（若涉主态递进）**、`flows/trade-via-agent`、`flows/automation-alerts`、**`risk/*`/`risk/acceptance`（`SC-RISK*`）/`keys` §1～§3 与 `boundaries` §9** |
| **关联合 PR** | 若有 **实现**并行 PR — **链接** |

---

## 8. 文档侧推进记录（便于跟踪；**非** **豁免 P0 OpenAPI**）

**收尾口径**：**本文** **§8** **仅** **记录** **可在** **Markdown** **内** **完成的** **对齐**（ADR、表行、链、阶段标签）。**P0-01～04** **全文关闭**、**P1-04/06** **「全流程 DoD」** **仍** **以** **所内 OpenAPI + Owner +（若需）实现** **为准** — **见** **§2～§3** **主表**。

**MR 合并描述 / 登记**：**[`closure-remaining.md` §0](closure-remaining.md)**（`contract-closure` **锚点速链表**）— **§6.4** **问题→首节动作**、**§6** **执行视图** **与** **§6.1** **所内必填列** **[`closure-remaining` §6～§6.4](closure-remaining.md#cc-exec-solve-path)** — **§7** **开放项总表**、**§7.1** **走读缺口粘贴**、**§7.5** **闭环路径**、**§7.6** **MR 执行清单**、**§7.2～§7.4** **Prompt/Runtime 派工 · 闭环互引 · AC-09 检核** — **与** **本条** **§2～§3** **主表** **同窗** **粘贴** **可** **减少** **漏链** **§**。**残余 OP / AC-09 一行登记** → **[§8.1 `#cc-section8-residual-paste`](#cc-section8-residual-paste)**。

<a id="cc-section8-residual-paste"></a>

### 8.1 残余开放项 · 可复制登记（**与** **`closure-remaining`** **§7.5～§7.6**）

**用途**：[`closure-remaining` §7.5～§7.6](closure-remaining.md#cc-remaining-open-close-path) **已经把 **OP-\*** **、** AC-09 **收口到单行判据**。**本节只提供：** **`§8` 表 「说明」列** **或 MR 描述** **可整段复制的字**。**不豁免** **§2～§3** **DoD**；宣称对客能力时 **亦须** **[§9 六款自检](#cc-section9-six)**。

| 场景 | **`§8`「说明」/ MR「登记」可复制草稿** |
|------|----------------------------------------|
| **AC-09q / OP-09Q · 仅 GitHub Actions** | **`CI：仅 GHA`。registry ↔ routing：** 跑 `python3 specs/requirements/prompts/library/scripts/check_registry_vs_routing_engine.py`，exit=0 由 [.github/workflows/prompt-registry-consistency.yml](../../.github/workflows/prompt-registry-consistency.yml) **`pull_request` 门禁保证**；[**`closure-remaining` §7.4～§7.6**](closure-remaining.md#cc-ac09-closure-matrix) · **OP-09Q** **勾选 N/A。** |
| **AC-09q / OP-09Q · 另有非 GitHub 门禁** | **`<宿主名>`** **流水线：** `python3 specs/requirements/prompts/library/scripts/check_registry_vs_routing_engine.py` **（exit=0）；与** [`closure-remaining` §7.4](closure-remaining.md#cc-ac09-closure-matrix) **右列同窗。** |
| **Timeline · OP-TML** | 默认 **执行级 V1**：`promptPackVersion` 口径见 [`observability` §2.3.1](observability/overview.md)；**未立项**事件级。**索引：** [**§7.5 · OP-TML**](closure-remaining.md#cc-remaining-open-close-path)**。 |
| **OP-AvB · 本轮仅 A** | 本轮为 **A（文档对齐）**，**不宣称对客 B**。若 MR 不含 B 阶段，则不承诺 **Hosted/生产实测**，亦不附 **[§9 六款](#cc-section9-six)** **勾选**。** **见** [**§7.5 · OP-AvB**](closure-remaining.md#cc-remaining-open-close-path)**。 |
| **残余总索引** | [**§6.4**](closure-remaining.md#cc-problem-to-action) **·** [**§6.1**](closure-remaining.md#cc-remaining-61) **·** [**§7.5**](closure-remaining.md#cc-remaining-open-close-path) **·** [**§7.6**](closure-remaining.md#cc-closure-exec-checklist) |

---

| 日期 | 项 | 说明 |
|------|-----|------|
| 2026-05-20 | **`product.md` §非目标 · 现货 OCO/bracket** | 本阶段 Exchange Agent **不交付** **`trade.spot.oco` / `trade.spot.bracket`** **`call_exchange_write`**；**同窗** **CC-P1-01 · MR-D 分支 C** · **`trade-via-agent`** · **`telegram/overview`** · **`agent-coobit-api-allowlist` §3**。**`contract-closure` **文档版本** **0.2.30** |
| 2026-05-18 | **`§8.1`** **残余可复制登记** **`OP-09Q`/Timeline/AvB** | **锚** **[`#cc-section8-residual-paste`](#cc-section8-residual-paste)** **`↔`** **[`closure-remaining`§7.5～§7.6](closure-remaining.md#cc-remaining-open-close-path)** **— **文档版本** **0.2.19** |
| 2026-05-18 | **`closure-remaining` §6.4 ↔ 本条闭环互链** | **文首** / **§8 MR 登记** / **§8.1 残余总索引** **`#cc-problem-to-action`** — **文档版本** **0.2.20** |
| 2026-05-18 | **`§0～§6.4` 残余入口同窗（首批 `contract-closure` 引文补链）** | **`Runtime/*`、`flows`、`exchange-agent`、`integrations/exchange`、`risk`、`observability/tracing`、`tools`、`prompts/system`、`standards`、`admin/*/functions｜rules｜flow`、`billing-management/README`、`retry-policy`、`activation`** 等 **`##` 节前一行** **`closure-remaining` §0·§6·§6.4** — **文档版本** **0.2.27** |
| 2026-05-18 | **`closure-remaining` 未完语义 SSOT** | **`#cc-unfinished-semantics`** **三类「未完」**；**§0 速链表增量**；**`contract-closure` / `LITE-MODE` 文首同窗** — **文档版本** **0.2.29** |
| 2026-05-18 | **`specs/design` · `openapi/OWNERS` · `src/admin` · §0·§6.4** | **`canonical-trading-model`/`deployment`/`runtime-architecture`/`sub-account-isolation`/`tool-calling-sequence`；`adr/README` + ADR-002～004；`OWNERS` 索引行；`src/admin/README`** — **文档版本** **0.2.28** |
| 2026-05-18 | **`telegram/overview` · `agent-context` · `management-console-v1-prd` · §0·§6.4** | **`telegram/overview`** **篇首** **`contract-closure`/`closure-remaining`** **速链**；**`agent-context`** **SSOT 表 `CC-P1-02`** **行**；**`management-console-v1-prd`** **篇首互引** — **文档版本** **0.2.26** |
| 2026-05-18 | **`onboarding`/`telegram`/admin-console · §0 同窗** | **`onboarding/overview` §5、`boundaries`**；**`telegram/README`**；**`admin-console` README / PRD IA / demo-routing** — **文档版本** **0.2.25** |
| 2026-05-18 | **`access-control`/`trading-agent-config`/`web`/评审规范 · §0 同窗** | **`domains/web/overview` §4·§5**；**`review-and-change-standard` §2** — **文档版本** **0.2.24** |
| 2026-05-18 | **`standards`/后台域 overview · §0·§6 同窗** | **`standards/README`；`prompt-management`/`tool-management`/`observability-management`/`agent-management`/`ai-settings`/`billing` — **文档版本** **0.2.23** |
| 2026-05-18 | **`prompts`/`flows`/`Runtime`/`observability`/`agent` 树 · §0 同窗** | **README / overview** **`closure-remaining` §0 · §6** — **文档版本** **0.2.22** |
| 2026-05-18 | **`contract-closure` 文首 + 邻域 §0 同窗** | **`closure-remaining` `§0`** **`#closure-remaining-quicklinks`；**`business`/`metrics`/`integrations`/`risk`/ **`implementation-alignment`** — **文档版本** **0.2.21** |
| 2026-05-14 | **`domains/README` · `e2e` 同窗** | **[`requirements/domains/README`](domains/README.md)** **篇首** **`e2e`↔`architecture` §对照** — **文档版本** **0.2.11** |
| 2026-05-14 | **`integrations/README` · `specs/README` · `e2e` 同窗** | **[`integrations/README`](integrations/README.md)** **篇首 + `exchange/`** **表行**；**[`specs/README`](../README.md)** **`design/`** **列** — **`e2e`↔`architecture` §对照** — **文档版本** **0.2.10** |
| 2026-05-14 | **`design/overview` · `integrations/exchange/overview` · `e2e` 同窗** | **[`design/overview`](../design/overview.md)** **入口列表**；**[`integrations/exchange/overview`](integrations/exchange/overview.md)** **篇首** — **`e2e`↔`architecture` §对照** — **文档版本** **0.2.9** |
| 2026-05-14 | **`product/README` · `overview` · `requirements-review` · `e2e` 同窗** | **[`README`](../../../product/README.md)** **文档地图/阅读顺序**；**[`overview`](../../../product/overview.md)** **鸟瞰段**；**[`requirements-review`](../../../product/requirements-review.md)** **§1（§4c）·§2（主路径议题表）** — **`e2e`↔`architecture` §对照** — **文档版本** **0.2.8** |
| 2026-05-14 | **`flows/*.md` + `product/flows` · 文首 `e2e`↔`architecture`** | **`trade-via-agent`** **及** **`consume-and-bill`/`activate-trading-agent`/`wealth-via-agent`/`read-analyze*`/`automation-alerts`** **摘要表补行**；**[`product/flows.md`](../../../product/flows.md)** **技术鸟瞰** — **文档版本** **0.2.7** |
| 2026-05-14 | **`spec`/根 README/`release-notes`/`closure` §7.1 · `e2e` 同窗收口** | **`spec.md`** **域段 `e2e`** **链** **`architecture` §对照**；**根 [`README`](../../../README.md)** **`flow/`** **树 + 必读**；**[`release-notes`](../../../product/release-notes.md)** **「已发布版本」历史 HTML 脚注**；**[`roadmap` TL;DR](../../../product/roadmap.md)**；**[`requirements-spec-human` §2](../../../product/requirements-spec-human.md)**；**[`closure-remaining` §7.1](closure-remaining.md#cc-remaining-gap-paste)** — **0.2.12** — **文档版本** **0.2.6** |
| 2026-05-14 | **`architecture` 架构语言 · `e2e` v1.5.7** | **`architecture.md`** **「与通用 Agent 栈之对照」**；**`product/`**、**`spec.md`**、**`design/adr/README`**、**`requirements-review`** **同窗索引**；**`flow/e2e-closed-loop.{md,html}`** **文首摘要行** **+** **HTML meta/footer** — **HTML v1.5.7** — **文档版本** **0.2.5** |
| 2026-05-14 | **`requirements-review` / `LITE-MODE` · ADR-004 评审链** | **[`§7.5` ADR-004 速查](../../../product/requirements-review.md#cc-adr004-review-checklist)**、`LITE-MODE` §1 **规格仓边界**、`closure-remaining` §0 **增** **CC-P1-07 速链**、`requirements/README` **product.md 备注** — **文档版本** **0.2.4** |
| 2026-05-14 | **`contract-closure` · 规格仓边界（不维护 Execution Gateway 代码）** | **移除** **`src/execution-gateway`**；**CC-P1-07** **文档与设计** **仍** **以** **canonical-trading-model / ADR-004** **为准**；**DoD B** **仅在** **所内工程/Runtime 仓库** **验收** — **文档版本** **0.2.3** |
| 2026-05-14 | **ADR-004 · Canonical Trading Model · CC-P1-07（文档 A）** | **[`canonical-trading-model.md`](../design/canonical-trading-model.md)**、**[`ADR-004`](../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)**、**[`architecture.md`](../design/architecture.md)** Gateway/Adapter、**[`trade-assistance`](domains/agent/exchange-agent/trade-assistance.md) §2.6**、**[`integrations/exchange/overview`](integrations/exchange/overview.md)** 表行、**§3 · CC-P1-07** — **Execution Gateway 实现对拍 = 后续 MR（DoD B）** — **文档版本** **0.2.0** |
| 2026-05-24 | **`requirements/README` + `e2e`** | **推荐阅读第 4 条**补 **`spec`** / **`exchange-agent/README`**（openapi-ai 同窗）；**`e2e-closed-loop` 文首**链 **`spec`**；**HTML v1.5.6** — **文档版本** **0.1.99** |
| 2026-05-23 | **`spec.md` + `exchange-agent/README`** | **域段落**同窗 openapi-ai、`integrations`、`design/api`、allowlist；**`exchange-agent/README` 篇首宿主** — **文档版本** **0.1.98** |
| 2026-05-22 | **`exchange-agent` + `agent/` + 编排总览** | **`exchange-agent/overview`** 篇首私网宿主；**`domains/agent/README`** 一行；**`agent-orchestration/overview`** **`openapi-ai` 同窗**；**`web/agent-onboarding` §1 句读** — **文档版本** **0.1.97** |
| 2026-05-21 | **`domains/web` + 编排篇首同窗** | **`domains/web/overview` 对上 Coobit（配置页）、`runtime-freeze`/`routing-engine` 篇首** — **`openapi-ai`/`integrations`/allowlist/矩阵同窗** — **文档版本** **0.1.96** |
| 2026-05-20 | **Web 绑定页 · 确认流 · permission** | **`agent-onboarding` §1、`permission-authorization` 篇首、`confirmation-flow` 互引下** — **`openapi-ai`/`integrations`/`allowlist` 同窗** — **文档版本** **0.1.95** |
| 2026-05-19 | **开通 / `Runtime/execution` · 绑定探测同窗** | **`activate-trading-agent`**；**`onboarding/overview` §1.1**；**`initialization-flow` §1.2**；**`Runtime/execution` §1 步 7** — **`openapi-ai` + `integrations/exchange` + allowlist** — **文档版本** **0.1.94** |
| 2026-05-18 | **`flows/` + `e2e` · openapi-ai 同窗** | **`trade-via-agent`/`consume-and-bill`/`wealth*`/`read-analyze*`/`automation-alerts`/`flows/README`、`flow/e2e-closed-loop.{md,html}`** **链** **`integrations/exchange/overview` + allowlist** — **文档版本** **0.1.93** |
| 2026-05-17 | **宿主 vs 契约 · 索引 + 检阅** | **`product/README`** **地图/读序**；**`LITE-MODE` §1 原则**；**`integrations/README` exchange 行** **「默认」措辞**；**`implementation-alignment` §6** **首勾** **pin+allowlist** — **文档版本** **0.1.92** |
| 2026-05-16 | **Coobit · `openapi-ai` 宿主 vs OpenAPI 契约** | **`product.md` 方向 / 术语 / 非目标** **同窗** **[`integrations/exchange/overview`](integrations/exchange/overview.md)**、**[`design/api.md`](../design/api.md) 边界**、**[`closure-remaining` §3·§7](closure-remaining.md)**、**[`spec.md`](spec.md) 索引**；**不新开 CC** — **实现 pin / 制品 URL** **仍** **所内 MR** — **文档版本** **0.1.91** |
| 2026-05-14 | **主交易流 · Truth Map · 任务调度 · `spec` · §7.1** | **`trade-via-agent` 文首表**；**`runtime-truth-source-map` §1** **§7.1**；**`state-machine` / `task-scheduler`**；**`spec.md` §7.1**；**`closure-remaining` 0.2.9**；**`release-notes` 2026-05-14** **补子项** — **文档版本** **0.1.90** |
| 2026-05-14 | **编排 / Runtime / `flows` 入口 · §7.1** | **`agent-orchestration` overview**、**`Runtime` overview**、**`planner-contract`**、**`goal-and-execution-paths`**、**`flows/README`**、**`domains/agent/README`**、**§8 MR 登记** **同窗** **§7 / §7.1** — **文档版本** **0.1.89** |
| 2026-05-14 | **`closure-remaining` §7.1** · **编排域互链** | **走读缺口粘贴** **`#cc-remaining-gap-paste`**；**`runtime-freeze` / `routing-engine` / `prompts` / roadmap / `e2e`** **同窗** — **文档版本** **0.1.88** |
| 2026-05-14 | **`closure-remaining` §7** **· 文首互链** | **剩余开放项** **一页总表** **`#cc-remaining-open-items`**；**`LITE` / `implementation-alignment` / `runtime-truth` / JV-07** **同窗** — **文档版本** **0.1.87** |
| 2026-05-14 | **§3.3 / §3.4 MR 稿 · 索引导读** | **六款** **勾选** **第 4 条** **显式** **`runtime-freeze` §3** **+** **`routing-engine` 文首**；**`README` / `domains/README` / `closure-remaining`** **补** **闸 1 ↔ §3** — **文档版本** **0.1.86** |
| 2026-05-14 | **§1.2 分工句 · 三闸闸 1** | **与** **文首** **`runtime-freeze` §3** **口径** **同窗**：**§13** **三闸摘要** **闸 1** **补全** **为** **寄存器 + §8 + §3** — **文档版本** **0.1.85** |
| 2026-05-14 | **文首三闸 · §9 §13.1 · `LITE-MODE`** | **显式** **闸 1** **→** **`runtime-freeze` §3** **（** **`implementation-alignment` v1.2.12** **）** — **文档版本** **0.1.84** |
| 2026-05-14 | **§1.2 款 4 · §3 CC-P1-01 · §9 款 4 · §6** | **链** **`runtime-freeze` §3.1～§3.11** **与** **`routing-engine` 写键对照**；**MR-D** **解冻** **补** **§3.8～§3.9** — **文档版本** **0.1.83** |
| 2026-05-14 | **§1.2 加码 · `observability` §2.4 / `SC-OBS08`** | **主态递进** **关单** **建议** **附** **时间线对签**；**§7** **核对** **补** **`§2.4`/`SC-OBS08`** — **文档版本** **0.1.81** |
| 2026-05-14 | **§10 · `LITE-MODE` + §13.1 写入步 2** | **五步** **节前** **说明** **小团队** **同窗** **§2 第五块**；**步 2** **嵌入** **`release-notes` 等价** **与** **三闸点检** — **文档版本** **0.1.80** |
| 2026-05-14 | **文首 + §1.2 + §6 链 `implementation-alignment` §13** | **对客「已支持」三闸** **口语化索引**（**不替代** **§1.2 / §9**）；**分工句** **入库** **§1.2 款 6 下** — **文档版本** **0.1.79** |
| 2026-05-11 | **用户触点分界（Billing 站内 vs onboarding 外置）** | **文首** **互链** [`product.md`](product.md) **触点分界**；**`product/`、`domains/web/`、`spec.md`、`requirements/README`** **同窗**；**勿将 CC-P0-03（账务三线 OpenAPI）误读为账单 UI 迁出交易所** — **文档版本** **0.1.78** |
| 2026-05-11 | **§2～§3「缺口」列校准 · CC-P0-03 / P1-04 / P1-06** | **对齐仓库现状**：账务/Prompt/Telegram **YAML 已链** **≠** **生产 DoD 已闭**；**执行顺序** **见** **[`closure-remaining` §6](closure-remaining.md#cc-exec-solve-path)** — **文档版本** **0.1.77** |
| 2026-05-11 | **`telegram/overview` §2.5 · 类型 A（收口措辞）** | **§1.2 款 3** **与** **§9 自检表款 3** **显式分层**：**类型 A · §2.5.x** **vs** **总则 §2～§2.6** — **文档版本** **0.1.76** |
| 2026-05-11 | **Telegram · 合约 SC 收口索引** | **`SC-CH-TG-FUT-01～03`** **登记** **[`design/api.md`](../design/api.md)** **（Telegram 交界表 · 矩阵「合约」「自动化」· 验收行）** **与** **本条 §1.2 款 3、§6 Telegram 行** — **文档版本** **0.1.75** |
| 2026-05-09 | **小团队 · LITE-MODE 管控** | **[`LITE-MODE.md`](LITE-MODE.md)** **日常默认**；**`contract-closure`** **全文** **降权为 Optional**；[`product/release-notes.md`](../../product/release-notes.md) **发版半页纸** — **文档版本** **0.1.74** |
| 2026-05-09 | **admin Demo · 移除契约收口索引页** | **删除** `src/admin` **`ContractClosureOpsPage`** **与** **`contractClosureRound*`**；`/system/contract-closure` → **`/runtime/executions`**；**§5.2.6 / §6** **与** `admin-console` **三表** **去** **`sys.contract-closure`**；[`product/requirements-review`](../../product/requirements-review.md) **§8** — **文档版本** **0.1.73** |
| 2026-05-15 | **MR-5 · `product.md` 已定稿（需求阶段）** | **[`product.md`](product.md)** **篇首状态**；[`spec.md`](spec.md) **`product` 已定稿 ≠ 本条 Draft**；[`business/README.md`](business/README.md) **索引行** — **文档版本** **0.1.72** |
| 2026-05-15 | **MR-5 预备 · README §3.0 + product 定稿门槛** | **[`requirements/README` 推荐阅读 §3.0](README.md#推荐阅读顺序)**；**[`product.md`](product.md)** **定稿门槛**；[`product/requirements-review.md`](../../product/requirements-review.md) **§7** **自检表** — **文档版本** **0.1.71** |
| 2026-05-09 | **MR-3/4 · C 类启用态 + P1 文档/B 分期** | **ADR-003** **决策 6**；[`tool-management-schemas`](../openapi/components/tool-management-schemas.yaml) **`enabledOperational`/`legalReviewTicketId`**；[`trade-assistance` §8.4](domains/agent/exchange-agent/trade-assistance.md)；**§3.0** **[`#cc-p1-doc-vs-b`](#cc-p1-doc-vs-b)** **+** **CC-P1-02 / MR-A** — **文档版本** **0.1.70** |
| 2026-05-09 | **干系人纪要 · billing 配置化 + product 对客分层** | **[`product/requirements-review`](../../product/requirements-review.md) §6** **MR 拆单**；**[`billing.md`](domains/admin/billing-management/overview.md) v0.2.15** — **§12.1** **baseUrl 配置文件**、**§10.6.1** **范式 C · UID**；**[`product.md`](product.md)** **对客准入 vs 契约闭环** — **文档版本** **0.1.69** |
| 2026-05-09 | **轮次 E++ · product 交叉引用 + §8 行模板** | **`PRODUCT_MD_ELEVATION_CROSSREF`** / **`CONTRACT_CLOSURE_SECTION8_ROW_TEMPLATE`** / **`buildRoundEGateAuxiliaryPackPaste`** — **文档版本** **0.1.68** |
| 2026-05-09 | **轮次 E+ · spec.md Status diff 范例** | **`SPEC_MD_STATUS_DIFF_EXAMPLE`** / **`buildRoundEGateWithSpecDiffPaste`** — **文档版本** **0.1.67** |
| 2026-05-09 | **轮次 E Demo · §5.1 升格 gate 自检** | **`contractClosureRoundEGatePaste`**；**§5.2.6** **行** **E** — **文档版本** **0.1.66** |
| 2026-05-09 | **轮次 D Demo · P1 MR-A～E 预填** | **`contractClosureRoundDMrPaste`** / **`P1_MR_PASTES`**；**§5.2.6** **行** **D** — **文档版本** **0.1.65** |
| 2026-05-09 | **轮次 C Demo · P0-02 MR 预填** | **`contractClosureRoundCMrPaste`**（矩阵/WS）；**§5.2.6** **行** **C** — **文档版本** **0.1.64** |
| 2026-05-09 | **轮次 B Demo · P0-03+01 MR 预填** | **`contractClosureRoundBMrPaste`**；**§5.2.6** **行** **B** — **文档版本** **0.1.63** |
| 2026-05-09 | **轮次 A Demo · P0-04+05 MR 预填粘贴** | **`ContractClosureOpsPage`** **+** **`contractClosureRoundAMrPaste.ts`**；**§5.2.6** **行** **A** **补** **Demo** — **文档版本** **0.1.62** |
| 2026-05-09 | **§5.2.6 + admin `sys.contract-closure` 全表** | **渐进执行顺序** **[#cc-526-progressive-order](#cc-526-progressive-order)**；**Demo 页同窗** **§5.2 P0/P1** — **文档版本** **0.1.61** |
| 2026-05-09 | **admin Demo · README 根索引 + vitest D-5** | **仓库根** [`README.md`](../../README.md) **链** **`src/admin`**；**`vitest`** **`observabilityDeepLink`** **单测**；**§6** **补** **`src/admin/README.md`** — **文档版本** **0.1.60** |
| 2026-05-09 | **admin Demo · 实轨页 + D-5 深链** | **`ContractClosureOpsPage`** **`/system/contract-closure`**；**`traceKey` URL 别名**；**`admin-console` 三表** — **文档版本** **0.1.59** |
| 2026-05-09 | **§5.2.1 · 锚 `cc-521-prd-map` + PRD §13 子弹** | **`requirements/README` 17**；**PRD §13** **`SC-MCV1-05`/`CC-P1-03`** **可勾选项** — **文档版本** **0.1.58** |
| 2026-05-09 | **§5.2.1 · CC-P1-03** **+** **`#cc-p1-mr-e`** | **PRD §6/§13** **叙事映射**；**`tool-management/overview`** **互链** **MR-E** — **文档版本** **0.1.57** |
| 2026-05-09 | **MR-E · CC-P1-03 组织轨** | **§3.1/§3.2/§3.3/§5.2.5** **补** **工具技能 SSOT·幂等 MR**；**§5.2.4** **标题前缀** — **文档版本** **0.1.56** |
| 2026-05-09 | **索引互链 · §5.2.5** | **`requirements/README`** **推荐阅读 16**；**`spec`/`product`** **契约索引** **补** **派工同屏**；**§3.2** **同窗修订纪律** — **文档版本** **0.1.55** |
| 2026-05-09 | **§5.2.5 · P1 MR-A～D 派工短骨架** | **`#cc-p1-exec-mr-skeleton`** **—** **与** **[§3.2](#cc-p1-mr-paste-templates)** **同窗镜像**；**§5.2** **主表** **同屏** **首节粘贴** — **文档版本** **0.1.54** |
| 2026-05-09 | **§3.4 · P0 MR GitHub 稿** | **[§3.4](#cc-p0-mr-github-full)** **`#cc-p0-mr-github-full`** — **P0-01～05** **复制模板**；**同窗** **§5.2** **首包**；**文档版本** **0.1.53** |
| 2026-05-09 | **§5.2 · 关单派工矩阵** | **[§5.2](#cc-exec-remaining)** **P0/P1** **逐 MR 回填索引**；**文档版本** **0.1.51** |
| 2026-05-09 | **§5.2 · 子节补齐** | **5.2.1** **PRD §13 映射** · **5.2.2** **锚点速查** · **5.2.3** **合入纪律**（**§4/§7/§9/§10** **显式 id**）· **5.2.4** **MR 标题前缀** — **文档版本** **0.1.52** |
| 2026-05-09 | **P0 · §2.1 会签证据登记** | **[§2.1](#cc-p0-signoff-register)** **`CC-P0-04`/`CC-P0-05`** **回填表** — **PRD §13** **`[x]`** **须** **与本表** **同窗**；**文档版本** **0.1.50** |
| 2026-05-09 | **`contract-closure` 文档版本** | **0.1.49** **（§3.3 互链）** **→** **0.1.50** **（§2.1 P0 会签表）**；**见** **顶行** |
| 2026-05-12 | **P1 · §3.3 GitHub MR 全稿** | **[§3.3](#cc-p1-mr-github-full)** **` ```markdown `** **块** — **§10/§9 勾选 + MR-A～D 差异行**；**§3.2** **链入** |
| 2026-05-11 | **P1 · §3.2 MR-A～D 粘贴稿** | **[§3.2](#cc-p1-mr-paste-templates)** **入库** **组织轨模板**（**与** **§3.1** **拆单一一对应**）；**§6** **索引导航** **+** **`requirements/README`** **推荐阅读** **补链** |
| 2026-05-10 | **P0 继续 · `components` 同窗 + PRD §13 `D-12`** | **`specs/openapi/components/*.yaml`** **全部 `info.version` → `2026-05-09`**，**与** **19 根业务 spec** **及** **`billing-schemas.yaml`** **同窗**；**[`management-console-v1-prd` §13](domains/admin/management-console-v1-prd.md)** **已增** **`D-12`/`CC-P0-04`** **发布 `[ ]`**；**[`openapi/README` Hosted 段](../openapi/README.md)** **CC-P0-01 文案** **含** **`components` 全量** |
| 2026-05-09 | **P0 收关 · 文档轨批次（五条）** | **`specs/openapi`** **19 根业务 YAML + `billing-schemas.yaml` `info.version` → `2026-05-09`**；**`design/api.md` 登记表第三列** **同窗** **· 脚注 v0.1.52**；**`openapi/README` Hosted 段** **补** **CC-P0-01 文档轨索引**；**CC-P0-02** **`design/api` 矩阵节后** **增** **WS/listenKey 与 `user-private-ws` 同窗句**；**CC-P0-03～05** **`billing.md` §12.1 生产登记模板**、**§10.6.1 财务会签项**、**§10.3.1 PRD §13 勾选纪律**；**§2 主表** **五条 P0 DoD** **追记** **本批次** — **不豁免** **财务首填 / 生产网关 / 实现勾选** |
| 2026-05-09 | **CC-P0-01（文档子集）** | **(a)** **仓库内可审 Spec** **与** **登记表版本列** **已对齐**；**(b)(c) Hosted、`release-*`** **仍须** **所内 MR** |
| 2026-05-09 | **CC-P0-02（文档子集）** | **矩阵 B `coobit-*` + WebSocket 登记行** **`info.version` 2026-05-09**；**延期格 B 阶段** **仍须** **PATH 或实现 MR** |
| 2026-05-09 | **CC-P0-03～05（模板）** | **`billing.md` §12.1 / §10.6.1 / §10.3.1** **增** **关单用登记与会签模板** — **生产/工单** **仍须** **首填** |
| 2026-05-08 | **B · onboarding + listenKey** | **`onboarding-schemas.yaml` + `user/onboarding.yaml`**（**me/agent/status、bindings、provisioning/confirm、recovery/deeplink**）；**`stream-schemas.yaml` + `user-private-ws`**（**`/sapi/v1/userDataStream` POST/PUT/DELETE**） |
| 2026-05-08 | **B · 子账户 exchange 矩阵** | **`exchange-schemas.yaml`（`CoobitJsonValue`）**；**扩写** **`coobit-spot`、`coobit-public`、`coobit-margin`、`coobit-futures`、`coobit-wealth`、`coobit-automation`** — PATH 同窗 **`design/api` 矩阵 + REST↔WS 对账** |
| 2026-05-08 | **B · 模块三 Tool** | **`tool-management-schemas.yaml`** + **`admin/tool-management.yaml`**（**`registry`、`schema`、`policy` PUT/PATCH、`enable`/`disable`、`observability-link`**）；**`$ref` `billing-schemas` Problem** |
| 2026-05-08 | **B · 模块四 AI + 模块二 Prompt** | **`ai-settings-schemas.yaml`** + **`admin/ai-settings.yaml`**（**providers、models、defaults、health-policy、health 200/202**）；**`prompt-management-schemas.yaml`** + **`prompt-management`**（**CRUD/publish/rollback/few-shots/sandbox、`GET /internal/prompts/effective`**） |
| 2026-05-08 | **B · Telegram + 用户/bundle** | **`telegram-channels-schemas.yaml`** + **`admin/telegram-channels.yaml`**（**GET/PATCH bot**、**GET/POST/DELETE webhook**、**self-test 200/202**）；**`users-global-config-schemas.yaml`** + **`users-global-config`**（**`agent-summary`、bundle `PATCH`**）；**`$ref` `billing-schemas` Problem/AsyncTaskAccepted** |
| 2026-05-08 | **B · 模块八 观测** | **`observability-schemas.yaml`**（**`InvocationState`、时间线 / 搜索 / 工具调用 / LLM 摘要、`$ref` `billing-schemas`**）；**`admin/observability.yaml`** **PATH**（**`/timeline`、`/search`、`/tool-calls`、`/llm`、`/audit-exports`**） |
| 2026-05-08 | **B · 模块六 准入信封** | **`access-control-schemas.yaml`**（**`EligibilityEnvelope` §4、`$ref` §7.1**）；**`admin/access-control.yaml` 全 PATH** + **`POST .../eligibility/evaluate`** |
| 2026-05-08 | **B · 模块一 I02 enum** | **`components/agent-management-schemas.yaml`**：**§7.1** **15** **`code`**、`AgentBatchRuntimeResult`；**`admin/agent-management.yaml` 全 PATH** |
| 2026-05-08 | **B · 账务同窗 schema** | **`components/billing-schemas.yaml`** **+** 扩写 **`admin/billing-admin`/`internal/billing-token`/`user/billing-me`**（**`$ref`、分页、FR-MC501～508 / FR-B12～B16**）；**OWNERS.md** **花名表** |
| 2026-05-08 | **`specs/openapi` B** | **`specs/openapi/**/*.yaml`** **首登** **+** **`api.md` 登记表** **链** **`info.version`/MR 短 SHA**；**`design/README` 索引** · **Owner** **仍为** **角色占位** **（花名 MR 回填）** |
| 2026-05-08 | **`design/api` 登记表 B** | **「填链占位」** 小节 **+** 各业务行 **Spec / 版本 / Owner `TBD` 模板**；**修复**「待补充」**blockquote** **与首条列表粘连** |
| 2026-05-07 | **CC-P1-03** | **ADR-002** [`design/adr/002-tool-skill-registry-ssot.md`](../design/adr/002-tool-skill-registry-ssot.md) |
| 2026-05-07 | **CC-P1-02** | **ADR-003** [`design/adr/003-external-tools-compliance-and-budget.md`](../design/adr/003-external-tools-compliance-and-budget.md) |
| 2026-05-07 | **CC-P1-01** | **`trade-assistance` §4/§8.2** **增** **`skill.spot.oco` / `skill.spot.bracket`**（**draft**）；**`design/api` 矩阵** **已增** **书面延期行（2026-05-09）**；**现货 OCO/bracket PATH** **冻结** **仍待** **矩阵 MR** |
| 2026-05-07 | **`routing-engine`** | **`research.sentiment_and_news`、稳定化 `monitoring.event_trigger`** **措辞** |
| 2026-05-07 | **CC-P1-05** | **`architecture.md`** **已有** **C4 语境/容器** — **狭义「缺图」** **降级** **为可选增强** |
| 2026-05-07 | **CC-P0-05** | **`config §11`** **补** **D-5/D-7** **→** **`billing` §10.3** |
| 2026-05-08 | **CC-P1-04（文档）** | **`prompt-management`** **头表** **标** **「评审中（V1）」**；**§3 P1-04** **DoD** **拆** **A/B** |
| 2026-05-08 | **CC-P1-06（文档）** | **明确** **A** **=** **`design/api` Telegram 专节 PATH 示意** **已齐**；**B** **= Spec/Owner** |
| 2026-05-08 | **索引** | **`spec.md` / `requirements/README` / `design/api`「待补充」** **链** **§8** |
| 2026-05-09 | **B · Owner 模板 + 矩阵 OCO** | **[`OWNERS.md`](../openapi/OWNERS.md)** **职能 DRI「待指派」** **同窗** **`design/api` 登记表**；**子账户矩阵** **补** **OCO/bracket** **书面延期（CC-P1-01）**；**`billing.md`** **§10.3 闭合陈述、§10.6 D-12、§12 OpenAPI**；**`requirements/README.md`** **§ MR 纪律**；**§13** **Telegram** **文档/仓库 B 子集** **勾选** |
| 2026-05-09 | **CC-P1-01 · `routing-engine`** | **§2** **增** **`trade.spot.oco` / `trade.spot.bracket`** **与** **`trade.spot.limit_order`** **路由分居**；**同窗** **`trade-assistance` §8.2 脚注** |
| 2026-05-10 | **trade-via-agent · OCO/bracket** | **专节 · 现货限价** **编排表** **+** **S12 交界** **链** **`routing-engine` §2** |
| 2026-05-10 | **CC-P1-02 · OpenAPI** | **`tool-management-schemas`** **`ToolRegistryEntry.externalToolCompliance`** |
| 2026-05-10 | **CC-P1-04 · `functions` §1.4** | **Prompt** **全流程 DoD** **核对表** |
| 2026-05-10 | **`orchestration/overview` §6** | **OCO/bracket** **承诺边界** |
| 2026-05-11 | **CC-P0-03 · billing OpenAPI** | **`billing-schemas`** **`traceKey`/`revenueAccountRef`**；**三线** **`info.version` 2026-05-11** |
| 2026-05-11 | **`confirmation-flow` · OCO** | **§1** **步骤 4 门禁** **（矩阵未解冻）** |
| 2026-05-11 | **`contract-closure` §9** | **`§1.2` 六款** **MR 自检模板** |
| 2026-05-11 | **`billing.md` §12** | **同窗索引** **`traceKey`（D-5）**、**`revenueAccountRef`（D-12）** — **文档版本** **0.2.8** |
| 2026-05-11 | **`design/api` 登记表 · 账务** | **模块五 / `internal` / `me`** **三行** **`info.version`** **锚** **`2026-05-11`** **同窗** **OpenAPI** — **`design/api` v0.1.44** |
| 2026-05-11 | **`OWNERS.md`** | **OpenAPI 行级主** **Jesson@chainup.com**（**花名** **Jesson**）；**备** **「同主」**（**本仓库统一 DRI 占位**） |
| 2026-05-12 | **CC-P0-01 · 文档进展** | **`OWNERS.md`** **具名** **+** **19 根 spec** **`info.contact.email`** **同窗** — **不豁免** **§1.2** **矩阵/Hosted** |
| 2026-05-12 | **CC-P0-03 · 文档进展** | **Owner/Contact** **同窗** **复述** **入账务 DoD**；**示意 PATH→生产** **仍待** **MR** |
| 2026-05-12 | **`design/api` 脚注** | **v0.1.46** **链** **§2** **CC-P0-01/03** **文档进展** |
| 2026-05-12 | **`contract-closure` §10** | **每期 MR 五步** **（选 CC · §9 · §4·§7 · §8+版本 · 邻域）** — **收口执行计划** **阶段 1** |
| 2026-05-12 | **CC-P0-04 · D-12 范式** | **`billing.md` §10.6.1** **V1 值格式 A/B** **+** **首填检查单**；**`keys` §5** **链**；**PRD §11** **脚注**；**`billing-schemas` `revenueAccountRef`** **叙述** **同窗** |
| 2026-05-12 | **CC-P0-03 · `billing.md` §12.1** | **账务三线** **`paths`** **键** **同窗表** **+** **三线 OpenAPI** **`info.version` 2026-05-12**；**`design/api` v0.1.47→v0.1.48** **链** **登记表** **与** **矩阵 B** **说明** — **生产 host/网关** **仍待** **MR** |
| 2026-05-12 | **CC-P0-02 · 矩阵 B（文档）** | **`coobit-spot|margin|futures|public|wealth|automation`** **`paths`** **与** **矩阵** **非延期** **行** **同窗**；**登记表** **版本列** **2026-05-12** — **延期格/OCO/WebSocket** **不扩** **虚假 PATH** |
| 2026-05-12 | **CC-P0-05 · §10.3.1** | **`billing.md` §10.3.1** **`D-5`/`D-7`** **实现对签检查单**；**`observability`** **`D-7`** **段落**；**PRD §13** **`[ ]`** **项** — **实现** **仍须** **MR** **勾选** |
| 2026-05-12 | **CC-P0-01 · Hosted/tag** | **`openapi/README.md`** **「Hosted Swagger 与 release tag」** — **`info.version` 同窗** **+** **§1.2** **六款** **归档口径** |
| 2026-05-12 | **P1 · 文档收口（批量）** | **CC-P1-01** **§4 邻域重申**；**CC-P1-02** **`legalReviewTicketId` 生产门槛**（**`tool-management-schemas`**）；**CC-P1-03** **三步 MR 建议/ADR-002**；**CC-P1-04** **`functions` §1.4 行 6** + **`prompt-management.yaml` 2026-05-12**；**CC-P1-06** **`admin-bot-config`×PRD §13** |
| 2026-05-13 | **§5.1 · 升格 gate + 索引导航** | **计划阶段 4** **操作定义** **入库**（**锚点** **`#cc-stage4-spec-gate`**）；**`requirements/README`** **推荐阅读第 10 条** + **矩阵纪律** **§5.1**；**`spec.md` / `product` / PRD §13** **互链** |
| 2026-05-14 | **§3.1 · P1 批量 MR 拆单** | **MR-A～D** **建议表** **入库**（**CC-P1-02/04/06/01**）；**链** **`spec` / `requirements/README`** — **不替代** **法务/生产实测** |

**P0-01～04、P1-04/06（B 阶段）**：**仍** **依赖** **Hosted/tag、生产网关、财务会签与实现 MR** — **未** **在** **本条** **声明** **生产可承诺**。**（2026-05-09）** **仓库内 (a) 可审 Spec** **与** **`design/api` 登记表 `info.version`** **已同窗**。**（2026-05-10）** **`components/*.yaml` 全量** **已同窗** — **见** **§8 顶行**。

---

<a id="cc-section9-six"></a>

## 9. `§1.2` 可对签六款 · MR 自检表（模板）

**用途**：**单条能力** **拟** **对客** **宣称「已支持 / 已闭环」** **前**，复制下表至 MR（或工单）并 **逐项勾选** **可链锚点**。**正文条款** **见** **上文** **§1.2**。**编排侧三闸一叶纸**（**闸 1** **含** **`runtime-freeze` §3**；**与下表同窗**）：[`implementation-alignment.md`](domains/agent/agent-orchestration/implementation-alignment.md) **§13.1**。

| # | 款 | 自检（须给链接或 §） |
|---|----|------------------------|
| **1** | **`design/api`** **登记表 + 矩阵** | OpenAPI **可访问**；PATH **已冻结** **或** **书面延期** **与备注一致**；**`design/api` 脚注** **已递增** |
| **2** | **`trade-assistance` §8 / `FR-TS07` / `toolId`** | **单行登记**；**[`observability/overview.md`](observability/overview.md) §2.1 · `SC-OBS01`** **等** **可对签** |
| **3** | **exchange-agent + Telegram** | **门禁/拒答** **与** **[`telegram/overview.md`](domains/agent/telegram/overview.md)**（**§2.5 · 类型 A / §2.5.x**、**总则 §2～§2.6**）** **对齐**；**合约 Telegram 验收** **`SC-CH-TG-FUT-01～03`** **见** **同文 §5** **与** **[`design/api.md`](../design/api.md)** **Telegram 专节** |
| **4** | **编排 `scenarioId` + ADR-001** | **[`routing-engine.md`](domains/agent/agent-orchestration/routing-engine.md)** **寄存器**；**[`runtime-freeze.md`](domains/agent/agent-orchestration/runtime-freeze.md)** **§3.1～§3.11**（**写键** **最小编排**）；**写路径** **[`adr/001`](../design/adr/001-telegram-confirm-before-coobit-write.md)** |
| **5** | **自动化 / Pull** | **[`automation-alerts.md`](flows/automation-alerts.md)**、**`trade-assistance` §8.3～8.5**、**[`state-machine.md`](domains/agent/agent-orchestration/state-machine.md)** **`taskId`** |
| **6** | **REST↔WS**（**若本条能力依赖**） | **[`Runtime/reconciliation.md`](Runtime/reconciliation.md) §1** **矩阵**；**`exchangeViewSource` / `SC-OBS06`** |

**矩阵格自** **`TBD`→冻结** **另须** **§4** **全文核对** **+** **§7** **登记**。

---

<a id="cc-section10-five"></a>

## 10. 每期 MR 固定动作（契约收口执行节奏）

**用途**：与 **需求层契约收口执行计划** **阶段 1** 对齐 — **任何** **拟** **推进** **CC-P0/P1** **或** **矩阵/登记表** **的 MR** **建议** **按序** **执行** **下列五步**（**可** **复制** **为** **MR 描述** **首节**）。**症状→Owner→首节可复制** → **[`closure-remaining` §6.4](closure-remaining.md#cc-problem-to-action)**；**推荐合并切片** → **[`closure-remaining` §6.2](closure-remaining.md#cc-remaining-62-merge-order)**。**走** **[`LITE-MODE`](LITE-MODE.md)** **时**：**步 2** **与** **该文 §2** **（常规四块 + 条件第五块）** **同窗** — **宣称闭环** **须** **第五块** **及** **[`implementation-alignment` §13.1](domains/agent/agent-orchestration/implementation-alignment.md)** **三闸**。

| 步 | 动作 |
|----|------|
| **1** | **选定** **本轮** **关闭或部分关闭** **的** **CC ID**（**优先** **§2** **P0** **未** **满** **DoD** **项**，**再** **并行** **§3** **P1**） |
| **2** | **复制** **上文** **§9** **六款自检** **至** **MR**（**小团队** **可** **用** **[`LITE-MODE` §2](LITE-MODE.md)** **第五块** **+** **[`product/release-notes`](../../../product/release-notes.md)** **最新一节** **作** **承诺/不承诺** **清单**，**但** **判据** **不得** **弱于** **§1.2**）；**若** **宣称** **对客** **「已支持 / 已闭环」**，**还须** **点检** **[`implementation-alignment` §13.1](domains/agent/agent-orchestration/implementation-alignment.md)** **三闸**。**若** **变更** **`design/api.md`** **矩阵格** **（含延期备注变更）** — **还须** **跑** **§4** **核对清单** **并** **勾选** |
| **3** | **按** **§7** **模板** **登记**：**矩阵格或登记表行**、**Spec URL/`openapi.yaml` 路径或 tag**、**`design/api` 新版本脚注**、**关联合 PR（若有实现）** |
| **4** | **合并前** **于** **本节** **§8** **表** **顶** **追加** **一行** **推进记录**；**递增** **本条** **文末** **「文档版本」** |
| **5** | **邻域同窗**：**交易/工具** **→** **`trade-assistance` §8** **`FR-TS07`**；**账务/观测** **→** **`billing`/`observability`**；**Telegram** **→** **`telegram/admin-bot-config`** **与** **PRD** **§13** |

---

**文档版本**：0.2.31 · **维护**：产品 + 架构接口 owner + Agent Runtime owner · **邻域**：[`design/api.md`](../design/api.md)、[`design/canonical-trading-model.md`](../design/canonical-trading-model.md)、[`design/adr/004-intent-centric-execution-and-canonical-trading-model.md`](../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`openapi/README.md`](../openapi/README.md)、[`billing-management/functions.md`](domains/admin/billing-management/functions.md)、[`domains/admin/observability-management/overview.md`](domains/admin/observability-management/overview.md)、[`trade-assistance.md`](domains/agent/exchange-agent/trade-assistance.md)、[`observability/overview.md`](observability/overview.md)、[`Runtime/reconciliation.md`](Runtime/reconciliation.md)、[`risk/README.md`](risk/README.md)、[`risk/acceptance.md`](risk/acceptance.md) 等 · **本版**：**文首 + CC-P1-04 链 PRS §4 改什么去哪**。**承** **0.2.30**。
