# Goal · 黄金路径 · 执行路径（Path-oriented 提要）

**路径**：`specs/requirements/domains/agent/agent-orchestration/goal-and-execution-paths.md`。

**职责**：把 **用户 Goal（目标）**、**黄金路径（Golden / Happy Path）**、**失败路径** 与 **恢复路径** **拴在同一叙事**里；**§5** **Goal** **七维**；**§6** **Golden Path** **八维**（**起点/任务链/依赖/I-O/失败/恢复/人工/结束态**）；并 **显式链** **[`Runtime/execution.md`](../../../Runtime/execution.md) §1** **与** **`flows/`** **主路径**。**结构化 Goal 范例（非契约）** → [`../goals/README.md`](../goals/README.md)。**不**新增 FR/SC 编号；**不**替代 **[`intents.md`](../exchange-agent/intents.md)**、**[`routing-engine.md`](routing-engine.md)**、**各 `flows/*.md`** 正文。**契约与验收**仍以 **`specs/requirements`** **与** **`design/`** **为准**。

**同窗**：[`overview.md`](overview.md) **FR-AO02**；[`implementation-alignment.md`](implementation-alignment.md) **§8～§12**；[`execution-lifecycle.md`](execution-lifecycle.md) **§5**；[`Runtime/execution.md`](../../../Runtime/execution.md) **§1 步 7 / 附录 A**；[`Runtime/runtime-truth-source-map.md`](../../../Runtime/runtime-truth-source-map.md)；[`flow/e2e-closed-loop.md`](../../../../../flow/e2e-closed-loop.md) **（文首「架构语言」）**；[`architecture` §「与通用 Agent 栈之对照」](../../../../design/architecture.md)；[`canonical-trading-model.md`](../../../../design/canonical-trading-model.md)、[`ADR-004`](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)；[`CC-P1-07`](../../../contract-closure.md#cc-p1-07)；[`requirements-review` §7.5](../../../../../product/requirements-review.md#cc-adr004-review-checklist)；**开放面 / 走读缺口** [`closure-remaining` §7](../../../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../../../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。

---

## 1. Goal（用户目标）— 需求层含义

| 层次 | **含义（摘要）** | **权威落点** |
|------|------------------|--------------|
| **语义簇（话怎么说）** | **自然语言簇**、**pillar**、**歧义分流** | [`intents.md`](../exchange-agent/intents.md) **§1～§3** |
| **路由键（跑哪条能力）** | **单轮** **0 或 1** 个主 **`scenarioId`**；寄存器 **SSOT** | [`routing-engine.md`](routing-engine.md)；**FR-AO02** · [`overview.md`](overview.md) |
| **结构化草案（实现下限）** | **槽位/草案** **字段** **与** **门禁顺序** **可对签** | [`implementation-alignment.md`](implementation-alignment.md) **§8**（**意图草案**） |

**产品约定**：本文 **「Goal」** **=** **用户在一次交互或短会话中要达成的业务结果**，**先** **经** **`intents`** **语义** **归类**，**再** **收敛为** **`routing-engine`** **登记键** **（若适用）**，**最后** **落入** **某条** **`flows/*.md`** **主路径** **与** **[`execution.md`](../../../Runtime/execution.md) §1** **管线步**。**不得** **把** **`scenarioId`** **与** **用户原句** **混为** **同一对象** **不交代** **收敛过程**（**SC-AO-02** 方向）。

**复合型会话**：**多回合** **切换** **意图** **时** **须** **保** **`sessionId`/`executionId`** **归因清晰** — [`sessions.md`](../../../Runtime/sessions.md)、[`context-management.md`](../../../Runtime/context-management.md) **§2**、[`consume-and-bill.md`](../../../flows/consume-and-bill.md)、[`session-concurrency-policy.md`](session-concurrency-policy.md) **（P0 · inbound 队列 · 多 execution 优先级）**。

---

## 2. 三种执行路径（Golden · Failure · Recovery）

**为何 Agent 侧必须写清**：编排 **非确定性** **与** **工具/模型** **可** **多重选择**；**若无** **标准轨迹** **与** **成对失败/恢复叙事**，则 **同类输入** **易出现** **行为漂移**、**工具不一致** **与** **验收** **不可比**。**治理抓手** **同窗** **FR-AO06**（预算顶）、**[`runtime-freeze.md`](runtime-freeze.md)**（DAG/版本）、**工具/技能登记**（[`trade-assistance.md`](../exchange-agent/trade-assistance.md)）。

| **路径类型** | **需求含义** | **条文与流程宿主（索引）** |
|--------------|--------------|---------------------------|
| **Golden Path** | **理想情况下** **平台** **应** **完成的** **`Runtime` §1** **顺序** **与** **业务** **`flows` 主路径（Happy path）** **步骤** **之** **可对齐组合** | [`execution.md`](../../../Runtime/execution.md) **§1**；[`business-process-standard.md`](../../../standards/business-process-standard.md) **§2**；**全键九步增量** [**`e2e#runtime-walkthrough-scenarios`**](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough-scenarios)；**写范例** [**`e2e#runtime-walkthrough`**](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough)（**`trade.spot.flash_convert`**） |
| **Failure Path** | **异常/拒答/超时/终局不明** **时** **用户可见语义**、**可观测原因**、**不** **伪造成交/静默写** | [`unknown-state.md`](../../../Runtime/unknown-state.md)、[`error-normalization.md`](../../../Runtime/error-normalization.md)、[`billing-management/flow.md`](../../admin/billing-management/flow.md) **失败路径**、[`kill-switch.md`](../../../risk/kill-switch.md)、**JV-06** · [`journey-validation.md`](../../../../../product/journey-validation.md)、[`eval.obs.504_unknown_write`](../../../evals/scenarios.md)；**编排绕过确认** **`eval.hitl.write_without_confirm`** |
| **Recovery Path** | **重试、退避、降级、对账补救** **与** **可恢复落盘** **之** **平台下限**（**不** **削弱** **写前确认**） | [`recovery.md`](../../../Runtime/recovery.md)、[`fallback-policy.md`](../../../Runtime/fallback-policy.md)、[`reconciliation.md`](../../../Runtime/reconciliation.md)、[`persistence.md`](../../../Runtime/persistence.md)；**控制台** **Recovery** **占位** · [`admin-console/runtime-to-ui-mapping.md`](../../../admin-console/runtime-to-ui-mapping.md) |

**HITL / 人工门**（**与 Golden 并列的「门禁型」路径**）：**类型 A**、**高危二次确认** — [ADR-001](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)、[`confirmation-flow.md`](confirmation-flow.md)、[`risk/hitl-and-automation-matrix.md`](../../../risk/hitl-and-automation-matrix.md)。

---

## 3. `Runtime/execution.md` §1 × `flows/` 主路径 — 映射模板

**用途**：评审 **`flows/*.md`** **时** **须** **能** **标明** **各 **S{n}** **主要** **落在** **§1** **哪几步**（**一步** **可** **对应** **多** **S** **或** **跨步异步**）；**避免** **只** **写** **业务步** **而** **无** **Runtime** **归因**。

| **`execution.md` §1 步** | **`flows/` 主路径常见落点（示意）** |
|---------------------------|--------------------------------------|
| **1 接入与归因** | 渠道触达、**`Update`** **入队**、**绑定/会话** **摘要** |
| **2 有效配置快照** | **前置条件** **命中** **`configVersion`/`FEATURE_*`/运维闸** |
| **3 起票 `executionId`** | **进入** **可计费/可归因** **执行单元**（**S** **或** **子阶段** **与** **FR-T01** **对齐**） |
| **4 编排与 Planner** | **意图收敛**、**`scenarioId`**、**编排步/工具选型**（**FR-AO06** **预算**） |
| **5 上下文装配** | **Prompt/上下文** **装配** **与** **工具回填** **隔离** |
| **6 确认门** | **类型 A**、**卡片** **与** **ADR-001**（**读路径** **常** **跳过** **交易写确认**） |
| **7 工具与外部调用** | **`call_exchange_write`** **或** **只读/API** **调用**、**504/UNKNOWN**；**统一交易语义文档链**（Intent→Canonical→Gateway）见 [`execution.md`](../../../Runtime/execution.md) **§1 步 7**、[`canonical-trading-model.md`](../../../../design/canonical-trading-model.md)、[`ADR-004`](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`CC-P1-07`](../../../contract-closure.md#cc-p1-07) |
| **8 终局与计费** | **accepted/可计费**、**`consume-and-bill`** **同窗** |
| **9 观测与留存** | **日志/指标/审计** **键** **与** **协查** |

**写路径 Golden Path 范例**（**密参照**）：[`e2e#runtime-walkthrough`](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough) **九步 Then 表**。

---

<a id="goal-seven-dimensions"></a>

## 5. Goal 七维检视（明确 · 可执行 · 可衡量 · 约束 · 终止 · 失败 · 重规划）

**用途**：对 **任一** 拟 **落地** **或** **对外承诺** **的 Goal**（**用户业务结果** / **`scenarioId`** **族**）做 **最小七问**；**不**替代 **逐条 FR/SC**。**执行性抽检** **宿主**：[`journey-validation.md`](../../../../../product/journey-validation.md) **JV-10**。

| **#** | **维度** | **须能回答（检视问题）** | **需求落点（索引）** | **Pass 口径（Then，摘要）** |
|-------|----------|-------------------------|----------------------|-----------------------------|
| **1** | **明确** | 用户 **要什么**？**与** **哪条** **pillar / 主 **`scenarioId`** **一致**？**歧义** **如何** **消解**？ | [`intents.md`](../exchange-agent/intents.md)；[`routing-engine.md`](routing-engine.md)；**FR-AO02** · [`overview.md`](overview.md)；[`implementation-alignment.md`](implementation-alignment.md) **§8** | **单轮** **主 **`scenarioId` ≤1**** **或** **可见** **澄清 / 分步**；**禁止** **无登记键** **冒充已支持** **而** **落写** |
| **2** | **可执行** | **在** **所内** **PATH / 技能 / 门禁** **下** **能否** **合法走通**？**是否** **`contract-closure`** **已闭环**？ | [`design/api.md`](../../../../design/api.md)；[`trade-assistance.md`](../exchange-agent/trade-assistance.md)；[`contract-closure.md`](../../../contract-closure.md)；**FR-T02**/**FR-T11** **等** | **矩阵或技能未冻** **→** **仅** **TBD/占位** **口径** **与** **`routing-engine` §占位** **一致**；**实现** **不** **越权假开** |
| **3** | **可衡量** | **观测/账务** **上** **如何** **判定** **「达成 / 未达成 / 未知** **」**？ | [`observability/overview.md`](../../../observability/overview.md)；[`consume-and-bill.md`](../../../flows/consume-and-bill.md)；**FR-T01**、**SC-AO-05** | **`executionId`**（**及** **`traceKey`/`billingTraceId`** **若适用**）**可调取**；**终局与计费** **可** **join** **本 Goal** **对应键** |
| **4** | **约束** | **预算、风控、FEATURE、VIP、Kill/Pause、合规** **如何** **收紧** **本 Goal**？ | **FR-AO06** · [`execution-lifecycle.md`](execution-lifecycle.md) **§4**；[`kill-switch.md`](../../../risk/kill-switch.md)；[`access-control/overview.md`](../../admin/access-control/overview.md)、[`eligibility-runtime.md`](../../admin/access-control/eligibility-runtime.md)；[`boundaries.md`](../exchange-agent/boundaries.md)；[`trading-agent-config/flow.md`](../../admin/trading-agent-config/flow.md) | **命中** **硬约束** **→** **`FR-T05`** **可解释** **阻断** **或** **合规降级** **符合** [`fallback-policy.md`](../../../Runtime/fallback-policy.md) **（** **不** **削弱** **写前确认** **）** |
| **5** | **终止条件** | **本条** **可归因执行** **何时** **算** **结束**（**含** **未知终局**）？**计费** **触发/不触发** **边界**？ | [`execution.md`](../../../Runtime/execution.md) **§1 步 8**；[`unknown-state.md`](../../../Runtime/unknown-state.md)；[`billing-management/overview.md`](../../admin/billing-management/overview.md) **`PER_EXECUTION_FINAL`** **叙事**；[`state-machine.md`](state-machine.md)（**`taskId`** **族**） | **用户可见终局语义** **与** **账务/观测** **无** **结构性** **矛盾**（**含** **504/UNKNOWN**） |
| **6** | **支持失败** | **失败 / 拒答 / 部分成功** **时** **用户** **与** **运维** **分别** **看到** **什么**？ | **§2 Failure Path**；[`error-normalization.md`](../../../Runtime/error-normalization.md)；**JV-06** · [`journey-validation.md`](../../../../../product/journey-validation.md)；[`billing-management/flow.md`](../../admin/billing-management/flow.md) **失败路径** | **不** **静默成功**、**不** **伪造成交**；**稳定原因** **上** **屏** **或** **摘要** **可协查** |
| **7** | **支持重规划** | **用户改口**、**澄清后换 `scenarioId`**、**重试/换轨** **时** **如何** **不落** **无界循环**、**归因** **仍** **清**？ | **FR-AO02** **澄清/分步**；[`retry-policy.md`](retry-policy.md)；[`recovery.md`](../../../Runtime/recovery.md)；[`context-management.md`](../../../Runtime/context-management.md) **§2**；**新** **`executionId`** **起票** **同窗** **FR-T01** | **单** **`executionId`** **内** **遵守** **DAG/预算**（**FR-AO06**）；**换 Goal** **须** **可见** **新收敛** **或** **新票** **（** **不得** **静默串意图** **污染** **确认链** **）** |

---

<a id="golden-path-eight-dimensions"></a>

## 6. 黄金路径八维检视（起点 · 任务链 · 依赖 · I/O · 失败 · 恢复 · 人工 · 结束态）

**用途**：对 **本条** **`scenarioId` / `flows` 主路径** **所描述** **的 Golden Path**（**理想执行轨迹**）做 **最小八问**；**与** **§3**（**§1×flow**）**及** **[`e2e` Walkthrough](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough)** **同窗**。**抽检宿主**：[`journey-validation.md`](../../../../../product/journey-validation.md) **JV-11**。

| **#** | **维度** | **须能回答（检视问题）** | **需求落点（索引）** | **Pass 口径（Then，摘要）** |
|-------|----------|-------------------------|----------------------|-----------------------------|
| **1** | **完整起点** | **用户/渠道** **从** **何种** **状态** **进入** **本路径**（**绑定、VIP、配置快照、会话**）？ | [`execution.md`](../../../Runtime/execution.md) **§1 步 1～2**；[`e2e-closed-loop.md`](../../../../../flow/e2e-closed-loop.md) **阶段 A～E**；各 **`flows/*.md`** **前置条件** | **文内** **或** **互引** **可拼出** **无断点** **准入**；**不得** **默认** **已绑定** **而不写** |
| **2** | **完整任务链** | **主路径** **S1…Sn** **或** **`Runtime` §1** **是否** **覆盖** **从** **触达到** **终局/摘要**？ | [`business-process-standard.md`](../../../standards/business-process-standard.md) **§2**；[`confirmation-flow.md`](confirmation-flow.md)；**[`e2e#runtime-walkthrough-scenarios`](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough-scenarios)** | **链** **可与** **九步/索引** **对齐**；**缺步** **须** **标** **TBD** **+** **`contract-closure`** |
| **3** | **依赖关系** | **读技能→类型 A→写**、**门禁** **与** **编排** **拓扑** **谁先谁后**？ | **FR-AO01～AO04** · [`overview.md`](overview.md)；[`runtime-freeze.md`](runtime-freeze.md)；[`trade-assistance.md`](../exchange-agent/trade-assistance.md) **§2** | **DAG/步骤** **不** **绕过** **确认/读技能**（**SC-AO-03/04** **方向**） |
| **4** | **输入与输出** | **每步** **（或关键步）** **依赖** **哪些** **上游** **产物**（**槽位、`executionId`、行情、技能返回**）？**产出** **哪些** **可观测 ID**？ | [`business-process-standard.md`](../../../standards/business-process-standard.md) **§3** **S{n} 模板**；[`observability/overview.md`](../../../observability/overview.md)；**implementation-alignment** **§8** | **主路径** **至少** **关键步** **具备** **执行者/动作/产出** **或** **显式** **指** **telegram** **卡面** **§** |
| **5** | **失败路径** | **分支与异常** **是否** **写明**（**拒答、超时、504/UNKNOWN、闸断**）？ | 各 **`flows/*.md`** **分支与异常**；**§2** **Failure Path**；**JV-06**、[`unknown-state.md`](../../../Runtime/unknown-state.md) | **不得** **仅** **Happy path** **一轨**；**负例** **可** **指向** **eval** **或** **SC** |
| **6** | **恢复路径** | **重试/降级/对账** **与** **用户** **下一步** **是否** **有** **索引**？ | [`recovery.md`](../../../Runtime/recovery.md)、[`reconciliation.md`](../../../Runtime/reconciliation.md)、[`retry-policy.md`](retry-policy.md)、[`fallback-policy.md`](../../../Runtime/fallback-policy.md) | **恢复** **不** **削弱** **写前确认**；**与** [`interaction-flow-standard.md`](../../../standards/interaction-flow-standard.md) **可点击** **恢复** **同窗** |
| **7** | **人工节点** | **何处** **须** **用户** **类型 A** **/ 高危二次确认**？ | [ADR-001](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)；[`telegram/overview.md`](../telegram/overview.md) **§2.5**；[`hitl-and-automation-matrix.md`](../../../risk/hitl-and-automation-matrix.md)；**`eval.hitl.*`** | **写路径** **人工门** **与** **自动化** **混编** **无** **未声明** **缺口** |
| **8** | **结束状态** | **成功 / 拒答 / 未知终局** **的** **用户侧** **与** **计费侧** **语义**？ | [`execution.md`](../../../Runtime/execution.md) **§1 步 8**；[`consume-and-bill.md`](../../../flows/consume-and-bill.md)；[`billing-management/overview.md`](../../admin/billing-management/overview.md)；[`state-machine.md`](state-machine.md)（**任务**）；[`architecture.md`](../../../../design/architecture.md)（**504/UNKNOWN 叙事**） | **与** **§5** **Goal** **表** **「终止条件」** **行** **不** **矛盾** |

---

## 维护

1. **`routing-engine.md`** **增删 **`scenarioId`** **→** **同窗** 更新 [**`e2e#runtime-walkthrough-scenarios`**](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough-scenarios)（**已在** **`routing-engine`** **文末** **约定**）。  
2. **每篇** **`flows/*`** **大改主路径** → **建议** **在** **文首摘要** **或** **「主路径」** **章** **补** **一句** **§1** **步覆盖** **或** **指** **本模板 §3**；**Golden Path** **评审** **可** **顺带** **勾** **§6** **八维**（**JV-11**）。  
3. **不** **以** **本篇** **替代** **`contract-closure`** **对** **对外承诺** **的** **裁决**。

---

**文档版本**：1.2.6 · **维护**：产品 + Agent Runtime owner · **本版**：**同窗** **补** **`architecture` §「与通用 Agent 栈之对照」** **`e2e` 文首「架构语言」**；**篇首** **`closure-remaining` §7.5 / §7.6** **互引**。**承** 1.2.5。
