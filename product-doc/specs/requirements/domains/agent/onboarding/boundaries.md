# Onboarding · 边界与分工

本卷说明 **`onboarding/`** 写什么、不写什么，以及与其它域的裁决顺序。**合规稳定码、可读恢复 Deeplink**（**Key/onboarding** → **Agent 产品线绑定页**；**Billing/理财等** → **交易所站内**，同窗 **`exchange-agent/boundaries`**）宿主 [**`exchange-agent/boundaries`**](../exchange-agent/boundaries.md)（与本目录 **不同层级**）。

---

## 1. 邻域分工表

| 邻域 | 宿主负责 | onboarding 不写 |
|------|-----------|----------------|
| [**`exchange-agent`**](../exchange-agent/overview.md) | **FR-T01/T02** 与五 pillar 能力语义、工具门禁 | Capability 全量与技能登记表 |
| [**`agent-management`**](../../../domains/admin/agent-management/overview.md) | 模板/实例、`agentState`、I02、Runtime IA | Prompt/Tool Profile 正文 |
| [**`billing-management`**](../../../domains/admin/billing-management/overview.md) | **商业层 + 轨 B 权益核销**（订阅/Capability/包、`me/commerce`）、**子账户 USDT 用于交易** | 分录细则 — **SSOT** [`commerce-model`](../../../domains/admin/billing-management/commerce-model.md) |
| [**`access-control`**](../../../domains/admin/access-control/overview.md) | 灰白名单、封禁、`AGENT_*`、`AGENT_MIN_VIP_TIER` | KYC 裁决写 SSOT（合规主系统） |
| [**`Runtime`**](../../../Runtime/overview.md) | 队列、Planner、重试/降级（[**`execution.md`**](../../../Runtime/execution.md)、[**`recovery.md`**](../../../Runtime/recovery.md) 等；**§1 目录**） | Planner/DAG **实现**拓扑全文 |
| [**`design/api`**](../../../../design/api.md) | PATH、OpenAPI、`TBD` 收口 | — |
| [**`flows`**](../../../flows/README.md) | **S{n}** 业务流程步骤 | — |

---

## 2. MR 归属判定（评审快捷表）

| 你在改的主题 | **优先落在 onboarding 的文件** |
|--------------|----------------------------------|
| **Agent 产品线绑定页**开通步骤、编排幂等、就绪判据 | [`initialization-flow.md`](initialization-flow.md)、[`overview.md`](overview.md) §1.1 |
| Telegram 与 **`userId` 绑定/OAuth**、多端与踢下线 | [`telegram-binding.md`](telegram-binding.md) |
| Agent API **默认读写范围**删减 | [`permission-authorization.md`](permission-authorization.md) + **`trade-assistance` §8** / 矩阵宿主 |
| 实例首次可接单与 Warm-up 体验 | [`runtime-provisioning.md`](runtime-provisioning.md) + **`Runtime`** |
| VIP vs 计费 vs onboarding **归因顺序**文案 | [`activation-policy.md`](activation-policy.md)、[`consume-and-bill`](../../../flows/consume-and-bill.md) S2 |

---

## 3. 会签提示

| **变更类型** | **同窗** |
|--------------|----------|
| **Agent 产品线 `me/agent/*` 绑定 · 状态 PATH**（**Billing 仍在交易所站内**） | **`design/api`**、[ **`contract-closure`**](../../../contract-closure.md)；[**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path) |
| Telegram Deeplink、**FR-T05**下限 | Telegram 渠道文、**`exchange-agent/boundaries`** |
| 子账户 / Agent API 就绪定义 | **`billing` §2**、**`product.md`** |

---

**文档版本**：1.2.3 · **维护**：产品 · **本版**：**§3 会签提示** **补** **`closure-remaining` §0·§6**。**承** **1.2.2**。
