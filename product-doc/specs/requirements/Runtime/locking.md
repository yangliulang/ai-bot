# Runtime · 锁与并发

**职责**：**单实例 / 多分片**下 **同一用户-会话-语义键** **互斥**、租约 TTL、防止 **双执行** **与幂等同窗**。**不**替代 **分布式锁中间件选型** ADR。

**同窗**（短）：[`domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md)；[`execution.md`](./execution.md)；[`persistence.md`](./persistence.md)；[`recovery.md`](./recovery.md)；[`design/architecture.md`](../../design/architecture.md)；[`domains/agent/agent-orchestration/session-concurrency-policy.md`](../domains/agent/agent-orchestration/session-concurrency-policy.md) **（单 session 产品优先级 · D-1）**。**横向全表** → [`boundaries.md`](./boundaries.md)。

---

## 1. 原则摘要（下限）

- **显式用户在途（D-1）** **须** **可查询**或可解释（与 **`monitoring-tasks`、`trade-assistance`** **同窗术语**）。  
- **租户隔离**：租户 / Agent 实例 A **互斥或排队故障** **不得**表现为租户 B **静默成功或静默丢弃**（同窗 **architecture**、[`execution.md`](./execution.md) **§1 队列**）。  

---

## 2. 行为与验收下限

| 主题 | 要求 |
|------|------|
| **互斥粒度（产品）** | 对 **同一用户 + 同一绑定revision（或等价）+ 同类可编排「在途」写操作** 须定义 **是否串行**：若 **D-1** 为真（挡后续写），**须** **用户可见或可诊断**；若允许并行，**须**与 [**`exchange-agent` / risk**](../domains/agent/exchange-agent/boundaries.md) **无矛盾** 且 **终态与计费不双花**。**单 session 多 execution / inbound 队列** **产品优先级 SSOT** → [`session-concurrency-policy.md`](../domains/agent/agent-orchestration/session-concurrency-policy.md) **（** **不** **替代** **本篇分布式锁** **）**。 |
| **租约与 TTL** | 若在途锁 **带 TTL**，**到期释放** **不得**在 **未到达 UNKNOWN/终局** 时 **默默**允许 **第二笔**写 **产生重复副作用**；与 [**`unknown-state.md`**](./unknown-state.md)、[**`recovery.md`**](./recovery.md) **对签**。 |
| **幂等协同** | 互斥 **不得**替代 **客户端/服务端幂等键**；**同一 `idempotencyKey`/`executionId` 段** 的 **重试** **仍须**满足于 [**`persistence.md`**](./persistence.md)、[`api.md`](../../design/api.md) **同窗**。 |
| **多分片** | **分片搬迁/扩缩容** 下 **不得**出现 **双主**执行同一 **业务互斥域**；**具体 fencing / epoch** → **工程 ADR**，本文 **只**要求 **行为上不双执行、不静默串户**。 |
| **附录 A 主态写入权威** | **同一 `executionId`** **对外的「当前主态」（附录 A 主行）** **须** **由单一逻辑写入者** **提交变更** — **实现上** **映射为** **编排运行时 / 状态机宿主**（**服务名与部署边界** **须在实现 ADR 登记**）。**计费、观测、对账、通道适配** **等模块** **不得** **裸写** **覆盖** **主态行**；**仅允许** **通过** **契约化输入**（**领域事件、内部 API、幂等回调**）**由宿主** **按** [`execution-transition-matrix.md`](./execution-transition-matrix.md) **归并** **迁移**。**多 Worker / 多实例** **并发认领同一执行** **时** **须** **租约、fence token、或乐观版本号** **择一以上** **串行化提交**；**禁止** **无协调双写** **导致** **主态分叉** **或** **终局双计费**。 |

---

## 3. 明确不包含

- **锁中间件产品选型、Redis/etcd 细节、看门狗实现**。  
- **字段级 OpenAPI**。  

---

**文档版本**：1.0.4 · **维护**：产品 + Agent Runtime owner · **本版**：**互引** **`session-concurrency-policy`**。**承** 1.0.3。
