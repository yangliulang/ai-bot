# Runtime Architecture

**当前真源**：逻辑层面的 **组件边界与数据流**以 **[`architecture.md`](./architecture.md)**、**[`deployment.md`](./deployment.md)** 为准；单次请求的 **执行管线（概念序）**以 **[`requirements/Runtime/execution.md` §1](../requirements/Runtime/execution.md)** 为准。

**统一交易语义与 Execution Gateway（文档 A vs 所内实现）**：[`canonical-trading-model.md`](./canonical-trading-model.md)、[`ADR-004`](./adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../requirements/domains/agent/exchange-agent/trade-assistance.md)；**契约** [`CC-P1-07`](../requirements/contract-closure.md#cc-p1-07)；**人类评审** [`requirements-review` §7.5](../../product/requirements-review.md#cc-adr004-review-checklist)；**管线落点** **[`execution` §1 步 7](../requirements/Runtime/execution.md)**。**Gateway 可执行代码** **不在本规格仓** — **同窗** **ADR-004** **后果段**。

**关单余量（MR 首节）**：[`closure-remaining` §0](../requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../requirements/closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../requirements/closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../requirements/contract-closure.md)。

**本文件**：**运行时组件级 / 进程级** 一图一表 的 **唯一挂载点**（与 **[`architecture.md`](./architecture.md)**、**[`deployment.md`](./deployment.md)**、**[`requirements/Runtime/`](../requirements/Runtime/)**、**[`exchange-agent/overview.md`](../requirements/domains/agent/exchange-agent/overview.md)** 对签后充实）。**需求已锚定（只读）**：展开时 **须**自洽于 **[`requirements/Runtime/execution.md` §1](../requirements/Runtime/execution.md)** 管线序、**[`Runtime/boundaries.md`](../requirements/Runtime/boundaries.md)** 分工、**[`Runtime/reconciliation.md`](../requirements/Runtime/reconciliation.md)** 对账 — **不**另写与上述 **五处** 矛盾的拓扑描述。

**曾计划的展开项**（回填时勾选）：运行时内部分层（接入 / 编排 / **工具执行**（**Coobit 出站：默认 `openapi-ai` 子进程或等价承载 + `allowlist` 断言点**）/ **出站观测**）、与 **队列/有状态存储** 的边界、与 **多实例** 下 **locking** 的落点 — 需求侧索引 [`Runtime/locking.md`](../requirements/Runtime/locking.md)。**Memory 热/温/冷默认 TTL（v0）**：[`architecture.md`](./architecture.md) **「Memory 留存」**。**`stableReason` 与 Taxonomy**：[`api.md`](./api.md) **附录**。**相关设计切片**（真源仍分散于 `api`/域）：[`sub-account-isolation.md`](./sub-account-isolation.md)、[`tool-calling-sequence.md`](./tool-calling-sequence.md)。**宿主叙事**：[`integrations/exchange/overview.md`](../requirements/integrations/exchange/overview.md)。

### 小团队互链（快照 · 不新增第二套 FR）

- **组件级图仍为充实项**：**不** 单独以本文充当「运行时拓扑已冻结」的对外话术；**文档级 TBD / 不承诺摘要**见 **[`product/release-notes.md`](../../product/release-notes.md)**，日常关门范式见 **[`LITE-MODE.md`](../requirements/LITE-MODE.md)** §3。  
- **生产契约**仍以 **[`contract-closure.md`](../requirements/contract-closure.md)** 与 **`architecture` / `deployment` / [`Runtime/`](../requirements/Runtime/)** 正文 **同窗 MR** 为准。

---

**文档版本**：1.0.6 · **维护**：系统架构 + Agent Runtime owner · **本版**：**篇首补** **`closure-remaining` §0·§6/§6.4**。**承** **1.0.5**。
