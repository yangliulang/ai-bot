# 部署与运行时拓扑（逻辑视图）

本文描述 **环境、发布原则与逻辑拓扑**，便于回答「系统在各环境如何跑起来、谁依赖谁」。**云厂商、集群规格、副本数、网络 CIDR** 等 **实现真源**须与 **运维 / Infra** 对签后写入 **所内 Wiki 或 IaC 仓库**，并在此 **以链接回填**（本文件 **不**虚构基础设施细节）。

**配套阅读**：逻辑协作与数据流见 [`architecture.md`](architecture.md)；HTTP 与登记表见 [`api.md`](api.md)；运行时横切需求见 [`requirements/Runtime/overview.md`](../requirements/Runtime/overview.md)。

**关单余量（MR 首节）**：[`closure-remaining` §0](../requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../requirements/closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../requirements/closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../requirements/contract-closure.md)。

---

## 1. 环境分层（典型）

| 环境 | 用途（下限） | 与规格的交叉 |
|------|----------------|--------------|
| **开发 / 联调** | 开发者本机或共享 Dev；可接沙箱所或 Mock | [`api.md`](api.md) 矩阵可为 Mock；**不得**用 Mock **冒充**已对签生产矩阵 |
| **预发 / Stage** | 与生产同构 **逻辑依赖**（真 Telegram、真所沙箱或隔离集群按所内规范） | **契约解冻**以 [`contract-closure.md`](../requirements/contract-closure.md) 为准 |
| **生产** | 服务真实用户；**配置与密钥**按 **`secretRef`** / 运维规范注入 | Kill / Freeze / D-1 行为必须与 [`architecture.md`](architecture.md) **在途与紧急停止**、[`config.md`](../requirements/domains/admin/management-console-v1-prd.md) §11 **一致** |

**租户与隔离**：多租户隔离下限见 [`Runtime/locking.md`](../requirements/Runtime/locking.md)；实例级 Pause/Stop 归因见 [`onboarding/runtime-provisioning.md`](../requirements/domains/agent/onboarding/runtime-provisioning.md)。

---

## 2. 逻辑部署单元（可映射到多条服务）

以下 **不**绑定具体微服务名或进程名，仅表达 **部署边界**：

| 单元 | 运行时起到的角色 | 关键外部依赖 |
|------|------------------|--------------|
| **渠道入口** | 接收 **Telegram Webhook**（或长轮询，按所内选型）；**Update** 路由到 Agent 平面 | Telegram Bot API；[`telegram/admin-bot-config.md`](../requirements/domains/agent/telegram/admin-bot-config.md)、[`trading-agent-config/keys.md`](../requirements/domains/admin/trading-agent-config/keys.md) §4 |
| **Agent 运行平面** | 编排、LLM 调用、工具执行、**`executionId`** 生命周期、会话状态 | LLM 提供商（[`integrations/llm/`](../requirements/integrations/llm/provider-routing.md)）；[`exchange-agent`](../requirements/domains/agent/exchange-agent/overview.md) 门禁 |
| **交易所出站** | 持有 **子账户 scope** 凭据，调用 **Coobit OpenAPI**；**出站实现默认** **`openapi-ai` 官方包**（CLI/Skill/MCP 等，**与** [`integrations/exchange/overview.md`](../requirements/integrations/exchange/overview.md) **同窗 pin**）；承载 504/UNKNOWN 归一与对账 **客户端逻辑** | Coobit 网关；[`api.md`](api.md) · [`agent-coobit-api-allowlist.md`](../requirements/integrations/exchange/agent-coobit-api-allowlist.md) |
| **计费出站** | 在 **可计费执行终局** 调用 **账务 / Token** API（子账户 · 币币 USDT） | Coobit 账务；[`billing.md`](../requirements/domains/admin/billing-management/overview.md) |
| **管理 / 运营 API** | 控制台写入 **`configVersion`**、审计、`setWebhook` 等运维动作 | 所内 IAM/RBAC；[`management-console-v1-prd.md`](../requirements/domains/admin/management-console-v1-prd.md) |
| **观测管线** | 采集、索引、追溯 **§2** 约定事件 | 所内日志/Tracing/指标后端；[`observability/overview.md`](../requirements/observability/overview.md) |

---

## 3. 配置、密钥与「如何生效」

- **全局与产品线闸**：`GLOBAL_AGENT_SWITCH`、`FEATURE_*`、**`OPS_GLOBAL_AGENT_PAUSE`** 等键真源见 [`trading-agent-config/keys.md`](../requirements/domains/admin/trading-agent-config/keys.md)；运行时必须读到 **与控制台一致**的有效快照（**`configVersion`**），见 [`trading-agent-config/flow.md`](../requirements/domains/admin/trading-agent-config/flow.md)。
- **Bot Token / Webhook**：仅存 **`secretRef`**，**明文 Secret 不进运营 UI**；运维 API 见 [`api.md`](api.md) 登记表「Telegram Bot / Webhook」。
- **子账户 API Key**：**仅能**在所内允许的面上使用；轮换与吊销 **[§6](#6-待-infra--运维回填建议在实现仓库或-wiki-维护)**。**`openapi-ai` 宿主**：**运行时** **须** **载入 pin 版本** **之**官方包镜像/制品（tag/commit **`design`/`contract-closure` 同窗**）；**密钥**仍由 Agent/网关进程注入 — **不写** Skill 静态资产。
- **Prompt / 工具版本**：与 **后台治理** 生效路径见 [`prompt-management/overview.md`](../requirements/domains/admin/prompt-management/overview.md)；避免「已部署代码但运营未发布提示版本」类漂移须在 **发布清单** 中显式勾选。

---

## 4. 发布、回滚与兼容

- **API 契约**：任何对外 PATH/字段变更 **须**同步 [`api.md`](api.md) 或解冻 [`contract-closure.md`](../requirements/contract-closure.md)（**禁止**只部署不改表）。
- **配置回滚**：乐观锁冲突与审计见 [`trading-agent-config/flow.md`](../requirements/domains/admin/trading-agent-config/flow.md)；**Kill > Freeze** 语义见 [`exchange-agent`](../requirements/domains/agent/exchange-agent/overview.md) 与 Runtime **freeze-policy**。
- **在途（D-1）**：发布或关闸 **不得** 假定 **在途执行瞬间全部消失** — 行为以 [`architecture.md`](architecture.md) 专节为准。

---

## 5. 健康与运维（下限叙事）

**产品规格层**须保证（具体探针由 Infra 定稿）：

- **渠道入口**：Webhook 可达、`getWebhookInfo` 与登记 **意图一致**（[`FR-MC711`](../requirements/domains/admin/trading-agent-config/functions.md) 同窗）。
- **Agent 平面**：能对 **Kill/Pause** 作 **新写拒绝**；**UNKNOWN** 对账路径可观测（[`observability` §2](../requirements/observability/overview.md)）。
- **503/504 级联**：须在 **运维 Runbook** 中定义与用户触达 **中性话术** 的协调（话术语义见 [`Runtime/unknown-state.md`](../requirements/Runtime/unknown-state.md)、[`exchange-agent` FR-T05](../requirements/domains/agent/exchange-agent/overview.md)）。

---

## 6. 待 Infra / 运维回填（建议在实现仓库或 Wiki 维护）

以下 **本条目不定义取值**，仅列 **应对签主题**：

- 实例拓扑图（AZ、LB、有状态组件若存在）
- CI/CD 流水线、蓝绿/金丝雀策略与 **配置预热**
- Secret 轮换、**子账户 API Key** 吊销与 Agent 侧重绑流程
- RPO/RTO 与备份（数值若出现须与 [`observability` / 运维协定](../requirements/domains/admin/trading-agent-config/rules.md) 一致）
- **DR**：交易所与 Bot 双活/降级策略（若适用）
- **`openapi-ai` 制品**：官方包 **镜像 / npm / git tag** **拉取路径**、**运行时版本号** **与** **发布清单** **勾选**（**同窗** [`integrations/exchange/overview.md`](../requirements/integrations/exchange/overview.md)）

**Infra 真源链接（回填）**：`_TBD_`

---

**文档版本**：1.0.2 · **维护**：系统架构 + SRE/Infra owner · **本版**：**篇首补** **`closure-remaining` §0·§6/§6.4。** **承** **1.0.1**
