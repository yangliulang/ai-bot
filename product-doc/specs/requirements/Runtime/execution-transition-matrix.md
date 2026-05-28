# Runtime · `executionId` 迁移矩阵（Transition Contract · **冻结 SSOT**）

**路径**：`specs/requirements/Runtime/execution-transition-matrix.md`。

**职责**：**逐对** **冻结** **「主态 A → 主态 B」** **是否允许**、**触发**、**守卫**、**副作用**、**计费/话术**。**状态词** **与** **[`execution.md`](./execution.md) 附录 A** **一致**。**本篇 §2（** **含 §2.2 逐边契约表** **）** **及** **§3～§9** **为** **「状态迁移规则」** **产品终裁** — **实现** **不得** **另立** **第三套主格**。**总图示意** → [`runtime-state-machine.md`](./runtime-state-machine.md)；**宪法** → [`runtime-invariants.md`](./runtime-invariants.md)。

**同窗**：[`trade-via-agent.md`](../flows/trade-via-agent.md) **S5.1**；[`unknown-state.md`](./unknown-state.md)；[`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4～§5**；[`locking.md`](./locking.md) **§2·主态写入权威**。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. 图例

| **列** | **含义** |
|--------|----------|
| **✓** | **允许**（**产品叙事** **须** **可测**） |
| **✓†** | **允许** **附条件**（**见 §2.1**） |
| **✗** | **禁止**（**同一 `executionId`** **unless** **新开** **`executionId`** **或** **ADR 登记之 replay**） |
| **✗†** | **默认禁止**；**例外** **须** **ADR** |

---

## 2. 迁移矩阵（主态 × 主态）

**行** = **从**；**列** = **到**。

| **从 \\ 到** | **accepted** | **planning** | **waiting_confirmation** | **executing** | **settling** | **completed** | **failed** | **unknown_pending** | **cancelled** |
|--------------|----------------|----------------|----------------------------|----------------|----------------|-----------------|------------|----------------------|-----------------|
| **accepted** | — | ✓ | ✓† | ✓† | ✗ | ✗ | ✓ | ✗ | ✓† |
| **planning** | ✗ | — | ✓ | ✓† | ✗ | ✗ | ✓ | ✗ | ✓ |
| **waiting_confirmation** | ✗ | ✗ | — | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ |
| **executing** | ✗ | ✗ | ✗ | **子态** | ✓ | ✗ | ✓ | ✓ | ✓† |
| **settling** | ✗ | ✗ | ✗ | ✗ | **子态** | ✓ | ✓ | ✓ | ✗ |
| **unknown_pending** | ✗ | ✗ | ✗ | ✗ | ✓† | ✓† | ✓ | **子态** | ✓† |
| **completed** | ✗ | ✗ | ✗ | ✗ | ✗ | — | ✗ | ✗ | ✗ |
| **failed** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | — | ✗† | ✗ |
| **cancelled** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | — |

### 2.1 备注（✓†）

- **accepted → waiting_confirmation / executing**：**仅当** **产品/流程** **明确** **跳过** **编排步或确认门** **之** **只读/特殊路径**；**交易写主路径** **须** **满足** **`execution` §1** **与** **类型 A**。  
- **accepted → cancelled**：**在** **未产生** **不可逆副作用** **前** **用户** **或** **运营** **撤销**（**口径** **与** **confirmation-flow** **对签**）。  
- **planning → executing**：**无** **写前确认** **之** **能力** **须** **在** **`routing-engine` + flow** **显式**；**否则** **须** **经** **`waiting_confirmation`**。  
- **executing → cancelled**：**仅当** **产品** **定义** **安全撤单点**（**未** **错误** **宣告终局**）。  
- **unknown_pending → settling / completed / cancelled**：**仅经** **对账** **或** **运维叙事** **闭环**（[`reconciliation.md`](./reconciliation.md)）；**completed** **须** **满足** **终局可采信** **且** **不与** **UNKNOWN** **口径** **矛盾**。  
- **failed → unknown_pending**：**一般** **禁止**；**例外** **须** **ADR**（**如** **迟至上浮之** **竞态**）。

### 2.2 逐边契约表（**研发不得另解**）

**六问（每条允许迁移须可答）**：（1）是否允许 ·（2）触发事实 ·（3）谁对**业务事实**负责 ·（4）Guard ·（5）副作用 ·（6）计费 / 对账 / 用户话术。

**主态持久化**：**下表「Authority」** = **触发责任域**（**谁产出归并前事实**）；**附录 A 主态行** **仅** **编排运行时宿主** **提交** — [`locking.md`](./locking.md) **§2**。**Trigger** **为** **建议结构化名**；**实现** **可** **映射** **为** **同窗事件名** — **语义** **不得** **弱于** **本表**。**事件与时间线字段映射** **SSOT** → [`observability/overview.md`](../observability/overview.md) **§2.4**（**`ObservabilityTimelineEvent.transitionTrigger`** **可选** **与** **`eventName`/`summary` 键**）。

#### 2.2.1 允许（与 §2 主格 **✓ / ✓†** 一一对应）

| **From** | **To** | **Allowed** | **Trigger / Event** | **Authority（触发域）** | **Guard** | **Side Effect** | **计费 · 对账 · 话术** |
|----------|--------|-------------|---------------------|-------------------------|-----------|-----------------|-------------------------|
| accepted | planning | ✅ | `execution.dispatched` | Runtime Engine | `executionId` 已分配；[`execution.md`](./execution.md) §1 步 1～2 快照有效 | 进入编排 | 非终局；不触发 `PER_EXECUTION_FINAL` |
| accepted | waiting_confirmation | ✅† | Orch.shortcut_to_confirm | Runtime Engine / Planner | **§2.1**；仅登记**跳过 planning** 路径 | 可建确认上下文 | 写仍须类型 A；[`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md) |
| accepted | executing | ✅† | Orch.shortcut_execute | Runtime Engine | **§2.1**；**触及** `call_exchange_write` **须**类型 A | 进入工具/IO | 不断言成交 |
| accepted | failed | ✅ | `gate.failed` / `early_abort` | Runtime Engine | Kill/FR-T02/预算等可解释失败 | 终局失败 | 不成功不扣；`FR-T05` |
| accepted | cancelled | ✅† | `user.cancelled` / `ops.cancelled` | User / Ops（经通道） | **§2.1** 无不可逆副作用前 | 终局取消 | 不成功不扣；`CANCELLED` 文案 |
| planning | waiting_confirmation | ✅ | `confirmation.required` | Planner → Runtime | **写路径**须类型 A；S5.1 | 确认门待闭合 | 推卡/会话 |
| planning | executing | ✅† | `plan.ready_no_confirm` | Planner → Runtime | **§2.1**；`routing-engine`+flow **明示**无确认门或只读 | 进入工具阶段 | 若有写仍过门禁 |
| planning | failed | ✅ | `plan.abort` / `risk_rejected` | Planner / Runtime | **风险/护栏拒答**；**不得静默进入** `call_exchange_write` **扩张** | 终局失败 | 不成功不扣；`FR-T05` |
| planning | cancelled | ✅ | `user.cancelled` | User / System | 产品安全取消点 | 终局取消 | 不成功不扣 |
| waiting_confirmation | executing | ✅ | `user.confirmed` | Confirmation / User（事实）→ Runtime | **ADR-001** 类型 A 有效 | 可执行写 | 未可采信前不报 success |
| waiting_confirmation | failed | ✅ | `confirm.timeout` / `reject` | System / Runtime | 超时或拒答 | 终局失败 | 不成功不扣 |
| waiting_confirmation | cancelled | ✅ | `user.cancelled` | User | 用户撤回 | 终局取消 | 不成功不扣 |
| executing | settling | ✅ | `tool.round_complete` / `order.submitted` | Tool Runtime → Runtime | 达「可终局判定」点；**部成仅子态** S5.1 | 进入结算链 | 尚未对用户宣 completed |
| executing | unknown_pending | ✅ | `tool.timeout` / `exchange.504` | Tool Runtime → Runtime | 终态不可判 — [`unknown-state.md`](./unknown-state.md) | 挂起；对账 | `unknown`；禁 success 话术 |
| executing | failed | ✅ | `tool.final_failed` | Tool Runtime → Runtime | 可采信终局失败 | 终局失败 | 不成功不扣 |
| executing | cancelled | ✅† | `user.cancelled` / `safe.abort` | User / System → Runtime | **§2.1** 安全撤单点 | 终局取消 | 不成功不扣 |
| settling | completed | ✅ | `reconciliation.success` + billing | Reconciliation / Billing → Runtime | 可采信成功；S4→S5 — [`consume-and-bill.md`](../flows/consume-and-bill.md) | **可** `PER_EXECUTION_FINAL` 评估 | **成功权益核销** **SC-B20**；用户可见成功 |
| settling | failed | ✅ | `settlement.failed` | Reconciliation → Runtime | 可采信失败 | 终局失败 | 不成功不扣 |
| settling | unknown_pending | ✅ | `reconciliation.inconclusive` | Reconciliation → Runtime | 终局暂不可采信 | 回退 UNKNOWN | 不断言成交；同窗 `billing` §10 |
| unknown_pending | settling | ✅† | `evidence.received` | Reconciliation → Runtime | **§2.1** 仅经对账/运维闭环 | 续结算 | 依证据更新话术 |
| unknown_pending | completed | ✅† | `final_success_confirmed` | Reconciliation → Runtime | **§2.1**；[`reconciliation.md`](./reconciliation.md) **§2** | 可走向计费评估 | 同窗 `billing` §10.1 |
| unknown_pending | failed | ✅ | `final_failed_confirmed` / `policy.timeout` | Reconciliation / Policy → Runtime | 可采信失败或策略终局 | 终局失败 | 不成功不扣 |
| unknown_pending | cancelled | ✅† | `ops.cancelled` / `policy.cancel` | Ops / User → Runtime | **§2.1** | 终局取消 | 不成功不扣 |

#### 2.2.2 代表 **禁止**（与 §2 **✗**；宿主须拒）

| **From** | **To** | **Allowed** | **Guard / 理由** | **计费 · 话术** |
|----------|--------|-------------|------------------|----------------|
| completed | 任非终局 | ❌ | **INV-001** 终局单调 | 禁止回卷计费 |
| failed | executing / settling / planning | ❌ | 须新 `executionId` 或 ADR replay | — |
| cancelled | executing / settling | ❌ | 已取消 | — |
| accepted | completed / settling | ❌ | [`execution.md`](./execution.md) §1 因果序 | — |
| failed | unknown_pending | ✗† | **仅** ADR 登记例外 | 须可审计 |

---

## 3. 捷径审计（Shortcuts）

**断言**：**任意** **单步** **主态迁移** **若** **不在** **§2** **主格** **为** **✓** **或** **✓†**，**则** **非法**。**✓†** **即** **唯一** **文档化「捷径」**（**须** **满足** **§2.1**）；**不** **存在** **未** **登记** **之** **「暗捷径」**。

**显式禁止** **（** **与同** **`executionId`** **）** **之** **偷跳样例**（**与** [`runtime-state-machine.md`](./runtime-state-machine.md) **§4** **一致**）：

| **从 → 到** | **结论** |
|-------------|----------|
| **accepted → completed / settling** | **✗** — **违反** **`execution` §1** **因果序** |
| **planning / waiting_confirmation → completed / settling** | **✗** — **跳过** **工具/终局判定链** |
| **completed → 任何非终局** | **✗** |
| **failed / cancelled → executing / settling / planning** | **✗** — **须** **新** **`executionId`** **或** **ADR replay** |

---

## 4. 迁移权威（总则）

**与 §2.2 同读**：**逐边「Authority（触发域）」** **见** **§2.2**；**本条** **只** **锁** **持久化纪律** — **附录 A 主态行** **仅** **编排运行时宿主** **提交**；**Planner / 用户 / 工具 / 对账 / 计费** **只** **投递事实**。**多实例** **须** **租约/版本/fence** — [`locking.md`](./locking.md) **§2**。

---

## 5. 前置条件（总则）

**逐边 Guard** **已列于** **§2.2.1「Guard」列**。**实现** **可** **加码** **不可** **减码** **unless** [`contract-closure.md`](../contract-closure.md) **登记豁免**。

---

## 6. `unknown_pending` 收口（与同执行永恒悬挂）

**问**：**是否** **存在** **「永远 unknown」** **之** **`executionId`** **被产品允许**？**答**：**否** **—** **须** **在** **可配置上界内** **走到** **§2** **允许** **之** **出口** **（** **completed / failed / cancelled** **或** **经 ADR 之** **failed→unknown** **例外链** **）** **或** **显式** **人工/运营** **处置**；**细节** **同窗** [`unknown-state.md`](./unknown-state.md)、[`../risk/unknown-stall-policy.md`](../risk/unknown-stall-policy.md)。

| **典型进入源** | **须可达的出口（经宿主归并）** |
|----------------|--------------------------------|
| **工具/HTTP 504、读超时** | **查单/对账** → **settling/failed/completed** **或** **维持 unknown** **直至** **策略上界** |
| **callback / WS 缺失** | **REST 拉齐** **或** **轮询 PATH** — [`reconciliation.md`](./reconciliation.md) |
| **双通道冲突** | **对账裁决** — [`reconciliation.md`](./reconciliation.md) |

---

## 7. 终局单调（Terminal monotonicity）

**三终局**：**`completed` / `failed` / `cancelled`**。**任何** **✓/✓†** **均** **无** **自** **三终局** **迁往** **非终局** **主态**（**§2** **主格** **全** **✗**）。**`failed → unknown_pending`** **为** **✗†** — **默认** **不得** **；** **例外** **ADR**。

**终局后** **「** **是否** **还能执行」** **答**：**不得** **在同一** **`executionId`** **下** **继续** **扩张** **Planner/执行** **主轨迹**；**新意图** **须** **新** **`executionId`** **或** **显式** **replay ADR**。

---

## 8. Retry / Replay · 计费边界

### 8.1 Retry vs Replay

| **行为** | **同 `executionId`？** | **须** |
|----------|------------------------|--------|
| **Retry** | **是**（**子态** **如** **RETRYING**） | **不** **增计** **FR-AO06** **工具次数**（**同窗** [`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4**）；**写工具** **禁止** **无脑自动 Retry** **同参下单** — [`runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md) **§3** |
| **Replay** | **原则上** **否** | **新** **`executionId`** **或** **ADR** **定义** **之** **恢复** |

**问**：**retry** **会否** **重复下单**？**答**：**仅当** **违反** **`runtime-contract` §3** **（** **对** **`create_order` 等** **自动重试** **）** **—** **产品** **禁止** **该路径** **；** **UNKNOWN** **后** **须** **查单** **再** **显式** **二次提交**。

### 8.2 计费（Billable 主态 · Agent 消耗 · 轨 B）

| **主态** | **成功 `ENTITLEMENT_DEBIT`（`PER_EXECUTION_FINAL` 边界）** |
|----------|-------------------------------------------------------------|
| **completed** | **是**（**须** **同窗** **S4→S5**、**SC-B20**） |
| **settling** | **仅在** **权益核销** **闭合尝试** **的** **叙事中** — **用户可见** **成功** **仍以** **completed** **+ `billingTraceId`** **为准** |
| **failed / cancelled / unknown_pending** | **否** **（** **不成功不核销** **）** |

**问**：**未确认完成** **却已计费**？**答**：**禁止** **—** [`billing-management/rules.md`](../domains/admin/billing-management/rules.md)、[`consume-and-bill.md`](../flows/consume-and-bill.md) **S4～S5**。

---

## 9. Recovery（crash · queue · 重放）

| **问** | **答（产品下限）** |
|--------|-------------------|
| **crash 后** **回到** **哪**？ | **最后** **一致** **检查点** **所记录** **主态+游标+幂等** — [`persistence.md`](./persistence.md) **§2** |
| **queue replay** **破坏** **单调**？**禁止** **—** **须** **与** **§7** **及** [`runtime-state-machine.md`](./runtime-state-machine.md) **§5** **不矛盾** |
| **recovery** **重复执行** **/ 重复计费**？**禁止** **—** [`persistence.md`](./persistence.md) **§1～2**；**§8.2** |

---

## 10. `executing` / `settling` / `unknown_pending` 内子态

**工具重试、部成、在途订单** **为** **子态或观测维** **不改变** **§2** **主格** — **`trade-via-agent` S5.1**。

---

## 11. 扩容规则

**新增主态** **或** **放宽 ✗→✓** **或** **§2.2 Trigger 集变更** **须**：**同一 MR** **改** **`execution` 附录 A**、**本篇** **§2（** **含 §2.2** **）～§9**、[`runtime-state-machine.md`](./runtime-state-machine.md) **§3 图**、[`runtime-invariants.md`](./runtime-invariants.md) **（** **若** **触及** **不变式条目** **）**、[`observability/overview.md`](../observability/overview.md) **§2.4（** **若** **触及** **Trigger 映射** **）**；**实现关单** **建议** **核对** **`SC-OBS08`** **邻域**。

---

**文档版本**：2.1.3 · **维护**：产品 + Agent Runtime owner · **本版**：**§8.2 · §2.2.1 轨 B 核销/SC-B20**。**承** 2.1.2。
