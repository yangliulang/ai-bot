# 命名与 ID 约定（薄索引）

**建议默认**：`scenarioId` / `toolId` / `skillId` / `billCode` / `configKey` **与** [`../../design/api.md`](../../design/api.md)、[`domains/agent/exchange-agent/trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§8**、[`domains/admin/management-console-v1-prd.md`](../domains/admin/management-console-v1-prd.md) **§5.1** **对签**；**避免**同一概念多拼法。  
细则扩写可在此文件后续追加 **表格式**登记，不替代设计矩阵。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. 执行 ID、场景 ID、会话 ID、用户标识（产品规则）

下列规则约束 **语义、字符集、稳定性**；若与 **`design/api.md` OpenAPI `pattern` 或字段表** 冲突，**以 OpenAPI / 实现登记表为真源**，本文作需求侧 **默认下限**。**注册表真源**：`scenarioId` → [`domains/agent/agent-orchestration/routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)。

| 键 | 语义（职责） | 格式与字符（默认） | 稳定性与备注 |
|----|----------------|-------------------|--------------|
| **`executionId`** | 单次 **可计费 / 可观测** 执行的主锚；与计费、工具链、审计 **join**（[`observability/tracing.md`](../observability/tracing.md) · FR-T01）。 | **仅 ASCII 数字 `0-9`**；**长度** **10～19**（与 OpenAPI `ExecutionId` **同窗**）。**演示**建议 **`YYYYMMDDHHmmss` + 3 位序列**（17 位，例 `20260511143208001`）；**生产**由 Runtime **雪花 / 所内 bigint 字符串** 发号，**仍须**满足本字符集。**禁止**字母前缀（如 `exec-`）、连字符、空格、全角。 | **创建后不可变**；**禁止回收复用** 于另一条执行链。**禁止**以 Telegram `message_id` **直接充当** 业务主锚（见 [`Runtime/execution.md`](../Runtime/execution.md) §1 步 3）。 |
| **`scenarioId`** | 编排 **路由键 / 寄存器** 键，标识 **一类** 业务场景（读/写/自动化族）；Prompt 包、DAG、工具门禁 **对签**（[`routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)）。 | **点分命名空间**：至少 **两段**，段间 **`.`**；每段匹配 `^[a-z][a-z0-9_]*$`（例 `trade.spot.limit_order`）；**全文小写**；**建议总长** ≤ 128。**须**在寄存器登记后方可用于 **生产 TRADING 类** 发布前校验（见 [`prompt-management/functions.md`](../domains/admin/prompt-management/functions.md)）。 | 寄存器 **版本与冻结** 由 orchestration / contract-closure 管理；**禁止** 与 **`toolId`** **混名同义**。 |
| **`sessionId`** | **渠道会话**（如 chat）上下文锚：**同一会话** 可产生 **多条** `executionId`（[`Runtime/sessions.md`](../Runtime/sessions.md)）。 | 与 `executionId` **同一字符类**（小写、`0-9`、`-`）；**建议长度** 8–64。**演示**前缀可为 `sess-` + 短码；**生产**建议 **ULID** 等与渠道绑定实现 **同窗**。 | **会话生命周期内** 稳定；**换绑 / 归因** 不得导致 **执行串户 join**（见 onboarding / observability）。 |
| **用户标识（对内 / 对外）** | **内部真源 `userId`**：**Coobit 母账户（主账号）UID**，租户会员体系主键，用于权限、账务、实例绑定；**≠** 子账户 **`subUid`**。**对外 / 运营可见 `userIdMasked`（列表、日志默认列）**：满足 **可 join、可检索** 的 **脱敏** 形态。交易所品牌与所名 **Coobit**，需求与实现文档 **均勿写作** **Coolbit**。 | **内部 `userId`**：格式 **由 IAM / 账户域** 与 **`design/api`** 登记冻结（本文不造第二套）。**`userIdMasked`（运营侧约定下限）**：**仅** `a-z`、`0-9`、`-`、`_`；**建议** `u-` + 数字或短码（与 admin 演示 `u-10482` 一类 **演示谱系** 一致）；**不得** 默认展示 **邮箱/手机全量**。 | **禁止** 在需求文档中将 **`userIdMasked`** 与 **`userId`** **当作可互换字符串**；对外报表 **脱敏规则** 与 observability **§2** / **`admin` IA** **同窗**。 |

**实现提示**：控制台筛选「用户标识」字段应对齐 API 返回 **`userIdMasked`** 或文档化之 **等价检索键**；深链 `buildObservabilitySearch` **同窗** [`observability` · FR-MC802](../domains/admin/observability-management/functions.md)。

**OpenAPI**：`pattern` / `minLength` / `maxLength` 冻结于 [`openapi/components/identity-schemas.yaml`](../../openapi/components/identity-schemas.yaml)（**`ExecutionId`** = **纯数字** `[0-9]{10,19}`，与上表一致）。

---

**文档版本**：1.2.2 · **维护**：产品 + 架构 · **本版**：**`executionId`** **冻结为纯数字 10～19 位**（废弃 `exec-` slug / ULID 并集）。**承** 1.2.1。
