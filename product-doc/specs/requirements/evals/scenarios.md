# Evals · 场景登记（首版草案）

**职责**：**可执行** **评测 / 回归** **场景** **与 **`SC-*`** **映射**。**素材正文**（对话日志、脚本）**可** **外链** **所内仓库**；**本条** **只** **保** **索引与版本槽**。**与** **契约开放面** **同窗抽检** → [**§0 速链**](../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../closure-remaining.md#cc-exec-solve-path) · [`closure-remaining` §7](../closure-remaining.md#cc-remaining-open-items)（**P0/P1、§3 实现验收** **等** **一行总表**）；**走读缺口** → **[§7.1](../closure-remaining.md#cc-remaining-gap-paste)** · **闭环路径** → **[§7.5](../closure-remaining.md#cc-remaining-open-close-path)** · **MR 执行清单** → **[§7.6](../closure-remaining.md#cc-closure-exec-checklist)**。

**OpenAPI / 配置真源**：**预算字段** **[`OrchestrationExecutionBudget`](../../openapi/components/ai-settings-schemas.yaml)**；**行情 Runtime** **[`market-runtime-schemas.yaml`](../../openapi/components/market-runtime-schemas.yaml)**；**记忆 Runtime** **[`memory-runtime-schemas.yaml`](../../openapi/components/memory-runtime-schemas.yaml)**；**叙事 GWT** **[`market-narrative.md`](./market-narrative.md)**；**记忆 GWT** **[`memory-runtime.md`](./memory-runtime.md)**。

---

## 1. 登记表

| `evalSetId` | 版本 / 轴 | 构造要点 | 映射 `SC-*` / 流程 |
|-------------|-----------|----------|---------------------|
| **`eval.obs.timeline_transition_contract`** | `0.1.0` | **非** **仅只读**：**走通** **[`execution-transition-matrix` §2.2.1](../../Runtime/execution-transition-matrix.md) **一条** **允许主态边** **之** **`executionId`**；**Then** **`FR-MC801` 时间线** **满足** **[`observability/overview` §2.4](../observability/overview.md)** **该边 Trigger 之下限** **或** **`transitionTrigger` 对签** | **`SC-OBS08`**、**[`execution-transition-matrix`](../../Runtime/execution-transition-matrix.md)** |
| **`eval.runtime.pipeline_write_order`** | `0.1.0` · **GWT** [`pipeline-write-order.md`](./pipeline-write-order.md) | **写路径** **`trade.spot.limit_order`**：**`spec_read` → `confirmation.required` → 写工具**；**负例** **跳过确认 / 逆序 spec_read** | **SC-OBS08**、**SC-OBS11**、**SC-TA01**、[`domain-model` §4](../Runtime/domain-model.md)、[`pipeline-walkthrough-checklist`](../Runtime/pipeline-walkthrough-checklist.md) |
| **`eval.orchestration.budget.tools`** | `0.1.0` · 配置 `maxToolCallsPerExecution=k`（**k** **为小整数** **如 3～5**） | 单 **`executionId`** **内** **迫使** **≥k+1** **次** **达终态** **工具调用**（**只读循环** **或** **沙箱** **mock**） | **`SC-AO-08`**、**`SC-OBS07`** |
| **`eval.orchestration.budget.steps`** | `0.1.0` · `maxOrchestrationStepsPerExecution=k` | **迫使** **编排** **超过** **k** **个** **`agent.orchestration.step`**（**DAG** **压力** **fixture**） | **同上** |
| **`eval.hitl.write_without_confirm`** | `0.1.0` | **尝试** **跳过** **类型 A** **直写** **须** **被拒绝** | **`SC-TA01`/`SC-TA02`**、[`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md) |
| **`eval.hitl.high_risk_double`** | `0.1.0` | **全仓清仓语义 / 大额市价** **须** **二次确认** **与普通类型 A** **可区分** | [`high-risk-confirmation.md`](../prompts/confirmation/high-risk-confirmation.md)、**`SC-TA*`** |
| **`eval.obs.504_unknown_write`** | `0.1.0` | **写** **遇** **504** **`exchangeOutcome=unknown`** — **禁止** **对用户报 SUCCESS** | **`SC-OBS03`**、[`architecture.md`](../../design/architecture.md) |
| **`eval.runtime.unknown_stall_resolution`** | `0.1.0` | **构造** **`unknown_pending`** **超过** [`unknown-stall-policy`](../risk/unknown-stall-policy.md) **§1** **Δt**：**须** **可观测告警或等价升级**；**用户侧** **`FR-T05` 族** **可读**；**查单/退避** **须** **有上界**（**禁止** **裸热循环**） | **`SC-RISK-06`**、[`unknown-state.md`](../Runtime/unknown-state.md)、[`recovery.md`](../Runtime/recovery.md) |
| **`eval.trade.slot_quote_base_clarify`** | `0.1.0` | **注入** **含** **quote/base** **歧义** **之** **自然语言**（**如** **「买 1000 的 BTC」** **未** **冻结口径**）；**Then** **须** **澄清** **或** **`FR-T05`**；**禁止** **无确认** **即** **`call_exchange_write`** | **`FR-T07`**、[`trade-via-agent.md`](../flows/trade-via-agent.md) **S6**、[`implementation-alignment.md`](../domains/agent/agent-orchestration/implementation-alignment.md) **§8** |
| **`eval.runtime.user_visible_phase_copy`** | `0.1.0` | **构造** **同一** **`executionId`** **跨** **`waiting_confirmation`→`executing`→`settling`/`unknown_pending`** **之多段** **用户消息**；**Then** **副本** **须** **与** [`telegram/overview.md`](../domains/agent/telegram/overview.md) **§3.1**、[`trade-via-agent.md`](../flows/trade-via-agent.md) **S5.1.1** **一致** — **禁止** **在途** **报** **终局成功**、**禁止** **UNKNOWN** **报** **成交** | **JV-12**、[`product/journey-validation.md`](../../../product/journey-validation.md)、[`unknown-state.md`](../Runtime/unknown-state.md) |
| **`eval.product.user_journey_chain`** | `1.1.0` · 与 [`../../../product/journey-validation.md`](../../../product/journey-validation.md) **同窗** | Bot **冷启动 Deeplink**；**绑定 409**（**含 **`AGENT_BIND_SUBACCOUNT_UID_MISMATCH`** / **`SC-WEB-12`**）；**母账号 VIP 门禁**；**类型 A 绕过负例**；**站内 Billing Deeplink**；**504/UNKNOWN 话术**；**全 **`scenarioId`** **九步**（**JV-07**）；**Goal 七维**（**JV-10**）；**Golden Path 八维**（**JV-11**）；**用户阶段话术与卡面对账**（**JV-12**）；**Webhook 重复（JV-08）**；**全局闸（JV-09）** | [`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md)（[**范例**](../../../flow/e2e-closed-loop.md#runtime-walkthrough)、[**全键索引**](../../../flow/e2e-closed-loop.md#runtime-walkthrough-scenarios)）；**文首「架构语言」** → [`architecture`「与通用 Agent 栈之对照」](../../design/architecture.md)；[`goal-and-execution-paths` §5–§6](../domains/agent/agent-orchestration/goal-and-execution-paths.md)、[`flows/consume-and-bill.md`](../flows/consume-and-bill.md)、**ADR-001**、[`domains/web/agent-onboarding.md`](../domains/web/agent-onboarding.md) **`FR-WEB06`** |
| **`eval.runtime.telegram_update_idempotent`** | `0.1.0` | **同一 **`update_id`**（**或** **同窗幂等键**）** **二次投递**；**Then** **0** **第二笔写**、**0** **二次核销成功** | **`SC-B20`** **方向**、[`persistence.md`](../../Runtime/persistence.md)、[`locking.md`](../../Runtime/locking.md)、[`product/journey-validation.md`](../../../product/journey-validation.md) **JV-08** |
| **`eval.runtime.global_pause_blocks_new_write`** | `0.1.0` | **快照** **含** **全局 Pause/Kill（拒新写）**；**Then** **新交易写** **阻断** **且** **`FR-T05`** **可解释**；**禁止** **静默穿透写成功** | [`kill-switch.md`](../risk/kill-switch.md)、[`exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md)、[`product/journey-validation.md`](../../../product/journey-validation.md) **JV-09** |
| **`eval.trade.spot.flash_convert.gwt`** | `0.1.0` · **GWT** **同构** [`implementation-alignment.md`](../domains/agent/agent-orchestration/implementation-alignment.md) **§12** | 用户话束 **闪兑/市价换币** → **主 **`scenarioId`=`trade.spot.flash_convert`**（**以寄存器为准**）；**读技能 → 类型 A → `call_exchange_write`**；**Then** **计费 S3～S5** **与** **`billing` §10.1** **一致** | **`SC-AO-01`～`04`**、[`trade-via-agent.md`](../flows/trade-via-agent.md)、[`consume-and-bill.md`](../flows/consume-and-bill.md)、[`routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md) |
| **`eval.read.market_portfolio_no_write`** | `0.1.0` | **只读**：行情 + **私有余额/持仓** **读** **须** **过 `FR-T02`**；**Then** **本轮无** **类型 A** **与** **`call_exchange_write`**；**观测** **无** **交易所写工具** **或** **仅有读类 tool** | **`SC-AO-02`**、[`read-analyze-and-search-via-agent.md`](../flows/read-analyze-and-search-via-agent.md)、[`implementation-alignment.md`](../domains/agent/agent-orchestration/implementation-alignment.md) **§4 §1 分区** |
| **`eval.automation.monitoring_create`** | `0.1.0` | **创建** **监控/到价类** 任务（**寄存器键** **如 **`monitoring.price_condition`** **以 MR 为准**）；**Then** **凡所内写** **须** **类型 A**；**`taskId` 可归因** **且** **≠ `executionId`** | **`SC-AO-07`**、[`automation-alerts.md`](../flows/automation-alerts.md)、[`state-machine.md`](../domains/agent/agent-orchestration/state-machine.md)、[`contract-closure.md`](../contract-closure.md) **§1.2 第 5 款** |
| **`eval.intent.invalid_scenario_reject`** | `0.1.0` | **注入** **非法/占位 **`scenario_id_candidates`** **或** **与 **`routing-engine`** **不一致**；**Then** **澄清** **或** **`FR-T05`** **可解释码**；**禁止** **静默落交易所写** | **`FR-AO02`**、[`routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)、[`overview.md`](../domains/agent/agent-orchestration/overview.md) **§6** |
| **`eval.context.session_execution_tool_bind`** | `0.1.0` | **交错** **两** **`sessionId`** **或** **两** **`executionId`** **（** **所内 fixture** **）**；**Then** **观测上** **每条 **`agent.tool.call`** **与** **本用户本回合** **join** **一致**；**Prompt 装配** **不得** **混入** **他会话** **工具原文** | [`context-management.md`](../../Runtime/context-management.md) **§2**、[`memory-runtime.md`](../../Runtime/memory-runtime.md) **§2.0、§10～§11**、[`locking.md`](../../Runtime/locking.md) **§1**、[`observability/overview.md`](../observability/overview.md) **§2.1** |
| **`eval.memory.semantic_gate_off`** | `0.1.0` | **跨会话 Semantic 开关 OFF**；**Then** **Prompt 宿主无 **`semanticNarrativeBlock`** **且** **不** **声称跨会话记忆** | **`SC-MEM01`**、[`memory-runtime.md` §9](../../Runtime/memory-runtime.md) |
| **`eval.memory.semantic_preference_persist`** | `0.1.0` | **开关 ON** → **用户明示偏好**（如只看 BTC、简短回复）→ **新 session 续聊** | **`SC-MEM02`**、**同上** |
| **`eval.memory.semantic_no_stale_price`** | `0.1.0` | **Semantic 含关注 BTC** + **新 **`executionId`** 问现价** | **`SC-MEM03`**、**同上** |
| **`eval.memory.semantic_user_revoke`** | `0.1.0` | **用户撤销记忆后再问「你还记得吗」** | **`SC-MEM04`**、**同上** |
| **`eval.memory.semantic_write_no_override`** | `0.1.0` | **Semantic 与类型 A 卡面冲突之写路径** | **`SC-MEM07`**、**同上** |
| **`eval.memory.semantic_write_confirm`** | `0.1.0` | **模糊「记住我」/ symbol 未确认** → **须澄清或确认后写入** | **`SC-MEM08`**、**同上** |
| **`eval.memory.budget_trim`** | `0.1.0` | **超 budget 装配** → **§11 裁剪序 + `memory_trimmed` 观测**；**②④ Facts 仍在** | **`SC-MEM09`**、**§11** |
| **`eval.memory.session_clear_stm`** | `0.1.0` | **多轮后「重新开始」** → **无旧轮注入**；**LTM 块仍在**（**开关 ON**） | **`SC-STM01`/`02`**、[`memory-runtime` §13](../../Runtime/memory-runtime.md) |
| **`eval.memory.stm_write_allowlist`** | `0.1.0` | **装配 Prompt** → **0** **处** **`clarify`/`intent` JSON 原文**、**`routingHints` 原文** **于 messages** | **`SC-STM07`**、[`memory-runtime` §15](../../Runtime/memory-runtime.md) |
| **`eval.memory.stm_l0_window_bound`** | `0.1.0` | **L0 超 turn 上限** → **远端轮不在 messages 或仅 summary** | **`SC-STM08`**、**同上** |
| **`eval.memory.stm_governance_regression`** | `0.3.0` | **生产僵尸澄清链**（**BNB 写澄清 → idle/TTL stale → 你好/只读/放弃**）→ **0 写澄清复读 · 0 内部 routing 词** | **`SC-STM10`**、[`memory-runtime` §16.8](../../Runtime/memory-runtime.md) · [`clarify-telegram` §11](./clarify-telegram.md) |
| **`eval.memory.idle_default_stale`** | `0.1.0` | **idle 后写 clarify → stale** · **「你好」** → **0 写澄清 · 活跃 L1 不含 stale 摘要** | **`SC-STM12`**、[`idle-default-stale.md`](./idle-default-stale.md) |
| **`eval.memory.resume_classifier_gate`** | `0.2.0` | **stale 后显式续单** → **温召回 + Fresh Facts** · **ambiguous「买」→ new** · **「再来一笔」→ need_one_clarify** | **`SC-STM13`**、[`resume-classifier-gate.md`](./resume-classifier-gate.md) |
| **`eval.memory.resume_classifier_multi_episode`** | `0.1.0` | **同 session 两条 stale episode** → **默认 staleAt 最近** · **显式指代可召回旧单** | **`SC-STM13`**、[`resume-classifier-multi-episode.md`](./resume-classifier-multi-episode.md) |
| **`eval.memory.idle_resume_or_new_topic`** | `0.1.0` | **（fallback）`STM_IDLE_DEFAULT_POLICY=prompt_resume_or_new`** · **模糊 inbound** → **可弹 cl:resume/cl:new** | **`SC-STM11`**、[`idle-resume-or-new-topic.md`](./idle-resume-or-new-topic.md) |
| **`eval.memory.stm_vs_ltm_intent`** | `0.1.0` | **「重新开始」走 §2.8**；**「清空记忆」走 §2.7.3** — **不得混意图** | **`SC-STM02`**、**`SC-CH-TG-STM-02`**、[`memory-runtime.md`](./memory-runtime.md) **§4.2** |
| **`eval.memory.obs_trim`** | `0.1.0` | **超 budget 裁剪** → **`agent.context.memory_trimmed`** + **②④ Facts 仍在** | **`SC-OBS10`**、[`memory-runtime.md`](./memory-runtime.md) **§5.1** |
| **`eval.memory.obs_semantic_updated`** | `0.1.0` | **LTM ON · 成功登记偏好** → **`agent.memory.semantic_updated`** **含 **`propositionType`** | **FR-MEM09**、[`memory-runtime.md`](./memory-runtime.md) **§5.2** |
| **`eval.market.ticker_facts_mapping`** | `0.1.0` | **Mock ticker 含 **`last`** → 注入 **`userVisibleMarketData`** **须含 **`lastPrice`**；问现价 **不得** **仅 bid/ask 降级** | **`SC-MRP01`**、[`market-runtime-payload` §3.3](../domains/agent/exchange-agent/market-runtime-payload.md) |
| **`eval.market.narrative_with_facts`** | `0.1.0` | **`marketPhase=sideways` + ticker 闭环** → **锚句+lastPrice/asOf 同窗** | **`SC-MI04`**、[`market-intelligence` §4](../domains/agent/exchange-agent/market-intelligence.md) |
| **`eval.market.narrative_stale_no_phase`** | `0.1.0` | **Facts stale/工具失败** → **不得注入 phase/编造盘感** | **`SC-MI05`**、**同上** |
| **`eval.market.narrative_funding`** | `0.1.0` | **`funding_crowded_long` + fundingRate 闭环** → **须复述费率+锚句** | **`SC-MI06`**、**同上** |
| **`eval.market.narrative_high_volatility`** | `0.1.0` | **`elevated_volatility` + volatility 字段** → **锚句与 Facts 同窗** | **`SC-MI07`**、**同上** |
| **`eval.market.phase_deterministic`** | `0.1.0` | **观测 **`marketPhase`** **须** **∈ §3.2.1**；**hints ≤3 条**；**无未登记 phase** | **`SC-MI08`**、**`FR-MI06`**、[`market-runtime-payload` §3.2.1](../domains/agent/exchange-agent/market-runtime-payload.md) |
| **`eval.market.narrative_obs`** | `0.1.0` | **注入 hints/phase 之 **`executionId`** **须** **有 **`agent.market.phase_computed`** **且 primary ∈ 枚举** | **`SC-OBS09`**、[`market-narrative.md`](./market-narrative.md) **§2.7** |
| **`eval.skill.missing_qty_no_confirm`** | `0.1.0` | 限价 **无数量** → **0** **载货写参** **类型 A**、**0** 写 \| **升格·分层** **`eval.gateway.missing_qty_blocks_*`** | **`SC-TA01`** **方向**、**INV-008**、[`skill-contract.md`](./skill-contract.md) |
| **`eval.gateway.missing_qty_blocks_trade_type_a`** | `0.1.0` | **`quantity`** **与** **`quoteQty`** **均缺**（**或未推断**）；**编排/回归** **强推确认** · **Then** **`0`** **次** **含** **`call_exchange_write`** **拟用字段** **之** **`confirmation`/类型 A** · **不符** **`→ fail`**（**.suite** **`WRITE_PARAMETER_CONTRACT`**） | **INV-008**、[runtime-invariants §0](../Runtime/runtime-invariants.md) |
| **`eval.gateway.missing_qty_blocks_exchange_write`** | `0.1.0` | **空参/缺参** **传入** **Gateway 前** · **Then** **`0`** **笔** **`trading.exchange_private`/`call_exchange_write`** **Ingress 成功**；**须 **`WRITE_PARAMS_INCOMPLETE`** **→ **`FR-T05`** | **INV-008** |
| **`eval.gateway.provenance_fallback_rejected`** | `0.1.0` | **注入** **`quantity.source=fallback_default`**（**或** **`parser_autofill`/`adapter_placeholder`/`llm_inferred_unconfirmed`**）· **Then** **`INVALID_PARAMETER_SOURCE`** **（** **映射** **`FR-T05`** **）** · **`0`** **写** | **INV-009**、**`WRITE_PARAMETER_CONTRACT`** |
| **`eval.gateway.sell_all_without_balance_read_fail`** | `0.1.0` | **话束** **「卖掉全部 BNB」** · **fixture** **禁止** **先于数量落盘** **之** **`runtime_read_balance`** **/ 同窗只读余额事件** · **却** **出现** **非空** **`quantity`** **写参** · **Then** **`fail`** | **INV-010** |
| **`eval.gateway.buy_all_requires_balance_read`** | `0.1.0` | **话束** **「全部买入 BNB」+ 闪兑/市价** · **Then** **须** **观测** **`orchestrationNextSteps`/`slot_fill_read_balance`** **或** **同窗只读余额事件** **先于** **载货类型 A** · **`quoteQty.provenance=runtime_read_balance`** · **用户可见** **0** **处** **`路由|写路径|禁止猜测`** | **INV-010**、[`trade-via-agent` S11.1](../flows/trade-via-agent.md#trade-inv-010-semantic-full-book)、[`clarify-user-visible` §1](../prompts/shared/clarify-user-visible.md) |
| **`eval.clarify.no_internal_jargon`** | `0.2.0` | **写路径澄清轮** · **Then** **用户消息** **不得** 含 **内部词**（**见 §12 denylist**） | [`clarify-user-visible` §1](../prompts/shared/clarify-user-visible.md) · **`SC-CLARIFY-09`** · [`clarify-telegram` §12](./clarify-telegram.md) |
| **`eval.clarify.one_question_per_turn`** | `0.2.0` | **首条写路径澄清** · **Then** **主问句 ≤1**（**或** **二选一按钮 1 组**）；**禁止** **≥3 项 checklist** | [`clarify-user-visible` §6 P2](../prompts/shared/clarify-user-visible.md) · [`clarify-telegram` §13](./clarify-telegram.md) |
| **`eval.clarify.reintent_each_inbound`** | `0.1.0` | **澄清态** **第 2 条 **`message`** **≠** **上轮** · **Then** **观测 Parser/意图重跑**；**outbound** **须** **承接 inbound**（**非** **逐字复读**） | **`SC-CLARIFY-05`**、[`clarify-session` §2.3](../domains/agent/agent-orchestration/clarify-session.md) |
| **`eval.clarify.abandon_on_cancel`** | `0.1.0` | **pending 写澄清** · **用户**「都不要了」· **Then** **`abandoned=true`** · **0** **条** **闪兑/限价** **澄清** | **`SC-CLARIFY-06`**、[`clarify-telegram.md` §7](./clarify-telegram.md) |
| **`eval.clarify.read_interrupts_write`** | `0.1.0` | **澄清态** · **用户**「有哪些币可以买」· **Then** **只读/listing 应答** · **写澄清 abandoned** | **`SC-CLARIFY-07`**、[`clarify-telegram.md` §8](./clarify-telegram.md) |
| **`eval.clarify.no_repeat_outbound`** | `0.1.0` | **连续 2 条 inbound**（**不同语义**）· **Then** **两轮 outbound** **不得** **逐字相同** | **`SC-CLARIFY-08`**、[`clarify-telegram.md` §9](./clarify-telegram.md) |
| **`eval.clarify.greeting_no_write_clarify`** | `0.1.0` | **无写 session** 或 **残留 clarify** · **用户**「你好」· **Then** **寒暄/能力介绍** · **0** **闪兑/限价盘问** | **`SC-CLARIFY-07`**、[`clarify-telegram.md` §10](./clarify-telegram.md) |
| **`eval.telegram.typing_on_inbound`** | `0.1.0` | **`message` inbound** · **Then** **≤300ms** **`sendChatAction(typing)`** **或** **≤1s** **早失败短句**；长路径 **须** **4500ms 续发或进度句** | **`SC-CH-TG-09`**、[`clarify-telegram.md` §2](./clarify-telegram.md) |
| **`eval.telegram.clarify_keyboard_present`** | `0.1.0` | **写澄清二选一** · **Then** **`inline_keyboard`** **同窗语** · **`callback_data` ≤64B** | **`SC-CH-TG-10`**、[`clarify-telegram.md` §3](./clarify-telegram.md) |
| **`eval.telegram.clarify_callback_merges_slots`** | `0.1.0` | **点 `cl:fc`** · **Then** **合并 `resolvedSlotsSoFar`** · **重跑 Resolver** · **保留 BNB/BUY** | **`SC-CH-TG-11`**、[`clarify-session` §4](../domains/agent/agent-orchestration/clarify-session.md) |
| **`eval.telegram.clarify_not_write_confirm`** | `0.1.0` | **澄清键盘** **无** **写确认动词** · **`cl:*` → 0 写** | **`SC-CLARIFY-01`** |
| **`eval.clarify.stm_resolved_slots_injected`** | `0.1.0` | **澄清第 2 轮** · **Then** **STM/Prompt 含 `resolvedSlotsSoFar` 摘要** | **`SC-CLARIFY-03`**、[`clarify-telegram.md` §5](./clarify-telegram.md) |
| **`eval.session.inbound_serial_no_double_parse`** | `0.1.0` | **1s 内连发 2 条不同 text** → **≤1 Parser 链或 coalesce** · **0 矛盾 outbound** | **`SC-AO-09`**、[`session-concurrency.md` §2](./session-concurrency.md) |
| **`eval.session.single_active_write_execution`** | `0.1.0` | **任意时刻** **在途写 execution ≤ `SESSION_MAX_ACTIVE_WRITE_EXECUTIONS`** | **`SC-AO-10`**、[`session-concurrency-policy` §3](../domains/agent/agent-orchestration/session-concurrency-policy.md) |
| **`eval.session.second_write_while_clarify`** | `0.1.0` | **写澄清 active + 新 symbol 写** → **abandon/挡 · 仅 1 活跃写澄清** | **`SC-AO-10`**、[`session-concurrency.md` §5.1](./session-concurrency.md) |
| **`eval.session.second_write_while_confirm`** | `0.1.0` | **类型 A 存活 + 新写** → **0 第二张无关类型 A** | **`SC-AO-10a`**、[`session-concurrency.md` §3](./session-concurrency.md) |
| **`eval.session.new_write_blocked_on_unknown`** | `0.1.0` | **`unknown_pending` + 新写** → **0 新写 · FR-T05 族** | **`SC-AO-10b`**、[`session-concurrency.md` §4](./session-concurrency.md) |
| **`eval.session.amend_chain_blocks_parallel_write`** | `0.1.0` | **逻辑改单 cancel 已发 + 同 symbol 新写** → **挡或 abort 后可写** | **`SC-AO-10c`**、[`session-concurrency.md` §5](./session-concurrency.md) |
| **`eval.session.callback_serial_with_message`** | `0.1.0` | **in-flight message + `cl:*`** → **串行 · 0 lost update** | **`SC-AO-09`**、[`session-concurrency.md` §6](./session-concurrency.md) |
| **`eval.session.read_during_write_clarify`** | `0.1.0` | **写澄清 + 只读问句** → **只读答 + abandoned**（**回归**） | **`SC-CLARIFY-07`**、[`session-concurrency.md` §1](./session-concurrency.md) |
| **`eval.read_clarify.multi_symbol_compare`** | `0.1.0` | **多标的比较** → **收敛后工具+答复** | **`SC-READ-CLARIFY-04`**、[`read-clarify-telegram.md` §2](./read-clarify-telegram.md) |
| **`eval.read_clarify.scope_portfolio_vs_market`** | `0.1.0` | **盈亏 scope 澄清** · **portfolio 须 FR-T02** | **`SC-READ-CLARIFY-06`** |
| **`eval.read_clarify.write_interrupts_read`** | `0.1.0` | **只读澄清 + 写意图** → **abandon 读 · 转写** | **`SC-READ-CLARIFY-02`** |
| **`eval.read_clarify.rc_no_exchange_write`** | `0.1.0` | **`rc:*` → 0 写** | **`SC-READ-CLARIFY-01`** |
| **`eval.read_clarify.monitoring_draft_then_type_a`** | `0.1.0` | **监控草案齐** → **独立类型 A** | **`SC-READ-CLARIFY-07`** |
| **`eval.fallback.llm_timeout_bounded_retry`** | `0.1.0` | **LLM 超时** → **有界 Retry** → **Stop** · **0 假类型 A** | **`SC-RT-FB-01`**、[`fallback-retry-decision-tree.md` §5](./fallback-retry-decision-tree.md) |
| **`eval.fallback.provider_degrade_no_confirm_bypass`** | `0.1.0` | **Provider 5xx** → **降级可观测** · **0 确认门跳过** | **`SC-RT-FB-02`**、[`fallback-policy` §2.2 FB-A2](../Runtime/fallback-policy.md) |
| **`eval.fallback.parse_missing_slot_write_clarify`** | `0.1.0` | **写缺槽** → **Clarify** · **0 write** | **`SC-RT-FB-03`**、[`fallback-retry-decision-tree.md` §3](./fallback-retry-decision-tree.md) |
| **`eval.fallback.parse_missing_slot_read_clarify`** | `0.1.0` | **只读 scope 歧义** → **ReadClarify `rc:*`** | **`SC-RT-FB-04`**、[`fallback-retry-decision-tree.md` §4](./fallback-retry-decision-tree.md) |
| **`eval.fallback.write_504_unknown_no_auto_replay`** | `0.1.0` | **create_order 504** → **unknown_pending** · **0 同参自动重放** | **`SC-RT-FB-05`**、[`fallback-retry-decision-tree.md` §2](./fallback-retry-decision-tree.md) |
| **`eval.fallback.retry_blocks_confirmation_bypass`** | `0.1.0` | **Retry 跳过类型 A 负例** → **blocked** | **`SC-RT-FB-06`**、[`fallback-retry-decision-tree.md` §3](./fallback-retry-decision-tree.md) |
| **`eval.fallback.read_tool_retry_budget_once`** | `0.1.0` | **get_balance Retry** **计一次预算** **≤ 上界** | **`SC-RT-FB-07`**、[`fallback-policy` §2.2 FB-C1](../Runtime/fallback-policy.md) |
| **`eval.unknown.status_query_no_false_success`** | `0.1.0` | **504 后 status_query** → **reconcile/只读有界 · 0 SUCCESS** | **`SC-RISK-07`**、[`unknown-followup-telegram.md` §2](./unknown-followup-telegram.md) |
| **`eval.unknown.new_write_blocked_on_pending`** | `0.1.0` | **unknown_pending + 新写** → **0 写 · FR-T05** | **`SC-RISK-07a`**、**回归** **`eval.session.new_write_blocked_on_unknown`** |
| **`eval.unknown.repeat_submit_no_auto_replay`** | `0.1.0` | **再试一次/再买** → **0 同参 create_order** | **`SC-RISK-07b`**、[`unknown-followup-telegram.md` §3](./unknown-followup-telegram.md) |
| **`eval.unknown.cancel_request_type_a`** | `0.1.0` | **可撤 + 取消** → **类型 A · 0 假撤成功** | **`SC-RISK-07c`** |
| **`eval.unknown.user_reconcile_cooldown`** | `0.1.0` | **连发追问** **≤ cooldown** → **reconcile 有界** | **`SC-RISK-07d`**、[`unknown-followup-telegram.md` §4](./unknown-followup-telegram.md) |
| **`eval.unknown.copy_throttle_no_spam`** | `0.1.0` | **Throttle 窗内** **0 长模板复读** | **`SC-RISK-07e`** |
| **`eval.unknown.read_order_during_pending`** | `0.1.0` | **查挂单** → **只读 + UNKNOWN 提醒** | **`SC-RISK-07`** |
| **`eval.gateway.metadata_normalize_empty_qty_no_default`** | `0.1.0` | **`exchange_metadata_normalize`** **仅** **可做** **tick/step** **舍入** · **负例** **空/缺** **`quantity`** **却** **normalize** **出** **默认经济数量**（**如** **0.01**）· **Then** **`INVALID_PARAMETER_SOURCE`** **或** **`WRITE_PARAMS_INCOMPLETE`** · **`0`** **写** | **INV-008/009** |
| **`eval.skill.margin_double_confirm`** | `0.1.0` | 全仓 **仅一次** ✓ → **0** `margin/order` | **`SC-CH-TG-MARGIN-01`**、**同上** |
| **`eval.skill.amend_cancel_before_order`** | `0.1.0` | 改单：**cancel** 先于 **order** | **`SC-CH-TG-SPOT-06`**、**同上** |

---

## 2. 分卷 · Market Narrative GWT

**构造正文** → [`market-narrative.md`](./market-narrative.md)（**Mock JSON、Bad/Good、最小回归束**）。

## 3. 分卷 · Memory Runtime GWT

**构造正文** → [`memory-runtime.md`](./memory-runtime.md)（**STM/LTM fixture、分流、最小回归束**）。

## 3.1 分卷 · Skill Contract GWT

**构造正文** → [`skill-contract.md`](./skill-contract.md)（**FR-T11 缺槽 / 分流 / 改单序 · P0 回归束**）。

---

## 4. 维护

- **新增行** **须** **增** **`evalSetId`** **并** **不** **复用** **旧 id** **改语义**。  
- **与** **[`README.md`](./README.md) §2** **登记约定** **一致**。

---

**文档版本**：0.2.24 · **维护**：产品 + QA · **本版**：**UNKNOWN 追问 eval 束**。**承** 0.2.23。
