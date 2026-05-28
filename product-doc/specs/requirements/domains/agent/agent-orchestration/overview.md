# Agent Orchestration（编排域）— 总览

**路径**：`specs/requirements/domains/agent/agent-orchestration/`。

**职责**：产品在 **场景键 `scenarioId`、执行链归因、任务/编排状态边界、风险类投放策略、写路径确认顺序、重试与版本冻结** 上的可对签下限；**不写** OpenAPI 字段、**不替代** `exchange-agent` 五域 **Capability** 正文、**不替代** `Runtime/` **平台状态机实现稿**。

**契约开放面 / 首节派工 / 走读缺口**（**P0/P1、A≠B、`runtime-freeze` §3 实现验收**）：[**§0 速链**](../../../closure-remaining.md#closure-remaining-quicklinks) · **[§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)** · [`closure-remaining` §7](../../../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../../../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。

**对上 Coobit 私网 HTTP**：寄存器 **`scenarioId`** 落地读/写出站时，[`routing-engine.md`](routing-engine.md) 与 [`runtime-freeze.md`](runtime-freeze.md) **文首** 写明 **openapi-ai** 默认宿主（须 pin）；契约面同窗 [`integrations/exchange/overview.md`](../../../integrations/exchange/overview.md)、[`design/api`](../../../../design/api.md)、[`agent-coobit-api-allowlist`](../../../integrations/exchange/agent-coobit-api-allowlist.md)。**不**在本总览新开 PATH。

**统一交易语义（Intent→Canonical→Gateway→Adapter）**：[`canonical-trading-model.md`](../../../../design/canonical-trading-model.md)、[`ADR-004`](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../exchange-agent/trade-assistance.md)；[`CC-P1-07`](../../../contract-closure.md#cc-p1-07)；[`requirements-review` §7.5](../../../../../product/requirements-review.md#cc-adr004-review-checklist)；**执行管线落点** [`Runtime/execution` §1 步 7](../../../Runtime/execution.md)、[`goal-and-execution-paths`](goal-and-execution-paths.md)。**同窗 · 架构语言**：[`architecture` §「与通用 Agent 栈之对照」](../../../../design/architecture.md)；[`flow/e2e-closed-loop`](../../../../../flow/e2e-closed-loop.md) **文首「架构语言」**。

---

## 1. 文档结构（本目录唯一入口地图）

| 文件 | 内容 |
|------|------|
| [`overview.md`](overview.md)（本文） | **FR-AO\*** 注册表、**`SC-AO*`** 验收交叉索引、**§6** 占位键对外承诺口径、邻域关系、裁决顺序、本目录版本 |
| [`routing-engine.md`](routing-engine.md) | **`scenarioId` 寄存器**、与 **意图 / 流程** 的路由对签（原 **§5**） |
| [`execution-lifecycle.md`](execution-lifecycle.md) | **`executionId` / 工具链归因**、**§4 单次执行预算（`FR-AO06`）**、与观测域下限（原 **§6.1**） |
| [`state-machine.md`](state-machine.md) | **`taskId` 生命周期与验收**（原 **§6.3**） |
| [`task-scheduler.md`](task-scheduler.md) | **风险类触达频控/合并**、监控/Pull **场景键与调度边界**（原 **§6.2** + **§5.4** 调度面） |
| [`confirmation-flow.md`](confirmation-flow.md) | **写路径步骤序、`SC-TA*`**（原 **§6.4**，与 ADR-001 对签） |
| [`clarify-session.md`](clarify-session.md) | **跨轮澄清 session**、**`cl:*` callback**、**`ClarifySessionSnapshot`**、**与类型 A 边界**（**`SC-CLARIFY-*` / `SC-CH-TG-10～11`**） |
| [`session-concurrency-policy.md`](session-concurrency-policy.md) | **单 session 并发**：**inbound 队列**、**多 execution 优先级**、**D-1 挡新写**、**改单链 in-flight**（**`FR-AO07` · `SC-AO-09～10`**） |
| [`read-clarify-session.md`](read-clarify-session.md) | **只读/监控澄清**：**`ReadClarifySessionSnapshot`**、**`rc:*`**、**与写澄清对称分流**（**`FR-AO08` · `SC-READ-CLARIFY-*`**） |
| [`retry-policy.md`](retry-policy.md) | **编排层未知/超时与重试产品下限**（与 `Runtime`、`design` 分工） |
| [`runtime-freeze.md`](runtime-freeze.md) | **`orchestrationVersion`、DAG 冻结与契约对签** |
| [`boundaries.md`](boundaries.md) | **本编排域非目标、与邻域分工**（**非** [`../exchange-agent/boundaries.md`](../exchange-agent/boundaries.md)） |
| [`implementation-alignment.md`](implementation-alignment.md) | **实现对齐**：术语、真源矩阵、`scenarioId`→flow、**execution §1** 映射、检查单；**§8～§12** **意图/计费/GWT**；**§13** **对外承诺三闸·评审门禁·eval 束** |
| [`goal-and-execution-paths.md`](goal-and-execution-paths.md) | **Goal · 黄金路径 · Golden/Failure/Recovery** **与** **`Runtime` §1 × `flows` 主路径** **映射**；**§5 Goal 七维**（**JV-10**）；**§6 Golden Path 八维**（**JV-11**）；Path-oriented 提要（**不**新增 FR/SC） |

**编号说明**：历史稿 **§5 / §6** 已按上表 **拆入分卷**；外链请改指 **分卷文件名**，避免继续锚到已不存在的 **`overview` §5～§6** 正文。

---

## 2. 功能需求 · `FR-AO*`（条文归宿仍在本总览）

| ID | **产品陈述（摘要）** | **展开与互引** |
|----|----------------------|----------------|
| **FR-AO01** | **写场景**（如 **`trade.spot.limit_order`**）须在 **寄存器** 中登记 **可审计步骤序**（读技能 → 校验/偏离带 → 类型 A → 写 → 摘要 **等**），与流程文对签 | [`confirmation-flow.md`](confirmation-flow.md)、[`routing-engine.md`](routing-engine.md)、[`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md)、[`../telegram/overview.md`](../telegram/overview.md) **§2.5 · 类型 A（§2.5.x）** |
| **FR-AO02** | **单轮主意图 / 槽位** 与 **`scenarioId` 收敛**：**0 或 1** 个主场景；冲突 **澄清** 或 **显式分步**（与 **`FR-T07`** 同窗） | [`routing-engine.md`](routing-engine.md)、[`../exchange-agent/intents.md`](../exchange-agent/intents.md)、[`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) |
| **FR-AO03** | **编排拓扑**：步骤依赖 **不得** 与用户可见承诺 **或** **合规顺序**（类型 A / 读技能 **等**）冲突；细节 **以实现冻结 DAG 为准** | [`runtime-freeze.md`](runtime-freeze.md)、[`confirmation-flow.md`](confirmation-flow.md) |
| **FR-AO04** | **`read_skill_operation_spec`（或等价）先于** **首张类型 A / 交易所写**（与 **`FR-T11`** 同窗） | [`confirmation-flow.md`](confirmation-flow.md)、[`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) |
| **FR-AO05** | **`agent.orchestration.step`（或合并字段）须** 能携带 **`scenarioId` + `orchestrationVersion`**；**禁止** **全链无 `scenarioId`** **却** 已调 **外网 / B 类工具** | [`execution-lifecycle.md`](execution-lifecycle.md)、[`runtime-freeze.md`](runtime-freeze.md)、[`../../observability/overview.md`](../../../observability/overview.md) **§2.1** |
| **FR-AO06** | **同一 `executionId` 内** **须** **工具调用次数、编排步骤（及可选模型回合）** **可配置硬顶**；**超限** **须** **终止 IO 扩张** **与** **`FR-T05` 可解释码**（**`execution-lifecycle` §4**） | [`execution-lifecycle.md`](execution-lifecycle.md) **§4**、[`runtime-contract.md`](../../admin/tool-management/runtime-contract.md) **§3**、[`../../Runtime/execution.md`](../../../Runtime/execution.md) **§1** |
| **FR-AO07** | **同一 `sessionId`** **须** **定义** **inbound 串行/合并策略**、**在途写 execution 数量上限**、**第二笔写/UNKNOWN/类型 A 与改单链** **之** **并发优先级**；**用户可见** **挡新写/排队** **须** **可解释** | [`session-concurrency-policy.md`](session-concurrency-policy.md)、[`clarify-session.md`](clarify-session.md) **§1.1**、[`locking.md`](../../../Runtime/locking.md) **§2**、[`unknown-state.md`](../../../Runtime/unknown-state.md) |
| **FR-AO08** | **只读/分析/监控草案** **跨轮澄清** **须** **轻量 **`ReadClarifySessionSnapshot`**、**`rc:*` 键盘** **与** **写路径 **`ClarifySession`** **分流**；**转写意图** **须** **abandon 读澄清** | [`read-clarify-session.md`](read-clarify-session.md)、[`read-analyze-and-search-via-agent.md`](../../../flows/read-analyze-and-search-via-agent.md) **S2**、[`clarify-session.md`](clarify-session.md) **§2.3** |

---

## 3. 验收 · `SC-AO*`（编排交叉索引）

本条 **不** 重复邻域正文中的 **Given/When/Then**；**抽检时** 按下列 **主宿主** 执行，**并** 以 **`FR-AO*`** 为编排侧归因。

| ID | **主题（摘要）** | **同窗 `FR-AO`** | **主宿主（细则 / 抽检口径）** |
|----|------------------|-------------------|-------------------------------|
| **SC-AO-01** | 写路径 **步骤序** 与 **寄存器** **一致** | **FR-AO01** | [`confirmation-flow.md`](confirmation-flow.md)、[`routing-engine.md`](routing-engine.md)；**卡面/确认 · §2.5.x** → [`../telegram/overview.md`](../telegram/overview.md)、[`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **`SC-TA01`/`SC-TA02`** |
| **SC-AO-02** | 单轮主 **`scenarioId`** 收敛（澄清 / 分步） | **FR-AO02** | [`routing-engine.md`](routing-engine.md)、[`../exchange-agent/intents.md`](../exchange-agent/intents.md)、[`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) |
| **SC-AO-03** | **DAG / 拓扑** **不** **绕过** **合规门** | **FR-AO03** | [`runtime-freeze.md`](runtime-freeze.md)、[`confirmation-flow.md`](confirmation-flow.md) |
| **SC-AO-04** | **读技能** **先于** **类型 A / 交易所写** | **FR-AO04** | [`confirmation-flow.md`](confirmation-flow.md)、[`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **`FR-T11`** |
| **SC-AO-05** | 工具链须可携带 **`scenarioId` + `orchestrationVersion`**；禁止无 **`scenarioId`** 却调外网 / B 类工具 | **FR-AO05** | [`execution-lifecycle.md`](execution-lifecycle.md)、[`../../observability/overview.md`](../../../observability/overview.md) **§2.1** |
| **SC-AO-06** | **重试** **不** **跳过** **确认/读技能**；**跨步** **可追版** | **FR-AO03**（门闩）+ **FR-AO05**（追踪） | [`retry-policy.md`](retry-policy.md)、[`confirmation-flow.md`](confirmation-flow.md)、[`execution-lifecycle.md`](execution-lifecycle.md) |
| **SC-AO-07** | **监控/Pull / `taskId`** **与** **契约 §1·5** **对签** | **FR-AO01～05** **在** **自动化混编** **场景** **之适用条** | [`task-scheduler.md`](task-scheduler.md)、[`state-machine.md`](state-machine.md)、[`../../flows/automation-alerts.md`](../../../flows/automation-alerts.md)、[`../../contract-closure.md`](../../../contract-closure.md) **§1** **第 5 款** |
| **SC-AO-08** | **执行预算顶** **可测**：逼近/突破 **工具或步骤** **配置上限** **时** **须** **稳定终止 + 用户可解释 + 可观测** | **FR-AO06** | [`execution-lifecycle.md`](execution-lifecycle.md) **§4**、[`../../observability/overview.md`](../../../observability/overview.md) **§4 `SC-OBS07`** |
| **SC-AO-09** | **inbound 串行/合并**：**连发/callback 与 message** **不得** **双 Parser 链** **致** **出站矛盾** | **FR-AO07** | [`session-concurrency-policy.md`](session-concurrency-policy.md) **§2**、[`evals/session-concurrency.md`](../../../evals/session-concurrency.md) |
| **SC-AO-10** | **在途写 execution ≤ 上限**；**第二笔写/UNKNOWN/类型 A/改单链** **按优先级表** **挡或终局前单** | **FR-AO07** | [`session-concurrency-policy.md`](session-concurrency-policy.md) **§3～§6**、**`SC-AO-10a～c`** |
| **SC-AO-11** | **只读澄清 **`rc:*`** **不触发写**；**写意图 inbound** **须** **abandon 读 session** | **FR-AO08** | [`read-clarify-session.md`](read-clarify-session.md)、[`evals/read-clarify-telegram.md`](../../../evals/read-clarify-telegram.md) |

---

## 4. 与邻域关系（裁决顺序 · 摘要）

1. **用户价值与五种 pillar 能力语义** → [`../exchange-agent/overview.md`](../exchange-agent/overview.md) 及分卷。  
2. **逐步骤剧本**（S{n}、分支）→ [`../../flows/`](../../../flows/README.md)。  
3. **PATH / 矩阵能否落地** → [`../../../design/api.md`](../../../../design/api.md)。  
4. **`agent.tool.call` / `executionId` / `invocationState` / 主态边观测** → [`../../observability/overview.md`](../../../observability/overview.md) **§2～§2.4**（**`transitionTrigger` · `SC-OBS08`**）；**逐边契约** [`../../../Runtime/execution-transition-matrix.md`](../../../Runtime/execution-transition-matrix.md) **§2.2**。  
5. **平台级队列、重试、D-1** → [`../../../Runtime/execution.md`](../../../Runtime/execution.md)、[`../../../Runtime/recovery.md`](../../../Runtime/recovery.md)、[`../../../Runtime/overview.md`](../../../Runtime/overview.md) + 本文 [`retry-policy.md`](retry-policy.md)。  
6. **Telegram**：**类型 A** 卡面条目 **§2.5.x**；**总则 §2～§2.6**（渠道闸、Bot API、Deeplink **等**）→ [`../telegram/overview.md`](../telegram/overview.md)。

完整边界表见 [`boundaries.md`](boundaries.md)。

---

## 5. 入口链（Speckit / 人类）

- **聚合**：[`../../spec.md`](../../../spec.md)、[`../../product.md`](../../../product.md)、[`../../contract-closure.md`](../../../contract-closure.md)（**§1.2** **与** [`implementation-alignment.md`](implementation-alignment.md) **§13** **同窗**）  
- **Capability**：[`../exchange-agent/overview.md`](../exchange-agent/overview.md)  
- **实现对齐（研发 / Code Review）**：[`implementation-alignment.md`](implementation-alignment.md) · **[`goal-and-execution-paths.md`](goal-and-execution-paths.md)**（Goal/三种路径/§1×flow）  
- **旧 §10 映射**：[`../exchange-agent/overview-legacy-migration.md`](../exchange-agent/overview-legacy-migration.md)  

---

## 6. 寄存器占位键与对外承诺（P0 口径）

[`routing-engine.md`](routing-engine.md) 中 **曾标注占位** 的 **`scenarioId`**（**现** **以** **`research.sentiment_and_news`、`monitoring.event_trigger`** **为** **v0.1 稳定键**）：**仍须** 与 **[`flows/`](../../../flows/README.md)**、[`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **`§8`** **同窗 MR** **后**，方可按 [`../../contract-closure.md`](../../../contract-closure.md) **视为可对外承诺之能力** — **矩阵 PATH / 工具未齐** **前** **不得** **单独** **标为**「已闭环」。**在此之前**，**不得** 将上述键 **在无矩阵依据时** 标为「已支持」。**现货** **`trade.spot.oco` / `trade.spot.bracket`** **见** [`routing-engine.md`](routing-engine.md) **§2** — **子账户矩阵 PATH 书面延期未解冻前** **适用** **本条** **不单独承诺** **口径**。

---

**文档版本**：1.4.9 · **维护**：产品 + Agent Runtime owner · **本版**：**FR-AO08 · read-clarify-session · SC-AO-11**。承 1.4.8。
