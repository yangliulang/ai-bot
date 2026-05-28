# `domains/web/` — 浏览器触点（Agent 产品线绑定 onboarding · 交易所站内账单 UX）

本目录承载 **浏览器侧** **UX / 交互需求**（**FR-WEB\***、**SC-WEB\***）：**① Agent 绑定页（onboarding）** — **Agent 项目托管**（[`agent-onboarding.md`](agent-onboarding.md)，**`me/agent/*`** **HTTP 同窗 OpenAPI**）；**② 交易所站内账单页** — [`agent-billing.md`](agent-billing.md)，与 **`product.md`** **触点分界** 同窗。

**不写**：OpenAPI 字段全集、账务落账策略、运行时编排 — **真源**分别见 [`design/api.md`](../../../design/api.md)、[`../admin/billing-management/overview.md`](../admin/billing-management/overview.md)、[`../agent/onboarding/`](../agent/onboarding/overview.md)、[`flows/`](../../flows/)；**Telegram · §2.5 · 类型 A / §2～§2.6** — [`../agent/telegram/overview.md`](../agent/telegram/overview.md)。

| 文件 | 内容 |
|------|------|
| [`overview.md`](overview.md) | **域边界**、文档地图、邻域互引、**§4** **FR-WEB→CC·`design/api` 映射** |
| [`agent-onboarding.md`](agent-onboarding.md) | **Agent 产品线绑定页** FR-WEB01～06、SC-WEB |
| [`agent-billing.md`](agent-billing.md) | **FR/SC**（**账单与消耗** · **`me/commerce` 主链**） |
| [`admin-console-web-billing-reconciliation.md`](admin-console-web-billing-reconciliation.md) | **`src/Web` 原型 SSOT · §0**（IA/列/文案 · **改页面先改本篇**） |
| [`commerce-deeplink.md`](commerce-deeplink.md) | Telegram ↔ H5 Deeplink |
| [`staging-me-commerce-runbook.md`](staging-me-commerce-runbook.md) | 本地 **`me/commerce`** 探针（`5175`） |

**关单与契约映射**：[`overview.md` §4](overview.md)。

**上级导航**：[`../README.md`](../README.md) · [`../../spec.md`](../../spec.md)
