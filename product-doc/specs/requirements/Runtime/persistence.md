# Runtime · 持久化与检查点

**职责**：**可恢复**执行 **须**落哪些 **业务键/版本/步骤游标**（不含 Secret），与 **幂等**、**重放**、**冷启动**同窗。**不写**具体存储引擎选型 — **以 ADR** 为准。

**同窗**（短）：[`design/api.md`](../../design/api.md)；[`domains/agent/agent-orchestration/runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md)；[`recovery.md`](./recovery.md)；[`unknown-state.md`](./unknown-state.md)；[`reconciliation.md`](./reconciliation.md)；[`event-storage.md`](./event-storage.md)；[`execution.md`](./execution.md)。**横向全表** → [`boundaries.md`](./boundaries.md)。

---

## 1. 原则摘要（下限）

- **同一 `operationId`（或等价）** **重放** **不得**产生 **双倍用户可见副作用**（与 **交易所/工具** **幂等契约**对签）。  
- **检查点** **须**含 **足够**信息支持 **运营可诊断**的 **挂起/续跑**（字段级 **OpenAPI** **不**在此展开）。  

---

## 2. 行为与验收下限

| 主题 | 要求 |
|------|------|
| **检查点最小信息** | **须**能恢复：**`executionId`**、**编排步骤游标 / `orchestrationVersion`**（若适用）、**冻结/Kill 摘要**、**幂等键状态**、**最后已知上游可判定结果或 UNKNOWN** — **与** [`runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md)、[`freeze-policy.md`](./freeze-policy.md) **同窗**。 |
| **重放顺序** | **冷启动重放** **不得**在 **已知终局已达成** 后 **再次触发** **可计费终局**（与 [`consume-and-bill.md`](../flows/consume-and-bill.md)、[`billing.md`](../domains/admin/billing-management/overview.md) **§10.1** 同窗）。 |
| **与恢复策略** | **退避、最大重试、降级** **须**与 [`recovery.md`](./recovery.md) **一致**；检查点 **须**记录 **足够**信息以解释 **为何停在此态**。 |
| **Secret** | **检查点与幂等表** **默认不落**明文 **API Secret / `secretRef` 展开值**；**与** [`architecture.md`](../../design/architecture.md) **信任区分**一致。 |
| **检查点放置（相对外向 IO）** | **至少** **在下列时机** **须** **持久化或等价预写日志**（**具体存储** **ADR**）：**(1)** **附录 A 主态** **迁出** **前一态** **前** **或** **与迁移** **同一原子单元**（**避免** **崩溃后** **主态超前于** **已提交之外网副作用**）；**(2)** **交易所写** **返回** **`504`/UNKNOWN** **或** **终态不可判定** **之后** **（** **挂起** **须可恢复** **—同窗** [`unknown-state.md`](./unknown-state.md) **）**；**(3)** **工作进程优雅关停** **或** **租约即将丧失** **前** **的最新游标**。**不得** **在** **未持有** [`locking.md`](./locking.md) **§2** **所要求协调假设下** **推进** **不可逆写**。**与 DAG 节点一一映射** **的细化图** → [`runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md) **+** **实现 MR**。 |

---

## 3. 明确不包含

- **存储引擎、表名、主键策略、多活复制** — **ADR / 数据设计 MR**。  
- **具体字段表** — **OpenAPI / observability schema**。  

---

**文档版本**：1.0.3 · **维护**：产品 + Agent Runtime owner · **本版**：§2 **检查点放置（相对外向 IO）**。**承** 1.0.2。
