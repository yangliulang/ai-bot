# 用户开通与绑定（Onboarding）— 总览

**路径**：`specs/requirements/domains/agent/onboarding/`。

**职责**：产品在 **Agent 就绪前置链**（身份与实例载体、**产品线绑定页** API 校验与托管绑定、Telegram 与会话绑定、授权与最小权限模板、运行时就位、激活与准入叠加）上的可对签下限；**不写** OpenAPI 字段全集、**不替代** [`../exchange-agent/overview.md`](../exchange-agent/overview.md) **Capability 五域正文**、**不替代** [`../../../Runtime/overview.md`](../../../Runtime/overview.md) **所载** **`execution`/队列 · Planner** 实现稿（[`README` 入口](../../../Runtime/README.md)）。

**步骤级编排**：[`../../../flows/activate-trading-agent.md`](../../../flows/activate-trading-agent.md)。**单轮执行前门禁**：[`../../../flows/consume-and-bill.md`](../../../flows/consume-and-bill.md) **S2**。

---

## 1. 文档结构（入口地图）

| 文件 | 内容 |
|------|------|
| [`overview.md`](overview.md)（本文） | **FR-ON\***、**SC-ON\***、术语、**§1.3** 摘要字段对齐、**§1.1** |
| [`initialization-flow.md`](initialization-flow.md) | 分阶段、异常、幂等、审计；**§7** **`ON-GWT-*`**；**同窗** **`TG-GWT-03`**（[`telegram-binding` §6.3](telegram-binding.md)）；**§2、§7** 与 **`ON-PERM`/`runtime-provisioning`** 交界 |
| [`telegram-binding.md`](telegram-binding.md) | **§3** FR-T05 多因子归因与 Deeplink；**§6** **`TG-GWT-01～03`**（ **`ON-PERM-03`** 频道同窗） |
| [`activation-policy.md`](activation-policy.md) | 因子优先级；**§5** **`agentState`** 归因 |
| [`agent-account.md`](agent-account.md) | 专用子账户载体；与 **§1.3** 摘要同窗 |
| [`permission-authorization.md`](permission-authorization.md) | API 授权与模板；**§3** 凭据生命周期；**§5～6** 轮换/吊销与 **`ON-PERM-*`** GWT |
| [`runtime-provisioning.md`](runtime-provisioning.md) | **M-A/B/C** 与可接单；**§3** **`agentState`/Pause** 话术与 onboarding 分界；冷启动 |
| [`boundaries.md`](boundaries.md) | 与 **exchange-agent** **MR 归属**、域分界 |

---

## 1.1 Agent 产品线绑定页（摘要）

**会话入口**：用户在 **Telegram** 首触时，须校验 **该 Telegram 会话锚点**是否已映射至 **至少一个可用的 Agent 实例**（[`telegram-binding.md`](telegram-binding.md)）；**若否** → 下发 **产品线 Deeplink**（指向 **Agent 项目绑定页**，**非**交易所主站）。

**绑定闭环**：用户打开 **产品线链接** → 进入 **Agent 绑定单页**（**不须访问 Coobit 交易所主站/H5**）→ 展示 **待绑定的 Telegram 账号**（例如 **`@username` / 脱敏 id**，与 Deeplink 签发上下文一致）与用户录入的 **`agentSubAccountUid`**、**子账户 API Key + Secret** → **保存时**服务端 **调用交易所开放 API** 校验凭据（**PATH / 次序 / `TradingApiBindRejectCode` 映射** **同窗** [**`design/api.md`**](../../../../design/api.md) **「用户侧 Agent 开通 / 绑定 API」** **与** **「绑定保存 · 交易所探测矩阵」**，摘要字段 [**§1.3**](overview.md) **同窗同文**）→ **仅在校验成功后** **创建 Agent 实例**（若尚无）、**托管凭据**并完成 **Telegram ↔ 可归因主体/实例** 映射。**对上 Coobit 私网出站**：**服务端**探测默认经 **`openapi-ai`/Skill（须 pin）**；**能力与 PATH** **仍以 **`design/api` **矩阵与 **`agent-coobit-api-allowlist`** **为 SSOT** — [**`integrations/exchange/overview.md`**](../../../integrations/exchange/overview.md)。**绑定单页不承载**多步开户向导；**Agent 专用子账户「就绪」**口径仍同窗 [`billing` §2](../../../domains/admin/billing-management/overview.md)、[`agent-account.md`](agent-account.md)。**分界**：**Key 绑定** **由 Agent 项目承载**；**用户账单查阅 / Token 流水** **仍为交易所内部功能**，见 [`web/agent-billing.md`](../../web/agent-billing.md)。

**展开**：[`initialization-flow.md`](initialization-flow.md)；**会话与 Deeplink**：[`telegram-binding.md`](telegram-binding.md)；**私域**：[`trade-assistance`](../exchange-agent/trade-assistance.md)、[`portfolio-insight`](../exchange-agent/portfolio-insight.md)、[`boundaries`](../exchange-agent/boundaries.md)。

---

## 1.2 术语

| 术语 | 含义 |
|------|------|
| **Agent 专用子账户** | 默认承载 Token 扣减与子账户 scope 调用的母子账子账户（[`agent-account.md`](agent-account.md)）。 |
| **子账户交易 API（本产品绑定）** | 用户在 **Agent 产品线绑定页**提交并通过校验后，由 Runtime **托管**（[`permission-authorization.md`](permission-authorization.md)）。 |
| **`userId`** | **Coobit** **母账户（主账号）UID**：交易所与所内 IAM 中的 **会员主键** 与 **账务可归因锚点**；**≠** 子账户 **`subUid`** / 绑定页 **`agentSubAccountUid`**。交易所品牌与对外所名 **Coobit**，需求与实现文档 **均勿写作** **Coolbit**。（**§1.2 成功后** **与实例映射确立**；**绑定页** **不须**用户进入交易所主站。） |
| **会话绑定** | Telegram 与 `userId`（及允许的实例上下文）映射（[`telegram-binding.md`](telegram-binding.md)）。 |

---

## 1.3 用户摘要字段（`config` §8.2 对齐）

字段名摘自 **[`management-console-v1-prd` §8.2](../../../domains/admin/management-console-v1-prd.md)**；HTTP/枚举真源 [**`design/api.md`**](../../../../design/api.md)。

| 字段 | onboarding 侧一致性要求 |
|------|-------------------------|
| **`agentSubAccountId`** | **S2** 成功后应可读；与用户触达侧「子账户就绪」一致。 |
| **`agentSubAccountStatus`**（若有） | 与 **billing「就绪」**同窗；禁止长期「Healthy」与会话 **`AGENT_SUBACCOUNT_BLOCKED`** 无理由并存。 |
| **`agentTradingApiBindingStatus`** | **S2** 成功路径须进入「已绑定本产品」语义。 |
| **`agentTradingApiKeyId`**（若有） | 仅公开 id；轮换可审计；不出现 Secret。 |
| **`agentState` / `lastProductBlockReason`** | 可由 [`activation-policy` §5](activation-policy.md) 解释；Pause / Warm-up **归因**同窗 [`activation-policy` §1](activation-policy.md)、[`runtime-provisioning` §3](runtime-provisioning.md)；**收窄权限误判**同窗 [`permission-authorization` §6.3](permission-authorization.md)；**`NORMAL`** 不得与隐性全局/运维熔断矛盾无说明。 |

---

## 2. 功能需求 · `FR-ON*`

| ID | 摘要 | 展开 |
|----|------|------|
| **FR-ON01** | **端到端绑定与会话闭环**可回放；阻断含 Deeplink（适用） | [`initialization-flow`](initialization-flow.md)、[`permission-authorization`](permission-authorization.md)、[`telegram-binding`](telegram-binding.md) |
| **FR-ON02** | 绑定可审计；Secret **不得**出现在默认观测面；**允许**用户在 **受控绑定页**短时提交 Secret **仅用于**校验与接入托管；多会话策略 | [`telegram-binding`](telegram-binding.md)、[`initialization-flow` §5](initialization-flow.md)、[`design/api`](../../../../design/api.md)、[`activate-trading-agent` S5](../../../flows/activate-trading-agent.md) |
| **FR-ON03** | 用户触达与管理台同源 | [`activation-policy`](activation-policy.md)、[`access-control`](../../../domains/admin/access-control/overview.md)、[`agent-management`](../../../domains/admin/agent-management/overview.md) |
| **FR-ON04** | 幂等、单活跃链默认 | [`initialization-flow` §4](initialization-flow.md)、[`agent-account`](agent-account.md) |
| **FR-ON05** | 摘要可 join、无 Secret | [`contract-closure`](../../../contract-closure.md)、[**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path)、[`observability`](../../../observability/overview.md) |

---

## 3. 验收 · `SC-ON*` 与 GWT 锚

| ID | 主题 | Given/When/Then |
|----|------|----------------|
| **SC-ON-01** | 主路径 | **`ON-GWT-01`**：[`initialization-flow` §7.1](initialization-flow.md) |
| **SC-ON-02** | Deeplink | **`ON-GWT-02`**：[`initialization-flow` §7.2](initialization-flow.md)，会话细节 [`telegram-binding` §6](telegram-binding.md) |
| **SC-ON-03** | I02 与摘要同源 | **`ON-GWT-03`**：[`initialization-flow` §7.3](initialization-flow.md) |
| **SC-ON-04** | Secret | **`ON-GWT-04`**：[`initialization-flow` §7.4](initialization-flow.md) |

**补充 GWT 锚（权限域）**：**`ON-PERM-01～03`** — [`permission-authorization` §6](permission-authorization.md)。

**补充 GWT 锚（频道 · 权限对齐）**：**`TG-GWT-03`** — [`telegram-binding` §6.3](telegram-binding.md)（与 **`ON-PERM-03`**、`SC-ON-03` **精神**同窗）。

## 4. 邻域关系

1. **exchange-agent**：五 pillar、**FR-T01/T02**。  
2. **`flows/`**。  
3. **`design/api`**。  
4. **`config` 附录、`agentState`、I02**：[`agent-management/functions` §7.1](../../../domains/admin/agent-management/functions.md)。  
5. **Agent 产品线绑定页触点（Web/H5 UX）**：[`web/agent-onboarding.md`](../../web/agent-onboarding.md)（**FR-WEB\***；编排真源仍本文档树）。  

[`boundaries.md`](boundaries.md) 载 **MR 归属**。

---

## 5. 入口链

- [`spec.md`](../../../spec.md)、[`product.md`](../../../product.md)、[`contract-closure.md`](../../../contract-closure.md)
- [`closure-remaining` §0 速链](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path) · [§7](../../../closure-remaining.md#cc-remaining-open-items)
- [`billing` §2](../../../domains/admin/billing-management/overview.md) · **Agent 产品线绑定页 UX** [`web/agent-onboarding.md`](../../web/agent-onboarding.md)、[`web/overview.md` §4](../../web/overview.md)（**FR-WEB→CC**）  

---

**文档版本**：1.4.4 · **维护**：产品 + Account/Runtime owner · **本版**：**§5** **入口链** **与** **`FR-ON05`** **同窗** **`closure-remaining` §0·§6**。**承** **1.4.3**。
