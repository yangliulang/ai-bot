# Runtime · 概念管线与实体索引（对签用）

**职责**：把 **评审/走读/所内编排** 常用的 **「用户输入 → … → Timeline」** **概念阶段** **映射到** **本仓库已有 SSOT**（**不** 新造 FR/SC；**不** 约束微服务边界）。**写路径交易主链** **以** [`trade-via-agent.md`](../flows/trade-via-agent.md) **S1～S10** **为流程 SSOT**；**五步确认序** **以** [`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md) **§1**；**横切因果序** **以** [`execution.md`](./execution.md) **§1**。

**契约开放面 / B 阶段派工** → [`closure-remaining` §7.5 · OP-*](../closure-remaining.md#cc-remaining-open-close-path) · [`skill-specs/MR-B-BFF-IMPLEMENTATION.md`](../skill-specs/MR-B-BFF-IMPLEMENTATION.md) · [`contract-closure` §2～§3](../contract-closure.md)。

**走读 / MR 勾选** → [`pipeline-walkthrough-checklist.md`](./pipeline-walkthrough-checklist.md) · **Eval** [`evals/pipeline-write-order.md`](../evals/pipeline-write-order.md)。

---

## 1. 概念十步 ↔ 规格真源（写路径 · 交易主轴）

**说明**：左列为 **架构/评审口语**；**「规格步骤」** 为 **本仓库编号**（**实现可异步化**，**但因果与观测序须满足 §3**）。

| # | 概念阶段 | 规格步骤（主） | FR / SC / 流程锚点 |
|---|----------|----------------|-------------------|
| 1 | **用户输入** | `trade-via-agent` **S1**；`execution` **§1 步 1** | Telegram `Update`、会话 — [`telegram/overview`](../domains/agent/telegram/overview.md) §2～§2.6 |
| 2 | **Scenario Router** | **S2**；`execution` **步 4**（`scenarioId`） | [`routing-engine`](../domains/agent/agent-orchestration/routing-engine.md) §2、**FR-T07 / FR-AO02** |
| 3 | **Skill Runtime** | **S4**；`confirmation-flow` **步骤 1**；`execution` **步 5b** | **`read_skill_operation_spec`** — **FR-T11 / FR-AO04**；[`production-runtime`](../skill-specs/production-runtime.md)、**SC-OBS11** |
| 4 | **Parameter Resolution** | **S6**、**S11～S13** | **FR-T07** 槽位补全 — [`intents`](../domains/agent/exchange-agent/intents.md) |
| 5 | **Validation** | **S6**、**S13**、偏离带专节 | **FR-T07** + **FR-T12**；skill spec §validation；`SYMBOL_POLICY_*` |
| 6 | **Risk Check** | **§2 风险闸束**（多时点） | **非单卷名** — 见 **§2** |
| 7 | **Confirmation** | **S7**；`confirmation-flow` **步骤 3**；`execution` **步 6** | 类型 A — **ADR-001**、[`telegram` §2.5](../domains/agent/telegram/overview.md)、**FR-T09**（限额，确认前） |
| 8 | **Execution** | **S8**；`confirmation-flow` **步骤 4**；`execution` **步 7** | **`call_exchange_write`** — **FR-T01**；Gateway **DoD B** — **CC-P1-07**（所内工程仓） |
| 9 | **Receipt** | **S9**；`confirmation-flow` **步骤 5** | 用户可见 — **FR-T05**（**≠** 运维时间线 **≠** 账务流水） |
| 10 | **Timeline** | **S5 起持续**；`execution` **步 9** | **`executionId`** join — **FR-MC801**、[`observability` §2.4](../observability/overview.md)、**SC-OBS08** |

**另须知晓（概念十步未单列）**：

| 主题 | 规格步骤 | 锚点 |
|------|----------|------|
| **`executionId` 起票** | **S5**（**早于** S6 槽位） | **FR-T01**、[`consume-and-bill`](../flows/consume-and-bill.md) |
| **计费终局** | **S10** | Token 扣减叙事 — [`billing-management/overview`](../domains/admin/billing-management/overview.md) |
| **Prompt / 上下文** | `execution` **步 5** | [`agent-context`](../domains/agent/agent-context/overview.md)、[`runtime-injection`](../domains/admin/prompt-management/runtime-injection.md) |
| **写参宪法（完备性/血缘）** | **S6～S14**、**确认前** · **`execution` §1 步 6～7** | [`runtime-invariants` §0、INV-008～010](./runtime-invariants.md)；[`confirmation-flow` 步骤 2](../domains/agent/agent-orchestration/confirmation-flow.md) |

**只读 / 纯对话**：**无** 步骤 3～8 全链；Router 后 **可** 直达工具只读 — [`read-analyze-and-search-via-agent.md`](../flows/read-analyze-and-search-via-agent.md)。

---

## 2. 风险闸束（Risk Check · 产品归并）

规格 **未** 使用单一阶段名 **「Risk Check」**；实现 **须** 按下表 **时点** 执行 **全部适用行**（**拒答** **FR-T05**）。

| 时点 | 闸 | 规格锚点 | 典型观测 / 验收 |
|------|-----|----------|-----------------|
| **R1 · 路由后（写/须私有读）** | 全局 Kill/Pause、**FEATURE_***、子账户+Key、VIP、计费阻断（**USDT 下界**）、**（Phase 2）Capability 额度** | `trade-via-agent` **S3** — **FR-T02**（**序** [`consume-and-bill`](../flows/consume-and-bill.md) **S2**） | 阻断须可读阶段提示（**余额不足 vs 配额用尽** **宜分族**） |
| **R2 · 配置快照（起票前后）** | **`configVersion`** 生效闸 | `execution` **§1 步 2**、[`freeze-policy`](./freeze-policy.md) | 与 R1 **同窗** 不同宿主 |
| **R3 · 校验后、类型 A 前** | 单笔/单日限额、偏离带（若 ON） | **S7**、**FR-T09**、**FR-T12** | 超限 **拒答**，**不** 静默写 |
| **R4 · 写路径横切** | 编排预算 **FR-AO06**、工具门禁顺序、[`risk/`](../risk/README.md) 护栏 | `execution` **步 4**、[`hitl-and-automation-matrix`](../risk/hitl-and-automation-matrix.md) | **SC-RISK*** 抽检宜 join **`executionId`** 时间线 |

**编排验收**：**不得** 将 R1～R3 **全部推迟到** Confirmation **之后**；**不得** 在 **无** `agent.skill.spec_read`（写路径）**的情况下** 首发类型 A（**SC-OBS11**）。

---

## 3. Receipt · Timeline · 计费（三轨分界）

| 轨 | 受众 | SSOT | 常见误读 |
|----|------|------|----------|
| **Receipt** | 终端用户（Telegram） | **FR-T05**、**S9**、[`telegram` §3.1](../domains/agent/telegram/overview.md) | **不是** Admin 执行详情页 |
| **Timeline** | 运营 / 协查 / 审计 | **FR-MC801**、`ObservabilityTimelineEvent`、**SC-OBS08** | **从 `executionId` 起票起** 持续写入，**非** Receipt 之后才开始 |
| **计费终局** | 账务 / Token | **S10**、[`consume-and-bill`](../flows/consume-and-bill.md) | **V1 非**「按 execution 单价」对客计费；**边界** 见 **FR-T01** + billing §10 |

**部成 / 在途**：用户 Receipt **须** 区分订单在途 vs **`executionId` 产品终局** — [`trade-via-agent` S5.1.1](../flows/trade-via-agent.md)。

---

## 4. 因果序 · 实现禁止项（写路径）

下列 **须（MUST）** 满足 **观测与走读**，**与** 是否拆队列 **无关**：

1. **`executionId`** **分配后** 才 **向用户承诺** **可计费协查键**（**S5**）。  
2. **`read_skill_operation_spec`（success）** **早于** **首张类型 A** 与 **首条** `call_exchange_write`（**SC-OBS11**）。  
3. **类型 A 用户确认** **早于** **每一笔** 新的 Coobit 私域写（**ADR-001**）；**逻辑改单** 例外见 **`trade-via-agent` 专节 · 逻辑改单**。  
4. **终局成功话术** **仅** 在交易所/对账可采信终局后（**禁止** 504/UNKNOWN 冒充成交）。  
5. **主态边** **须** 在时间线 **可还原** Trigger（**SC-OBS08**）。

**概念十步与 `trade-via-agent` 编号对照（写路径）**：

```text
S1 输入 → S2 路由 → S3 门禁(R1) → S4 读技能 → S5 executionId
→ S6 槽位/校验 → S7 限额(R3)+类型A → S8 执行 → S9 Receipt → S10 计费
（Timeline：自 S5 起与步 4～9 事件并行）
```

---

## 5. 核心实体索引（无「Runtime Execution」专卷）

| 实体 / 概念 | SSOT | 备注 |
|-------------|------|------|
| **`executionId`** | [`exchange-agent/overview`](../domains/agent/exchange-agent/overview.md) **FR-T01**；[`execution-transition-matrix`](./execution-transition-matrix.md) | **产品主执行键**；**禁止** 用 message id 替代 |
| **`scenarioId`** | [`routing-engine`](../domains/agent/agent-orchestration/routing-engine.md) | 业务能力路由 **第一维** |
| **`skillId` / 操作规范** | [`trade-assistance` §8](../domains/agent/exchange-agent/trade-assistance.md)、L0 [`skill-specs/`](../skill-specs/README.md) | **Cursor Skill** **≠** 运行时 **`skillId`** — [`product.md`](../product.md) 术语表 |
| **主态机** | [`runtime-state-machine`](./runtime-state-machine.md)、附录 [`execution` 附录 A](./execution.md) | 部成/在途 **子态**，**非** 独立主行 |
| **Gateway / Canonical** | [`canonical-trading-model`](../../design/canonical-trading-model.md)、**CC-P1-07** | **文档 A** 在本仓；**DoD B** 在所内 |

**旧稿 §10.x 映射** → [`overview-legacy-migration`](../domains/agent/exchange-agent/overview-legacy-migration.md)（**非** 能力 SSOT）。

---

## 6. V1 刻意不定义的通用 Agent 模型（[`product.md`](../product.md) §非目标 同窗）

| 模型 | V1 口径 | 若需要 |
|------|---------|--------|
| **Runtime IR**（中间表示 DAG） | **不** 专卷；编排下限见 [`runtime-freeze` §3](../domains/agent/agent-orchestration/runtime-freeze.md) | 所内 ADR |
| **Worker Model** | **不** 产品化；队列叙事见 [`execution`](./execution.md) | 实现仓 |
| **Distributed Execution** | **不** 专卷；[`locking`](./locking.md)、[`recovery`](./recovery.md) | 实现仓 |
| **Nested Execution** | **非目标** | 独立 MR + `product.md` 解除 |
| **State Recovery** | **有** — 分散 [`recovery`](./recovery.md)、[`persistence`](./persistence.md)、[`unknown-state`](./unknown-state.md) | 本表 **不** 列为缺口 |

---

## 7. 开放项 · 本概念管线 **不能** 单靠本文关闭

**A 阶段（本 Git）**：本篇 + 互链 **闭合「顺序混读 / 三轨混读 / Risk 漏闸」** 类文档债。

**B 阶段 / 所内（仍开放）** — 关单 **仍以** [`closure-remaining` §7.5](../closure-remaining.md#cc-remaining-open-close-path) **为准**：

| 优先级 | ID | 所内须交付 |
|:------:|-----|------------|
| **P0** | **OP-P0**、CC-P0-01～05 | Hosted/矩阵/账务/会签 |
| **高** | **SK-B02**、**OP-AO3** | 真 `read_skill` 编排 + §3 对拍 |
| **高** | **CC-P1-07** | Execution Gateway 实现 |
| **高** | **OP-PR**、**MR-B** | Prompt Runtime 全链 |
| **中** | **SK-B01**、**SK-B03～05** | Publish 落库、Eval 真跑、Registry、矩阵数值 |
| **中** | **OP-MEM**、**OP-NAR** | Memory / 盘感注入与 Eval |

**所内最小 MR 清单（可复制到工单）** → [`skill-specs/MR-B-BFF-IMPLEMENTATION.md`](../skill-specs/MR-B-BFF-IMPLEMENTATION.md)。

---

**文档版本**：0.1.1 · **维护**：产品 + Agent Runtime owner · **本版**：**写参宪法** **行（另须知晓）**。承 0.1.0。
