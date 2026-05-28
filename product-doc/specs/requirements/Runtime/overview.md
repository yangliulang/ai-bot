# Agent Runtime（运行时 — 横切总览）

本目录承载 **Agent 运行时层面**跨多域的需求叙事：编排与执行投递、会话与执行上下文、持久化与恢复、冻结策略、并发互斥与事件溯源等。当内容 **跨多个 `domains/`** 文件、或需要 **独立评审与版本脚注** 时，在此以 **独立 `.md`** 维护。

**与设计对读（系统如何跑）**：逻辑 C4 + 主数据流见 **[`design/architecture.md`](../../design/architecture.md)**（**含** **「与通用 Agent 栈之对照」**）；**端到端鸟瞰** **[`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md)**（文首 **「架构语言」** → **同窗** **`architecture` §对照**）；环境、发布与 **逻辑部署单元**见 **[`design/deployment.md`](../../design/deployment.md)**。单条请求的 **执行管线（概念序 9 步）**见 **[`execution.md`](./execution.md) §1**（**步 7** **对齐** **Intent→Canonical→Gateway** **文档链**）。**「生产级 Runtime 真主在哪、还缺啥」** → **[`runtime-truth-source-map.md`](./runtime-truth-source-map.md)**。

**与「写」同窗的统一交易语义（跨所前置 · 文档 A）**：[**`canonical-trading-model.md`**](../../design/canonical-trading-model.md)、[**`ADR-004`**](../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[**`trade-assistance` §2.6**](../domains/agent/exchange-agent/trade-assistance.md)；**契约** [**`CC-P1-07`**](../contract-closure.md#cc-p1-07)；**人类评审** [**`requirements-review` §7.5**](../../../product/requirements-review.md#cc-adr004-review-checklist)。**Gateway 可执行实现** **不在本规格仓**；**DoD B** **在所内工程仓** **验收**。

**HTTP、PATH、字段真源**：仍 **[`design/`](../../design/)** — 本目录 **不**抄写 OpenAPI。

**对上 Coobit 私有所内 HTTP**：**出站实现默认** **ChainUp `openapi-ai` 官方包**（**制品须 pin**），**矩阵与 PATH 白名单不变** — **[`integrations/exchange/overview.md`](../integrations/exchange/overview.md)** · **[`agent-coobit-api-allowlist.md`](../integrations/exchange/agent-coobit-api-allowlist.md)**。

**小团队 / 发版**：**文档级 TBD 摘要**见 **[`product/release-notes.md`](../../../product/release-notes.md)**；**设计侧运行时组件挂载**（充实进度与 **`architecture` / `deployment` / 本篇** 对签）见 **[`design/runtime-architecture.md`](../../design/runtime-architecture.md)**。日常 **[`LITE-MODE.md`](../LITE-MODE.md)** §3。**关单 / 首节派工 / 开放项 / 走读缺口**：[**§0 速链**](../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../closure-remaining.md#cc-exec-solve-path) · [`closure-remaining` §7](../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../closure-remaining.md#cc-closure-exec-checklist)** · [`contract-closure`](../contract-closure.md)。

## 1. 文档结构（目录地图）

**本文件（`overview.md`）** 即 **总入口**；以下为 **同目录分卷**。

| 文件 | 内容 |
|------|------|
| [domain-model.md](./domain-model.md) | **概念管线 SSOT**：十步 ↔ `trade-via-agent` S* / `confirmation-flow` / `execution` §1；**风险闸束 R1～R4**；**Receipt / Timeline / 计费三轨**；V1 **不** 做 IR/Worker/Nested **索引** |
| [pipeline-walkthrough-checklist.md](./pipeline-walkthrough-checklist.md) | **写路径走读勾选 + MR 粘贴块**；**同窗** `eval.runtime.pipeline_write_order` |
| [runtime-truth-source-map.md](./runtime-truth-source-map.md) | **Runtime Truth Source 映射**：Goal→执行→状态→失败/恢复→记忆 **对照表**；**Failure Matrix** **索引**；**与** **Runtime Freeze** **对拍** |
| [runtime-invariants.md](./runtime-invariants.md) | **宪法**：**INV-001～010** · **§0 Execution Matrix**；**逐边 SSOT** → **`execution-transition-matrix` §2.2** |
| [runtime-consistency.md](./runtime-consistency.md) | **一致性自检**：跨卷主态/矩阵/计费词/Taxonomy·`stableReason`/Memory **勾选清单**（**不**替代各卷正文） |
| [runtime-state-machine.md](./runtime-state-machine.md) | **单笔 `executionId` 状态机总览**：**分域**、**主态图**、**非法迁移**、**恢复索引**；**Transition Contract** **入口** |
| [execution-transition-matrix.md](./execution-transition-matrix.md) | **Transition Contract 冻结**：**§2** **主格** + **§2.2 逐边**；**§3～§9** **权威·守卫·捷径·Unknown·终局·计费·恢复**；**Trigger→观测** [`observability/overview.md`](../observability/overview.md) **§2.4** · **`SC-OBS08`**（**控制台** **`SC-OM-04`**） |
| [runtime-error-taxonomy.md](./runtime-error-taxonomy.md) | **错误 Taxonomy** → **处置** **分类层**；**同窗** **`failure-matrix`** |
| [planner-contract.md](./planner-contract.md) | **Planner 契约入口**：**能/禁**、**§5 输出形态**（**`PlannerPlanEnvelope`/`PlannerPlanStep`**）、**§6 线性计划/禁嵌套分支** **与** **`execution-lifecycle` §5** **互引** |
| [memory-runtime.md](./memory-runtime.md) | **Memory 分域·Episodic/Semantic·TTL·注入序**（**v1.3.1**）；**§2.0 STM/LTM**；**§10 召回**；**§11 裁剪**；**§12 自检**；**§9 `FR-MEM*`**；**§13 `FR-STM*`**；**Eval GWT** [`evals/memory-runtime.md`](../evals/memory-runtime.md)；**OpenAPI** [`memory-runtime-schemas.yaml`](../../openapi/components/memory-runtime-schemas.yaml)；**执法条** **`context-management` §2** |
| [boundaries.md](./boundaries.md) | 与 `domains` / `design` / `flows` **SSOT 分工表** |
| [execution.md](./execution.md) | 调度、Planner、队列、**可计费执行**投递与在途语义（**横切**）；**[`§1`](./execution.md#1-执行管线概念序) 执行管线（概念序）**；**同窗** [`goal-and-execution-paths.md`](../domains/agent/agent-orchestration/goal-and-execution-paths.md) |
| [sessions.md](./sessions.md) | 会话载体、绑定快照、与用户触达侧的 **execution** 交界；**§2** **行为与验收下限** |
| [runtime-state.md](./runtime-state.md) | 运行态、`agentState` 与门禁短路与 **摘要**同窗（**`agentState` 枚举真源** → **`management-console-v1-prd` §9**）；**单笔 `execution` 主态** → [`execution.md`](./execution.md) **附录 A** |
| [context-management.md](./context-management.md) | 上下文管线、预算与压缩、**§2 隔离 / 反污染** — **读模型**横切 |
| [persistence.md](./persistence.md) | 检查点、幂等键与 **可恢复**状态落盘边界；**§2** **行为与验收下限** |
| [freeze-policy.md](./freeze-policy.md) | Kill/冻结/版本戳与 **`orchestrationVersion`** 同窗 **政策层** |
| [locking.md](./locking.md) | 租约、单写者、跨实例/分片 **互斥**下限；**§2** **行为与验收下限** |
| [recovery.md](./recovery.md) | 重试、退避、**Fallback/降级**；**504/UNKNOWN** **与** [`unknown-state.md`](./unknown-state.md) **对读** |
| [fallback-policy.md](./fallback-policy.md) | **Fallback 类型学**：**Runtime **策略 **vs **`prompts/`** **话术域 ** **分界** |
| [error-normalization.md](./error-normalization.md) | 上游错误 → **`stableReason`** / 观测字段 **契约层** |
| [failure-matrix.md](./failure-matrix.md) | **失败 → Runtime 处置** **合一索引**；**字段终裁** **与** **`stableReason` SSOT** **对读** |
| [unknown-state.md](./unknown-state.md) | **UNKNOWN** 与 **504** 的 **平台语义**下限 |
| [reconciliation.md](./reconciliation.md) | **REST ↔ WS** 对账与补救路径 **政策层**（矩阵 **可对签**） |
| [event-storage.md](./event-storage.md) | 执行与审计相关 **事件**留存、关联键与保留期 **需求下限**；**§2** **行为与验收下限** |

---

## 2. 与邻域的边界（摘要）

**同窗**：各分卷 **职责** 下的 **同窗** 为 **短列表**（仅直接依赖）；**横向分工全表** 见 **[boundaries.md](./boundaries.md)**。

**原则**：`Runtime/*.md` **不**自创与 `domains` 矛盾的 FR；新验收条目默认落在 **对应域** **FR/SC**，此处 **只叙事与索引**，或单列 **运行时横切 REQ** 并 **脚注域内编号**。

此外：**[`domains/agent/runtime/overview.md`](../domains/agent/runtime/overview.md)** 为 **`domains/agent/`** 树下的 **运行时导航透镜**（链向本篇 §1 与各 **域** **正文**）；**不**承载独立 FR/SC SSOT。

---

## 3. 书写与评审

- 结构对齐 **[`../standards/prd-standard.md`](../standards/prd-standard.md)**（触发 / 行为 / 边界 / 追溯）；跨步骤链对齐 **[`../standards/business-process-standard.md`](../standards/business-process-standard.md)**。
- MR：**[`../standards/review-and-change-standard.md`](../standards/review-and-change-standard.md) §2～§3**；涉及对外承诺时对 **[`../contract-closure.md`](../contract-closure.md)**。
- 存量分批：**[`../standards/STANDARDS-ADOPTION.md`](../standards/STANDARDS-ADOPTION.md)** · **Wave R**。

在 [`../spec.md`](../spec.md)、[`../README.md`](../README.md)、**本目录 [README](./README.md)** 中已登记本目录；新增正文后请 **回填索引一句**。

---

**文档版本**：1.1.12 · **维护**：产品 + Agent Runtime owner · **本版**：**目录表** **`planner-contract` §5～§6 输出形态**。**承** **1.1.11**。
