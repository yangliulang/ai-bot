# 编排 · 实现对齐（降低偏差）

**路径**：`specs/requirements/domains/agent/agent-orchestration/implementation-alignment.md`。

**职责**：在**不替代**各域 SSOT 的前提下，为 **研发 / 架构 / 评审** 提供 **「需求真源 → 设计 → 实现落点」** 的 **对照索引** 与 **反模式清单**，降低 **「以为需求要求 X、实现做成 Y」** 的认知偏差。**本文不** 新增 OpenAPI 字段、**不** 穷举 DAG 全图（仍遵 [`runtime-freeze.md`](runtime-freeze.md)）。

**互引**：[`overview.md`](overview.md) **FR-AO\***；[`boundaries.md`](boundaries.md)；[`../../../Runtime/domain-model.md`](../../../Runtime/domain-model.md) **（概念十步 · 风险闸束 · 三轨）**；[`../../../Runtime/execution.md`](../../../Runtime/execution.md) **§1**；[`architecture`](../../../../design/architecture.md) **§「与通用 Agent 栈之对照」**（**同窗** [`flow/e2e-closed-loop`](../../../../../flow/e2e-closed-loop.md) **文首「架构语言」**）；[`../../../contract-closure.md`](../../../contract-closure.md) **§1.2**；**对客三闸** **§13.1**（**与** **`contract-closure`** **同窗**）；**统一交易语义** [`canonical-trading-model`](../../../../design/canonical-trading-model.md)、[`ADR-004`](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`CC-P1-07`](../../../contract-closure.md#cc-p1-07)、[`requirements-review` §7.5](../../../../../product/requirements-review.md#cc-adr004-review-checklist)；**开放面 / 首节派工 · 走读缺口** **[§0 速链](../../../closure-remaining.md#closure-remaining-quicklinks)** · **[`closure-remaining` §6](../../../closure-remaining.md#cc-exec-solve-path)** · **[§6.4](../../../closure-remaining.md#cc-problem-to-action)** · **[§7](../../../closure-remaining.md#cc-remaining-open-items)** · **[§7.1](../../../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.2～§7.4 Prompt/Runtime · AC-09](../../../closure-remaining.md#cc-ac09-closure-matrix)** · **[§7.5 DoD 路径](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 执行清单](../../../closure-remaining.md#cc-closure-exec-checklist)**。

---

## 1. 读者与使用方式

| 角色 | 建议用法 |
|------|----------|
| **实现** | 实现任一 **`scenarioId`** 前：先对 [`routing-engine.md`](routing-engine.md) 行 + **§4** 流程锚点 + [`runtime-freeze.md`](runtime-freeze.md) **§3**（**写路径**）+ [`confirmation-flow.md`](confirmation-flow.md)（写序） |
| **Code Review** | 用 **§6 检查单** 抽检；**意图/计费** 交叉用 **§8～§10**；抽检用例骨架见 **§12**；**对客「已支持」** 对照 **§13** |
| **产品/架构** | 争议时先用 **§2 术语** 对齐词义，再用 **§3 真源矩阵** 判「该吵哪份文档」 |

---

## 2. 术语对照（避免同词不同义）

| 文档常用词 | 含义（本仓库内） | **不是** |
|-------------|------------------|----------|
| **`scenarioId`** | 编排 **路由键 / 寄存器键**，[`routing-engine.md`](routing-engine.md) 为产品 SSOT | 不等价于单个 `toolId`；禁止与 `toolId` 混名同义（[`naming-standard.md`](../../../standards/naming-standard.md)） |
| **流程步骤 `S1`…** | [`flows/`](../../../flows/README.md) 里 **业务叙事** 的步骤编号 | 不必与 **观测** 里 `stepSeq` **数值一一相等**；映射关系以 **实现冻结** 文档为准 |
| **确认流步骤 1～5** | [`confirmation-flow.md`](confirmation-flow.md)**写路径** 强制顺序（读 skill → … → 类型 A → 写） | 仅适用于 **触及 `call_exchange_write`** 的场景；**只读分析** 不适用 **FR-T11** 全链 |
| **DAG** | **有向编排拓扑**（节点间允许边）；**不得** 绕过类型 A / 读技能等门 | **不是**「任意 LLM 现场规划步骤」；节点枚举 [**runtime-freeze §2**](runtime-freeze.md) **明示** 在 **实现仓库** 冻结；**环语义** **见** [**runtime-freeze §2.1**](runtime-freeze.md) |
| **Planner** | **Runtime** 内 **选型与推进** 编排的逻辑角色（[`execution.md`](../../../Runtime/execution.md) §1 第 4 步） | **不是** Prompt 里一句「你是 planner」即算达标；须有 **可观测步进 + 预算**（**`FR-AO06`**）；**纯模型多轮** **须** **同窗** **`design` 冻结之回合口径**（**见** [`execution-lifecycle.md`](execution-lifecycle.md) **§4.1 项 3**） |
| **FR-T07** | **意图路由 + 槽位**（[`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) 交界） | **不是** FR-AO 的替代；与 **FR-AO02** **同窗** |
| **`taskId` 状态机** | 长驻 **监控 / 自动化** 任务（[`state-machine.md`](state-machine.md)） | **不是** 单次对话 **`executionId`** 的别名；二者并存 |

---

## 3. 真源矩阵（吵需求时以谁为准）

| 主题 | **需求侧主宿主** | **设计 / 契约** | **实现侧真源（预期）** |
|------|------------------|-----------------|-------------------------|
| HTTP/PATH/字段 | [`design/api.md`](../../../../design/api.md) | OpenAPI / 登记表 | 网关与下游 **对齐矩阵** |
| **Coobit HTTP 出站（实现宿主）** | [`integrations/exchange/overview.md`](../../../integrations/exchange/overview.md)；[`trade-assistance.md`](../exchange-agent/trade-assistance.md) **文首宿主段** | **`openapi-ai` pin**、`allowlist` | **官方 Skill/CLI/MCP** **仅发白名单 PATH**；**不**并行维护同源工具 SSOT |
| **Intent→Canonical→Gateway（统一交易语义 · 文档 A）** | [`canonical-trading-model.md`](../../../../design/canonical-trading-model.md)；[`trade-assistance.md`](../exchange-agent/trade-assistance.md) **§2.6**；[`Runtime/execution.md`](../../../Runtime/execution.md) **§1 步 7** | [`ADR-004`](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)；[`CC-P1-07`](../../../contract-closure.md#cc-p1-07)；[`requirements-review` §7.5](../../../../../product/requirements-review.md#cc-adr004-review-checklist) | **Execution Gateway 可执行实现 / DoD B** **在所内工程仓** **验收**；**本规格仓** **不承载** **Gateway 代码** |
| **`scenarioId` 表** | [`routing-engine.md`](routing-engine.md) | — | **配置或注册表** 与表名 **版本同窗** |
| **已承诺写 · 最小编排（依赖/并行/失败边）** | [`runtime-freeze.md`](runtime-freeze.md) **§3**（**§3.1～§3.11**） | **写键 ↔ §3** **映射** → [`routing-engine.md`](routing-engine.md) **文首「写路径 · 编排下限对签」** | **恢复/Planner** **不得** **违反** **表内** **须先于 / 禁止并行** |
| **写路径步骤序** | [`confirmation-flow.md`](confirmation-flow.md) + `flows/trade-*` | [ADR-001](../../../../design/adr/001-telegram-confirm-before-coobit-write.md) | 状态机 / 工作流 **不得跳过** 步骤 1～3 |
| **DAG 节点与边** | 约束：**FR-AO03**、[`runtime-freeze.md`](runtime-freeze.md) | [`runtime-architecture.md`](../../../../design/runtime-architecture.md) **（随 MR 充实）** | **Planner 仓库** 冻结 **`orchestrationVersion`** |
| **`executionId` / 工具归因** | [`execution-lifecycle.md`](execution-lifecycle.md) | — | [`observability/overview.md`](../../../observability/overview.md) **§2.1** |
| **会话与上下文** | [`../agent-context/overview.md`](../agent-context/overview.md) → `Runtime/context-management` | — | Token 预算与压缩 **实现冻结** |
| **行情只读 · Runtime Context 注入** | [`market-runtime-payload.md`](../exchange-agent/market-runtime-payload.md) **`userVisibleMarketData`/`marketInsightData`**；别名 **§1**，对客 **§2** | **`routing-engine`§1.1**、[read-analyze](../../../flows/read-analyze-and-search-via-agent.md)、OpenAPI `agentContext` | **观测**写 **canonical `scenarioId`**；**用户面** **严禁** PATH / `scenarioId` 字面（**§6 检查单** 增项） |
| **能否对外承诺** | [`contract-closure.md`](../../../contract-closure.md) **§1.2 六款** | — | 矩阵 **`TBD`** **不得** **单独** 当「已支持」；**MR/发版速查** **§13.1** |

---

## 4. `scenarioId` → 流程锚点 → 写确认（摘要）

**全表** 仍以 [`routing-engine.md`](routing-engine.md) 为准。下表仅帮实现 **快速跳转**（**族级**；省略逐行键名）。

| **`routing-engine` 分区** | **首推流程 / 分卷** | **写路径须过 `confirmation-flow`？** | **`runtime-freeze` §3（编排下限）** |
|---------------------------|----------------------|----------------------------------------|-------------------------------------|
| **§1 读侧 / 分析** | [`read-analyze-and-search-via-agent.md`](../../../flows/read-analyze-and-search-via-agent.md) | **否**（默认无类型 A）；**不得隐式写** | — |
| **§2 现货/衍生品写** | [`trade-via-agent.md`](../../../flows/trade-via-agent.md) 开篇四轨 + 专节 | **是**（**ADR-001 / FR-T09**） | **§3.1～§3.9** |
| **§3 理财** | [`wealth-via-agent.md`](../../../flows/wealth-via-agent.md) | **写路径是**；**回退主站** 见 [`boundaries.md`](../exchange-agent/boundaries.md) | **§3.10**（**`subscribe` / `redeem`**） |
| **§4 监控 / 自动化** | [`automation-alerts.md`](../../../flows/automation-alerts.md) | **凡所内写**（创建任务/改条件等）**每笔** **类型 A**；**不含** 网格/DCA **全量机器人**（见该 flow 文首） | **§3.11** |

**计费与终局**：任 **`accepted`** 可计费路径 → [`consume-and-bill.md`](../../../flows/consume-and-bill.md) + [`billing-management/overview.md`](../../admin/billing-management/overview.md)。

---

## 5. `Runtime/execution.md` §1 与逻辑职责（示意）

**权威步骤** 见 [`execution.md`](../../../Runtime/execution.md) **§1**（9 步）。下表 **仅为降低「该把代码挂哪」歧义** 的 **逻辑映射**；**不** 绑定微服务个数或类名。

| §1 步（概念） | **编排域关注点** | **易混提醒** |
|---------------|------------------|--------------|
| 1 接入与归因 | `sessionId` 稳定引用（[`sessions.md`](../../../Runtime/sessions.md)） | 禁止单用 Telegram `message_id` 作跨异步唯一锚 |
| 2 有效配置快照 | Kill/Pause **与** `scenarioId` **是否仍允许新写** | 与 **FR-T02～T04** 同窗 |
| 3 **`executionId`** | **FR-T01**、与 billing **幂等键** 分层 | — |
| **4 编排与 Planner** | **`scenarioId`、门禁顺序、FR-AO06 预算** | **本节之前** **勿** **调交易所写** |
| 5 上下文装配 | Prompt 版本（[`prompt-management`](../../admin/prompt-management/overview.md)） | **非** `routing-engine` 替代 |
| **6 确认门（写前）** | **须** 对齐 **类型 A** 与 [`confirmation-flow.md`](confirmation-flow.md) | **模型输出** **不得** **替代** **用户点击/明示确认** |
| 7 工具与外部调用 | `trade-assistance` §8 **已登记** `toolId` | **无登记工具** → **FR-T05** |
| 8～9 终局与观测 | 504/UNKNOWN **不得** 冒充终局（[`unknown-state.md`](../../../Runtime/unknown-state.md)） | — |

---

## 6. 实现评审检查单（反认知偏差）

- [ ] **Coobit 私网出站**（触及 `call_exchange_write` **或须** **子账户 scope** **之私有读**）：所内宿主（`openapi-ai`/Skill）**是否已 pin**，且出站 PATH **是否仅** **`agent-coobit-api-allowlist`** **已载项**？【[`allowlist`](../../../integrations/exchange/agent-coobit-api-allowlist.md)、[`exchange/overview · openapi-ai 节`](../../../integrations/exchange/overview.md)】
- [ ] **写路径** 是否 **先** **`read_skill_operation_spec`**（**FR-AO04 / FR-T11**）再 **类型 A**？  
- [ ] **任一** **`agent.orchestration.step`**（或等价）是否 **可携带** **`scenarioId` + `orchestrationVersion`**（**FR-AO05**）？  
- [ ] **是否存在**「无 **`scenarioId`** 却调 **B 类 / 外网** 工具」路径？（**禁止**）  
- [ ] **单轮** 是否 **最多一个主** **`scenarioId`**；冲突是否 **澄清**（**FR-AO02**）？  
- [ ] **工具次数 + 编排步 +（若启用）模型回合** 是否 **有硬顶 + 可观测终止**（**FR-AO06** / **SC-AO-08**）？  
- [ ] **DAG** 是否 **无绕门**（读技能、类型 A）（**SC-AO-03**）？  
- [ ] **写路径拓扑** 是否 **与** [`runtime-freeze.md`](runtime-freeze.md) **§3** **对应** **`scenarioId` 小节**（**§3.1～§3.11**）**之** **须先于 / 禁止并行 / 失败出口** **一致**（**键映射** **见** [`routing-engine.md`](routing-engine.md) **文首**）？ **只读** **`scenarioId`** **可标 N/A** **并** **述理由**？  
- [ ] **`routing-engine`** **占位 / 延期** 行是否 **未** 单独标「生产已支持」（见 [`overview.md`](overview.md) **§6**）？  
- [ ] **LLM / 解析层** 给出的 **`scenarioId` 候选** 是否 **必经** [`routing-engine.md`](routing-engine.md) **+ 有效 `config` 快照** **二次校验**（非法键 → **澄清或 `FR-T05`**，**禁止**静默落交易所写）？  
- [ ] **可计费边界** 是否 与 [`consume-and-bill.md`](../../../flows/consume-and-bill.md) **S3～S5**、[`billing-management/overview.md`](../../admin/billing-management/overview.md) **§10.1 / §7.4.1** **一致**（含 **504/UNKNOWN** **不得** 向用户 **断言成交**）？  
- [ ] **`DAG` / 编排步**：**`FR-AO06.2`** **硬顶** **是否** **生效**；**静态无环 / 环检测** **策略** **是否** **与** [`runtime-freeze.md`](runtime-freeze.md) **§2.1** **同窗**（**或** **明文** **首版 DAG MR 豁免**）？  
- [ ] **上下文反污染**：**工具结果回填** **是否** **仅** **携带** **当前** **`sessionId` + `executionId`（或等价键）** — **见** [`context-management.md`](../../../Runtime/context-management.md) **§2**、[`locking.md`](../../../Runtime/locking.md) **§1**？  
- [ ] **用户可见阶段话术** **是否** **与** [`telegram/overview.md`](../telegram/overview.md) **§3.1**、[`trade-via-agent.md`](../../../flows/trade-via-agent.md) **S5.1.1**、[`unknown-state.md`](../../../Runtime/unknown-state.md) **用户可见副本** **无** **终局误导**（**抽检** **`eval.runtime.user_visible_phase_copy` / JV-12**）？  
- [ ] **行情只读 · Telegram**：用户正文 **不含** **`/sapi/`**、裸 **`GET`/`POST`**、**「场景 ID」**、**`read.market.*`/`scenarioId` 字面**/调试块 — **`market-runtime-payload`§2**、[`read-analyze](../../../flows/read-analyze-and-search-via-agent.md) **S6**？
- [ ] **行情 Facts 映射**：**`tool.market.ticker`** **成功且上游含 **`last`** **时** **`userVisibleMarketData.lastPrice`** **须存在** — **[`market-runtime-payload` §3.3](../exchange-agent/market-runtime-payload.md)**、**`SC-MRP01`**、**`eval.market.ticker_facts_mapping`**？
- [ ] **Market Narrative**：**`marketPhase` ∈ §3.2.1** **确定性产出**（**非模型自造**）；**Funding phase 须带 fundingRate** — **`FR-MI06`～`08`**、**`eval.market.narrative_*`**、[`common-phrases` §8](../../../prompts/shared/common-phrases.md)？
- [ ] **记忆召回 · STM**：**[`memory-runtime` §10、§14.6](../../../Runtime/memory-runtime.md)** — **L0/L1** **按 **`sessionId`/`executionId`** **注入**；**stale 后活跃 L1 不含写澄清**；**Resume 门控 + 置信阈值**；**新 execution 问价/余额** **须重拉工具或 stale**？
- [ ] **记忆召回 · LTM**：**`FEATURE_SEMANTIC_NARRATIVE` OFF** **无 **`semanticNarrativeBlock`**；**ON** **则** **§9 + FR-MEM09 写入 + Telegram §2.7** — **`SC-MEM*`** / **`SC-CH-TG-MEM-*`**？
- [ ] **STM vs LTM 删除分流**：**「重新开始」** **走** **§13/§2.8**；**「清空记忆」** **走** **§2.7.3** — **`SC-STM*`** / **`SC-CH-TG-STM-*`**？
- [ ] **并发 callback 归因**：**类型 A callback** **绑定原 **`executionId`** — **`memory-runtime` §10.4**？
- [ ] **单 session 并发**：**inbound 串行/合并** **符合** [`session-concurrency-policy` §2](../../domains/agent/agent-orchestration/session-concurrency-policy.md)；**在途写 execution ≤ `SESSION_MAX_ACTIVE_WRITE_EXECUTIONS`**；**第二笔写/UNKNOWN/类型 A** **按 §3～§6** — **`SC-AO-09～10`** · **`eval.session.*`**？
- [ ] **只读澄清**：**`rc:*` 不触发写**；**写打断读** **abandon ReadClarifySession** — [`read-clarify-session`](../../domains/agent/agent-orchestration/read-clarify-session.md) **§2.3、§4** · **`SC-READ-CLARIFY-01/02`** · **`eval.read_clarify.*`**？
- [ ] **上下文超 budget**：**裁剪顺序** **符合** **`memory-runtime` §11**；**`eval.memory.budget_trim`**；**②④** **未被静默删**？
- [ ] **类型 A 卡面字段** **与** **即将调用之** **OpenAPI 写请求** **是否** **可** **字段级对账**（**或** **同窗契约测**）**—** **禁止** **确认摘要** **与** **实参** **系统性漂移**？  
- [ ] **若 MR / `release-notes` / 营销稿** **宣称** **本能力「生产已可用 / 已闭环」**：是否 **已** **按** **§13.1** **三闸** **附链**（**或** **本轮** **明确** **未作** **对客闭环宣称**）？

---

## 7. 最小阅读顺序（单人从 0 到可写代码）

1. [`overview.md`](overview.md) **§2～§3**（FR-AO / SC-AO）  
2. [`routing-engine.md`](routing-engine.md)（键名登记）  
3. [`confirmation-flow.md`](confirmation-flow.md)（写序）  
4. [`../../../Runtime/execution.md`](../../../Runtime/execution.md) **§1**  
5. [`goal-and-execution-paths.md`](goal-and-execution-paths.md)（**Goal §5 · Golden §6 · JV-10/11** · §1×flow · HITL 索引）  
6. **[`flow/e2e-closed-loop.md`](../../../../../flow/e2e-closed-loop.md) · [Walkthrough 范例](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough)**、**[全 `scenarioId` 索引](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough-scenarios)**  
7. 目标 **`scenarioId`** 对应 [`flows/`](../../../flows/README.md) 专节  
8. [`runtime-freeze.md`](runtime-freeze.md)（**`orchestrationVersion`、DAG、§2.1 有向环**、**§3 写路径最小编排**）  
9. [`../../../Runtime/context-management.md`](../../../Runtime/context-management.md) **§2**（**反污染**）  
10. [`../../../contract-closure.md`](../../../contract-closure.md)（若涉及对外承诺）  
11. **意图 / 计费专项对读**：**§8～§10**；**GWT 抽检**：**§12**  
12. **拟对客宣称「已支持」前**：**§13.1** **三闸**（**与** **`release-notes` / 六款** **同窗**）

---

## 8. 意图：识别、分类、路由（实现侧约定）

**需求 SSOT**：语义簇与歧义 → [`../exchange-agent/intents.md`](../exchange-agent/intents.md)；Prompt 侧下限 → [`../../../prompts/intents/`](../../../prompts/intents/README.md)；路由键 → [`routing-engine.md`](routing-engine.md)；单轮主场景 → **FR-AO02** / **FR-T07**（[`overview.md`](overview.md)、[`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md)）。**写路径澄清 · LLM/规则/组合分工** → [`prompts/shared/clarify-user-visible` §0](../../../prompts/shared/clarify-user-visible.md#clarify-execution-split)（**本篇表管识别/路由**；**§0 管澄清/补槽**）。

| 阶段 | **产品含义** | **实现常见落点（示意）** | **硬闸** |
|------|----------------|---------------------------|----------|
| **识别** | 从自然语言得到 **草案**（是否写、槽位草稿、是否追问） | LLM + Prompt 注入；可 **结构化输出 / 单工具 `propose_intent`** | **不得** 未过 **FR-T02** **即调私有写** |
| **分类** | 归入 **pillar / 流程族**（与 [`intents.md` §1](../exchange-agent/intents.md) **表一致**） | 规则后置校验、或与模型标签 **对签** | **网格/全策略** → **澄清/边界**，[`trade.md` 意图条文](../../../prompts/intents/trade.md) |
| **路由** | 收敛到 **0 或 1** 个主 **`scenarioId`** + 选配 `flow` | **寄存器查找** + **FEATURE\_\***；冲突 → **澄清 / 分步** | **FR-AO02**；**无键** **禁止** **冒充已支持** |

### 8.1 结构化「意图草案」最低字段（产品下限 · 非 OpenAPI）

下列字段为 **实现可对齐、评审可抽检** 的 **下限建议**；**允许** 等价命名或嵌套，**须** 能映射到观测与 **`scenarioId` 终裁**。

| 字段（逻辑名） | **必填** | **说明** |
|----------------|----------|----------|
| **`scenario_id_candidates`** | 推荐 | 零个或多个 **字符串**；**须** 经 [`routing-engine.md`](routing-engine.md) **校验**；**主场景最多一个生效**（**FR-AO02**） |
| **`intent_family`** | 推荐 | **粗分类**，与 [`intents.md` §1](../exchange-agent/intents.md) **行** 可对照（如 `market_read` / `portfolio_read` / `trade_write` / `wealth` / `monitoring` / `clarify_only`） |
| **`slots`** | 视场景 | 业务槽位（如 **`side`、数量、标的、限价/市价提示**）；**不全** → **追问**，**禁止** 臆测下单（**FR-T07**） |
| **`requires_clarification`** | 推荐 | 人话 **追问原因** 列表；非空时 **不得** 生成 **类型 A 写** |
| **`orchestration_next_steps`** | 推荐 | **INV-010** 等 **编排须插入步**（如 **`slot_fill_read_balance`**）— **非** Telegram 正文；Demo · [`allInOrchestration.ts`](../../../../src/admin/src/productionRuntime/allInOrchestration.ts) · **执行小样** [`orchestrationReadBalanceFill.ts`](../../../../src/admin/src/productionRuntime/orchestrationReadBalanceFill.ts) |
| **`telegram_outbound`** | 推荐 | BFF 出站：**typing 期望**、**澄清 `inline_keyboard`**、**进度/润色锚点** — OpenAPI **`TelegramClarifyOutboundHints`** |
| **`clarify_session`** | 推荐 | **澄清快照** — OpenAPI **`ClarifySessionSnapshot`**；**SSOT** [`clarify-session.md`](clarify-session.md) **§3** |
| **`invokes_exchange_write`** | 推荐 bool | **是否** 拟触发 **`call_exchange_write`**；`true` **须** 走 [`confirmation-flow.md`](confirmation-flow.md) **全链** |

### 8.2 澄清会话 · `ClarifySessionSnapshot`（写路径 · 产品下限）

**全文 SSOT**：[`clarify-session.md`](clarify-session.md)（**边界**、**callback 注册表**、**旅程示例**、**SC-CLARIFY-***）。

**与 §8.1 关系**：**§8.1** **管** **单步 Parser/Resolver 草案**；**§8.2** **管** **跨轮持久化** **与** **`cl:*` 点按**。**二者** **须** **同窗** **`executionId`**。

**STM 注入（MUST）**：**每轮** **写澄清** **Prompt 上下文** **须** **含** **`resolvedSlotsSoFar` 人话摘要** + **单一 `pendingClarifyKind`/`missing` 首项** — **同窗** [`memory-runtime` §10.2、§15～§16](../../../Runtime/memory-runtime.md) · **`SC-CLARIFY-03`** · **`FR-STM11`** **装配前四原则硬闸**。

**澄清态 inbound（MUST）**：**每条** **`Update.message`** **须** **重跑** **§8 识别/分类** — **禁止** **仅** **凭** **`clarify_session.pendingClarifyKind`** **复读 outbound** — [`clarify-session.md` §2.3](clarify-session.md) · **`SC-CLARIFY-05～09`**。

**空闲 / TTL stale + Resume（MUST）**：**写路径 idle/TTL 先达** → **[`memory-runtime` §14.6](../../../Runtime/memory-runtime.md)** · **[`clarify-session` §2.4](clarify-session.md)** — **退出活跃 L1** · **温索引 **`WarmExecutionEpisode`** · **规则续单 bypass 分类器** · **ambiguous 须 **`confidence ≥ RESUME_CLASSIFIER_MIN_CONFIDENCE`** · **`stale→active`** **须 Resolver 重算 **`pendingClarifyKind`** — **`FR-STM12～14`** · **`SC-STM12～13`**。

**说明**：**不要求** 指定 **厂商 JSON Schema**；若团队冻结 **Pydantic / `response_format`**，**须** 与上表 **字段语义同窗**，并在 **Prompt 发布**（[`prompt-management`](../../admin/prompt-management/overview.md)）中 **版本化**。

---

## 9. 语义簇 → `routing-engine` 分区（映射）

**权威话术与歧义** 仍以 [`../exchange-agent/intents.md`](../exchange-agent/intents.md) **§1～§3** 为准。下表仅加速 **「分类语义 → 往寄存器哪一段找键」**；**具体 `scenarioId`** **以** [`routing-engine.md`](routing-engine.md) **行为准**。

| **`intents.md` §1 意图簇（摘要）** | **首选 `routing-engine` 分区** | **备注** |
|-----------------------------------|-------------------------------|----------|
| 行情、Funding、K 线/解读、舆情/检索 | **§1 读侧 / 分析** | **`market.*`、`research.*`、`futures.read_funding`** 等 |
| 余额、持仓、盈亏、挂单、在途 | **§1**（**`orders.*` / `portfolio.*`**） | **私读** → **FR-T02** |
| 提醒、到价、风险阈值、监控订阅 | **§4 监控与自动化** + [`monitoring-tasks.md`](../exchange-agent/monitoring-tasks.md) | **`taskId`** **≠** **`executionId`** |
| 买/卖/闪兑/限价/合约/杠杆/止盈止损 | **§2 写路径** | **四轨互斥** → [`trade-via-agent.md`](../../../flows/trade-via-agent.md) 文首 |
| 理财申购/赎回/持仓/推荐 | **§3 理财** | **写** + **类型 A**；**矩阵缺** → **主站回退码** |
| 条件单到期、**定投、网格、全策略机器人** | **不自动映射生产键** | **澄清 / 非目标** / 主站 — [`trade.md`](../../../prompts/intents/trade.md)、[`automation-alerts.md`](../../../flows/automation-alerts.md) 文首 |

---

## 10. 计费与执行交界（索引）

**业务序 SSOT**：[`consume-and-bill.md`](../../../flows/consume-and-bill.md)。

| 主题 | **权威条目** | **实现/评审注意** |
|------|----------------|-------------------|
| **`executionId` 分配** | **S3**、**FR-T01** | 与 **核销幂等**（**`FR-B05` / `SC-B20`**）**同窗** [`billing-management/overview.md`](../../admin/billing-management/overview.md) |
| **门禁与余额** | **S2**、[`billing.md` §7.4.1](../../admin/billing-management/overview.md) | **可计费路径** **不得** **在已知将完不成 S5** 时 **仍耗尽 USDT 可用**（保守下界、`effectiveMinChargeUsdt`） |
| **终局与封印** | **S4**、**billing §10 D-2 / §10.1** | **UNKNOWN** 时 **S5 核销评估** **叙事** **以 §10.1 为准**；**用户可见成交断言** **仍须** **`architecture` 对账** |
| **核销 POST（轨 B · Agent S5）** | **S5**、`POST …/billing/entitlements/debit` · **`ENTITLEMENT_DEBIT`** | [`internal/billing-entitlements.yaml`](../../../../openapi/internal/billing-entitlements.yaml)、[`commerce-model`](../../admin/billing-management/commerce-model.md) §4；**不**默认 **`internal/billing/charges`（轨 A 对读）** |
| **504 / UNKNOWN** | [`consume-and-bill.md` §「与交易所写调用交界」](../../../flows/consume-and-bill.md)、[`unknown-state.md`](../../../Runtime/unknown-state.md) | **观测** `trading.exchange_private`；**禁止** **矛盾文案** |
| **用户流水** | **S6**、[`web/agent-billing.md`](../../web/agent-billing.md) | **与 Telegram Deeplink** 同窗 |

---

## 11. 在途、队列与重试（横切索引）

| 主题 | **主宿主** |
|------|------------|
| **D-1 在途策略、紧急停止** | [`management-console-v1-prd.md`](../../admin/management-console-v1-prd.md) **§11**、[`exchange-agent/overview.md`](../exchange-agent/overview.md) **FR-T04**、[`consume-and-bill.md`](../../../flows/consume-and-bill.md) **余额不足/在途**；**504 后** **不可逆成交** **默认 (A)** 见 [`billing-management/overview.md`](../../admin/billing-management/overview.md) **§10.2** |
| **队列、Planner、重试叙事** | [`execution.md`](../../../Runtime/execution.md) **§1～§2**、[`recovery.md`](../../../Runtime/recovery.md)、[`retry-policy.md`](retry-policy.md) |
| **并发 / 锁** | [`locking.md`](../../../Runtime/locking.md) |

---

## 12. 评审用 Given / When / Then 模板（可复制）

**用途**：对某一 **`scenarioId`** 或 **用户话束** 做 **需求↔实现对签**。**Then** 须 **可观测**（`executionId`、`scenarioId`、`agent.tool.call` 等）。

```text
用例 ID：
Given：用户已绑定子账户 / VIP / FEATURE___ = ON（按需）
  与 会话 sessionId = ___

When：用户输入「___」
  且 本轮主 scenarioId 预期 = ___

Then：
  - 编排下限：`runtime-freeze.md` §3 对应小节（写路径）— 须先于/禁止并行/失败边未被违反 = 是/否/N/A（只读键）
  - 门禁：若须私有读/写，FR-T02 与 billing §7.4.1 行为 = ___
  - 意图：单轮主 scenarioId 个数 ≤ 1；非法键 = 澄清或 FR-T05（码 ___）
  - 写路径：read_skill → 校验/槽位 → 类型 A → call_exchange_write（布尔 是/否）
  - 风险闸 R1～R3 时点：[`domain-model` §2](../../../Runtime/domain-model.md) = 是/否/N/A
  - 管线序（时间线）：spec_read < confirmation.required < 写 = 是/否（走读 [`pipeline-walkthrough-checklist`](../../../Runtime/pipeline-walkthrough-checklist.md)）
  - 观测：orchestrationVersion = ___；工具链携带 scenarioId = 是/否
  - 计费：accepted 与 executionId；S4～S5 轨 B 核销与 billing §10.1 一致 = 是/否
  - 若 504：用户可见无「已成交」断言；exchangeOutcome unknown = 是/否
```

---

## 13. 评审建议固化 · 对外承诺、评审门禁与回归束（P0～P2）

**用途**：把 **「矩阵未冻却宣称已支持」**、**「仅文档 v0.3 被误读为全能」** 类偏差 **收口为可执行纪律**；**不替代** [`contract-closure.md`](../../../contract-closure.md) **全文**。

### 13.1 对客「生产已支持」三闸（P0）

若要在 **营销、帮助中心、发布说明、`product/release-notes`** 等 **对客材料** 中将某一能力标为 **生产已可用 / 已闭环**，**须** **同时** 满足 **下列三条**（**缺一不可**）；否则 **仅可** 表述为 **需求或设计已覆盖**、**实现中 / TBD**。

| # | **闸** | **权威锚点** | **最小判据** |
|---|--------|--------------|--------------|
| **1** | **寄存器与能力登记** | [`routing-engine.md`](routing-engine.md)；[`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **§8**；[`overview.md`](overview.md) **§6**；[`runtime-freeze.md`](runtime-freeze.md) **§3** | **非** **无 flows / §8 依据之占位键**；**或与** **占位行** **同窗 MR** **后再宣称**。**写键** **另须** **与** **§3 最小编排** **无冲突**（**同窗** [`contract-closure.md`](../../../contract-closure.md) **§1.2 款 4**） |
| **2** | **矩阵与 PATH** | [`design/api.md`](../../../../design/api.md)；[`contract-closure.md`](../../../contract-closure.md) **§1.2 第 1 款** | 对应 **PATH** **非** **长期无说明 `TBD`**；**延期** **须** **与实现备注一致** |
| **3** | **六款齐备（B）或小团队等价关门** | [`contract-closure.md`](../../../contract-closure.md) **§1.2**；[`LITE-MODE.md`](../../../LITE-MODE.md) **§3** | **大团队 / 审计轨**：**§1.2 六款** **逐项** **可对签**。**两人模式**：**`product/release-notes.md`** **须** **列明** **本版承诺 / 明确不承诺**，**且** **不与** **矩阵占位** **矛盾** |

**实现验收（本 Git 之外）**：**`runtime-freeze` §3** **写路径下限** **之** **「Planner/恢复是否真遵守」** **须** **在** **所内 Agent Runtime 仓库** **以** **可审计轨迹 / 集成测** **证实**；**本仓库** **可** **先做** **[`e2e` Walkthrough](../../../../../flow/e2e-closed-loop.md#runtime-walkthrough)**、**[`journey-validation` JV-07](../../../../../product/journey-validation.md)** **文档抽检**。**首节派工单** → **[§6](../../../closure-remaining.md#cc-exec-solve-path) · [§6.4](../../../closure-remaining.md#cc-problem-to-action)**。**开放面总表** → [`closure-remaining` §7](../../../closure-remaining.md#cc-remaining-open-items)；**走读缺口粘贴** → **[§7.1](../../../closure-remaining.md#cc-remaining-gap-paste)**。**未关闭项闭环路径** → **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)**。**MR 关单勾选** → **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。

**反模式**：**分卷标 v0.3**、**`intents.md` 已写** **但** **上表未关** → **禁止** **单独** **使用**「已支持」「已全能」**话术**。

### 13.2 Code Review / 迭代合并最小门禁（P1）

- **编排相关 MR**：**§6** **逐项勾选** **或** **明文豁免理由**（**须** **Review 可复读**）。**新增 / 变更写** **`scenarioId`** **或** **改** **依赖拓扑**：**须** **有** [`runtime-freeze.md`](runtime-freeze.md) **§3** **对应小节** **或** **本轮** **MR** **附** **「仅读路径 · N/A」** **可复读理由**。  
- **意图 / Prompt / 计费交界**：**§8～§10** **至少通读diff 命中条**。  
- **主态 / 模块八时间线**：若 MR **触及** **`executionId` 主态归并**或 **`admin/observability/*` · `FR-MC801`**，**须** **同窗** [`execution-transition-matrix.md`](../../../Runtime/execution-transition-matrix.md) **§2.2**、[`observability/overview.md`](../../../observability/overview.md) **§2.4**；**勿** **吞 `transitionTrigger`** — **抽检** **可** **`SC-OBS08`** / [`eval.obs.timeline_transition_contract`](../../../evals/scenarios.md)。  
- **抽检**：**§12** **GWT** **至少复制填空 1 条** **且** **与本轮 **`scenarioId`** **或** **用户话束** **一致**（**可** **贴 MR 描述** **§2**）。

### 13.3 最小回归用例束索引（P2 · evals）

**登记宿主**：[`../../evals/scenarios.md`](../../evals/scenarios.md)。**正文** **以该表** **`evalSetId`** **为准**；**构造** **与** **Then** **须** **与** **§12** **同构**（**可观测**、**可对照 `SC-*`**）。**端到端 Walkthrough** → [`flow/e2e-closed-loop.md`](../../../../flow/e2e-closed-loop.md#runtime-walkthrough-crosscut)。

**本仓库可执行 Mock 下限**：[`../../evals/README.md`](../../evals/README.md) **§3** — **`src/admin`** **`npm test`** · **`mock.timeline.contract.test.ts`**（**同窗** **`eval.obs.timeline_transition_contract`**）。

| 主题 | **`evalSetId`（见 scenarios 表）** |
|------|-----------------------------------|
| **`trade.spot.flash_convert`** 意图 → 写路径 + 计费 | **`eval.trade.spot.flash_convert.gwt`** |
| **只读**：行情/余额 **无** **`call_exchange_write`** | **`eval.read.market_portfolio_no_write`** |
| **监控/自动化**：创建任务 **（写 + 类型 A + `taskId`）** | **`eval.automation.monitoring_create`** |
| **504 / UNKNOWN 写** | **`eval.obs.504_unknown_write`**（已登记） |
| **主态边 × `FR-MC801` 时间线（Transition Contract）** | **`eval.obs.timeline_transition_contract`** |
| **写路径 · 五段事件序（spec_read → 确认 → 写）** | **`eval.runtime.pipeline_write_order`** — [`pipeline-write-order.md`](../../evals/pipeline-write-order.md)、[`pipeline-walkthrough-checklist`](../../../Runtime/pipeline-walkthrough-checklist.md) |
| **非法/占位路由键** → **澄清或 `FR-T05`** | **`eval.intent.invalid_scenario_reject`** |
| **`sessionId`/`executionId` 工具回填隔离** | **`eval.context.session_execution_tool_bind`** |
| **Webhook 重复 Update / 幂等** | **`eval.runtime.telegram_update_idempotent`** |
| **全局 Pause/Kill 拒新写** | **`eval.runtime.global_pause_blocks_new_write`** |
| **Market Narrative · ticker 映射 / phase / Funding** | **`eval.market.ticker_facts_mapping`**、**`eval.market.narrative_*`**、**`eval.market.narrative_obs`** — **GWT** [`evals/market-narrative.md`](../../evals/market-narrative.md) |
| **Memory · STM/LTM / 裁剪 / 分流 / 四原则 / stale+Resume** | **`eval.memory.stm_governance_regression`**、**`eval.memory.idle_default_stale`**、**`eval.memory.resume_classifier_gate`**、**`eval.memory.resume_classifier_multi_episode`**、**`eval.clarify.*`**（**含 §12～§13**）、**`eval.memory.stm_vs_ltm_intent`**、**`eval.memory.obs_trim`** — **GWT** [`evals/memory-runtime.md`](../../evals/memory-runtime.md) · [`evals/clarify-telegram.md`](../../evals/clarify-telegram.md) |
| **Session 并发 · inbound 队列 / 多 execution / D-1** | **`eval.session.inbound_serial_no_double_parse`**、**`eval.session.single_active_write_execution`**、**`eval.session.second_write_while_confirm`**、**`eval.session.new_write_blocked_on_unknown`**、**`eval.session.amend_chain_blocks_parallel_write`** — **GWT** [`evals/session-concurrency.md`](../../evals/session-concurrency.md) |
| **只读澄清 · `rc:*` / 写读对称** | **`eval.read_clarify.write_interrupts_read`**、**`eval.read_clarify.scope_portfolio_vs_market`**、**`eval.read_clarify.monitoring_draft_then_type_a`** — **GWT** [`evals/read-clarify-telegram.md`](../../evals/read-clarify-telegram.md) |
| **Fallback/Retry · 决策树 / 504 / 确认门** | **`eval.fallback.write_504_unknown_no_auto_replay`**、**`eval.fallback.retry_blocks_confirmation_bypass`**、**`eval.fallback.parse_missing_slot_write_clarify`** — **GWT** [`evals/fallback-retry-decision-tree.md`](../../evals/fallback-retry-decision-tree.md) |
| **UNKNOWN 追问 · 504 后 inbound** | **`eval.unknown.status_query_no_false_success`**、**`eval.unknown.new_write_blocked_on_pending`**、**`eval.unknown.repeat_submit_no_auto_replay`** — **GWT** [`evals/unknown-followup-telegram.md`](../../evals/unknown-followup-telegram.md) |

---

**文档版本**：1.2.30 · **维护**：产品 + Agent Runtime owner · **本版**：**§13.3 multi-episode + clarify §12～§13 eval**。承 **1.2.29**。
