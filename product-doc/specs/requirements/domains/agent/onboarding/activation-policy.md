# 激活策略（门禁叠加）

本卷约定：**在完成子账户/API/会话绑定（onboarding）之后**，仍可能阻断 Agent **使用或计费**的外层因子，以及其与 **摘要、`agentState`、I02** 的一致性要求。**账务 JSON、费率、最小扣费**宿主 [**`billing-management`**](../../../domains/admin/billing-management/overview.md)；VIP 阈值真源宿主 [**`trading-agent-config/keys`**](../../../domains/admin/trading-agent-config/keys.md)；**VIP 比对口径**（母账号 `vipTier`）宿主 [**`access-control/eligibility-runtime`**](../../../domains/admin/access-control/eligibility-runtime.md) **§1**。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 因子族与叙事顺序（产品级）

以下顺序 **仅用于「用户归因优先级」**：当 **多因子同时失败**时，**优先展示**更小序号的一类（实现可等价映射到 **`lastProductBlockReason`/摘要**宿主字段，同窗 **附录 A、`design`**）。

| 优先级 | 因子族 | 典型来源 |
|:------:|--------|----------|
| 1 | **全局产品与渠道**：`GLOBAL_AGENT_SWITCH`、`FEATURE_AGENT_*`、`CHANNEL_TELEGRAM` | [`management-console-v1-prd` 附录](../../../domains/admin/management-console-v1-prd.md)、**`exchange-agent` boundaries** |
| 2 | **运营级 Pause / 熔断**：全站或分批 | [**`agent-management` rules**](../../../domains/admin/agent-management/rules.md)、**Runtime** |
| 3 | **Onboarding**：子账户、Agent API、会话绑定 | 本目录 + [`activate-trading-agent`](../../../flows/activate-trading-agent.md)，码族示例 **`AGENT_SUBACCOUNT_BLOCKED`、`AGENT_TRADING_API_REQUIRED`** |
| 4 | **准入**：VIP、灰白名单、封禁 | [**`access-control`**](../../../domains/admin/access-control/overview.md)、**`AGENT_*` 枚举**与 I02、`agentState` |
| 5 | **计费**：子账户 USDT、`BILLING_BLOCKED` | **billing**、[`consume-and-bill` **S2**](../../../flows/consume-and-bill.md) |

**归因诚实性**：**仅缺 USDT / VIP / 合规**时，会话 **不得**用「API 失灵」话术掩盖；同理，**缺 onboarding**时 **不得**仅提示「充值」。

---

## 2. 与 `activate-trading-agent` 的补充说明

| 步骤 | 本条强调 |
|------|----------|
| **S3** | USDT **就绪**独立于 **开通**叙事；未完成 **§1.2** **时**不可用「充值修好一切」话术。 |
| **S4** | **母账号** VIP **不足**（**`vipTier` < `AGENT_MIN_VIP_TIER`**）：须可走 **会员升级 Deeplink**，与 **`MEMBERSHIP_BLOCKED`**同窗。 |
| **S5** | **须**同窗 **`telegram-binding`** 与 **因子 1 渠道开关**。 |

---

## 3. I02（后台创建实例）与侧边一致

- **I02 第二道**失败 **`code`** 须可被用户侧 **同一事实**映射（宿主 [**`functions` §2.2、§7.1**](../../../domains/admin/agent-management/functions.md)）。  
- **禁止**：控制台已成功 **派发实例**，会话侧却无理由长期 **`AGENT_SUBACCOUNT_BLOCKED`**（同窗 **SC-ON-03、contract-closure**）。

---

## 5. `agentState` 与 onboarding 归因（`config` §9 对齐）

以下为 **[`management-console-v1-prd` §9](../../../domains/admin/management-console-v1-prd.md)** 枚举 **叙述级**解读；**语义终裁**同窗 **exchange-agent**、**flows**。

| **`agentState`** | **狭义 onboarding**（本子账户 / Agent API / Telegram 绑定缺口）为主因？ | 用户侧叙事提示 |
|------------------|------------------------------------------------------------------------|----------------|
| **`NORMAL`** | 否 | 可进入 **FR-T02** 后继判定 |
| **`GLOBAL_OFF`** | 否 | 全局产品关 |
| **`OPS_SUSPENDED`** | 否 | 运维/熔断 |
| **`MEMBERSHIP_BLOCKED`** | 否（准入 / VIP） | 升级会员 Deeplink |
| **`AGENT_SUBACCOUNT_BLOCKED`** | **是** | **Agent 产品线绑定页** §1.2、**产品线 Deeplink**（**不须**把用户叙事收窄为「必须登录交易所主站」） |
| **`BILLING_BLOCKED`** | 否（计费 / 余额） | Billing / 充值划转 |

**组合失败**：须按 **§1** 优先级 **`lastProductBlockReason`** 择一主因展示，**禁止**用 **`AGENT_SUBACCOUNT_BLOCKED`** 掩盖计费或 VIP **事实**。

---

## 6. 非目标

- 不复制 **FR-MC601～607**条文 — [**`access-control/functions`**](../../../domains/admin/access-control/functions.md)。  
- 不冻结 **`me/billing`** 响应字段表 — **`design/api`**。

---

**文档版本**：1.2.2 · **维护**：产品 · **本版**：§5 **`AGENT_SUBACCOUNT_BLOCKED`** 叙事 **对齐 Agent 绑定页**（承 **1.2.1**）。
