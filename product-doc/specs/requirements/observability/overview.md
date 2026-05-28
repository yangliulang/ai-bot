# 域需求：观测与审计（observability）

| 项 | 内容 |
|----|------|
| **产品** | ChainUp AI Agent（Coobit 单所） |
| **文档** | `specs/requirements/observability/overview.md` |
| **状态** | **评审中**（**§2.1** 工具事件含 **`invocationState`** · **§2.2** UNKNOWN / 对账 / **`exchangeViewSource`** · **§2.4** **主态迁移 Trigger 映射**；**§4** **SC-OBS** **含 SC-OBS06～08**） |
| **策略** | 定义结构化日志/事件 **下限**：计费链路、工具与编排、交易所 UNKNOWN **可对账**；字段口径 **不低于** [`billing.md`](../domains/admin/billing-management/overview.md)、[`config.md`](../domains/admin/management-console-v1-prd.md)、[`overview.md`](../domains/agent/exchange-agent/overview.md) 引用 |
| **互引** | [`billing.md`](../domains/admin/billing-management/overview.md)；[`config.md`](../domains/admin/management-console-v1-prd.md)；[`overview.md`](../domains/agent/exchange-agent/overview.md)；[`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§8.3～8.5**；[`agent-orchestration/overview.md`](../domains/agent/agent-orchestration/overview.md)（**`FR-AO*`**）、[`agent-orchestration/routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)；[`prompt-management/overview.md`](../domains/admin/prompt-management/overview.md) · **§2.3 join**；[`tool-management/runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md) **（`invocationState`、Result envelope）**；[`domains/admin/observability-management/overview.md`](../domains/admin/observability-management/overview.md) **（模块八控制台面）**；[`execution-transition-matrix.md`](../Runtime/execution-transition-matrix.md) **§2.2**（**Trigger → 本条 §2.4**）；[`tracing.md`](./tracing.md)、[`audit-log.md`](./audit-log.md)、[`metrics.md`](./metrics.md)、[`hallucination.md`](./hallucination.md)、[`runtime-monitor.md`](./runtime-monitor.md)；[`design/architecture.md`](../../design/architecture.md)、[`design/api.md`](../../design/api.md)；[`contract-closure.md`](../contract-closure.md)；[**`closure-remaining` §0**](../closure-remaining.md#closure-remaining-quicklinks) · **[§6 / §6.4**](../closure-remaining.md#cc-exec-solve-path)；[`risk/acceptance.md`](../risk/acceptance.md)（**`SC-RISK*` 抽检可与本法 §2 事件、`executionId` 轴同窗**） |

---

## 目录

| § | 内容 |
|---|------|
| §1 | 目的 |
| §2 | 计费相关事件（下限）；**§2.1** 工具编排；**§2.2** UNKNOWN 与对账；**§2.3** Prompt 治理快照（**§2.3.1** `promptPackVersion` 粒度）；**§2.4** **主态迁移 Trigger ↔ 事件**（Transition Contract） |
| §3 | 留存 |
| §4 | 验收标准 |
| §5 | **分卷**：[`tracing`](./tracing.md)、[`audit-log`](./audit-log.md)、[`metrics`](./metrics.md)、[`hallucination`](./hallucination.md)、[`runtime-monitor`](./runtime-monitor.md) |

---

## 1. 目的

规定 **结构化日志 / 事件** 的 **留存、脱敏、检索键**，使 **计费 / 运营协查 / 客诉** 可还原；**细节**不低于 [`billing.md`](../domains/admin/billing-management/overview.md)、[`config.md`](../domains/admin/management-console-v1-prd.md)、[`overview.md`](../domains/agent/exchange-agent/overview.md) 所引字段。

## 2. 计费相关事件（下限）

**Agent 消耗主链（轨 B · 默认）**：**每条可计费 `executionId`** **须** **在 S4→S5** **产生** **可 join** **之** **`billingTraceId`** **与** **下列事件（或所内等价名）** **至少一条终态**。**Metering**（Token 等）**可** **并列** **于** **`agent.tool.call` / LLM 摘要**，**不** **替代** **核销事件**。

| 事件场景 | 建议事件名（示意） | 必备字段（示意） |
|----------|-------------------|------------------|
| **权益核销尝试** | `billing.entitlement_debit_attempt` | `userId`、`executionId`、`billingTraceId`、`idempotencyKey`（**`:rail-b:entitlement-debit`**）、**`capabilitySkuId`**、**可选** **`packGrantId`**、**`commercialSettlementType=ENTITLEMENT_DEBIT`**、**可选** **`inputTokens`/`outputTokens`**（**Metering**）、ts — **SC-B20**、[`commerce-model`](../domains/admin/billing-management/commerce-model.md) **§5.1** |
| **权益核销成功** | `billing.entitlement_debit_success` | 同上 + **`status=SUCCESS`**、**可选** **`debitUnits`**（**配额扣减单位** · **OpenAPI MR 冻结**） |
| **权益核销失败** | `billing.entitlement_debit_fail` | 同上 + **`status`**（**`INSUFFICIENT`/`FAILED`**）、**`failureClass`**（**`quota_exhausted`/`gateway`** 等 · **OpenAPI MR**）、**可选** **`stableReason`** |
| 未核销跳过 | `billing.skipped` | `reason`：`policy` / **`quota_exhausted`**（**S2 已拦** **或** **非可计费路径**）/ `below_min_tokens`（**Metering 阈值** · **非 S5 扣 Token**）+ 摘要计数 |

**轨 A · Token 扣费（历史 / 对读 · 非 Agent S5 默认）**：

| 事件场景 | 建议事件名（示意） | 必备字段（示意） |
|----------|-------------------|------------------|
| 扣费尝试创建 | `billing.charge_attempt` | `userId`、`billingTraceId`、`executionId`、`idempotencyKey`、`amount`、`currency`、`meterKey`、`inputTokens`、`outputTokens`、ts |
| 扣费成功 | `billing.charge_success` | 同上 + 所内 `tx` 引用（若有） |
| 扣费失败 | `billing.charge_fail` | 同上 + `billCode`、`failureClass`、`chargeStatus` |
| 管理台写配置 | `admin.audit` | 与 `config.md` **§15.4** 一致 |
| 交易所侧调用（私有 HTTP） | `trading.exchange_private`（或所内等价名） | **须**经 **子账户 scope**；`userId`、`executionId`、**`agentSubAccountId`**、**可选** **`agentTradingApiKeyId`**（**公开 id**）、**`methodPathSummary`**（如 `POST /sapi/v2/order`；**不含 Secret**、**不含**完整敏感 query/body）、**可选** **`httpStatus`**、**`exchangeOutcome`**=`success`\|`fail`\|`unknown`（**`unknown`**：**504**、空响应、终态不可判定等，**语义** [`design/architecture.md`](../../design/architecture.md)、[`design/api.md`](../../design/api.md)）、**可选** **`coobitRequestId`**、**可选** **`clientOrderRef`**（`newClientOrderId` / `clientOrderId` **等所内字段名的摘要或原值** — **非 Secret**；用于 **对账 join**）、**可选** **`parentToolCallSeq`** / **`relatedStepId`**（与同执行内 **`agent.tool.call` / `agent.execution.step`** 关联）、**可选** **`exchangeViewSource`**=`WS`|`REST`|`MIXED`（**订单/余额视图来源摘要**；**须与** [`design/api.md`](../../design/api.md) **「REST ↔ WebSocket 对账」专节**、[`Runtime/reconciliation.md`](../Runtime/reconciliation.md) **同窗**）、ts |

### 2.1 工具编排与多步执行（下限）

| 事件场景 | 建议事件名 | 必备字段（示意） |
|----------|------------|------------------|
| **单次工具调用开始/结束** | `agent.tool.call` | `userId`、`executionId`、**`toolId`**（或所内 **稳定工具名**）、**`toolCallSeq`**（同 `executionId` 内单调序号）、`phase=start|success|fail`（**遗留 · 兼容**）、**可选** **`invocationState`**（VALIDATING \| EXECUTING \| RETRYING \| SUCCESS \| FAILED · **须** **与** **[`domains/admin/tool-management/runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md) §1** **对签**）、`durationMs`（结束 optional）、**`agentSubAccountId`**（若已在本执行绑定）、ts |
| **交易子步骤**（多腿） | `agent.execution.step` | `userId`、`executionId`、`stepId`（ULID/序号）、**`stepKind`**（如 `validate` / `quote` / `submit_order` / `query_order` **对账**）、`coobitRequestId`（若已得）、**`symbol` 摘要**（可）、**`outcome`**=`success`\|`fail`\|`unknown`（**`unknown`** 须 **后续** **查单** 或 **`trading.exchange_private` 闭合**，见 **§2.2**）、ts |
| **自动化任务** | `agent.task.lifecycle` | `userId`、**`taskId`**、**`taskKind`**（`conditional_order` / `wealth_maturity` / `risk_threshold` 等）、`action`=`created`\|`triggered`\|`cancelled`\|`failed`、`executionId`（**若**与本事件同振）、ts |
| **编排步骤** | `agent.orchestration.step`（或合并入 `agent.execution.step` **须**含下列键） | `userId`、`executionId`、**`scenarioId`**、**`orchestrationVersion`**、**`stepKind`**、**`stepSeq`**、ts |
| **技能规范已读** | `agent.skill.spec_read` | `userId`、`executionId`、**`skillId`**、**`skillSpecVersion`**、**`specDigest`**（可选 **hash** **非**全文）、`phase`=`success`\|`fail`、ts |
| **上下文压缩** | `agent.context.compress` | `userId`、`executionId`、**`fromLevel`**、**`toLevel`**、**`estimatedTokensSaved`**（可选）、ts |
| **行情 phase 派生** | `agent.market.phase_computed` | `userId`、`sessionId`、`executionId`、**`symbol`**、**`primaryMarketPhase`**、**`secondaryMarketPhases[]`**（可选）、**`marketPhaseSource`**=`rules`|`tool`、**`factSources[]`**（可选）、**`narrativeHintCount`**（可选）、ts — **同窗** [`market-intelligence` §4](../domains/agent/exchange-agent/market-intelligence.md)、[`design/market-narrative-runtime.md`](../../design/market-narrative-runtime.md) |
| **上下文 budget 裁剪** | `agent.context.memory_trimmed` | `userId`、`sessionId`、`executionId`、**`trimmedLayers[]`**（**同窗** [`memory-runtime-schemas`](../../openapi/components/memory-runtime-schemas.yaml) **`MemoryTrimmedLayer`**）、**`estimatedTokensSaved`**（可选）、ts — **同窗** [`memory-runtime` §11](../Runtime/memory-runtime.md) |
| **Semantic 命题写入** | `agent.memory.semantic_updated` | `userId`、**`propositionType`**、**`sessionId`**/`executionId`（可选）、**`updatedAt`**、ts — **草案 · LTM 解冻后** — **FR-MEM09** |
| **STM 会话清空** | `agent.memory.session_cleared` | `userId`、**`sessionId`**、**`clearedAt`**、ts — **FR-STM04** |
| **Resume 门控分类** | `agent.memory.resume_classified` | `userId`、**`sessionId`**、**`decision`**（**`new_intent`/`resume_prior_write`/`need_one_clarify`**）、**`confidence`**（可选）、**`executionId`**（可选）、**`episodePickReason`**（可选）、ts — **§14.6.4** · OpenAPI **`MemoryResumeClassifiedEventPayload`** |

**B/C 类与只读分析路径**（与 [`flows/read-analyze-and-search-via-agent.md`](../flows/read-analyze-and-search-via-agent.md)、[`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§8 B/C** **对签**）：

- **`agent.tool.call` · 状态对齐**：**`invocationState`**（VALIDATING / EXECUTING / RETRYING / SUCCESS / FAILED）须与 [`tool-management/runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md) **§1** 及 Runtime 可对签；可保留 **`phase=start|success|fail`** 作遗留兼容，**`phase→invocationState`** 映射由 **`design`/OpenAPI** 冻结。Retry 与幂等见 **`runtime-contract` §3**。
- **`agent.tool.call`**：`toolId` **须** **为** **注册表** **`trade-assistance` §8.3～8.4 / 所内等价** **已登记** **之** **稳定名**；**推荐** **同条** **或** **同序紧邻** **`agent.orchestration.step`** **携带** **`scenarioId` + `orchestrationVersion`**（**与** [`../domains/agent/agent-orchestration/overview.md`](../domains/agent/agent-orchestration/overview.md) **FR-AO05** **一致**；**二选一落点** **须在实现冻结** — **禁止** **全链** **零** **`scenarioId`** **却** **已调** **外网/B 类工具**）。  
- **`toolDomain`（可选列）**：**建议** **枚举** **`exchange_read`** / **`web`** / **`model`** / **`other`** **便于** **协查聚合**（**所内** **可** **并入** **`toolId` 前缀规范** **替代**）。  
- **外网类 `agent.tool.call`**：**禁止** **默认** **落** **完整 URL 之** **query/apiKey**、**Cookie**、**用户粘贴的** **私钥/Secret**；**须** **归因**（域名/提供商摘要 **无** **凭证**）**与** **响应体** **truncation** **策略** **ADR**。  
- **理财 `scenarioId`**（**`wealth.holdings_read` / `wealth.recommend` / `wealth.subscribe` / `wealth.redeem`**）：**`agent.orchestration.step`（或 FR-AO05 合并字段）** **须** **带** **`scenarioId`**，**与** [`../domains/agent/agent-orchestration/routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md) **§3**、[`flows/wealth-via-agent.md`](../flows/wealth-via-agent.md) **对签**；**`FEATURE_AGENT_WEALTH=OFF`** **负例** **见** [`config.md`](../domains/admin/management-console-v1-prd.md) **TC-26**、[`boundaries.md`](../domains/agent/exchange-agent/boundaries.md) **与** [`wealth-via-agent.md`](../flows/wealth-via-agent.md) **理财门禁叙事**。

### 2.2 交易所 UNKNOWN 与对账（下限 · 与 `design/architecture` 对签）

- **语义**：**HTTP 504** 等 **不得**在日志字段中记为 **伪造的** `exchangeOutcome=success|fail`；**须** `unknown`（或所内等价）直至 **查单** 得见可信终态。详见 [`design/architecture.md`](../../design/architecture.md) **「504 UNKNOWN 与写操作对账」**。
- **`stableReason`（平台归一键 · 推荐）**：**用户触达链 / 聚合告警** **推荐** **在** **`trading.exchange_private`** **或** **紧邻** **编排/工具事件** **携带** **`stableReason`** — **字面** **与** [`Runtime/runtime-error-taxonomy.md`](../Runtime/runtime-error-taxonomy.md) **类** **对签** **之** **登记表** **见** [`design/api.md`](../../design/api.md) **附录 · `stableReason`↔Taxonomy**。**`exchangeOutcome=unknown`** **之** **写** **不得** **映射** **为** **业务成功类** **`stableReason`**（**如** **`TERMINAL_BUSINESS_REJECT`**）。
- **`trading.exchange_private`**：**写**（下单、撤单）与 **读**（**查单**、`/account` 等）**均** **可**用本事件承载；**对账** 序列 **须** **相同 `executionId`（及推荐的 `toolCallSeq`/`stepId`）** 可 **重放** 为 **「提交 → UNKNOWN → 查单 → 解析」**。
- **`exchangeViewSource`（可选）**：**若** **本轮窗口** **聚合** **WS + REST** **视图**，**须在** **`trading.exchange_private`** **读路径** **或** **紧邻** **`agent.execution.step`**（如 **`query_order`** **闭合**）**携带** **`WS`/`REST`/`MIXED`** — **与** **`Runtime/reconciliation`** **矩阵**、**[`design/api.md`](../../design/api.md)** **对账表** **同窗**，**便于** **协查用户所见通路**。
- **解析后的终态**（**可选**）：**或** 更新 **后续** 一条 **`agent.execution.step`** 的 `outcome`；**或** **追加** **`trading.exchange_private`**（`exchangeOutcome=success|fail` + **业务状态摘要**）；**或** 所内 **`trading.exchange_reconcile`** 专用事件 — **三选一须冻结**，**禁止** **仅**依赖 **非结构化** 文本。
- **OpenAPI 字段冻结**：**若** **在** **`observability-schemas.yaml`** **为** **本条事件** **登记** **`stableReason`**（**或** **同窗枚举**），**须** **与** **上文** **字面约束** **及** [`design/architecture.md`](../../design/architecture.md) **「观测事件 `stableReason`」**、[`design/api.md`](../../design/api.md) **附录** **同一 MR 对签**。**`unknown_pending` 无进展** **须** **可协查**（**同窗** [`risk/unknown-stall-policy.md`](../risk/unknown-stall-policy.md)、**抽检** [`risk/acceptance.md`](../risk/acceptance.md) **`SC-RISK-06`**）。

**说明**：**工具回填** 文本 **不**入 **默认**结构化日志全文；**须**保留 **token 计数/计量** 侧键供 **`billing`** join。

### 2.3 Prompt 治理快照（下限 · 与 `prompt-management` 对签）

**目的**：**不写** **Prompt 全文**（与 **§2 末段** **脱敏** **一致**），但 **须**能 **按执行** **join** **「当前回合用哪几包、哪一版」** 与 **校验器修订号**，供 **混版排查 / 审计 / 计费 attribution**。**事件整体** OpenAPI SSOT：**`specs/openapi/components/observability-schemas.yaml` · `AgentPromptBindingResolvedEvent`**；**绑定快找子对象** **`$ref`** **`prompt-management-schemas.yaml` · `ResolvedPromptBinding`**（**禁止**再拆第三套 body 键）。

**闭环 / 派工索引**（**非** substitute **OpenAPI**）：[`closure-remaining` §7.2～§7.4](../closure-remaining.md#cc-ac09-closure-matrix) · **[§7.5](../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../closure-remaining.md#cc-closure-exec-checklist)** — **与** **Timeline · 事件级 `promptPackVersion`** **之产品决策**、**Runtime 拼装链** **同窗**（**若** **升级事件级粒度** **须** **另行** **`observability` §2 MUST MR**）。

#### 2.3.1 策略：`promptPackVersion` 粒度（V1 终局口径）

| 策略 | 状态 | 说明 |
|------|------|------|
| **执行级绑定（V1）** | **MUST** | 按 **`executionId`**（或等价可计费执行）关联 **`ResolvedPromptBinding`**（JSON） **与** **事件** **`agent.prompt.binding_resolved`**，与 [`runtime-injection` §3](../domains/admin/prompt-management/runtime-injection.md) **同窗**；**满足** **本条 §2.3 表与 SC-OBS04** **即** **规格侧** **「Timeline 细粒度」** **之** **默认闭环**。**未** **单独要求** **每条 NLU/LLM 子调用** **各自** **`promptPackVersion`**。 |
| **事件级（NLU/LLM 每步）** | **可选 · 非 V1 默认** | **仅当** 产品 **书面批** **且** **本条 §2** **增补 MUST + OpenAPI** **`observability-schemas`** **同窗 MR** **后** **方可** **宣称**；**升格前** **禁止** **对外等同** **「全链事件级可观测」** **与** **现网** **实现**。**检核表** → [`closure-remaining` §7.4](../closure-remaining.md#cc-ac09-closure-matrix) · **闭环路径** [`§7.5`](../closure-remaining.md#cc-remaining-open-close-path)。 |

| 事件场景 | 建议事件名 | 必备字段（示意） |
|----------|------------|------------------|
| **回合开端解析完成** | `agent.prompt.binding_resolved` | `userId`、`executionId`、**`scenarioId`**、`sessionId`（若与 `executionId` 不同）、**`systemPromptPackId` + `systemPromptPackVersion`**、**`safetyPromptPackId` + `safetyPromptPackVersion`**、**`runtimeClarifyPromptPackId/Version`**、**`runtimeOutputContractPromptPackId/Version`**（**SYSTEM 横切** · `pp-runtime-*`）、**`tradingPromptPackId` + `tradingPromptPackVersion`**（**场景/分析策略槽** · **无**某类包 **可** `null` **须** **OpenAPI 明示**）、**可选** **`fewShotDigest`**（Few-shot **序列化 hash**，**非**明文）、**可选** **`placeholderDenylistRevision`**、**可选** **`safetyPhraseBlocklistRevision`**、ts |
| **Publish 被 Safety/占位符闸拦截** | `admin.prompt.publish_blocked`（或并入 `admin.audit` **须**含子类型） | **`promptPackId`、`promptPackVersion`（草稿）**、`actor`、`reasonCode`（如 `SAFETY_PHRASE`、`PLACEHOLDER_DENYLIST`）、**`matchedRuleId`**（**不**含 **命中原文** **或** **仅** **hash**）、ts |

**规则**：

- **`agent.prompt.binding_resolved`**：**须** **在首次模型调用前** **或** **与会话首条 user 同序** **落一条**（**与** [`prompt-management/runtime-injection.md`](../domains/admin/prompt-management/runtime-injection.md) **§3** **对签**）。**JSON 形状** **以** **`observability-schemas.yaml` · `AgentPromptBindingResolvedEvent`** **为准**（**`additionalProperties: false`**）。  
- **禁止** **默认** **落** **`body`/`messages` 全文**；**须** **与** [`prompt-management/functions.md`](../domains/admin/prompt-management/functions.md) **SC-PM-09** **可对账**。

### 2.4 主态迁移 `Trigger` 与观测事件映射（**Transition Contract · 语义不得弱于** **[`execution-transition-matrix`](../Runtime/execution-transition-matrix.md) §2.2**）

**目的**：[`execution-transition-matrix.md`](../Runtime/execution-transition-matrix.md) **§2.2.1** **「Trigger / Event」** **列** **为** **结构化名**；**实现** **可** **沿用** **字面** **或** **所内别名**，**但** **须** **可在** **同一** **`executionId`** **时间线** **上** **还原** **「触发事实 → 主态边」** **不低于** **矩阵 Guard / Authority** **之** **可审计性**。

**时间线（`FR-MC801`）**：**推荐** **在** **编排宿主归并主态** **之** **同一** **trace/timeline 窗** **内**：（**二选一或并存，所内终裁**）**(a)** **`ObservabilityTimelineEvent.transitionTrigger`** **填** **本条表** **`矩阵 Trigger`** **字面** **或** **已登记别名**；**(b)** **主事件** **`eventName`** **落** **下表** **「主承载事件」**，**且** **`summary`** **须** **含** **可 join** **之 **`stepKind` / `outcome` / `invocationState` / `exchangeOutcome`** **等键** — **禁止** **仅** **非结构化** **一句话** **冒充** **迁移审计**。**抽检验收** **见** **§4 · `SC-OBS08`**。

| **§2.2 Trigger / Event（字面）** | **主承载 `eventName`（§2～§2.1）** | **摘要 / 邻域（下限）** |
|----------------------------------|-------------------------------------|-------------------------|
| `execution.dispatched` | `agent.orchestration.step` **或** `agent.execution.step` | **`stepKind`** **须** **明示** **进入编排**（如 `dispatch` / `enter_planning`）；**同窗** **矩阵** **From→To** `accepted→planning` |
| `Orch.shortcut_to_confirm` | `agent.orchestration.step`（**或** **`agent.execution.step`** **合并键**） | **`summary`** **须** **可证** **§2.1** **跳过 planning**；**写路径** **仍** **对齐** **[`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md) |
| `Orch.shortcut_execute` | 同上 **+** **若触及写** **`trading.exchange_private`** **与** **`agent.tool.call`** | **类型 A** **须** **可** **从** **时间线** **还原**（**ADR-001**） |
| `gate.failed` / `early_abort` | `agent.execution.step` **或** **宿主等价** **终局前步骤** | **`outcome=fail`** **或** **`stableReason`** **族** **对齐** [`runtime-error-taxonomy.md`](../Runtime/runtime-error-taxonomy.md) **；** **不可** **伪** **success** |
| `user.cancelled` / `ops.cancelled` | `admin.audit` **或** **所内** **「用户/运营动作」** **结构化事件**（**`eventName` 所内终裁**） | **`actor`/`source` 归因**；**终局取消** **须** **与** **矩阵 §2.2.1** **Guard** **一致** |
| **`skill.spec_loaded`** | **`agent.skill.spec_read`** | **`skillId`**、**`skillSpecVersion`**、**`phase`**；**须** **早于** **`confirmation.required`**（**写路径** · [`production-runtime` §3](../skill-specs/production-runtime.md)） |
| `confirmation.required` | `agent.orchestration.step` | **`stepKind`** **含** **`confirm_gate`** **或** **等同**；**S5.1** **部成** **不** **升格主态** |
| `plan.ready_no_confirm` | `agent.orchestration.step` | **`scenarioId`/`routing` 明示**无确认门 **须** **可 join** [`routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md) |
| `plan.abort` / `risk_rejected` | `agent.orchestration.step` **或** **`agent.tool.call` 终态** | **风险拒答** **须** **与** [`runtime-invariants.md`](../Runtime/runtime-invariants.md) **INV-004** **口径** **一致**（**不** **静默进入** **会扩张** **交易所写** **`executing`**） |
| `user.confirmed` | `admin.audit`（**类型 A 对签**）**或** **`agent.execution.step`** **`stepKind=confirm`** | **ADR-001** **有效** **须** **可审计** |
| `confirm.timeout` / `reject` | `agent.execution.step` | **`outcome`** **或** **超时码** **对齐** **产品话术** |
| `tool.round_complete` / `order.submitted` | **`agent.tool.call`**（**终态 SUCCESS** **或** **阶段完成**）**与/或** **`agent.execution.step`**（**`submit_order`**）**与** **`trading.exchange_private`** | **S5.1**：**部成** **仅** **子态**；**不写** **completed** **主态** |
| `tool.timeout` / `exchange.504` | **`trading.exchange_private`**（**`exchangeOutcome=unknown`**）**+** **`agent.tool.call`** | **§2.2**、**SC-OBS03**；**UNKNOWN** **闭环** **同窗** [`unknown-state.md`](../Runtime/unknown-state.md) |
| `tool.final_failed` | **`agent.tool.call`**（**`invocationState=FAILED`**） | **终局失败** **可采信** **键** |
| `safe.abort` | **`admin.audit` 或** `user.cancelled` **同类行** | **§2.1** **安全撤单点** |
| `reconciliation.success` + **`billing`** | **`billing.entitlement_debit_success`**（**或** **`attempt` → `success`** **链**）**+** **`agent.execution.step`** **闭合步** | **S4→S5**、**`SC-B20`** **同窗** [`consume-and-bill.md`](../../flows/consume-and-bill.md) |
| `settlement.failed` | **`agent.execution.step`** **或** **`trading.exchange_private`**（**`exchangeOutcome=fail`**） | **可采信失败** |
| `reconciliation.inconclusive` | **`trading.exchange_private`**（**unknown**）**或** **`agent.execution.step`** **对账步** | **同窗** [`billing.md`](../domains/admin/billing-management/overview.md) **§10**、**`unknown` 话术** |
| `evidence.received` | **`agent.execution.step`**（**如** **`query_order`**）**或** **`trading.exchange_private` 读** | **对账证据** **须** **与** **`executionId`** **同链可重放** |
| `final_success_confirmed` | **上表同类** **+** **`billing.entitlement_debit_*`** **若已闭合核销** | **§2.1** **终局可采信** |
| `final_failed_confirmed` / `policy.timeout` | **`agent.execution.step`** **或** **策略宿主事件** | **同窗** [`unknown-stall-policy.md`](../risk/unknown-stall-policy.md) |
| `policy.cancel` | **`admin.audit`** **或** **策略/运营事件** | **与** **`ops.cancelled`** **行** **Guard** **一致** |

**`/`（同格多 Trigger）**：**上表** **同格** **`a / b`** **表示** **实现** **可** **择一** **字面** **登记为 `transitionTrigger`**；**语义** **须** **覆盖** **二者** **之** **并集** **且** **不得** **弱于** **矩阵** **该行之 Guard**。

**脱敏**：**不得**在 **默认**日志中落 **prompt/回复全文**；**用户 id** 对外渠道 **须**与 **企业脱敏规范**一致。

**`traceKey`**：运营协查 UI 展示字段，**与 `billingTraceId` 同值**（[`billing.md`](../domains/admin/billing-management/overview.md) **FR-B06**，[`config.md`](../domains/admin/management-console-v1-prd.md) **§11 D-5**）。**关闭** **`CC-P0-05`（`D-5`）** **须** **同窗** **`billing` §10.3.1** **检查单** **序号 1**。

**`D-7`（未知终局 × 计费）**：**`trading.exchange_private` 写** **遇** **504/UNKNOWN** **之** **事件语义** **须** **与** **`billing`/消费计费** **同窗** — **不可** **观测侧** **断言 success** **而** **账务侧** **另作终局**；**主路径** [`billing.md` §10.3](../domains/admin/billing-management/overview.md)、[`consume-and-bill.md`](../../flows/consume-and-bill.md)。**MR** **关闭** **`CC-P0-05`** **须** **勾选** **`billing` §10.3.1** **序号 2** **并** **附** **`SC-OBS03`** **构造用例** **链接**。

## 3. 留存

**全链审计 / 协查**：**≥180 天** 或与 **`config.md` 审计** 取 **更长**（评审冻结）。

**与 Memory「温」默认**：**可检索索引 / 抽检面** **须** **覆盖** **[`design/architecture.md`](../../design/architecture.md) **Memory 留存** **温层 v0（30 自然日）** **或** **更长** — **避免** **运营协查窗** **短于** **架构默认**；**审计底线** **仍** **以上句** **≥180d** **为准**（**取更长者** **作为** **对外承诺** **须** **同窗 MR 明示**）。

## 4. 验收标准

| ID | 标准 |
|----|------|
| SC-OBS01 | **B/C 工具与 `scenarioId`**：抽样 **`agent.tool.call`** **且** **`toolId`** **登记于** [`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§8.3～8.4** **之**执行，**须** **在** **同** **`executionId`** **下** **可 join** **`scenarioId`**（**落点** **`agent.orchestration.step` 或 `agent.tool.call` 之一**，与 **§2.1** **B/C 段** **一致**）；**违例** **测试失败**。 |
| SC-OBS02 | **外网工具脱敏**：对 **`tool.web.*`** **类** **`agent.tool.call`** **之** **默认结构化日志** **跑** **静态/抽检规则**，**不得** **出现** **明文凭据**（**apiKey=、Bearer 后完整 token、Cookie:** **等** — **列** **所内 ADR**）；**违例** **阻断发布** **或** **告警升级**（**二选一须冻结**）。 |
| SC-OBS03 | **504 / UNKNOWN**：**任**一 **`trading.exchange_private`** **写** **遇** **HTTP 504** **或** **终态不可判** **之** **首条**事件 **`exchangeOutcome`** **须** **`unknown`**（**非** **人为** **success/fail**）；**与** [`design/architecture.md`](../../design/architecture.md)、**`overview.md` SC** **可对账** **≥1** 条 **构造用例**。 |
| SC-OBS04 | **Prompt 绑定快照**：抽样 **带** **模型调用** **`executionId`**，**须** **存在** **`agent.prompt.binding_resolved`** **或** **`agent.orchestration.step`（或合并事件）** **之** **等价字段集**（见 **§2.3**；**OpenAPI** **`AgentPromptBindingResolvedEvent`** → **`ResolvedPromptBinding`**）：**可 join** **`scenarioId` + 各 `promptPackId`/`promptPackVersion`**（**无**明文 **Prompt**）；**与** [`prompt-management/runtime-injection.md`](../domains/admin/prompt-management/runtime-injection.md) **§3**、[`prompt-management/functions.md`](../domains/admin/prompt-management/functions.md) **SC-PM-09** **对签**。 |
| SC-OBS05 | **`invocationState` 对齐**：**`agent.tool.call`** **`invocationState`** 须与 [`tool-management/runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md) **§1** 及 Runtime 可对账；**门禁与 §2.1 首张表须在 `design`/OpenAPI **并列冻结** |
| SC-OBS06 | **`exchangeViewSource`（视图通路）**：抽样 **涉** **私有交易所 HTTP** **且** **本轮执行** **经 WS / REST / 二者闭合** **已形成用户可见订单或余额视图** **`executionId`**，**须** **存在** **`exchangeViewSource`**=`WS`|`REST`|`MIXED` **于** **`trading.exchange_private`** **或** **§2.2** **所述紧邻 **`agent.execution.step`** **路径**；**语义** **须与** [`design/api.md`](../../design/api.md) **「REST ↔ WebSocket 对账」专节**、[`Runtime/reconciliation.md`](../Runtime/reconciliation.md) **同窗**；**违例** **测试失败**。 |
| SC-OBS07 | **编排执行预算顶**：构造 **`executionId`** **逼近或突破** **工具调用次数** **或** **编排步骤** **之** **配置上限**（[`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4、`FR-AO06`**），**须** **终止** **新** **工具体 `EXECUTING`** **且** **用户可见** **`FR-T05` 族** **与** **建议码** **`ORCHESTRATION_BUDGET_EXCEEDED`**（**或** **`design` 冻结等价**）；**`agent.tool.call` 终态条数** **可** **按** **`executionId`** **计数核对 ≤ 配置顶** — **与** **`SC-AO-08`** **同窗**。 |
| SC-OBS08 | **主态迁移可审计（Transition Contract）**：抽样 **至少** **发生** **[`execution-transition-matrix.md`](../Runtime/execution-transition-matrix.md) **§2.2.1** **一条** **允许主态边** **且** **非** **仅** **只读分析路径** **之** **`executionId`**，**`FR-MC801` 时间线** **须** **可还原** **该边** **对应** **Trigger** — **(a)** **`transitionTrigger`** **与** **§2.2.1** **字面一致** **或** **已登记别名**，**或** **(b)** **`eventName`/`summary`** **键集** **满足** **上文 §2.4** **该 Trigger 行** **下限**；**违例** **测试失败**。 |
| SC-OBS09 | **Market phase 可审计**：抽样 **注入 **`marketNarrativeHints`** **或** **`marketInsightData.marketPhase`** **之** **`executionId`**，**须** **存在** **`agent.market.phase_computed`** **且** **`primaryMarketPhase`** **∈** **[`market-runtime-payload` §3.2.1](../domains/agent/exchange-agent/market-runtime-payload.md) **登记枚举**；**`marketPhaseSource=rules`** **时** **须** **与** **`design/market-narrative-runtime`** **确定性规则同窗**；**违例** **测试失败**。 |
| SC-OBS10 | **Memory 裁剪可审计**：抽样 **触发** [`memory-runtime` §11](../Runtime/memory-runtime.md) **裁剪之 **`executionId`**，**须** **存在 **`agent.context.memory_trimmed`** **且 **`trimmedLayers[]`** **非空**；**②④ Facts** **仍在 Prompt/Context** — **同窗** **`eval.memory.budget_trim`**；**违例** **测试失败**。 |
| SC-OBS11 | **写路径读技能规范**：抽样 **触及** **A 类写** **`executionId`**（**如** **`trade.spot.limit_order`**），**须** **存在 **`agent.skill.spec_read`** **`phase=success`** **且** **时间线序** **早于** **类型 A / `call_exchange_write`** **首条**；**`summary`** **或** **结构化字段** **须** **含** **`skillId` + `skillSpecVersion`**；**违例** **测试失败**。 **同窗** [`production-runtime` §3](../skill-specs/production-runtime.md)、**`SC-OM-05`** |

**`SC-RISK*`**（运营闸 / 护栏）：验收口径见 [`risk/acceptance.md`](../risk/acceptance.md)；**抽检时** **推荐** **沿用** **本条 §2** **`executionId`** **时间线** **与** **`admin.audit`** **拼** **归因** — **与** **`SC-RISK*`** **重复度** **叙事** **勿** **另编** **新** **`SC-OBS*`** **仅** **为** **复述** **同一条** **风险**（**独立** **`SC-OBS*`** **如** **§2.4/** **`SC-OBS08`** **仍** **保留**）。

---

**文档版本**：0.5.20 · **维护**：产品 + SRE · **本版**：**§2 计费事件** **轨 B 主链**；**§2.4 核销 Trigger 映射**。**承** 0.5.19。
