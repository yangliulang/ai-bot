# Web / H5 用户触点（Web）— 总览

**路径**：`specs/requirements/domains/web/`。

**职责**：用户在 **浏览器** 内与 Agent 相关的 **两类触点** 的 **交互、信息架构与验收下限**：① **绑定配置页（onboarding）** — **Agent 项目（产品线 Web/H5）承载**，**`me/agent/*`** **契约路径同窗** **[`initialization-flow` §1.2](../agent/onboarding/initialization-flow.md)**、**`FR-WEB06`** — **不要求用户访问 Coobit 交易所主站**，服务端 **经交易所 API** 完成校验；② **账单与消耗（Billing）** — **交易所站内** **`/subaccount/billing` · `me/commerce`**（**[`admin-console-web-billing-reconciliation` §0](admin-console-web-billing-reconciliation.md)**）。与 **Telegram Deeplink**（绑定页 → **产品线**；账单 → **站内**）对齐。**不包含** 会话内 Bot 话术正文（真源 [`../agent/telegram/overview.md`](../agent/telegram/overview.md) **§2.5 · 类型 A；总则 §2～§2.6 · Deeplink/Bot API**）。

**对上 Coobit（配置页保存链）**：服务端 **交易所 API 校验/探测** 出站默认 **`openapi-ai`**（Skill 宿主），制品须 pin；PATH 与出站面 同窗 [`initialization-flow` §1.2](../agent/onboarding/initialization-flow.md)、[`design/api`](../../../design/api.md)、[`agent-coobit-api-allowlist`](../../integrations/exchange/agent-coobit-api-allowlist.md)、[`integrations/exchange/overview`](../../integrations/exchange/overview.md)。（账单触点之账务 HTTP 仍以 `billing` 与 [`design/api`](../../../design/api.md) 为准。）

---

## 1. 文档结构

| 文件 | 内容 |
|------|------|
| [`overview.md`](overview.md)（本文） | 域边界、§2 **不写**、§3 邻域、**§4 关单映射** |
| [`agent-onboarding.md`](agent-onboarding.md) | **配置页**：**FR-WEB01～06**、**SC-WEB-01～06**、**SC-WEB-12**（**UID≠`subUid`**；与 Billing **`SC-WEB-07`** **避让**） |
| [`agent-billing.md`](agent-billing.md) | 账单页：**FR-WEB07～11**、**SC-WEB-07～11**；**§2.1** **Phase 2 配额**（**FR-B17～B21**、**SC-WEB-14～15**） |
| [`admin-console-web-billing-reconciliation.md`](admin-console-web-billing-reconciliation.md) | **`src/Web` 账单 IA 对齐 §0**（改原型先改本篇） |
| [`commerce-deeplink.md`](commerce-deeplink.md) | Telegram ↔ H5 **配额/升级/买包/流水** |
| [`staging-me-commerce-runbook.md`](staging-me-commerce-runbook.md) | 本地 **`me/commerce` BFF** 探针 |

---

## 2. 本域不写（SSOT 归属）

| 主题 | 真源 |
|------|------|
| 子账户开立、API 绑定、幂等与审计步骤 | [`../agent/onboarding/`](../agent/onboarding/overview.md)、[`flows/activate-trading-agent.md`](../../flows/activate-trading-agent.md) |
| Telegram 会话绑定、Deeplink、防钓鱼 | [`../agent/onboarding/telegram-binding.md`](../agent/onboarding/telegram-binding.md)、[`../agent/telegram/overview.md`](../agent/telegram/overview.md) **§2.2～§2.6**（**会话内写确认 · §2.5 · 类型 A** **见** [`trade-via-agent.md`](../../flows/trade-via-agent.md)） |
| **Commerce 配额/消耗（主链）**、`me/commerce/*` | [`../admin/billing-management/commerce-model.md`](../admin/billing-management/commerce-model.md)、[`overview.md`](../admin/billing-management/overview.md) |
| `billCode` 族（配额用尽 vs USDT 不足） | 同上 + [`design/api.md`](../../../design/api.md) |
| 后台运营协查、模块五 IA | [`../admin/billing-management/functions.md`](../admin/billing-management/functions.md)、[`../../admin-console/`](../../admin-console/README.md) |

---

## 3. 邻域关系

1. **onboarding**：摘要字段 **§1.3**、主路径 **FR-ON\*** — Web 页 **成功态与持久摘要**须 **可 join**、**不出现 Secret**（配置页 **输入框短时持有**不归入默认审计「展示面」，同窗 **FR-WEB02 / SC-ON-04**）。  
2. **billing-management**：用户侧 **FR-B\***（流水、导出、月度）— Web 账单页 **语义同窗**。  
3. **telegram**：开通成功后的 **官方 Bot 打开方式**须符合 **渠道 Deeplink 纪律**（同窗 **telegram-binding** / **[telegram/overview §2.2～§2.6](../agent/telegram/overview.md)**；**写路径 §2.5 · 类型 A** 见 [**trade-via-agent**](../../flows/trade-via-agent.md)）。  
4. **exchange-agent**：流水「场景类型」归因与 **交易 / 非交易** 划分须与 **可计费执行** 归类 **一致**（同窗 [`../agent/exchange-agent/trade-assistance.md`](../agent/exchange-agent/trade-assistance.md)、[`flows/consume-and-bill.md`](../../flows/consume-and-bill.md)）。

---

## 4. 关单与契约映射（FR-WEB → CC · design/api）

**说明**：**`domains/web`** **不单独增设** **P0/P1 CC**；本节供 **MR 勾选**、**登记表对读** 与 **触点验收** 引用 — **Web 页面对客承诺**须与 **下列同窗 CC / OpenAPI** **一并闭合**（或 **在 `contract-closure` §4/§8 显式登记豁免**）。**关单导航 / 首节派工 / 勾选路径**：[**`closure-remaining` §0 速链**](../../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../../closure-remaining.md#cc-exec-solve-path) · [**§7.5～§7.6**](../../closure-remaining.md#cc-remaining-open-close-path)（与 **`contract-closure` §4 / §8 / §10** **同窗**）。

### 4.1 [`contract-closure.md`](../../contract-closure.md)（节选）

| FR-WEB | 同窗 CC | 映射说明 |
|--------|---------|----------|
| **FR-WEB01～04** | （无独占 CC） | **业务门禁与幂等**以 **`SC-ON*`**、**`flows/activate-trading-agent`** **为准**；**OpenAPI 登记表** **总体纪律**同窗 **`CC-P0-01`** **§1.2 六款**（**`user/onboarding.yaml` 行** **须** **可访问 Spec + Owner**）。 |
| **FR-WEB05**（打开 **官方 Telegram Bot**） | **`CC-P1-06`**（**同窗口径**） | 触点 **外链/Deeplink** **须** **与** **运营配置之 Bot 身份** **一致**；**防钓鱼**同窗 [`telegram-binding`](../agent/onboarding/telegram-binding.md)、[`telegram/overview` §2.2～§2.6 · §2.5 · 类型 A](../agent/telegram/overview.md)。**§4.2** **不替代** **Hosted/生产实测 DoD**。 |
| **FR-WEB05**（**划转**叙事） | **`CC-P0-03`**（**叙事边界**） | 页面 **仅引导**；**扣减主体 / 可用余额事实**以 **`billing` §2**、**账务 HTTP** **为准**。 |
| **FR-WEB07～09**（**配额/消耗主链**） | **（轨 B · `contract-closure` §8）** | **`me/commerce/*`** · [`user/commerce-me.yaml`](../../../openapi/user/commerce-me.yaml) **与** **FR-B17～B20** **同窗**；**消耗明细/核销状态** **§5.3 join** |
| **FR-WEB12～13**（**§2.1 · Phase 2**） | **（轨 B · 独立 MR）** | **`me/commerce/*`** · **`GET …/entitlements/summary`** **与** **FR-B17** **同窗**；**生产闭环** **`contract-closure` §8 轨 B MR** |
| **FR-WEB09**（**执行 ID / trace 展示**） | **`CC-P0-05`**（**间接**） | 用户可见 **`executionId`**（**纯数字 10～19** · [`agent-billing` §2.2](agent-billing.md)）与 **`billingTraceId`** **须** **可与** **附录 A `D-5`/`D-7`** **观测 join** — **DoD** **仍归** **`billing` §10.3.1** **与实现 MR**。 |

### 4.2 [`design/api.md`](../../../design/api.md) 登记表与 PATH 示意（同窗）

| FR-WEB | 登记表行 / 专节（节选） | OpenAPI（仓库内 Spec） | PATH 示意（**终裁以 YAML `paths` 为准**） |
|--------|-------------------------|-------------------------|-------------------------------------------|
| **FR-WEB01～06** | **Agent 绑定 · `me/agent/*`** | [`openapi/user/onboarding.yaml`](../../../openapi/user/onboarding.yaml) | 见 **`design/api`** **用户 Agent 开通 / 绑定** 专节（与 [`onboarding/overview`](../agent/onboarding/overview.md) **对齐**） |
| **FR-WEB07～09** | **Commerce 配额/消耗（主链）** | [`openapi/user/commerce-me.yaml`](../../../openapi/user/commerce-me.yaml) | **`GET`** `.../me/commerce/entitlements/summary`；**演进** **消耗明细/导出 PATH** **implementation MR** — **同窗** **`commerce-model` §5.3** |
| **FR-B17**（**§2.1**） | **用户侧 · Commerce 配额摘要** | [`openapi/user/commerce-me.yaml`](../../../openapi/user/commerce-me.yaml) | **`GET`** `.../me/commerce/entitlements/summary` |
| **FR-WEB07～11** | **用户侧 H5 · `me/commerce`** | [`openapi/user/commerce-me.yaml`](../../../openapi/user/commerce-me.yaml) | **`GET`** `.../me/commerce/entitlements/summary` · **`GET`** `.../me/commerce/consumptions`（**实现 MR** 同窗 **§5.3**） |

**内部扣减面（非浏览器直连）**：[`internal/billing-entitlements.yaml`](../../../openapi/internal/billing-entitlements.yaml) — **Agent S5 · `ENTITLEMENT_DEBIT`**。用户 H5 **对客** **仅** **`me/commerce`**（**[`admin-console-web-billing-reconciliation.md`](admin-console-web-billing-reconciliation.md) §0**）。

---

## 5. 入口链

- [`../../spec.md`](../../spec.md)、[`../../product.md`](../../product.md)、[`contract-closure.md`](../../contract-closure.md)
- [`closure-remaining` §0 速链](../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../closure-remaining.md#cc-exec-solve-path) · [§7 开放项](../../closure-remaining.md#cc-remaining-open-items)
- [`../README.md`](../README.md)、[`../agent/README.md`](../agent/README.md)

---

**文档版本**：1.2.6 · **维护**：产品 + Web 触点 owner · **本版**：**全仓叙事清扫（§0 同窗 reconciliation）**。**承** **1.2.5**。
