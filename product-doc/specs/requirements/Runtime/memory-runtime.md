# Runtime · 记忆与上下文（Memory · 分域与注入）

**路径**：`specs/requirements/Runtime/memory-runtime.md`。

**职责**：在 **[`context-management.md`](./context-management.md)** **§1～§2** **硬下限之上**，冻结 **交易型 Agent Runtime** **可用的「记忆」分层**、**注入优先级**、**Episodic/Semantic 产品语义** **与** **TTL 分级口径**。**热/温/冷 默认数值（v0）** **见** **[`design/architecture.md`](../../design/architecture.md)**；**可调存储键 / OpenAPI** **随实现 MR 对签**。**Prompt 字面、denylist** → [`prompt-management`](../domains/admin/prompt-management/overview.md)。

**同窗**：[`context-management.md`](./context-management.md)；[`sessions.md`](./sessions.md)；[`persistence.md`](./persistence.md)；[`event-storage.md`](./event-storage.md)；[`observability/overview.md`](../observability/overview.md) **§2**；[`domains/agent/goals/README.md`](../domains/agent/goals/README.md)；[`../../design/architecture.md`](../../design/architecture.md) **（Memory 留存 v0）**；[`../../design/api.md`](../../design/api.md) **（`stableReason` 附录）**。

---

## 1. 与 `context-management` 分工

| **卷** | **边界** |
|--------|----------|
| **`context-management` §1～§2** | **预算、降级、隔离、反污染** **MUST** **表** — **继续** **为** **执法条** |
| **本篇（`memory-runtime`）** | **Memory 类型学**、**注入序**、**留存分级** — **把** **「是什么、先後、留多久」** **说清** |

**冲突时**：**以** **`context-management` §2** **反污染** **为准**；**本篇** **不** **放宽** **跨租户/跨执行** **误用**。

**治理宪法**：**该记的记、不该记的别乱记、该忘的一定要忘记、不该忘的不要忘记** — **执行矩阵** **[§16](./memory-runtime.md#16-记忆治理四原则must--防僵尸澄清--防错乱写)**（**同窗** **§14～§15**、[`clarify-session` §2.3](../domains/agent/agent-orchestration/clarify-session.md)）。

### 2.0 产品别名：短期记忆 / 长期记忆（STM / LTM）

**用途**：与业界用语、实现对齐；**SSOT 仍以 L 层为准**，下表 **不** **新增第二套枚举。

| **产品/业界说法** | **规格层** | **召回默认** | **契约** |
|-------------------|------------|--------------|----------|
| **短期记忆 · STM** | **L0 + L1**（热 · Episodic） | **每轮自动** | **已承诺路径**（[`context-management` §2](./context-management.md)） |
| **长期记忆 · LTM（对用户）** | **L2 + Semantic**（§9） | **开关 ON 时自动** | **草案 · 默认 OFF**（`FR-MEM*`） |
| **长期留存（对系统）** | **L3 + 温/冷** | **默认不注入 Prompt** | 审计/账务；**非** LTM |

---

## 2. Memory scope（产品分层）

### 2.0 术语别名（STM / LTM · 与实现对齐）

| **产品/业界说法** | **本仓 SSOT** | **默认进 Prompt** |
|-------------------|---------------|-------------------|
| **短期记忆（STM）** | **L0** 回合工作记忆 + **L1** Execution 归因记忆（**热 · Episodic**） | ✓ |
| **长期记忆（LTM · 对用户）** | **L2** 用户偏好 + **可选 Semantic**（**§9 `FR-MEM*`**） | **默认 OFF** |
| **长期留存（LTM · 对系统）** | **L3** + **温/冷**（审计/账务/排障） | ✗ **默认不灌模型** |

**说明**：实现 **可**在日志/代码中使用 `shortTermMemory` / `longTermMemory` **等** **工程名**，**须** **文档化映射** **至** **上表 L 层** — **禁止** **第二套** **产品 SSOT**。

| **层** | **含义** | **典型内容** | **默认绑定键** |
|--------|----------|--------------|----------------|
| **L0 · 回合工作记忆** | **当前用户轮次** **拼装** **用之** **易失窗口** | **近轮 user/assistant 可见句、可选 rolling summary** — **准入** **[§15.1](./memory-runtime.md#15-stm-写入准入--什么进什么不进must)** | **`sessionId` + 当前回合** |
| **L1 · Execution 归因记忆** | **须** **可 join** **`executionId`** **之** **工具快照/编排摘要** | 类型 A 已确认包、**裁剪后** Facts、澄清槽摘要 — **[§15.2](./memory-runtime.md#152-l1execution-归因记忆--准入)** | **`executionId`** **（+ `sessionId`）** |
| **L2 · 用户偏好 / 策略记忆** | **用户显式** **或** **运营配置** **之** **跨会话偏好**（**非** **无限自传**） | 风险档位、黑白名单、默认下单语义（**若** **产品开放**） | **用户/实例配置域**（**`design` 键**） |
| **L3 · 留存与审计** | **合规/账务/排障** **所需** **事件与检查点** | **计费**、**审计**、**检查点** — **非** **模型 prompt 无限上下文** | **保留期** **见** **§4** **与** **`event-storage`/`persistence`** |

**禁止**：**把** **L3** **审计卷** **等同于** **可向 LLM 无界注入** **的** **「全历史」**。

---

## 3. Episodic vs Semantic（本仓用语）

| **类** | **定义（需求层）** | **本阶段产品承诺** |
|--------|--------------------|---------------------|
| **Episodic（情节型）** | **按时间/回合/执行** **可追溯** **之** **原始或轻摘要痕迹**（工具 I/O、卡片、拒答原因） | **须有** **`executionId`/`sessionId` 归因**；**与** **`context-management` §2** **一致** |
| **Semantic（语义型）** | **从多轮事实** **抽取** **之** **稳定命题**（**如** **用户偏好**、**允许的交易对集合**） | **首版** **不** **承诺** **无界** **自增长** **语义库** **必须** **进** **模型主上下文**；**跨会话 Semantic Narrative** **若启用** → **§9 `FR-MEM*`** + **`prompt-management` 注入闸** |

**跨 `executionId`**：**Episodic** **默认** **不得** **冒充** **当前行情/订单真值** **驱动** **新写** — **同** **`context-management` §2** **第三行**。

---

## 4. TTL / 分级留存（口径 · 数值已登记 v0）

**原则** **与** **热/温/冷** **定义** **见** **上表**；**全所默认数值（v0）** **见** **[`design/architecture.md`](../../design/architecture.md)** **「Memory 留存」**。**环境覆盖** **须** **可审计**。

| **级** | **原则** |
|--------|----------|
| **热** | **L0/L1** **随** **会话与 execution 生命周期** **回收**；**终局后** **不得** **无限** **占** **拼装顶** |
| **温** | **可观测/抽检样例** **与** **短窗排障** **（** **`event-storage`** **）** |
| **冷** | **审计/账务/监管** **要求** **之** **下限** — **与** **billing/audit** **对签** |

**显式删除/遗忘**：若产品提供 **「清空会话/撤销记忆」**，**须** **区分** **两类用户动作** — **不得** **混为** **同一按钮/同一意图**（**同窗** **§13**、[`telegram/overview` §2.7～§2.8](../domains/agent/telegram/overview.md)）：

| **用户动作（产品说法）** | **须触及层** | **须保留** |
|--------------------------|--------------|------------|
| **清空本会话 / 重新开始（STM）** | **L0** + **当前 `sessionId` 下活跃 L1** | **L2/Semantic**、**L3** |
| **撤销跨会话记忆 / 清空偏好（LTM）** | **L2 + Semantic 叙事块**（**§9 `FR-MEM05`**） | **L3**；**不** **默示** **删** **其它用户** **数据** |

**不** **默认可** **静默** **删** **L3** **法定留存**。

---

## 5. 上下文注入优先级（Runtime 拼装序 · 概念）

**后者** **不得** **覆盖** **前者** **已锁** **之** **安全/闸** **语义**（**同** **字段** **冲突时** **以** **更严** **或** **`prompt-management`** **冻结** **为准**）：

1. **平台策略 / Kill / 有效配置快照**（[`execution.md`](./execution.md) **§1 步 2**）  
2. **本次** **`executionId`** **已确认** **之** **类型 A 事务参数**（**写**）  
3. **本回合** **用户** **显式** **输入**  
4. **本** **`executionId`** **归因** **之** **工具结果**（**新鲜度** **须** **满足** **trade-assistance/确认卡** **叙事**）  
5. **可选** **L2** **用户偏好**（**若** **启用**）  
6. **可选** **Semantic** **摘要块**（**若** **产品** **单独** **解冻**）

---

## 6. Workflow memory vs User memory

- **Workflow memory**：**同** **`executionId`** **内** **Planner/编排** **为** **完成本单** **所** **需** **之** **结构化中间结论**（**仍属** **L1** ** unless** **`design` 另有持久槽**）。  
- **User memory**：**L2** **与** **可选 Semantic** — **须** **与** **[`goals/README.md`](../domains/agent/goals/README.md)** **`Goal`** **约束块** **对读**；**升格 SSOT** **前** **不得** **强绑** **`routing-engine`**。

---

## 7. 抽检与旅程

- **Eval**：[`evals/scenarios.md`](../evals/scenarios.md) **`eval.context.session_execution_tool_bind`**；**Memory GWT** → [`evals/memory-runtime.md`](../evals/memory-runtime.md)。  
- **旅程原则**：[`journey-validation.md`](../../../product/journey-validation.md) **§1**（**Memory** **与** **`context-management` §2** **可对齐**）。

---

## 8. Narrative Memory 对照（评审用 · 非独立契约 SSOT）

**用途**：把业界/实现侧常称的 **Narrative Memory（叙事记忆）** **对齐到** **本篇 §2～§6** **既有分层**，便于评审 **复用** **或** **升格 FR**。**本文** **不** **新增** **「Narrative Memory」** **为** **登记枚举**；**升格前** **不得** **单独** **作为** **对外承诺**。

### 8.1 业界常见含义（工作定义 · 评审口径）

| **子类（常见叫法）** | **典型内容** | **产品关切** |
|----------------------|--------------|--------------|
| **Session narrative** | 同一会话内「我们刚才聊了什么」的压缩 storyline | 连贯多轮、少重复澄清 |
| **Task / workflow narrative** | 单次 Goal 内步骤进展（已确认什么、卡在哪） | 写路径、类型 A、Planner 续跑 |
| **User story / profile narrative** | 跨会话用户画像式摘要（风格、常交易对、风险偏好叙述） | 个性化 vs 合规/幻觉 |
| **Outcome narrative** | 已发生业务结果的口语化 recap（「上次那单 UNKNOWN 后来…」） | 不得冒充当前交易所真值 |

### 8.2 → 本仓 Memory 分层映射

| **Narrative Memory 子类** | **主要映射** | **Episodic / Semantic** | **默认 TTL** | **注入序（§5）** | **本阶段承诺** |
|---------------------------|--------------|---------------------------|--------------|------------------|----------------|
| **Session narrative** | **L0**（近轮原文 + **可选** 回合内 rolling summary） | **Episodic**（摘要由 Episodic 派生） | **热**（随 session） | **③ 本回合用户输入** 之后、**④ 之前** 或 **并入 L0 窗口** | **隐含于** 会话上下文；**无** 独立 FR |
| **Task / workflow narrative** | **L1 · Workflow memory**（§6） | **Episodic** | **热**（随 `executionId`） | **④ 本 execution 工具结果** 同窗 | **已覆盖**；Planner 中间结论 **须** **`executionId` 归因** |
| **Confirmed write narrative** | **L1** 之子集（类型 A 已确认参数包 + 用户明示确认语义） | **Episodic** | **热** → 终局后回收 | **②**（写路径 **优先于** ③④） | **已覆盖**；**不得** 被 Session narrative **覆盖** |
| **User story / profile narrative** | **L2** + **可选 Semantic**（§3） | **Semantic**（须抽取/登记） | **热** 或 **更短**（[`architecture` v0](../../design/architecture.md)） | **⑤ L2** → **⑥ Semantic 块** | **§9 `FR-MEM*`**（**解冻前 TBD**） |
| **Outcome narrative（跨 execution）** | **L3 温/冷索引** **只读回放**；**进 Prompt 须** **重拉工具** 或 **明示 stale** | **Episodic 归档**；**非** 真值 | **温/冷** | **默认不注入**；若注入 **须** **低于** ④ **且带 `asOf`** | **禁止** **冒充** 当前行情/订单（**§3**、**`context-management` §2**） |
| **Goal 约束叙事** | **[`goals/README`](../domains/agent/goals/README.md)** **结构化 Goal** + **L1/L2** | **Semantic 倾向** | **随 Goal 寄存器 MR** | **与** **⑤⑥** **同级或更前**（**不得** 弱于 Safety） | **评审范例**；**非** SSOT **直至** **会签 `routing-engine`** |

### 8.3 与 Workflow memory / User memory（§6）细拆

| **叙事来源** | **Workflow memory** | **User memory** |
|--------------|---------------------|-----------------|
| 「本单进行到哪一步」 | ✓ **主宿主** | ✗ |
| 「用户常做 BTC 现货、偏保守」 | ✗（除非仅为本单中间结论） | ✓ **L2 / Semantic** |
| 「三小时前 UNKNOWN 那笔后来查到了」 | ✗ **默认不进 Prompt** | **仅** **经** **只读重查** **或** **带 stale 的 recap** |
| **Planner 决策摘要** | ✓ **L1** | ✗ |

### 8.4 反污染与交易真值（MUST · 与 Narrative 相关）

1. **Narrative 摘要不得升级真值**：任何 **跨轮/跨 execution** **叙事** **不能** **替代** **本 execution** **Fresh 工具结果** **驱动** **类型 A 或写** — **同** **`context-management` §2** **第三行**。  
2. **Semantic 叙事须可撤销**：用户 **「清空会话/撤销记忆」** **须** **定义** **是否** **触及** **L2/Semantic 叙事块** — **§4** **显式删除**。  
3. **观测分离**：**L3** **完整 episode**（工具 I/O、审计）**可** **长于** **注入用 narrative**；**禁止** **把 L3 全量** **当** **Narrative Memory** **无界灌入模型**。

### 8.5 升格决策树（复用 vs 新立 FR）

| **若产品要…** | **建议** | **须补文档/闸门** |
|---------------|----------|-------------------|
| **仅** 同会话少重复、连贯回复 | **复用 L0** + **`context-management` 压缩** | **无** 新 FR；实现对齐 **§5 注入序** |
| **单次下单/分析** 内续跑、记卡面 | **复用 L1 Workflow memory** | **SC-AO-05** 归因；**eval.context.session_execution_tool_bind** |
| **跨会话记住** 「用户偏好/口吻/常交易对」 | **L2 + Semantic 解冻** | **§9 `FR-MEM*`** + **`prompt-management` 注入闸** + **用户可见开关/删除** |
| **自动增长** 「用户人生故事线」 | **默认不做** | **专项 MR** + **合规/PII** + **TTL 上限**；**不得** **默认长热留存** |
| **把 Narrative Memory 登记为 Runtime 枚举** | **新立类型学前置评审** | **本篇 §8 升格为 §2 行** **或** **独立分卷**；**OpenAPI 键** **随 design MR** |

### 8.6 建议 Eval（若解冻 Semantic / 跨会话 narrative）

**正式登记** → **§9.3** **`eval.memory.*`**。**摘要**：

| **Eval 方向** | **Then（摘要）** |
|---------------|------------------|
| **Session 连贯** | 同 `sessionId` **第二轮** **须** **引用** **第一轮已确认事实** **且** **不** **编造** **未发生写** |
| **跨 execution 不污染** | 新 `executionId` **问现价/余额** **须** **重拉工具** **或** **明示 stale** — **不得** **仅** **凭** **旧 narrative** **报数** |
| **撤销记忆** | 用户触发清空后 **Semantic/L2 narrative** **不得** **再注入** **除非** **用户重新显式提供** |

**互引**：[`goal-and-execution-paths.md`](../domains/agent/agent-orchestration/goal-and-execution-paths.md) **§1 复合型会话**；[`runtime-truth-source-map.md`](./runtime-truth-source-map.md) **Memory 行**；**Telegram UX** → [`../domains/agent/telegram/overview.md` §2.7](../domains/agent/telegram/overview.md)。

---

## 9. 跨会话 Semantic Narrative（`FR-MEM*` · 解冻草案）

**范围**：**User story / profile narrative**（§8.2）— **L2 用户偏好** **与** **可选 Semantic 摘要块** **注入主 Prompt 上下文**。**不含**：L0/L1 **已覆盖** **之** **会话内/workflow 叙事**；**不含** **无界自传 / 全历史 L3 灌入**。

**契约状态**：**草案 · 解冻前 TBD** — **未** **单独** **满足** [`contract-closure.md`](../contract-closure.md) **§1.2** **不得** **对客宣称「已记住你」** **类** **闭环**。**OpenAPI 形状 SSOT** → [`memory-runtime-schemas.yaml`](../../openapi/components/memory-runtime-schemas.yaml)（**`SemanticNarrativeBlock`/`AgentRuntimeMemoryContext`**）；**注入管线** → [`design/memory-runtime-injection.md`](../../design/memory-runtime-injection.md)。

**互引**：[`prompt-management/runtime-injection`](../domains/admin/prompt-management/runtime-injection.md) **§2**（**块 5 · Runtime Context**）；[`context-management.md`](./context-management.md) **§2**；[`sessions.md`](./sessions.md)；[`goals/README.md`](../domains/agent/goals/README.md)；[`hallucination.md`](../observability/hallucination.md)。

### 9.1 功能需求 · `FR-MEM*`

| ID | 陈述 |
|----|------|
| **FR-MEM01** | **跨会话 Semantic Narrative** **须** **经** **产品/实例级显式开关** **`FEATURE_SEMANTIC_NARRATIVE`**（**[`trading-agent-config/keys`](../domains/admin/trading-agent-config/keys.md) §2**；**或等价 `configKey`**）**启用**；**默认 OFF** **时** **Runtime MUST NOT** **向** **主 Prompt 装配路径** **注入** **§9.2 命题类** **Semantic 块**（**L2 运营配置** **仍可按** **既有** **配置域** **生效**）。**装配快照** **须** **映射** **`semanticNarrativeEnabled`** **与** **开关一致**。 |
| **FR-MEM02** | **可写入 Semantic 块的命题类型 MUST** **在所内 allowlist 登记**；**下限白名单**（**可扩展，扩展须 MR**）：**(a)** **交互偏好**（语言桶、回复详略）；**(b)** **自选关注 symbol 列表**（**须** **用户明示或确认**）；**(c)** **自述风险档位/保守程度**（**非** **投顾结论**）；**(d)** **已拒绝的能力边界复述**（**如** **「不要主动推下单」**）。**禁止默认写入**：**余额/持仓/订单终态/最新价** **等** **须** **工具闭环** **之** **交易所真值**。 |
| **FR-MEM03** | **Semantic 块注入位序 MUST** **遵守** **§5** **之** **⑤ L2 → ⑥ Semantic**；**不得** **高于** **② 类型 A 已确认参数** **或** **④ 本 execution 工具结果**；**与 Safety/Kill 冲突时** **以** **更严** **为准**。 |
| **FR-MEM04** | **跨 `executionId` 之 Semantic 叙事 MUST NOT** **单独** **作为** **类型 A 参数来源** **或** **`call_exchange_write` 事实依据**；**写路径** **须** **仍** **走** **fresh 读 + 类型 A**（**同窗** **`context-management` §2 第三行**）。 |
| **FR-MEM05** | **用户 MUST** **可在 Telegram 对话内** **(a)** **查看** **当前已记住偏好之摘要**（**人话，非** **内部 JSON**）；**(b)** **一键撤销/清空** **L2+Semantic 叙事块**（**不** **默示** **删除** **L3 法定留存**）。**撤销后** **下一回合起** **不得** **再注入** **被清命题** **除非** **用户重新明示**。 |
| **FR-MEM06** | **Semantic 块 MUST** **受** **TTL 与体量上限** **约束**：**默认** **不得** **长于** **[`architecture` v0](../../design/architecture.md)** **热级 Semantic 口径**；**单块 token/字符顶** **须** **`design`/ai-settings MR** **冻结**；**超限** **须** **确定性裁剪或拒绝 Publish 级注入** **并** **可观测**。 |
| **FR-MEM07** | **命题抽取/更新 MUST** **可观测**：**须** **关联** **`userId`（±实例）**、**来源 `sessionId`/`executionId`（若适用）**、**`updatedAt`**；**禁止** **向** **用户** **或** **模型** **注入** **Secret/API Key/完整** **PII**。 |
| **FR-MEM08** | **Semantic 命题更新 MUST NOT** **绕过** **`prompt-management` Publish 兼容闸** **所禁** **之** **越狱/特权类字面**；**注入宿主键** **须** **在** **`runtime-injection` §2.4.1** **映射层** **显式绑定**（**勿静默丢字段/勿混 raw 上游 JSON**）。 |
| **FR-MEM09** | **Semantic 命题写入/更新 MUST** **遵守** **下列流水线**：（**a**）**仅** **从** **用户** **本轮或近期** **明示话束** **或** **经** **用户确认** **之** **类型 C 卡** **抽取** — **禁止** **静默** **从** **工具 JSON/模型草稿** **默认落库**；（**b**）**命中** **allowlist（FR-MEM02）** **且** **语义** **无歧义** **时** **可** **直接登记**；**对** **(b) symbol 列表** **等** **易误读项** **须** **二次确认** **或** **等价** **显式 yes** **后** **方可** **持久化**；（**c**）**同类型命题冲突** **时** **以** **更新时刻** **较新** **之** **用户明示** **为准** **确定性覆盖**；（**d**）**每次** **成功写入/覆盖/撤销** **须** **可观测**（**建议事件** **`agent.memory.semantic_updated`** **携带** **`userId`、`propositionType`、`sessionId`/`executionId`、`updatedAt`**）。 |

### 9.2 Runtime Context 形状下限（Prompt 宿主 · 示意）

**键名以 OpenAPI/`agentContext` 为 SSOT**；下表为 **产品 camelCase 下限**：

| 字段（可选 · 按需存在） | 说明 |
|-------------------------|------|
| `semanticNarrativeEnabled` | **与** **FR-MEM01** **同窗**；**false/缺失** → **不注入** **下列块** |
| `semanticNarrativeBlock` | **allowlist 命题** **之** **裁剪摘要**（**非** **全量 L3**） |
| `semanticNarrativeAsOf` | **摘要生成/刷新时间锚** |
| `userMemoryRevokedAt` | **若** **用户已撤销** → **Runtime MUST NOT** **注入** **`semanticNarrativeBlock`** |
| `preferredSymbols` | **用户确认过的关注列表**（**⊂ FR-MEM02(b)**） |
| `interactionPreferences` | **语言/详略等**（**⊂ FR-MEM02(a)**） |

**缺块时**：Prompt **不得** **虚构** **「我记得你…」** **类** **跨会话事实** — **同窗** **`FR-MI03`/hallucination**。

### 9.3 验收 · `SC-MEM*`

| ID | **Given / When / Then（摘要）** | **同窗 `FR-MEM`** |
|----|--------------------------------|-------------------|
| **SC-MEM01** | **Given** **开关 OFF** **或** **`semanticNarrativeEnabled=false`** · **When** **任意只读/写回合装配 Prompt** · **Then** **观测/Prompt 宿主** **无** **`semanticNarrativeBlock`**（**或** **等价空**）；**模型回复** **不得** **声称** **跨会话记忆已启用** | **FR-MEM01** · **`SC-CH-TG-MEM-03`** |
| **SC-MEM02** | **Given** **开关 ON** · **When** **用户在本会话明示**「以后默认只看 BTC、回复简短」**且** **系统完成登记** · **Then** **新 session** **装配含** **allowlist 内命题**；**不含** **未登记类型**（**如** **杜撰余额**）；**查看时** **须** **§2.7.2 结构** | **FR-MEM02**、**07** · **`SC-CH-TG-MEM-01`** |
| **SC-MEM03** | **Given** **Semantic 块含**「用户关注 BTC」 · **When** **新 `executionId` 问「BTC 现价」** · **Then** **须** **调用** **`tool.market.ticker`（或矩阵等价）** **再答**；**不得** **仅** **凭 narrative** **报具体数值** | **FR-MEM04** |
| **SC-MEM04** | **Given** **已存在 Semantic 块** · **When** **用户触发「清空记忆/不再记住」** · **Then** **下一回合起** **不注入** **被清块**；**用户可见一句确认** | **FR-MEM05** · **Telegram** **[`telegram/overview` §2.7.3](../domains/agent/telegram/overview.md)** · **`SC-CH-TG-MEM-02`** |
| **SC-MEM05** | **Given** **Semantic 块接近/超过体量顶** · **When** **装配** · **Then** **确定性裁剪或拒注入** **+** **可观测事件**；**不得** **静默截断致** **半条命题** **冒充完整偏好** | **FR-MEM06** |
| **SC-MEM06** | **Given** **交错两用户/两 `sessionId` fixture** · **When** **装配** · **Then** **Semantic 块** **仅** **属** **当前 `userId`/绑定实例** — **同窗** **`eval.context.session_execution_tool_bind`** | **FR-MEM07**、**`context-management` §2** |
| **SC-MEM07** | **Given** **写路径** · **When** **Semantic 块与类型 A 卡面字段冲突** · **Then** **以** **类型 A + fresh 工具** **为准**；**Semantic** **不得** **覆盖** **已确认数量/价格** | **FR-MEM03**、**04** |
| **SC-MEM08** | **Given** **开关 ON** · **When** **用户话束** **模糊**（**如** **「记住我」** **未说明** **记什么**）**或** **含** **禁止类型**（**余额/现价**）· **Then** **须** **澄清/拒写** **或** **类型 C 确认** **后** **方可** **登记**；**禁止** **静默写入** | **FR-MEM02**、**09** |
| **SC-MEM09** | **Given** **上下文超 budget** · **When** **装配** · **Then** **裁剪顺序** **符合** **§11**；**须** **可观测** **`agent.context.memory_trimmed`**（**或等价**）；**②④** **Facts** **不得** **被删** | **FR-MEM06**、**§11** |

### 9.4 Eval 登记（与 §8.6 升格）

| `evalSetId` | 版本 | 构造要点 | 映射 |
|-------------|------|----------|------|
| **`eval.memory.semantic_gate_off`** | `0.1.0` | **开关 OFF** **跑** **只读询价** | **SC-MEM01** |
| **`eval.memory.semantic_preference_persist`** | `0.1.0` | **开关 ON** → **用户明示偏好** → **新 session 续聊** | **SC-MEM02** |
| **`eval.memory.semantic_no_stale_price`** | `0.1.0` | **块内「关注 BTC」** + **新 execution 问价** | **SC-MEM03** |
| **`eval.memory.semantic_user_revoke`** | `0.1.0` | **撤销记忆** **后再问「你还记得吗」** | **SC-MEM04** |
| **`eval.memory.semantic_write_no_override`** | `0.1.0` | **Semantic 与类型 A 冲突之写路径负例** | **SC-MEM07** |
| **`eval.memory.semantic_write_confirm`** | `0.1.0` | **模糊「记住我」/ 关注 symbol 未确认** → **须澄清或确认后写入** | **SC-MEM08** |
| **`eval.memory.budget_trim`** | `0.1.0` | **构造超 budget** → **裁剪序 §11** + **`memory_trimmed` 观测**；**②④** **仍在** | **SC-MEM09** |

**Eval 索引 SSOT**：[`evals/scenarios.md`](../evals/scenarios.md) **须** **登记上表行** **后** **方可** **CI 引用**。**GWT 构造专卷** → [`evals/memory-runtime.md`](../evals/memory-runtime.md)。**Walkthrough 回归束** → [`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md#runtime-walkthrough-crosscut) **Goal-MEM-LTM**。

### 9.5 解冻 MR 检查单（节选）

- [ ] **`FEATURE_SEMANTIC_NARRATIVE`**（**[`keys` §2`](../domains/admin/trading-agent-config/keys.md)**）**默认 OFF** **与** **FR-MEM01** **同窗**。  
- [ ] **allowlist** **与** **OpenAPI `semanticNarrativeBlock` 形状** **同窗 MR**；**写入流水线** **对拍** **FR-MEM09**。  
- [ ] **STM 清空 vs LTM 撤销** **UX/意图** **对拍** **§13**、**Telegram §2.7～§2.8**、**`eval.memory.budget_trim`**。  
- [ ] **`runtime-injection` §2** **增** **Semantic 块映射** **+ Publish CI** **不** **与** **Schema 冲突**。  
- [ ] **Telegram** **撤销/查看** **话术** **链** **[`telegram/overview` §2.7](../domains/agent/telegram/overview.md)**、**`SC-CH-TG-MEM-01～03`**、[`response-format` §1](../prompts/shared/response-format.md) **用户问题解决面**（**在对话内闭环**）。  
- [ ] **Ticker 映射**：[`market-runtime-payload` §3.3](../domains/agent/exchange-agent/market-runtime-payload.md)、**`SC-MRP01`**、**`eval.market.ticker_facts_mapping`**。  
- [ ] **对客宣称前** **[`contract-closure` §1.2](../contract-closure.md)** **六款** **或** **§3.0 分期叙事** **明示** **能力边界**。

---

## 10. 会话内召回路径（STM / LTM · 实现对签）

**职责**：把 **「用户发一条消息后，短期/长期记忆如何进入 Prompt」** 写成 **可对签步骤**；**不** **替代** [`runtime-injection` §1](../domains/admin/prompt-management/runtime-injection.md) **块序**。

### 10.1 触发点（每条 inbound）

**同窗** [`execution.md` §1](./execution.md) **步 1～5**：

| **步** | **动作** | **记忆相关** |
|--------|----------|--------------|
| **1 接入** | 解析 **`sessionId`**、绑定 **`userId`/实例** | **召回键** **锚定** |
| **3 起票** | 分配 **`executionId`** | **L1 作用域** **开始** |
| **5 上下文装配** | **STM/LTM 召回 + 裁剪** → **块 5 Runtime Context** + messages | **本节核心** |

### 10.2 短期记忆（STM）召回 · MUST

1. **读 L0**：**同一 `sessionId`** 下 **近轮 messages**（及 **可选** rolling summary）；**join** **当前 inbound 回合**。  
2. **读 L1**：**同一 `executionId`** 下 **类型 A 已确认包**、**本 execution **`agent.tool.call`** 成功快照**、Planner 中间摘要。  
3. **写路径澄清（增补）**：**同一 `executionId`** **须** **注入** **[`ClarifySessionSnapshot.resolvedSlotsSoFar`](../domains/agent/agent-orchestration/clarify-session.md) **人话摘要** — **并入 Prompt 块 5 Runtime Context（步骤 4 之前）**；**`SC-CLARIFY-03`**。  
4. **写入 Prompt**：**③ 用户输入**、**④ 工具 Facts**（含 [`market-runtime-payload`](../domains/agent/exchange-agent/market-runtime-payload.md) **`userVisibleMarketData`** 等）— **§5 优先级**。  
5. **新 `executionId`**：**不得** **仅** **凭** **前序 execution L1** **报** **行情/余额/订单** — **须** **重拉工具** **或** **明示 stale**（**`context-management` §2**）。

### 10.3 长期记忆（LTM）召回 · MUST

1. **前置**：**`semanticNarrativeEnabled=true`**（**§9 `FR-MEM01`**）**且** **无** **`userMemoryRevokedAt`**。  
2. **读 L2**：实例/用户 **配置域** **偏好**（**⑤**）。  
3. **读 Semantic 块**：**allowlist 裁剪后之** **`semanticNarrativeBlock`**（**⑥**）。  
4. **默认 OFF**：**跳过 2～3**；**禁止** **模型** **假称** **跨会话记忆**（**`SC-MEM01`**）。  
5. **用户主动查看/撤销**：**不** **改变** **被动注入规则** — **Telegram** [`overview` §2.7](../domains/agent/telegram/overview.md)。

### 10.4 并发 · callback · 异步续跑（STM 归因 · MUST）

| **场景** | **须** |
|----------|--------|
| **类型 A `callback_query`** | **L1** **绑定** **发起该卡之 **`executionId`**；**禁止** **用** **其它 execution** **之** **未确认草稿** |
| **同 session 并行两 execution**（若产品允许） | **每条 inbound** **须** **显式** **归属** **其一 **`executionId`**；**工具回填** **不得** **交叉** |
| **`edit_message` 续写卡面** | **L1** **仍以** **原 execution** **为准**；**不得** **因 edit** **新建** **无票** **写路径** |
| **session 内 Prompt 包冻结** | **同窗** [`sessions.md` §2](./sessions.md)、[`runtime-injection` §3](../domains/admin/prompt-management/runtime-injection.md) |

### 10.5 召回后写回（episode 更新）

**写入规则 SSOT**：**§15**（**allowlist/denylist** — **非** **全量聊天记录**）。

**工具成功 / 用户确认 / 编排步进后** **须** **按 §15.4** **更新** **L1**（**同 **`executionId`**）；**回合结束** **按 §15.1** **更新** **L0**。**观测** **须** **可 join** **`sessionId` + `executionId`**（**`FR-MEM07`** **同窗**）。

---

## 11. 上下文预算与裁剪（召回失败模式 · MUST）

**宿主执法条**：[`context-management.md` §1～§2](./context-management.md)；**数值** **`design`/ai-settings MR**。

**超 budget 时裁剪顺序**（**先裁后者**；**禁止** **静默** **删除** **②④** **写/读关键 Facts**）：

1. **L0** 远端轮次原文 → **L0 rolling summary** **再压缩**  
2. **⑥ Semantic 块** **次要句**（**不得** **删光** **allowlist 命题** **致** **半条误导** — **`SC-MEM05`**）  
3. **⑤ L2** **非安全相关** **说明性字段**  
4. **仍不足** → **可观测** **拒扩 / 短答 / 请用户收窄** — **不得** **伪造** **未召回之 Facts**

**须可观测事件**（**建议名 · OpenAPI 终裁**）：`agent.context.memory_trimmed` **携带** **`trimmedLayers[]`、`sessionId`、`executionId`**。

---

## 12. 设计闭环自检（Memory · MR / 评审勾选）

**用途**：回应 **「规格是否合理且可落地」** — **与** **§9.5、[`implementation-alignment` §6](../domains/agent/agent-orchestration/implementation-alignment.md)** **同窗**。

- [ ] **STM**：同 **`executionId`** **类型 A 与 tool 结果** **可字段级对账** **Prompt 块 5 / messages**。  
- [ ] **STM 跨 execution**：问现价/余额 **观测有** **新 **`agent.tool.call`** **或** **明示 stale**（**`eval.memory.semantic_no_stale_price`** **精神适用于全部 Facts**）。  
- [ ] **Ticker 映射**：**`GET /sapi/v2/ticker`** **`last`→`lastPrice`** 等 — **[`market-runtime-payload` §3.3](../domains/agent/exchange-agent/market-runtime-payload.md)**、**`eval.market.ticker_facts_mapping`**。  
- [ ] **LTM 开关 OFF**：**无** **`semanticNarrativeBlock` 注入**（**`SC-MEM01`**）。  
- [ ] **LTM 撤销**：**`userMemoryRevokedAt` 后不再注入**（**`SC-MEM04`**、**Telegram §2.7.3**）。  
- [ ] **并发 callback**：**§10.4** **归因** **有** **集成测 ** **或** **eval 登记**。  
- [ ] **预算裁剪**：**§11 顺序** **有** **单测/日志**；**②④** **不被静默删**（**`eval.memory.budget_trim`**）。  
- [ ] **STM 清空**：**§13** **与** **LTM 撤销** **分流**；**`eval.memory.session_clear_stm`**。  
- [ ] **STM 四原则硬闸**：**§16.1** **装配前** **失效→过滤→注入→校验** — **`eval.memory.stm_governance_regression`** · **`FR-STM11`**。  
- [ ] **STM 写入准入**：**§15 denylist** — **`eval.memory.stm_write_allowlist`**。  
- [ ] **idle/TTL stale + Resume**：**§14.6** — **`eval.memory.idle_default_stale`** · **`eval.memory.resume_classifier_gate`** · **（fallback only）** **`eval.memory.idle_resume_or_new_topic`**。  
- [ ] **Semantic 写入**：**FR-MEM09** **确认/拒写** — **`eval.memory.semantic_write_confirm`**。  
- [ ] **对客宣称 LTM**：**已过** **`contract-closure` §1.2** **或** **分期叙事**。

---

## 13. 短期记忆（STM）· 清空本会话（`FR-STM*`）

**范围**：**L0 + 当前 `sessionId` 下活跃 L1** — **不含** **跨会话 L2/Semantic（§9）**。**默认** **已承诺路径**（**与会话上下文同窗**）；**本节** **补** **「清空本会话」** **与** **LTM 撤销** **之** **边界**。

**互引**：[`sessions.md`](./sessions.md)；[`telegram/overview` §2.8](../domains/agent/telegram/overview.md)；[`prompts/intents/analysis` §6](../prompts/intents/analysis.md)。

### 13.1 功能需求 · `FR-STM*`

| ID | 陈述 |
|----|------|
| **FR-STM01** | **用户触发「清空本会话 / 重新开始 / 新话题」** **时** **Runtime MUST** **清除** **当前 `sessionId` 之 L0 窗口** **及** **该 session 下未终局之 L1 草稿/工具快照注入源** — **使** **下一回合 Prompt** **不得** **再含** **被清轮次** **之** **messages/rolling summary**。**实现** **可** **(a)** **原地清空 L0/L1 槽** **或** **(b)** **分配新 `sessionId`** — **`design` MR 冻结**，**须** **可观测** **二者之一**。 |
| **FR-STM02** | **STM 清空 MUST NOT** **触及** **L2/Semantic 叙事块**、**L3 审计/账务** — **除非** **用户** **在同一流程** **显式** **选择** **LTM 撤销**（**§9 `FR-MEM05`**）。 |
| **FR-STM03** | **进行中之类型 A 确认卡** **（`waiting_confirmation`）** **若** **存在** **于** **当前 session**：**STM 清空前 MUST** **取消/过期该卡** **或** **二次说明** **「将放弃未确认操作」** — **禁止** **清空后** **仍** **可用** **旧 callback** **触发写**。 |
| **FR-STM04** | **STM 清空 MUST** **可观测**（**建议事件** **`agent.memory.session_cleared`** **携带** **`sessionId`、`userId`、`clearedAt`**）；**用户可见** **一句确认** **+** **下一步**（**同窗** [`telegram/overview` §2.8](../domains/agent/telegram/overview.md)）。 |
| **FR-STM05** | **交易 Agent**：**STM 内** **未确认写参、工具价量快照、澄清槽** **MUST NOT** **自动升格** **LTM/Semantic** — **同窗** **§14.3**、**FR-MEM09**。 |
| **FR-STM06** | **热面回收或 `ClarifySession`/`pending_confirm` 失效后**，**下一 inbound MUST NOT** **凭** **已失效 STM/L1** **驱动** **`call_exchange_write`** **或** **载货类型 A** — **§14.2**。 |
| **FR-STM07** | **写路径 idle/TTL 先达或 ambiguous 续聊 inbound**，**须** **走** **§14.6 stale + Resume 门控** **（默认 **`stale_prior_write`**）** **或** **等价** **重意图 + Fresh Facts**。

### 13.2 验收 · `SC-STM*`

| ID | **Given / When / Then（摘要）** | **同窗 `FR-STM`** |
|----|--------------------------------|-------------------|
| **SC-STM01** | **Given** **同 session 多轮对话** · **When** **用户「重新开始」** · **Then** **下一回合 Prompt** **无** **被清轮次** **原文**；**模型** **不得** **引用** **已清事实** **作** **当前真值** | **FR-STM01** |
| **SC-STM02** | **Given** **已存在 Semantic 块（LTM ON）** · **When** **仅 STM 清空** · **Then** **新 session/回合** **仍** **可** **注入** **未撤销之 Semantic**；**用户** **未** **触发** **§2.7.3** **时** **偏好** **仍在** | **FR-STM02**、**`SC-MEM04`** **负例** |
| **SC-STM03** | **Given** **未确认类型 A 卡** · **When** **STM 清空** · **Then** **旧 callback** **不得** **再触发写**；**用户** **可见** **放弃未确认操作** **之说明**（**若适用**） | **FR-STM03** |

### 13.3 Eval 登记

| `evalSetId` | 版本 | 构造要点 | 映射 |
|-------------|------|----------|------|
| **`eval.memory.session_clear_stm`** | `0.1.0` | **多轮后「重新开始」** → **Prompt 无旧轮**；**LTM 块** **仍在**（**开关 ON fixture**） | **SC-STM01**、**02** |

**Eval 索引**：[`evals/scenarios.md`](../evals/scenarios.md) · **GWT** [`evals/memory-runtime.md`](../evals/memory-runtime.md) **§4**。

---

## 14. 交易 Agent · STM/LTM 治理（Telegram · 防错乱写 · MUST）

**背景**：Telegram **无** **独立「新话题/线程」** UI；**Chatbot 级记忆错乱** **多为** **答非所问**，**交易 Agent** **错乱** **可** **误触发** **写路径/过期确认**。**本节** **冻结** **STM 控制、失效、升格 LTM、召回 LTM** **之** **产品矩阵** — **不** **放宽** **`context-management` §2**。

**互引**：[`clarify-session.md`](../domains/agent/agent-orchestration/clarify-session.md) **§2.1～§2.3**；[`telegram/overview` §2.7～§2.8](../domains/agent/telegram/overview.md)；[`architecture` Memory 留存 v0](../../design/architecture.md)；**热面回收默认** **session 空闲 ≥24h** **或** **execution 终局后 ≥2h**（**先达者**）。

### 14.1 STM 承载范围与写路径风险

| **STM 内容（L0/L1/BFF）** | **用途** | **若错乱/过期的风险** |
|---------------------------|----------|------------------------|
| **L0** 近轮 messages / rolling summary | 连贯多轮、少重复问 | **错承接意图** → **误进写澄清** |
| **L1** 本 `executionId` 工具快照、类型 A 草稿 | 本单编排/workflow | **过期价/余额** → **错参类型 A** |
| **`ClarifySessionSnapshot`** | 写澄清槽位 | **僵尸澄清** → **复读/误续单** |
| **`pending_confirm`（类型 A）** | 写授权 | **过期 callback** → **误下单** |

**MUST NOT 由 STM 单独承担（交易真值）**：**余额、持仓、现价、订单终态、经济敏感写参** — **须** **Fresh 工具 + 类型 A（写）** 或 **明示 stale**（**§5 ②④**、**`FR-MEM04`**）。

### 14.2 STM 清空或失效 · 触发矩阵（MUST）

| **触发** | **须执行（摘要）** | **需求锚点** |
|----------|-------------------|--------------|
| **用户「新话题 / 重新开始 / 清空本次对话」** | **清 L0 + session 活跃 L1**；**取消/过期** **未确认类型 A**；**`ClarifySession` abandoned** | **FR-STM01～03** · **§13** · **Telegram §2.8** |
| **用户「不要了 / 取消」等放弃写路径** | **`ClarifySession.abandoned`**；**不** **再注入** **写澄清 STM 摘要** | **clarify-session §2.1.1** · **`SC-CLARIFY-06`** |
| **澄清 session `expiresAt` 到达** | **等同 §14.6 先达 stale**（**默认 TTL 900s**）；**下条 inbound** **§2.3 + Resume 门控** — **不得盲续 **`pendingClarifyKind`** | **clarify-session §2.4.1** · **§14.6** |
| **类型 A `pending_confirm` TTL 到达** | **确认失效**；**旧 `cf:*` 不得写**；**可** **恢复澄清**（**§1.1 · v0 默认**） | **Telegram §2.3** · **ADR-001** · **clarify-session §1.1** |
| **类型 A 存活 + 写澄清并存** | **§14.6 idle/TTL** **不得** **使 **`pending_confirm`** **失效**；**澄清 snapshot 冻结** — **idle inbound 走类型 A 生命周期** | **clarify-session §1.1** · **§14.6.0 豁免** |
| **`executionId` 达终局**（`completed`/`failed`/`cancelled`/`unknown_pending` 等） | **该 execution 之 L1** **不得** **驱动新写**；**+2h** **热面回收**（**v0 默认**） | **`context-management` §2** · **`architecture` 热级** |
| **写路径 idle/TTL 先达者**（**`STM_IDLE_RESUME_PROMPT_SEC` 或 `STM_CLARIFY_SESSION_TTL_SEC`**）**且仍有写澄清/写 L1** | **默认 **`lifecycleState=stale`** · 退出活跃 L1 · 写温索引** | **§14.6.1** · **`FR-STM12`** |
| **session 空闲 ≥24h**（**v0 默认**） | **热面回收** **L0/L1**；**下条 inbound** **须** **新意图起票** | **`architecture` 热级** · **§14.4** |
| **绑定/子账户 scope 变更生效** | **新执行** **须** **新 scope**；**旧 L1 私有读/写参** **不得** **串户** | **`sessions.md` §2** |
| **用户 STM 清空（§13）** | **同上** **用户主动行** | **FR-STM01～04** |

**禁止**：**仅** **因** **STM 仍含** **「上次要买 BNB」** **即** **自动续写路径** **而不** **重跑 Parser + Resolver** — **同窗** **clarify-session §2.3**、**`SC-CLARIFY-05`**。

### 14.3 STM → LTM（Semantic）· 什么能升格、什么永远不能

**原则**：**交易态、订单态、账户数值** **永不** **自动从 STM 升格 LTM**。

| **来源（STM 中常见）** | **可否升格 LTM** | **条件** |
|------------------------|------------------|----------|
| **交互偏好**（语言、详略） | ✓ | **用户明示** + **FR-MEM02(a)** + **FR-MEM09** |
| **关注 symbol 列表** | ✓ | **用户明示或二次确认** + **FR-MEM02(b)** |
| **风险自述**（偏保守等） | ✓ | **明示** + **FR-MEM02(c)** |
| **能力边界复述**（「别主动推下单」） | ✓ | **明示** + **FR-MEM02(d)** |
| **未确认写参、澄清槽、类型 A 草稿** | ✗ | **仅 L1 热数据** |
| **工具返回的余额/价/持仓/订单** | ✗ | **禁止 FR-MEM02 默认写入** |
| **模型推断的「用户想买的量」** | ✗ | **INV-008/009** |

**流水线 SSOT**：**FR-MEM09** — **禁止** **静默** **从工具 JSON/模型草稿落库**。

### 14.4 LTM 召回 · 何时注入 Prompt

| **条件** | **Then** |
|----------|----------|
| **`FEATURE_SEMANTIC_NARRATIVE` / `semanticNarrativeEnabled=true`** | **可** **召回 ** **allowlist 命题** |
| **`userMemoryRevokedAt` 已设** | **MUST NOT** **注入** **`semanticNarrativeBlock`** |
| **写路径 / 新 `executionId` 问价查余额** | **可** **用 LTM** **知「用户关注 BTC」** **但** **须** **Fresh 工具报数** — **`SC-MEM03`** |
| **类型 A 参数、本 execution 工具 Facts** | **LTM 不得覆盖** — **`SC-MEM07`** |
| **开关 OFF（默认）** | **无 LTM 注入**；**不得** **假称** **「我记得你」** — **`SC-MEM01`** |

**注入位序**：**§5** **⑤ L2 → ⑥ Semantic** — **低于** **② 类型 A 已确认** **与** **④ 本 execution Facts**。

### 14.5 Telegram · 无「新话题」UI 之补偿（MUST · 产品）

**问题**：**不能假设用户会用自然语言** **说清** **「新话题」**。

**须** **至少提供一种** **常驻、非类型 A** **之** **入口**（**`design` MR 冻结具体形态**）：

| **入口（择一或多）** | **行为** |
|----------------------|----------|
| **`/new` 或 `/restart` BotCommand** | **等同** **FR-STM01** **意图** → **§2.8.2** |
| **会话内常驻 `ReplyKeyboard` / Menu** **「新话题」** | **同上** |
| **空闲 ≥24h 后首条 inbound** | **宜** **类型 C 短句** + **可选** **「继续上次 / 新话题」** **二选一**（**非** **类型 A**）— **§14.6** |

**验收**：**`SC-CH-TG-STM-03`**（**§5** · [`telegram/overview`](../domains/agent/telegram/overview.md)）。

### 14.6 隔较久回来 · 默认 stale + Resume 门控（MUST）

**原则**：**不依赖**用户说「继续上一笔 / 新话题」— **主路径** **`STM_IDLE_DEFAULT_POLICY=stale_prior_write`**（**[`keys` §2.1](../domains/admin/trading-agent-config/keys.md)**）。**类型 C 续/新按钮**（**`cl:resume`/`cl:new`**）**仅** **可选 fallback**，**非** **主依赖**。

#### 14.6.0 触发 · 统一（MUST · 先达者）

**写路径上下文** **=** **未 `abandoned` 之 **`ClarifySessionSnapshot`** **或** **同 session 未终局写 **`executionId` L1**（**类型 A 草稿 / 未确认写参 · 无 snapshot 时仍适用**）。

**当存在写路径上下文** **且** **下列任一先达**：

| **条件** | **配置键 · 默认** | **Then** |
|----------|-------------------|----------|
| **A · session 空闲** | **`STM_IDLE_RESUME_PROMPT_SEC=1800`** | **进入 §14.6.1 stale** |
| **B · 澄清 TTL** | **`STM_CLARIFY_SESSION_TTL_SEC=900`** → **`expiresAt`** | **同上** — **与 A 独立计时 · 先达者生效** |
| **C · 下条 inbound 前已 stale** | — | **§14.6.2～§14.6.4** **全序** |

**互斥**：**§2.3 即时分流**（**放弃/只读/寒暄/新写意图**）**优先于** **等待 idle/TTL** — **不必等 30min**。**同窗** [`clarify-session` §2.4.1](../domains/agent/agent-orchestration/clarify-session.md)。

**类型 A 豁免（MUST）**：**`pending_confirm` 存活**（**`waiting_confirmation`**）**时** **§14.6.1 stale** **不得** **取消/改写类型 A** **或** **强制 abandoned 澄清** — **全序** **[`clarify-session` §1.1](../domains/agent/agent-orchestration/clarify-session.md)**。

**设计管线** → [`memory-runtime-injection` §2.4](../../design/memory-runtime-injection.md)。

#### 14.6.1 步 0 · 默认 stale（MUST · 先于 Prompt 装配）

| **动作** | **说明** |
|----------|----------|
| **标记 stale** | **`ClarifySessionSnapshot.lifecycleState=stale`** · **`staleAt=now`**（**有 snapshot 时**）；**无 snapshot 之写 L1** **须** **等价标记 execution 级 stale 并写温索引** |
| **退出活跃 L1** | **写澄清摘要 / `pendingClarifyKind` / 未终局写 L1** **不得** **进入 Prompt 活跃注入** — **等同默认新话题** |
| **温索引保留** | **须** **写入/更新 **`WarmExecutionEpisode`**（**一条人话摘要 + `resolvedSlotsSoFar` + `executionId` + `staleAt`**）— **L3/温层** **可检索** **·** **非** **messages 全量** |
| **禁止** | **盲续** **过期 clarify 模板** **或** **弹阻塞式「继续/新话题」** **作为唯一路径** |

**温索引多条**：**同 session 默认召回 **`staleAt` 最近一条** **写路径 episode** — **同窗** [`clarify-session` §2.4.3](../domains/agent/agent-orchestration/clarify-session.md)。

#### 14.6.2 步 1 · 重意图（MUST）

**每条 inbound** **须** **clarify-session §2.3** — **Parser/意图** **仅看** **本条话束** **（+ 可选 L0 近轮 · 不含 stale L1 写澄清）**。**stale 态下只读/寒暄/放弃** → **`abandoned=true`** — **§2.3 步 2/3**。

#### 14.6.3 步 2 · Resume 门控（规则优先 · 分类器仅 ambiguous）

| **分流** | **条件（示例）** | **Then** |
|----------|------------------|----------|
| **A · 明确新意图** | 新 symbol/新任务/只读/寒暄/放弃（**§2.1.1**） | **不召回** 温摘要 · **新 execution 或只读** · **stale session **`abandoned=true`** |
| **B · 明确续单（规则层 · bypass 分类器）** | 「刚才那个 BNB」「继续买」「还是闪兑」+ 写动词/槽位延续；**或** **inbound 显式指代与温索引 **`executionId`/symbol 匹配** | **温召回 **`resolvedSlotsSoFar` 人话摘要** → **§14.6.5 stale→active** → **合并槽** → **Fresh 工具 Facts** → **Resolver** |
| **C · ambiguous** | 仅「买」「100」「再来一笔」**且无** **足够指代** | **Resume 分类器**（**§14.6.4**）— **默认 **`new_intent`** |
| **D · 用户显式 **`cl:resume`/`cl:new`** | 点按 fallback 按钮 | **同窗** [`clarify-session` §4.1.1](../domains/agent/agent-orchestration/clarify-session.md) |

**禁止**：**Resume** **不得** **直接输出类型 A 写参** **或** **恢复 stale 前 **`pendingClarifyKind` 模板 outbound**；**价/余额/订单** **须 Fresh 或 stale 声明**（**`FR-MEM04`**）。

#### 14.6.4 Resume 分类器（MUST · 窄门控）

**定位**：**非主对话 LLM** — **仅** **判定** **是否从温索引召回上一笔写路径摘要。**规则层 B 分流命中时 MUST NOT 调用**。

| **项** | **MUST** |
|--------|----------|
| **输入** | **当前 inbound** + **至多一条 **`WarmExecutionEpisode` 摘要**（**默认 **`staleAt` 最近** · **`episodePickReason=most_recent_stale_at`**） |
| **输出** | **`ResumeClassifierDecision`**（**`new_intent`** \| **`resume_prior_write`** \| **`need_one_clarify`** — **禁止经济写参字段**）+ **`confidence` [0,1]** + **`executionId?`** + **`episodePickReason?`** |
| **阈值** | **`resume_prior_write`** **仅当** **`confidence ≥ RESUME_CLASSIFIER_MIN_CONFIDENCE`**（**默认 0.75** · **[`keys` §2.1](../domains/admin/trading-agent-config/keys.md)**）；**否则降级 **`new_intent`** |
| **默认** | **低置信 / 平局 / 未达阈值** → **`new_intent`**（**采纳默认新话题**） |
| **`need_one_clarify`** | **须** **一条开放问**（**如**「您是要继续上一笔 BNB 买入，还是新的一笔？」）**+ 可选非阻塞短句** — **禁止** **盲发 stale 前 **`pendingClarifyKind`** 模板**；**用户下条仍 ambiguous** → **再判 · 默认仍 **`new_intent`** |
| **观测** | **宜** **`agent.memory.resume_classified`** **含 **`decision`、`confidence`、`executionId`、`episodePickReason`** — **OpenAPI **`MemoryResumeClassifiedEventPayload`** |

**OpenAPI 示意** → **`ResumeClassifierResult`**（[`memory-runtime-schemas.yaml`](../../openapi/components/memory-runtime-schemas.yaml)）。

#### 14.6.5 stale → active 恢复（MUST）

**仅当** **§14.6.3 B/C 允许召回** **且** **本条仍为写路径** — **同窗** [`clarify-session` §2.4.4](../domains/agent/agent-orchestration/clarify-session.md)：

| **项** | **MUST** |
|--------|----------|
| **`lifecycleState`** | **`stale` → `active`** |
| **`executionId`** | **沿用** **温索引 **`executionId`**（**除非** **明确新 symbol/新任务**） |
| **`clarifyTurn`** | **递增** **不重置** |
| **`pendingClarifyKind`** | **须** **重跑 Resolver 后** **由 **`missing[]`** **重算** — **禁止** **恢复 stale 前模板** |
| **失败** | **Resolver 仍缺参且非明确续单** → **保持/回 **`stale`** **或 **`abandoned`** — **禁止 silent 类型 A** |

#### 14.6.6 用户可见（宜 · 非阻塞）

**宜** **一条短句**（**L 润色**）：如「距上次较久，已按新对话处理；若要接着上一笔，可直接说『继续买 BNB』。」— **不得** **替代** **§2.3 分流** **或** **强制卡死等待二选一**。

**Eval（登记）**：**`eval.memory.idle_default_stale`** · **`eval.memory.resume_classifier_gate`** · **`eval.memory.resume_classifier_multi_episode`** · **`eval.memory.idle_resume_or_new_topic`**（**fallback 按钮**）· **`eval.memory.stm_governance_regression`** → [`evals/scenarios.md`](../evals/scenarios.md)。

### 14.7 验收 · `SC-STM*`（增补）

| ID | Then |
|----|------|
| **SC-STM04** | **STM 清空或 session 热回收后** **写路径** **须** **新意图起票**；**0** **笔** **凭** **已清 L1** **之** **silent write** |
| **SC-STM05** | **工具 JSON/澄清槽** **静默升格 LTM** → **0** **条** **新 Semantic 命题** |
| **SC-STM06** | **隔较久 inbound** → **默认 stale 或 Resume 高置信续单或明确新意图** — **0** **盲续过期写澄清模板** — **§14.6** |
| **SC-STM12** | **默认 stale** · **idle 后「你好」** → **0 写澄清** · **stale L1 不在活跃注入** |
| **SC-STM13** | **默认 stale** · **idle 后显式续单** → **温召回 + Fresh Facts + stale→active** — **§14.6.3～§14.6.5** |

---

## 15. STM 写入准入 · 什么进、什么不进（MUST）

**原则**：**STM ≠ 全量聊天记录**。Runtime **须** **按本节 allowlist 写入 L0/L1**；**禁止** **把 Telegram 全线程、编排内部载荷、工具原始 JSON** **无差别** **灌入** **Prompt messages**。**观测/L3** **可** **保留更全 episode** — **与** **注入用 STM** **分离**（**§8.4**）。

**互引**：[`runtime-injection` §1 块 5](../domains/admin/prompt-management/runtime-injection.md)；[`market-runtime-payload` §3.3 `userVisibleMarketData`](../domains/agent/exchange-agent/market-runtime-payload.md)；[`clarify-user-visible` §1](../prompts/shared/clarify-user-visible.md)；[`context-management` §2](./context-management.md)。

### 15.1 L0（会话工作记忆）· 准入

| **类别** | **是否写入 L0** | **写入形态（注入 Prompt）** |
|----------|-----------------|----------------------------|
| **用户 inbound 自然语言**（Telegram `message` / 语音转写） | ✓ **MUST** | **本轮 User 块** + **近 N 轮 user 原文**（**N=`STM_L0_MAX_TURNS` 默认 10** · [`keys` §2.1](../domains/admin/trading-agent-config/keys.md)） |
| **助手用户可见回复**（`sendMessage`/`edit_*` 正文） | ✓ **宜** | **近 N 轮 assistant 原文** — **须** **为用户可见句**，**非** **内部 JSON** |
| **L0 rolling summary**（可选） | ✓ **宜** | **压缩 storyline** — **须** **标注** **为摘要**；**不得** **含** **经济写参真值** **冒充** **Facts** |
| **纯进度/typing/系统 ack**（「稍等…」、仅 emoji） | △ **可选** | **可** **省略** **或** **合并入摘要** — **不宜** **占满** **N 轮窗口** |
| **结构化 `clarify`/`intent` JSON** | ✗ **禁止** | **仅** **L1/BFF** **消费** — **同窗** [`clarify-user-visible` §1](../prompts/shared/clarify-user-visible.md) |
| **`routingHints` / `orchestrationNextSteps` 原文** | ✗ **禁止** | **观测可留** — **不进** **messages** |
| **上游 HTTP `code`/`msg`、堆栈、REST PATH** | ✗ **禁止** | **错误** **须** **归一化** **后再** **决定是否** **入 L0 assistant 句** |
| **模型 chain-of-thought / 未出站草稿** | ✗ **禁止** | **不得** **回灌** **Prompt** |
| **Secret / API Key / 完整 PII** | ✗ **禁止** | **同窗** **runtime-injection §2** |

### 15.2 L1（Execution 归因记忆）· 准入

**范围**：**仅** **当前 `sessionId` 下** **活跃** **（未终局且未热回收）** **之 **`executionId`** **集合** — **默认** **宜** **同时** **仅** **1** **条** **写路径** **活跃 execution**（**所内终裁** **并行策略**）。

| **类别** | **是否写入 L1** | **说明** |
|----------|-----------------|----------|
| **类型 A 已确认参数包**（用户已点确认 consumed 前之冻结载荷） | ✓ **MUST** | **注入位** **§5 ②** |
| **本 execution 成功 `agent.tool.call` 之用户可见 Facts** | ✓ **MUST** | **`userVisibleMarketData` 等** — **非** **raw 上游 JSON 全文** |
| **`ClarifySessionSnapshot` · `resolvedSlotsSoFar` 人话摘要** | ✓ **MUST**（写澄清时） | **非** **裸 snapshot JSON** **替代** **§7 话术** |
| **Planner / workflow 中间结论**（本 execution） | ✓ **宜** | **结构化** **或** **短摘要** |
| **`pending_confirm` 元数据**（confirmId、expiresAt、意图摘要哈希） | ✓ **MUST**（服务端） | **BFF 存储** — **不进** **L0 长文** |
| **未确认写参草案**（Parser 槽位草稿） | △ **须标注 provisional** | **不得** **单独** **驱动类型 A** — **INV-008** |
| **失败/超时工具调用的完整响应体** | ✗ **默认禁止进 Prompt** | **可** **L3**；**若注入** **须** **归一化错误桶** **一句** |
| **已终局 execution 的 L1 快照** | ✗ **禁止注入新 Prompt** | **可** **L3/温索引** — **跨 execution 须 Fresh/stale** |
| **其它 `executionId` / 其它用户 / 其它 session 的工具结果** | ✗ **禁止** | **§2 反污染** |

### 15.3 明确不进 STM（denylist · 摘要）

下列 **即使出现在会话中**，**也 MUST NOT** **作为** **STM 注入 Prompt** **之** **依据**（**L3 审计除外**）：

1. **全量 Telegram 更新日志**（含 `update_id`、未处理 callback 等）  
2. **交易所私有读/写 API 原始 JSON**（**须** **经** **`userVisible*` / Facts 裁剪**）  
3. **Prompt 包正文、Skill spec 全文、FR/INV 条文**  
4. **已 `abandoned` / `lifecycleState=stale` 澄清 session（活跃 L1）/ 已过期 `pending_confirm` 的载荷** — **stale 摘要仅经 Resume 门控从温索引注入**  
5. **终局 execution 的余额/价/订单快照** **用于** **新写**  
6. **LTM Semantic 块** — **走** **§9 独立注入位**，**不算** **L0/L1 追加**  

### 15.4 写入时机与窗口（MUST）

| **事件** | **L0** | **L1** |
|----------|--------|--------|
| **用户 inbound 完成** | **追加 user 轮**；**超窗** **则** **裁远端/压 summary**（**§11**） | **不自动追加** |
| **助手用户可见 outbound 完成** | **追加 assistant 轮**（**若** **§15.1 允许**） | — |
| **工具调用 SUCCESS（本 execution）** | — | **更新 Facts 快照** |
| **类型 A 用户确认 / `cl:*` 合并槽** | — | **更新确认包 / `resolvedSlotsSoFar`** |
| **execution 终局 / STM 清空 / 热回收** | **清或截断** | **该 execution L1 退出活跃集** |
| **澄清 abandoned / 放弃写** | **宜** **不再引用** ** abandoned 轮** **为** **活跃上下文** | **snapshot 标记 abandoned** |

**禁止**：**「每句都进永久 STM」** — **L0** **必须有界**（**turn/token · `STM_L0_*` · `design` MR**）。

### 15.5 功能需求 · `FR-STM*`（增补）

| ID | 陈述 |
|----|------|
| **FR-STM08** | **STM 写入 MUST** **遵守** **§15.1～§15.3** **allowlist/denylist**；**禁止** **无差别** **持久化** **全量会话** **至** **Prompt 装配路径**。 |
| **FR-STM09** | **L0 窗口 MUST** **有上界**（**轮次或 token**）；**超界** **须** **§11 裁剪** **或** **rolling summary** — **不得** **静默** **丢** **②④** **关键 Facts**。 |
| **FR-STM10** | **注入 Prompt 的 L1 工具/Facts MUST** **来自** **`userVisible*` / 登记裁剪器** — **禁止** **raw `agent.tool.call` 响应** **全文** **默认进 messages**。 |

### 15.6 验收 · `SC-STM*`（增补）

| ID | Then |
|----|------|
| **SC-STM07** | **Prompt 装配** **无** **`clarify`/`intent` JSON 原文**、**无** **`routingHints` 原文** **于** **user/assistant messages** |
| **SC-STM08** | **L0 超 `STM_L0_MAX_TURNS`** → **远端轮** **不在** **messages** **或** **仅** **summary** **可观测** |
| **SC-STM09** | **新 execution 问价** → **Facts** **来自** **本 execution 工具** **或** **stale 声明** — **非** **L0 旧 assistant 报价** |

**Eval（登记）**：**`eval.memory.stm_write_allowlist`** · **`eval.memory.stm_l0_window_bound`** → [`evals/scenarios.md`](../evals/scenarios.md)。**四原则执法** → **§16**。

---

## 16. 记忆治理四原则（MUST · 防僵尸澄清 · 防错乱写）

**背景**：生产 **Telegram 僵尸澄清**（**用户已寒暄/只读/放弃，仍复读闪兑/限价**；**内部 routing 话术外泄**）**根因** **多为** **四类治理失效** **叠加** — **非** **「模型记性差」** ** alone**。**负例叙事** → [`clarify-session` §2.3 负例](../domains/agent/agent-orchestration/clarify-session.md)。

**互引**：**§14.2** 失效矩阵 · **§15** 写入准入 · [`clarify-session` §2.3](../domains/agent/agent-orchestration/clarify-session.md) **重意图** · [`context-management` §2](./context-management.md) **反污染** · [`telegram/overview` §2.8](../domains/agent/telegram/overview.md) **新话题**。

### 16.1 四原则（产品宪法）

| **原则** | **含义（一句话）** | **执法 SSOT** |
|----------|-------------------|---------------|
| **该记的记** | **同 session / 同 execution 内**，**为连贯编排与少重复问** **须** **持久化** **allowlist 内容** | **§16.2** · **§15.1～§15.2** · **§15.4 写入时机** |
| **不该记的别乱记** | **全量聊天、内部载荷、raw JSON、已失效态** **不得** **进入 Prompt 装配路径** | **§16.3** · **§15.3 denylist** · **`SC-CLARIFY-09`** |
| **该忘的一定要忘记** | **放弃、只读打断、寒暄、失效、终局、空闲、用户清空** **须** **使对应 STM/L1 退出活跃注入** | **§16.4** · **§14.2** · **§15.4** · **clarify-session §2.1.1/§2.3** |
| **不该忘的不要忘记** | **同 execution 已确认槽、本 execution Fresh Facts、用户 L2/Semantic（未撤销）** **不得** **被误清或跨 execution 冒充真值** | **§16.5** · **§5 注入序 ②④** · **FR-STM02** · **`SC-MEM07`** |

**装配前硬闸（MUST）**：**Prompt 拼装前** **Runtime/BFF MUST** **依次** **(a)** **应用 §16.4 失效** **(b)** **过滤 §16.3 denylist** **(c)** **注入 §16.2 allowlist** **(d)** **校验 §16.5 保留项仍在** — **禁止** **跳过 (a) 直接灌 L0 全线程**。

### 16.2 该记的记（MUST persist · 活跃 STM）

**仅下列** **在** **仍属活跃 session/execution** **时** **须** **写入并可注入**（**细节** **§15**）：

| **类别** | **层** | **何时写** | **用途** |
|----------|--------|------------|----------|
| **用户 inbound 自然语言**（近 N 轮） | **L0** | **每 inbound** | **连贯对话、承接话术** |
| **助手已出站用户可见句**（近 N 轮） | **L0** | **每 outbound 完成** | **少重复、镜像 prior** |
| **可选 L0 rolling summary** | **L0** | **超窗压缩** | **省 token** — **非经济真值** |
| **`resolvedSlotsSoFar` 人话摘要** | **L1** | **澄清 follow-up / `cl:*`** | **少重复问已选 side/mode** |
| **本 execution 裁剪 Facts**（`userVisible*`） | **L1** | **工具 SUCCESS** | **本单编排/workflow** |
| **类型 A 已确认参数包**（consumed 前） | **L1** | **用户确认前冻结** | **写路径授权载荷** |
| **`pending_confirm` 元数据** | **BFF/L1** | **发类型 A 卡** | **callback 归因** — **不进 L0 长文** |
| **Planner/workflow 中间结论**（本 execution） | **L1** | **编排步进** | **续跑** |

**禁止误读**：**「该记」≠「全聊天记录」** — **N 有上界**（**`STM_L0_MAX_TURNS` · `design` MR**）；**进度/typing 宜省略**（**§15.1**）。

### 16.3 不该记的别乱记（MUST NOT write / inject）

**下列** **即使** **出现在 Telegram 或 Runtime 内部**，**也 MUST NOT** **作为** **Prompt messages / 默认真值**（**L3 审计除外**）：

| **类别** | **原因** |
|----------|----------|
| **`clarify`/`intent` JSON、`routingHints`、`orchestrationNextSteps` 原文** | **内部编排** — **致** **话术外泄与盲续**（**生产负例**） |
| **交易所/API raw JSON 全文** | **须** **`userVisible*` 裁剪** |
| **Prompt/Skill/FR/INV 条文、CoT、未出站草稿** | **非用户可见** |
| **全量 update 日志、Secret、完整 PII** | **安全/噪声** |
| **已 `abandoned` 澄清 / 已过期 confirm / 终局 execution 快照** | **僵尸态** — **致** **误续单/误写** |
| **其它 `executionId`/session/用户 的工具结果** | **反污染** |

**完整 denylist** → **§15.3**。**验收** **`SC-STM07`** · **`SC-CLARIFY-09`** · **`eval.memory.stm_write_allowlist`**。

### 16.4 该忘的一定要忘记（MUST invalidate · 退出活跃注入）

**下列事件** **MUST** **使对应记忆** **退出 Prompt 活跃集**（**可保留 L3**）：

| **触发** | **须忘记（退出注入）** | **锚点** |
|----------|------------------------|----------|
| **放弃写路径**（「都不要了」「取消」等） | **写澄清 L1 摘要 · `pendingClarifyKind`** | **clarify-session §2.1.1** · **`SC-CLARIFY-06`** |
| **只读/寒暄 inbound**（「有哪些币」「你好」等） | **写澄清 session → `abandoned`** | **§2.3 步 2** · **`SC-CLARIFY-07`** |
| **澄清 `expiresAt` 到达** | **整份 `ClarifySessionSnapshot` 活跃态** | **§14.2** |
| **类型 A TTL / STM 清空 / 用户「新话题」** | **L0 + session 活跃 L1 · 未确认卡** | **FR-STM01～03** · **§14.2** |
| **`executionId` 终局** | **该 execution 之 L1** | **§14.2** · **`SC-STM04`** |
| **session 空闲 ≥24h（热面回收 v0）** | **L0/L1 热槽** | **`architecture` 热级** |
| **写路径 idle/TTL 先达者** **且仍有写澄清/写 L1** | **默认 **`lifecycleState=stale`** · 退出活跃 L1 注入**（**§14.6.1**） | **§14.6** · **`FR-STM12～14`** |
| **每条 inbound（澄清态）** | **禁止** **凭** **过期 `pendingClarifyKind`** **跳过 Parser** | **clarify-session §2.3** · **`SC-CLARIFY-05`** |

**禁止**：**用户已明确新意图或放弃后**，**仍** **从 L0/L1** **引用** **旧写澄清 outbound** **作** **本轮默认回复**。

### 16.5 不该忘的不要忘记（MUST retain · 误清即缺陷）

| **类别** | **须保留至何时** | **禁止** |
|----------|------------------|----------|
| **同 `executionId` 内 `resolvedSlotsSoFar`（未 abandon）** | **澄清 follow-up / `cl:*` 合并前** | **每轮澄清新建 execution 丢槽**（**`SC-CLARIFY-02`**） |
| **本 execution 类型 A 已确认包（②）** | **消费前 / 写完成** | **被 L0 裁剪或 Semantic 覆盖**（**§5 注入序**） |
| **本 execution Fresh 工具 Facts（④）** | **直至 supersede 或终局** | **用 L0 旧 assistant 报价冒充**（**`SC-STM09`**） |
| **L2/Semantic（用户未撤销）** | **STM 清空后仍可召回** | **「重新开始」误删 LTM**（**FR-STM02** · **`SC-STM02`**） |
| **L3 审计/账务/计费 episode** | **保留期内** | **与 STM 清空混为一谈** |
| **温索引 stale 写路径摘要**（**§14.6.1 · clarify-session §2.4.3**） | **`WARM_EXECUTION_INDEX_TTL_SEC` 内** | **默认注入 Prompt**（**仅 Resume 门控后**） |

**跨 execution**：**可** **「记得用户关注 BTC」**（**LTM**）**但** **价/余额/订单** **须 Fresh 或 stale 声明** — **不得** **用 STM 叙事当真值**（**`FR-MEM04`** · **`SC-MEM03`**）。

### 16.6 功能需求 · `FR-STM*`（增补）

| ID | 陈述 |
|----|------|
| **FR-STM11** | **Prompt 装配前** **Runtime MUST** **执行** **§16.1 硬闸四步**（**失效 → 过滤 → 注入 allowlist → 校验保留项**）；**禁止** **无闸** **全量 L0 灌模**。 |
| **FR-STM12** | **写路径 idle/TTL 先达者**（**`STM_IDLE_RESUME_PROMPT_SEC` 或 `STM_CLARIFY_SESSION_TTL_SEC`**）**且** **存在未 abandoned 写澄清/写 L1** → **MUST** **`STM_IDLE_DEFAULT_POLICY=stale_prior_write`（默认）**：**标记 stale、退出活跃 L1 注入、重跑 §2.3 意图** — **禁止** **盲续 **`pendingClarifyKind`** 模板**。 |
| **FR-STM13** | **Resume 门控**：**ambiguous 且低置信** → **MUST** **按 `new_intent`（默认新话题）** — **不得** **为续单强行召回 stale 写路径**。 |
| **FR-STM14** | **仅** **规则层明确续单** **或** **`resume_prior_write` 且 `confidence ≥ RESUME_CLASSIFIER_MIN_CONFIDENCE`** **时** **可** **从温索引召回 **`resolvedSlotsSoFar` 摘要** **合并槽并重跑 Resolver**（**§14.6.5**）；**`need_one_clarify`** **须开放问 · 禁止盲续模板**；**价/余额/订单 MUST Fresh 或 stale 声明** — **禁止 silent 类型 A**。 |

### 16.7 验收 · `SC-STM*`（增补）

| ID | Then |
|----|------|
| **SC-STM10** | **生产回归链**（**同窗** **§16.8 叙事**）：**澄清 pending** → **用户**「都不要了」/「你好」/「有哪些币可买」→ **0** **条** **闪兑/限价写澄清复读** · **0** **处** **routing/写路径内部词** |
| **SC-STM11** | **（fallback）`STM_IDLE_DEFAULT_POLICY=prompt_resume_or_new`** · **模糊 inbound** → **可** **类型 C 或 ** **new_intent** — **非** **过期模板逐字复读** |
| **SC-STM12** | **默认 stale** · **idle 后「你好」** → **0 写澄清** · **stale L1 不在活跃注入** — **§14.6** |
| **SC-STM13** | **默认 stale** · **idle 后显式续单话束** → **温召回 + 合并槽 + Fresh Facts** — **§14.6.2** |

### 16.8 生产负例 · 端到端叙事（评审/Eval 构造）

**Given**（**同窗** **生产截图类**）：

1. 用户「全部买入 BNB」→ **写澄清 pending**（**缺 spot 方式**）  
2. 用户「闪兑」→ **仍缺项或误路由**  
3. **idle ≥1800s 或 clarify TTL ≥900s 先达** → **写 clarify 自动 stale**（**默认 **`stale_prior_write`**）  
4. 用户「你好」→ **Then** **寒暄** · **0** **闪兑/限价盘问**（**stale · 无活跃 L1 注入**）  
5. 用户「有哪些币可以买」→ **Then** **只读/listing** · **0** **写澄清复读**  
6. 用户「都不要了」→ **Then** **`abandoned=true`** · **短句确认** · **0** **写澄清**  
7. （**正例**）用户「还是买 BNB 100U 闪兑」→ **Then** **Resume 召回 + Fresh 余额** · **非** **18:27 模板复读**

**Eval**：**`eval.memory.stm_governance_regression`**（**整链**）· **`eval.memory.idle_default_stale`** · **`eval.memory.resume_classifier_gate`** · **分项** **`eval.clarify.*`** → [`evals/clarify-telegram.md`](../evals/clarify-telegram.md) **§7～§11**。

---

**文档版本**：1.8.0 · **维护**：产品 + Agent Runtime owner · **本版**：**§14.6 评审修复 · 触发统一/先达者 · 温索引召回 · 置信阈值 · stale→active**。承 1.7.0。
