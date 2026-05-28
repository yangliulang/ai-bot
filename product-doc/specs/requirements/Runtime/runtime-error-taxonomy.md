# Runtime · 错误分类（Error Taxonomy → 处置）

**路径**：`specs/requirements/Runtime/runtime-error-taxonomy.md`。

**职责**：给出 **平台侧错误「种类」** **到** **默认 Runtime 语义** **的分类层**（**Taxonomy**），**与** **[`failure-matrix.md`](./failure-matrix.md)** **§2** **对读**；**具体 `stableReason` 字面** **仍** **只认** **[`error-normalization.md`](./error-normalization.md)** **与** **`design` 登记表**。

**同窗**：[`recovery.md`](./recovery.md)；[`unknown-state.md`](./unknown-state.md)；[`retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md)；[`../../design/api.md`](../../design/api.md) **附录 · `stableReason`↔Taxonomy**。

---

## 1. 分类（产品词）

| **Taxonomy 类** | **含义（摘要）** | **典型默认动作** | **详表** |
|-----------------|------------------|------------------|----------|
| **`TRANSIENT_UPSTREAM`** | 超时、连接抖动、可重试 5xx / 供应商**瞬态** | **Retry**（有界）→ 失败则 **UNKNOWN 或 failed** | [`failure-matrix.md`](./failure-matrix.md) §2 行 1 |
| **`RISK_OR_CONFIG_GATE`** | Kill、Pause、子账户/权限、**FR-T02** 拒绝 | **Stop** | [`failure-matrix.md`](./failure-matrix.md) §2 行 2 |
| **`WRITE_PARAMETER_CONTRACT`** | 写参数完备性/血缘违例（[`runtime-invariants`](./runtime-invariants.md) **INV-008～010**）：缺槽、非法 `provenance`、Parser/Adapter **默认占位** | **Stop** + **`FR-T05` 可解释**（**典型实现枚举** **`WRITE_PARAMS_INCOMPLETE`/`INVALID_PARAMETER_SOURCE`** → **登记** [`error-normalization`](./error-normalization.md)） | [`failure-matrix.md`](./failure-matrix.md) §2；[`confirmation-flow` 步骤 2](../domains/agent/agent-orchestration/confirmation-flow.md) |
| **`BUDGET_OR_QUOTA`** | **FR-AO06**、外网步池顶 | **Stop** + 可解释码 | [`failure-matrix.md`](./failure-matrix.md) §2 行 3 |
| **`UNKNOWN_OR_AMBIGUOUS_END`** | **504**、双通道冲突未裁决、**不得冒充成功** | **Reconciliation** | [`failure-matrix.md`](./failure-matrix.md) §2 行 4；[`unknown-state.md`](./unknown-state.md) |
| **`PLATFORM_RECOVERABLE`** | 队列/实例故障、**检查点**可续 | **Resume** | [`failure-matrix.md`](./failure-matrix.md) §2 行 5 |
| **`IDEMPOTENCY_DUPLICATE`** | 重复回调/Webhook | **Idempotent ignore / merge** | [`failure-matrix.md`](./failure-matrix.md) §2 行 6 |
| **`TERMINAL_BUSINESS`** | 业务拒单、余额不足、规则违例（**已可采信**） | **failed**（**非** UNKNOWN） | 典型 `stableReason`：`TERMINAL_BUSINESS_REJECT` — [`design/api.md`](../../design/api.md) 附录；exchange-agent、映射表 |

**新增类** **须** **同时** **补** **本表** **与** **`failure-matrix` §2** **一行**。**`PLATFORM_RECOVERABLE`** **等** **类** **不** **保证** **各有独立** **`stableReason`** **字面**（**对内观测/编排** **可用** **Taxonomy** **或** **实现枚举**）。

---

## 2. 与 Planner / 禁忌

**Taxonomy** **不得** **被** **用作** **绕过** **[`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) §5.2** **之** **借口**（**如** **假重试** **跳过确认门**）。

---

**文档版本**：1.0.3 · **维护**：产品 + Agent Runtime owner · **本版**：**`WRITE_PARAMETER_CONTRACT`** **↔** **INV-008～010**。**承** 1.0.2。
