# ADR-003：C 类外网 / 分析工具（`tool.web.*`）合规与预算

| 字段 | 内容 |
|------|------|
| **状态** | 已接受（**文档草案**） |
| **日期** | 2026-05-07 |
| **决策 owner** | 产品 + 合规接口人（所内）+ Agent Runtime owner |

## 上下文

[`trade-assistance.md`](../../requirements/domains/agent/exchange-agent/trade-assistance.md) §8.4 列出 **`tool.web.social_sentiment`** 等 **C 类** 能力；[`contract-closure.md`](../../requirements/contract-closure.md) **CC-P1-02** 要求 **ADR** 与 **`agent-context`** **预算** **对签**。

## 决策

1. **调用前置**：任 **`tool.web.*`** **须在** **本次 `executionId`** **声明的预期工具集合** 内（**Tool Profile / T05**）；**未声明** **不得** **隐式** **升格** **为外网调用**。
2. **子源与速率**：**每工具** **须** 在 **运营配置或登记表** 中 **登记** **允许域名 / API 供应方**、**默认 QPS / 日预算**；**超限** → **FAILED** **可恢复码** + **observability** **归因**（**不** **静默丢弃** **用户问题** **除非** **产品明示降级**）。
3. **PII / 脱敏**：**默认** **不向**第三方 **外传** **用户标识**（**tg user id、子账户号** **等**）；**须外传** **时** **走** **所内** **令牌化或最小字段** **策略** — **细则** **与法务** **对签** **后** **写入** **`design/api` 通用契约** **或** **域内 rules**。
4. **Disclaimer**：**模型/第三方摘要** **须** **可视来源与 `asOf`**（[`market-intelligence`](../../requirements/domains/agent/exchange-agent/market-intelligence.md)、[`read-analyze-and-search-via-agent`](../../requirements/flows/read-analyze-and-search-via-agent.md) **同窗**）。
5. **`agent-context` 预算**：**token / 工具调用次数** **下限** **见** [`agent-context/overview.md`](../../requirements/domains/agent/agent-context/overview.md)；**C 类** **默认** **计入** **「外网步」** **预算池** — **超池** → **拒答或降级路径** **与** **FR-T05** **一致**。**同一 `executionId` 之「整条执行」工具/编排步硬顶** **见** [`execution-lifecycle.md`](../../requirements/domains/agent/agent-orchestration/execution-lifecycle.md) **§4 `FR-AO06`**（**与** **本分项池** **可同时生效**）。
6. **登记与启用态（选用规则）**：**C 类** **`tool.web.*`** **仅当** **运营工具登记表中存在对应 `toolId` 且** **启用态（同窗 `ToolRegistryEntry.enabledOperational` 或实现对等字段）为真** **时** **可被路由选中**；**未登记或停用** **则** **不得调用**（**与** **本条 (1) T05 声明** **叠加**）。**将生产环境中的 C 类条目从停用改为启用** **仍属** **写操作** **—** **须** **满足** **`contract-closure` CC-P1-02** **与** **OpenAPI** **`legalReviewTicketId`** **等下限**（**或** **§8** **登记之合规豁免**），**与** **「仅启用可选」** **不矛盾**：**停用** **时** **无需** **校验工单号**。

## 后果

- **CC-P1-02**：**文档侧** **已具备** **可评审 ADR**（**含** **运行时选用 vs 生产 Enable 写闸** **分层**）；**OpenAPI** **字段级 rate-limit / allowlist** **仍须** **矩阵 MR** **冻结**。
- **观测**：**`agent.tool.call`** **须** **可区分** **`toolId`** **与** **外网** **latency bucket** — [`observability/overview.md`](../../requirements/observability/overview.md) **§2.1**。

## 引用

- [`trade-assistance.md`](../../requirements/domains/agent/exchange-agent/trade-assistance.md) §8.4
- [`contract-closure.md`](../../requirements/contract-closure.md) **CC-P1-02**
- [`closure-remaining` §0](../../requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../requirements/closure-remaining.md#cc-exec-solve-path)（**关单余量 / MR 首节**）
- [`read-analyze-and-search-via-agent.md`](../../requirements/flows/read-analyze-and-search-via-agent.md)
