# Runtime · 会话与执行上下文边界

**职责**：**`chat`/渠道会话** ↔ **`userId`（± 实例上下文）** 绑定生效后，**单次用户输入**如何在 Runtime 侧挂载 **可追溯执行锚点**，并与 **会话绑定 SSOT** 无冲突。**不**重写 Telegram 矩阵 — 宿主 **`onboarding`/渠道**。

**同窗**（短）：[`telegram-binding.md`](../domains/agent/onboarding/telegram-binding.md)；[`domains/agent/onboarding/overview.md`](../domains/agent/onboarding/overview.md)；[`Runtime/context-management.md`](./context-management.md)；[`observability/overview.md`](../observability/overview.md) · **`executionId`/`invocationState`**；[`flows/consume-and-bill.md`](../flows/consume-and-bill.md)；[`domains/agent/agent-orchestration/session-concurrency-policy.md`](../domains/agent/agent-orchestration/session-concurrency-policy.md) **（inbound 队列 · 多 execution）**。**横向全表** → [`boundaries.md`](./boundaries.md)。

---

## 1. 原则摘要（下限）

- **绑定快照**：执行路径 **须**能以 **不脱敏观测**可解释的键 **join** **合法绑定** revision；换绑后与 **旧执行**归因 **不得**串户（与 [`telegram-binding.md`](../domains/agent/onboarding/telegram-binding.md) **resolvedBinding** 叙事同窗）。  
- **执行实例化**：单次请求 **须有** **`executionId`（或合并字段）** **可与**计费、审计 **对齐**的实现定义（真源宿主 **`design`/observability**）。**`executionId` / `sessionId` / 用户标识** **默认格式与语义** → [`standards/naming-standard.md`](../standards/naming-standard.md) **§1**。  

---

## 2. 行为与验收下限

| 主题 | 要求 |
|------|------|
| **会话上下文指针** | 自 **渠道入站到 Planner 起票** 须保留 **稳定会话引用**（实现可为 `sessionId` / `chatId` + 绑定 revision 之组合），**禁止**仅靠 **单条 Telegram `message_id`** 承载 **跨异步边界**的执行锚点。 |
| **换绑与历史** | **绑定变更生效后** **新执行** **须**按新绑定解析 **Coobit 子账户 scope**；**历史 `executionId`** 的归因与导出 **不得**因换绑而 **改写**为「仿佛始终在新子账户下发生」。 |
| **与会话预算/压缩** | 会话级 **上下文预算、压缩策略** 的 **读模型** → [`context-management.md`](./context-management.md)；本文 **只**要求 **执行锚点与会话键**在 **观测与计费 join** 中 **可恢复、不串户**。 |
| **与编排冻结** | 若会话内存在 **`resolvedPromptBinding` / `orchestrationVersion` 冻结** 语义，**单会话多并发**时 **不得**出现 **可计费执行** 使用 **已过期的绑定快照** 仍向用户展示为「当前有效契约」（与 [`prompt-management/overview.md`](../domains/admin/prompt-management/overview.md) **PM-C10**、[`freeze-policy.md`](./freeze-policy.md) 同窗验收）。**inbound 串行与在途写上限** → [`session-concurrency-policy.md`](../domains/agent/agent-orchestration/session-concurrency-policy.md) **§2～§3**。 |

---

## 3. 明确不包含

- **Telegram 卡片模板正文、H5 深链文案** → [`telegram/overview.md`](../domains/agent/telegram/overview.md)。  
- **字段级 OpenAPI / DB DDL**；**渠道连接器实现选型** — **ADR / Infra**。  

---

**文档版本**：1.0.3 · **维护**：产品 + Agent Runtime owner · **本版**：§2 **行为与验收下限**（由原占位扩展）。**顺延 1.0.2**。
