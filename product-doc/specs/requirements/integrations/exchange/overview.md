# Integrations · Exchange（总览）

**职责**：回答 **交易所上游（GitBook OpenAPI Doc V2）长什么样** — 能力分面、协议共性、上游语义与上游文档中的风险提示。**不**写平台运行时策略（重连、对账、轮询、`stableReason`、会话机）。

**对内 PATH/矩阵**：[`../../../design/api.md`](../../../design/api.md)。  
**平台如何应对上游**：[`../../Runtime/overview.md`](../../Runtime/overview.md) · [`error-normalization.md`](../../Runtime/error-normalization.md) · [`unknown-state.md`](../../Runtime/unknown-state.md) · [`reconciliation.md`](../../Runtime/reconciliation.md) · [`recovery.md`](../../Runtime/recovery.md)。  
**业务门禁与工具**：[`../../domains/agent/exchange-agent/overview.md`](../../domains/agent/exchange-agent/overview.md)。

**端到端鸟瞰 · 架构语言（交易所出站所处系统位置）**：[`flow/e2e-closed-loop.md`](../../../../flow/e2e-closed-loop.md) **文首「架构语言」** → [`architecture` §「与通用 Agent 栈之对照」](../../../design/architecture.md)。

**分卷**：[`spot-api.md`](spot-api.md)、[`futures-api.md`](futures-api.md)、[`margin-api.md`](margin-api.md)、[`convert-api.md`](convert-api.md)、[`wealth-api.md`](wealth-api.md)、[`websocket-api.md`](websocket-api.md)、[`account-and-balance.md`](account-and-balance.md)、[`order-lifecycle.md`](order-lifecycle.md)、[`error-codes.md`](error-codes.md)。  
**Agent 首版 · 仅现有 PATH 调用白名单**（实现对照）：[`agent-coobit-api-allowlist.md`](agent-coobit-api-allowlist.md)。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../contract-closure.md)。

## Coobit · 官方 openapi-ai（Skill）采纳（对上 HTTP 的实现宿主）

**定位**：ChainUp **所内 ARCH `openapi-ai` 仓库**（及 **与 GitBook OpenAPI Doc V2 同窗** **发布** **之 `skills/*/SKILL.md`、CLI、可选 MCP **等**「官方包」**）为 **对上 Coobit 的优选实现宿主**。**不**改写 **能力面 SSOT**：**GitBook / 下文外链**、`specs/openapi/exchange/coobit-*.yaml`、`design/api.md` **endpoint 矩阵**、[`agent-coobit-api-allowlist.md`](agent-coobit-api-allowlist.md) **白名单**。

| 条目 | 说明 |
|------|------|
| **契约真源** | **PATH · 鉴权语义 · `code`/HTTP · 限速** — **仍以** GitBook、`integrations/exchange/*` **分卷**与 **`design/api.md`** **矩阵同窗**为准；官方 Skill **仅为实现载体**，**不**构成第二契约 SSOT。 |
| **路径与版本** | 官方包 **须** **pin** **tag/commit/冻结分支** **与 MR 登记** **同窗** **`contract-closure` / Owner** — **禁止** 「漂在 HEAD」进入生产归因。 |
| **白名单等价** | 经由官方包发出 **私有所内 HTTP** **仍须** **仅** **映射至** **`agent-coobit-api-allowlist`** **已载 PATH（及矩阵已冻结方法）**；**禁止**借 Skill **扩大** 子账户网关调用面。**若**需 **网关代理/出站过滤** **`design`/ADR** **登记**。 |
| **平台不重复** | **不得在**本产品仓库 **并行维护** **与官方 `openapi-ai` 同源重复的** 「逐 PATH 自编工具规格 / OpenAPI 薄封装叙事」 **作为** **`skillId`/`toolId`** **的第二 SSOT**；**登记键** **`trade-assistance` §4·§8** **与** **`registry`** **仍为** **`FR-TS07`/ADR-002**。 |
| **不变项** | **类型 A、`FR-T0x`、`executionId`、`internal/billing`、504/UNKNOWN、对账、观测 —** **仍属** **`domains/agent/*`、`Runtime/*`**；**计费** **不经** Skill **另设收费**。 |
| **ADR-004 · Adapter 语义** | **官方 `openapi-ai` 包**（含 `skills/*/SKILL.md`）**为 Coobit Execution Adapter 之可选实现宿主**；**统一交易语义与 P0 领域对象** **见** [`canonical-trading-model.md`](../../../design/canonical-trading-model.md)、[`ADR-004`](../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../../domains/agent/exchange-agent/trade-assistance.md)；**契约 CC-P1-07** [`contract-closure`](../../contract-closure.md#cc-p1-07)；**人类评审** [`requirements-review` §7.5](../../../../product/requirements-review.md#cc-adr004-review-checklist)。**跨所领域真源** **不得** **落在** **所名 Skill 分包** **内**。 |

**非目标**：本分卷 **不**承载 **openapi-ai** **构建/发布流水线**、`node`/TS **版本矩阵** — **归** **`design/architecture`、`design/deployment`** **或实现仓库**。

---

## 交易所对外文档（GitBook）

| 主题 | 链接 |
|------|------|
| 通用（HTTPS、`Content-Type`、签名头、鉴权类型、限频与 HTTP 语义） | [OpenApi 基本信息](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2?fallback=true) |
| ENUM | [ENUM](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/enum) |
| 币币 REST | [币币交易](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/bi-bi-jiao-yi) |
| 杠杆 REST | [杠杆交易](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/gang-gan-jiao-yi) |
| 合约 REST | [合约交易](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/he-yue-jiao-yi) |
| 子账户 | [子账户](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/zi-zhang-hu) |
| 万向划转 | [万向划转](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/qian-bao) |
| WS 现货用户数据 | [资产变动与订单更新](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/websocket-tui-song-zi-chan-bian-dong-yu-ding-dan-geng-xin) |
| WS 合约订单仓位 | [合约订单仓位](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/websocket-tui-song-he-yue-ding-dan-cang-wei) |
| 业务错误码表 | [错误码](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/cuo-wu-ma) |

---

## 非目标（本分卷）

- 运行时 UNKNOWN/504 的用户叙事与补偿 — **`Runtime/unknown-state.md`**、**`recovery.md`**  
- REST↔WS **真相源次序**与平台对账 — **`Runtime/reconciliation.md`**  
- 上游 `code` → 平台稳定归因码 — **`Runtime/error-normalization.md`**  
- 具体 FR/SC、Telegram 确认流 — **`domains/agent/*`**、**`flows/`**
