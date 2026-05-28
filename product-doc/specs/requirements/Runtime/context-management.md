# Runtime · 上下文管理

**职责**：推理与工具链 **上下文管线**（窗口预算、压缩、爆炸保护、多轮合并）在 **跨域一致读模型** 下的 **需求下限**。**不写** Prompt 资产目录 — 宿主 **`prompts/`** 与 **prompt-management**。

**同窗**（短）：[`domains/agent/agent-context/overview.md`](../domains/agent/agent-context/overview.md)；[`domains/admin/prompt-management/overview.md`](../domains/admin/prompt-management/overview.md)；[`memory-runtime.md`](./memory-runtime.md)（**Memory 分域·注入·TTL 口径**）。**横向全表** → [`boundaries.md`](./boundaries.md)；总览 → [`overview.md`](./overview.md)。

---

## 1. 产品下限（需求草案）

- **预算违反**时 **须**有 **可观测**降级路径（截断/摘要/拒绝）**之一**，**不得**静默截断致 **交易语义**与 **用户确认**不一致。  
- **与计费**同窗：上下文扩展 **不得**单方面承诺 **免费增值**（须 **billing/FR** 对签）。  

## 2. 隔离与反污染（会话 · `executionId` · 工具回填）

**用途**：收窄 **「Memory 污染」** 在工程上常指的 **跨会话串料、跨执行 Unit 误用旧工具结果、租户串户** — **本条为产品下限**；**字段级与拼装算法** → **`prompt-management` + `design` 冻结**。

| 风险面 | **须（MUST）** |
|--------|----------------|
| **归因与拼装** | **注入模型上下文** 的 **工具结果 / 编排摘要** **须** **可追溯** **到** **当前回合** **的** **`sessionId` + `executionId`**（**或** **观测域规定的等价 join 键**）— **与** [`observability/overview.md`](../observability/overview.md) **§2.1**、[`execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md) **§1** **同窗**。 |
| **跨会话 / 跨用户** | **不得** **将** **其他用户**、**其他 `sessionId`** **下** **产生** **之** **私有工具输出** **静默混入** **本用户** **本轮** **Prompt 装配路径**（**租户隔离原则** **见** [`locking.md`](./locking.md) **§1**）。 |
| **跨 `executionId` 陈旧结果** | **已终局** **之** **前序** **`executionId`** **的** **工具快照** **不得** **在无** **重拉 / 重算 / 明示降级策略** **下** **冒充** **当前** **行情·订单·余额** **真值** **驱动** **新的** **类型 A 或交易所写**（**细则** **可** **落** **确认流 / UX 冻结 MR** **与** [`unknown-state.md`](./unknown-state.md) **对签**）。 |
| **STM 全量聊天** | **禁止** **无差别** **把** **全 Telegram 线程、raw 工具 JSON、内部编排载荷 ** **写入** **Prompt messages** — **准入** **[`memory-runtime` §15](./memory-runtime.md#15-stm-写入准入--什么进什么不进must)** |
| **记忆四原则** | **该记/不该记/该忘/不该忘** **执法** **须** **在 Prompt 装配前完成** — **[`memory-runtime` §16](./memory-runtime.md#16-记忆治理四原则must--防僵尸澄清--防错乱写)** · **`FR-STM11`** |
| **Prompt 注入面** | **用户可控文本** **与** **工具 JSON** **进入** **SYSTEM/TRADING 块** **之** **闸** **见** [`prompt-management/runtime-injection.md`](../domains/admin/prompt-management/runtime-injection.md) **§2～§5、§7** — **不** **在本条** **复述** **denylist**。 |

**抽检**：**[`evals/scenarios.md`](../evals/scenarios.md)** **`eval.context.session_execution_tool_bind`**（**登记宿主**）。

## 3. 预算裁剪与记忆召回（同窗 [`memory-runtime` §11](./memory-runtime.md)）

**超 token/字符 budget 时** **须** **可观测** **裁剪（§1）**，**且** **遵守** **下列顺序** — **完整表** **见** **`memory-runtime` §11**：

1. **先** **L0 远端轮次 / 次要摘要**  
2. **再** **LTM Semantic 非关键句**（**不得** **半条命题**）  
3. **仍不足** → **拒扩或短答** — **禁止** **删** **本 execution 类型 A（②）** **与本 execution 工具 Facts（④）**

**旧稿回迁**：承接原 **`memory.md`** 叙事占位，**现以本条为需求下限入口**。

---

**文档版本**：1.1.2 · **维护**：产品 + Agent Runtime owner · **本版**：**§3 预算裁剪与记忆召回**（链 **`memory-runtime` §11**）。**承** 1.1.1。
