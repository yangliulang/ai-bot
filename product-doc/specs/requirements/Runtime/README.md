# Runtime（横切运行时需求）

**主入口**：[**overview.md**](./overview.md)（目录地图、书写约定）· **概念管线对签**：[**domain-model.md**](./domain-model.md) · **Memory / STM**：[**memory-runtime.md**](./memory-runtime.md)（**§14.6 stale+Resume** · **§16 四原则**）· **Truth Source**：[**runtime-truth-source-map.md**](./runtime-truth-source-map.md) · **状态机**：[**runtime-state-machine.md**](./runtime-state-machine.md) · **迁移矩阵**：[**execution-transition-matrix.md**](./execution-transition-matrix.md)（**§2.2 逐边**）· **Trigger→观测**：[**observability** §2.4](../observability/overview.md) · **`SC-OBS08`** · **Planner**：[**planner-contract.md**](./planner-contract.md) · **Failure**：[**failure-matrix.md**](./failure-matrix.md) · **邻域**：[**boundaries.md**](./boundaries.md) · **执行管线**：[**execution.md**](./execution.md) §1（**步 7 · Intent→Canonical→Gateway 文档链**）· **Fallback**：[**fallback-policy.md**](./fallback-policy.md)

**端到端鸟瞰**：[**`flow/e2e-closed-loop.md`**](../../../flow/e2e-closed-loop.md) — 文首 **「架构语言」** → [**`architecture` §对照**](../../../design/architecture.md)。

本路径即 **`specs/requirements/Runtime/`**；[`requirements/README.md`](../README.md)、[`spec.md`](../spec.md)、`.specify` 等处 **`Runtime/`** 均指本目录。**FR/SC SSOT** 仍以各 **`domains/`** 正文为准。

**清点口径**：专题 **分卷** 与 **`README` / `overview`** 并存；评估中的「Runtime 文件个数」**勿写死**，以 **当前分支** 实际枚举为准（参见 [`product/release-notes.md`](../../../product/release-notes.md) 篇首 **完整性读法**）。

**目录名 `Runtime/` 首字母大写**：与各主题小写目录（如 `risk/`、`metrics/`）刻意区分，**表示运行时横切主链**；工具或脚本偏好全小写路径时，**以本篇与 `requirements/README` 的显式链接为准**，勿假定大小写可互换。
