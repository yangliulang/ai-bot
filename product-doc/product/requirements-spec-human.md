# 产品需求说明书（人话导读）

**用途**：给 **产品 / 设计 / 管理层 / 评审** 一篇 **按「须 / 不得 / 边界」组织的可读需求**，弥补 **`flows` / `overview` 偏故事线**、**`domains/` 偏编号** 之间的空隙。  
**非第二套 SSOT**：**不**新增 FR/SC；**编号、矩阵 PATH、`skillId`、验收 ID** 仍以 **`specs/requirements/`**、**`specs/design/`** 为准。叙事与 **`specs`** 冲突时：**以 `specs` 正文为准**，并回写 `product/`。

**权威裁断**：方向与范围表 → [`specs/requirements/product.md`](../specs/requirements/product.md)。  
**关单与升格**：[`specs/requirements/contract-closure.md`](../specs/requirements/contract-closure.md) · [`closure-remaining.md`](../specs/requirements/closure-remaining.md)（**[§7 一页总表](../specs/requirements/closure-remaining.md#cc-remaining-open-items)** · **[§7.5 闭环路径](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 执行清单](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)**）。  
**小团队日常**：[`specs/requirements/LITE-MODE.md`](../specs/requirements/LITE-MODE.md) · [发版半页纸](./release-notes.md)。

---

## 1. 产品边界（当前版本）

| 须成立 | 条文入口 |
|--------|----------|
| **仅 Coobit 单所**；**不按多租户商户 SaaS** 交付 | [`product.md`](../specs/requirements/product.md) **方向** |
| 对客会话渠道 **仅 Telegram**（类型 A 确认闸门）；**不含 App**（暂缓口径不变） | [`telegram/overview.md`](../specs/requirements/domains/agent/telegram/overview.md) **§2.5 · 类型 A、§2～§2.6** |
| **非目标**（跨所、商户 SaaS 等）**不得** silent 扩张进 PRD 承诺 | [`product.md`](../specs/requirements/product.md) **非目标** |

---

## 2. 开通与账户

| 须 / 不得 | 条文入口 |
|-----------|----------|
| 用户使用交易相关能力前，须具备 **Agent 专用子账户** 与 **子账户交易 API（Agent 绑定）**；**Telegram 首触**若无实例绑定 → **产品线 Deeplink**；用户在 **Agent 产品线绑定页** 提交 **`agentSubAccountUid`**、Key/Secret 并 **保存** **`POST .../bindings/trading-api`**（**不须访问交易所主站**），**§1.2 下限须全部通过**（含 **UID≡`subUid`**；[**FR-WEB06**](../specs/requirements/domains/web/agent-onboarding.md)、[**TradingApiBindRejectCode**](../specs/openapi/components/onboarding-schemas.yaml)）**后方** **实例化与绑定**；**默认观测面不得出现 Secret**（与 **FR-ON02 / SC-ON-04** 同窗） | [`onboarding/overview.md`](../specs/requirements/domains/agent/onboarding/overview.md)、[`exchange-agent/overview.md`](../specs/requirements/domains/agent/exchange-agent/overview.md) **FR-T01/T02** |
| **Telegram 首触（实例门禁）** 与 **Agent 绑定页（明示保存 + §1.2 下限校验）** **顺序** **典型**为 **先会话 Deeplink → 后绑定页**；**不得**仅用会话 **替代** **§1.2** **保存校验与绑定** | [`initialization-flow.md`](../specs/requirements/domains/agent/onboarding/initialization-flow.md) **§1.2～§1.3**、[`telegram-binding.md`](../specs/requirements/domains/agent/onboarding/telegram-binding.md) **§2** |
| **凡 Agent 相关交易写 / 须私有读的查询**，须走 **子账户 scope**；**禁止**默认 **主账户** Key | [`billing-management/overview.md`](../specs/requirements/domains/admin/billing-management/overview.md) **§2**、[`exchange-agent/overview.md`](../specs/requirements/domains/agent/exchange-agent/overview.md) |
| **须** 把 **用户业务 Goal**（[`intents`](../specs/requirements/domains/agent/exchange-agent/intents.md)）**收敛**为 **0/1 个** **`scenarioId`**，并 **按** **Golden / Failure / Recovery** **三类路径** **对齐全链路验收**；**发版前** **须** **过** **Goal** **七维**（[`goal-and-execution-paths` §5](../specs/requirements/domains/agent/agent-orchestration/goal-and-execution-paths.md#goal-seven-dimensions)、**JV-10**）；**每条** **主路径** **须** **过** **Golden Path** **八维**（[`§6`](../specs/requirements/domains/agent/agent-orchestration/goal-and-execution-paths.md#golden-path-eight-dimensions)、**JV-11**） | [`goal-and-execution-paths.md`](../specs/requirements/domains/agent/agent-orchestration/goal-and-execution-paths.md)、[`routing-engine.md`](../specs/requirements/domains/agent/agent-orchestration/routing-engine.md)、[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md) **（文首「架构语言」→ [`architecture` §对照](../specs/design/architecture.md)）**、[`journey-validation.md`](./journey-validation.md) |

---

## 3. 会话、交易写与工具

| 须 / 不得 | 条文入口 |
|-----------|----------|
| **任一交易所私有写** 前：**须** **`read_skill_operation_spec`**（**FR-T11**），**须** **Telegram 类型 A** 明示确认后再 **`call_exchange_write`**（**禁止静默写**） | [`trade-assistance.md`](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md) **§2·§8**、[ADR-001](../specs/design/adr/001-telegram-confirm-before-coobit-write.md)、[`trade-via-agent.md`](../specs/requirements/flows/trade-via-agent.md) |
| **A 类写 `skillId`** **逐条登记**（**FR-TS07**）；编排 **`scenarioId`** **须** 与 [`routing-engine.md`](../specs/requirements/domains/agent/agent-orchestration/routing-engine.md) **同窗** | `trade-assistance` **§4·§8.2** |
| **矩阵 `TBD` / 书面延期** **或** **`product.md` §非目标 **明确** **暂不交付** **之能力**（**现货 OCO/bracket**），**不得**对客宣称「经 Agent 已支持实盘闭环」；**须** **`FR-T05` / 主站 / 分步** | [**`product.md` §非目标**](../specs/requirements/product.md)、[`contract-closure.md`](../specs/requirements/contract-closure.md)、[`design/api.md`](../specs/design/api.md)、[`trade-via-agent.md`](../specs/requirements/flows/trade-via-agent.md) |
| **504 / UNKNOWN**：不得向用户 **断言**已成交/已撤单；须 **查单对账** 叙事与计费 **同窗** | [`architecture.md`](../specs/design/architecture.md)、[`consume-and-bill.md`](../specs/requirements/flows/consume-and-bill.md)、[`billing-management/overview.md`](../specs/requirements/domains/admin/billing-management/overview.md) **§10** |
| **对上 Coobit 私有所内 HTTP**：**出站默认**经 **ChainUp `openapi-ai` 官方宿主**（Skill/CLI/MCP，**制品须 pin**）；**不得**借此 **调用白名单外 PATH**；**OpenAPI/`design/api` 矩阵** **仍为** **契约 SSOT**（**非**「应与宿主一并删除的重复胶水」） | [`integrations/exchange/overview.md`](../specs/requirements/integrations/exchange/overview.md)、[`product.md`](../specs/requirements/product.md) **方向·术语**, [`trade-assistance.md`](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md) **文首** |
| **统一交易语义（多所前置）**：**能力名/意图** **不得** **长期等价于** **某一所 REST 形态**；**工程** **须** **Intent → Canonical → Gateway → Adapter**（**openapi-ai** **可为 Adapter 宿主之一**）；**本 Git 仓** **仅** **叙事与设计**（**[`ADR-004`](../specs/design/adr/004-intent-centric-execution-and-canonical-trading-model.md)**、**[`canonical-trading-model.md`](../specs/design/canonical-trading-model.md)**、**[`trade-assistance` §2.6](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)**） — **DoD B** **见** **[`CC-P1-07`](../specs/requirements/contract-closure.md#cc-p1-07)** | 同上 + [`architecture.md`](../specs/design/architecture.md) |

---

## 4. 计费与账单

| 须 / 不得 | 条文入口 |
|-----------|----------|
| Agent 消耗 **S5 仅轨 B 权益核销**；**子账户 USDT** **用于交易/理财**（**与 Agent 消耗分域**） | [`billing-management/commerce-model.md`](../specs/requirements/domains/admin/billing-management/commerce-model.md) · [`overview.md`](../specs/requirements/domains/admin/billing-management/overview.md) **§2** |
| **订阅 / Capability / 加购包**（用尽即停、仅加购延展）；**`executionId` 仍为锚** | [`commerce-model.md`](../specs/requirements/domains/admin/billing-management/commerce-model.md)、[`billing-management/functions.md` §5](../specs/requirements/domains/admin/billing-management/functions.md) |
| **单次可计费执行** 顺序（门禁 → `executionId` → 封印 → 结算；**Phase 2 S2/S5** **含额度/轨 B**） | [`consume-and-bill.md`](../specs/requirements/flows/consume-and-bill.md) |
| 用户 **配额 / Capability 核销流水 / 月度汇总 / CSV**（**交易所站内 · `/subaccount/billing` · 账单与消耗**） | **FR-B17～B20**、**FR-WEB07～11**（**`me/commerce`**）；原型 SSOT [`web-billing-reconciliation` §0](../specs/requirements/domains/web/admin-console-web-billing-reconciliation.md)；触点 [`agent-billing.md`](../specs/requirements/domains/web/agent-billing.md) |
| **`traceKey`（D-5）**、**未知终局 × 计费（D-7）**、**收入专户（D-12）** 关单 **须** 工单/MR 证据；**禁止**无实现 MR **预勾** PRD §13 | [`contract-closure.md`](../specs/requirements/contract-closure.md) **§2.1**、`billing` **§10.3.1·§10.6.1** |

---

## 5. 运营、观测与合规（提要）

| 须 / 不得 | 条文入口 |
|-----------|----------|
| 控制台 **Bot/Webhook、`TELEGRAM_*`** 与 **附录 A 发布勾选** **分期**：文档 **≠** 生产实测闭环 | [`admin-bot-config.md`](../specs/requirements/domains/agent/telegram/admin-bot-config.md)、**`contract-closure` CC-P1-06** |
| **C 类外网工具** 生产启用：**合规工单 / `legalReviewTicketId`** 等写闸 | [`contract-closure.md`](../specs/requirements/contract-closure.md) **CC-P1-02**、ADR-003 |
| 观测 **`toolId`/`skillId`/`traceKey`** **须** 可与账务 join（关单条件见收口表） | [`observability/overview.md`](../specs/requirements/observability/overview.md) |

---

## 6. 产品负责人例行事项（与本仓库纪律对齐）

1. **范围变更**：改 **`product.md`** 后 **回写** [`overview.md`](./overview.md)、[`roadmap.md`](./roadmap.md)、[`release-notes.md`](./release-notes.md)（若对外发版）。  
2. **对外话术**：路演/合作方 **须** **`product.md` + `design/api` 矩阵 + `contract-closure` + `closure-remaining`（§7 / §7.5 / §7.6 · Open 项与 MR 路径）** **同屏**；**禁止**仅靠 `product/` 故事代替「已冻结生产契约」。  
3. **小团队发版**：更新 **`release-notes`** 最新一节（[`LITE-MODE` §3](../specs/requirements/LITE-MODE.md)）。  
4. **跨职能收口**：**D-12 财务会签**、**D-5/D-7 实现勾选**、**Hosted/tag** 等 — **派工见** [`closure-remaining.md`](../specs/requirements/closure-remaining.md)（**[§7](../specs/requirements/closure-remaining.md#cc-remaining-open-items)** · **[§7.5](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)**、**走读缺口** **[§7.1](../specs/requirements/closure-remaining.md#cc-remaining-gap-paste)**）；产品侧 **跟进度与 PR 勾选纪律**，**不**替代工单证据。  
5. **`specs` 大改后**：检查 [`README.md`](./README.md) **文档地图**、[`requirements-review.md`](./requirements-review.md) **§2** 议题链。

---

## 7. 延伸阅读（叙事 × 步骤 × 契约）

| 目的 | 文档 |
|------|------|
| 故事线七章 | [`flows.md`](./flows.md) |
| 鸟瞰技术闭环 | [`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md)；**对内架构叙事** [`architecture`「与通用 Agent 栈之对照」](../specs/design/architecture.md) |
| 评审会议打包 | [`requirements-review.md`](./requirements-review.md) |
| 聚合索引 | [`spec.md`](../specs/requirements/spec.md) |

---

**文档版本**：2026-05-14 · **维护**：产品负责人 · **本版**：§2 **条文入口** **补** **`e2e` 文首→`architecture` §对照**。**承** **2026-05-14**。
