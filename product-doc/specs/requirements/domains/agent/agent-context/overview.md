# Agent Context（会话上下文）

**职责**：用户侧 **对话窗口预算、压缩与截断、工具结果回填、长会话（尤其 `tool.web.*`）与上下文爆炸降级** 的 **域级入口**。**不写** OpenAPI 明细与 Prompt 条文全文 — API 矩阵见 [`design/api.md`](../../../../design/api.md)；Prompt 资产见 [`prompts/`](../../../prompts/README.md) 与 [`prompt-management/overview.md`](../../admin/prompt-management/overview.md)。

---

## SSOT 分工（须无 FR 冲突）

| 主题 | 权威 |
|------|------|
| 上下文管线下限（压缩、降级路径、与计费同窗） | [`Runtime/context-management.md`](../../../Runtime/context-management.md) **§1～§3**（**§2** **隔离 / 反污染**；**§3** **裁剪序**）、[`Runtime/memory-runtime.md`](../../../Runtime/memory-runtime.md)（**§2.0 STM/LTM**；**§10 召回**；**§11 裁剪**；**§9 `FR-MEM*`**；**§13 `FR-STM*`**）、[`Runtime/overview.md`](../../../Runtime/overview.md) §1 |
| **单次执行工具/编排步预算**（**`FR-AO06`**，**非** token 分项预算） | [`../agent-orchestration/execution-lifecycle.md`](../agent-orchestration/execution-lifecycle.md) **§4**、[`Runtime/execution.md`](../../../Runtime/execution.md) **§1** |
| 工具调用 / B&C 归因与观测下限 | [`observability/overview.md`](../../../observability/overview.md) **§2.1～2.2** |
| C 类外传、Disclaimer、`tool.web.*` 行为 | [`exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **§8.4**；契约见 [`contract-closure.md`](../../../contract-closure.md) **CC-P1-02**；关单余量 [**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · [**§6/§6.4**](../../../closure-remaining.md#cc-exec-solve-path) |
| 计费与「上下文扩展是否影响 inputTokens」终裁 | [`billing-management/overview.md`](../../admin/billing-management/overview.md)（与 **`D-9`** / `observability` **同窗 MR**）、**Runtime/context-management §1** |
| **反污染抽检** | **工具回填** **须** **与** **`sessionId`/`executionId` 同窗** — [`Runtime/context-management.md`](../../../Runtime/context-management.md) **§2**；**eval** → [`evals/scenarios.md`](../../../evals/scenarios.md) **`eval.context.session_execution_tool_bind`** |
| **跨会话 Semantic Narrative（解冻草案）** | [`Runtime/memory-runtime.md` §9](../../../Runtime/memory-runtime.md) **`FR-MEM*`/`SC-MEM*`**；**默认 TBD/OFF** |

**本目录**：首版仅 **`overview.md`**；细分条目随 Wave D／`Runtime` 分卷再拆。

---

**文档版本**：1.0.4 · **维护**：产品 + Agent Runtime owner · **本版**：**SSOT 表链** **`memory-runtime` §13 STM**。**承** 1.0.3。
