# FE 对接清单（后端已就绪）

最新条目在 **顶部**。实现请 **`/fe`** 在 **`admin/`** 完成；契约真源 **`server/docs/BACKEND_SPEC.md`**、**`API_INTEGRATION_GUIDE.md`** §4.3 / §4.11。

**交付确认（勾选）**：`/fe` 每完成一条清单项，须将本文对应项从 `- [ ]` 改为 `- [x]`，便于 **`/be`** 核对前端已交付；未完成则保持未勾选。

---

## 2026-05-28 — 只读续轮「深度数据呢」ValidationError / 交易对污染

### 背景

盘面分析后继续问 **「深度数据呢」** 偶发 **ValidationError** 或查错交易对：只读 **pending** 被 **`last_trade_slots`** 覆盖；意图分数加成可能 **>1** 导致 Pydantic 校验失败。

### FE

**本次无需 FE 跟进**。

### 验收

1. 先查 **BTC** 盘面/深度，再问 **「深度数据呢」** → 仍 **BTC-USDT** · **`read.market.depth`**，无内部错误。
2. 同会话曾有现货下单上下文时，只读续轮不被 **ETH** 等写单槽位带偏。

### Refs

`tests/test_read_context_carryover.py` · `tests/test_intent_ranked_clamp.py` · `BACKEND_SPEC.md` 变更表 2026-05-28。

---

## 2026-05-28 — 全场景意图矩阵回归 + 合约路由修复

### 背景

**`/be`** 新增 **`tests/test_scenario_intent_matrix.py`**（只读/现货/合约/杠杆/条件单/FAQ + 交易与只读多轮）；修复 **`_prefer_trade_on_complete_spot_slots`** 在 **「BTC永续市价买入」** 等句误拉回 **spot flash** 的问题。

### FE

**本次无需 FE 跟进**。

### 验收

- `uv run pytest tests/test_scenario_intent_matrix.py` 全绿
- `test_runtime_intent_futures_market_keyword` 恢复 **trade.futures.market_order**

---

## 2026-05-28 — 交易多轮澄清 / 门禁误报修复（Telegram）

### 背景

用户截图两类问题：（1）**「看下账户余额」「当前市价」** 偶发 **「暂时无法加载门禁或路由」**——根因含 **`agent_llm_clarify` `session_id` NameError** 被 inbound 吞掉；（2）**「买入 1 eth」→ 闪兑 → 当前市价** 反复问闪兑/限价或落 **只读 ticker**。后端已修：**`last_trade_slots`** 跨轮保留、**`clarify_phrase_slots`**、**pending/trade 路由加权**、**`tradeMode` 已齐时跳过 LLM 澄清润色**；inbound 区分 DB 与内部异常文案。

### FE

**本次无需 FE 跟进**（Telegram + `recognize_intent_full` / STM）。

### 验收（QA / 自测）

1. 已绑定用户：**买入 1 eth** → 确认摘要（非 FAQ 长文）。
2. 续轮 **闪兑** / **闪队** → 不再重复同一澄清问句。
3. **当前市价** → 延续 **闪兑 Type-A**，非 **read.market.ticker** CLARIFY。
4. **看下账户余额** → **read.account.balance**（非门禁 fallback）。

### Refs

`server/docs/BACKEND_SPEC.md`（变更表 2026-05-28 交易多轮）、`tests/test_trade_context_carryover.py`。

---

## 2026-05-28 — 只读多轮上下文修复（Telegram）

### 背景

用户反馈：句内 **`BTC-USDT`** 未识别、查价后说「盘面分析」又索要交易对。后端已修：**中文邻接交易对抽取** + **只读成功后保留 `symbol` 槽位** + **跟进话术路由 depth**。

### FE

**本次无需 FE 跟进**（纯服务端 Parser/STM）。

---

## 2026-05-28 — MR-MEM-01（续）· GlobalConfigBundle + 只读澄清键盘

### 背景

**`/be`** 补齐：**Admin 全局 bundle 写**（STM/SESSION/READ 键热生效）、**只读澄清 Telegram `rc:*` 出站键盘**、**`coalesce_latest` 入站**、**类型 A 取消** 释放写门控。

### 契约

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/trading-agent-config/bundle` | **`configVersion`** + **`values`**（Env 默认与 DB 覆盖合并）+ **`defaults`** |
| `PATCH` | 同上 | Body **`{ values, expectedConfigVersion? }`**；Header **`If-Match`** 或 body 版本；**409** 乐观锁冲突 |

**键名**：`STM_*` / `SESSION_*` / `READ_*`（见 `memory-runtime-config-constants.ts`）；PATCH 后 **无需重启** API（`get_effective_settings()` 读内存覆盖）。

**只读澄清出站**：`scope_portfolio_vs_market` → **`rc:scope:market` / `rc:scope:portfolio`**；`multi_symbol_compare` → **`rc:sym:*`**；监控草案 → **`rc:mon:*`**。

### FE 任务清单

- [x] **`admin-trading-agent-config.ts`**：`getTradingAgentConfigBundle` / `patchTradingAgentConfigBundle`（带 **`If-Match`**）
- [x] **`MemoryRuntimeConfigPanel`**：由只读 Env 参考改为 **GET 展示当前值 + PATCH 保存**（`configVersion` 乐观锁）
- [x] 保存成功提示：**热生效**，无需重启（与 Env 冲突时 bundle 覆盖优先）

### 验收

1. PATCH `STM_L0_MAX_TURNS=12` 后，同进程 Telegram 澄清 L0 上限行为变化（或 Admin context 对账 `configSnapshot.stmL0MaxTurns`）。
2. 「盈亏怎么样」→ 出站含 **看全市场/看我的持仓** 按钮；点 **portfolio** 走持仓读路径（0 写）。

### Refs

- `server/chainup_agent/application/memory_runtime_settings.py` · `admin_trading_agent_config.py`
- `product-doc/specs/openapi/admin/users-global-config.yaml`

---

## 2026-05-28 — MR-MEM-01 · 澄清会话 v1.6 / stale+Resume / 会话并发

### 背景

后端落地 **OP-MEM** 规格批次：`ClarifySessionSnapshot` 生命周期（**active/stale/abandoned**）、**idle/TTL** 先达 → **stale + WarmExecutionEpisode**、**Resume 分类器**（规则层 · `confidence≥0.75`）、**§2.3 每条 inbound 重意图**（放弃/只读打断/寒暄）、**`cl:*` / `rc:*` 澄清回调**（与 **`cf:*`/`fcp` 类型 A** 分层）、**session 串行队列** + **`update_id` 幂等**、**FR-STM11 记忆治理四步闸**（L0 denylist 过滤）。

### 契约

| 项 | 说明 |
|----|------|
| **澄清回调** | **`cl:fc`/`cl:lo`/`cl:buy`/`cl:sell`/`cl:resume`/`cl:new`** 等 — 仅合并槽位，**0** `call_exchange_write`；**`rc:*`** 只读澄清 |
| **类型 A 优先** | **`pendingTypeAValid`** 时 **不** 推进写澄清 stale 废卡 |
| **Env（`CHAINUP_AGENT_*`）** | **`STM_IDLE_RESUME_PROMPT_SEC`**（默认 1800）、**`STM_CLARIFY_SESSION_TTL_SEC`**（900）、**`RESUME_CLASSIFIER_MIN_CONFIDENCE`**（0.75）、**`SESSION_INBOUND_QUEUE_POLICY`**（`serial_per_session`）、**`SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN`**（true） |
| **观测** | **`agent.memory.resume_classified`**（日志/后续时间线）、**`agent.memory.session_cleared`** 仍含 **澄清 abandon** |
| **Prompt/STM** | **`runtime_context.agentRuntimeMemoryContext`** — **`shortTermL1[].clarifySummary`** 人话摘要（**非**裸 JSON） |

### FE 任务清单

- [x] **Telegram 出站**：写澄清轮 **`inline_keyboard`**（`cl:fc`/`cl:lo` 等）— **`telegram_clarify_keyboard.py`** / **`telegram_clarify_outbound.py`** · CLARIFY 分支已挂 **`reply_markup`**
- [x] **Admin 协查**：执行详情展示 **`lifecycleState`/`clarifyTurn`/`resolvedSlotsSoFar`**（时间线 + **`GET /api/v1/runtime/memory/sessions/{sessionId}/context`** 响应 **`clarifySession`**）
- [x] **配置页（Phase1）**：**`MemoryRuntimeConfigPanel`** 只读 Env 参考已就绪；**可编辑 PATCH** 见上文 **「MR-MEM-01（续）」** 清单

### 验收

1. 澄清中用户「都不要了」→ **无** 复读闪兑/限价盘问（**`eval.clarify.abandon_on_cancel`**）。
2. 澄清中「只查价」→ 只读应答 + 写澄清 **abandon**（**`eval.clarify.read_interrupts_write`**）。
3. 空闲后「你好」→ **寒暄**，**0** 写澄清模板（**`eval.memory.idle_default_stale`**）。
4. stale 后「还是买 BNB 100U 闪兑」→ **resume** 合并槽位（**`eval.memory.resume_classifier_gate`**）。
5. 连发两条 inbound → **≤1** 完整 Parser 链（**`eval.session.inbound_serial_no_double_parse`**）。

### Refs

- `server/chainup_agent/application/clarify_session.py` · `read_clarify_session.py` · `memory_stale_resume.py` · `session_concurrency.py` · `memory_governance.py` · `clarify_inbound.py`
- `product-doc/specs/requirements/domains/agent/agent-orchestration/clarify-session.md` **v1.6**
- `product-doc/specs/openapi/components/memory-runtime-schemas.yaml`

---

## 2026-05-27 — S11 写路径澄清（全品类 + LLM + 多轮槽位）

### 背景

**`trade_slot_clarify`** 覆盖 **闪兑/现货限价/全仓杠杆市价·限价/合约市价·限价**；**`RESOLVE_TRADE_NOTIONAL`**（= 闪兑/杠杆市价「全部买入」读余额）；**`sessionId`** **`pending_clarify_slots`** 多轮合并；可选 **`intentClarifyUseLlm`** → 时间线 **`llm.agent.runtime.runtime_clarify`**。

### 契约

| 项 | 说明 |
|----|------|
| **`plan.nextStep`** | **`CLARIFY`** \| **`RESOLVE_TRADE_NOTIONAL`** \| **`RESOLVE_FLASH_NOTIONAL`** \| **`CONFIRM_TYPE_A`** |
| **`policyCodes`** | **`QUOTE_PAIR_NOT_FROZEN`**、**`TRADE_NOTIONAL_PENDING`**、**`FUTURES_NOMINAL_AMBIGUOUS`**、**`SLOT_TRADE_INCOMPLETE`** |
| **Env** | **`CHAINUP_AGENT_INTENT_CLARIFY_USE_LLM`**；Admin **`gateway_defaults.intentClarifyUseLlm`** |
| **限价 `quoteQty`** | Telegram/裁决 BUY 侧按限价换算 **base `quantity`** |

### FE 任务清单

- [x] 意图调试 / 协查：展示 **`plan.clarify[]`**、**`policyCodes`**、**`RESOLVE_TRADE_NOTIONAL`**
- [x] Admin 网关默认：可选开关 **`intentClarifyUseLlm`**（类型待 **`/fe`** 表单）
- [x] 时间线筛选 **`llm.agent.runtime.runtime_clarify`**

### 验收

1. 多轮：「全部买入 BCH」→ 澄清计价 →「是」→ **`RESOLVE_TRADE_NOTIONAL`**（需绑定）→ Type A。
2. 「全仓杠杆 全部买入 ETH」→ 同上（杠杆市价）。
3. 「BTC-USDT 限价 65000 用 100U 开多」（合约）→ **`FUTURES_NOMINAL_AMBIGUOUS`** 澄清。

### Refs

- `server/chainup_agent/application/trade_slot_clarify.py`
- `server/chainup_agent/application/agent_llm_clarify.py`
- `server/chainup_agent/application/memory_session_store.py`（**`pending_clarify_slots`**）

---

## 2026-05-27 — 写路径 spec_read · STM 主链路 · 澄清/防猜（E2E 对齐）

### 背景

后端按 E2E 图收口：**Type A 前** 统一 **`agent.skill.spec_read`**（含闪兑/合约/杠杆/条件单等已登记 skill）；**Telegram** 接入 **STM**（L0 召回进 `runtime_context.stmL0Messages`、回合写回、**「重新开始」** / **「清空记忆」** 分流）；意图 **多轮** 传 **`previousScenarioId`**；LLM NLU **剔除无文本依据的槽位**。

### 契约（行为 · 无新 Admin API）

| 项 | 说明 |
|----|------|
| **写路径** | `CONFIRM_TYPE_A` 且场景在 skill 映射表内 → 时间线 **`binding_resolved` → `spec_read` → `confirmation.required`**（闪兑 Telegram 已补 **`confirmation.required`**） |
| **HTTP 闪兑** | `POST …/trade/spot/flash-convert` 在下单前同样写入 **spec_read + confirmation + implicit confirm** |
| **STM** | `runtime_context.memoryContext` + `stmL0Messages`（最近 8 条）；事件 **`agent.memory.session_cleared`** / **`agent.memory.ltm_revoke_requested`** |
| **LTM** | 用户说「清空记忆」→ 说明与 STM 分流，**不** 清 STM-only |
| **澄清** | Telegram 自动带 **`previousScenarioId`**（同 `tg:{chatId}` 上一 resolved 场景） |

### FE 任务清单

- [x] 执行详情时间线：闪兑/合约写路径应可见 **`agent.skill.spec_read`**（治理区 SC-OM-05）
- [x] 可选：协查页展示 `runtime_context.stmL0Messages`（若后续接只读 API）— **暂缓**（2026-05-27 · 无 Admin 只读 API，待 **`/be`**）
- [x] 产品文案：LTM 撤销仍为 **筹备中**（与后端回复一致）

### 验收

1. Telegram 闪兑意图 → 时间线含 **`agent.skill.spec_read`** 且早于 confirm 相关事件。
2. 同会话先说「限价买 BTC」缺价 → 澄清；下一条补价格 → 仍识别为限价场景（`previousScenarioId`）。
3. 「重新开始」→ 回复确认句 + 下轮不再带旧 L0 上下文。

### Refs

- `server/chainup_agent/application/telegram_stm.py`
- `server/chainup_agent/application/write_path_pipeline.py`
- `server/docs/BACKEND_SPEC.md` 修订记录 2026-05-27

---

## 2026-05-27 — 执行详情 Tab：任务队列 / 运行事件 / Retries / Recovery

### 背景

后端为 **`/runtime/executions/:id`** 四个占位 Tab 提供只读 API，数据来自 **`agent_execution_event`**（任务队列叠加 **`orchestration_flow_catalog`** 步骤定义）；恢复 Tab 复用对账推断（与 **`GET /api/v1/agent/trading/reconcile/status`** 同源逻辑）。

### 契约

**鉴权**：与其它 Admin Observability 一致。

| Tab | Method | Path | 响应要点 |
|-----|--------|------|----------|
| 任务队列 | `GET` | `/api/v1/admin/observability/executions/{executionId}/queue` | `{ items: [{ taskId, executionId, state, scheduledAt, stepKey?, stepLabelZh? }] }` · **`state`**: `PENDING` \| `RUNNING` \| `BLOCKED` |
| 运行事件 | `GET` | `…/events` | `{ items: [{ executionId, at, eventType, summary, seq? }] }` · **不含** `agent.orchestration.step` |
| 重试 | `GET` | `…/retries` | `{ retryCount, items: [{ attempt, at, reason, eventType?, seq? }] }` |
| 恢复 | `GET` | `…/recovery` | `stillUnknown`, `caseKind`, `resolutionStatus`, `recoveryTitle`, `recoveryBody`, `observabilitySearchPath`, `reconcileApiHint`, `manualRetrySupported`（恒 `false`） |

**404**：`AGENT_ADMIN_EXECUTION_NOT_FOUND`（与 timeline 一致）。

### FE 任务清单

- [x] **`admin/src/api/admin-observability.ts`**（或同级 client）新增上述 4 个 GET 与类型
- [x] **`ExecutionDetailPage.vue`**：`tab=queue|events|retries|recovery` 时拉对应 API，替换 Phase1 占位文案
- [x] **Retries** 表头「重试次数」可与 **`retryCount`** 或总览占位对齐
- [x] **Recovery**：展示 **`recoveryTitle`/`recoveryBody`**；**`observabilitySearchPath`** 链到 **`/observability?executionId=`**（与原型 **`obsHref`** 一致）
- [x] 运行事件 **`eventType`** 可继续用现有 **`zhRuntimeEventType`** 映射（API 返回持久化名如 **`trading.exchange_private`**）

### 验收

1. 对含 **`agent.orchestration.step`** 的 execution，`/queue` 返回未完成步骤行。
2. 对含工具/对账事件的 execution，`/events` 有条目且不含 orchestration 步。
3. 对 `unknown` + `trading.reconcile` 时间线，`/retries` **`retryCount` ≥ 1**。
4. `/recovery` 返回 **`observabilitySearchPath`** 含当前 **`executionId`**。

### Refs

- `server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md` §6
- `server/chainup_agent/application/admin_observability_execution_tabs.py`
- 产品：`product-doc/specs/requirements/admin-console/page-specs.md` · `runtime.execution-detail`

---

## 2026-05-27 — Prompt 治理 16 包入库（`pp-*` · Admin 编辑真源）

### 背景

产品 **16 包**正文已与 Demo 模板对齐（`product-doc/src/admin/src/data/promptBodyTemplates.ts`）。后端新增迁移 **`0030_governance_prompt_pack_seed`**：将 **`pp-system-core`** 等 **16 个 `promptPackId`** 以 **`PUBLISHED` v1** 写入 **`admin_prompt_pack`**；既有 **`pack_*_v1`** 同行 **`scenarioId`** 标为 **`DEPRECATED`**。Runtime / effective / binding **优先按 governance-map 解析 `pp-*`**。

### 契约

| 动作 | 说明 |
|------|------|
| **迁移** | 联调/生产库执行：`cd server && uv run alembic upgrade head`（含 **0030**） |
| **列表** | `GET /api/v1/admin/prompt-packs` 出现 **`pp-*`**；旧 **`pack_*`** 为 **DEPRECATED**（勿再 Publish） |
| **编辑** | `GET/PATCH …/prompt-packs/{promptPackId}` 使用 **`pp-trading-spot-limit`** 等治理 id |
| **读侧** | `read.market.*` 等解析到 **`pp-analysis-core`**（`scenario_id=agent.runtime.analysis_core`） |
| **横切** | **`pp-runtime-clarify`** / **`pp-runtime-output-contract`** 已入库；binding 四槽非空 |

写路径 TRADING 包 **`variableSchema.skillSpecRef`** 种子为 **`skillId` 字符串**（Publish 前须在 skill-specs 已发布对应版本）。

### FE 任务清单

- [x] **`/prompts/strategy`** 列表：以 API 返回 **`pp-*`** 为主键打开编辑器（勿写死 `pack_*`）
- [x] 合并 Demo mock 时：**以 DB 列表为准**，mock 仅补登记册文案
- [x] 执行协查 **`summarizeTradingPromptBinding`** 可显示 **`pp-*`** id（后端已返回）

### 验收

1. 迁移后 `GET …/prompt-packs` 含 **16 条 `pp-*` + `PUBLISHED`**。
2. 打开 **`pp-trading-spot-limit`** 编辑器可见六段 Markdown 正文。
3. `GET …/internal/prompts/effective?scenarioId=trade.spot.limit_order` 的 **`resolvedPromptBinding.tradingPromptPackId`** = **`pp-trading-spot-limit`**。

### Refs

- `server/chainup_agent/data/prompt_governance_catalog.py`
- `product-doc/specs/requirements/prompts/governance-map.md`
- `product-doc/product/prompt-governance-checklist.md` §三

---

## 2026-05-26 — 执行协查 `/runtime/executions` · Prompt 治理与时间线（对齐 5176 原型）

### 背景

后端已对齐产品 **SC-PM-22 / SC-OBS04**：跨包 **`resolvedPromptBinding`**（平台 SYSTEM/SAFETY + 场景 TRADING + 横切 clarify/output 槽位）、时间线 **`agent.prompt.binding_resolved`**、**`summary.promptBindingResolved` / `summary.skillSpecRead`** 镜像字段，以及场景 **Skill 范围** 只读 API。  
生产 **`admin/`**（5173）详情页已有 **`promptPackVersion` / `resolvedPromptBinding`** 总览与时间线 Tab；**治理四折叠块**（Skill 范围 / Prompt 拼装追溯 / Skill Spec 读侧 / Canonical）需按 **`product-doc` 5176** 接线。

### 契约

**鉴权**：与其它 Admin 一致，`Authorization: Bearer <access_token>`。

| 用途 | Method | Path |
|------|--------|------|
| 执行列表 | `GET` | `/api/v1/admin/observability/executions` |
| 执行详情 | `GET` | `/api/v1/admin/observability/executions/{executionId}` |
| 时间线 | `GET` | `/api/v1/admin/observability/executions/{executionId}/timeline` |
| 场景 Skill 范围 | `GET` | `/api/v1/admin/observability/scenarios/{scenarioId}/skill-scope` |

**列表 Query（生产已实现 · 与 5176 原型差异）**

| 原型 `observabilityExecutions.ts` | 生产 `admin-observability.ts` | FE 建议 |
|-----------------------------------|-------------------------------|---------|
| `cursor` / `nextCursor` | `limit` + `offset` + `total` | 分页用 offset；勿假定 cursor |
| `status` | `state`（`ACCEPTED`/`SUCCEEDED`/`FAILED`/`CANCELLED`） | 映射字段名 |
| `intentContains` | `keyword`（子串匹配 executionId/userId/scenarioId） | 合并检索框映射到 `keyword` |
| `orchestrationVersion` / `intent` 摘要 | **无** | 列表列可继续占位「—」或从 `note`/`scenarioId` 推导 |

**`ResolvedPromptBinding`（camelCase · 详情 + 时间线）**

| 字段 | 说明 |
|------|------|
| `systemPromptPackId` / `systemPromptPackVersion` | 平台 SYSTEM（DB 常为 `pack_platform_system_v1`；条文 `pp-system-core`） |
| `safetyPromptPackId` / `safetyPromptPackVersion` | 平台 SAFETY（`pack_platform_safety_v1` / `pp-safety-global`） |
| `tradingPromptPackId` / `tradingPromptPackVersion` | 场景策略 TRADING 包 |
| `runtimeClarifyPromptPackId` / `runtimeClarifyPromptPackVersion` | 横切澄清；**无已发布包时为 `null`** |
| `runtimeOutputContractPromptPackId` / `runtimeOutputContractPromptPackVersion` | 输出契约；**无包时为 `null`** |
| `fewShotDigest` | 场景包 few-shot 摘要 hash（可选） |
| `placeholderDenylistRevision` / `safetyPhraseBlocklistRevision` | 与 Publish 闸同窗 |

**时间线 `summary`（`ObservabilityTimelineItem`）**

- **`agent.prompt.binding_resolved`**：`summary.resolvedPromptBinding` 与 **`summary.promptBindingResolved`**（同对象，便于原型 `parseBindingFromTimeline` 逻辑迁移）。
- **`agent.skill.spec_read`**：`skillId`、`skillSpecVersion`、`specDigest` + **`summary.skillSpecRead`** 对象镜像。
- **`prompt.snapshot`** + `stepKind=trading_write`：仍含 **`resolvedPromptBinding`**（写路径 AC-5）；拼装追溯可优先读 binding 事件，其次 snapshot。

**`GET …/scenarios/{scenarioId}/skill-scope` 响应要点**

| 字段 | 说明 |
|------|------|
| `mode` | `write_skill` \| `read_only` \| `unmapped_write` |
| `skills[]` | 写路径主 Skill：`skillId`、`skillSpecVersion`、`specDigest`、`contractComplete`、`role` |
| `promptStrategyPackId` / `promptStrategyVersion` | 已发布场景 TRADING 包 |
| `promptSkillScopeRef` | 来自包 `variableSchema.skillSpecRef` 或 `skillId@version` 推断 |
| `narrative` | 只读说明文案（中文） |

**类型扩展**：`admin/src/shared/api/admin-prompt-packs.ts` 的 **`ResolvedPromptBinding`** 建议补上 **`runtimeClarify*`** / **`runtimeOutputContract*`**（与 OpenAPI 一致）。

### FE 任务清单

- [x] **`admin/src/shared/api/admin-observability.ts`**：扩展 `ResolvedPromptBinding` 与时间线 `summary` 类型（`promptBindingResolved`、`skillSpecRead`）；新增 **`getScenarioSkillScope(scenarioId)`**。
- [x] **`/runtime/executions/:executionId`**（`ExecutionDetailPage.vue`）：总览下增加 **治理折叠区**（对齐 `ExecutionDetailGovernanceSection`）：Skill 范围接 **`skill-scope`** API；Prompt 拼装层用 **`bindingToAssemblyLayers`** 逻辑移植（可放 `shared/lib/execution-prompt-assembly.ts`）；Skill Spec 从时间线 **`skillSpecRead`** 渲染。
- [x] **`ObservabilityExecutionTimelinePanel.vue`**：对 **`agent.prompt.binding_resolved`** 展示拼装层摘要；对 **`agent.skill.spec_read`** 展示 skill 版本行（已有 `resolvedPromptBinding` 的 snapshot/llm 行保持）。
- [x] **`ExecutionListPage.vue`** / 筛选：列表 query 使用 **`state`**、**`keyword`**（勿直接抄 5176 的 `cursor`/`intentContains` 除非做适配层）。
- [x] **（可选）** `summarizeTradingPromptBinding` 扩展为一行多槽（system/safety/strategy）或沿用详情 JSON `<details>`。

### `/pm` 可选

- OpenAPI 片段：`product-doc/specs/openapi/components/prompt-management-schemas.yaml` **`ResolvedPromptBinding`**；`observability-schemas.yaml` **`AgentPromptBindingResolvedEvent`**（已冻结，无需改条文除非 FE 发现缺口）。

### 验收

1. 本地 API **`8080`** + Admin **`5173`** 登录后打开 **`/runtime/executions`**，点进一条 **写路径**（如限价单）执行。
2. 总览 **`resolvedPromptBinding`** JSON 含 **system/safety/trading** 三槽非空（已 seed 的环境）。
3. 时间线 Tab 可见 **`agent.prompt.binding_resolved`** 在 **`execution.dispatched`** 之后、**`agent.skill.spec_read`** 之前。
4. Skill 范围折叠块请求 **`…/skill-scope`** 返回 **`mode=write_skill`** 且 **`skills[0].skillId`** 与场景一致。
5. 读侧场景（如 `read.market.ticker`）**`mode=read_only`**，`skills` 为空数组。

### Refs

- `server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md` §5 / §5.1b
- `server/chainup_agent/application/resolved_prompt_binding.py`
- 产品原型：`product-doc/src/admin` **`http://localhost:5176/runtime/executions`**（`VITE_USE_OBSERVABILITY_API` 可参考字段映射，分页/query 以生产为准）

---

## 2026-05-26 — 技能与工具 · `/ai/tool-registry`（A 类 skill-specs API）

### 背景

服务端已实现 **A 类写技能操作规范** 的 Admin Publish 链（功能包 `2026-05-27--skill-publish-effective`）：列表、生效指针、版本履历、Markdown 正文、**Publish 落库**。  
页面 **`/ai/tool-registry`**（`ai.tool-registry`）的 **「可帮用户下单」Tab + 右侧抽屉主流程** 应接真实 API；**查询类 / 外部检索 / 是否启用开关 / 变更记录** 仍为 **原型本地态**（mock + `localStorage`），**本条目无对应生产 API**，勿向 `/be` 追 Registry 接口除非另开需求。

### 契约

**鉴权**：与其它 Admin 路由一致，`Authorization: Bearer <access_token>`；未登录 **401** `ADMIN_CONSOLE_AUTH_REQUIRED`。

| 页面操作 | Method | Path | 说明 |
|----------|--------|------|------|
| A 类列表 / 顶栏 Runtime 统计 | `GET` | `/api/v1/admin/skill-specs` | Query 可选 **`lifecycle`**（如 `PUBLISHED`）；响应 **`{ items: SkillOperationSpecSummary[] }`** |
| 单技能摘要（可选） | `GET` | `/api/v1/admin/skill-specs/{skillId}` | 生效指针 + 摘要；**404** `PROMPT_SKILL_REF_INVALID` |
| 抽屉 · 版本履历 | `GET` | `/api/v1/admin/skill-specs/{skillId}/versions` | **`{ skillId, items: [{ skillSpecVersion, lifecycle, publishedAt }] }`** |
| 抽屉 · 正文预览 | `GET` | `/api/v1/admin/skill-specs/{skillId}/versions/{skillSpecVersion}` | **`bodyMarkdown`**、**`specDigest`**、**`sourceGitRef`** |
| Publish 到 Runtime | `POST` | `/api/v1/admin/skill-specs/{skillId}/publish` | 见下表 |

**`SkillOperationSpecSummary`（列表项 / 摘要，camelCase）**

| 字段 | 类型 | 说明 |
|------|------|------|
| `skillId` | string | 如 `skill.spot.limit_order` |
| `skillSpecVersion` | string | **当前生效指针** 版本号 |
| `lifecycle` | string | 指针版本状态；**`PUBLISHED`** 表示 Runtime 已发布 |
| `scenarioIds` | string[] | 关联场景（可为空数组） |
| `contractComplete` | boolean | 正文是否满足 contract-complete（§1 等） |
| `specDigest` | string \| null | 正文摘要 |
| `publishedAt` | string \| null | ISO 时间 |

**`POST …/publish` Body**

| 字段 | 必填 | 说明 |
|------|------|------|
| `skillSpecVersion` | 是 | **单调递增**（语义化版本比较），不可 ≤ 已发布最大版 |
| `bodyMarkdown` | 条件 | 全文；若省略则尝试沿用指针版本或 bundle 种子正文 |
| `specDigest` | 否 | 省略则服务端计算 |
| `sourceGitRef` | 否 | 溯源用 |

**Publish 相关错误码**（FastAPI 体含 `code` + `message`）

| code | HTTP | 说明 |
|------|------|------|
| `PROMPT_SKILL_REF_INVALID` | 404 | 未知 `skillId` / 版本不存在 |
| `PROMPT_SKILL_VERSION_ROLLBACK` | 400 | 版本号回退 |
| `PROMPT_SKILL_CONTRACT_INCOMPLETE` | 422 | 正文缺 §1 或未达 contract-complete |
| `VALIDATION_ERROR` | 422 | `skillId` / `skillSpecVersion` 空等 |

**与 Prompt 治理联动（已实现，本页不重复接线）**

- `POST /api/v1/admin/prompt-packs/{id}/publish` 校验 `variableSchema.skillSpecRef` → 须指向 **已 Publish** 的技能版本（**SC-PM-21**）。
- FE 文案：`admin/src/pages/prompts/usePromptPackEditor.ts` · `explainPromptPackApiError`。

### 数据合并约定（A 类表格行）

后端 **仅** 返回规范指针与 Runtime 状态；**不** 返回「用户怎么用 / 实际下单方式 / matrix 状态 / 默认启用」等登记文案。

| 来源 | 字段 |
|------|------|
| 前端 SSOT | `admin/src/entities/tool-registry/skill-registry-catalog.ts`（与 manifest 同序） |
| API overlay | `skillSpecVersion`、`lifecycle`、`contractComplete`、`specDigest`、`publishedAt` |
| 合并函数 | `mergeSkillRegistryWithApi(items)` |

**统计卡建议**

| 卡片 | 计算 |
|------|------|
| 说明文档已就绪 | `publishRequired` 行中 `contractComplete === true` 计数 |
| Runtime 已发布 | `publishRequired` 且 `lifecycle === 'PUBLISHED'` |
| 可下单 · 已启用 | **本地** `localStorage` 开关（非 API） |

### FE 任务清单

**API 客户端（`admin/src/shared/api/admin-skill-specs.ts`）**

- [x] `listSkillOperationSpecs({ lifecycle? })`
- [x] `getSkillOperationSpec(skillId)`（可选；列表行已含指针时可不调）
- [x] `getSkillOperationSpecVersions` / `getSkillOperationSpecVersionBody`
- [x] `publishSkillOperationSpec(skillId, body)`
- [x] `explainSkillSpecApiError` 映射 `PROMPT_SKILL_REF_INVALID` / `PROMPT_SKILL_VERSION_ROLLBACK` / `PROMPT_SKILL_CONTRACT_INCOMPLETE`

**页面 `/ai/tool-registry`**

- [x] 路由 `ai.tool-registry`；旧路径重定向 `/ai/skill-specs`、`/tools/*` 等
- [x] **可帮用户下单** Tab：`listSkillOperationSpecs` + catalog merge + 本地 keyword 筛选
- [x] 行点击 → `SkillOperationDrawer`：`versions` → 选版本 → `bodyMarkdown` → 前端解析 §1～§6 展示
- [x] Publish Modal：`skillSpecVersion` + `bodyMarkdown`（≥200 字且含 `## 1.` 与 FE 校验一致）
- [x] Publish 成功后刷新列表并更新抽屉内指针/正文
- [x] 列表/抽屉 loading、空态、API 错误展示（`AdminPageHeader` error 或 toast）
- [x] **可选**：`explainSkillSpecApiError` 增加 `PROMPT_SKILL_CONTRACT_INCOMPLETE` 友好文案
- [x] **可选**：A 类表格「仅 Runtime 已发布」筛选（客户端 `isRuntimePublished`；列表仍 `GET` 全量以支撑顶栏统计；`listSkillOperationSpecs({ lifecycle: 'PUBLISHED' })` 客户端已支持供其它页复用）

**明确不接 API（保持现状即可）**

- [x] **查询类 / 外部检索** Tab：`entities/tool-registry/tool-registry-mock.ts`
- [x] **是否启用** / **恢复默认开关** / **变更记录**：`entities/tool-registry/tool-registry-storage.ts`（`chainup-admin-tool-registry-demo-v1`）
- 生产化上述能力 → 另需求 **`/api/v1/admin/tools/registry`**（OpenAPI `product-doc/specs/openapi/admin/tool-management.yaml`），**不在本交付**

### `/pm` 可选

- 产品页说明已与原型对齐：`product-doc/specs/requirements/domains/admin/tool-management/config.md`、`page-specs.md` § `ai.tool-registry`。
- 若条文写「生产 Registry API 已上线」需 **`/pm`** 改回「原型本地 Enable」或等 Registry 功能包。

### 验收

```bash
cd server && uv run alembic upgrade head && uv run chainup-agent-api   # :8080
cd admin && npm run dev   # :5173，登录后带 Bearer
```

1. **列表**：≥11 条 A 类技能（迁移种子 `runtime-bundle.json`）；`skill.spot.limit_order` 等 id 存在。
2. **抽屉**：切换版本可加载 `bodyMarkdown`；概览指标与「对话与下单要求」分段有内容（依赖正文含 §1～§6 表）。
3. **Publish**：递增版本如 `1.0.1` 成功；重复低版本返回 **400** `PROMPT_SKILL_VERSION_ROLLBACK`。
4. **Runtime 标签**：Publish 后该行 `lifecycle` 为 **`PUBLISHED`**，顶栏「Runtime 已发布」计数增加。
5. **B/C / 审计**：无网络请求亦可操作；刷新后开关/审计仍来自 localStorage（预期行为）。

### Refs

- 功能包：`handoff/features/2026-05-27--skill-publish-effective/`（`api.openapi.yaml`、`backend/notes.md`）
- 路由实现：`server/chainup_agent/api/routers/admin_skill_specs.py`
- 存储/Publish：`server/chainup_agent/application/skill_operation_spec_store.py`
- 迁移：`server/alembic/versions/0029_skill_operation_spec_publish.py`
- 测试：`server/tests/test_skill_publish_effective.py`
- FE 联调记录：`handoff/features/2026-05-27--skill-publish-effective/frontend/integration.md`
- OpenAPI  live：`http://127.0.0.1:8080/openapi.json`（paths 含 `/api/v1/admin/skill-specs`）
- **未实现（勿联调）**：`GET /api/v1/admin/tools/registry` 等 Tool Management Registry API

---

## 2026-05-25 — P1 运营 · Observability tool/llm + 实例 I02/I04/I05

### 背景

服务端已挂载 **`GET …/observability/executions/{executionId}/tool-calls|llm`**，以及 **`POST/PATCH …/agents/instances`**、**`POST|DELETE …/binding`**。`/observability` 的 **工具调用 / 大模型** Tab 可脱离占位文案接线。

### 契约

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/observability/executions/{executionId}/tool-calls` | **`items[]`**：`toolId`、`toolCallSeq`、`invocationState`、`phase`、`summary` |
| `GET` | `/api/v1/admin/observability/executions/{executionId}/llm` | **`modelId`**、**`calls[]`**（`eventName`、`gatewayModelId`、`outcome`…；无 messages 全文） |
| `POST` | `/api/v1/admin/agents/instances` | **I02** Body **`telegramUserId`**、可选 **`templateId`** / **`exchangeSubAccountUserId`** → **201** |
| `PATCH` | `/api/v1/admin/agents/instances/{instanceId}` | **I05** **`instanceOverrides`**（白名单：`preferredLanguage`、`cooldownPreferenceSec`、`symbolPreference`、`voiceOutputEnabled`） |
| `POST` | `/api/v1/admin/agents/instances/{instanceId}/binding` | **I04** **`subAccountId`** 或 **`exchangeSubAccountUserId`** |
| `DELETE` | `/api/v1/admin/agents/instances/{instanceId}/binding` | **I04** 解绑 API 托管行（保留实例） |

### FE 任务清单

- [x] **`admin-observability.ts`**：`getAdminObservabilityToolCalls` / `getAdminObservabilityLlm`
- [x] **`ObservabilityPage.vue`**：`tab=tool|llm` 时按 **`executionId`**（query）拉取并展示；无 id 时提示先选执行
- [x] **`agent-instances.ts`**：`createAgentInstance` / `patchAgentInstance` / `bindInstanceSubaccount` / `unbindInstanceSubaccount`
- [x] **实例列表/详情**：创建实例表单、**I05** 编辑 **`instanceOverrides`**（表单四白名单键 · **I04** 登记/解绑）

### 验收

- 有时间线数据的 **`executionId`**：tool-calls 至少 1 条（现货写路径）；llm 在开启 narrate 的轮次有 **`calls`**
- 新建实例后 Deeplink 绑定 → 详情 **BOUND**；**DELETE binding** 后 **NONE** 且实例仍在

### Refs

- `server/docs/API_INTEGRATION_GUIDE.md` §4.7a、§4.7
- `server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md`
- `server/tests/test_admin_p1_ops.py`

---

## 2026-05-21 — 提示词治理 · 列表「Prompt 名称」`title`

### 背景

列表列此前用 **`scenarioId` / `promptPackId`** 充当名称，与产品原型 **`MockPromptPack.title`**（如「行情查询」「平台 SYSTEM 内核」）不一致。服务端现按 **场景寄存器 `flow.title`** + **`agent.runtime.*` 固定文案** + **草稿后缀** 解析 **`title`**。

### 契约

| 字段 | 出现位置 | 说明 |
|------|----------|------|
| `title` | **`GET/POST/PATCH` 包摘要与详情**（`PromptPackSummary` / `PromptPackDetail`） | 运营可见展示名；**只读**（Phase1 不落库，不接收 PATCH body） |

**解析规则（摘要）**

- 有 **`scenarioId`** 且在 **`GET /api/v1/agent/scenarios`** 寄存器 → **`flow.title`**（例：`read.market.ticker` →「行情查询」）
- **`agent.runtime.platform_system` / `platform_safety` / `intent_nlu`** → 平台固定中文名
- **`pack_draft_*`** 无场景 →「交易草稿 · {id 前 8 位}」等
- **`lifecycle=DRAFT`** 且标题未含「草稿」→ 追加 **「（草稿）」**

### FE 任务清单

- [x] **`PromptPackSummary` / `PromptPackDetail`** 类型增加 **`title?: string`**
- [x] **`PromptStrategyPage` / `PromptSafetyPage`** 列表「Prompt 名称」列：**优先 `row.title`**，勿再用 `scenarioId ?? promptPackId`
- [x] 编辑器「Prompt 名称」只读框：**`detail.title`**（可保留 scenarioId 作副文案）
- [x] 关键字筛选：本地 **`q`** 同时匹配 **`title`**、`promptPackId`、`scenarioId`

### Refs

- `server/chainup_agent/application/admin_prompt_packs.py` · `resolve_prompt_pack_title`
- `product-doc/specs/requirements/domains/admin/prompt-management/config.md` §3 **`title`**

---

## 2026-05-20 — 提示词治理 · 新建草稿（`/prompts/strategy` · 对齐原型）

### 背景

后端完善 **`POST /api/v1/admin/prompt-packs`**，对齐产品原型 **`/prompts/strategy`**「新建草稿」双模式：**空白草稿** / **从模板复制**（不再依赖浏览器 local-only 草稿）。

### 契约

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/admin/prompt-packs` | **201** 创建 **`DRAFT`** |

**Body（camelCase）**

| 字段 | 必填 | 说明 |
|------|------|------|
| `promptPackType` | 是 | `SYSTEM` / `TRADING` / `ANALYSIS` / `SAFETY`（策略页通常不含 SAFETY） |
| `scenarioId` | **TRADING/ANALYSIS 必填** | 须在 **`GET /api/v1/agent/scenarios`** 寄存器内，否则 **422** **`PROMPT_SCENARIO_INVALID`** |
| `promptPackId` | 否 | 留空则服务端生成 `pack_{scenario}_*` 或 `pack_draft_*` |
| `sourcePromptPackId` | 否 | **从模板复制**：复制源包 `messages` + `variableSchema` 到新 DRAFT；可配合新 `scenarioId` / `promptPackType` 覆盖 |

**空白草稿**：返回带场景说明的 **system 占位正文**（非空字符串），便于编辑器直接改。

**错误码**：`VALIDATION_ERROR`（缺 scenario）、`PROMPT_SCENARIO_INVALID`、`AGENT_PROMPT_PACK_ID_CONFLICT`（409）、`AGENT_PROMPT_PACK_NOT_FOUND`（模板 id 不存在）

**成功后**：跳转 **`/prompts/editor/:promptPackId`** → **`GET/PATCH …/prompt-packs/{id}`** → 可选 **`POST …/publish`**

### FE 任务清单（接力）

- [x] **新建草稿 Modal** 对齐原型两段：**空白草稿** / **从模板复制**（`Segmented`）
- [x] **空白**：`POST` 仅传 `promptPackType` + `scenarioId`（TRADING/ANALYSIS 场景 **Select** 数据源：`GET /api/v1/agent/scenarios`，按 `category`/`readiness` 筛选）
- [x] **模板**：`POST` 带 `sourcePromptPackId`（列表当前页 `promptPackId`）；可选让用户改 `scenarioId` 再创建
- [x] 创建成功 **`router.push('/prompts/editor/' + promptPackId)`** 并刷新列表
- [x] 移除或降级 **local-draft-*** 仅浏览器草稿路径（Admin 无此路径；创建走服务端 **POST**）
- [x] `admin-prompt-packs.ts`：`createPromptPack` 增加可选 **`sourcePromptPackId`**

### 验收

- TRADING 未填 `scenarioId` → **422**
- 从已有包复制 → 新 `promptPackId`，`bodyMarkdown` 含源正文
- 创建后编辑器可 PATCH 并 publish（scenario 在寄存器内）

### Refs

- `server/docs/BACKEND_SPEC.md` §Admin · Prompt Management
- `server/docs/API_INTEGRATION_GUIDE.md` §4.9
- `product-doc/specs/openapi/admin/prompt-management.yaml` · `PromptPackCreateRequest`
- 原型：`product-doc/src/admin` · `PromptCreateDraftModal.tsx` / `PromptStrategyPage.tsx`

---

## 2026-05-20 — Agent 实例删除（I06 · `DELETE …/instances/{instanceId}`）

### 背景

后端落地 **FR-AM-I06**：运营硬删 **`agent_instance`** 时 **同步删除** 同用户的 **`telegram_agent_trading_binding`**（Agent 解绑；交易所子账户不动）。用户可 **重新进入 Deeplink 绑定页** 完成绑定并获得 **新 `instanceId`**。

### 契约

| 方法 | 路径 | 说明 |
|------|------|------|
| `DELETE` | `/api/v1/admin/agents/instances/{instanceId}` | **204** 无 body；**404** **`AGENT_ADMIN_INSTANCE_NOT_FOUND`** |
| | | **422** **`AGENT_ADMIN_INSTANCE_DELETE_BLOCKED`**：`details.openExecutions` / `details.pendingConfirmations`（未终局执行或 Telegram Type-A 待确认） |

### FE 任务清单

- [x] **`admin` API client**：`deleteAgentInstance(instanceId)` → **`DELETE`** 上路径
- [x] **实例列表/详情**：删除按钮 + 二次确认；失败展示 **`message`** / **`code`**
- [x] 删除成功后刷新列表；绑定列表同步刷新（该用户绑定行已清除）

### 验收

- 无在途执行时可删，列表不再出现该 **`instanceId`**；**`GET …/trading-bindings`** **不再**含该 **`telegramUserId`**
- 同用户可再走 Deeplink：**`onboarding/initiate`** → **`bind_trading_api`** → **`POST …/bindings/trading-api`** 得 **新 `instanceId`**
- 存在 **`ACCEPTED`** 执行未 **finalize** 时删除返回 **422**

### Refs

`server/docs/BACKEND_SPEC.md` §Admin · Agent 实例 · **`product-doc/specs/openapi/admin/agent-management.yaml`** **I06**

---

## 2026-05-20 — Telegram · Bot 接入页（原型四段 · `/system/channels/telegram`）

### 背景

**`/fe` 已重构** `TelegramChannelDetailPage.vue`（路由 `system/channels/telegram`），对齐 product-doc 原型 **§1～4**：Bot 基础 / Webhook / 渠道能力（演示）/ 用户体验（演示）。后端新增 **`GET …/telegram/bot`**、**`POST …/telegram/self-test`**。

### 契约

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/channels/telegram/bot` | getMe 摘要；**`tokenConfigured`**、**`secretRefFingerprint`**（非明文 Token）；**`runtimeParams`** / **`configVersion`**（PATCH 落地后回显） |
| `PATCH` | `/api/v1/admin/channels/telegram/bot` | Body **`{ runtimeParams }`**（keys.md §4.2）；可选 **Header `If-Match`** = **`configVersion`** |
| `POST` | `/api/v1/admin/channels/telegram/self-test` | **getMeOk** + **getWebhookInfoOk** + **errorSummary** |
| `GET/POST/DELETE` | `/api/v1/admin/channels/telegram/webhook` | 既有 Webhook 运维 |

### FE 任务清单

- [x] 页面四段布局、**测试连接**、Webhook 表单（URL + Secret）、投递错误提示
- [x] `telegram-channel.ts` API client；`telegramDeliveryHints.ts` 复用
- [x] **§3/§4** 正式写入 **`PATCH …/telegram/bot`**（`runtimeParams` · `telegram-runtime-params.ts`）；**`/be` 已落地**（合并写入 · 可选 **`If-Match`** = **`configVersion`**）

### Refs

`admin-bot-config.md` FR-TG-ADMIN-01～06 · `telegram-channels.yaml`

---

## 2026-05-20 — 运行场景 · 执行流程编排（Phase 2 · `/ai/runtime-orchestration`）

### 背景

后端落地 **FR-AO01/05/06 子集**：14 场景 **执行流程** 登记（**`flowSummary` + `executionSteps[]`**）、场景详情 API、Admin **执行策略** 读接口；运行时在 **`executionId`** 下写入 **`agent.orchestration.step`**；编排预算 **`ORCHESTRATION_BUDGET_EXCEEDED`** 写入前 enforcement。

### 契约（camelCase）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/agent/scenarios` | 列表项增 **`flowSummary`**（优先于 **`summary`** 展示）、**`executionSteps[]`**（`stepKey`/`labelZh`/`order`）、**`closureStatus`** |
| `GET` | `/api/v1/agent/scenarios/{scenarioId}` | 详情：**`flowSummary`**、**`executionSteps`**、**`specRefs`**、**`flowAnchor`**、**`promptBindingHint`**、**`orchestrationRegistryVersion`** |
| `GET` | `/api/v1/admin/orchestration/policy` | 执行策略 Tab 读模型（对齐原型 **`ExecutionPolicyState`**）；**`maxToolCalls`/`maxOrchestrationSteps`** 来自网关预算 |

**执行流程示例**（`read.market.ticker`）：`分析 → 读行情 → 返回结果`；步骤键序：`intent.route` → `access.evaluate` → `read.market` → `summarize.return`。

### FE 任务清单

- [x] **`RuntimeOrchestrationPage`**：列表 **执行流程** 列优先用 **`flowSummary`**（fallback **`summary`**）；详情 Drawer 展示 **`executionSteps[]`** 步骤条。
- [x] **类型/API**：`agent-runtime.ts` 扩展 **`ScenarioListItem`** / 新增 **`getScenarioDetail`**；新建 **`admin-orchestration.ts`** → **`GET …/orchestration/policy`**。
- [x] **`OrchestrationPolicyTab`**：由 sessionStorage mock 改为 **`GET …/admin/orchestration/policy`** 初始加载（保存仍可先本地演示，或 **`PATCH …/admin/ai/defaults`** 仅改预算字段）。

### 验收

- 运行场景页与后端 **14** 条 **`flowSummary`** 一致（如截图「分析 → 读行情 → 返回结果」）。
- 点击场景详情可见 **`executionSteps`** 有序步骤。
- 执行策略 Tab 加载 **`maxToolCalls`**=32（默认）等与 AI 网关 defaults 一致。

### Refs

- `server/docs/BACKEND_SPEC.md` §Agent Runtime · §Admin Orchestration
- `server/docs/API_INTEGRATION_GUIDE.md` §4.3
- `server/tests/test_orchestration_flow_catalog.py`
- `server/chainup_agent/application/orchestration_flow_catalog.py`

---

## 2026-05-20 — 提示词编辑器（`/prompts/editor/:promptPackId`）

### 背景

后端补齐 **提示词治理 · 编辑器** OpenAPI 子集：**fork 新版本线**、**版本履历**、**回滚**、**PATCH If-Match**；详情增加 **`bodyMarkdown`/`rowVersion`/`updatedAt`**。Runtime **SYSTEM** 包 **`LOCKED`** 态纳入生效读（修复发布后拼装 miss）。迁移 **`0022_admin_prompt_pack_version_event`**。

**说明**：原型 mock id **`pp-sys-core`** 对应联调种子 **`pack_platform_system_v1`**（**`agent.runtime.platform_system`**）；**LOCKED** 包须先 **`POST …/fork`** 得新 **DRAFT** 再进编辑器。

### 契约（camelCase）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/prompt-packs/{id}` | 新增 **`bodyMarkdown`**、**`rowVersion`**、**`updatedAt`** |
| `PATCH` | `/api/v1/admin/prompt-packs/{id}` | 可选 **Header `If-Match`** = **`rowVersion`**；冲突 **409** **`AGENT_PROMPT_PACK_VERSION_CONFLICT`** |
| `POST` | `/api/v1/admin/prompt-packs/{id}/fork` | **201** 新 **DRAFT**；Body 可选 **`promptPackId`**；源包 **LOCKED/PUBLISHED/DRAFT** |
| `GET` | `/api/v1/admin/prompt-packs/{id}/versions` | **`items[]`**：`promptPackVersion`、`publishedAt`、`lifecycle`、`event`（**`PUBLISH`/`ROLLBACK`**）、`summary` |
| `POST` | `/api/v1/admin/prompt-packs/{id}/rollback` | Body **`{ promptPackVersion }`**；**`PUBLISHED`/`LOCKED`** 可回滚 |

### FE 任务清单

- [x] **`admin-prompt-packs.ts`**：新增 **`forkPromptPack`**、**`listPromptPackVersions`**、**`rollbackPromptPack`**；**`patchPromptPack`** 支持可选 **`ifMatch`**（取自 **`rowVersion`** 或响应 **Header `ETag`**）。
- [x] **`PromptPackEditorPage`**：侧栏版本历史接 **`GET …/versions`**；启用「从历史版本恢复」→ **`POST …/rollback`**（需确认弹窗）。
- [x] **`PromptStrategyPage`**：对 **LOCKED** 行「编辑」改为 **fork → 跳转新 id 编辑器**（或弹窗指定新 **`promptPackId`**）。
- [x] 类型扩展：**`PromptPackDetail.rowVersion`**、**`updatedAt`**、**`bodyMarkdown`**（可选直接读，仍可用 **`messages`** 转换）。

### 验收

- **`alembic upgrade head`**（含 **`0022`**）。
- **`pack_platform_system_v1`**：**fork** → 编辑 → **publish** → **`LOCKED`**；旧 SYSTEM 同场景 → **`DEPRECATED`**。
- 编辑器 **⌘S** 保存带 **`If-Match`** 时并发 PATCH 返回 **409** 有友好提示。

### Refs

- `server/docs/BACKEND_SPEC.md` §Admin · Prompt Management
- `server/docs/API_INTEGRATION_GUIDE.md` §4.9
- `server/tests/test_admin_prompt_editor.py`
- `admin/src/pages/prompts/PromptPackEditorPage.vue`

---

## 2026-05-20 — 安全防护（`ai.prompt-safety` · `/prompts/safety`）

### 背景

后端已实现 **`/api/v1/admin/prompt-safety/*`** 聚合读接口；**SAFETY Prompt 包** 仍用既有 **`/api/v1/admin/prompt-packs`**（`promptPackType=SAFETY`）创建/编辑/发布。Publish/Patch 新增 **§7.1 越狱用语闸**（**422 `PROMPT_SAFETY_VIOLATION`**）。拦截流水来自 **Publish 阻断日志** + **执行时间线**（确认规则拦截、限价偏离等）。

### 契约（camelCase）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/prompt-safety/overview` | **`safetyPhraseBlocklistRevision`**、**`platformSafetyPack`**、**`safetyPromptPackCount`**、**`publishedSafetyPackCount`**、**`enabledConfirmationRulesCount`**、**`globalAgentSwitchOn`**、**`opsSuspended`** |
| `GET` | `/api/v1/admin/prompt-safety/blocklist` | **`rules[]`**（`ruleId`/`phrase`/`matchMode`）、**`safetyPhraseScanScopeDefault`** |
| `GET` | `/api/v1/admin/prompt-safety/prompt-packs` | 同 **`GET …/prompt-packs?promptPackType=SAFETY`** |
| `GET` | `/api/v1/admin/prompt-safety/runtime-governance` | **`items[]`**：`name`、`riskLevelLabel`、`autoExecSummary`、`confirmSummary`、`breakerSummary`、`hrefKind`（`confirmation`/`policy`/`routing`） |
| `GET` | `/api/v1/admin/prompt-safety/tool-policies` | **`items[]`**：`toolPattern`、`policy`、`enforcementMode`、`note` |
| `GET` | `/api/v1/admin/prompt-safety/session-policy` | **`items[]`**：`label`、`summary`、`status` |
| `GET` | `/api/v1/admin/prompt-safety/intercepts` | Query **`category`**、**`limit`**、**`offset`**；**`items[]`**：`id`、`ts`、`category`、`scenarioLabel`、`kindLabel`、`reason`、`subject`、`executionId`、`matchedRuleId` |

**SAFETY 包 CRUD（沿用 §4.9）**

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/admin/prompt-packs` | Body **`promptPackType: "SAFETY"`**；可选 **`scenarioId`**（平台护栏 **`agent.runtime.platform_safety`**） |
| `PATCH` | `/api/v1/admin/prompt-packs/{id}` | Body **`messages[]`**；命中用语闸 → **422 `PROMPT_SAFETY_VIOLATION`** |
| `POST` | `/api/v1/admin/prompt-packs/{id}/publish` | **SAFETY** → **`PUBLISHED`**；同 **`scenarioId`** 旧版 → **`DEPRECATED`** |

### FE 任务清单

- [x] 新建 **`admin/src/shared/api/admin-prompt-safety.ts`**（上表聚合 API）。
- [x] 页面 **`/prompts/safety`**（参照原型 `http://localhost:5176/prompts/safety`）：Tab **安全策略** / **拦截记录**。
- [x] 子 Tab：**Prompt 安全** → 接 **`/prompt-safety/prompt-packs`** + 详情 Drawer（可复用策略页 **`PromptPackDetailDrawer`** 模式）；新建 SAFETY 草稿 → **`POST …/prompt-packs`**。
- [x] 子 Tab：**Runtime 安全** → **`/runtime-governance`**；链接 **`/ai/confirmation-rules`**、编排页。
- [x] 子 Tab：**Tool 安全** / **Session 安全** → 对应 GET；Session 为说明性条目。
- [x] **拦截记录** Tab → **`/intercepts`** 分页表格。
- [x] 移除 **`safetyCenterMock`** / sessionStorage 演示数据；**`overview`** 展示用语闸 **revision**（`admin/` 无 mock）。

### 验收

- 联调库 **`alembic upgrade head`**（含 **`0021`**）。
- **`GET /prompt-safety/overview`** 可见 **`platformSafetyPack.promptPackId=pack_platform_safety_v1`**（迁移 **0013** 后）。
- PATCH 含 **`ignore previous instructions`** → **422 `PROMPT_SAFETY_VIOLATION`**；Publish 同类失败出现在 **`/intercepts?category=prompt`**。

### Refs

- `server/docs/BACKEND_SPEC.md` §Admin · Prompt Safety / §Prompt Management
- `server/docs/API_INTEGRATION_GUIDE.md` §4.11
- `server/chainup_agent/application/prompt_safety_phrase_validation.py`
- `product-doc/src/admin/src/pages/prompt/PromptSafetyPage.tsx`

---

## 2026-05-20 — 人工确认规则（`ai.confirmation-rules`）

### 背景

后端已实现 **`/api/v1/admin/confirmation-rules`** CRUD + 启用切换 + 重置；内置 6 条规则（代码目录，只读）+ 自定义规则（DB）；Telegram 现货闪兑/限价 Type-A 前已接入规则评估（二次确认前缀、禁止自动执行拦截）。

### 契约（camelCase）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/confirmation-rules` | **`items[]`**：`id`、`title`、`summary`、`riskLevel`、`triggerConditions[]`（`fieldKey`/`operator`/`value`）、`scenarios[]`、`action`、`defaultEnabled`、`enabled`、`isBuiltin`；**`total`**、**`enabledCount`** |
| `POST` | `/api/v1/admin/confirmation-rules` | **201** 创建自定义（Body 无 `id`，服务端生成 `custom-{uuid}`） |
| `GET` | `/api/v1/admin/confirmation-rules/{ruleId}` | 详情 |
| `PUT` | `/api/v1/admin/confirmation-rules/{ruleId}` | 仅自定义；内置 **409** `AGENT_ADMIN_CONFIRMATION_RULE_BUILTIN_READONLY` |
| `DELETE` | `/api/v1/admin/confirmation-rules/{ruleId}` | **204**；内置 **409** |
| `PATCH` | `/api/v1/admin/confirmation-rules/{ruleId}/enabled` | Body **`{ "enabled": boolean }`** |
| `POST` | `/api/v1/admin/confirmation-rules/reset` | 恢复演示自定义样例 + 内置默认启用态 |

**枚举**（与原型 `confirmationRulesCatalog.ts` 一致）：

- **`riskLevel`**：`low` \| `medium` \| `high`
- **`action`**：`force_confirm` \| `second_confirm` \| `otp_confirm` \| `block_auto_execute`
- **`scenarios`**：`spot` \| `futures` \| `convert` \| `wealth` \| `leverage` \| `transfer` \| `conditional_order`
- **`triggerConditions[].fieldKey`**：`nominal_usdt` \| `leverage` \| `operation_scope` \| `custom`
- **`triggerConditions[].operator`**：`gt` \| `gte` \| `lt` \| `lte` \| `eq` \| `contains`

**内置规则 id**（不可编辑/删）：`hitl-trade-fund-write`、`hitl-large-notional`、`hitl-high-leverage`、`hitl-conditional-auto`、`hitl-wealth`、`hitl-close-all`

### FE 任务清单

- [x] 新建 **`admin/src/shared/api/admin-confirmation-rules.ts`**（ky client，对齐上表）。
- [x] 新建类型 **`ConfirmationRule*`**（可对照 product-doc `confirmationRulesCatalog.ts`）。
- [x] 路由 **`/ai/confirmation-rules`**、**`/ai/confirmation-rules/new`**、**`/ai/confirmation-rules/edit/:ruleId`** 页面（参照原型 `http://localhost:5176/ai/confirmation-rules`）。
- [x] 列表：筛选（风险等级、关键词）、启用 Switch（关闭 `force_confirm`/`block_auto_execute` 时弹强警示，与原型一致）。
- [x] 编辑器：新建/编辑自定义规则；内置仅查看 + 启用切换。
- [x] 「恢复默认」→ **`POST …/reset`**。
- [x] 移除 sessionStorage mock（`ConfirmationRulesContext` 等价逻辑改 API；`admin/` 无该 mock，已直连 API）。

### 验收

- 联调库 **`alembic upgrade head`**（含 **`0020`**）后，列表 ≥ 9 条（6 内置 + 3 演示自定义）。
- 切换 **`custom-demo-flash-convert`** 启用/禁用后刷新仍持久化。
- 关闭内置 **`hitl-large-notional`** 后，Telegram 大额闪兑不再出现二次确认前缀（可选联调）。

### Refs

- `server/docs/BACKEND_SPEC.md` §Admin · Confirmation rules
- `server/docs/API_INTEGRATION_GUIDE.md` §4.10
- `server/chainup_agent/domain/confirmation_rules_catalog.py`
- `product-doc/src/admin/src/pages/governance/confirmation/`（原型 UI）

---

## 2026-05-20 — Prompt 包 / 平台场景 ID 去 `phase1` 段

### 背景

后端种子与存量库已统一 **`prompt_pack_id`**、平台 **`scenario_id`**，去掉 `_phase1_` / `phase1_` 阶段标记；新迁移 **`0019_remove_phase1_prompt_identifiers`**。

### 契约（Admin 提示 / 筛选文案）

| 旧 | 新 |
|----|-----|
| `agent.runtime.phase1_platform_system` | `agent.runtime.platform_system` |
| `agent.runtime.phase1_platform_safety` | `agent.runtime.platform_safety` |
| `pack_trading_chat_faq_phase1_v1` | `pack_trading_chat_faq_v1` |
| `pack_phase1_platform_system_v1` | `pack_platform_system_v1` |
| （其它 TRADING 包同理：`*_phase1_v1` → `*_v1`） | |

绑定模板默认：**`tmpl_agent_default`**（原 **`tmpl_phase1_default`**）。

### FE 任务清单

- [x] **`admin/src/pages/prompts/PromptStrategyPage.vue`**：平台场景下拉改为上表 **`scenarioId`**。
- [x] 若页面/文档硬编码旧 **`promptPackId`**，按上表替换（列表 API 返回新 id）。

### 验收

- 运营后台 Prompt 策略页可选 **`agent.runtime.platform_system`** / **`platform_safety`** 且无 404。
- 已发布包在列表中显示新 **`promptPackId`**（联调库须 **`alembic upgrade head`** 含 **0019**）。

### Refs

- `server/alembic/versions/0019_remove_phase1_prompt_identifiers.py`
- `server/docs/BACKEND_SPEC.md` §8 Prompt Assembly

---

## 2026-05-20 — Admin AI：catalog **`modelId` 含 `/`** · Query **`modelId`**（GET/PATCH/DELETE）

### 背景

**`GET|PATCH|DELETE …/models/{modelId}`** 在 **`model_id` 含 `/`**（如 **`deepseek-ai/DeepSeek-V4-Flash`**）时，须经路径编码 **`%2F`**。**部分网关/反向代理会破坏该编码**，表现为 **路由 404**（控制台切换「启用/禁用」等设备命中 **PATCH**）。

### 契约

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/ai/models` | Query **`modelId`**（单列）：`**items`** 仅一项；与 **`providerId` 勿同送**→ **422** |
| `PATCH` | `/api/v1/admin/ai/models` | Query **`modelId`** + Body 同原 **`PATCH …/models/{id}`** |
| `DELETE` | `/api/v1/admin/ai/models` | Query **`modelId`** |

路径形参版 **保留**，无 `/` 的 id 仍可沿用。

### FE 任务清单

- [x] **`admin/src/shared/api/admin-ai-settings.ts`**：**`getAiModel` / `patchAiModel` / `deleteAiModel`** 已改为 **`…/models?modelId=`**（ky **`searchParams`**）。

### `/pm`

- OpenAPI **`admin/ai-settings.yaml`** 可增补 Query 别名说明（本节以 **`BACKEND_SPEC`** 为先）。

### Refs

- **`server/docs/BACKEND_SPEC.md`** §Admin · AI Settings、`server/tests/test_api.py` **`test_admin_ai_model_slash_id_get_patch_delete_via_query`**

---

## 2026-05-19 — AI Settings：**厂商→模型目录**、`apiModel`、网关策略 **`modelId` 校验**

### 背景

策略（**`GET|PATCH /api/v1/admin/ai/defaults`**）里 **`scenarioChatModel` / `scenarioTradingModel` / `scenarioRiskModel` / `defaultModelId` / `defaultInferenceModel` / `fallbackModel`** 引用的是 **`admin_ai_model.model_id`**（**全局唯一的 catalog id**），不是「控制台下拉展示串」本身。同名上游 **`model`** 串在不同厂商可同时存在：**各厂商各建一条目录行**，**`modelId` 必须互不重复**；可选 **`apiModel`** 填入对端 HTTP JSON **`"model"`** 字段的值，**不传则等价于 **`modelId`**。**`PATCH …/defaults`** 若上述字段指向未注册的 **`modelId`** → **422 **`AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG`****。

### 契约（camelCase）

| 变更 | 说明 |
|------|------|
| **DB** | 迁移 **`0017_admin_ai_model_api_model`**：**`admin_ai_model.api_model`**（可空）。 |
| **`POST/PATCH …/models`** | Body / 摘要增加可选 **`apiModel`**。 |
| **`PATCH …/defaults`** | 合并后与内置默认合并视图一并校验 catalog；**422 **`AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG`**，`details.missing`** 列 **`field`、`modelId`**。 |
| **`GET …/models` 等读目录** | DB **未跑迁移 `0017`**、缺 **`api_model`** 列时：**503 **`AGENT_DB_SCHEMA_OUT_OF_DATE`**（含 **`details.migrationHint`**）；须 **`alembic upgrade head`**。 |
| **运行时观测**（若消费 LLM meta） | **`gatewayModelId`**（catalog）与 **`gatewayUpstreamModel`**（线 id = **`apiModel` ?? `modelId`**）。 |

### FE 任务清单

- [x] **推理与路由页**：下拉 **option value 必须使用 `modelId`（catalog）**，label 组合 **`displayName`/厂商名**，避免只靠上游名导致二义性（与截图中「同名不同厂商」一致）。
- [x] **厂商→模型表单**：可选 **`apiModel`**；占位/说明：**留空则用 `modelId` 作为对端 **`model`****。
- [x] **`agent-runtime` / OpenAPI 类型**：`**`AdminAiModelSummary` / create·patch`** 增补 **`apiModel`**；`**`PATCH …/defaults`**** 文档化错误码 **`AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG`**。
- [x] **`GET …/models` /详情**：展示 **`apiModel`**（可与 **`modelId` 分列**）。

### `/pm`

- 产品 **`product-doc/specs/openapi/admin/ai-settings.yaml`** 可按需增补 **`apiModel`** 与网关错误码条目（本节以 **`server/docs/BACKEND_SPEC.md`** §Admin · AI Settings 为先）。

### 验收

1. 控制台 **PATCH defaults** 将 **`scenarioChatModel`** 改为不存在的 id → **422**，**`code`** 如上表。  
2. 两条 Provider、两条 **`modelId`**（不同），**相同的 **`apiModel`****，分别保存为策略字段 → LLM 请求体 **`model`** 为 **`apiModel`**，**Bearer/baseUrl** 随 Provider 分流。

### Refs

- **`server/docs/BACKEND_SPEC.md`** §**Admin · AI Settings**、`server/docs/API_INTEGRATION_GUIDE.md` §**4.8**
- **`server/alembic/versions/0017_admin_ai_model_api_model.py`**

---

## 2026-05-23 — Admin：**`POST /api/auth/register`**（database 控制台账号）

### 背景

运营后台除 **`POST /api/auth/login`** 外新增 **`POST /api/auth/register`**：在 **`CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE=database`** 且 **`alembic upgrade head`** 后，将管理员写入 **`admin_console_user`**（bcrypt）；**首张**管理员可在**空库**时直接注册（**`password` ≥ 8**）；之后再注册需服务端 **`CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION=true`** 或继续使用 CLI **`chainup-agent-seed-admin`**。**`env`** 模式下注册返回 **503**，仍用 **`ADMIN_PANEL_USERNAME` / `PASSWORD`** 登录。

### 契约

| 方法 | 路径 | Body | 说明 |
|------|------|------|------|
| `POST` | `/api/auth/register` | **`username`**、**`password`**（≥8） | **`200`** 体同 **`/api/auth/login`**：`access_token`、`token_type`、`username`。**`503`** **`ADMIN_CONSOLE_REGISTRATION_REQUIRES_DATABASE_AUTH`**；**`403`** **`ADMIN_CONSOLE_REGISTRATION_DISABLED`**；**`409`** **`ADMIN_CONSOLE_USERNAME_ALREADY_EXISTS`**；口令过短 **422 `VALIDATION_ERROR`** |
| `POST` | `/api/auth/login` | （不变） | 与 **`BACKEND_SPEC`** §**3.1** 一致 |

生产建议配置 **`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`**（≥16）：登录/注册下发的 **`access_token`** 均为 JWT，`/api/v1/admin/*` 须 **`Authorization: Bearer`**。

### FE 任务清单

- [x] **`/login` 路由**：表单提交 **`POST /api/auth/register`**（注册）与 **`POST /api/auth/login`**（登录）；成功后存 **`access_token`**，后续请求带 Bearer（沿用现有 axios/fetch 拦截器）。
- [x] （可选）首访引导：仅在 **`database`** 模式下展示「注册」，或区分「首张管理员注册」文案；服务端错误 **`code`** 如上表可做 i18n/提示。
- [x] **`agent-runtime`/OpenAPI**：若手写 client，补足 **`/api/auth/register`** 调用与 **`AdminLoginResponse`** 复用（见 **`admin/src/shared/api/admin-auth.ts`**）。

### `/pm`

- 控制台登录/注册产品条文若以 **`product-doc/specs/design/api.md`** 为准，可按需增补 **`/api/auth/register`** 条目（本条以 **`BACKEND_SPEC`** / **`API_INTEGRATION_GUIDE`** §**3.6** 为先）。

### 验收

1. **`server`**：`.env` 设 **`ADMIN_CONSOLE_AUTH_MODE=database`**，迁移已跑，**`JWT_SECRET`** 非空。  
2. **空库**：**`POST /api/auth/register`** → **200**；再 **GET `/api/v1/admin/…`** 带头成功。  
3. **第二张账号**：不配 **`OPEN_REGISTRATION`** → 注册 **403**；设为 **`true`** → **200**。  
4. **`AUTH_MODE=env`**：`register` → **503**；`login` 仍可用 env 账号。

### Refs

- **`server/docs/BACKEND_SPEC.md`** §**3.1**、§**6.1**、配置表 **`ADMIN_CONSOLE_OPEN_REGISTRATION`**
- **`server/docs/API_INTEGRATION_GUIDE.md`** §**3.6**、§**4.6**

---

## 2026-05-18 — 现货 **`GET …/open-orders`** · **`POST …/cancel`**（Coobit **`/sapi/v2/openOrders`** · **`/sapi/v2/cancel`**）

### 背景

后端对接 GitBook Spot **Current Open Orders** / **Cancel Order**：绑定用户可调 **`GET /api/v1/agent/trade/spot/open-orders`**（可选 **`symbol`**、**`limit`**）与 **`POST /api/v1/agent/trade/spot/cancel`**（**`orderId`** 或 **`newClientOrderId`**）。**`routing/execute`** / **`GET /scenarios`** 增加 **`trade.spot.open_orders`**、**`trade.spot.cancel_order`**；意图关键词 **撤单 / 当前委托** 等。

### 契约（camelCase）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/agent/trade/spot/open-orders` | Query **`userId`**，可选 **`symbol`**、**`limit`**（1～1000）；**200** **`scenarioId`**、`orders[]`、`symbol`、`symbolOrder` |
| `POST` | `/api/v1/agent/trade/spot/cancel` | Body **`userId`**、**`symbol`**、**`orderId`** 或 **`newClientOrderId`**（至少其一）；**200** **`scenarioId`**=`trade.spot.cancel_order` |

常见错误码：**403** **`AGENT_SUBACCOUNT_REQUIRED`**；**400** **`AGENT_SPOT_ORDER_REJECTED`**；撤单 **502** **`AGENT_SPOT_ORDER_FAILED`** / **`AGENT_OPENAPI_PROBE_FAILED`**；当前委托 **502** **`AGENT_SPOT_OPEN_ORDERS_FAILED`** / **`AGENT_OPENAPI_PROBE_FAILED`**；**422** **`VALIDATION_ERROR`**。

### FE 任务清单

- [x] **Agent / trading API client**（如 `agent-runtime.ts` / OpenAPI 生成类型）：补齐上述路径与请求/响应类型。
- [x] **Observability**：时间线 **`stepKind`** **`cancel_order`**（撤单）；若控制台枚举硬编码 **`submit_order`** / **`quote`** 等，按需扩展展示 **`cancel_order`**。
- [x] （可选）运营场景 **`trade.spot.open_orders`** / **`trade.spot.cancel_order`** 文案或过滤器与 **`GET /scenarios`** 对齐。

### 运维联调（Admin）

- **`/system/spot-open-orders`**：`GET …/open-orders`、`POST …/cancel`（侧栏 · **系统与配置**；布局对齐 **`/system/spot-limit-order`** / 原型系统联调）。

### Refs

- **`server/docs/BACKEND_SPEC.md`** §**3.1**（现货小节）、changelog **2026-05-18**
- **`server/docs/API_INTEGRATION_GUIDE.md`** §**4.3c**
- **`server/tests/test_api.py`**：**`test_spot_open_orders_*`**、**`test_spot_cancel_order_*`**、**`test_build_coobit_signed_get_request_path_sorts_query`**

---

## 2026-05-21 — **`read.account.balance` / `wealth.holdings_read`** 可选 Telegram LLM · 迁移 **0016**

### 背景

与 **`read.market.ticker` / `depth` / `trades`** 同构：**`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_ACCOUNT_BALANCE`**、**`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_WEALTH_HOLDINGS_READ`** 为 **true** 且对应 **托管只读成功**后追加 **一轮** **`invoke_llm_chat_for_telegram`**（**`runtime_context.exchangeReadPreview`**）。时间线：**`llm.read.account.balance`**（**`read_account_balance_llm`**）、**`llm.wealth.holdings_read`**（**`wealth_holdings_read_llm`**）。**迁移 `0016_read_account_balance_wealth_trading_prompt_seed`**。

### 契约（Prompt 包 id）

| **`promptPackId`** | **`scenarioId`** |
|--------------------|------------------|
| **`pack_trading_read_account_balance_phase1_v1`** | **`read.account.balance`** |
| **`pack_trading_wealth_holdings_read_phase1_v1`** | **`wealth.holdings_read`** |

### FE 任务清单（与行情条目一致粒度）

- [x] Prompt：**`scenarioId`** 过滤器可检索上表两 **TRADING** 包。
- [x] Observability：时间线事件 **`llm.read.account.balance`** / **`llm.wealth.holdings_read`**，**`stepKind`** **`read_account_balance_llm`** / **`wealth_holdings_read_llm`**（若控制台硬编码枚举则扩展）。

### Refs

- **`server/docs/BACKEND_SPEC.md`** §**3.1**、env 表、§**11**
- **`server/tests/test_api.py`**：**`test_telegram_read_account_balance_llm_narration_success`**、**`test_telegram_read_account_balance_llm_timeline_event`**、**`test_telegram_wealth_holdings_read_llm_timeline_event`**、**`test_telegram_wealth_holdings_read_llm_narration_success`**

---

## 2026-05-18 — **`read.market.depth` / `read.market.trades`** 可选 Telegram LLM · 迁移 **0015**

### 背景

与 **`read.market.ticker`**（**① `0014`/`NARRATE_TICKER`**）同构：**`telegram_llm_narrate_read_market_depth`**、**`telegram_llm_narrate_read_market_trades`**（**`CHAINUP_AGENT_TELEGRAM_LLM_*`**）为 **true** 且对应只读 **成功**后，追加 **一轮** **`invoke_llm_chat_for_telegram`**（**`runtime_context.exchangeReadPreview`**）。时间线：**`llm.read.market.depth`**（**`read_market_depth_llm`**）、**`llm.read.market.trades`**（**`read_market_trades_llm`**）。**迁移 `0015_read_market_depth_trades_trading_prompt_seed`**：**`pack_trading_read_market_depth_phase1_v1`** · **`pack_trading_read_market_trades_phase1_v1`**。

### 契约（Prompt 包 id）

| **`promptPackId`** | **`scenarioId`** |
|--------------------|------------------|
| **`pack_trading_read_market_depth_phase1_v1`** | **`read.market.depth`** |
| **`pack_trading_read_market_trades_phase1_v1`** | **`read.market.trades`** |

### FE 任务清单（与 ticker 条目一致粒度）

- [x] Prompt：**`scenarioId`** 过滤器可检索 **`read.market.depth`** / **`read.market.trades`** 的 TRADING 包（上表 **`promptPackId`**）。
- [x] Observability：**`llm.read.market.depth`**、**`llm.read.market.trades`** / **`read_market_depth_llm`** / **`read_market_trades_llm`**（若控制台枚举展示）。

### Refs

- **`server/docs/BACKEND_SPEC.md`** §**3.1**、env 表、§**11**；**`PHASE1_ACCEPTANCE.md`** **AC-00a**
- **`server/tests/test_api.py`**：**`test_telegram_read_market_depth_llm_narration_success`**、**`test_telegram_read_market_trades_llm_timeline_event`**

---

## 2026-05-18 — Telegram：**`read.market.ticker`** 可选 LLM 叙述 · Prompt 迁移 **0014**

### 背景

Phase1：**`telegram_llm_narrate_read_market_ticker`**（**`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER`**，默认 **false**）为 **true** 且 **`read.market.ticker`** **只读成功**后，追加 **一轮** **`invoke_llm_chat_for_telegram`**，**Prompt Assembly** 与 **`chat.faq`** 同链；**`runtime_context`** 含 **`exchangeReadPreview`**。**失败**仍为确定性 ticker 摘要。新增迁移 **`0014_read_market_ticker_trading_prompt_seed`**：**`prompt_pack_id`** **`pack_trading_read_market_ticker_phase1_v1`** · **`scenarioId`** **`read.market.ticker`** · **`TRADING`** · **`PUBLISHED`**。**可观测**：**`agent_execution_event`** **`llm.read.market.ticker`**（**`stepKind`**=`read_market_ticker_llm`）。

### 契约（运营台 / Prompt 控制台）

| 字段 | 说明 |
|------|------|
| **`scenarioId`** | **`read.market.ticker`**（与 **`read.market.*`** 路由键一致） |
| **`promptPackId`** | **`pack_trading_read_market_ticker_phase1_v1`** |

### FE 任务清单

- [x] Prompt 列表/过滤器：可按 **`scenarioId`**=`read.market.ticker` 检索 **TRADING** 包 **`pack_trading_read_market_ticker_phase1_v1`**。
- [x] Observability Timeline：如需展示新开事件名，增补 **`llm.read.market.ticker`** / **`read_market_ticker_llm`**（服务端已写入；控制台若硬编码枚举需扩展）。

### 验收

- 跑 **`alembic upgrade head`** 后控制台可见上述包；服务端单测：**`server/tests/test_api.py`**（**`test_telegram_webhook_read_market_ticker_llm_*`**、**`test_telegram_read_market_ticker_llm_timeline_event`**）。

### Refs

- **`server/docs/BACKEND_SPEC.md`** §**3.1**、env 表、§**11**（**2026-05-18**）
- **`server/docs/API_INTEGRATION_GUIDE.md`** §**4.2a** revision **2026-05-18**
- **`server/docs/PHASE1_ACCEPTANCE.md`** **AC-00a**（**`0014`**）

---

## 2026-05-19 — Phase1 Prompt Assembly 种子包（runtime-injection §1）

### 背景

后端实现 **`chat.faq`** / Intent NLU 的 **拼装顺序**（平台 **SYSTEM → SAFETY → 场景 TRADING / NLU → Few-shot → Runtime Context → Tool JSON Schema SSOT → User**）。联调库执行 **`alembic upgrade head`** 后写入三包 **`PUBLISHED`** 草稿（迁移 **`0013_phase1_prompt_assembly_seed`**）。

### 契约（scenarioId · 仅供 Prompt 管理与 observability 对齐）

| `promptPackType` | `scenarioId`（冻结键） |
|------------------|-------------------------|
| **SYSTEM** | **`agent.runtime.phase1_platform_system`** |
| **SAFETY** | **`agent.runtime.phase1_platform_safety`** |
| **TRADING** | **`chat.faq`** |

### FE 任务清单

- [x] Prompt 控制台（若已有列表按 **`scenarioId`** 过滤）：支持检索/展示上述三包；编辑 **`messages`** 仍走既有 **PATCH**（留意 **`variableSchema`** 非空时的占位符校验）。

### LLM 拼装允许列表（Observability / 控制台）

- **`GET /api/v1/agent/scenarios`**：**`chat.faq`** 的 **`readiness`** 为 **`ready`**（Telegram **`ROUTE_CHAT_FAQ`** + Prompt Assembly 已落地）。
- Phase1 **`scenarioId`** 走 LLM TRADING 拼装入口的**代码允许列表**为 **`PHASE1_TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`**（**`chat.faq`**、**`read.market.ticker`**、**`read.market.depth`**、**`read.market.trades`**）；扩展场景由 **`/be`** 增量放行（须 **`PUBLISHED` TRADING** 包 + 迁移）。

### Telegram 用户可见话术

- **`CHAINUP_AGENT_TELEGRAM_INTENT_PREVIEW_IN_REPLY`**：**默认 false**——用户侧**不**再附带「（编排预览）粗略意图 …」联调行；需要时在运行环境设为 **`true`**。

### Refs

- **`server/docs/BACKEND_SPEC.md`** §**11**（修订 **2026-05-19**）、**`PHASE1_ACCEPTANCE.md`** §**8** **AC-09a～e**

---

## 2026-05-18 — 门禁 `EligibilityEnvelope.requiresMainSite`（AC-09l · Phase1）

### 背景

**`POST /api/v1/agent/access/evaluate`** 响应可选 **`requiresMainSite`**（camelCase）：提示客户端是否应将用户导向 **主站/H5 绑定链路**。

### 契约

- **`true`**：**`allowed=false`** 且 **`AGENT_SUBACCOUNT_REQUIRED`**（未绑定且无放行）。
- **`false`**：**`allowed=true`**（**Phase1 env 放行名单**会话 **或** **DB **`bindingVerified=true`**）。
- **`null`/省略**：全局关闸 / 运维暂停 / 封禁 / 灰度放行等其它阻断语义（与 **`BACKEND_SPEC`** §**3** 对齐）。

### FE 任务清单

- [x] 若控制台或联调面板消费 **`evaluate`**：**TypeScript`/OpenAPI` 模型**增补 **`requiresMainSite?: boolean | null`**；可选展示徽章或 Tooltip（不改变既有 **`allowed`** 行为）。

### 验收

- 见 **`server/tests/test_api.py`**：**`requiresMainSite`** 与 **`AGENT_SUBACCOUNT_REQUIRED`/allowlist/绑定验证**断言。

### Refs

- **`server/docs/BACKEND_SPEC.md`** §**3**（**`POST …/access/evaluate`**）、**`PHASE1_ACCEPTANCE.md`** §**8** **AC-09l**

---

## 2026-05-19 — Prompt 包：`variableSchema`（AC-09f 部分）

### 背景

**`admin_prompt_pack`** 增加 **`variable_schema_json`**。**`PATCH /api/v1/admin/prompt-packs/{promptPackId}`** 可单独或同时更新 **`messages`** / **`variableSchema`**（**至少传其一**）。当 **`variableSchema`** 为 **非空 JSON 对象** 时，正文 **`{{…}}`** 占位符须在 **`variableSchema` 键名 ∪ 平台内置白名单**（见 **`BACKEND_SPEC`**），否则 **422** **`PROMPT_VALIDATION_FAILED`**。未配置或非空 schema 时仍只跑原有 **Secret denylist**（兼容旧包）。

### 契约

- **详情 / effective**：**`GET …/admin/prompt-packs/{id}`**、**`GET …/internal/prompts/effective`** 增加可选 **`variableSchema`**（对象，可能为 **`null`**）。
- **PATCH Body**：**`messages`** 可选；**`variableSchema`** 可选；二者不可同时缺省。

### FE 任务清单

- [x] Prompt 包编辑页：**`variableSchema`** JSON 编辑区（或可折叠 **「允许的占位符」**）；保存走现有 **PATCH**。
- [x] 展示 **平台白名单键** 只读提示（**`effective_locale`、`scenario_id`、`prompt_pack_version`…** — 文案以后端 **`BACKEND_SPEC`** 为准）。

### Refs

- `server/docs/BACKEND_SPEC.md` §3.4 修订 **2026-05-19**、`server/docs/PHASE1_ACCEPTANCE.md` §8 **AC-09f**

---

## 2026-05-18 — 协查 Timeline：Telegram `prompt.snapshot` / `llm.chat.faq`

### 背景

已绑定 Telegram 走 **`ROUTE_CHAT_FAQ`** 时，**`GET …/observability/executions/{executionId}/timeline`** 除既有路由/交易事件外，会多两行：**`prompt.snapshot`**（意图 NLU 包 **`agent.runtime.intent_nlu`**）与 **`llm.chat.faq`**（闲聊网关调用 + **`chat.faq`** 有效包快照）。

### 契约

- **`eventName`**：`prompt.snapshot` \| `llm.chat.faq`（其余不变）。
- **`summary.stepKind`**：`intent_nlu` \| `chat_faq`；**`summary.outcome`**：`llm.chat.faq` 上为 **`success`** / **`failure`**（**`info`** 见 **`prompt.snapshot`**）。
- **`summary`** 含 **`promptPackVersion`**、**`resolvedPromptBinding`**（与 effective 同源，可无包则为 **`null`**）、**`gatewayModelId`** / **`gatewayProviderId`** / **`useArkProtocol`**（闲聊路径，网关已解析时）。

### FE 任务清单

- [x] 时间线 UI：识别上述 **`eventName`**，折叠展示 **`summary`**（避免长 JSON 占屏）。

### 验收

- 复现：`test_api.py` **`test_telegram_bound_chat_faq_timeline_includes_prompt_and_llm_events`** 覆盖 admin timeline 断言。

### Refs

- `server/docs/BACKEND_SPEC.md`（修订表 **2026-05-18**）、`server/docs/PHASE1_ACCEPTANCE.md` §8 **AC-09k**

---

## 2026-05-18 — 执行观测：`promptPackVersion` / `resolvedPromptBinding` + 意图 `effectiveLocale`

### 背景

后端在 **`agent_execution`** 增加 **`prompt_pack_version`**、**`resolved_prompt_binding`**（与 **`GET /api/v1/internal/prompts/effective`** 同源快照）；**`POST /api/v1/agent/execution/accept`** 在提供 **`scenarioId`** 且未手填时可自动写入。**`POST /api/v1/agent/intent/recognize`** 响应增加 **`effectiveLocale`**（zh-Hans / zh-Hant / en）。

### 契约

- **Admin**：**`GET /api/v1/admin/observability/executions`**、**`GET …/{executionId}`** 的 **`items[]` / 详情** 含可选 **`promptPackVersion`**、**`resolvedPromptBinding`**（见 **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** §2.3～2.4）。
- **运行时**：**`GET /api/v1/agent/execution/{executionId}`** 同字段。
- **意图**：**`IntentRecognizeResponse.effectiveLocale`**（camelCase）。

### FE 任务清单

- [x] 观测/执行列表与详情：展示 **`promptPackVersion`**；**`resolvedPromptBinding`** 可折叠 JSON 或仅展示关键键（**`tradingPromptPackId`**、**`tradingPromptPackVersion`** 等）。
- [x] 意图调试页（若有）：展示 **`effectiveLocale`**。

### 验收

- 对已发布 Prompt 场景的 **`scenarioId`** 发起 **`execution/accept`** 后，Admin 执行详情可见非空 **`promptPackVersion`**（无发布包时 **`null`**）。

### Refs

- `server/docs/BACKEND_SPEC.md` §3.3、`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md`
- 迁移 **`0011_exec_prompt_meta`**

---

## 2026-05-15 — Admin 列表/详情：`*At` / `ts` 的时区展示（UTC 契约）

### 背景

**`BACKEND_SPEC` §2.1、`API_INTEGRATION_GUIDE` §3.3**：服务端 API 返回的 **`createdAt`、`updatedAt`、执行时间线 `ts` 等** 均为 **UTC**（ISO 8601）。运营在列表里若直接当「本地墙钟」读，会与 **本机日志（常 CST）** 或 **UTC 表盘** 相差整整时区。**不改变 HTTP 契约**；由 **Admin** 在展示层统一换算并标注。

### 契约

- **无后端字段重命名**；仍消费现有 camelCase 时间字段。
- **语义**：解析为 **`Date`** 对象时按 **UTC** 理解（字符串带 `Z` / `+00:00` 时依标准）。

### FE 任务清单

- [x] **实例 / 执行 / 日志 / 观测** 等含 **`createdAt`、`updatedAt`、`ts`、`addedAt`** 的表格与详情：**默认展示运营时区**（建议固定 **`Asia/Shanghai`** 或与产品约定可配置），表头或列副标题标明 **`UTC+8`** 或 **`本地`**。
- [x] **可选**：工具栏或用户设置中 **切换「UTC / 本地」**，便于与灰度日志对表。
- [x] 避免把 API 原文字符串 **无 Z** 时默认当浏览器本地解析反噬（若后端偶发无时区串，按 **`BACKEND_SPEC` §2.1** 报告 **`/be`**）。

### 验收

- 同一笔记录在 **DB（UTC）**、**接口 JSON**、**Admin 列表（运营时区）** 三者时刻 **可换算一致**；表头**明确**所用时区。

### Refs

- `server/docs/BACKEND_SPEC.md` §2.1、`server/docs/API_INTEGRATION_GUIDE.md` §3.3

---

## 2026-05-15 — 执行时间线 summary：`venue` / `canonicalOp`（ADR-004）

### 背景

服务端现货闪兑与限价写路径内经 **`domain/canonical_trading`** 组单；**`GET /api/v1/admin/observability/executions/{executionId}/timeline`** 中，与 **`trade.spot.flash_convert` / `trade.spot.limit_order`** 相关的 **`quote`、`submit_order`、`trading.exchange_private`**（及 Telegram 下单异常占位）事件 **`summary`** 增加 **`venue`**（固定 **`coobit`**）、**`canonicalOp`**（**`place_order`**）。

### 契约

- **无 HTTP 变更**。时间线条目 **`summary`** 为 JSON 对象，在既有字段基础上可能含 **`venue`**、**`canonicalOp`**。

### FE 任务清单

- [x] **执行时间线 / 实例日志**：若 UI 展示 **`summary`** 键值，可选展示 **`venue` / `canonicalOp`**（筛选或列示按产品需要）
- [x] 类型：Admin 客户端若手写 **`ObservabilityTimelineItem.summary`**，可扩展可选字段

### 验收

- 下一笔闪兑或限价 HTTP 下单后，打开 **`…/executions/{executionId}/timeline`**，**`quote` 与 `trading.exchange_private`** 的 **`summary`** 含 **`venue`/`canonicalOp`**

### Refs

- `server/docs/BACKEND_SPEC.md`（Admin · Observability · 版本记录）、`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md` §5.2

---

## 2026-05-15 — 提示词治理：草稿创建与发布（`/prompts/strategy`）

### 背景

后端已扩展 **`/api/v1/admin/prompt-packs`**：**`POST`** 创建 **`DRAFT`**；**`POST …/{promptPackId}/publish`** 发布（**`SYSTEM`→`LOCKED`**，**`TRADING`/`ANALYSIS`→`PUBLISHED`** 且 **`scenarioId`** 须在 **`GET /api/v1/agent/scenarios`** 寄存器内；同 **scenario** 旧 **`PUBLISHED`** 行标记 **`DEPRECATED`**）；列表支持 Query **`promptPackType` / `scenarioId` / `lifecycle`**；**`PATCH` messages** 对 **`LOCKED`/`DEPRECATED`/`DISABLED`** 返回 **409**（**`PROMPT_PACK_LOCKED`** 等）；正文 **PM-C04** **256KiB** 上限 **`PROMPT_BODY_TOO_LARGE`**。**`GET /api/v1/internal/prompts/effective`** 仍仅 **`PUBLISHED`**。

### 契约

- **`POST /api/v1/admin/prompt-packs`**：**`promptPackType`** 必填；**`scenarioId`、`promptPackId`** 可选；**201** 详情体
- **`POST /api/v1/admin/prompt-packs/{promptPackId}/publish`**：**200** **`promptPackId`、`promptPackVersion`、`lifecycle`**
- 错误码：**`PROMPT_SCENARIO_INVALID`**、**`PROMPT_PUBLISH_INVALID_STATE`**、**`AGENT_PROMPT_PACK_ID_CONFLICT`** 等（见 **`ErrorBody.code`**）

### FE 任务清单

- [x] **`PromptStrategyPage.vue`**：**「新建草稿」** 调用 **`POST`**（表单：`promptPackType`、`scenarioId`、`promptPackId` 可选）；抽屉内可增加 **「发布」** 调 **`POST …/publish`**（**`DRAFT`** 可见）；展示 **`409`** 锁定/下线文案
- [x] **`admin-prompt-packs.ts`**：补充 **`createPromptPack`、`publishPromptPack`**；**`listPromptPacks`** 传 Query 与路由筛选对齐（可选）

### Refs

- `server/docs/BACKEND_SPEC.md`（Admin · Prompt Management）、`server/docs/API_INTEGRATION_GUIDE.md` §4.9

---

## 2026-05-15 — 准入管理 Access Control API（`/access` · 白名单 / 封禁 / 灰度 / 最低 VIP）

### 背景

后端已落地 **`/api/v1/admin/access-control/*`**（迁移 **`0010_admin_access_control`**）：白名单、封禁、**`membership/min-vip-tier`**、**`rollout`** 开关、KYC mirror stub；**`POST /api/v1/agent/access/evaluate`** 已接 **DB 封禁**与 **`enforce_rollout_whitelist`** 白名单门闸（在 env Phase1 放行之后、绑定校验之前）。原型页 **`/access?tab=whitelist`** 等可自 **`DEMO_*` / sessionStorage** 改为真实 API。

### 契约（camelCase）

- **`GET|POST /api/v1/admin/access-control/whitelist`**、`DELETE …/whitelist/{entryId}`：详见 **`API_INTEGRATION_GUIDE`** §4.6a；重复 **`listId`+`userUid`** → **409** **`AGENT_ADMIN_ACCESS_WHITELIST_DUPLICATE`**
- **`GET|POST …/bans`**、`DELETE …/bans/{banId}`；**`POST`** 可选 **`linkedPause`**（数值 **`userUid`** 时尝试 **`agent_instance.runtime_state=PAUSED`**）
- **`GET|PATCH …/membership/min-vip-tier`**（**`minVipTier`**）；**`GET|PATCH …/rollout`**（**`rolloutWhitelistEnforced`**，PATCH 须显式 bool）
- **`GET …/users/{userId}/kyc-mirror`**：**stub** **`available=false`**
- **门禁**：evaluate 顺序见 **`BACKEND_SPEC`**「Admin · Access control」/ §3.3 **`access/evaluate`**

### FE 任务清单

- [x] 新增或复用 **`admin`** API client（如 `access-control.ts`）：上述路径 + **`ErrorBody.code`**
- [x] **`AccessPage.vue`（`/access`）**：白名单 / 封禁 / VIP / 灰度开关与 **evaluate** 联调；移除或降级 **`DEMO_WHITELIST`**、**`DEMO_USER_BANS`**、sessionStorage VIP mock（以服务端为准）
- [x] 鉴权：**`Authorization: Bearer`**（与既有 Admin 登录一致）

### 验收

- 控制台配置白名单条目后，**`evaluate`** 在 **`enforce_rollout_whitelist=true`** 下对未列入用户返回 **`AGENT_ROLLOUT_BLOCKED`**；**`false`** 时恢复原有绑定/env 语义
- 封禁用户 **evaluate** 返回 **`AGENT_USER_BLOCKED`** 或 **`AGENT_COMPLIANCE_RESTRICTED`**（视 **`reasonCode`**）

### Refs

- `server/docs/BACKEND_SPEC.md`（Admin · Access control）、`server/docs/API_INTEGRATION_GUIDE.md` §4.6a、§4.4 **`access/evaluate`**
- `product-doc/specs/openapi/admin/access-control.yaml`

---

## 2026-05-15 — 运行场景寄存器 API 扩展（`GET /api/v1/agent/scenarios`）

### 背景

后端 **`scenarioId`** 目录与 Admin **`/ai/runtime-orchestration`** 静态表 **`2026.05-orc-v1`** 对齐；新增 **`wealth.holdings_read`** 交易所只读接线（`POST /sapi/v1/asset/account/by_type`）及占位场景键（合约/杠杆/条件单）**`readiness=phase1_stub`**。

### 契约

- **`GET /api/v1/agent/scenarios`**：响应增 **`orchestrationRegistryVersion`**（**`2026.05-orc-v1`**）；**`scenarios[]`** 项可选 **`title`**、**`category`**、**`riskLevel`**（camelCase）。
- **`POST /api/v1/agent/routing/execute`**：**`scenarioId=wealth.holdings_read`**（须托管绑定）→ 理财/OTC 账本只读摘要（与 **`BACKEND_SPEC` §3.3** 一致）。

### FE 任务清单

- [x] **运行场景页（可选）**：由静态 **`ROUTE_PHASE1_SCENARIOS`** 改为 **`GET /api/v1/agent/scenarios`** 拉取（或启动时合并），减少与后端寄存器漂移。

### 验收

- 上述 GET 在联调环境 **200**，且含 **`wealth.holdings_read`** 与 **`orchestrationRegistryVersion`**。

### Refs

- `server/docs/BACKEND_SPEC.md` §3.3 · `server/chainup_agent/application/agent_scenario_catalog.py`

---

## 2026-05-14 — Agent 实例 Runtime（R01–R06）· G01 横幅 · 实例日志 Tab（L01–L03 Phase1）

### 背景

后端已挂载 **`admin_agent_control`**：**G01** 只读、**Runtime** 单实例与批量、三类日志 Tab（基于 **`agent_execution` / `agent_execution_event`**，深链现有 Observability **`executions` / `timeline`**）。**`agent_instance.runtime_state`** 持久化（迁移 **`0009_agent_instance_runtime`**）。

### 契约

- **`GET /api/v1/admin/agents/runtime/global-agent-gate`**：**`globalAgentSwitchOn`**、**`opsSuspended`**、**`bannerMessage`**、**`reasonCodes`**
- **`POST /api/v1/admin/agents/instances/{instanceId}/runtime/{action}`**：**`action`**=`start`|`pause`|`resume`|`stop`；**200** 为 **`AdminAgentInstanceItem`**（与列表项一致）；**422**：**`AGENT_GLOBAL_OFF`**、**`AGENT_OPS_SUSPENDED`**、**`RUNTIME_COMMAND_REJECTED`**（及 **404** **`AGENT_ADMIN_INSTANCE_NOT_FOUND`**）
- **`POST /api/v1/admin/agents/instances/runtime/batch`**：**`instanceIds`**、**`action`**；整批 **start/resume** 在 G01 关闭时 **422**；否则 **200**，部分失败 **`code`**=`AGENT_BATCH_PARTIAL`，**`failures[]`**（**`instanceId`/`code`/`message`**），**`succeeded[]`**
- **`GET …/instances/{instanceId}/logs/conversations|tools|errors`**：Query **`limit`/`offset`**；响应 **`tab`**、**`items`**、**`total`**、**`observabilityBasePath`**；每项含 **`observabilityExecutionPath`** 或 **`observabilityTimelinePath`**（相对路径，可拼 Admin 基座）

列表/详情：**`runtimeState`**（**`RUNNING`/`PAUSED`/`STOPPED`/`ERROR`**）；**`agentState`**（**`GLOBAL_OFF`** / **`OPS_SUSPENDED`** / **`NORMAL`** / **`AGENT_SUBACCOUNT_BLOCKED`**）

### FE 任务清单

- [x] **Agent 实例列表/详情**：G01 横幅数据源（轮询或进入页拉 **`global-agent-gate`**）；**Start/Pause/Resume/Stop** 与批量 Runtime；按钮禁用与 **422** 文案对齐 **`agentState`/`reasonCodes`**
- [x] **实例侧「对话 / Tool / 错误」Tab**：接三类 logs API；行内跳转 Observability（**`executionId`** 路由已由 **`observability*Path`** 给出）
- [x] **类型/OpenAPI**：与 **`openapi.json`** 或生成 client 对齐 **`AgentBatchRuntimeResponse`**、日志 item 字段

### `/pm` 可选

- **`product-doc/specs/openapi/admin/agent-management.yaml`** 若需补充 **`GET …/global-agent-gate`** 与 **`RUNTIME_COMMAND_REJECTED`** 等与实现对签

### 验收

- 关 **`GLOBAL_AGENT_SWITCH`**（env **`CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED=true`**）时：**Start/Resume**（单/批）**422** **`AGENT_GLOBAL_OFF`**；**Pause/Stop** 仍 **200**
- 运维暂停 env 下 **Start/Resume** **422** **`AGENT_OPS_SUSPENDED`**
- 日志 Tab 与同一 **`telegram_user_id`** 的 **`GET …/observability/executions*`** 可交叉验证；深链可打开对应 execution / timeline

### Refs

- **`server/docs/BACKEND_SPEC.md`**（Admin · Agent 实例）、**`server/docs/API_INTEGRATION_GUIDE.md`** §4.7

---

## 2026-05-14 — 现货限价单：`POST …/trade/spot/limit-order` + 意图 + Telegram Type-A

### 背景

后端已落地 **`trade.spot.limit_order`**：**`POST /api/v1/agent/trade/spot/limit-order`**（Coobit **`POST /sapi/v2/order`** · **LIMIT**）；**`GET /api/v1/agent/scenarios`** 中该场景 **`readiness=ready`**。**`POST /api/v1/agent/intent/recognize`** 在槽位齐全时 **`plan.nextStep=CONFIRM_TYPE_A`**（与闪兑同一枚举，按 **`resolvedScenarioId`** 区分）。**Telegram** 内联确认前缀 **`lcp` / `lcx`**（限价），与闪兑 **`fcp` / `fcx`** 并存。

### 契约

- **`POST …/trade/spot/limit-order`**（camelCase）：**`userId`**、**`symbol`**、**`side`**（`BUY` | `SELL`）、**`volume`**（**base 数量** 字符串，与市价卖 / 闪兑用户口径一致）、**`price`**（限价字符串）、可选 **`timeInForce`**（**`GTC` \| `IOC` \| `FOK`**，缺省 **GTC**）、可选 **`newClientOrderId`**
- **200**：**`scenarioId`**=`trade.spot.limit_order`、**`orderId`** / **`orderIdString`**、**`type`**=`LIMIT`、**`exchangeOrderPreview`** 等（形状同闪兑响应）
- **422**：参数校验；**`PRICE_REJECTED_AGENT_BAND`** — 当 **`CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_ENABLED=true`** 时，限价相对公开 **`lastPrice`** 超出 **`CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_MAX_PCT`**（默认 5）
- **403 / 400 / 502**：与闪兑一致（未绑定、交易所拒单、网关失败）

### FE 任务清单

- [x] **Observability / Execution / Agent 调试**：识别新 **`scenarioId`**、时间线 **`limit.*`** / **`orderRequest.limitOrderMeta`**（若有）
- [x] **Runtime 类型**：为 **`SpotLimitOrderRequest` / `SpotLimitOrderResponse`**（或 OpenAPI 生成类型）增加封装；**`POST …/limit-order`**

### `/pm` 可选

- **`product-doc`** OpenAPI / 路线图 §2.2 若需显式列出 **`limit-order`** 路径与 **`PRICE_REJECTED_AGENT_BAND`**

### 验收

- Admin 侧能按 **`userId`** + **`scenarioId=trade.spot.limit_order`** 过滤执行；时间线含 **quote（可选 band）→ submit_order → trading.exchange_private**

### Refs

- **`server/docs/BACKEND_SPEC.md`**、**`server/docs/API_INTEGRATION_GUIDE.md`** §4.3a/现货写路径、**`openapi.json`** **`/api/v1/agent/trade/spot/limit-order`**

---

## 2026-05-14 — `routing/execute` 与 Telegram `read.*`：执行记录 + 时间线协查

### 背景

**`POST /api/v1/agent/routing/execute`** 每笔请求在服务端 **`execution_accept` → 路由逻辑 → `agent_execution_event` → `execution_finalize`**，与 **`POST …/trade/spot/flash-convert`** 一样可落 **`agent_execution`**。**Telegram** 已绑定用户的 **`read.*`** 在同一轮 **`run_telegram_turn_execution`** 的 **`executionId`** 下追加同款时间线事件（**`trading.exchange_public` / `trading.exchange_private`** · **`exchange_read`** 或 **`routing.read.failed`**）。

### 契约

- **`POST …/routing/execute`** **200**：除 **`routed` / `scenarioId` / `exchangeReadPreview`** 外，新增 **`executionId`**（与 Admin **`GET …/observability/executions/{executionId}/timeline`** 对齐）
- **403 等业务错误**：仍返回标准 **`AppError`**；DB 侧对应 **`agent_execution.state`**=**`FAILED`**，时间线含 **`routing.read.failed`**
- **时间线**：见 **`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** §5.2.2

### FE 任务清单

- [x] **Observability / Execution**：时间线 UI 识别 **`trading.exchange_public`**（只读行情）· **`stepKind`**=`exchange_read`；**`summary.exchangeReadPreviewSummary`**、**`transitionTrigger`**（**`routing.read.*`**）
- [x] **Agent 调试 / Runtime 类型**：**`RoutingExecuteResponse.executionId`** 展示或可复制

### Refs

- **`server/docs/BACKEND_SPEC.md`**（**`routing/execute`**、Admin 时间线）、**`server/docs/API_INTEGRATION_GUIDE.md`** §4.3  
- **`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** §5.2.2、§7

---

## 2026-05-14 — Phase1 公开行情：`read.market.depth` / `read.market.trades`

### 背景

后端已对齐 **`product-doc/specs/openapi/exchange/coobit-public.yaml`** 中 **`GET /sapi/v2/depth`** 与 **`GET /sapi/v2/trades`**：`POST /api/v1/agent/routing/execute` 在托管绑定前提下返回脱敏 **`exchangeReadPreview`**；关键词意图与 Telegram **`ROUTE_READ_SKILL`** 已接线。**`read.market.ticker`** 行为不变。

### 契约

- **`POST /api/v1/agent/routing/execute`**（camelCase Body）
  - **`scenarioId`**：`read.market.depth` | `read.market.trades`
  - **`userId`**：Telegram **`tg_id`** 数值串（与现有只读一致）
  - **`symbol`**：必填（如 `BTC-USDT`）
  - **`marketDataLimit`**：可选，整数 **1～100**，默认 **20**（depth 为每侧档位数；trades 为返回成交条数上限）
- **200**：**`routed`**、**`scenarioId`**、**`exchangeReadPreview`**、**`executionId`**（持久化执行锚点；Admin 时间线 **`GET …/executions/{executionId}/timeline`**）
- **403 / 422**：与 **`read.market.ticker`** 相同（未绑定 **`AGENT_SUBACCOUNT_REQUIRED`**；缺 **`symbol`** **`VALIDATION_ERROR`**）

### FE 任务清单

- [x] **`GET /api/v1/agent/scenarios`**：类型与列表展示纳入 **`read.market.depth`**、**`read.market.trades`**（**`readiness`**=`ready`）
- [x] 任意调试页 / Agent Runtime：**`routing/execute`** 表单支持上述 **`scenarioId`** + **`symbol`** + **`marketDataLimit`**
- [x] （若存在）**`agent-runtime.ts` / OpenAPI 生成类型**：**`RoutingExecuteRequest`** 增加 **`marketDataLimit`**

### 验收

- 已绑定用户：**`read.market.depth`** + **`symbol`** → **`exchangeReadPreview.asks`** / **`bids`** 非空（或交易所侧空盘口时数组为空但 **200**）
- **`intent/recognize`**：`BTC-USDT 盘口`、`ETH 近期成交` → **`scenarioId`** 与 **`plan.nextStep`**=`ROUTE_READ_SKILL`

### Refs

- **`server/docs/BACKEND_SPEC.md`** §3.3 **`routing/execute`**、**`server/docs/API_INTEGRATION_GUIDE.md`** §4.3  
- **`product-doc/specs/openapi/exchange/coobit-public.yaml`**（`/sapi/v2/depth`、`/sapi/v2/trades`）  
- **迁移**：**`0008_intent_nlu_read_market_expand`**（**`agent.runtime.intent_nlu`** 种子文案；LLM 意图须允许新 **`scenarioId`**）

---

## 2026-05-14 — 执行协查：现货闪兑时间线（quote → confirm → order）

### 背景

后端在 **`trade.spot.flash_convert`** 全链写入 **`agent_execution_event`**：Telegram Type-A **同一 `executionId`** 下可看到 **询价、确认提示、用户点按确认、挂单**；HTTP **`POST /api/v1/agent/trade/spot/flash-convert`** 亦有 **quote + 下单** 事件。**`summary`** 内可含 **`transitionTrigger`**（与产品 observability §2.4 / OpenAPI **`ObservabilityTimelineEvent`** 可选字段对齐思路一致）。

### 契约

- **不变更** Admin 路径：仍 **`GET /api/v1/admin/observability/executions/{executionId}/timeline`**
- **响应**：根字段 **`items[]`**（每项 **`eventName` / `ts` / `executionId` / `userId` / `summary` 对象**）；**`trading.exchange_private`** 与 **`agent.execution.step`（submit_order）** 可能同带 **`stepKind`**，请以 **`eventName`** 分卡展示
- **`trading.exchange_private`.`summary`**（典型 **`stepKind`=`submit_order`**）中的 **`orderRequest`** / **`exchangeResponsePreview`**（接口路径未改，仍为上述 **GET timeline**）：
  - **`orderRequest`**：**下单请求快照**，与 **`POST /sapi/v2/order`** 请求体 **字段子集**对齐，便于运营核对「发出的订单参数」；常见键含 **`symbol`**、**`side`**、**`type`**、**`volume`**、**`newClientOrderId`**，示例中可有 **`path`**（如 **`POST /sapi/v2/order`** 摘要）；**不包含** API Key、Secret、签名参数等敏感字段（脱敏策略以后端为准）。
    - **`orderRequest.flashMarketMeta`**：**市价单 wire `volume` 语义说明**（避免 BUY 侧 **`volume`** 被误认为 base 数量）：**`volumeSemantics`**（**`market_buy_quote_amount`** / **`market_sell_base_qty`**）、**`baseQtyUserRequested`**、BUY 时 **`quoteAmountOnWire`**（与 **`volume`** 一致）、**`lastPriceUsed`**、**`volumeSemanticsNote`**；SELL 时常用 **`baseQtyOnWire`** 等与 **`volume`** 对齐。
  - **`exchangeResponsePreview`**：**成功**时为交易所 ACK **白名单摘录**（如 **`orderIdString`**、**`clientOrderId`** 等）；**拒单且对端返回 JSON**（如时间戳偏差、**`AGENT_SPOT_ORDER_REJECTED`**）时为 **`code`/`msg`** 等同源摘要，可与 **`exchangeMsg`** 对照；**超时、非 JSON** 等通常 **无** 该对象。均**不是**原始响应全文。
  - **JSON 真源示例**：**`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** §5.2 响应样例中的 **`orderRequest`** / **`exchangeResponsePreview`** 对象。
- **闪兑典型 `eventName` + `summary.stepKind`**：见 **`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** §5.2.1

### FE 任务清单

- [x] **Observability / Execution 时间线**：消费 **`summary.transitionTrigger`**（若存在）与 **`stepKind`**，按 **quote → confirm → order** 排版；**`scenarioId`=`trade.spot.flash_convert`** 时对照 §5.2.1 验收
- [x] 类型：确保 TS 与 **`ObservabilityTimelineResponse`** 一致（**`items`**，非草稿里的 **`events`**）
- [x] **`orderRequest.flashMarketMeta`**：时间线卡片专块展示 **volume 语义**与 **`baseQtyUserRequested`** / **`quoteAmountOnWire`** / **`lastPriceUsed`** 等（协查可读）

### 验收

- 完成一笔 **HTTP flash-convert** 与一笔 **Telegram 确认闪兑** 后，各取 **`executionId`**：时间线条数与非空 **`summary`** 与 **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** 表一致；**复用 pending `executionId`** 路径下 **不应** 出现第二条 **quote**（下单前）

### Refs

- **`server/docs/BACKEND_SPEC.md`**（Admin 可观测性、Webhook 闪兑）、**`server/docs/API_INTEGRATION_GUIDE.md`** §4.7a、**`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** §5～7  
- **`product-doc/specs/openapi/admin/observability.yaml`**、`product-doc/specs/requirements/observability/overview.md`

---

## 2026-05-14 — Admin 可观测性：执行详情 · 协查时间线（`executionId`）

### 背景

后端持久化 **`agent_execution_event`**（**`0007_exec_event`**），并在 Telegram **闪兑二次确认**成功/失败路径追加 **`agent.execution.step`**、**`trading.exchange_private`** 等事件。运营可按工单 **`executionId`** 拉取时间线，对齐产品 **`observability-management/flow.md`**（FR-MC801）与 OpenAPI **`ObservabilityTimelineResponse`**。

### 契约

- **`GET`** **`/api/v1/admin/observability/executions/{executionId}/timeline`**
- **200**：根 **`items[]`**，每项 **`eventName`**、**`ts`**（ISO 8601）、**`executionId`**、**`userId`**、**`summary`**（JSON 对象，含 **`stepKind`/`outcome`/`transitionTrigger`** 或交易所 **`methodPathSummary`/`exchangeOutcome`** 等）
- **404**：**`AGENT_ADMIN_EXECUTION_NOT_FOUND`**（父 **`agent_execution`** 不存在；**无父行则无时间线**）
- **删除**：**`DELETE …/executions/{executionId}`** 会先删时间线子表再删主表

### FE 任务清单

- [x] **`/observability?tab=execution`**（**`ObservabilityPage`**）：与 product-doc IA 一致（`tab` 枚举）；执行 Tab 接线列表 **`GET …/executions`** 与工单时间线 **`GET …/{executionId}/timeline`**；其余 Tab 占位提示 OpenAPI 待挂载。
- [x] **Observability / Execution 详情**：增加 **「时间线」** Tab 或侧栏，调用上述 **GET**；解析 **`summary`** 为可读片段（可折叠原始 JSON）。（Admin API client / 类型：`ObservabilityTimelineResponse` · **`/runtime/executions/:id`** 与 **`/observability?tab=execution`**）
- [x] 列表行可浅链：**复制 `executionId`** 或 **打开详情并默认时间线**（按需）

### 验收

- 完成一次 Telegram 闪兑确认后，在控制台用同一 **`executionId`** 请求时间线：**≥1** 条事件；拒单或异常路径可见 **`outcome`/`exchangeOutcome`** 与错误摘要。

### Refs

- `server/docs/BACKEND_SPEC.md`（Admin 可观测性 · 执行协查）、`server/docs/API_INTEGRATION_GUIDE.md` §4.7a、`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md` §5  
- `product-doc/specs/openapi/admin/observability.yaml`、`product-doc/specs/requirements/domains/admin/observability-management/flow.md`

---

## 2026-05-14 — Telegram 闪兑：Inline 二次确认 + Prompt 管理子集

### 背景

- Webhook 除 **文本**外处理 **`callback_query`**：**`callback_data`** **`fcp`/`fcx` + 16位 hex**（与 **`agent_telegram_pending_confirm.public_token`** 对应）→ 确认时 **`POST /api/v1/agent/trade/spot/flash-convert`**（**`userId`=点按人 `from.id`**，须托管绑定）；取消仅删 pending。
- 新增：**`GET /api/v1/internal/prompts/effective?scenarioId=`**（**`304` ETag**）、**`GET|PATCH /api/v1/admin/prompt-packs*`**。**`INTENT_NLU_USE_LLM`** 的系统 prompt 从 DB **`scenarioId`=`agent.runtime.intent_nlu`** 读取（**`0006_pm_tg`** 种子包 **`pack_system_intent_nlu_v1`**）。

### FE 任务清单

- [x] **Admin · Prompt**：列表/详情/**编辑 `messages`（PATCH）** 对接 **`/api/v1/admin/prompt-packs`**（Bearer 同其它 Admin）；内部 **`/api/v1/internal/prompts/effective`** 供运行时/BFF，控制台可只做文档或运维链接。（**`admin-prompt-packs.ts`** · **`PromptStrategyPage.vue`** · 路由 **`/prompts/strategy`**）
- [x] **Telegram**：无需改 H5；**`/system/agent-runtime-probe`** 页头已说明 **闪兑确认** 依赖 **InlineKeyboard** / **`callback_query`**，**非** Deeplink。

### Refs

- `server/docs/BACKEND_SPEC.md` §3.1（Webhook）、Admin Prompt 小节；`server/docs/API_INTEGRATION_GUIDE.md` §4.2、§4.9

---

## 2026-05-14 — Agent Runtime：`POST /intent/recognize` 结构化 NLU + 裁决层

### 背景

`POST /api/v1/agent/intent/recognize`：**须 DB**（与其它 Agent 写库路由一致）。**`nlu.source`**：**`keyword_v1`** | **`llm_structured_v1`**（**`CHAINUP_AGENT_INTENT_NLU_USE_LLM=true`** 且 Admin 网关可用时）；LLM 系统段来自 **`admin_prompt_pack`**（**`agent.runtime.intent_nlu`**）或内置回退。**`orchestrationVersion`**：**`intent-router.policy.v2`**。**Telegram 已绑定**会话与 **HTTP** 共用 **`recognize_intent_full`**；闪兑 **`plan.nextStep=CONFIRM_TYPE_A`** 时发摘要并附 **确认/取消** Inline 按钮（会话态 **`agent_telegram_pending_confirm`**），**不**在文本回合内直接下单。

### 契约

- **路径**：`POST /api/v1/agent/intent/recognize`
- **`plan.nextStep`** 枚举：**`CLARIFY`** | **`ROUTE_READ_SKILL`** | **`ROUTE_CHAT_FAQ`** | **`CONFIRM_TYPE_A`** | **`BLOCKED_FEATURE`** | **`STUB_NOT_EXECUTABLE`** | **`UNKNOWN`**

### FE 任务清单

- [x] 若控制台或联调工具调用本接口：扩展 TS 类型与 client，消费 **`nlu` / `plan`**（编排调试、Execution 对齐）；无调用则可忽略。（**`agent-runtime.ts`** + **`AgentRuntimeProbePage`**）

### 验收

- 同一句子：**`plan.nextStep=CONFIRM_TYPE_A`** 且闪兑槽位齐全；限价+市价冲突词：**`CLARIFY`** 且 **`FR_AO02_AMBIGUOUS`**。

### Refs

- `server/docs/BACKEND_SPEC.md` §3.3、`server/docs/API_INTEGRATION_GUIDE.md` §4.3 · `server/chainup_agent/application/agent_intent_pipeline.py`

---

## 2026-05-13 — Agent Runtime：现货闪兑 HTTP（quote + flash-convert）

### 背景

第二阶段 **§2.1**：后端新增 **`GET /api/v1/agent/trade/spot/quote`**、**`POST /api/v1/agent/trade/spot/flash-convert`**（托管绑定用户 + 交易所 **`POST /sapi/v2/order` · `MARKET`**）。**`routing/execute`** 对 **`trade.spot.flash_convert`** 仅返回指引正文，**不在该路由内下单**。

### 契约（camelCase / Query）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/agent/trade/spot/quote` | Query **`userId`**（`tg_id`）、**`symbol`** → **`scenarioId`、`symbol`、`symbolOrder`、`quotePreview`** |
| POST | `/api/v1/agent/trade/spot/flash-convert` | Body **`userId`、`symbol`、`side`（BUY/SELL）、`volume`（字符串）**，可选 **`newClientOrderId`** → **`orderId`、`exchangeOrderPreview`、`type`** 等 |

错误码：**403** **`AGENT_SUBACCOUNT_REQUIRED`**；**400** **`AGENT_SPOT_ORDER_REJECTED`**；**502** **`AGENT_SPOT_ORDER_FAILED`** / **`AGENT_OPENAPI_PROBE_FAILED`**。**MARKET BUY**：`volume` 语义为 GitBook 所称 **计价资产数量（amount）**。

### FE 任务清单

- [x] （若控制台 / BFF 需演示或运维联调）在 **`admin/`** 增加或扩展 API client（如 `agent-runtime` 同类模块）与可选调试页：封装上述两路径；Vite **`/api` proxy** 已指后端时可用相对路径。（**`getAgentTradeSpotQuote` / `postAgentTradeSpotFlashConvert`**；调试页 **`/system/spot-flash-convert`**）
- [x] 类型：可从服务端 **`/openapi.json`** 生成或手写 TS 类型，与响应字段对齐。（**`AgentTradeSpotQuoteResponse`**、**`AgentTradeSpotFlashConvertBody|Response`**，对齐 `agent_spot_trade` schema）

### `/pm` 可选

- 产品 **`product-doc/product/roadmap.md`** 与 **`product-doc/specs/openapi/exchange/coobit-spot.yaml`** 已为路径锚点（遗留 HTTP 阶段见 `development-roadmap.md`）；若需冻结 **Agent** 侧 YAML，可另开条目。

### 验收

- 已绑定用户：`GET …/quote` **200** 且 **`quotePreview`** 含 ticker 摘要；`POST …/flash-convert` 在所内沙箱可用时 **200** 且返回 **`orderId`** 或交易所字段。

### Refs

- `server/docs/BACKEND_SPEC.md` §3.3 · `server/docs/API_INTEGRATION_GUIDE.md` §4.3a  
- `server/coobit_openapi.md`

---

## 2026-05-13 — Admin API：`ADMIN_CONSOLE_JWT_SECRET` 与 Bearer 强制

### 背景

服务端收口：**当**进程配置 **`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`**（≥16）时，`POST /api/auth/login` 返回的 **`access_token`** 为可校验 **JWT**；所有 **`/api/v1/admin/*`** **必须**带 **`Authorization: Bearer <access_token>`**。未配置 Secret 时行为与此前一致（随机 token、Admin 路由不校验）。

### FE 任务清单

- [x] **axios/fetch 封装**：在 **JWT 模式**下为 **`/api/v1/admin/`** 请求统一附加 **`Authorization`**（沿用既有 login 存储的 token；实现为 `http-client` + `ky` 对 **`v1/admin/*` path 注入 Bearer）。
- [x] **401 处理**：遇 **`ADMIN_CONSOLE_AUTH_REQUIRED`** / **`ADMIN_CONSOLE_ACCESS_TOKEN_EXPIRED`** / **`ADMIN_CONSOLE_ACCESS_TOKEN_INVALID`** 时清空本地 token 并跳转登录。

### Refs

- `server/docs/BACKEND_SPEC.md` §3.1 · §5  
- `server/chainup_agent/api/deps.py` · `require_admin_console_bearer`

---

## 2026-05-13 — Observability：删除执行记录 `DELETE …/executions/{executionId}`

### 背景

Admin 增加 **硬删除** **`agent_execution`**：**`DELETE /api/v1/admin/observability/executions/{executionId}`** → **204**（无 Body）；不存在 → **404** **`AGENT_ADMIN_EXECUTION_NOT_FOUND`**。供联调清理列表脏数据。

### FE 任务清单

- [x] **`admin-observability.ts`**：新增 **`deleteAdminObservabilityExecution(executionId)`**（**`DELETE`**，期望 **204**）。
- [x] **`ExecutionListPage`** / **`ExecutionDetailPage`**：危险操作二次确认后调用删除；成功后刷新列表或 **`router.replace`** 回列表。

### Refs

- `server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md` §4  
- `server/docs/BACKEND_SPEC.md` · Admin · Observability  

---

## 2026-05-13 — Observability：`agent_execution` Admin 列表/详情 API

### 背景

服务端已实现 **`GET /api/v1/admin/observability/executions`**（分页 + 筛选）与 **`GET …/executions/{executionId}`**（单行），数据源 **`agent_execution`**（与 Runtime **`execution/*`**、Telegram **`accept→finalize`** 同源），camelCase 响应。**404**：**`AGENT_ADMIN_EXECUTION_NOT_FOUND`**。**422**：非法 **`state`**。

### 契约（Query 节选）

| Query | 说明 |
|--------|------|
| **`limit`** / **`offset`** | 1～200 / ≥0，默认 50 / 0 |
| **`executionId`** | 精确 |
| **`userId`** / **`channel`** / **`scenarioId`** | 可选精确 |
| **`state`** | **`ACCEPTED` \| `SUCCEEDED` \| `FAILED` \| `CANCELLED`** |
| **`keyword`** | 子串匹配 **`executionId` / `userId` / `scenarioId`** |
| **`createdAfter`** / **`createdBefore`** | **`date-time`** |

排序：**`createdAt`** **降序**。

### FE 任务清单

- [x] API client（ **`admin/src/shared/api/admin-observability.ts`**，前缀 **`/api/v1/admin/observability`**）。
- [x] **`/runtime/executions`**（**`ExecutionListPage`**）：**`GET …/executions`**（`keyword` / `state` / `scenarioId` / 日期 + 分页）；已移除本地 **`demo-runtime-api`** 列表依赖。
- [x] **`/runtime/executions/:executionId`**（**`ExecutionDetailPage`**）：首屏 **`GET …/executions/{executionId}`**；「时间线」Tab **`GET …/executions/{executionId}/timeline`**；其余 Tab **占位**。协查视图另见 **`/observability?tab=execution`**。

### 验收（简述）

列表 Network：**200**，**`items`/`total`**；点开详情：**executionId** 一致。**403**：控制台登录态与本项目惯例一致。

### Refs

- `server/docs/BACKEND_SPEC.md` · Admin · Observability — 持久化执行  
- `server/docs/API_INTEGRATION_GUIDE.md` §4.7a  
- **`server/docs/API_ADMIN_OBSERVABILITY_EXECUTIONS.md`**（字段级契约 / 示例 JSON / 筛选语义）

---

## 2026-05-13 — Agent execution DB 持久化 · Telegram Webhook 早 ACK

### 背景

**`agent_execution`**（§1.5）：**accept / finalize** 与 Telegram 闲聊链路写入数据库并 **`commit`**；进程重启后 **`GET /api/v1/agent/execution/{executionId}`** 仍可读到记录。**门禁 deny** 路径 **不**写入 execution。Webhook：**HTTP 200 先行**，耗时逻辑放 **`BackgroundTasks`**，避免 Telegram 长时间等待。

### FE 任务清单

- [x] **Agent 运行时探针**（`/system/agent-runtime-probe`）：**`/fe` 已对齐**页首说明 — execution Phase1 **落库**，可按 **`executionId`** 复查（Telegram Webhook 自动链路同理）。**代码**：`admin/src/pages/system/AgentRuntimeProbePage.vue`。

### 可选 / 本期不要求

- **`/runtime/executions`**：服务端 **`GET /api/v1/admin/observability/executions*`** 已就绪 → **`/fe`** 接线见 **`FE_HANDOFF.md`** **顶部「Observability」**小节；时间线 / 工具 / LLM 子资源仍为 **`openapi/admin/observability.yaml`** 后续迭代。
- Webhook 早 ACK 为服务端行为，Admin **无**必改调用序列。

### Refs

- `server/docs/BACKEND_SPEC.md` · Agent execution / Telegram webhook  
- `server/docs/API_INTEGRATION_GUIDE.md`  

---

## 2026-05-13 — Telegram 闲聊 LLM：火山方舟 `/responses` + `secretRef` 明文 Key

### 背景

**`chat.faq`** 上游路由：`Provider.baseUrl` 主机含 **`volces.com`** 时 **`POST …/api/v3/responses`**（与方舟 **`Authorization: Bearer`**、`input` · **`input_text`** 对齐；Telegram 侧 **`stream=false`** 单次回复）。其余 **`baseUrl`** 仍走 OpenAI 兼容 **`…/chat/completions`**。

### 契约 / 运维（Admin 提示可对齐）

- **`secretRef`**：**匹配 env 变量名**（`^[A-Za-z_][A-Za-z0-9_]*$`）→ 服务端读 **`os.environ`**；**否则**整串视为 **Bearer/API Key**，**明文**写入 **`admin_ai_provider.secret_ref`**（Phase1）。空 → **`CHAINUP_AGENT_LLM_FALLBACK_API_KEY`**。
- **方舟**：**`baseUrl`** 填控制台 Endpoint 根（如 `https://ark.cn-beijing.volces.com`）；模型 id 与控制台开通一致（目录 **`modelId`**）。
- **运行时策略**：须保存 **`scenarioChatModel`**（及目录中存在对应 **`modelId`**，**`status=enabled`**）。
- **关键词**：含「行情」「余额」等仍走只读路由，**不**走 LLM。

### FE 任务清单

（带 **`[x]`** ＝ **`/fe` 已在 `admin/` 落地**，**非**「待办句式」；**`/be`** 可按下行 **代码路径** 抽查。）

- [x] AI Settings / Provider：**`secretRef`** — **已完成**「env 变量名 **或** 明文 Key（入库）、安全提示、回退 env」等帮助文案。**代码**：`admin/src/pages/ai/AiSettingsPage.vue`（页头、目录空状态、新增 Provider 弹窗）。
- [x] （可选）方舟 **`baseUrl`** / **`modelId`** — **已完成**占位与说明（Provider **`baseUrl`** 示例根域名；**添加模型** 弹窗内方舟 **`modelId`** 与 **`volces.com` → `/api/v3/responses`** 提示）。**代码**：同文件 `AiSettingsPage.vue`。

### Refs

- `server/docs/BACKEND_SPEC.md` §3.1、§「Admin · AI Settings」  
- `server/docs/API_INTEGRATION_GUIDE.md` §4.2、§4.6  
- `server/chainup_agent/application/agent_llm_chat.py`  

---

## 2026-05-13 — AI Settings：删除后刷新「复活」— 非没落库

### 背景

**`DELETE`/`POST`/`PATCH`** 均已 **`commit`**。先前 **`GET …/admin/ai/*`** 在 **Provider 目录为空** 时会自动插入 **`demo`** 目录（`_maybe_seed_catalog`），因此删掉 **`demo`**（或删光 Provider）后 **刷新** 会再次看到 **`demo`**，易被误判为「没落库」。现已改为：**默认关闭**该运行时种子（**`CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY`**，默认 **false**）；正常部署依赖 **`alembic upgrade`**（**`0004_aisettings`**）写入初始 **`demo`**；仅 ORM **`create_all`** 无迁移数据时，可在 `.env` 设 **`…=true`** 保留旧便利行为。

### FE / 验收

- Admin **Network** 面板确认 **`DELETE`** → **204**，刷新后 **`GET …/providers`** 与删除预期一致。  

### Refs

- `server/docs/BACKEND_SPEC.md` · Admin · AI Settings  
- `server/docs/API_INTEGRATION_GUIDE.md` §4.8  

---

## 2026-05-13 — AI Settings：删除 Provider（DELETE）

### 背景

新增 **`DELETE /api/v1/admin/ai/providers/{providerId}`**：**204**；可选 **`If-Match`**（与 **`row_version`** 一致，冲突 **409**）。不存在 **404** **`AGENT_AI_PROVIDER_NOT_FOUND`**。数据库 **`admin_ai_model.provider_id`** 为 **`ON DELETE CASCADE`**，删除 Provider 会删除其下模型目录行（网关 **`defaults`** JSON 若仍引用该 **`providerId`/模型 id**，需运营自行 **`PATCH /defaults`** 调整 — 服务端 Phase1 不做级联改写 JSON）。

### FE 任务清单

- [x] Provider 列表 / 详情：**删除** 调用 **`DELETE`**；必要时二次确认（级联删模型）。

### Refs

- `server/docs/BACKEND_SPEC.md`、`server/docs/API_INTEGRATION_GUIDE.md` §4.8  

---

## 2026-05-13 — AI Settings：模型详情 / 删除 / PATCH 归属（providerId）

### 背景

- **`GET /api/v1/admin/ai/models/{modelId}`**：单条 **`LlmModelSummary`**，便于编辑表单回填。  
- **`DELETE /api/v1/admin/ai/models/{modelId}`**：**204**，支持 **`If-Match`**（与 **`row_version`** 一致）。  
- **`PATCH …/models/{modelId}`**：在原有 **`status`**、**`contextWindowTokens`** 上增加可选 **`providerId`**（变更模型归属 Provider）；未知 Provider → **404** **`AGENT_AI_PROVIDER_NOT_FOUND`**；Body 全空或与现状相同则不递增 **`row_version`**。

### FE 任务清单

- [x] API client：**`GET`/`DELETE`**；**`PATCH`** 增加 **`providerId`**。  
- [x] 模型运营：**编辑**（PATCH）、**删除**（DELETE + 列表刷新）、详情可用 **GET**。

### Refs

- `server/docs/BACKEND_SPEC.md`、`server/docs/API_INTEGRATION_GUIDE.md` §4.8  

---

## 2026-05-13 — AI Settings：`POST /models` 与 Provider 创建 500 修复

### 背景

1. **`POST /api/v1/admin/ai/providers`** 曾误用 **`LlmProviderDetail.model_validate(LlmProviderSummary)`**，Pydantic v2 抛 **`ValidationError`** → **500**；已改为经 **`model_dump`** 构造 **`LlmProviderDetail`**。  
2. 新增 **`POST /api/v1/admin/ai/models`**：**201** 写入 **`admin_ai_model`**；**404** **`AGENT_AI_PROVIDER_NOT_FOUND`**；同一 **`modelId`** **409** **`AGENT_AI_MODEL_ID_CONFLICT`**。

### 契约

- **`POST /api/v1/admin/ai/models`** · Body（camelCase）：**`providerId`**、**`modelId`** 必填；可选 **`status`**（默认 **`enabled`**）、**`contextWindowTokens`**。响应 **`LlmModelSummary`**；**Header `ETag`** 含 **`row_version`**。

### FE 任务清单

- [x] API client：增加 **`POST …/models`**（及 **`409`** / **`404`** 处理）。
- [x] 模型运营 UI：**「添加模型」** 调用 **`POST`**，列表仍 **`GET /models`**。

### `/pm` 可选

- 若 SSOT 仅 **`PATCH`** 模型：建议在 **`product-doc/specs/openapi/admin/ai-settings.yaml`** 增补 **`POST /models`** 或与后端扩展条文对齐。

### 验收

1. **`POST …/providers`** → **201**，响应含 **`providerId`** / **`configured`**。  
2. **`POST …/models`** → **201**；重复 **`modelId`** → **409**；不存在 **`providerId`** → **404**。  

### Refs

- `server/docs/BACKEND_SPEC.md` · Admin · AI Settings  
- `server/docs/API_INTEGRATION_GUIDE.md` · §4.8  

---

## 2026-05-13 — Admin AI Settings（模型配置 / 网关默认）

### 背景

服务端已实现 **`/api/v1/admin/ai/*`**（对齐 **`admin/ai-settings.yaml`**），持久化 Provider、模型目录、网关默认 JSON（含 **`orchestrationExecutionBudget`**）及 Health 策略。网关默认 JSON **兼容产品原型** **`product-doc/src/admin` · `/ai-settings`**（`AiSettingsPage` / `aiRuntimePolicyMock`）：含 **`defaultInferenceModel`**、`scenarioChatModel`、`scenarioTradingModel`、`scenarioRiskModel`、`maxContextTokens`、`timeoutSec`、降级开关、`fallbackModel`、成本限流等。**Telegram → LLM 推理调用下一迭代再接**，本轮仅配置 API。

### 契约摘要（camelCase）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/ai/providers` | 列表（迁移或运维种子见 **`CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY`**；默认不自动插入 demo） |
| POST | `/api/v1/admin/ai/providers` | **201**；Body：`displayName`、`baseUrl` 必填；可选 `secretRef`（**env 变量名** 或 Phase1 **明文 Key 入库**，见上文 §secretRef） |
| GET | `/api/v1/admin/ai/providers/{providerId}` | **404** `AGENT_AI_PROVIDER_NOT_FOUND` |
| PATCH | `/api/v1/admin/ai/providers/{providerId}` | 可选 **Header `If-Match`**（与 **`row_version`** 一致）；**409** `AGENT_AI_SETTINGS_VERSION_CONFLICT` |
| DELETE | `/api/v1/admin/ai/providers/{providerId}` | **204**；可选 **`If-Match`**；下属模型 **DB CASCADE** |
| GET | `/api/v1/admin/ai/models/{modelId}` | **404** `AGENT_AI_MODEL_NOT_FOUND` |
| GET | `/api/v1/admin/ai/models` | Query 可选 **`providerId`** |
| POST | `/api/v1/admin/ai/models` | **201**；Body **`providerId`**、**`modelId`**；可选 **`status`**、**`contextWindowTokens`**；**409** `AGENT_AI_MODEL_ID_CONFLICT` |
| PATCH | `/api/v1/admin/ai/models/{modelId}` | Body：可选 **`providerId`**、**`status`**、**`contextWindowTokens`**；**404** `AGENT_AI_MODEL_NOT_FOUND` / `AGENT_AI_PROVIDER_NOT_FOUND` |
| DELETE | `/api/v1/admin/ai/models/{modelId}` | **204**；可选 **`If-Match`** |
| GET | `/api/v1/admin/ai/defaults` | 网关默认（内置默认值 ∪ DB） |
| PATCH | `/api/v1/admin/ai/defaults` | JSON 合并；**`orchestrationExecutionBudget`** 数量下限校验 **422**；可选 **`If-Match`** |
| GET/PATCH | `/api/v1/admin/ai/health-policy` | JSON 文档（Phase1 自由结构） |
| POST | `/api/v1/admin/ai/providers/{providerId}/health` | 同步探针：**200** `ok`、`latencyMs`、`checkedAt`、`message` |

**响应**：Provider 含 **`configured`**（是否有 **`secretRef`**），**不返回** API Key。

### FE 任务清单

- [x] 新增或对齐 **`admin`** API 客户端（例：`shared/api/admin-ai-settings.ts`），前缀 **`/api/v1/admin/ai`**。
- [x] **AI Runtime / 模型策略页**：将 **`AiSettingsPage`** 从本地 mock 改为 **`GET/PATCH /defaults`**（字段与 `aiRuntimePolicyMock` 对齐）。
- [x] （可选）Provider / **`secretRef`**：**`GET`** 列表、**`POST`** 创建、**`DELETE`**；**`PATCH`/`GET` 单条 Provider** 暂未接 Admin UI（与契约一致，可后续补）。
- [x] （可选）模型运营：`GET /models`、`GET /models/{modelId}`、**`POST /models`**、**`PATCH /models/{modelId}`**（含 **`providerId`**）、**`DELETE /models/{modelId}`**。
- [x] （可选）**编排预算**：表单项 **`orchestrationExecutionBudget`**。
- [x] PATCH **409**：冲突时在界面提示并 **`loadAll` 全量刷新**（Defaults / 模型行编辑）；**`If-Match` / ETag** 乐观锁暂未串联（遇 409 依赖刷新后重保存）。

### 验收建议

1. `GET .../defaults` 含 **`scenarioChatModel`**、**`rateLimitRpm`**。  
2. **`PATCH`** 更新 **`timeoutSec`** 后再 **`GET`** 一致。  
3. 错误 **`If-Match`** → **409**。  

### Refs

- `server/docs/BACKEND_SPEC.md` · Admin · AI Settings  
- `server/docs/API_INTEGRATION_GUIDE.md` · §4.8  
- `product-doc/specs/openapi/admin/ai-settings.yaml`  
- `product-doc/src/admin/src/pages/ai/AiSettingsPage.tsx`
