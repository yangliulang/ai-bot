# Business（业务层索引）

本目录聚合 **业务向叙事与需求入口** 的链接，**不替代**各域 SSOT。

**交付形态（当前主线）**：在 **现有交易所后台** 增加 **交易 Agent** 管理能力（配置 / 计费 / 提示词 / 观测等以各域文档为 SSOT）；终端用户使用 **Telegram Bot**。双端与触点见域导航：[**`domains/README.md`**](../domains/README.md)、[**`domains/agent/telegram/README.md`**](../domains/agent/telegram/README.md)、[**`domains/web/README.md`**](../domains/web/README.md)（**绑定 onboarding（可外置）** · **站内账单 · FR-WEB**）。**小团队发版关门**：[**`product/release-notes.md`**](../../../product/release-notes.md)（与 [`LITE-MODE.md`](../LITE-MODE.md) **§3** 同窗）。

新增 `positioning.md`、`pricing.md` 等独立文件时，在此目录维护索引表即可。

| 主题 | 当前权威位置 | 说明 |
|------|----------------|------|
| **发版能力快照（半页纸）** | [`../../../product/release-notes.md`](../../../product/release-notes.md)、[`LITE-MODE.md`](../LITE-MODE.md) **§3** | **不**替代 `product.md` / 各域；**此刻哪些未承诺**以 release-notes **从新到旧第一节**为准 |
| **「文档完整性」读法（范围·分仓·计数）** | [`../../../product/release-notes.md`](../../../product/release-notes.md) **篇首** §「与「文档完整性」评估如何对齐」 | **「完整」**限于 [`product.md`](../product.md) 已定稿范围；**实现/Hosted 他仓** 不以本仓文档独证签发；**勿写死**全仓或子目录 Markdown **个数** |
| **关单执行（P0/P1 分工）** | [`closure-remaining.md`](../closure-remaining.md)（**[§0 速链](../closure-remaining.md#closure-remaining-quicklinks)** · **[§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)** · **[§7 开放项总表](../closure-remaining.md#cc-remaining-open-items)** · **[§7.5 闭环路径](../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 执行清单](../closure-remaining.md#cc-closure-exec-checklist)**）、[`contract-closure.md`](../contract-closure.md) | **本仓** **vs** **所内/实现** **速查**；**证据** **§2.1**、**MR 模板 §3** |
| **Prompt 治理清单（非 SSOT）** | [`product/prompt-governance-checklist.md`](../../../product/prompt-governance-checklist.md)、[`prompts/README.md`](../prompts/README.md) | **清单** **≠** **契约**；**正文发布** **走** **`prompt-management`** |
| **需求阶段定稿 vs 生产 B 阶段** | [`../product.md`](../product.md)、[`../contract-closure.md`](../contract-closure.md) **[§3.0](../contract-closure.md#cc-p1-doc-vs-b)** | **product 已定稿** **≠** **P0/P1 已关**；**业务叙事** **仍以** **域/flows** **为准** |
| 定位与范围 | [`../../../product/overview.md`](../../../product/overview.md)、[`../product.md`](../product.md) | 人类可读与方向 SSOT |
| 定价与计费 | [`../domains/admin/billing-management/commerce-model.md`](../domains/admin/billing-management/commerce-model.md)、[`overview.md`](../domains/admin/billing-management/overview.md) | **对客**：订阅 · Capability · 加购包；**Agent 消耗 S5 仅轨 B 权益核销** |
| 用户画像 / Personas | [`../../../product/overview.md`](../../../product/overview.md)（叙事） | 若需独立成文，可在此目录新增 `personas.md` 并链回 product |
| 场景与用例 | [`../flows/`](../flows/README.md) | 主流程（业务步骤级） |
| **主站 / H5 · 浏览器触点 UX（Agent 产品线绑定 + 站内账单）** | [`../domains/web/README.md`](../domains/web/README.md)（[`overview` §4→CC](../domains/web/overview.md)） | **FR-WEB**；编排/账务契约仍以 **`onboarding`** / **`billing-management`** / **`design/api`** 为准 |
| **Telegram Bot / Webhook（交易所后台 · 运维配置）** | [`../domains/agent/telegram/admin-bot-config.md`](../domains/agent/telegram/admin-bot-config.md)，[`../domains/admin/trading-agent-config/keys.md`](../domains/admin/trading-agent-config/keys.md) **§4**；登记表 [`../../design/api.md`](../../design/api.md) **`Telegram Bot / Webhook` 行**；[`../contract-closure.md`](../contract-closure.md) **CC-P1-06**；PRD **[`management-console §13`](../domains/admin/management-console-v1-prd.md)** | 与 **模块七**同窗；密钥仅 **`secretRef`** |
| 合规与审计 | [`../observability/overview.md`](../observability/overview.md)、[`../contract-closure.md`](../contract-closure.md) | 可追溯、对外承诺闭环；法务条款以所内文书为准 |

**相关**：渠道与终端能力见 [`../domains/agent/telegram/`](../domains/agent/telegram/README.md)。
