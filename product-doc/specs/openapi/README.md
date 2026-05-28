# specs/openapi（B 阶段 · 仓库内契约骨架）

本目录 **OpenAPI 3.0.3** 文件为 **`design/api.md` 登记表** 在 **无 Hosted Swagger** 时的 **可访问 Spec**：评审可本地打开 YAML，或在 MR 中 diff。

| 文件 | 登记表行 |
|------|-----------|
| `admin/agent-management.yaml` | 运营后台 · Agent 模板/实例/Runtime |
| `admin/prompt-management.yaml` | 运营后台 · Prompt |
| `admin/tool-management.yaml` | 运营后台 · Tool Registry |
| `admin/ai-settings.yaml` | 运营后台 · AI Settings |
| `admin/billing-admin.yaml` | 运营后台 · Billing & Settlement（admin） |
| `admin/access-control.yaml` | 运营后台 · Access Control |
| `admin/observability.yaml` | 运营后台 · Logs & Observability |
| `admin/telegram-channels.yaml` | 运营后台 · Telegram Bot / Webhook |
| `admin/users-global-config.yaml` | 用户摘要 + 全局配置写 |
| `exchange/coobit-spot.yaml` | 子账户 · 币币 |
| `exchange/coobit-margin.yaml` | 子账户 · 杠杆 |
| `exchange/coobit-futures.yaml` | 子账户 · 合约 |
| `exchange/coobit-wealth.yaml` | 子账户 · 理财 |
| `exchange/coobit-automation.yaml` | 子账户 · 自动化 |
| `exchange/coobit-public.yaml` | 公开行情 |
| `user/onboarding.yaml` | Agent 产品线 · `me/agent/*` 开通/绑定 |
| `internal/billing-token.yaml` | **历史归档** · Token 扣费（**CC-P0-03** · **非 Agent S5** · **本仓 Demo 不实现**） |
| [`internal/billing-entitlements.yaml`](internal/billing-entitlements.yaml) | **Agent S5 主链（轨 B）** — 权益核销 / 余额 / pack-grants |
| `internal/agent-orchestration.yaml` | Agent 编排 · L0 Trade Resolver（`AgentTradeResolverOutput` · INV-008） |
| `user/billing-me.yaml` | **历史归档** · `me/billing`（**CC-P0-03** · **本仓 `src/Web` 不实现**） |
| [`user/commerce-me.yaml`](user/commerce-me.yaml) | 用户侧 **`me/commerce`** · FR-B17 摘要 |
| `stream/user-private-ws.yaml` | WebSocket · 成交/订单 |

**同窗组件（`components/`）**

| 文件 | 说明 |
|------|------|
| [`components/identity-schemas.yaml`](components/identity-schemas.yaml) | **`ExecutionId` / `SessionId` / `ScenarioId` / `UserIdMasked`** · [`standards/naming-standard.md`](../requirements/standards/naming-standard.md) **§1** 同窗 **`pattern`**；**`billing-schemas`** **复用** **`ExecutionId`** |
| [`components/billing-schemas.yaml`](components/billing-schemas.yaml) | **同窗 **`$ref`**；**Agent 主链 **SC-B20**；**历史 Token 包 **CC-P0-03** / **SC-B08** |
| [`components/access-control-schemas.yaml`](components/access-control-schemas.yaml) | **`admin/access-control`** · **`EligibilityEnvelope` §4** · **`code` `$ref` §7.1**；**`eligibility/evaluate`** |
| [`components/agent-management-schemas.yaml`](components/agent-management-schemas.yaml) | **`admin/agent-management`** · **I02/`code` §7.1 enum**；**R06 `AgentBatchRuntimeResult`** |
| [`components/observability-schemas.yaml`](components/observability-schemas.yaml) | **`admin/observability`** · **[`observability/overview.md`](../requirements/observability/overview.md) §2**（**`billing.entitlement_debit_*` 主链** + **`capabilitySkuId`**）；**`ObservabilityTimelineEvent`** · **`$ref` identity/billing-schemas** |
| [`components/telegram-channels-schemas.yaml`](components/telegram-channels-schemas.yaml) | **`admin/telegram-channels`** · [`admin-bot-config.md`](../requirements/domains/agent/telegram/admin-bot-config.md) **FR-TG-ADMIN-01～06**、**SC-TG-ADMIN-01～05**；**`$ref` `billing-schemas`** 之 **`Problem` / `AsyncTaskAccepted`**（409、自检 202） |
| [`components/users-global-config-schemas.yaml`](components/users-global-config-schemas.yaml) | **`admin/users-global-config`** · **单用户协查摘要**（PRD **§8.2**）+ **全局 bundle PATCH**；**`$ref` `billing-schemas`** 之 **`Problem`**（404 / 409） |
| [`components/ai-settings-schemas.yaml`](components/ai-settings-schemas.yaml) | **`admin/ai-settings`** · **FR-MC401～407**；**`providerId`/`modelId`** 与 **[`observability/overview.md`](../requirements/observability/overview.md) §2**、**FR-MC804** 同窗；**`$ref` `billing-schemas`** **`Problem` / `AsyncTaskAccepted`** |
| [`components/prompt-management-schemas.yaml`](components/prompt-management-schemas.yaml) | **`admin/prompt-management`**（含 **`GET /internal/prompts/effective`**）· **FR-PM01～08**、**`resolvedPromptBinding`** 与 **observability §2.3** 同窗；**`scenarioId`** → **`identity-schemas`** |
| [`components/skill-operation-spec-schemas.yaml`](components/skill-operation-spec-schemas.yaml) | **`admin/prompt-management`** 同窗路径 **`admin/skill-specs/*`**、**`GET /internal/skills/effective`** · **FR-T11** · Git [`skill-specs/`](../requirements/skill-specs/) |
| [`components/tool-management-schemas.yaml`](components/tool-management-schemas.yaml) | **`admin/tool-management`** · **FR-TM01～05** / **FR-MC301～305**；**`toolRiskLevel`**、**`matrixStatus`** 同窗 **runtime-contract** **§2** 与 **trade-assistance §8**；**`$ref` `billing-schemas`** **`Problem`** |
| [`components/exchange-schemas.yaml`](components/exchange-schemas.yaml) | **`exchange/coobit-*`** · **`CoobitJsonValue`** 占位；PATH 与 **`design/api.md` 子账户矩阵** / **REST↔WS 对账** 同窗 |
| [`components/onboarding-schemas.yaml`](components/onboarding-schemas.yaml) | **`user/onboarding`** · **FR-ON01～05**、[`onboarding/overview.md`](../requirements/domains/agent/onboarding/overview.md)；**`$ref` `billing-schemas` `Problem`** |
| [`components/stream-schemas.yaml`](components/stream-schemas.yaml) | **`stream/user-private-ws`** · **listenKey** HTTP 生命周期；同窗 **GitBook WebSocket** 与 **`design/api` REST↔WS** |
| [`components/market-runtime-schemas.yaml`](components/market-runtime-schemas.yaml) | **Runtime Context · 行情 Facts 与叙事 hints**（**非 HTTP 公网 API**）· **`MarketPhase`/`UserVisibleMarketData`/`MarketInsightData`/`MarketNarrativeHints`/`AgentRuntimeMarketContext`**；同窗 **[`market-runtime-payload` §3](../requirements/domains/agent/exchange-agent/market-runtime-payload.md)**、**[`market-intelligence` §4](../requirements/domains/agent/exchange-agent/market-intelligence.md)**、**[`design/market-narrative-runtime.md`](../design/market-narrative-runtime.md)** |
| [`components/memory-runtime-schemas.yaml`](components/memory-runtime-schemas.yaml) | **Runtime Context · STM/LTM / Semantic / 四原则硬闸**（**非 HTTP 公网 API**）· **`MemoryRuntimeConfigSnapshot`/`WarmExecutionEpisode`/`ResumeClassifierResult`/`MemoryResumeClassifiedEventPayload`**；同窗 **[`memory-runtime` §9～§16](../requirements/Runtime/memory-runtime.md)**、**[`keys` §2.1](../requirements/domains/admin/trading-agent-config/keys.md)**、**[`design/memory-runtime-injection.md`](../design/memory-runtime-injection.md)**；**LTM 默认 OFF** |
| [`components/orchestration-runtime-schemas.yaml`](components/orchestration-runtime-schemas.yaml) | **`AgentTradeResolverOutput`**、**`InternalTradeResolverRequest/Response`** · **INV-008**；同窗 **`internal/agent-orchestration`**、**`tradeResolverTypes`** / **`internalTradeResolverAdapter`**（`src/admin/src/productionRuntime`）|

**具名 Owner（主/备）**：[OWNERS.md](OWNERS.md)（**本仓库** **暂** **统一 DRI** **见表内主列**；**规模化** **须** **拆** **备** **为** **第二责任人**）。

**说明**

- **`info.version`**：与 **登记表「版本」列** **首列日期** **对齐**；**`billing-schemas` Phase 2 扩展（2026-05-26）** **同窗** [`internal/billing-entitlements`](internal/billing-entitlements.yaml)、[`admin/billing-admin` `commerce_phase2`](admin/billing-admin.yaml)、[`user/commerce-me`](user/commerce-me.yaml)。**git 短 SHA** 由 **合入 `specs/openapi` 的 MR** 在合并后记入（**或** **CI** **写回**），**不必**手抄进 19 行（防 amend **漂移**）。
- **paths** 为 **设计冻结示意**；**账务三线**、**计费轨 B（权益/包）OpenAPI** **已挂上表** **`billing-entitlements`/`commerce-me`/`admin` `commerce`**；其余 **字段/schema** **所内 MR** **补全** **后与** **`design/api.md`** **双向对签**。
- **Coobit 交易** 类 YAML 含 **`externalDocs`** → GitBook **产业锚**；**正式 baseurl** 仍 **所内冻结**。

**索引**：[`../design/api.md`](../design/api.md) · [`../requirements/contract-closure.md`](../requirements/contract-closure.md) · [`../requirements/closure-remaining.md`](../requirements/closure-remaining.md)（**CC-P0-01 等** **§7 / §7.5 / §7.6** **关单路径**）

## Hosted Swagger 与 `release-*` tag（CC-P0-01 · 终裁）

**运维逐步勾选** → [`HOSTED-ROLLOUT-CHECKLIST.md`](HOSTED-ROLLOUT-CHECKLIST.md)。

**B 阶段 closing**：**对运营/对内「可访问 Spec」** **至少** **满足其一**：**(a)** **本仓库** **`specs/openapi/*.yaml` + `info.version` 日期** **与** **[`design/api.md`](../design/api.md) 登记表第三列** **同窗**；**(b)** **Hosted** **Swagger UI / Redoc** **HTTPS URL** **指向** **与 (a) 同内容** **或** **同 CI artifact**；**(c)** **`release-<service>-<semver|date>`** **Git tag** **锚定** **合并提交**。**全能力宣称** **前** **建议 (b) 或 (c)** **与 (a)** **在同一 MR** **登记** [`contract-closure.md`](../requirements/contract-closure.md) **§7** — **禁止** **仅改实现** **不回填** **版本列**。

**CC-P0-01 · 文档轨批次（2026-05-09～续）**：**原 19 根业务 spec**、`components/*.yaml` **与** **`billing-schemas`**：**多数** **`info.version`** **`2026-05-09`** — **满足 (a)** **之本仓库可审文档子集**。**增量**：**轨 B** **`internal/billing-entitlements`、`user/commerce-me`**、**`admin/billing-admin` commerce** 与 **`billing-schemas` Phase 2** **`2026-05-26`** — **见** [`design/api.md`](../design/api.md) **登记表第三列**。**(b)(c) Hosted/`release-*`、§1.2 六款逐项与生产矩阵终裁** **仍须** **所内 MR** **勾选**（见 [`contract-closure.md`](../requirements/contract-closure.md) **§2 · §5.2 · §8**）。
