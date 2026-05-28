# Trading Agent Config · `configKey` 登记（模块七 SSOT）

**叙事**：[`overview.md`](overview.md)。**控制台 IA**：[`config.md`](config.md)。

**与 PRD 附录 A**：[`management-console-v1-prd.md`](../management-console-v1-prd.md) **附录 A §5.1** 须与本节 **同行 PR 或可合并窗口** 对齐；附录可作 **摘录索引**，**枚举完整度以本文为准**。**OpenAPI 真源**：[`design/api.md`](../../../../design/api.md) **「运营后台 · 全局配置写入」**；冲突码见 [`functions.md`](functions.md) **§5**。

**通则**

1. **`design/api` 矩阵仍为 `TBD` 或未登记** 的交易能力，**不得**在本域单独宣告 **全开** **`FEATURE_AGENT_*`**（与 **SC-MCV1-05** 精神一致）。
2. **新增键**：须 **MR** 更新 **本文 + 附录 A§5.1**，并满足 [`rules.md`](rules.md)。
3. 下表 **`type`** 为示意，**JSON Schema/OpenAPI** 终裁。

---

## 1. 全局闸（Tab：**全局闸** · FR-MC701～702）

| `configKey` | type（示意） | 说明 |
|-------------|----------------|------|
| `GLOBAL_AGENT_SWITCH` | bool | 总开关。OFF → `agentState` 可归因 `GLOBAL_OFF`（附录 A §9）。**[`agent-management` G01](../agent-management/functions.md)** **不在本模块改键**。 |
| `OPS_GLOBAL_AGENT_PAUSE` | bool 或枚举 | 运维熔断；与 `GLOBAL_AGENT_SWITCH` **并行语义、`OPS_SUSPENDED` 归因由 `design` 冻结** |

---

## 2. 特性矩阵（Tab：**特性矩阵** · FR-MC703）

| `configKey` | type（示意） | 说明 |
|-------------|----------------|------|
| `FEATURE_TRADING` | bool | 交易写总闸；与 `FEATURE_AGENT_*`、[`exchange-agent/overview.md`](../../agent/exchange-agent/overview.md) **产品线闸对签** |
| `FEATURE_ANALYSIS` | bool | 分析类总闸 |
| `FEATURE_MARKET_ANALYSIS` | bool | 行情分析（示例） |
| `FEATURE_ONCHAIN_ANALYSIS` | bool | 链上分析（示例） |
| `FEATURE_VOICE` | bool | 语音/Voice |
| `FEATURE_AGENT_SPOT` | bool | 现货/闪兑轨道 |
| `FEATURE_AGENT_MARGIN` | bool | 杠杆 |
| `FEATURE_AGENT_FUTURES` | bool | 合约。**V1 产品默认 OFF**；详见 [`runtime-policy` §7](../../agent/exchange-agent/boundaries.md#7-market-scope-governance市场范围治理) |
| `FEATURE_AGENT_WEALTH` | bool | 理财 · 与 **`management-console`** **TC-26** 等互引 |
| `FEATURE_SEMANTIC_NARRATIVE` | bool | **跨会话 Semantic Narrative（LTM · 对用户）** · **默认 OFF**；**须** **与** [`memory-runtime` §9](../../../Runtime/memory-runtime.md) **`FR-MEM01`**、**`semanticNarrativeEnabled`** **同窗**；**ON** **时** **仍须** **用户侧查看/撤销** **[`telegram/overview` §2.7](../../agent/telegram/overview.md)** |
| `CHANNEL_TELEGRAM` | bool | Telegram 渠道；与 [`telegram/overview.md`](../../agent/telegram/overview.md) **总则 §2～§2.6、`CHANNEL_*`（§2.1 同窗）** **对签** |

---

## 2.1 Runtime · Memory / STM（`FR-STM*` · 产品默认 v0）

**需求 SSOT**：[`memory-runtime.md` §14～§16](../../../Runtime/memory-runtime.md) · **OpenAPI** [`memory-runtime-schemas.yaml`](../../../../openapi/components/memory-runtime-schemas.yaml) · **设计管线** [`design/memory-runtime-injection.md`](../../../../design/memory-runtime-injection.md)。

**通则**：下列键 **须** **进入** **Execution §1 步 2 有效配置快照**；**变更** **须** **`configVersion`/`admin.audit`**；**环境覆盖** **须** **可观测** **实际生效值**。

| `configKey` | type（示意） | **产品默认（v0）** | 说明 |
|-------------|----------------|---------------------|------|
| `STM_L0_MAX_TURNS` | int | **10** | **L0** **近轮 user+assistant 对** **上限**（**§15.1** · **`SC-STM08`**）；**超界** **裁远端或压 rolling summary** |
| `STM_IDLE_RESUME_PROMPT_SEC` | int | **1800**（**30min**） | **写澄清/写 L1 空闲 ≥ 本值** → **§14.6 默认 stale + Resume 门控**（**`FR-STM12～14`**） |
| `STM_IDLE_DEFAULT_POLICY` | enum | **`stale_prior_write`** | **`stale_prior_write`**（**默认**）· **`prompt_resume_or_new`**（**fallback 弹 **`cl:resume`/`cl:new`**） |
| `RESUME_CLASSIFIER_MODE` | enum | **`rules_then_llm`** | **`rules_only`** **\|** **`rules_then_llm`** — **ambiguous 默认 **`new_intent`**（**`FR-STM13`**） |
| `RESUME_CLASSIFIER_MIN_CONFIDENCE` | float | **0.75** | **`resume_prior_write`** **须 **`confidence ≥` 本值** — **否则降级 **`new_intent`**（**`FR-STM14`** · **§14.6.4**） |
| `WARM_EXECUTION_INDEX_TTL_SEC` | int | **86400**（**24h**） | **温索引 **`WarmExecutionEpisode`** 保留** — **≤ session 热回收** |
| `STM_CLARIFY_SESSION_TTL_SEC` | int | **900**（**15min**） | **`ClarifySessionSnapshot.expiresAt`** **默认 TTL**（**§14.2** · **clarify-session §3**） |
| `STM_SESSION_CLEAR_MODE` | enum | **`in_place`** | **FR-STM01** **实现策略**：**`in_place`** **原地清 L0/活跃 L1** · **`rotate_session_id`** **分配新 `sessionId`** — **须** **可观测** **二者之一** |
| `STM_HOT_RECYCLE_SESSION_IDLE_SEC` | int | **86400**（**24h**） | **session 空闲热面回收**（**§14.2** · [`architecture` 热级](../../../../design/architecture.md)）；**与** **`STM_IDLE_RESUME_PROMPT_SEC`** **独立** — **见 design §2.1** |
| `STM_HOT_RECYCLE_EXECUTION_AFTER_TERMINAL_SEC` | int | **7200**（**2h**） | **execution 终局后 L1 热回收**（**v0 默认** · **先达者触发**） |

**互斥与优先级（MUST · 需求层）**：

1. **`STM_IDLE_RESUME_PROMPT_SEC`** **与 **`STM_CLARIFY_SESSION_TTL_SEC`** → **先达者触发 §14.6 stale**（**默认 stale_prior_write** · **非阻塞续/新 UI**）。  
2. **明确 inbound**（**放弃/只读/寒暄/新写意图**）→ **clarify-session §2.3** **优先** — **不必等 idle/TTL**。  
3. **规则层明确续单** → **bypass 分类器**；**ambiguous** → **Resume 分类器** — **低置信或未达 **`RESUME_CLASSIFIER_MIN_CONFIDENCE`** → **`new_intent`**（**`FR-STM13～14`**）。  
4. **全量热回收后** **下一 inbound** **须** **新意图起票** — **`SC-STM04`**。

---

## 2.2 会话并发 · `SESSION_*`（Tab：**记忆与上下文** · 与 STM 同窗快照 · **`FR-AO07`**）

**通则**：**须** **进入** **Execution §1 步 2** **有效配置快照**；**与** [`session-concurrency-policy.md`](../../domains/agent/agent-orchestration/session-concurrency-policy.md) **§2～§8** **对读**。

| `configKey` | type（示意） | **产品默认（v0）** | 说明 |
|-------------|----------------|---------------------|------|
| `SESSION_INBOUND_QUEUE_POLICY` | enum | **`serial_per_session`** | **`serial_per_session`** · **`coalesce_latest`** · **`reject_while_busy`** — **§2.1** |
| `SESSION_INBOUND_QUEUE_MAX_DEPTH` | int | **3** | **排队硬顶**；**超限** **丢弃/合并策略** **须** **可观测** |
| `SESSION_INBOUND_COALESCE_WINDOW_MS` | int | **800** | **仅** **`coalesce_latest`** **生效** |
| `SESSION_BUSY_ACK_WITHIN_MS` | int | **800** | **in-flight** **内** **须** **typing 或进度短句** |
| `SESSION_MAX_ACTIVE_WRITE_EXECUTIONS` | int | **1** | **在途写 **`executionId`** **上限** — **§3** |
| `SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN` | bool | **true** | **`unknown_pending`** **时** **挡新写（D-1 默认 ON）** — **§5.3** |

**互斥**：**`SESSION_MAX_ACTIVE_WRITE_EXECUTIONS=1`** **与** **类型 A / clarify / UNKNOWN 优先级表** **同窗** — **不得** **仅靠** **配置** **>1** **绕过** **§1.2 六款** **写确认**。

---

## 2.3 只读澄清 · `READ_*`（Tab：**记忆与上下文** · **`FR-AO08`**）

| `configKey` | type（示意） | **产品默认（v0）** | 说明 |
|-------------|----------------|---------------------|------|
| `READ_CLARIFY_SESSION_TTL_SEC` | int | **600**（**10min**） | **`ReadClarifySessionSnapshot.expiresAt`** — **短于** **`STM_CLARIFY_SESSION_TTL_SEC`** |
| `READ_CLARIFY_MAX_TURNS` | int | **2** | **只读澄清轮次软顶** — **超限** **缩窄或拒答** |

**SSOT**：[`read-clarify-session.md`](../../domains/agent/agent-orchestration/read-clarify-session.md)。

---

## 2.4 UNKNOWN 追问 · `UNKNOWN_*`（Tab：**记忆与上下文** · **`SC-RISK-06～07`**）

**通则**：**须** **与** [`unknown-stall-policy.md`](../../risk/unknown-stall-policy.md) **§2～§3** **对读**；**504 对账算法** **不** **在本表**。

| `configKey` | type（示意） | **产品默认（v0 · 语义）** | 说明 |
|-------------|----------------|---------------------------|------|
| `UNKNOWN_STALL_ALERT_SEC` | int | **300**（**5min · 示意**） | **无进展 Δt 告警** — **§1** |
| `UNKNOWN_USER_RECONCILE_COOLDOWN_SEC` | int | **30** | **用户追问触发 reconcile 最小间隔** — **§2.4** |
| `UNKNOWN_MAX_USER_FOLLOWUP_RECONCILE_PER_EXECUTION` | int | **5** | **单 **`executionId`** 用户触发 reconcile 上界** |
| `UNKNOWN_FOLLOWUP_COPY_THROTTLE_SEC` | int | **60** | **同 UNKNOWN 长模板复读节流** — **§2.4 U5** |
| `UNKNOWN_RECONCILE_MAX_ATTEMPTS` | int | **所内 MR 冻** | **自动+用户 reconcile 总轮次上界** — **§1** |

**互引**：**D-1 挡新写** **仍** **用** **`SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN`**（**§2.2**）。

---

## 3. 交易护栏 · 默认值（Tab：**交易护栏** · FR-MC704～705）

| `configKey` | type（示意） | 说明 |
|-------------|----------------|------|
| `AGENT_MIN_VIP_TIER` | int | 最低 VIP；**比对须取母账号（`userId`）之 `vipTier`**（[`eligibility-runtime` §1](../../admin/access-control/eligibility-runtime.md) Step **VIP**）；**运营编辑 UX** [`access-control`](../access-control/overview.md)；与 **运营摘要、`I02`、FR-T02** 对签 |
| `SYMBOL_POLICY_MODE` | enum | allowlist/blocklist · **OpenAPI 枚举终裁** |
| `SYMBOL_ALLOWLIST` | string[]（JSON） | **可下单 symbol 列表** |
| `SYMBOL_BLOCKLIST` | string[]（可选） | 黑名单并行 · **可选** |
| `AGENT_PRICE_DEVIATION_BPS` | int | 限价/建议价最大偏离 |
| `AGENT_COOLDOWN_SEC` | int | 写操作冷却 |
| `AGENT_MAX_NET_EXPOSURE_USDT` | decimal | **最大持仓**口径（净名义）；见 [`runtime-policy` §6](../../agent/exchange-agent/boundaries.md#6-position-governance仓位治理) |
| `AGENT_MAX_DISTINCT_SYMBOLS` | int | **最大币种数**（distinct symbol） |
| `AGENT_MAX_SINGLE_SYMBOL_WEIGHT_BPS` | int | **最大单币占比**（bps） |
| `AGENT_MAX_SESSION_LOSS_USDT` | decimal | **最大亏损**闸（实现+浮亏；窗口定义 `design`/ADR） |
| `AGENT_LARGE_ORDER_THRESHOLD_USDT` | decimal | **大额订单**阈（[`runtime-policy` §4·§8](../../agent/exchange-agent/boundaries.md#4-confirmation-policy交易确认策略)） |
| `AGENT_HFT_WINDOW_SEC` | int | **高频检测**滑动窗（秒） |
| `AGENT_HFT_MAX_WRITES_PER_WINDOW` | int | **窗内**最大写次数（与上键成对） |
| `AGENT_*`（其它） | — | **`AGENT_SLIPPAGE_BPS`、`AGENT_MAX_LEVERAGE`** 等 · **按 MR 增补** · 细则见 [`boundaries.md`](../../agent/exchange-agent/boundaries.md)、[`exchange-agent/overview-legacy-migration.md`](../../agent/exchange-agent/overview-legacy-migration.md) **§2**（旧 **§10.5** 产品线闸映射） |

**与模板**：全局为底、`agent-management` 模板风控 **只可收紧**，见 [`functions.md`](functions.md) **§2.6**。**配置叠层**：[`runtime-policy §2`](../../agent/exchange-agent/boundaries.md#2-runtime-trading-policy-priority运行时配置叠层优先级)。

---

## 4. 渠道 · Telegram（Tab：**渠道** · FR-MC706～711）

**产品叙事与运营功能项**：[`telegram/overview.md`](../../agent/telegram/overview.md) **§2.5 · 类型 A；§2～§2.6**，[`telegram/admin-bot-config.md`](../../agent/telegram/admin-bot-config.md)（**FR-TG-ADMIN-01～06**）。**卡片 / `callback` 交互全集** **不**在本 Tab 编辑 — 见 [`interaction-flow-standard.md`](../../../standards/interaction-flow-standard.md) **§8**。

### 4.1 编排摘要（只读 · FR-MC706）

| 数据源 | 说明 |
|--------|------|
| **Telegram 编排摘要** | **只读**；不写 Bot `callback`/卡片正文。`configVersion` 与 `exchange-agent` / `telegram` **读路径** **同城对签**。 |

### 4.2 非密钥运行参数（可写 · FR-MC709）

下列键可走 **全局配置 bundle** 原子提交 **`design` 冻结**，或由 **Telegram 子 resource** **独立 `PUT`/`If-Match`** — **OpenAPI 终裁**。**须**计入 **`configVersion`**（或 **子版本** **`design` 单列**），与 **SC-TAC-04 / SC-TG-ADMIN-02** 对签。

| `configKey` | type（示意） | 说明 |
|-------------|----------------|------|
| `TELEGRAM_DEFAULT_LOCALE` | string | **BCP 47** 子集或由 **enum** 冻结；Bot 应答 **默认语言**（与用户级偏好合并策略 **`design`/ADR**） |
| `TELEGRAM_HELP_H5_URL_TEMPLATE` | string | **主站/H5「帮助」** 落地 URL 模板（**禁止**嵌入长期 JWT；占位符 **`OpenAPI`** 冻结） |
| `TELEGRAM_WEBHOOK_URL_TEMPLATE` | string | **Webhook 公网基址 + path 模板**（**不得**含 Bot Token；**服务端** 与 vault Token **拼装** — **[`FR-TG-ADMIN-04`](../../agent/telegram/admin-bot-config.md)**） |
| `TELEGRAM_LINK_PREVIEW_DEFAULT` | bool | **消息链默认** 是否允许 **link preview**（与 [`telegram/overview.md`](../../agent/telegram/overview.md) **§2.2** **卡片与 Deeplink** 体验一致） |
| `TELEGRAM_TYPING_INDICATOR_MODE` | enum | **`off` / `auto`** 等 · **减少骚扰** 与 **可感知延迟** 折中 · **`design` 冻结** |
| `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN` | string（多行） | **简体中文**（`zh-Hans`）· **Agent 开通完成** ∧ **Telegram 已绑定** 后 **首次** **欢迎消息正文**（[`telegram/overview.md`](../../agent/telegram/overview.md) **§2.1.1**、[`admin-bot-config.md`](../../agent/telegram/admin-bot-config.md) **FR-TG-ADMIN-06**） |
| `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_TW` | string（多行） | **繁体中文**（`zh-Hant`，台港澳等）· **同上** **触发与幂等** |
| `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_EN` | string（多行） | **英文** · **同上** |
| `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT` | string（多行） | **迁移/兼容键**（**可选**）：**若** **按** **§2.1.1** **语言解析 + 回退链** **仍无** **非空** **正文** **且** **本键非空** → **投递** **本键**；**若** **`_ZH_CN` 空** **且** **本键非空** → **简体** **亦可** **回退** **至** **本键**（**同窗** **overview §2.1.1**）。**新建** **须** **以** **三语键** **为主** |

**欢迎语** **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_*`** **共享**：**占位符白名单**（如 `{displayName}`）· **`OpenAPI`/渲染 `design` 冻结**；**每条** **须** **低于** Telegram **`sendMessage` 上限**（[`telegram/overview` §2.6](../../agent/telegram/overview.md)），超限 → **写入拒绝**或 **裁剪** **`design` 冻结**（**校验** **对** **各语** **逐条** **或** **聚合** **`design` 终裁**）

### 4.3 凭证引用（可写 · FR-MC710 · 高危）

| `configKey` / 字段 | type（示意） | 说明 |
|--------------------|----------------|------|
| `TELEGRAM_BOT_TOKEN_SECRET_REF` | string | **Vault / KMS 路径名或逻辑 `secretRef`**；**控制台、审计默认值、导出** **禁止**明文 Token · 与 [`ai-settings`](../ai-settings/overview.md) **同窗** |

**轮换语义**：旧 ref 下线、Webhook 重登记顺序与 **短窗双活** **否** **由 `design`/Runbook 冻结**。

### 4.4 Webhook 运维与自检（FR-MC711）

**不**强制建模为 `configKey`：**setWebhook** / **deleteWebhook** / **连通性探测** 为 **运维 API 动作**（[`design/api.md`](../../../../design/api.md) **登记表 · Telegram Bot** 行）；须 **RBAC、`admin.audit`**，与 **`getWebhookInfo` 摘要** **同窗展示**。

---

## 5. `BILLING_*`（控制台边界）

账务语义 **SSOT**：[**`billing-management/overview.md`**](../billing-management/overview.md) **§7.4 · §11**。**模块五控制台** **`FR-MC501～508`**：详见 [`billing-management/functions.md` §2](../billing-management/functions.md)。下列键 **`configKey` 字符串** **`OpenAPI`/附录 A§5.1** **同窗终裁**；若所内命名不同，**仅**改本节与附录 **同行 MR**。

| `configKey`（示意） | type（示意） | 说明 |
|---------------------|----------------|------|
| `BILLING_MODE` | enum | **`shadow`** **\|** **`enforce`** · 与控制台 **计费健康（FR-MC501）**、`design` **同窗** |
| `BILLING_TOKEN_RATE` | JSON 或分项 `configKey`（OpenAPI 终裁） | **Token 费率**：input/output 计价（如 **每 1k token · USDT**）；**可选**按 `modelId`/场景分档；**Schema 同窗** **FR-MC502** / **FR-B02** 可读子集 |
| `BILLING_SETTLE_POLICY` | enum 或结构化 | **`billing.md` §7.4**：**默认 `ENTITLEMENT_ONLY`** — **S5 仅轨 B**；**禁止** **未 ADR** **`DUAL_RAIL`/`TOKEN_CHARGE`** — **同窗** [`commerce-model` §4](../billing-management/commerce-model.md) |
| `PHASE2_COMMERCE_RAILS_ENABLED` | boolean | **`false` 默认** · 启用后 Runtime/BFF **可走轨 B HTTP**（**S2 balance / S5 debit**）；**不**扩写 **CC-P0-03** — [`commerce-model` §5.2](../billing-management/commerce-model.md)、[`config.md`](../billing-management/config.md) |
| `effectiveMinChargeUsdt`（或同窗 `BILLING_MIN_CHARGE_USDT`） | decimal | **§7.2** 单次 **可计费**阈值；与 **账务划转 HTTP** **粒度**对齐 |
| `BILLING_AGENT_REVENUE_ACCOUNT_REF` | string（模板） | **附录 A `D-12`/`CC-P0-04`**：收入 **专户**标识 — **V1 范式** [`billing-management/overview.md` §10.6.1](../billing-management/overview.md) |
| `BILLING_CAPABILITY_MAP` | JSON（同窗名 `design` 终裁） | **`scenarioId`/自动化类型 → Capability SKU** **与** **扣额权重/聚合** — **Phase 2** · [`commerce-model.md`](../billing-management/commerce-model.md) **`functions` §5** |
| `COMMERCE_SKU_CATALOG_REF` | string 或 JSON | **SKU/套餐目录** **真源引用**（CMS/DB/配置服务）；**控制台** **FR-MC509** — **OpenAPI MR** **收束** |

其它 **`BILLING_*`**（币种、PSP 网关映射、**SKU** 等）按 **`FR-MC502`/`FR-MC508`、`FR-MC509`** MR 增补；若在 **附录 A§5.1** 暴露，须 **产品与账务 owner 双签** 并回本表追加一行。

## 6. 写路径元数据（FR-MC707～708）

| 概念 | 说明 |
|------|------|
| `configVersion` / `ETag` | 乐观锁；**409 · `ADMIN_OPS_CONCURRENT`**（[`management-console`](../management-console-v1-prd.md) **§7.2 · §8.4**） |
| **`configSnapshotId`** | **回滚**快照 |
| **Diff 摘要** | 落 **`admin.audit`**；字段下限与 [`observability`](../../../observability/overview.md) **及** **`design`/OpenAPI** **并列冻结** |

---

**文档版本**：0.1.18 · **维护**：后台 + Runtime owner · **本版**：**§2.1 stale 默认 · Resume 分类器 · 温索引 TTL**。**承** **0.1.17**。



