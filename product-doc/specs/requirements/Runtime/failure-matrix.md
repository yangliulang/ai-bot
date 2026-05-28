# Runtime · Failure Matrix（失败 → 处置 · 字段终裁索引）

**路径**：`specs/requirements/Runtime/failure-matrix.md`。

**职责**：把 **常见失败类** **到** **Runtime 处置**（停 / 重试 / 对账 / 恢复 / 幂等忽略）**与** **观测字段归宿** **收成单表索引**，降低 **Recovery 散落** 导致的 **Undefined Behavior**。**`stableReason` / 上游码表字面** **不** **在此 duplicated** — **归一化规则** → [`error-normalization.md`](./error-normalization.md)；**枚举登记** → [`design/api.md`](../../design/api.md) **或** **同窗** **exchange-agent 附录**（**单 SSOT** **见** `error-normalization` §「映射表 SSOT」）。

**同窗**：[`runtime-error-taxonomy.md`](./runtime-error-taxonomy.md)；[`recovery.md`](./recovery.md)；[`retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md)；[`unknown-state.md`](./unknown-state.md)；[`reconciliation.md`](./reconciliation.md)；[`persistence.md`](./persistence.md)；[`locking.md`](./locking.md)；[`runtime-truth-source-map.md`](./runtime-truth-source-map.md) **§3**；[`../../design/api.md`](../../design/api.md) **附录 · `stableReason`↔Taxonomy**。

---

## 1. 字段终裁（处置链必备）

| **字段 / 概念** | **终裁归属** | **用途（摘要）** |
|-----------------|--------------|------------------|
| **`stableReason`** | **`design/api` 登记表** **或** **exchange-agent 附录（二选一）** | 平台内 **聚合、告警路由、用户副本管道** |
| **`upstreamCode` / HTTP / body** | **观测保留 ·** [`error-normalization.md`](./error-normalization.md) **§分层** | **排障、供应商对账** |
| **可重试准入** | [`recovery.md`](./recovery.md) **须** **引用** **映射表版本** | **Planner / 队列退避** |
| **`executionId` + 幂等键** | [`persistence.md`](./persistence.md)、**`FR-B05`/`SC-B20`** **方向** | **重复回调、重复核销门闩** |

---

## 2. Failure → Runtime 动作（产品级）

| **失败 / 异常类（产品词）** | **默认 Runtime 动作** | **条文 / 叙事宿主** |
|----------------------------|----------------------|---------------------|
| **工具 / 网关超时、可归因可重试错误** | **退避重试**（有界）→ 仍失败则 **终局失败或 UNKNOWN** | [`recovery.md`](./recovery.md)、[`retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md) |
| **Risk / 门禁 / Kill / Pause 拒答** | **Stop**（**不** **扩张外网写**） | [`execution.md`](./execution.md) **§1 步 2**；[`kill-switch.md`](../risk/kill-switch.md) |
| **写参数契约违例（完备性 / 血缘 / 占位默认）** | **Stop**（**不** **调用 `call_exchange_write`** / **不扩张** **交易所写 `executing`**） | [`runtime-invariants.md`](./runtime-invariants.md) **§0、INV-008～010**；[`runtime-error-taxonomy.md`](./runtime-error-taxonomy.md) **`WRITE_PARAMETER_CONTRACT`** |
| **`FR-AO06` 预算顶** | **Stop** + **可解释码** | [`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§4** |
| **UNKNOWN / 504 / 终局未决** | **Reconciliation**（**不得当业务成功**） | [`unknown-state.md`](./unknown-state.md)；[`reconciliation.md`](./reconciliation.md) |
| **队列积压、实例崩溃、检查点已落盘** | **Resume**（**可恢复路径**） | [`execution.md`](./execution.md) **§2**；[`persistence.md`](./persistence.md)；[`locking.md`](./locking.md) |
| **重复 Update / 重复 Webhook / 重复终态回调** | **Idempotent ignore 或 合并到同一终局** | [`persistence.md`](./persistence.md)；**eval** **`telegram_update_idempotent`** **方向** |

**规则**：新增一行 **须** **有** **上表右侧级** **之** **宿主文档**；**禁止** **仅在本表** **发明无宿主处置**。**场景决策树（Retry/Fallback/Reconcile/Stop）** → [`fallback-policy.md`](./fallback-policy.md) **§2**。

---

## 3. 与 Planner 禁忌叠放

**Planner** **不得** **用重试 / 再规划** **覆盖** [`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§5.2** **禁忌**（例如 **绕过确认门**）。

---

**文档版本**：1.0.3 · **维护**：产品 + Agent Runtime owner · **本版**：**写参数契约** **_FAILURE_** **行。** **承** **1.0.2**。
