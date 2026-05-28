# Integrations（外部系统拆分）

**本目录职责（仅此四层）**：（1）**外部系统提供的能力**；（2）**外部协议与格式约束**；（3）**上游文档中的语义**（含上游声明的 HTTP/`code` 含义）；（4）**上游强加的风险提示**（如限频封禁语义）。

**不负责**：运行时重试/退避策略、会话状态机、编排确认流、产品门禁、UX 文案、观测字段 **`stableReason`** 的全平台定义、WS 断线后的平台对账策略 — 见 **[`Runtime/`](../Runtime/overview.md)**（尤其 **`error-normalization`**、**`unknown-state`**、**`reconciliation`**、**`recovery`**）及 **`domains/agent/*`**。

**PATH/字段 SSOT**：[`../../design/api.md`](../../design/api.md)。

**端到端鸟瞰 · 架构语言**：[`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md) **文首「架构语言」** → [`architecture` §「与通用 Agent 栈之对照」](../../design/architecture.md)。

**契约收口 / 未关闭项 MR 路径**：[`contract-closure.md`](../contract-closure.md) **§2～§3**；**[`closure-remaining`](../closure-remaining.md)** · **[§0 速链](../closure-remaining.md#closure-remaining-quicklinks)** · **[§6～§6.4](../closure-remaining.md#cc-exec-solve-path)** · **[首节表 §6.4](../closure-remaining.md#cc-problem-to-action)** · **[§7.5](../closure-remaining.md#cc-remaining-open-close-path)** / **[§7.6](../closure-remaining.md#cc-closure-exec-checklist)**。

| 子目录 | 说明 |
|--------|------|
| **[`exchange/`](exchange/overview.md)** | 交易所 OpenAPI/WS **上游契约摘要** + GitBook 索引；**对上 Coobit 私网 HTTP** **出站默认** **`openapi-ai` 官方包**（Skill/CLI/MCP，**须 pin**），**契约** **仍以** **`design/api`/`allowlist`/GitBook** **为准**（见 **`exchange/overview`** **同窗节**）；**同窗** **`e2e`→[`architecture` §对照](../../design/architecture.md)** |
| **[`telegram/`](telegram/bot-api.md)** | Telegram Bot API **上游契约摘要**；**会话 · 类型 A / Bot API** **叙事真源** **[`domains/agent/telegram/overview.md`](../domains/agent/telegram/overview.md)（§2.5 · 类型 A；总则 §2～§2.6）** |
| **[`llm/`](llm/provider-routing.md)** | LLM 供应商侧协议与路由边界摘要（配置 SSOT：`domains/admin/ai-settings/`） |
| **[`notifications/`](notifications/push-delivery.md)** | 推送通道 **上游语义**（投递策略见 **`Runtime`** / 实现） |

## 与邻域分工

| 层级 | 写什么 |
|------|--------|
| **`integrations/*`** | **外部系统是什么**：鉴权类型、参数位置、限频 **文档语义**、错误载荷形状、WS 帧格式（按上游文档） |
| **`design/api.md`** | 对内登记表：PATH、模型、模块归属 |
| **`design/architecture.md`**、**`design/deployment.md`** | **系统如何协作与如何在各环境运行**（逻辑 C4、数据流、部署单元）；**不**替代 `integrations` 上游协议摘要 |
| **`Runtime/`** | **平台如何应对**：UNKNOWN、归一化错误码、对账、recovery |
| **`domains/agent/*`** | 业务 FR/SC、用户可见行为、工具门禁 |

## 维护约定

- **GitBook**：交易所外链集中在 [`exchange/overview.md`](exchange/overview.md)。
- **Telegram / LLM**：官方文档入口写在各篇正文（Bot API Core、各供应商 OpenAPI）；**禁止**在 `integrations` 展开退避 / 幂等队列 / `stableReason` 规则。
- **推送**：APNs/FCM **语法与载荷**见厂商文档；队列与重试 **见 [`Runtime/recovery.md`](../Runtime/recovery.md)**。
- **禁止 Runtime 泄漏**：若在 `integrations` 中发现「须退避 / 须轮询 / 会话状态机 / stableReason 映射规则」等，应 **迁至 `Runtime/`** 或 **域**，**integrations 仅保留「见某某」**。
