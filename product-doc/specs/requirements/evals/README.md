# Evals（评测素材与场景索引）

**职责**：存放 **可执行评测 / 回归 / 抽检** 所需的 **场景、用例集、数据集版本** 的 **登记与导航**。**不**替代各 **`domains/`** 之 **FR/SC SSOT**；**不**替代 **[`../metrics/README.md`](../metrics/README.md)**（阈值、SLI、验收条目索引）。

---

## 1. 与 `metrics/` 的分工

| 路径 | 角色 |
|------|------|
| **`metrics/`** | **验收标准与指标命名**：成功率 ≥ *X*%、`SC-*` 指针、控制台 SLI 下限等 |
| **`evals/`**（本文） | **验证该标准所用的素材**：golden 对话、异常注入、504/UNKNOWN 回放、工具循环压力、确认链负例等 |

**原则**：**指标定义一处真源**（域文或 `metrics/` 索引）；**评测用例**在此 **列目录 / 版本 / 映射到哪条 `SC-*` 或业务流**，避免在 `metrics/` 里堆长用例正文。

---

## 2. 登记约定（V1）

1. **每条评测集** **须** **有** **唯一 `evalSetId`**（所内命名规范由 **`design`/运营** **冻结**）与 **版本号**（与 Prompt 包 / `orchestrationVersion` **可对签之日** **任选其一** **作为主版本轴** — **`design` 冻结**）。  
2. **映射**：在素材登记表（本目录后续 `.md` 表或所内仓库）**须** **能** **指向** **至少一条** **`SC-*`** **或** **[`../flows/`](../flows/README.md)** **流程文** **之** **抽检口径**。  
3. **回测 / 离线**：若使用 **历史行情或脱敏日志**，**合规与留存** **须** **与** [`../observability/overview.md`](../observability/overview.md)、[`../domains/admin/management-console-v1-prd.md`](../domains/admin/management-console-v1-prd.md) **同窗**。  
4. **异常与资金安全**：**须** **含** **预算顶**（[`../domains/agent/agent-orchestration/execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4**）、**确认链绕过负例**（[`../risk/user-confirmation.md`](../risk/user-confirmation.md)）、**高危二次确认**（[`../prompts/confirmation/high-risk-confirmation.md`](../prompts/confirmation/high-risk-confirmation.md)）**之** **可构造子集** — **具体条目** **随首版登记 MR** **补齐**。

---

## 3. 分卷

| 文件 | 用途 |
|------|------|
| [`scenarios.md`](scenarios.md) | **`evalSetId` 草案**、**构造要点** **与 **`SC-*`** **映射**；**[`eval.gateway.*`](scenarios.md)** **负例** **`WRITE_PARAMETER_CONTRACT`**；**编排** **最小回归束** → [`implementation-alignment` §13.3](../domains/agent/agent-orchestration/implementation-alignment.md)；**写路径 §3 下限** **与** **JV-07** **总检入口** → [§0 速链](../closure-remaining.md#closure-remaining-quicklinks) · [§6～§6.4](../closure-remaining.md#cc-exec-solve-path) · [`closure-remaining` §7](../closure-remaining.md#cc-remaining-open-items) **·** **[§7.1](../closure-remaining.md#cc-remaining-gap-paste)** **·** **[§7.5](../closure-remaining.md#cc-remaining-open-close-path)** **·** **[§7.6](../closure-remaining.md#cc-closure-exec-checklist)**；**主态×时间线** **`eval.obs.timeline_transition_contract`** ↔ **`SC-OBS08`**；**用户阶段话术** **`eval.runtime.user_visible_phase_copy`**、**槽位澄清** **`eval.trade.slot_quote_base_clarify`** → **JV-12**；**上下文隔离** **`eval.context.*`** → [`Runtime/context-management` §2](../Runtime/context-management.md) |
| [`clarify-telegram.md`](clarify-telegram.md) | **Telegram 澄清 GWT**：**typing**、**键盘**、**callback**、**STM**、**abandon/read-interrupt/no-repeat/greeting** — **SSOT** [`clarify-session.md`](../domains/agent/agent-orchestration/clarify-session.md) · **`SC-CLARIFY-05～09`** |
| [`session-concurrency.md`](session-concurrency.md) | **`eval.session.*` GWT** · **inbound 队列**、**多 execution**、**D-1**、**改单链** — **SSOT** [`session-concurrency-policy.md`](../domains/agent/agent-orchestration/session-concurrency-policy.md) · **`SC-AO-09～10`** |
| [`read-clarify-telegram.md`](read-clarify-telegram.md) | **`eval.read_clarify.*` GWT** · **只读澄清 · `rc:*`** — **SSOT** [`read-clarify-session.md`](../domains/agent/agent-orchestration/read-clarify-session.md) · **`SC-READ-CLARIFY-*`** |
| [`fallback-retry-decision-tree.md`](fallback-retry-decision-tree.md) | **`eval.fallback.*` GWT** · **Retry/Fallback/Reconcile/Stop 场景树** — **SSOT** [`fallback-policy.md`](../Runtime/fallback-policy.md) **§2** · **`SC-RT-FB-*`** |
| [`unknown-followup-telegram.md`](unknown-followup-telegram.md) | **`eval.unknown.*` GWT** · **504 后用户追问** — **SSOT** [`unknown-stall-policy.md`](../risk/unknown-stall-policy.md) **§2** · **`SC-RISK-07*`** |
| [`fallback-retry-decision-tree.md`](fallback-retry-decision-tree.md) | **`eval.fallback.*` GWT** · **Retry/Fallback/Reconcile/Stop 决策树** — **SSOT** [`fallback-policy` §2](../Runtime/fallback-policy.md) · **`SC-RT-FB-*`** |
| [`market-narrative.md`](market-narrative.md) | **`eval.market.*` GWT**、Mock 基线、Bad/Good — **MNRA** [`market-narrative-runtime/README`](../market-narrative-runtime/README.md)、[`scenario-matrix`](../market-narrative-runtime/scenario-matrix.md)；FR [`market-intelligence` §4](../domains/agent/exchange-agent/market-intelligence.md) |
| [`idle-default-stale.md`](idle-default-stale.md) | **`eval.memory.idle_default_stale`** · **`SC-STM12`** |
| [`resume-classifier-gate.md`](resume-classifier-gate.md) | **`eval.memory.resume_classifier_gate`** · **`need_one_clarify`** · **`SC-STM13`** |
| [`resume-classifier-multi-episode.md`](resume-classifier-multi-episode.md) | **`eval.memory.resume_classifier_multi_episode`** · **温索引多条** · **`SC-STM13`** |
| [`idle-resume-or-new-topic.md`](idle-resume-or-new-topic.md) | **`eval.memory.idle_resume_or_new_topic`** · **fallback only** · **`SC-STM11`** |
| [`memory-runtime.md`](memory-runtime.md) | **`eval.memory.*` GWT**、STM/LTM fixture、**四原则/僵尸澄清回归**、**STM vs LTM 分流**、**P0/P1 回归束** — **同窗** [`memory-runtime` §9～§16](../Runtime/memory-runtime.md) · **CI 登记** [`design/memory-runtime-injection` §7](../../design/memory-runtime-injection.md) |
| [`skill-contract.md`](skill-contract.md) | **`eval.skill.*`** — **FR-T11** 缺槽/分流/双确认/逻辑改单序；映射 **S-01～S-09 + amend**；**需求层** 已闭合 → [`skill-specs/requirements-closure` §3](../skill-specs/requirements-closure.md#3-需求层-dod-a-阶段--可勾选) · **B** 真跑 → 同文 **§4 SK-B03** |
| [`pipeline-write-order.md`](pipeline-write-order.md) | **`eval.runtime.pipeline_write_order`** · **五段序**；**负例** **P-N4～P7** — **同窗** **`eval.gateway.*`**；走读 [`pipeline-walkthrough-checklist`](../Runtime/pipeline-walkthrough-checklist.md)；Mock **`mock.timeline.contract.test.ts`** |
| **本仓库 · Demo 门卫** | `src/admin`（Vitest）：**`npm test`** — **`mock.timeline.contract.test.ts`**（**SC-OBS08** + **`eval.runtime.pipeline_write_order`**）· **`skillContract.contract.test.ts`**（**`eval.skill.*` P0**） |
| [`../../../product/journey-validation.md`](../../../product/journey-validation.md) | **端到端用户旅程正式验证**：Given/When/Then、门禁分层、`eval.product.user_journey_chain` |
| [`skill-contract.md`](skill-contract.md) | 写路径 **Skill Contract** — **见上** |
| *（待增）* | 交易 / 理财 **按 `scenarioId` 扩面** — **MNRA** → [`market-narrative.md`](market-narrative.md) |

---

## 4. 上级索引

[`../README.md`](../README.md) · [**PRS 总入口 · 改什么去哪** `../prompt-runtime/README.md#prs-where-to-edit`](../prompt-runtime/README.md#prs-where-to-edit) · [`../spec.md`](../spec.md) · [`../metrics/README.md`](../metrics/README.md) · [`../risk/README.md`](../risk/README.md)

---

---

## 5. Memory · P0 回归束与 CI 登记（需求层 · 2026-05-27）

**用途**：**所内 Agent Runtime / Telegram BFF CI** **须** **引用** **下列 **`evalSetId`**（**GWT** **见** [`memory-runtime.md`](memory-runtime.md) · [`clarify-telegram.md`](clarify-telegram.md) · [`session-concurrency.md`](session-concurrency.md)）— **本仓** **仅登记** **不实现 Runner**。

| **优先级** | **`evalSetId`** | **SC** |
|------------|-----------------|--------|
| **P0** | **`eval.memory.stm_governance_regression`** | **`SC-STM10`** |
| **P0** | **`eval.memory.idle_default_stale`** | **`SC-STM12`** |
| **P0** | **`eval.memory.resume_classifier_gate`** | **`SC-STM13`** |
| **P0** | **`eval.clarify.reintent_each_inbound`** | **`SC-CLARIFY-05`** |
| **P0** | **`eval.clarify.abandon_on_cancel`** | **`SC-CLARIFY-06`** |
| **P0** | **`eval.clarify.read_interrupts_write`** | **`SC-CLARIFY-07`** |
| **P0** | **`eval.session.inbound_serial_no_double_parse`** | **`SC-AO-09`** |
| **P0** | **`eval.session.second_write_while_confirm`** | **`SC-AO-10a`** |
| **P0** | **`eval.session.new_write_blocked_on_unknown`** | **`SC-AO-10b`** |
| **P1** | **`eval.read_clarify.write_interrupts_read`** | **`SC-READ-CLARIFY-02`** |
| **P1** | **`eval.read_clarify.scope_portfolio_vs_market`** | **`SC-READ-CLARIFY-06`** |
| **P1** | **`eval.fallback.write_504_unknown_no_auto_replay`** | **`SC-RT-FB-05`** |
| **P1** | **`eval.fallback.retry_blocks_confirmation_bypass`** | **`SC-RT-FB-06`** |
| **P1** | **`eval.unknown.status_query_no_false_success`** | **`SC-RISK-07`** |
| **P1** | **`eval.unknown.new_write_blocked_on_pending`** | **`SC-RISK-07a`** |
| **P1** | **`eval.memory.stm_write_allowlist`** | **`SC-STM07`** |
| **P1** | **`eval.memory.idle_resume_or_new_topic`** | **`SC-STM11`**（**fallback policy only**） |

**关单**：[`closure-remaining` OP-MEM](../closure-remaining.md#cc-remaining-open-close-path) · **设计** [`memory-runtime-injection` §7](../../design/memory-runtime-injection.md)。

---

**文档版本**：0.2.11 · **维护**：产品 + QA / Agent Runtime owner · **本版**：**UNKNOWN 追问 eval 分卷**。**承** 0.2.10。
