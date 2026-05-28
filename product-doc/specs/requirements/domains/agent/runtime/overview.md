# Agent Runtime（用户侧 · 域内索引）

**职责**：从 **`domains/agent/`** 视角串联 **「用户请求如何进入可计费执行、如何与会话/编排交界、如何冻结与恢复」** 的 **导航入口**。**横切需求正文、目录地图与版本脚注**在 **[`Runtime/overview.md`](../../../Runtime/overview.md)**；**与邻域的 SSOT 分工表**在 **[`Runtime/boundaries.md`](../../../Runtime/boundaries.md)**。本目录 **不**抄写 [`design/api.md`](../../../../design/api.md)，**不**新建与域正文或设计矩阵冲突的 FR/SC。

**小团队 / 发版**：[`product/release-notes.md`](../../../../../product/release-notes.md) · [`LITE-MODE`](../../../LITE-MODE.md) §3；**设计侧组件级挂载** [`design/runtime-architecture.md`](../../../../design/runtime-architecture.md)。

---

## 1. 为何曾为空

仓库刻意将 **运行时契约叙事** 收敛到 **`specs/requirements/Runtime/`**，避免与 **`agent-orchestration`**、**`onboarding`**、**`exchange-agent`** 等重复定义；**`domains/agent/runtime/`** 此前仅作 **占位**。现以本篇补齐 **`agent/`** 树内的 **索引透镜**；**细分专题正文**仍优先落在 **`Runtime/`** 分卷或 **邻域单文件**。

---

## 2. SSOT 分工（须无 FR 冲突）

| 主题 | 权威 / 先读 |
|------|-------------|
| 调度、Planner、队列、**可计费执行**投递 | [`Runtime/execution.md`](../../../Runtime/execution.md)、[`Runtime/overview.md`](../../../Runtime/overview.md) §1 |
| 会话载体、绑定与 **execution** 交界 | [`Runtime/sessions.md`](../../../Runtime/sessions.md)；[`../onboarding/telegram-binding.md`](../onboarding/telegram-binding.md) |
| `agentState`、门禁短路、用户摘要 | [`Runtime/runtime-state.md`](../../../Runtime/runtime-state.md)；[`../exchange-agent/boundaries.md`](../exchange-agent/boundaries.md) |
| Kill / 冻结 / **`orchestrationVersion`** | [`Runtime/freeze-policy.md`](../../../Runtime/freeze-policy.md)；[`../agent-orchestration/runtime-freeze.md`](../agent-orchestration/runtime-freeze.md) |
| 开通 → 可接单、Warm-up / Provisioning 归因 | [`../onboarding/runtime-provisioning.md`](../onboarding/runtime-provisioning.md) |
| 上下文管线、预算与压缩 | [`../agent-context/overview.md`](../agent-context/overview.md) → [`Runtime/context-management.md`](../../../Runtime/context-management.md) |
| **`FR-AO*`**、步骤机、用户可见重试 | [`../agent-orchestration/overview.md`](../agent-orchestration/overview.md)、[`../agent-orchestration/retry-policy.md`](../agent-orchestration/retry-policy.md) |
| **`executionId` 主态 / 迁移契约 / UNKNOWN≠终局** | [`Runtime/runtime-state-machine.md`](../../../Runtime/runtime-state-machine.md)、[`Runtime/execution-transition-matrix.md`](../../../Runtime/execution-transition-matrix.md)；**Trigger→观测** [`observability/overview.md`](../../../observability/overview.md) **§2.4 · `SC-OBS08`**；[`Runtime/execution.md` 附录 A](../../../Runtime/execution.md) |
| **Planner 可审入口** | [`Runtime/planner-contract.md`](../../../Runtime/planner-contract.md) → [`../agent-orchestration/execution-lifecycle.md`](../agent-orchestration/execution-lifecycle.md) **§5** |
| **Memory P2 / 上下文硬下限** | [`Runtime/memory-runtime.md`](../../../Runtime/memory-runtime.md)（**v1 分域·注入·TTL**）；[`Runtime/context-management.md`](../../../Runtime/context-management.md) |
| 幂等、`504` / UNKNOWN、HTTP 矩阵 | [`design/api.md`](../../../../design/api.md)；[`Runtime/recovery.md`](../../../Runtime/recovery.md)、[`Runtime/unknown-state.md`](../../../Runtime/unknown-state.md) |
| **逻辑架构、环境/发布（设计侧）** | [`design/architecture.md`](../../../../design/architecture.md)、[`design/deployment.md`](../../../../design/deployment.md)；单条请求 **概念序** [`Runtime/execution.md` §1](../../../Runtime/execution.md) |

更细的 **主题 ↔ 宿主** 映射见 **[`Runtime/boundaries.md`](../../../Runtime/boundaries.md)**。

---

## 3. 扩展规则

- **仅用户侧措辞、且不跨 `admin/`**：可在 **`domains/agent/runtime/`** 增页，并 **脚注对应域内 FR/SC**。  
- **跨多域或需独立评审/版本脚注**：**正文落在 `Runtime/`** 分卷；此处 **只保留链回与评审提示**。  

**本目录**：首版 **`overview.md`** + **`README.md`**；与 **`exchange-agent/boundaries.md`** 中 **`../runtime/`** 链同窗。

---

**文档版本**：1.0.4 · **维护**：产品 + Agent Runtime owner · **本版**：**§2** **主态行** **链 **`observability` §2.4。**承** 1.0.3。
