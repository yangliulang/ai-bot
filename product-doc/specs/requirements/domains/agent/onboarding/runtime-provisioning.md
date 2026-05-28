# 运行时就位（Provisioning）

本卷限定：当 **开通链**在技术上已满足 **FR-T02** 中与 **子账户/API** 相关的因子之后，单个 **Agent 实例**如何从「策略上允许调度」过渡到「可被 Runtime 接单并完成一次可计费执行」的产品下限。**Planner、队列、冷队列、D-1** 横切叙事见 [**`Runtime/overview.md`**](../../../Runtime/overview.md) **§1**（**[`execution.md`](../../../Runtime/execution.md)** 等）；实现细节 **不**在此展开。

---

## 1. 里程碑：开通 vs 可接单

| 代号 | 含义 | 宿主 |
|------|------|------|
| **M-A** | 主站侧 **子账户 + 子账户交易 API** 就绪 | [`initialization-flow.md`](initialization-flow.md) §1.2、[**`billing`** §2](../../../domains/admin/billing-management/overview.md) |
| **M-B** | Telegram **会话绑定**就绪 | [**`telegram-binding.md`**](telegram-binding.md) |
| **M-C** | 运营台若存在 Instance：**Runtime Start**（或等价）后 **实例可投递用户请求** | [**`agent-management`**](../../../domains/admin/agent-management/overview.md) |

向用户作出的「可以使用 Agent」类承诺 **至少**需要：**M-A** 成立 **且** 通过 [`consume-and-bill`](../../../flows/consume-and-bill.md) **S2** 中与 **VIP/计费/全局开关等**同窗的门禁（宿主 **activation-policy、exchange-agent**）。

若控制台显示实例 **Healthy** 但外层门禁未通过：**用户可见归因**必须以 **外层因子**为准，不得以「再走一遍开通页」泛泛替代（同窗 SC-ON-03）。

---

## 2. Runtime 机电态与用户可读归因

| 运行时动作（概念） | 用户摘要 / `lastProductBlockReason` 下限 |
|--------------------|--------------------------------------------|
| **Pause / Stop**（单实例） | **须区别于** onboarding 未完；归因指向 **运维/熔断/实例控制**同窗 [**`agent-management` rules**](../../../domains/admin/agent-management/rules.md) |
| **Warm-up / Provisioning** | 须有可读占位（载入中 / 备货中）；**不等价于**再次要求用户 **重做 §1.2 Key/onboarding**（**Pause/Warm-up ≠** 密钥吊销） |
| **全局 Pause / Kill** | 须与 **单方实例 Pause** 可区分（叠加规则同窗 **exchange-agent boundaries、附录 A**） |

---

## 3. `agentState`、机电态与用户话术（附录 A §9）

**`agentState` 枚举真源**见 [**`management-console-v1-prd` §9**](../../../domains/admin/management-console-v1-prd.md)（`NORMAL`、`GLOBAL_OFF`、`OPS_SUSPENDED`、`MEMBERSHIP_BLOCKED`、`AGENT_SUBACCOUNT_BLOCKED`、`BILLING_BLOCKED`，与 `exchange-agent` / flow 对签）。

本节规定：**实例 Pause、Warm-up、全局熔断**在向用户解释时，**不得误诊为「必须重新走 onboarding（§1.2 绑定页校验链）」**，须与 [`activation-policy` §1](activation-policy.md) **归因诚实性**同窗。GWT 场景以 **ON-GWT-* / ON-PERM-*** 为主宿主；本节为 **话术与 `agentState` 映射下限**，评审时与 [`initialization-flow` §7](initialization-flow.md) **一并**对读。

| **典型技术态**（实现可映射为多字段） | **用户摘要侧推荐主锚** | **禁止的误导话术** |
|--------------------------------------|------------------------|--------------------|
| **实例 Pause**（单实例，[**`agent-management` rules §3**](../../../domains/admin/agent-management/rules.md)） | **`OPS_SUSPENDED`**（若产品与 **IA** 约定「实例级 Pause 单独分项」则摘要可 **整体 `agentState` + 分项原因**——以 **`design` / 附录 A** 为准） | 「请先去 **主站重绑 Agent Key**」——**除非**归因 **确为**本子账户 / API **未就绪**（Pause **≠** 必然重做 onboarding） |
| **OPS 全局 Pause** | **`GLOBAL_OFF`**（或附录同窗的全局熔断枚举） | 同上 |
| **Warm-up / Provisioning** | 通常落在 **`NORMAL`**；可辅以会话内「载入中」或 **`lastProductBlockReason`**（以 **`design`** 冻结为准） | 「API Key **已吊销**」——**Warm-up ≠** 密钥吊销 |
| **子账户 / API 真未就绪** | **`AGENT_SUBACCOUNT_BLOCKED`** 等（同窗 [`activation-policy` §5](activation-policy.md)） | 「**运维停机**」——**颠倒**归因 |
| **会员 / 计费阻断** | **`MEMBERSHIP_BLOCKED`** / **`BILLING_BLOCKED`** | 用「子账户未开」掩盖 **VIP / 欠费** |

**叠加**：实例 Pause **且** OPS 全局 on 时，须满足 [**`agent-management` rules §3.3**](../../../domains/admin/agent-management/rules.md)：**两行原因**均需对用户或运营 **可解释**；Resume 实例在全局仍 on 时 **可能仍不可执行**。

---

## 4. 冷启动与首条计费

- **新实例**：从第一条可进入 **accepted 计费**路径的用户消息之前的 **Warm-up**（模型/提示装配等），超时须有 **可读原因**或可退避路径；话术须与 **§3** 一致——**不得**把 **Warm-up** 写成「须 **重新**开通」。  
- **租户隔离**：单租户 Pause 不得静默把失败「转嫁」给其他租户会话（宿主 [`design/architecture.md`](../../../../design/architecture.md) 所载信任边界、`Runtime`）。

---

## 5. 非目标

- 不写 **`scenarioId` DAG / `orchestrationVersion`**语义 → [**`runtime-freeze.md`**](../agent-orchestration/runtime-freeze.md)。  
- 不写 **`executionId`、`invocationState` 字段 SSOT** → [**`observability/overview.md`**](../../../observability/overview.md)。

---

**文档版本**：1.2.3 · **维护**：产品 + Runtime owner · **本版**：§3 Pause **话术** **去「主站开通子账户」** **误导**（承 **1.2.2**）。
