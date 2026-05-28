# 接口与契约（需求路径与能力面 SSOT；OpenAPI 登记表 B：链至 [`specs/openapi/`](../openapi/README.md)，Owner [`OWNERS.md`](../openapi/OWNERS.md)）

汇总 **HTTP / WebSocket / 内部事件** 等契约的入口说明（可逐步替换为 OpenAPI 链接或片段）。

## Agent 执行与 API 边界

**Agent 运行时**在 **Coobit 侧落地** 的动作（委托、撤单、条件单、划转、借还及 **依赖交易所状态的只读** 等）**仅以** **子账户 scope** 下 **本文矩阵** 与 **所内已冻结 OpenAPI** **已列明** 的 endpoint **为依据**。**公档或所内 spec 未覆盖** 或矩阵 **PATH 为 TBD** 的能力 **首版不实现、不对外承诺**；**禁止** 未文档化内部接口、浏览器自动化或 **伪造** 成交/委托。**对上 Coobit 的 HTTPS 出站** **可** **由** **ChainUp 所内 `openapi-ai` 官方包**（Skill、CLI、可选 MCP，**须 pin 版本**）**承载**，**但必须** **仅命中** [`agent-coobit-api-allowlist.md`](../requirements/integrations/exchange/agent-coobit-api-allowlist.md) **所列** **`requestPath`（方法与矩阵同窗）**。**同窗** [`integrations/exchange/overview.md`](../requirements/integrations/exchange/overview.md) 「Coobit · 官方 openapi-ai（Skill）采纳」。**禁止**在未更新矩阵/白名单前 **借由** Skill **新增或放宽** 调用面；**本产品仓库不并行维护** 与 **`openapi-ai` 同源重复的** **逐 PATH 工具规格 SSOT**。**用户须交易所站内完成的动作**（**不含** **Agent Key 绑定/onboarding**：同窗 **`FR-WEB01`**、**`me/agent/*`** **须在 Agent 产品线绑定页完成**） 通过 [`overview.md`](../requirements/domains/agent/exchange-agent/overview.md) **稳定码**（如 **`WEALTH_ACTION_REQUIRES_WEB`**、**`TRANSFER_REQUIRES_WEB`**）**转交**，**不属于** Agent **用非公开 API 补齐**。

**契约收口 / MR**：**矩阵格、`TBD`→PATH（或延期备注）、登记表行补齐** **须**在本 PR 或可合并窗口内 **按 [`contract-closure.md`](../requirements/contract-closure.md) §4、§7 核对邻域**；**本条**递增 **文末版本脚注**，与 **`design`↔需求** **`v*.x.+` 脚注**对齐。**排期 · 本 Git vs 所内 · MR 勾选** **同窗** [`closure-remaining.md`](../requirements/closure-remaining.md) **[§7.5](../requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../requirements/closure-remaining.md#cc-closure-exec-checklist)**（**不**替代 **`contract-closure` DoD**）。

**两阶段收口（阅读说明）**：**需求路径 / PATH 示意 / 矩阵书面延期** 与 **`contract-closure.md` §1 · §1.1** **一致** — **A「需求落地」** 可由本文正文单独承载；**B「OpenAPI 可访问 + Owner」** 仍以登记表为准（**CC-P0-01～03**）。

## 所内 OpenAPI / 契约登记（SSOT 入口）

**规则**：所内 **正式 spec**（Swagger / Redoc 链接、`openapi.yaml` Git 提交、`release-xxx` 标签等）**填入下表**后，本文 **endpoint 矩阵** 的 **`TBD` PATH** **须**在同 PR 或紧随 PR 中替换；**禁止**仅改实现不改表。**Owner** 为所内 **接口/网关** 对口人（花名 + 域账号可评审）。

**登记表填写清单（所内落地）**：

| 自检项 | 说明 |
|--------|------|
| **Spec 可访问** | **URL**（Swagger UI / Redoc）或 **仓库内 `openapi.yaml`（及 commit / tag）**；评审须能打开或与 CI **artifact** 对齐。 |
| **baseurl 分行** | **现货/钱包** 与 **合约** **分列**（**沙箱 / 生产** **分开**更佳）；与矩阵 **双网关** 一致，**禁止**混写为单 host。 |
| **环境与鉴权** | 文档中注明 **测试账户 / Key 权限** 获取方式（**不**在本文写 Secret）。 |
| **Owner + 备份** | **主/备** 对口；**契约变更** **须** 有 PR **更新本表或本文版本**，**禁止**「只部署不改表」。 |
| **与矩阵一致性** | 登记表 **某业务行** 填 spec 后，对应 **endpoint 矩阵** **TBD** **须在可合并窗口内** 替换为 **冻结 PATH**（或 **书面**标 **延期**）。 |
| **阻塞语义** | 矩阵 **PATH 仍为 TBD** 的 **P0** 能力：**Agent 首版不交付**（见 **「Agent 执行与 API 边界」**），直至 **登记完成 + PATH 冻结**。 |

**登记表填链占位（B 阶段 · 替换上表各业务行第 2～4 列）**：

| 列 | 填写模板（复制到上表） |
|----|------------------------|
| **OpenAPI / Spec** | **`TBD`** → **可访问** **Swagger UI / Redoc** **`https://…`**，**或** 仓库内 **`…/openapi/<name>.yaml`** **锚定** **`@<tag>` / commit（短 SHA）** |
| **版本或 Git 标签** | **`TBD`** → **与上列 spec artifact 一致** 的 **release tag**、**commit** 或 **冻结日期（YYYY-MM-DD）** |
| **Owner** | **`TBD`** → **主** **`花名(域账号)`** · **备** **`…`** |

**（本仓库）** **B 阶段落地**：各业务行 **可链** **[`specs/openapi/`](../openapi/README.md)** **下 YAML**；**账务三线** **同窗** **`billing-schemas`**；**模块一 · I02 `code`** **`agent-management-schemas`**；**模块六 · §4 信封 `code`** **`access-control-schemas`（`$ref` §7.1 单源）**；**模块八 · Logs & Observability** **`observability-schemas`**（**`admin/observability`** **同窗** **`billing-schemas`** 之 **`ExecutionId`/`BillingTraceId`**）；**模块七子面 · Telegram** **`telegram-channels-schemas`**（**`admin/telegram-channels`**）；**用户协查摘要 + 全局 bundle** **`users-global-config-schemas`**（**`admin/users-global-config`**）；**模块四 · AI Settings** **`ai-settings-schemas`**（**`admin/ai-settings`**）；**模块二 · Prompt** **`prompt-management-schemas`**（**`admin/prompt-management`**，**含** **`GET /internal/prompts/effective`**）；**编排 Resolver** **`orchestration-runtime-schemas`**（**`internal/agent-orchestration`** · **INV-008**）；**模块三 · Tool Registry** **`tool-management-schemas`**（**`admin/tool-management`**）；**子账户 Coobit 矩阵** **`exchange-schemas`**（**`exchange/coobit-spot|margin|futures|wealth|automation|public`**）；**用户开通 / 私有流** **`onboarding-schemas`**（**`user/onboarding`**）**与** **`stream-schemas`**（**`stream/user-private-ws`** · listenKey）；**花名** **[`OWNERS.md`](../openapi/OWNERS.md)**。**Hosted Swagger** **可**与 YAML **并行** **不作废** **仓库内文件**。**终裁** **（Hosted URL / `release-*` tag / 版本列同窗）** **见** [`openapi/README.md`](../openapi/README.md) **「Hosted」**。

**登记表 · OpenAPI 列说明（本版）**：**A 阶段（[`contract-closure` §1.1](../requirements/contract-closure.md)）** 已齐时，下表 **第 2～4 列** **可**先用 **上表「填链占位」** 之 **`TBD` 字面**，**避免**空单元格被误读；**B 阶段** **须**替换为 **可访问 Spec + 版本锚 + 具名 Owner**（[`contract-closure`](../requirements/contract-closure.md) **§1.2**）并实现 **矩阵 PATH** 冻结或与延期备注一致。**能力面与 PATH 示意** 以 **同列「对齐需求」** 及下文 **`admin/agents*` / `prompt-packs*` / `admin/tools*` / `admin/ai*` / `admin/billing*` / `admin/access-control*` / `admin/users*` / `admin/observability*`**、**子账户矩阵** 为 **需求下限**。

| 范围 | OpenAPI 或设计文档 URL / 路径 | 版本或 Git 标签 | Owner | 对齐需求 |
|------|-------------------------------|-----------------|-------|----------|
| **（外链）Coobit · OpenAPI 用户文档 v2** | [Open API Doc V2 — GitBook](https://exchangedocsv2.gitbook.io/open-api-doc-v2) · [站点图 / sitemap](https://exchangedocsv2.gitbook.io/open-api-doc-v2/sitemap.md) | 站内 CHANGELOG：**2025-03-28** | 所内 **对接** | **产业锚**：[基本信息](https://exchangedocsv2.gitbook.io/open-api-doc-v2/openapi-basic-information.md)、Spot / Margin / Futures / Sub Account / Wallet / WebSocket / Errors；**正式环境与 baseurl** **须所内冻结**，本文下表 **PATH 与文档逐条对签** |
| **运营后台 · Agent 模板/实例/Runtime（模块一 · management）** | [`admin/agent-management.yaml`](../openapi/admin/agent-management.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **MR 短 SHA**）（**合并后请换 release tag**） | **管理台/配置 BFF（主）· 架构（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **「运营侧 Agent Management API（`admin/agents/*`）」专节** + **`instanceOverrides`、`runtimeInstanceState`、`RUNTIME_*`/批量、`TEMPLATE_*`、`INSTANCE_*`**；**I02 响应 `code`** **须与** [`agent-management/functions.md`](../requirements/domains/admin/agent-management/functions.md) **§7.1 · OpenAPI `enum`** **一致**（含 **`AGENT_ROLLOUT_BLOCKED`** 及 **`access-control`** 同窗登记之 **`AGENT_*`**）；**准入触点** [`access-control/functions.md`](../requirements/domains/admin/access-control/functions.md) **§2～§4**；**统一准入结果信封 · `capabilities`（可选）** [`access-control/eligibility-runtime.md`](../requirements/domains/admin/access-control/eligibility-runtime.md) **§4 · §10**。**需求** [`agent-management/functions.md`](../requirements/domains/admin/agent-management/functions.md) **§2.2·§7.1**；**控制台 IA** [`config.md`](../requirements/domains/admin/agent-management/config.md)。**填链后与需求域做一次对齐 PR**。
| **运营后台 · Prompt / 提示词（模块二 · prompt-management）** | [`admin/prompt-management.yaml`](../openapi/admin/prompt-management.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **`CC-P1-04` · `functions` §1.4**）（**合并后请换 release tag**） | **管理台/配置 BFF（主）· 架构（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **「运营侧 Prompt Management API（`admin/prompt-packs/*`）」专节** + **`promptPack*`**、发布/回滚、**`FR-PM08`**、**拼装**、**`resolvedPromptBinding`**、`placeholderDenylistRevision`/`safetyPhraseBlocklistRevision`、**[`observability` §2.3](../requirements/observability/overview.md)**：**需求** [`functions.md`](../requirements/domains/admin/prompt-management/functions.md) **§1.4（含 §1.2 六款会签）**、[`runtime-injection.md`](../requirements/domains/admin/prompt-management/runtime-injection.md) **§2.3 · §7.1**；**IA** [`config.md`](../requirements/domains/admin/prompt-management/config.md)。**填链后与 `agent-orchestration` / `observability` §2.3 / `FR-T05` 对齐 PR** · **`CC-P1-04`** |
| **运营后台 · Tool Registry / 策略 / 启用（模块三 · tool-management）** | [`admin/tool-management.yaml`](../openapi/admin/tool-management.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **MR 短 SHA**）（**合并后请换 release tag**） | **管理台/配置 BFF（主）· 架构（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **「运营侧 Tool Management API（`admin/tools/*`）」专节** + **`toolId`、镜像、`toolRiskLevel`、`enabledOperational`、`matrixStatus`、**`FR-TM03`**（`toolPolicy*` / `allowed*` / **`denyByDefault`**）、**Tool Profile → `toolId[]`**（**T05** · **SC-TM-09**）、**`agent.tool.call` **`invocationState`**、**统一 Result 信封**（**[`runtime-contract.md`](../requirements/domains/admin/tool-management/runtime-contract.md)** **§1·§4**）、启用门槛、观测跳链：**需求** [`functions.md`](../requirements/domains/admin/tool-management/functions.md) **§2～§7**；**IA** [`config.md`](../requirements/domains/admin/tool-management/config.md) **§2～§5**；**流程** [`flow.md`](../requirements/domains/admin/tool-management/flow.md)。**与 `design/api` 矩阵 + `trade-assistance` §8 对齐 PR**；**禁止 TBD「假开」**（SC-MCV1-05）。 |
| **运营后台 · AI Settings（模块四 · ai-settings）** | [`admin/ai-settings.yaml`](../openapi/admin/ai-settings.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **MR 短 SHA**）（**合并后请换 release tag**） | **管理台/配置 BFF（主）· LLM 集成（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **`FR-MC401～408`**、**`SC-AI*`**；[`ai-settings/functions.md`](../requirements/domains/admin/ai-settings/functions.md)、[`overview`](../requirements/domains/admin/ai-settings/overview.md)；[`integrations/llm/provider-routing.md`](../requirements/integrations/llm/provider-routing.md)；[`Runtime/recovery.md`](../requirements/Runtime/recovery.md)；下文 **「运营侧 AI Settings API（`admin/ai/*`）」** **与** **「编排执行预算（`FR-AO06`）」**；**`providerId`/`modelId`** 与 [`observability/overview` §2](../requirements/observability/overview.md)、**FR-MC804** 同窗；**密钥仅 `secretRef`**（**不**与 [`keys.md`](../requirements/domains/admin/trading-agent-config/keys.md) 交易键混落明文）。**`CC-P0-01`** |
| **运营后台 · Billing & Settlement（模块五 · billing-management）** | [`admin/billing-admin.yaml`](../openapi/admin/billing-admin.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-26`**（`info.version` · **轨 A：`FR-MC501～508`** · **轨 B：`commerce_phase2`、`FR-MC509～512`** · **同窗** **`billing-schemas`** + `billing.md` §12.1）（**合并后请换 release tag**） | **管理台/账务（主）· 架构（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **Agent 消耗关单主链**：**轨 B** **`FR-MC509～512`**、**`SC-B20/B21`**、[`commerce-model.md`](../requirements/domains/admin/billing-management/commerce-model.md)；**轨 A 对读**：**`FR-MC501～508`**；[`overview` §6～§10 · §12.1](../requirements/domains/admin/billing-management/overview.md)、[`functions` §5](../requirements/domains/admin/billing-management/functions.md)、[`config · IA`](../requirements/domains/admin/billing-management/config.md)。**同窗**下文 **「运营侧 Billing API」**、**「内部 · 商业轨 / 权益核销（Agent S5）」**、**「内部 · Token 账务扣减 API（轨 A 对读）」**、**[`user/commerce-me.yaml`](../openapi/user/commerce-me.yaml)**、**[`user/billing-me.yaml`](../openapi/user/billing-me.yaml)**；**Agent S5 关单** **`contract-closure` §8**；**CC-P0-03** **仅轨 A**。 |
| **运营后台 · Access Control（模块六 · 准入/名单/封禁/KYC 镜像）** | [`admin/access-control.yaml`](../openapi/admin/access-control.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **MR 短 SHA**）（**合并后请换 release tag**） | **管理台/配置 BFF（主）· 合规（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **「运营侧 Access Control API（`admin/access-control/*`）」专节** + [`access-control/functions.md`](../requirements/domains/admin/access-control/functions.md) **FR-MC601～607**、**SC-AC**；[`access-control/config` · I02 §4](../requirements/domains/admin/access-control/config.md)；[`access-control/eligibility-runtime.md`](../requirements/domains/admin/access-control/eligibility-runtime.md)（**评估顺序、灰度命中、运行时反应、缓存、事件、结果信封、`capabilities`**）。业务 **`code` 与 [`agent-management` §7.1](../requirements/domains/admin/agent-management/functions.md) **OpenAPI `enum` 同窗**（含 **`AGENT_COMPLIANCE_RESTRICTED`、`AGENT_USER_BLOCKED`、`AGENT_REGION_BLOCKED`、`AGENT_KYC_REQUIRED`/`AGENT_KYC_INSUFFICIENT`（收口策略见同窗）、`AGENT_ROLLOUT_BLOCKED`、`AGENT_MEMBERSHIP_BLOCKED`**）。**填链**后与 **用户摘要、`agentState`、附录 A** **对签 PR**。
| **运营后台 · Logs & Observability（模块八 · observability-management）** | [`admin/observability.yaml`](../openapi/admin/observability.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **MR 短 SHA**）（**合并后请换 release tag**） | **管理台/配置 BFF（主）· 观测（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **`FR-MC801～807`**、**`SC-OM*`**；[`observability-management/functions.md`](../requirements/domains/admin/observability-management/functions.md)；[`overview` §2～§5](../requirements/domains/admin/observability-management/overview.md)；事件下限 [`observability/overview` §2～§4](../requirements/observability/overview.md)（**§2.4** **`transitionTrigger`** **主态边**）；追踪与 **`executionId`** 主锚 [`tracing.md`](../requirements/observability/tracing.md)；计费 join **`FR-MC503`**；下文 **「运营侧 Logs & Observability API」**；**`CC-P0-01`** |
| **运营后台 · Telegram Bot / Webhook（模块七子面 · `admin/channels/telegram/*`）** | [`admin/telegram-channels.yaml`](../openapi/admin/telegram-channels.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **MR 短 SHA**）（**合并后请换 release tag**） | **管理台/渠道（主）· 架构（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **「运营侧 Telegram 渠道运维 API」专节** + **`FR-MC709～711`**、**`FR-TG-ADMIN-01～06`**（含 **`keys` §4.2** **开通欢迎语** **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN|ZH_TW|EN`** **与** **遗留键**）；[`telegram/admin-bot-config.md`](../requirements/domains/agent/telegram/admin-bot-config.md)；**`TELEGRAM_BOT_TOKEN_SECRET_REF`** **仅 `secretRef`**（与 **模块四** [`ai-settings`](../requirements/domains/admin/ai-settings/overview.md) **同窗**）；**`setWebhook` / `getWebhookInfo` / 自检** **PATH** **OpenAPI 终裁** · **`CC-P1-06`** |
| 运营后台 · 用户摘要 + 全局配置写 | [`admin/users-global-config.yaml`](../openapi/admin/users-global-config.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **MR 短 SHA**）（**合并后请换 release tag**） | **管理台/配置 BFF（主）· 架构（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **「运营侧用户协查摘要 API（`admin/users/*`）」专节** + [`config.md`](../requirements/domains/admin/management-console-v1-prd.md) **FR-M07、§7.2、§8.2**；**全局 bundle 写** [`trading-agent-config/flow`](../requirements/domains/admin/trading-agent-config/flow.md)、[`keys.md`](../requirements/domains/admin/trading-agent-config/keys.md)；**模块六归因** [`access-control/overview.md`](../requirements/domains/admin/access-control/overview.md) |
| 子账户 scope · **币币**（私有读/写） | [`exchange/coobit-spot.yaml`](../openapi/exchange/coobit-spot.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **矩阵 B · `paths` 键同窗**）（**合并后请换 release tag**） | **交易所网关（主）· Agent Runtime（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | 下文矩阵 · **币币** 行 |
| 子账户 scope · **杠杆** | [`exchange/coobit-margin.yaml`](../openapi/exchange/coobit-margin.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **矩阵 B · 借还行延期、下单撤单同窗**）（**合并后请换 release tag**） | **交易所网关（主）· Agent Runtime（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | 下文矩阵 · **杠杆** 行 |
| 子账户 scope · **合约** | [`exchange/coobit-futures.yaml`](../openapi/exchange/coobit-futures.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **矩阵 B · `paths` 键同窗**）（**合并后请换 release tag**） | **交易所网关（主）· Agent Runtime（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | 下文矩阵 · **合约** 行 |
| 子账户 scope · **理财** | [`exchange/coobit-wealth.yaml`](../openapi/exchange/coobit-wealth.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **矩阵 B · 细分延期、已列 PATH 同窗**）（**合并后请换 release tag**） | **交易所网关（主）· Agent Runtime（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | 下文矩阵 · **理财** 行 |
| 子账户 scope · **自动化**（条件单等） | [`exchange/coobit-automation.yaml`](../openapi/exchange/coobit-automation.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **矩阵 B · 合约条件单同窗**）（**合并后请换 release tag**） | **交易所网关（主）· Agent Runtime（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | 下文矩阵 · **自动化** 行 |
| **公开** 行情（免子账户 Key） | [`exchange/coobit-public.yaml`](../openapi/exchange/coobit-public.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **矩阵 B · 币币行情 PATH 同窗**）（**合并后请换 release tag**） | **交易所网关（主）· Agent Runtime（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | 矩阵备注「公开层」 |
| **Agent 产品线 · Agent 开通 / 绑定 / 状态（`me/agent/*`）** | [`user/onboarding.yaml`](../openapi/user/onboarding.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-11`**（`info.version` · **绑定校验 **`TradingApiBindRejectCode`** **同窗 `design/api`「绑定保存 · 交易所探测矩阵」**）（**合并后请换 release tag**） | **Agent BFF（主）· host 所内冻结**（**可与交易所网关合并部署**，**不得弱化** **§1.2**）（[`OWNERS.md`](../openapi/OWNERS.md)） | [`onboarding/overview.md`](../requirements/domains/agent/onboarding/overview.md)、[`web/agent-onboarding.md`](../requirements/domains/web/agent-onboarding.md) **`FR-WEB06`**、**本文「用户侧 Agent 开通 / 绑定 API」与「绑定保存 · 交易所探测矩阵」** |
| 账务 · Token 扣费（**历史归档 · CC-P0-03** · 子账户 USDT ↓ + 收入专户） | [`internal/billing-token.yaml`](../openapi/internal/billing-token.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **`billing.md` §12.1** · **`billing-schemas`**）（**合并后请换 release tag**） | **账务服务（主）· Agent Runtime（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **下文「内部 · Token 账务扣减 API（轨 A 对读）」** · **非 Agent S5 默认**；[`billing/overview` §2 · §7 · §11 · §12.1](../requirements/domains/admin/billing-management/overview.md) **`FR-B11、FR-B14`**；与用户 **`me/billing`**、运营 **`admin/billing/*`** **同窗 `billingTraceId`/幂等** · **`CC-P0-03`**。 |
| **内部 · Agent 编排 Trade Resolver**（L0 缺参 · BFF） | [`internal/agent-orchestration.yaml`](../openapi/internal/agent-orchestration.yaml) · [索引](../openapi/README.md) | **`2026-05-26`**（`info.version` · **`orchestration-runtime-schemas`**） | **Agent Runtime BFF（主）· 编排（备）**（[`OWNERS.md`](../openapi/OWNERS.md)） | **下文「内部 · Agent 编排 Trade Resolver API」** · INV-008、[`runtime-invariants`](../requirements/Runtime/runtime-invariants.md) · [`MR-B-BFF-IMPLEMENTATION` §9](../requirements/skill-specs/MR-B-BFF-IMPLEMENTATION.md)；TS `postInternalAgentOrchestrationTradeResolver`。 |
| **内部 · 商业轨 / 权益核销（Agent S5 主链）** | [`internal/billing-entitlements.yaml`](../openapi/internal/billing-entitlements.yaml) · [索引](../openapi/README.md) | **`2026-05-26`**（`info.version` · **`billing-schemas` Phase 2 扩展同窗**）（**合并后请换 release tag**） | **账务服务（主）** · **同窗** **`design/api`「内部 · 商业轨 / 权益核销」** · [`commerce-model.md`](../requirements/domains/admin/billing-management/commerce-model.md) | **轨 B**：**S2/S5 `ENTITLEMENT_DEBIT`**、余额、pack-grants；**不**计入 **CC-P0-03（Token）** DoD；**闭环** **`contract-closure` §8**。 |
| 用户侧 **H5/主站** · Billing（`me/billing` · **历史归档 · CC-P0-03**） | [`user/billing-me.yaml`](../openapi/user/billing-me.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **`billing.md` §12.1** · **`billing-schemas`** **`2026-05-26` 同窗扩展**）（**合并后请换 release tag**） | **主站/BFF（主）· 账务（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | **演进/历史 Token 流水** · [`billing/overview` §8 · §12.1](../requirements/domains/admin/billing-management/overview.md) **`FR-B12～B16`、`SC-B13/14`**；**用户主链配额** **见 **`me/commerce`** 行** · **`CC-P0-03`**。 |
| 用户侧 **H5/主站** · Commerce（`me/commerce` · **用户主链**） | [`user/commerce-me.yaml`](../openapi/user/commerce-me.yaml) · [索引](../openapi/README.md) | **`2026-05-26`**（`info.version` · **`MeCommerceEntitlementsSummary`**）（**合并后请换 release tag**） | **主站/BFF（主）· 账务（备）**（**同窗** Billing 登记表 Owner） | **订阅/Capability 配额摘要** + **演进消耗明细**（**FR-B17～B20**）；**不含** PSP 表单；同窗 [`commerce-model.md`](../requirements/domains/admin/billing-management/commerce-model.md)；**买包链路** **`design`/实现 MR** |
| WebSocket · 用户成交/订单（若启用） | [`stream/user-private-ws.yaml`](../openapi/stream/user-private-ws.yaml) · [索引](../openapi/README.md)（**仓库内 Spec**；**可**并行挂 Swagger） | **`2026-05-09`**（`info.version` · **MR 短 SHA**）（**合并后请换 release tag**） | **交易所网关（主）· Runtime Push（备）**（**主/备**：[`OWNERS.md`](../openapi/OWNERS.md)；**备** **暂** **「同主」**） | [`exchange-agent/overview` §5（旧 §10.2→Push）](../requirements/domains/agent/exchange-agent/overview.md)；[`monitoring-tasks.md`](../requirements/domains/agent/exchange-agent/monitoring-tasks.md)、[`automation-alerts.md`](../requirements/flows/automation-alerts.md)；与 [`billing/overview` §2](../requirements/domains/admin/billing-management/overview.md)、[`consume-and-bill.md`](../requirements/flows/consume-and-bill.md) **`executionId`/`FR-T01`** 同窗 |

## 待补充

> **契约收尾进度**（**文档侧** **登记**）：[`requirements/contract-closure.md`](../requirements/contract-closure.md) **§8**。下表条目 **A 阶段** **多为** **PATH 示意 + 域 FR**；**B 阶段** **=** **可访问 OpenAPI + Owner + 矩阵格替换 `TBD`**（**见** **contract-closure** **§1.1～§2**）。

- **运营后台 · 单用户摘要**（[`config.md`](../requirements/domains/admin/management-console-v1-prd.md) **FR-M07、§8.2**）：只读返回 **`userId`**、**`displayName`**（脱敏）、**`agentSubAccountId`** / **`agentSubAccountStatus`**（**Agent 专用子账户**；与 [`billing.md`](../requirements/domains/admin/billing-management/overview.md) **§2** 就绪口径一致）、**`agentTradingApiBindingStatus`** / **`agentTradingApiKeyId`**（**公开 id**；**与** [`overview.md`](../requirements/domains/agent/exchange-agent/overview.md) **`子账户交易 API（Agent 绑定）`** **一致**；**禁止**返回 **Secret**）、**`agentState`**、**`vipTier`**（**母账号 / `userId` 维度** VIP 等级，**与 **`AGENT_MIN_VIP_TIER`** 比对时以此为 SSOT**；**非**子账户独立 VIP）、**`agentMinVipTier`**（**拉取时刻**全局 **`AGENT_MIN_VIP_TIER`** 快照）、运营暂停与 **`lastProductBlockReason`**、当日统计、**`recentCharges`**（**≤5**）等 — **下限**以 **§8.2** 为准；无效 `userId` → **404** / `ADMIN_USER_NOT_FOUND`（**§8.4**）。**`agentState` / `lastProductBlockReason`** **须可与** **`access-control`/`I02`** **归因对齐**（**`agent-management` §7.1**，例：**`AGENT_COMPLIANCE_RESTRICTED`、`AGENT_USER_BLOCKED`、`AGENT_REGION_BLOCKED`、`AGENT_KYC_REQUIRED`/`INSUFFICIENT`、`AGENT_ROLLOUT_BLOCKED`、`AGENT_MEMBERSHIP_BLOCKED`**；**附录 A / `design` 同窗**）。**可选** **`capabilities`**（**现货/合约/自动交易旗标**）见 [`eligibility-runtime` §10](../requirements/domains/admin/access-control/eligibility-runtime.md)。**鉴权**：SSO、**`CONFIG_OPERATOR` / `READ_ONLY`**，`OpenAPI` 冻结。
- **运营后台 · Access Control 写与读（模块六）**（[`access-control/functions.md` §2～§4](../requirements/domains/admin/access-control/functions.md)、[`access-control/config` §4](../requirements/domains/admin/access-control/config.md)、[`access-control/eligibility-runtime.md`](../requirements/domains/admin/access-control/eligibility-runtime.md)）：**FR-MC601～607**：灰度/白名单/封禁 **`CRUD`**、导入导出；**KYC 只读镜像**；**`AGENT_MIN_VIP_TIER`** 编辑（数值与 [`keys.md` §3](../requirements/domains/admin/trading-agent-config/keys.md) **同窗 MR**）。**读侧 SLA** **`design` 冻结**（满足 [SC-AC-04](../requirements/domains/admin/access-control/functions.md)）。**可选 BFF：`EvaluateEligibility`** — 响应体 **`allowed` / `code` / `reason`** 见 [`eligibility-runtime` §4](../requirements/domains/admin/access-control/eligibility-runtime.md)。**I02** 等业务失败响应 **`code`** 之 OpenAPI **`enum`** 须与 [`agent-management` §7.1](../requirements/domains/admin/agent-management/functions.md) **表一致**；**新增 `code`** **须**先履行 [SC-AC-08](../requirements/domains/admin/access-control/functions.md)（扩展 [`agent-management` §7.1](../requirements/domains/admin/agent-management/functions.md) **与 OpenAPI**）。**登记表**：上文 **模块六** 行。
- **运营后台 · Billing & Settlement（模块五）**（[`billing-management/functions.md` §2～§5](../requirements/domains/admin/billing-management/functions.md)、[`commerce-model.md`](../requirements/domains/admin/billing-management/commerce-model.md)、[`billing-management/overview.md`](../requirements/domains/admin/billing-management/overview.md)、[`billing-management/flow.md`](../requirements/domains/admin/billing-management/flow.md)）：**Agent 消耗关单主链** **`FR-MC509～512`、`SC-B20/B21`**（**轨 B · S2/S5 `ENTITLEMENT_DEBIT`**）；**`me/commerce`** + **§5.3 执行 join**；**轨 A 对读** **`FR-MC501～508`、`SC-B*`**、**`me/billing`**；**`BILLING_TOKEN_RATE`、`effectiveMinChargeUsdt`、`BILLING_CAPABILITY_MAP`、`COMMERCE_SKU_CATALOG_REF`**；**内部落账 · 平台流水 · 导出（含月 rollup）· 退款工单**（[`rules.md` §2～8](../requirements/domains/admin/billing-management/rules.md) **`+ §流水 ledger`**）；**轨 B PATH** **见下文** **「内部 · 商业轨 / 权益核销」** · **`CC-P0-03`**（**轨 A 关单不替代 §8 轨 B**）。
- **运营后台 · Logs & Observability（模块八）**（[`observability-management/functions.md`](../requirements/domains/admin/observability-management/functions.md)、[`observability-management/overview.md`](../requirements/domains/admin/observability-management/overview.md)）：**`FR-MC801～807`、`SC-OM*`**；**`executionId`** 时间线（**含** **§2.4** **`ObservabilityTimelineEvent.transitionTrigger`** **·** **`SC-OM-04`**）、**`billingTraceId` join `FR-MC503`**（**[`observability/overview.md`](../requirements/observability/overview.md) §2～§2.4**）；**同窗**上文 **「运营侧 Logs & Observability API（`admin/observability/*`）」**；**`CC-P0-01`**。
- **运营后台 · 全局配置写入**（[`management-console-v1-prd`](../requirements/domains/admin/management-console-v1-prd.md) §7.2、§8.4；[`trading-agent-config/functions` §5](../requirements/domains/admin/trading-agent-config/functions.md) · `ADMIN_*`）：`GLOBAL*` / `FEATURE*` / **`STM_*`/`RESUME_*`/`WARM_EXECUTION_INDEX_TTL_SEC`（Memory · [`keys` §2.1](../requirements/domains/admin/trading-agent-config/keys.md)）** / `SYMBOL*` / `AGENT_*` / **`TELEGRAM_*`（非密钥，`keys` §4.2）** 等键真源见 [`keys.md`](../requirements/domains/admin/trading-agent-config/keys.md) 与附录 A §5.1，要求与 PRD 同步维护。按 Tab 或 bundle 建模，单次请求原子提交；乐观锁 `If-Match` / `configVersion` 冲突 → `409` / `ADMIN_OPS_CONCURRENT`。Dry-run、快照与回滚、`admin.audit` 见 [`flow.md`](../requirements/domains/admin/trading-agent-config/flow.md)；**Runtime 生效快照** **对账** [`memory-runtime-schemas.yaml`](../openapi/components/memory-runtime-schemas.yaml) **`MemoryRuntimeConfigSnapshot`**；观测与对签对齐 [`observability`](../requirements/observability/overview.md) 中与运营写路径相关的条目。**Bot Token / Webhook 运维**（**`secretRef`**、**setWebhook**）见 **登记表「Telegram Bot / Webhook」行** 与 [`telegram/admin-bot-config.md`](../requirements/domains/agent/telegram/admin-bot-config.md)。
- **运营后台 · Prompt 包读写与生效读模型（模块二）**：**写路径**草稿/发布/回滚、Few-shot、`LOCKED` 语义；**读路径（Runtime/BFF）**按 **`scenarioId`/`promptPackVersion`/`ETag`（§2.9）** **拉生效包**；**拼装/变量闸/`resolvedPromptBinding`** [**`runtime-injection.md`**](../requirements/domains/admin/prompt-management/runtime-injection.md)。失败语义见 **`FR-PM08`·`FR-T05`**。**需求** [**`functions.md` §1.2～§7**](../requirements/domains/admin/prompt-management/functions.md)（业务能力 **`scenarioId` 优先**：**PM-C15**、`config.md` §1.1a）；**登记表**与本条 **对上表 Prompt 行**。
- **运营后台 · Tool Registry / Enable / Policy（模块三）**：镜像 **`design/api`** 矩阵与 **`toolId`**；**`toolRiskLevel`**（[**`runtime-contract` §2**](../requirements/domains/admin/tool-management/runtime-contract.md)）；**`FR-TM03`** **对象与 BFF**（[`config.md` §3](../requirements/domains/admin/tool-management/config.md)）；**Enable** **须** PATH 冻结 **+** **可调用的策略绑定（缺省禁止 Enable，§7）** **+** CC-P1-02（**C 类**）；模板 **T05** **`toolProfileRef` 逐项校验**（[`flow.md` §6](../requirements/domains/admin/tool-management/flow.md) · **SC-TM-09**）；**Runtime** **`invocationState`**、**Result 信封**、**子账户隔离**（[**`runtime-contract.md`§1·§4·§9**](../requirements/domains/admin/tool-management/runtime-contract.md)），**并与** **[`observability` §2.1 · SC-OBS05**](../requirements/observability/overview.md)** **对签**。**需求** [**`functions.md`** §2.25·§2.4·§4·§7](../requirements/domains/admin/tool-management/functions.md)；登记表 **对上表 Tool 行**。
- **运营后台 · AI Settings（模块四）**（[`ai-settings/functions.md`](../requirements/domains/admin/ai-settings/functions.md)、[`overview`](../requirements/domains/admin/ai-settings/overview.md)）：**`FR-MC401～408`、`SC-AI*`**；密钥仅 `secretRef` 引用（**不**落明文）；[`integrations/llm/provider-routing.md`](../requirements/integrations/llm/provider-routing.md)、[`Runtime/recovery.md`](../requirements/Runtime/recovery.md)。**同窗**上文 **「运营侧 AI Settings API（`admin/ai/*`）」**、**「编排执行预算」** **与** **`modelId`/FR-MC804**：[`observability/overview.md`](../requirements/observability/overview.md) **§2**；登记表 **对上表模块四行**；**`CC-P0-01`**。
- 用户开通 / 查询 Agent 状态（**用户侧**：**Agent 产品线绑定页 / Telegram Deeplink** **`me/agent/*`**；**终端不须登录交易所主站**完成 Key 绑定；**非**上述运营摘要）：**HTTP PATH·校验次序·Coobit 探测** **见上文「用户侧 Agent 开通 / 绑定 API」** **及** **「绑定保存 · 交易所探测矩阵」**（**同窗 **`FR-WEB06`** **`TradingApiBindRejectCode`**）
- **计费资金划转**（与 Coobit 账务）：**USDT** 从 **计费扣减主体**（**Agent 专用子账户 · 币币 USDT 可用**，见 [`billing.md`](../requirements/domains/admin/billing-management/overview.md) **§2**）**扣减** + **同额** **Agent 收入专户**入账（[`billing.md`](../requirements/domains/admin/billing-management/overview.md) **FR-B11、FR-B14**）；**须**在账务 API 中 **显式绑定**子账户/账本维度（**禁止**默认从主账户母账本扣 **Token 费**）；须 **原子或可对账等价**（双分录 / 内部转账），**单边成功**须冲正；平台收入账户标识来自 **`BILLING_AGENT_REVENUE_ACCOUNT_REF`**（[`config.md`](../requirements/domains/admin/management-console-v1-prd.md) §5.1）。**USDT 最小可划转/记账单位**（用于 **`effectiveMinChargeUsdt`** 下限，见 `billing.md` **§2**、**§7.4（结算策略）**，勿与 **`config.md` §7.4** 协查节混淆）须在此 **冻结常量或与所内文档对齐**
- **Coobit · 子账户 scope 私有交易 API（Agent 运行时）**：**下单、撤单、改单**及 **`FR-T01` **所指**策略必需只读查询** **须**使用 **挂在 Agent 专用子账户上**、**经 [`initialization-flow` §1.2](../requirements/domains/agent/onboarding/initialization-flow.md) **`POST .../bindings/trading-api` 服务端校验通过后** **托管绑定至本产品线 Runtime** 的 **API 凭据**（**`billing.md` §2「子账户交易 API（Agent 绑定）」**与 [`consume-and-bill.md`](../requirements/flows/consume-and-bill.md) **`executionId` 同窗**；**触点** [`onboarding/overview.md`](../requirements/domains/agent/onboarding/overview.md) **§1.1**、[`web/agent-onboarding.md`](../requirements/domains/web/agent-onboarding.md) **`FR-WEB01`**）。**默认禁止**使用 **主账户** API Key **调用上述 endpoint**（另有变更单除外）。**权限最小化**模板：**须含** 委托与 **[`overview-legacy-migration`§2](../requirements/domains/agent/exchange-agent/overview-legacy-migration.md)** **所映** **槽位/私有读**（**旧稿 `§10.1`～`§10.3` → `intents` / `FR-T01` 只读等**），及 **[`trade-assistance.md`§8（原 `tools` §10.4）](../requirements/domains/agent/exchange-agent/trade-assistance.md) **与「下表」** 的只读查询；**默认不含** **提币/出金**、**母账户 ↔ Agent 子账户划转**（见 **[`boundaries.md`](../requirements/domains/agent/exchange-agent/boundaries.md) §8.4**）。**HMAC / 签名、时间窗、错误码、rate limit** 与 **所内交易所 OpenAPI** 对齐后 **将下表 PATH 列替换为正式 path**。**Secret** **仅**存 **密钥服务 / 运行时**；**运营后台、审计、结构化日志默认值** **不得**落 **Secret**（**可**记录 **`agentTradingApiKeyId`** 等 **公开 id**）。

### 子账户 scope · endpoint 矩阵（对齐 [`trade-assistance.md`](../requirements/domains/agent/exchange-agent/trade-assistance.md) **§8/`FR-TS07`（原 **`tools` §10.4**）** · **PATH** 与 [Coobit OpenAPI v2](https://exchangedocsv2.gitbook.io/open-api-doc-v2) 对签）**

**双网关（公档）**：**现货 / 杠杆 / 钱包** 与 **合约** **不同主机** —— [Spot](https://exchangedocsv2.gitbook.io/open-api-doc-v2/spot.md) / [Wallet](https://exchangedocsv2.gitbook.io/open-api-doc-v2/wallet.md) 示例为 **`https://openapi.xxx.xx`**；[Futures](https://exchangedocsv2.gitbook.io/open-api-doc-v2/futures.md) 为 **`https://futuresopenapi.xxx.xx`**。公档个别行出现 **`futuersopenapi` 拼写** 或 **`.com` / `.xx` 混用**，**实现与文档以所内冻结 baseurl 为准**。下表 **PATH** 均为 **requestPath**（签名串组成部分，见 [OpenApi Basic Information](https://exchangedocsv2.gitbook.io/open-api-doc-v2/openapi-basic-information.md)）。

**列**：**业务线** | **能力** | **R/W** | **PATH（公档）** | **首版** | **备注**

| 业务线 | 能力 | R/W | PATH（公档 · 所内冻结前仍须 OpenAPI 终裁） | 首版 | 备注 |
|--------|------|-----|---------------------------------------------|------|------|
| **币币** | 行情：ticker / 深度 / K 线 / 成交 | R | **现货网关** `GET /sapi/v2/ping`、`/time`、`/symbols`、`/depth`、`/ticker`、`/trades`、`/klines` | P0 | [Spot](https://exchangedocsv2.gitbook.io/open-api-doc-v2/spot.md)；公档 **MARKET_DATA** 类 **须 API Key**；所内 **可** 另设 **公开** 聚合层 **免 Key** |
| **币币** | 账户：余额、委托、成交 | R | **现货网关** `GET /sapi/v1/account`；`GET /sapi/v2/order`、`/openOrders`、`/myTrades`；`GET /sapi/v3/historyOrders`、`/sapi/v3/myTrades` | P0 | 字段与版本以所内 spec 为准 |
| **币币** | 下单、撤单、改单 | W | **现货网关** `POST /sapi/v2/order`、`/order/test`、`/batchOrders`；`POST /sapi/v2/cancel`、`/batchCancel` | P0 | **改单**：公档 Spot **未列** amend — **书面延期（CC-P0-02）**：首版 **撤单 + 重建**；所内补 amend endpoint 后 **回填本格 PATH 描述** |
| **币币** | OCO（一取消另一） | W | **书面延期（CC-P1-01）** | P0 | **`skill.spot.oco`** — [`trade-assistance.md`](../requirements/domains/agent/exchange-agent/trade-assistance.md) **§4·§8.2**；**PATH 冻结前** **不对用户承诺**；解冻 **须** [`contract-closure.md`](../requirements/contract-closure.md) **§4** |
| **币币** | Bracket（入场 + 保护腿） | W | **书面延期（CC-P1-01）** | P0 | **`skill.spot.bracket`** — **同窗** **§4·§8.2**；**PATH 冻结前** **不承诺** |
| **杠杆** | 借币、还币、利息/仓位查询 | R/W | **书面延期（CC-P0-02）** | P0 | [Margin](https://exchangedocsv2.gitbook.io/open-api-doc-v2/margin.md)；借还/利息 **PATH** **以所内 OpenAPI 或扩展章为准**；**冻结前** Agent **不承诺**本行自动化 → **`FR-T05` / 主站**（**[`boundaries.md`](../requirements/domains/agent/exchange-agent/boundaries.md) §8.4**） |
| **杠杆** | 杠杆下单、撤单 | W | **现货网关** `POST /sapi/v2/margin/order`；`GET /sapi/v2/margin/order`；`POST /sapi/v2/margin/cancel`；`GET /sapi/v2/margin/openOrders`、`/myTrades` | P0 | [Margin](https://exchangedocsv2.gitbook.io/open-api-doc-v2/margin.md) |
| **合约** | 行情：标记价、指数、资金费、深度 | R | **合约网关** `GET /fapi/v1/ping`、`/time`、`/contracts`、`/depth`、`/ticker`、`/ticker_all`、`/index`、`/klines` | P0 | [Futures](https://exchangedocsv2.gitbook.io/open-api-doc-v2/futures.md)；**独立 host** |
| **合约** | 账户：持仓、保证金、风险度 | R | **合约网关** `GET /fapi/v1/account` | P0 | KOL/扩展：`/fapi/v1/kol_*` 等 **一般非 Agent 首版** |
| **合约** | 开平仓、撤单、调杠杆与保证金 | W | **合约网关** `POST /fapi/v1/order`；`GET /fapi/v1/order`、`/openOrders`；`POST /fapi/v1/cancel`、`/cancel_all`；`GET /fapi/v1/myTrades`；历史类 `POST /fapi/v1/orderHistorical`、`/profitHistorical`；`POST /fapi/v1/edit_lever`、`/edit_position_margin`、`/edit_user_margin_model`、`/edit_user_position_model` | P0 | **撤改**：未见与 Spot 对称之 **改价改量**；以所内为准。**Telegram 类型 A** **对签** **[`telegram/overview` §2.5.4 · §5](../requirements/domains/agent/telegram/overview.md) **`SC-CH-TG-FUT-01`、`SC-CH-TG-FUT-03`** **与** **[`trade-via-agent`](../requirements/flows/trade-via-agent.md)** **专节（第三步/第六步）** |
| **理财** | 持仓、到期、收益（只读） | R | **现货网关** `POST /sapi/v1/asset/account/by_type`（`accountType` **含 `4=otc`**，与 **理财/多账本** **映射所内确认**） | P0 | [Wallet](https://exchangedocsv2.gitbook.io/open-api-doc-v2/wallet.md)；**细分产品 API** — **书面延期（CC-P0-02）** 至所内映射冻结。**产品侧只读路径**、**类 2** 见 [`flows/wealth-via-agent.md`](../requirements/flows/wealth-via-agent.md)；**编排** **`wealth.holdings_read`** 见 [`../requirements/domains/agent/agent-orchestration/routing-engine.md`](../requirements/domains/agent/agent-orchestration/routing-engine.md) **§3**。 |
| **理财** | 申购、赎回 | W | **现货网关** `POST /sapi/v1/asset/universal_transfer`（`fromAccountType` / `toAccountType` **含 `4=otc`**；另见 `POST /sapi/v1/asset/universal_transfer_query`） | P0 / 主站 | **`skill.wealth.subscribe` / `skill.wealth.redeem`** **与** **八步流程** 见 [`flows/wealth-via-agent.md`](../requirements/flows/wealth-via-agent.md)、[`trade-assistance.md`](../requirements/domains/agent/exchange-agent/trade-assistance.md) **§8.2**；**编排** **`wealth.subscribe` / `wealth.redeem`** 见 [`../requirements/domains/agent/agent-orchestration/routing-engine.md`](../requirements/domains/agent/agent-orchestration/routing-engine.md) **§3**。**PATH 未纳入模板** **或** **所内强制主站** → **`WEALTH_ACTION_REQUIRES_WEB`**（[`boundaries.md`](../requirements/domains/agent/exchange-agent/boundaries.md) **§8.3**）。 |
| **全** | 子账户 **内** 多账本 **划转** | W | **现货网关** `POST /sapi/v1/asset/universal_transfer`、`/universal_transfer_query`；**现货账本** 亦可 `POST /sapi/v1/asset/transfer`、`/transferQuery`（[Spot](https://exchangedocsv2.gitbook.io/open-api-doc-v2/spot.md)） | **条件** | **仅当** 模板 **书面**纳入（**§8.4**）；**accountType** 枚举见 Wallet **1 spot · 2 isolated · 3 cross · 4 otc · 5 contract** |
| **自动化** | 条件单 / 计划委托：创建、查询、取消 | R/W | **合约网关** `POST /fapi/v1/conditionOrder`；配合 `POST /fapi/v1/cancel`、`GET /fapi/v1/order` 等 | P0 | **现货**侧 **计划/条件委托** — **书面延期（CC-P0-02）**：首版 **以本行合约 PATH** 为自动化承诺下限；**现货**侧 **所内扩展前不承诺** → **`FR-T05` / 主站**；同窗 [`automation-alerts.md`](../requirements/flows/automation-alerts.md)、[`monitoring-tasks.md`](../requirements/domains/agent/exchange-agent/monitoring-tasks.md) 与 [`exchange-agent/overview` §5（旧 §10.6）](../requirements/domains/agent/exchange-agent/overview.md)。**Telegram** **触发条件独立版式** **`SC-CH-TG-FUT-02`** · **[`telegram/overview` §2.5.4](../requirements/domains/agent/telegram/overview.md)** · **`trade-via-agent`** **「合约止盈止损 · 分流」** |
| **自动化** | 网格 / DCA 全量机器人 | W | — | **非目标** | 首版 **不包含** |

**规则**：上表 **PATH** 以 **GitBook 用户文档** 为 **产业锚**；**正式环境与权限位** **须** 在所内 OpenAPI **冻结**后与 **[`boundaries.md`](../requirements/domains/agent/exchange-agent/boundaries.md) §8.4**、**子账户 Key `authority`** 逐项对签。**TBD** 或 **未冻结** 行：**Agent 执行首版不支持**（**与** 上文 **「Agent 执行与 API 边界」**）；产品侧 **可** 降级为 **主站引导** 或 **拒答**（对齐 **`exchange-agent` 分卷**：[ **`overview`** §1～§5](../requirements/domains/agent/exchange-agent/overview.md)、[`README`](../requirements/domains/agent/exchange-agent/README.md)）。**`sapi`/`fapi` 版本号** 与所内 **changelog** 同步。

**B 阶段（文档子集 · CC-P0-02 · 2026-05-09）**：**矩阵** 中 **非书面延期** **PATH 行**（**币币行情/账户/下单撤单**、**杠杆下单撤单**、**合约行情/账户/开平仓**、**理财只读与划转 · 全辖 `universal_transfer`/`transfer`**、**合约条件单 / 自动化行 P0 下限**）**已与** **[`specs/openapi/exchange/`](../openapi/exchange/)** **`coobit-public`/`coobit-spot`/`coobit-margin`/`coobit-futures`/`coobit-wealth`/`coobit-automation`** **`paths`** **键** **同窗登记**（**`info.version` 2026-05-09**；**见** [`contract-closure.md`](../requirements/contract-closure.md) **§8**）。**书面延期格**（**CC-P0-02/CC-P1-01**）、**网格/DCA 非目标** **不** **在** **OpenAPI** **扩虚假 PATH** **直至解冻 MR**。

**CC-P0-02 · WebSocket / listenKey（B 阶段文档子集 · 2026-05-09）**：**登记表** **「WebSocket · 用户成交/订单」** 行 **与** [`stream/user-private-ws.yaml`](../openapi/stream/user-private-ws.yaml) **`info.version` 同窗**；**listenKey HTTP** **同窗** **上表** **「WebSocket / 推送」** **与** **[`Runtime/reconciliation.md`](../requirements/Runtime/reconciliation.md)**。**若** **对外承诺 REST 兜底闭合** **且** **依赖私有 WS**：**§1.2 第 6 款**、**`exchangeViewSource` / `SC-OBS06`** **仍须** **实现 MR** **可对签**（**不替代** **延期矩阵格** **之** **所内 PATH 终裁**）。


以下内容 **不替代** 所内 OpenAPI；用于 **Agent 网关 / 运行时** 与 **交易所** 对接时的 **一致约定**，直至正式 spec 链出。

| 主题 | 约定 |
|------|------|
| **鉴权** | **须**使用 **Agent 绑定** 子账户 API Key（**FR-T01**：[`billing.md` §2](../requirements/domains/admin/billing-management/overview.md)、[`consume-and-bill.md`](../requirements/flows/consume-and-bill.md)、[`exchange-agent/overview-legacy-migration.md` §1](../requirements/domains/agent/exchange-agent/overview-legacy-migration.md)）。**与 Coobit 公档一致**：**`X-CH-APIKEY`**；**TRADE / USER_DATA** 须 **`X-CH-SIGN`（HMAC SHA256）**、**`X-CH-TS`**，签名原文 **`timestamp`+`method`+`requestPath`+`body`**；**`recvWindow`** 缺省 **5000 ms**。详见 [OpenApi Basic Information](https://exchangedocsv2.gitbook.io/open-api-doc-v2/openapi-basic-information.md)。 |
| **请求幂等（写）** | **建议**：客户端生成 **`newClientOrderId` / `clientOrderId`**（文档字段名以 [Spot](https://exchangedocsv2.gitbook.io/open-api-doc-v2/spot.md)、[Margin](https://exchangedocsv2.gitbook.io/open-api-doc-v2/margin.md)、[Futures](https://exchangedocsv2.gitbook.io/open-api-doc-v2/futures.md) **各节为准**），**重复提交** **不得** 双倍成交；与 **[`overview.md`](../requirements/domains/agent/exchange-agent/overview.md) `executionId`** **可拆分**：**执行** 级幂等归 Agent，**委托** 级归交易所。 |
| **响应关联** | **须**返回或可解析 **`coobitRequestId`**（或所内等价 **request trace id**），写入 [`observability.md`](../requirements/observability/overview.md) **`trading.exchange_private`** / **`agent.execution.step`**。 |
| **错误体** | **业务拒绝**（精度、余额、权限、黑白名单、**`FEATURE_AGENT_*` OFF** 在所内的映射）**须** **稳定机器码** + 可读 `message`；Agent **映射** 至 **[`overview.md`](../requirements/domains/agent/exchange-agent/overview.md) FR-T05** / **主站 Deeplink**。**HTTP 504**：公档明确 **不可**直接当失败、终态 **UNKNOWN**（须 **[OpenApi Basic Information](https://exchangedocsv2.gitbook.io/open-api-doc-v2/openapi-basic-information.md)** 与客户一致）；**查单对账、幂等重试与用户话术** 见 [`overview.md`](overview.md) **「504 UNKNOWN 与写操作对账」**。**429 / 410 / 418**（频控与封禁）**须**退避或熔断，见同文 **LIMITS**。 |
| **scope 与产品线** | 网关 **在调用前** 结合 **[`config.md`](../requirements/domains/admin/management-console-v1-prd.md) `FEATURE_AGENT_*`** 做 **软拦截**（及早失败）；交易所 **仍可能** 拒绝 **权限不足**（**双保险**）。 |
| **WebSocket / 推送** | **用户成交流 / 订单变更** **若** Agent **长驻监听**依赖：见 [WebSocket](https://exchangedocsv2.gitbook.io/open-api-doc-v2/websocket.md)、[资产变动与订单更新](https://exchangedocsv2.gitbook.io/open-api-doc-v2/websocket-asset-changes-and-order-updates.md)、[合约订单与仓位](https://exchangedocsv2.gitbook.io/open-api-doc-v2/websocket-futures-orders-position.md)；**listenKey / 续期 / 正式 URL** **所内冻结**（同窗 [`exchange-agent/overview` §5（旧 §10.2）](../requirements/domains/agent/exchange-agent/overview.md)、[`monitoring-tasks.md`](../requirements/domains/agent/exchange-agent/monitoring-tasks.md)）。 |
| **Telegram 会话（交界）** | **首版**从 **Telegram** 进站：**Bot API** **须先于**上表 **矩阵 · `W`** 满足 **[`domains/agent/telegram/overview.md`](../requirements/domains/agent/telegram/overview.md) **§2.5 · 类型 A**（总则 **§2～§2.6**，含 **`callback_data` 64B、`sendMessage`/caption 上限、`answerCallbackQuery`**）；**永续市价/限价 · 止盈止损/条件单** **卡面条目** **须** **同窗** **同文 §2.5.4 · §5 **`SC-CH-TG-FUT-01～03`** **与** **[`trade-via-agent.md`](../requirements/flows/trade-via-agent.md)** **专节**；**详** **下文专节**。 |

## REST ↔ WebSocket 对账 PATH（与 Runtime reconciliation 对签）

**规则**：下列 PATH **须**与 **上文「子账户 scope · endpoint 矩阵」** **同行一致**；**真相源次序**（WS 优先或 REST 优先）**不在本文赋值**，见 **[`Runtime/reconciliation.md`](../requirements/Runtime/reconciliation.md) §1 冻结矩阵**。

| 对账用途 | REST PATH（公档锚 · 与矩阵对签） | 矩阵锚 |
|----------|----------------------------------|--------|
| 现货订单终态补全 | `GET /sapi/v2/order`；开放委托 `GET /sapi/v2/openOrders` | 矩阵「币币 · 账户：余额、委托、成交」 |
| 现货成交明细 | `GET /sapi/v2/myTrades`；或 `GET /sapi/v3/myTrades`（所内终裁） | 同上 |
| 杠杆订单 | `GET /sapi/v2/margin/order`；`GET /sapi/v2/margin/openOrders`、`/myTrades` | 矩阵「杠杆 · 杠杆下单、撤单」 |
| 合约订单 | `GET /fapi/v1/order`；`GET /fapi/v1/openOrders` | 矩阵「合约 · 开平仓、撤单…」 |
| 合约成交 | `GET /fapi/v1/myTrades` | 同上 |
| 余额快照 | `GET /sapi/v1/account`（现货）；`GET /fapi/v1/account`（合约） | 矩阵对应只读行 |

**观测**：**可选** 字段 **`exchangeViewSource`**（`WS` \| `REST` \| `MIXED`）**须与** **[`observability/overview.md`](../requirements/observability/overview.md) §2 · `trading.exchange_private`** **同窗**。

## Telegram Bot API（会话 → Agent 网关，与 Coobit 写路径的先后顺序）

**本文**主述 **Agent ↔ Coobit**。**用户触达**另有 **Telegram ↔ Bot API**；本节界定 **与上文「通用契约」表的衔接**。**官方**：[core.telegram.org/bots/api](https://core.telegram.org/bots/api)。**需求正文**：[`telegram.md`](../requirements/domains/agent/telegram/overview.md) **§2.5 · 类型 A、§2～§2.6**（文件实体：**`overview.md`**）。

| 主题 | **约定** |
|------|----------|
| **先于 Coobit `W`** | **未**完成 **§2.5 · 类型 A「确认」** **及** **`exchange-agent` `FR-T02`～`FR-T03`、产品线闸** 前，**禁止**调用 **子账户矩阵** 任一 **写入** endpoint（下单、撤单、条件单创建等）。**`Update` 到达**≠ **交易所已执行**。 |
| **`callback_data` 上限** | **1～64 字节 UTF-8**；确认键 **仅能**承载 **短 id**，**单笔写语义** **须**服务端 **[`telegram.md`](../requirements/domains/agent/telegram/overview.md) §2.6** **`pending confirm`** ↔ **本节「请求幂等（写）」** **分层**。 |
| **正文长度** | **超限** ⇒ **拆分消息、`edit_*`、或 `InlineKeyboardButton.url`（主站/H5 预览）**；避免 **`MESSAGE_TOO_LONG`**。 |
| **`answer_callback_query`** | **须及时**；**可与 Coobit 慢调用解耦**：**先 answer** 结束 spinner，再以 **异步**消息更新会话。 |
| **`send_chat_action`（`typing`）** | **用户 `message` inbound** **后** **须** **尽快**（**≤300ms**）**首次** `typing`；**续发间隔 4500ms**（**产品默认** · **§2.3.1 表**）；**长耗时** **须** **续发** **或** **进度短句** — **同窗** [`telegram/overview` §2.3.1](../requirements/domains/agent/telegram/overview.md) · **`SC-CH-TG-09`**。 |
| **验收** | **[`telegram.md`](../requirements/domains/agent/telegram/overview.md) §5 `SC-CH-TG-08`**（**会话/`callback_data` 边界**）**与 `SC-CH-TG-FUT-01～03`**（**永续订单/条件卡面 · 同窗 §2.5.4**）**+** **本节**网关单测 **可同台**。**ADR**：[`decisions/001-telegram-confirm-before-coobit-write.md`](adr/001-telegram-confirm-before-coobit-write.md)。 |

---

## 其它契约片段（需求叙事 · OpenAPI 终裁仍属所内）

- **`executionId`（单次可计费执行 ID）**：与 **[`exchange-agent/overview.md`](../requirements/domains/agent/exchange-agent/overview.md) `FR-T01`**（同窗 [`billing.md`](../requirements/domains/admin/billing-management/overview.md) **§2**、[`consume-and-bill.md`](../requirements/flows/consume-and-bill.md)）、**`billing.md` FR-B05**（`idempotencyKey` 拼接串）一致；内部 API **须**透传至计费与日志
- **用户 Billing 流水列表 / 详情 / 个人 CSV**：行为见 [`billing.md`](../requirements/domains/admin/billing-management/overview.md) **FR-B12、FR-B15**；**月度账单** **FR-B16**（**`SC-B14`**）。

### 运营侧 Agent Management API（`admin/agents/*` · PATH 示意 · OpenAPI 终裁）

**鉴权**：运营 **SSO + IAM**（模板/实例/Runtime **分角色**：如 **`AGENT_TEMPLATE_EDITOR`**、**`INSTANCE_OPS`**、**`RUNTIME_OPERATOR`** — 所内 RBAC 终裁）；**写路径须审计**（同窗 **`agent-management/functions.md`**、**`observability` `admin.audit`**）。

与 **[`agent-management/functions.md`](../requirements/domains/admin/agent-management/functions.md) `FR-AM-*`**、**`FR-MC101～114`**、**I02 `code` `enum`**（**§7.1**）、**[`config.md` · IA](../requirements/domains/admin/agent-management/config.md)** 同窗；**PATH** 所内可 **合并 resource**，**不得弱化**下列能力面。**`CC-P0-01`（模块一登记表行）**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| 模板列表 / 筛选 | `GET` | `/api/v1/admin/agents/templates` | **FR-AM-T01** · Query：名称、`templateId`、启用状态等 |
| 创建模板 | `POST` | `/api/v1/admin/agents/templates` | **T02** · 返回 `templateId`、**草稿**态 |
| 模板详情 / 更新 | `GET` / `PATCH` | `/api/v1/admin/agents/templates/{templateId}` | **T03** · 乐观锁 `If-Match`；**已发布**走 **新版本**草稿 |
| 模板克隆 | `POST` | `/api/v1/admin/agents/templates/{templateId}/clone` | **T09** |
| 草稿删除 | `DELETE` | `/api/v1/admin/agents/templates/{templateId}`（**或** `/draft` 子资源） | **T10** · 仅 **DRAFT** |
| 发布 / 版本履历 | `POST` / `GET` | `/api/v1/admin/agents/templates/{templateId}/publish`、`/versions` | **T03/T04～T07** 封装 **因 BFF 而异** |
| 实例列表 | `GET` | `/api/v1/admin/agents/instances` | **I01** · 与 Runtime 摘要、子账户绑定 **同窗** |
| 创建实例 | `POST` | `/api/v1/admin/agents/instances` | **I02** · **准入+计费** 失败码 **§7.1** |
| 实例详情 / 更新 | `GET` / `PATCH` | `/api/v1/admin/agents/instances/{instanceId}` | **I03、I05** |
| 子账户绑定 | `POST` / `DELETE` | `/api/v1/admin/agents/instances/{instanceId}/binding` | **I04** |
| 删除实例 | `DELETE` | `/api/v1/admin/agents/instances/{instanceId}` | **I06** · 在途校验 |
| Runtime 单实例 | `POST` | `/api/v1/admin/agents/instances/{instanceId}/runtime/{action}` | **`action`**：`pause` · `resume` · `stop` · `start` — **R01～R05** |
| Runtime 批量 | `POST` | `/api/v1/admin/agents/instances/runtime/batch` | **R06** · Body：`instanceId[]`、`action` |
| 实例列表导出 | `POST` / `GET` | `/api/v1/admin/agents/instances/exports`、`/exports/{taskId}` | **I08** · 大表 **202** + **D-18** 同窗 |

**前缀 `/api/v1/admin/...`** 仅为示意。**日志深链（L01～L03）** 可 **复用** **`admin/observability/*`** **query**（`instanceId`）— **同窗** **模块八**。

### 运营侧 Prompt Management API（`admin/prompt-packs/*` · PATH 示意 · OpenAPI 终裁）

**鉴权**：**SSO + IAM**（**Editor / Approver** 分权，见 [`prompt-management/functions.md`](../requirements/domains/admin/prompt-management/functions.md) **§2.1**）；**写路径须审计**。

与 **`FR-PM01～08`**、**`FR-MC201～207`**、**[`runtime-injection.md`](../requirements/domains/admin/prompt-management/runtime-injection.md)**、**[`observability` §2.3](../requirements/observability/overview.md)** 同窗；**`promptPackVersion` 单调**、**`LOCKED`**、**拼装/占位符闸** **不得弱化**。**`CC-P0-01`（模块二）**；**`CC-P1-04`** 填链对象。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| 包列表（按类型 `SYSTEM`/`TRADING`/`ANALYSIS`/`SAFETY` 等） | `GET` | `/api/v1/admin/prompt-packs` | **FR-PM02～04** · Query：`promptPackType`、`scenarioId` 等。**`scenarioId` 与寄存器可追溯** **`MUST`**。**不得**仅以 **枚举类型**筛选替代 **scenario** 治理能力（[`config.md` §1.1a](../requirements/domains/admin/prompt-management/config.md)、[`functions.md` §1.2 **`PM-C15`**](../requirements/domains/admin/prompt-management/functions.md)） |
| 创建草稿包 | `POST` | `/api/v1/admin/prompt-packs` | **新 `promptPackId`** |
| 包详情 / 更新草稿 | `GET` / `PATCH` | `/api/v1/admin/prompt-packs/{promptPackId}` | **`If-Match`/`etag`** · **PM-C03** |
| 版本履历 | `GET` | `/api/v1/admin/prompt-packs/{promptPackId}/versions` | 只读时间线 |
| 发布 | `POST` | `/api/v1/admin/prompt-packs/{promptPackId}/publish` | **FR-PM07** · 发布后 **LOCKED** 新版本生效 |
| 回滚生效指针 | `POST` | `/api/v1/admin/prompt-packs/{promptPackId}/rollback` | **指定 `promptPackVersion`** |
| Few-shot 示例子资源 | `GET` / `POST` / `PATCH` / `DELETE` | `/api/v1/admin/prompt-packs/{promptPackId}/few-shots` **或** `/few-shots/{id}` | **FR-PM05** |
| 沙箱运行 | `POST` | `/api/v1/admin/prompt-packs/sandbox/runs` | **FR-PM06** · **隔离**生计费 |
| 运行时生效读（BFF / 内部） | `GET` | `/api/v1/internal/prompts/effective` **或** 网关 BFF 同窗路径 | **FR-PM08** · **仅 `PUBLISHED`**；**禁**草稿进用户链路 |

**前缀**：表内 **`/prompt-packs`** 与 **`/internal/prompts/effective`** 所内可 **合并或改名** — **不得弱化**上表 **Then** 与 **PM-C01～C15**。

#### Skill Operation Spec API（`admin/skill-specs/*` · FR-T11 · 同窗 `prompt-management.yaml`）

**正文 SSOT**：Git [`skill-specs/`](../requirements/skill-specs/) · Publish 规则 [`PUBLISH.md`](../requirements/skill-specs/PUBLISH.md) · Schemas [`skill-operation-spec-schemas.yaml`](../openapi/components/skill-operation-spec-schemas.yaml)。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| 技能规范列表 | `GET` | `/api/v1/admin/skill-specs` | **`skillId`** 与 **`trade-assistance` §4** 同窗 |
| 摘要 / 版本履历 / 正文 | `GET` | `/api/v1/admin/skill-specs/{skillId}`、`/versions`、`/versions/{skillSpecVersion}` | **`bodyMarkdown`** = 单文件 §1～§6 **全文** |
| 发布 | `POST` | `/api/v1/admin/skill-specs/{skillId}/publish` | **单调 `skillSpecVersion`** · CI `check_skill_contract_complete.py` |
| 运行时读 | `GET` | `/api/v1/internal/skills/effective` | **`read_skill_operation_spec`** · 仅 **PUBLISHED** · 未知版 → **`PROMPT_SKILL_REF_INVALID`** |

#### 内部 · Agent 编排 Trade Resolver API（`internal/agent/orchestration/*` · INV-008）

**OpenAPI**：[`internal/agent-orchestration.yaml`](../openapi/internal/agent-orchestration.yaml) · Schemas [`orchestration-runtime-schemas.yaml`](../openapi/components/orchestration-runtime-schemas.yaml)。**TS 同窗**：`src/admin/src/productionRuntime/internalTradeResolverAdapter.ts`。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| L0 缺参聚合（闪兑 / 限价） | `POST` | `/api/v1/internal/agent/orchestration/trade-resolver` | **Body**：`mode` + `slots` + `options`；**Response**：`output: AgentTradeResolverOutput`；**Then** `missing` 非空 **不得** 载货类型 A |

### 运营侧 Tool Management API（`admin/tools/*` · PATH 示意 · OpenAPI 终裁）

**鉴权**：**`tool.*` 资源**（[`tool-management/functions.md`](../requirements/domains/admin/tool-management/functions.md) **§2.1**）。**Enable** **须**满足 **矩阵非 `TBD` 或书面延期**（**SC-MCV1-05**）。

与 **`FR-TM01～05`**、**`FR-MC301～305`**、**[`trade-assistance` §8](../requirements/domains/agent/exchange-agent/trade-assistance.md)**、**[`runtime-contract.md`](../requirements/domains/admin/tool-management/runtime-contract.md)** 同窗。**`CC-P0-01`（模块三）**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| Registry 镜像列表 | `GET` | `/api/v1/admin/tools/registry` | **FR-TM01** · 过滤 **域/风险级/PATH 状态** |
| 单条 Registry 镜像 | `GET` | `/api/v1/admin/tools/registry/{toolId}` | **矩阵摘要、Owner** |
| Schema 运营视图 | `GET` | `/api/v1/admin/tools/{toolId}/schema` | **FR-TM02** · **只读或可写边界 OpenAPI 冻结** |
| 调用权限策略 | `GET` / `PUT` / `PATCH` | `/api/v1/admin/tools/{toolId}/policy` | **FR-TM03** · **`denyByDefault`** |
| 启用 | `POST` | `/api/v1/admin/tools/{toolId}/enable` | **FR-TM04** · **门槛** §2.4 |
| 停用 | `POST` | `/api/v1/admin/tools/{toolId}/disable` | **FR-TM04** |
| 日志协查入口（重定向或嵌入） | `GET` | `/api/v1/admin/tools/{toolId}/observability-link` **或** Query 模板 | **FR-TM05** · 实参 **`executionId`/`userId`** |

### 运营侧 Access Control API（`admin/access-control/*` · PATH 示意 · OpenAPI 终裁）

**鉴权**：**合规 / 运营** 分角色（[`access-control/rules.md`](../requirements/domains/admin/access-control/rules.md) **导出脱敏、审批** **同窗**）。**`AGENT_MIN_VIP_TIER`** 写路径 **须与** [`keys.md` §3](../requirements/domains/admin/trading-agent-config/keys.md) **同窗 MR**。

与 **`FR-MC601～607`**、**[`eligibility-runtime.md`](../requirements/domains/admin/access-control/eligibility-runtime.md)**、**[`agent-management` §7.1 `code`](../requirements/domains/admin/agent-management/functions.md)** 同窗。**`CC-P0-01`（模块六）**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| 灰度 / 渠道策略 | `GET` / `PATCH` | `/api/v1/admin/access-control/rollout` | **FR-MC601** · **读侧 SLA** **SC-AC-04** |
| 白名单集合 | `GET` / `POST` | `/api/v1/admin/access-control/whitelist` | **FR-MC602** |
| 白名单条目 | `GET` / `PATCH` / `DELETE` | `/api/v1/admin/access-control/whitelist/{entryId}` | **导入导出** **同窗 `rules`** |
| 封禁 | `GET` / `POST` | `/api/v1/admin/access-control/bans` | **FR-MC603** |
| 单条封禁 | `GET` / `PATCH` / `DELETE` | `/api/v1/admin/access-control/bans/{banId}` | **FR-MC603～604** · 时效 |
| KYC / 合规只读镜像 | `GET` | `/api/v1/admin/access-control/users/{userId}/kyc-mirror` | **FR-MC605** · **禁止**写回 |
| 地域 / 风险测评（若 V1 启用） | `GET` / `PATCH` | `/api/v1/admin/access-control/region-policy` | **FR-MC606** · **可选** |
| VIP 最低门槛 | `GET` / `PATCH` | `/api/v1/admin/access-control/membership/min-vip-tier` | **FR-MC607** · **或** **并入** [`trading-agent-config/flow`](../requirements/domains/admin/trading-agent-config/flow.md) **全局 bundle**（**OpenAPI 二选冻结**） |

### 运营侧用户协查摘要 API（`admin/users/*` · PATH 示意 · OpenAPI 终裁）

与 **[`management-console-v1-prd` §8.2](../requirements/domains/admin/management-console-v1-prd.md)**、**[`access-control` 归因](../requirements/domains/admin/access-control/overview.md)** 同窗；**字段下限** 见 **「待补充」** 首条与 **`config.md` FR-M07**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| 单用户 Agent 协查摘要 | `GET` | `/api/v1/admin/users/{userId}/agent-summary` | **`agentState`、`recentCharges`（≤5）** 等；未知用户 **404** / `ADMIN_USER_NOT_FOUND` |

### 用户侧 Agent 开通 / 绑定 API（`me/agent/*` · PATH 冻结 · OpenAPI 终裁）

与 **[`user/onboarding.yaml`](../openapi/user/onboarding.yaml)**、[`initialization-flow.md`](../requirements/domains/agent/onboarding/initialization-flow.md) **§1.2**、[`web/agent-onboarding.md`](../requirements/domains/web/agent-onboarding.md) **`FR-WEB06`**、[`openapi/components/onboarding-schemas.yaml`](../openapi/components/onboarding-schemas.yaml) **`TradingApiBindRejectCode`** **同窗**。**绑定页明示保存** **须** **先于** **实例创建 / 绑定** **完成交易所侧下限校验**；失败 **`409`** **`Problem.code`** **禁止** **吞码** **换笼统文案**。

| 用途 | 方法 | 路径（冻结 · `user/onboarding.yaml`） | 说明 |
|------|------|----------------------------------------|------|
| 开通与运行时摘要 | `GET` | `/api/v1/me/agent/status` | **`FR-ON03`** 等；响应 **`MeAgentStatus`** |
| **提交子账户 UID + Key/Secret · 服务端校验后绑定** | `POST` | `/api/v1/me/agent/bindings/trading-api` | Body：**`TradingApiBindRequest`**（**`idempotencyKey`、`agentSubAccountUid`**（**绑定页必填**，与交易所 **`subUid`** 同窗）、**`apiKey`、`apiSecret`**）；成功 **`TradingApiBindResult`**；**校验失败 `409`** **`TradingApiBindRejectCode`**（含 **`AGENT_BIND_SUBACCOUNT_UID_MISMATCH`**） |
| 吊销绑定 | `DELETE` | `/api/v1/me/agent/bindings/trading-api` | **204**；审计 **无 Secret** |
| Legacy 一键确认（幂等） | `POST` | `/api/v1/me/agent/provisioning/confirm` | **首选**配置页走上一行；**同窗 `ProvisioningConfirmRequest`** |
| 阻断恢复 Deeplink 提示 | `GET` | `/api/v1/me/agent/recovery/deeplink` | **`FR-T05`**；Query **`reason`** |

**前缀 `/api/v1/me/agent/...`** **终裁以 YAML `paths` 为准**；**Agent 产品线 BFF** **可** **合并 host**，**不得弱化** **§1.2** **校验语义（含 **`agentSubAccountUid`** **与 **`subUid`** **一致性）**。

#### 绑定保存 · 交易所探测矩阵（`POST .../bindings/trading-api` · 建议实现次序）

**前提**：绑定服务 **持有** **用户提交的 **`agentSubAccountUid`** **及** **子账户 **`apiKey`/`apiSecret`** **成对** **短时** **用于向交易所网关探测**（**标准绑定路径二者均不可缺省**；**禁止**弱化「仅 Key、无 Secret」；**禁止**落运营摘要 **Secret**）。**终端用户** **不须登录 Coobit 交易所主站**（[`agent-onboarding.md`](../requirements/domains/web/agent-onboarding.md) **`FR-WEB01`**）；**母账户列表/状态类 PATH** **须由服务端调用身份（母账户代理、运营注入等，`design` 冻结）** **执行**，**不得弱化** **§1.2 下限校验**。下列 PATH **均为** [**现货网关**](https://exchangedocsv2.gitbook.io/open-api-doc-v2/openapi-basic-information.md) **示例 host** **`openapi.xxx.xx`** **之 `requestPath`**；**正式 host** **所内冻结**。

**权限位（公档）**：[`Sub Account · Query Sub Account API Key`](https://exchangedocsv2.gitbook.io/open-api-doc-v2/sub-account.md) **响应 `authority`** — **逗号分隔**：**`0`** 允许读、**`1`** 币币、**`2`** 杠杆、**`3`** 合约（另有 **`4`** 提币、**`8`** 子母账户等）。**`FR-WEB06` ③** **下限**：**须同时包含 `1`、`2`、`3`**（**币币 / 杠杆 / 合约**）；**`0`** **建议保留** **以利账户类只读探测。** **若产品口径「API 交易」** **与公档某独立枚举同窗**：**以所内 ENUM/OpenAPI **补充 MR** **终裁**；此前 **可等价** **为** **`authority`** **含 **`1`** **且** **签名 **`USER_DATA`/`TRADE`** **类 PATH **不因 Key 级闸整体禁用而失败**（与 **[Errors](https://exchangedocsv2.gitbook.io/open-api-doc-v2/errors.md)** **`-2015` 等 **对签**）。

| 次序 | `FR-WEB06` / `initialization-flow §1.2` 项 | 推荐探测（调用身份） | PATH（公档 · Sub Account） | 失败 **`Problem.code`**（首选） |
|------|-------------------------------------------|----------------------|---------------------------|--------------------------------|
| 1 | **① Key 须归属子账户且在母账户可见** | **主账号维度 OpenAPI**（**SSO 映射之母账户 API Key** **或** **所内「母账户代理签名」** **冻结其一**）：按 **`subUid`**（可取用户提交的 **`agentSubAccountUid`** **或** **枚举母账户下子账户 **`subUid`**）拉子账户 API 列表并 **匹配用户粘贴的 `apiKey`**（列表项 **通常不含 Secret**；**子账户签名类探测（矩阵「—」行）及 Coobit 扩展归属接口** **须使用用户请求体内的 `apiKey`/`apiSecret` 成对**，以完成可归因校验） | **`POST /sapi/v1/sub_user/sub_account_api/list`**（Body **`subUid`**）— [`sub-account.md`](https://exchangedocsv2.gitbook.io/open-api-doc-v2/sub-account.md) **Sub Account API Key Management** | **`AGENT_BIND_KEY_NOT_SUBACCOUNT`**（列表 **无匹配** **或** **Key 落在主账户 Key 空间） |
| 1b | **①-b **`agentSubAccountUid`** **须与 Key 命中之子账户 **`subUid`** **一致** | **①** **命中 **`apiKey`** **后**，取得 **`subUid`** **（列表请求体所用 **`subUid`** **或与 **`apiKey`** **同窗之子账户标识）；与用户 **`TradingApiBindRequest.agentSubAccountUid`** **规范化一致比对** | （数据源自 **①**，**无额外 PATH**） | **`AGENT_BIND_SUBACCOUNT_UID_MISMATCH`** |
| 2 | **② 子账户整体启用** | 同上 **母账户维度** | **`POST /sapi/v1/sub_user/get_sub_user_List`** — 响应 **`subUserList[].status`**（**`1`** **启用** **`0`** **禁用**） | **`AGENT_BIND_SUBACCOUNT_DISABLED`** |
| 3 | **③ 权限全开（API 交易 + 币币 + 杠杆 + 合约）** | **由 **①** 列表项** **`authority`** **解析**（**无需额外 PATH** **若列表已含权限串**）；**缺项** **填充 **`details.missingPermissions[]`** **(`API_TRADING`/`SPOT`/`MARGIN`/`FUTURES`)** **同窗 **`onboarding-schemas`** | （数据源自 **`apiList[].authority`** **同窗上表） | 单项：**`AGENT_BIND_*_PERMISSION_DISABLED`**；多项：**`AGENT_BIND_PERMISSION_INCOMPLETE`** |
| — | **兜底探测（可选）** | **用户提交的子账户 **`apiKey`/`apiSecret` 成对** **签名**：轻量 **`USER_DATA`** **调用** **校验 Key **本身有效且非吊销 | 例如 **`GET /sapi/v1/account`**（**同窗** **上文「子账户 scope · endpoint 矩阵」· 币币账户只读**） | **不与 **① **重复判主账户** **时**：可归 **`AGENT_BIND_KEY_NOT_SUBACCOUNT`** **或** **交易所 **`message`** **映射后的权限类码** |

**规则**：**①·①-b·②** **依赖服务端交易所网关调用身份**（**母账户代理 / 运营注入、`design` 冻结**），**与 **`FR-WEB01`** **一致**：**终端绑定页** **不须用户进入交易所主站**；**禁止** **在未使用用户提交的 `apiSecret` 完成可归因签名（或未走所内冻结之母账户调用身份 / 归属接口）的前提下，仅凭 `apiKey` 字符串猜测母账户拓扑**。**③** **以 **`authority`** **为 **SSOT** **优先**；**与 **`missingPermissions`** **逐项对齐 **`meAgent.ts`** **中文映射**。矩阵 **`PATH`** **若与所内私有化变更不一致**：**以所内 OpenAPI **为准 **并 **回填本表**（**`CC-P0-01`** **登记表 **「Agent 绑定 · `me/agent/*`」** **行同窗**）。

### 用户侧 Billing API（PATH 示意 · OpenAPI 终裁）

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| 个人月度账单列表 | `GET` | `/api/v1/me/billing/statements` 或所内等价 | **`FR-B16`**：**`year/month`（或同窗账期锚）**，**分页 `SC-B13`** |
| 单月月度账单导出 | `GET` | `/api/v1/me/billing/statements/{periodId}/export` 或同窗 | **FR-B16**：大结果异步 **202** + 任务（**D-18**，同窗 **FR-B15** CSV） |
| 扣费流水列表 | `GET` | `/api/v1/me/billing/charges` 或所内等价 | Query：**时间起止**、**状态分组**、`billingTraceId` 精确等，与 **FR-B12** AND 语义一致；**`pageSize` ≤ 200**，越界 **400**（**SC-B13**） |
| 单条流水详情（若与列表分接口） | `GET` | `/api/v1/me/billing/charges/{billingTraceId}` | **须**校验归属 **当前登录用户** |
| 个人账单 CSV | `GET` 或 `POST` | `/api/v1/me/billing/charges/export` | **FR-B15**；大结果 **异步**（**D-18**）时可 **202** + 任务 id + 短时下载 URL |

**前缀 `/api/v1/me/...`** 仅为示意；所内网关路径冻结后 **替换本表**并链接 OpenAPI。

### 内部 · Token 账务扣减 API（**轨 A 对读** · 结算服务 / BFF · PATH 示意）

**说明**：**Agent 消耗 S5 主链** **见下文** **「内部 · 商业轨 / 权益核销」**（**`SC-B20`**）。**本节** **保留** **历史 Token **`CHARGE`** **契约** — **CC-P0-03**。

**调用方**：**计费结算服务**（**非** Agent 消耗默认路径），**非**终端用户、**非**管理台浏览器直连。**须**与 **`FR-B05`、**`FR-B11`/`FR-B14`、**`SC-B08`** 对签；落账 **`ledgerEntryType=CHARGE`**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| 执行单笔扣费落账 | `POST` | `/api/v1/internal/billing/charges` 或 **gRPC 同窗** | **Body**：`executionId`、`idempotencyKey`、计量字段、子账户/账本锚点等 — **OpenAPI 终裁**；**重复键**须 **可安全重放**得同一 **`billingTraceId`**（**`SC-B08`**） |
| 查询扣费结果（可选，与队列解耦） | `GET` | `/api/v1/internal/billing/charges/by-idempotency` 或同窗 | **Query**：`idempotencyKey` 或 `executionId`；**用于**对账与 **UNKNOWN** 恢复 |
| 执行退款账务（服务侧，非管理台表单） | `POST` | `/api/v1/internal/billing/refunds/apply` 或同窗 | **由** **`FR-MC505` 审批通过后** 的 **作业**调用；**`refundIdempotencyKey`**（**`SC-B15`**）；**与 `admin/billing/refunds`** **禁止**双重标准 |

**前缀 `/api/v1/internal/...`** 仅为示意；**可与所内 service mesh 命名空间路径合并**，**不得**暴露公网 **without** 网关策略。

### 内部 · 商业轨 / 权益核销（**Agent S5 主链** · OpenAPI）

**SSOT**：[`commerce-model.md`](../requirements/domains/admin/billing-management/commerce-model.md) **§4～§5.3**；**FR/SC**：[`billing-management/functions.md` §5](../requirements/domains/admin/billing-management/functions.md)。**关单**：**`contract-closure` §8**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| **核销订阅/包额度** | `POST` | `/api/v1/internal/billing/entitlements/debit` 或同窗 | **Body**：`executionId`、`idempotencyKey`、`capabilitySkuId`/`packGrantId` 等 — **OpenAPI MR**；**`SC-B20`** **幂等** |
| **查询权益余额（服务侧）** | `GET` | `/api/v1/internal/billing/entitlements/balance` 或同窗 | **Query**：`userId`；与 **消费主路径 S2** **同窗** |
| **加购包入账（支付回调作业）** | `POST` | `/api/v1/internal/commerce/pack-grants/apply` 或同窗 | **FR-B18** **后台链路** · **PSP** **`design`** **同窗** |

**用户侧 `me/commerce/*`（订阅展示、买包、剩余额度 — FR-B17）**：**OpenAPI** [`user/commerce-me.yaml`](../openapi/user/commerce-me.yaml)（**`GET …/me/commerce/entitlements/summary`**）；**买包 PSP** **PATH** **另见** **实现 MR** · **同窗** **`user/onboarding`** **BFF 划分**。

### 运营侧 AI Settings API（`admin/ai/*` · PATH 示意 · OpenAPI 终裁）

**鉴权**：运营 **SSO + IAM**（建议窄角色 **`AI_SETTINGS_OPERATOR`** vs `READ_ONLY`，与 [`ai-settings/config` §3](../requirements/domains/admin/ai-settings/config.md) **同窗**）；**不得**经本 API **返回** **LLM Provider 完整 API Key**（**仅** `secretRef` 或「已配置」语义）。

与 **[`ai-settings/functions.md`](../requirements/domains/admin/ai-settings/functions.md) `FR-MC401～408`**、**[`rules.md`](../requirements/domains/admin/ai-settings/rules.md)**、**[`integrations/llm/provider-routing.md`](../requirements/integrations/llm/provider-routing.md)**、**[`Runtime/recovery.md`](../requirements/Runtime/recovery.md)** 同窗冻结；**PATH** 所内可合并为更少 resource，**不得**弱化下列 **能力面**。**`CC-P0-01`**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| Provider 列表 / 单条 | `GET` | `/api/v1/admin/ai/providers`、`/providers/{providerId}` | **FR-MC401** · 列表/详情仅 `secretRef` 或占位，**不含 Secret 明文** |
| Provider 创建 / 更新 | `POST` / `PATCH` | `/api/v1/admin/ai/providers`、`/providers/{providerId}` | **Body**：`baseUrl`、`secretRef` 等；乐观锁 `If-Match` 与其余 **`admin`** 写路径同窗 |
| 模型目录 | `GET` | `/api/v1/admin/ai/models` | **FR-MC402** · Query `providerId` 可选 |
| 模型元数据 PATCH | `PATCH` | `/api/v1/admin/ai/models/{modelId}` | 启用/下架/上下文窗；与 [`agent-management/config`](../requirements/domains/admin/agent-management/config.md) 中 **`defaultModelRef` 允许集** 同窗 |
| 网关默认 profile | `GET` / `PATCH` | `/api/v1/admin/ai/defaults` 或 `/gateway-profile` | **FR-MC403～406**、**FR-MC408**（**编排执行预算** · 见下文专节）· Body/响应 **`AiGatewayDefaults.orchestrationExecutionBudget`** — **`ai-settings-schemas`**；**schema OpenAPI 冻结** |
| 手动 Health 探针 | `POST` | `/api/v1/admin/ai/providers/{providerId}/health` | **FR-MC407** · **202（异步作业）或 200（同步）同窗** SLA |
| Health 策略 | `GET` / `PATCH` | `/api/v1/admin/ai/health-policy` 或同窗 | **FR-MC407** · 阈值/周期；可与 **`网关默认 profile`** **`design`** **同窗合并**为一资源 |

**前缀 `/api/v1/admin/...`** 仅为示意。**`modelId`/`providerId`** **字段名** **须与** **[`observability/overview` §2](../requirements/observability/overview.md)**、**FR-MC804** **一致**。

#### 编排执行预算（`FR-AO06` / `FR-MC408` · OpenAPI）

**需求 SSOT**：[`execution-lifecycle.md`](../requirements/domains/agent/agent-orchestration/execution-lifecycle.md) **§4**、[`tool-management/runtime-contract.md`](../requirements/domains/admin/tool-management/runtime-contract.md) **§3.1**。**运营可读写过** **[`admin/ai-settings.yaml`](../openapi/admin/ai-settings.yaml)** **`GET|PATCH /api/v1/admin/ai/defaults`** **内嵌** **`orchestrationExecutionBudget`**（**`OrchestrationExecutionBudget`**）：

| 字段 | 约束 | 说明 |
|------|------|------|
| **`maxToolCallsPerExecution`** | `integer` **≥ 1** **必填**（对象存在时） | **达终态**之 **逻辑** **工具调用** **上限**；**`RETRYING`** **同** **`toolCallSeq`** **计一次** |
| **`maxOrchestrationStepsPerExecution`** | `integer` **≥ 1** **必填**（对象存在时） | **`agent.orchestration.step`**（**或** **等价 `stepSeq`**）**单调步数** **上限** |
| **`maxModelTurnsPerExecution`** | `integer` **≥ 1** **或** **`null`** | **可选**；**`null`** **=** **不设** **独立模型回合顶**（**与** **计费回合定义** **同窗** **后再启用**） |

**默认值**：**所内** **首版** **建议** **`maxToolCallsPerExecution`≤64**、**`maxOrchestrationStepsPerExecution`≤64**（**经** **容量/P99** **MR** **可收紧**）；**具体默认** **以** **配置快照 / 租户覆盖** **终裁**。**可合并窗口内**：**`GET /api/v1/admin/ai/defaults`** **须** **返回** **可审计** **之** **`orchestrationExecutionBudget`**（**或** **文档化** **等价** **多租户默认**）；**此前** **Runtime** **可** **以内置常量兜底** **满足** **`FR-AO06`** **下限** — **兜底值** **所内** **须** **与** **`ai-settings-schemas`** **默认** **对签**。

**用户触达（超限）**：**`stableReason`** **须** **可** **取** **`ORCHESTRATION_BUDGET_EXCEEDED`**（**字符串** **常数**）；**`billCode`** **与** **`FR-T05`** **族** **映射表** **由** **BFF/Telegram** **OpenAPI** **冻结** — **勿** **与** **管理台 I02 **`AGENT_*`** **混列** **同一 enum**（**`SC-OBS07`/`SC-AO-08`** **抽检**）。

### 运营侧 Billing API（`admin/billing/*` · PATH 示意 · OpenAPI 终裁）

与 **[`billing-management/functions.md`](../requirements/domains/admin/billing-management/functions.md) `FR-MC501～508`**、**[`rules.md`](../requirements/domains/admin/billing-management/rules.md)（IAM/`billing.export`、水印、双签、**§流水 ledger 项类型 **`CHARGE`/`REFUND`**）** 同窗冻结；**PATH 列**所内可合并为更少 resource，**不得**弱于下列 **能力面**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| 计费健康摘要 | `GET` | `/api/v1/admin/billing/summary` 或所内等价 | **`FR-MC501`**：`BILLING_MODE`、**`effectiveMinChargeUsdt`**、**`BILLING_TOKEN_RATE`** 生效摘要等 |
| Token 费率与最小扣费 | `GET` / `PATCH` | `/api/v1/admin/billing/pricing` 或同窗 | **`FR-MC502`**；写路径 **双签/审计** 以 **同窗 `rules`** 为准；**`src/admin` Demo** **无**独立定价运营页（**keys/所内** 或 BFF 探针） |
| 单笔协查 | `GET` | `/api/v1/admin/billing/traces`（query）或 `/.../traces/{billingTraceId}` | **`FR-MC503`**：与 **`userId` / `executionId` / `billingTraceId`** 串联 observability |
| 平台流水列表 | `GET` | `/api/v1/admin/billing/charges` 或所内等价 | **`FR-MC504`**；筛选维与 **`FR-MC507` 导出** **同源**；**无 Secret** |
| 退款 / 冲正 | `POST` | `/api/v1/admin/billing/refunds` 或同窗 | **`FR-MC505`**：绑定原 **`billingTraceId`**、**`refundIdempotencyKey`**（**`SC-B15`**） |
| 扣费网关错误聚合 | `GET` | `/api/v1/admin/billing/gateway-errors` 或同窗 | **`FR-MC506`**；下钻 **FR-MC503** |
| 异步导出任务 | `POST` / `GET` | `/api/v1/admin/billing/exports`、`/exports/{taskId}` 或同窗 | **`FR-MC507`**：流水 CSV、**自然月 rollup**（与 **FR-B16** 字段同窗）；大结果 **202** + **D-18** |
| 财务对账文件 | `GET` 或 `POST` | `/api/v1/admin/billing/reconciliation-exports` 或同窗 | **`FR-MC508`**；与 **`D-12`** 对签字段同窗 |

**Phase 2 · `admin/billing/commerce/*`（FR-MC509～512）**：**OpenAPI** 冻结 **`commerce_phase2` tag**，同窗 [`admin/billing-admin.yaml`](../openapi/admin/billing-admin.yaml) — **`GET`/`PATCH`** `/api/v1/admin/billing/commerce/capability-catalog`（**SKU/Capability 矩阵**）、**`GET`** `/api/v1/admin/billing/commerce/users/{userId}/overview`、**`GET`** `/api/v1/admin/billing/commerce/revenue-export-template`、**`GET`** `/api/v1/admin/billing/commerce/quota-blocked-summary`。需求 SSOT：[`functions` §5](../requirements/domains/admin/billing-management/functions.md)。

**前缀 `/api/v1/admin/...`** 仅为示意；**与 `me/billing`、内部扣减、`keys`、Coobit 账本 PATH** **禁止**Silent 分叉字段语义（**`CC-P0-03`**）。

### 运营侧 Logs & Observability API（`admin/observability/*` · PATH 示意 · OpenAPI 终裁）

**鉴权**：运营 **SSO + IAM**（[`observability-management/rules.md`](../requirements/domains/admin/observability-management/rules.md)：**`READ_ONLY`** **vs** 支持 / **L2** 下钻）；**不得**经本 API **返回** **用户 Prompt/Secret 全文**（**默认裁剪**）。

与 **[`observability-management/functions.md`](../requirements/domains/admin/observability-management/functions.md) `FR-MC801～807`**、**[`observability/overview.md`](../requirements/observability/overview.md) §2～§2.4**（**含** **主态迁移 Trigger 映射** **与** **`transitionTrigger`**）**与** **`FR-MC503`（`billingTraceId` join）** **同窗冻结**；**PATH** 所内可 **合并为统一 search**，**不得**弱化下列 **能力面**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| **执行记录列表** | `GET` | `/api/v1/admin/observability/executions` 或同窗 | **控制台** **`runtime.executions`**：**分页** **`ObservabilityExecutionSummary`**（intent、运行态、阶段、outcome、时间等）；**详** **时间线** **见** **下行**；**与** **`FR-MC802`** **协查** **可** **同窗** **筛** **`userId`/时间窗** |
| 按 `executionId` 时间线 | `GET` | `/api/v1/admin/observability/executions/{executionId}/timeline` 或同窗 | **`FR-MC801`**：**按 ts 排序** 的事件行（类型、键、摘要）；**OpenAPI schema 与 **`observability` §2** **列集同窗**；**主态边审计** **见** **§2.4** **与** **`ObservabilityTimelineEvent.transitionTrigger`**；**控制台 UX** **下限** [`observability-management/functions.md`](../requirements/domains/admin/observability-management/functions.md) **`SC-OM-04`** |
| 联合搜索 | `GET` | `/api/v1/admin/observability/search` 或 `/events` | **`FR-MC802`**：Query **`userId`**、时间窗、可选 **`billingTraceId`**、`toolId`、`scenarioId` 等；**`pageSize` 上界 **`design`/OpenAPI 冻结** |
| 工具调用明细 | `GET` | `/api/v1/admin/observability/executions/{executionId}/tool-calls` 或同窗 | **`FR-MC803`**：**`toolId`**、**`toolCallSeq`**、**`invocationState`** |
| LLM 计量明细 | `GET` | `/api/v1/admin/observability/executions/{executionId}/llm` 或同窗 | **`FR-MC804`**：**`modelId`**、token 摘要；**禁止**默认返回 **messages 全文** |
| 审计日志导出任务 | `POST` / `GET` | `/api/v1/admin/observability/audit-exports`、`/audit-exports/{taskId}` 或同窗 | **`FR-MC806～807`**：大结果 **202** + **D-18** 同窗；**水印 / 短时 URL** |

**`traceId` / `spanId`**：若采用 **W3C Trace Context**，**可**作为 **可选筛选或响应元数据**；**产品主锚仍为 **`executionId`** **（[`observability-management/config` §4](../requirements/domains/admin/observability-management/config.md)、[`tracing.md`](../requirements/observability/tracing.md)**）**。

### 运营侧 Telegram 渠道运维 API（`admin/channels/telegram/*` · PATH 示意 · OpenAPI 终裁）

**鉴权**：运营 **SSO + IAM**（窄角色 · **禁止** 控制台返回 **`TELEGRAM_BOT_TOKEN` 明文**）。与 **[`telegram/admin-bot-config.md`](../requirements/domains/agent/telegram/admin-bot-config.md)**、**[`trading-agent-config/keys.md` §4](../requirements/domains/admin/trading-agent-config/keys.md)**、**[`management-console-v1-prd`](../requirements/domains/admin/management-console-v1-prd.md) 附录 A §5.1** 同窗；**`secretRef` 同窗** **模块四 · AI Settings**。**`CC-P1-06`**。

| 用途 | 方法 | 路径（示意） | 说明 |
|------|------|--------------|------|
| Bot 配置（`secretRef`、bot 元数据、`runtimeParams` **`keys` §4.2**） | `GET` / `PATCH` | `/api/v1/admin/channels/telegram/bot` | **`FR-MC709～711`**、**`FR-TG-ADMIN-01～03`/`FR-TG-ADMIN-06`** · **`PATCH`** **`runtimeParams`** **覆盖 **`TELEGRAM_*`**（含 **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_*`** **三语** **与** **遗留键**） |
| 设置 Webhook | `POST` | `/api/v1/admin/channels/telegram/webhook` | **`FR-TG-ADMIN-04`** · Body：`url`、`secretToken`（若用）等 |
| 查询 Webhook | `GET` | `/api/v1/admin/channels/telegram/webhook` | **`getWebhookInfo`** 语义；与 **Telegram Bot API** **同窗** |
| 删除 / 降级 Webhook | `DELETE` 或 `POST` | `/api/v1/admin/channels/telegram/webhook`（`delete` **或** 独立子路径） | 与 **`deleteWebhook`** **同窗** |
| 连通性自检 | `POST` | `/api/v1/admin/channels/telegram/self-test` | **`FR-TG-ADMIN-05`** · **202** 可接受 |

**前缀 `/api/v1/admin/...`** 仅为示意；**字段级** **OpenAPI** **终裁** — **须**链 **登记表「Telegram Bot / Webhook」行**。

- 计费扣费结果与流水查询
- 错误码与幂等键约定（与 **`billing.md`**、**`overview.md`** 交叉引用；列表 **`pageSize` ≤ 200**、越界 **400** 见 **`billing.md` SC-B13**）

## 附录 · `stableReason` 与 Runtime Error Taxonomy（登记表）

**需求对读**：[`runtime-error-taxonomy.md`](../requirements/Runtime/runtime-error-taxonomy.md)、[`failure-matrix.md`](../requirements/Runtime/failure-matrix.md)、[`error-normalization.md`](../requirements/Runtime/error-normalization.md)。

**规则**：

- **新增** **`stableReason`** **字面** **须** **归入** **下表** **`Taxonomy` 类** **之一** **并** **PR** **更新** **本附录** **与** **`failure-matrix`**（**若** **改变** **默认处置**）。
- **交易所** **`body.code` / HTTP → `stableReason`** **整表** **仍** **以** **GitBook +** [`integrations/exchange/error-codes.md`](../requirements/integrations/exchange/error-codes.md) **及** **专项映射 MR** **为准** — **本附录** **只** **锁** **「平台侧已命名键」** **与** **Taxonomy** **勾连**。

| **`stableReason`（`UPPER_SNAKE`）** | **`Taxonomy` 类** | **备注** |
|--------------------------------------|-------------------|----------|
| `ORCHESTRATION_BUDGET_EXCEEDED` | `BUDGET_OR_QUOTA` | 见上文 **编排执行预算**；**用户触达** **同窗** |
| `EXCHANGE_WRITE_UNKNOWN_OUTCOME` | `UNKNOWN_OR_AMBIGUOUS_END` | **504/空体/网关未知** **写** **之** **归一** **名**；**须** **与** **`observability`** **`exchangeOutcome=unknown`** **同窗** |
| `UPSTREAM_TIMEOUT` | `TRANSIENT_UPSTREAM` | **可读超时**；**可重试准入** [`recovery.md`](../requirements/Runtime/recovery.md) |
| `PROVIDER_RATE_LIMITED` | `TRANSIENT_UPSTREAM` | **HTTP 429** **类** **供应商** |
| `RISK_GATE_REJECTED` | `RISK_OR_CONFIG_GATE` | **聚合** **Kill/Pause/门禁** **之** **顶**；**细码** **`FR-T05`/`billCode`** **可** **另表** **子映射** |
| `TERMINAL_BUSINESS_REJECT` | `TERMINAL_BUSINESS` | **可采信** **业务拒单**（**余额/规则** **等**）— **勿** **标** **UNKNOWN** |
| `IDEMPOTENCY_REPLAY` | `IDEMPOTENCY_DUPLICATE` | **安全重放** **同一** **幂等键** |

---

**对齐说明**（跨域索引）：**计费扣减主体** = **Agent 专用子账户 · 币币 USDT**（[`billing.md`](../requirements/domains/admin/billing-management/overview.md) **§2**）；**`effectiveMinChargeUsdt` / 结算模式** 以同文 **§7.4（结算策略）** 与 **§2** 为准；**列表分页上界**：用户 **`me/billing`** **见** **`billing.md` SC-B13**（**≤200**）；**运营 **`admin/observability/*` 搜索 **`pageSize`** 上界 OpenAPI **同窗**；**`executionId` / 幂等** 以 **`FR-T01`**（[`overview-legacy-migration.md`](../requirements/domains/agent/exchange-agent/overview-legacy-migration.md) **§1～§2**；同窗 **`billing`** §2、[`consume-and-bill.md`](../requirements/flows/consume-and-bill.md)）与 [`billing.md`](../requirements/domains/admin/billing-management/overview.md) **FR-B05** 为准；**用户侧 Agent 开通 / 绑定（`me/agent/*`）与子账户 Key 保存校验 · Coobit 探测 PATH** **见** **上文「用户侧 Agent 开通 / 绑定 API」** **及** **「绑定保存 · 交易所探测矩阵」**（**同窗 **`FR-WEB06`** **`TradingApiBindRejectCode`**）；**用户侧 · 内部扣减 · 运营侧 Billing** **PATH 示意见上文** **「用户侧 / 内部 / 运营侧 Billing」专节与三表** 与登记表 **账务/`me`/`billing` 行**；**模块四 AI Settings** 见 **「运营侧 AI Settings API（`admin/ai/*`）」** 与登记表 **模块四行（`CC-P0-01`）**；**模块八 Logs & Observability** 见 **「运营侧 Logs & Observability API（`admin/observability/*`）」** 与登记表 **模块八行（`CC-P0-01`）**；**模块一 Agent Management** 见 **「运营侧 Agent Management API」**；**模块二 Prompt / 模块三 Tool / 模块六 Access Control** 见 **「运营侧 Prompt / Tool / Access Control API」** 专节；**单用户协查摘要** 见 **「运营侧用户协查摘要 API（`admin/users/*`）」**；**控制台 Telegram 运维 PATH** 见 **「运营侧 Telegram 渠道运维 API」**；**先于 Coobit 写、`callback_data`/`sendMessage` 上限** 见 **[`domains/agent/telegram/overview.md`](../requirements/domains/agent/telegram/overview.md) **§2.5 · 类型 A**（总则 **§2～§2.6**，含 **§2.6**）**与** **上文「Telegram Bot API」专节**；**运营协查 / 导出入口（UX）** 见 [`config.md`](../requirements/domains/admin/management-console-v1-prd.md) **§7.4**（协查 / 导出节，**≠** billing **结算**语义节）；**单用户摘要字段下限**（含 **`agentMinVipTier`、`agentSubAccountId`、`agentTradingApiBindingStatus`、`agentTradingApiKeyId`**）见同文 **§8.2**；**`access-control`** 归因、**[`eligibility-runtime`](../requirements/domains/admin/access-control/eligibility-runtime.md)** **（顺序/信封/运行时）**、**I02 `code` `enum`** 见 **本文** 「所内 OpenAPI / 契约登记」**模块六** 行与「待补充」相关条，及 [`access-control/overview.md`](../requirements/domains/admin/access-control/overview.md)；**交易所侧委托/查询** **须** **子账户交易 API**，见 **「所内 OpenAPI / 契约登记」**、**「子账户 scope · endpoint 矩阵」**、**「通用契约（设计草案）」** **及** **`exchange-agent` 分卷**：[`exchange-agent/overview.md`](../requirements/domains/agent/exchange-agent/overview.md) **§1～§5**（§5：**旧 §10 映射**）、**`FR-T01`**、[`trade-assistance.md`](../requirements/domains/agent/exchange-agent/trade-assistance.md) **`FR-T02`**；**产品线写闸** `FEATURE_AGENT_*` 见 **`config.md` §5.1**、**§14 TC-23～TC-26**。

---

**本文档版本**：0.1.73 · **维护**：架构 + 交易所网关 owner · **本版**：**轨 B OpenAPI 实稿** — [`internal/billing-entitlements.yaml`](../openapi/internal/billing-entitlements.yaml)、[`user/commerce-me.yaml`](../openapi/user/commerce-me.yaml)、**`admin/billing-admin` `commerce_phase2`**、**`billing-schemas` Phase 2**；登记表与 **「运营侧 Billing」专节** 同步。**承** **0.1.72**
