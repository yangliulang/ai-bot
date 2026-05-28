# 用户端 · Agent 账单对齐（`src/Web` · Capability 核销）

**路径**：`specs/requirements/domains/web/admin-console-web-billing-reconciliation.md`  
**读者**：产品、Web、计费联调  
**原型 SSOT**：`src/Web/src/pages/subaccount/BillingPage.tsx` · `src/Web/README.md`  
**域 FR**：[`agent-billing.md`](agent-billing.md) · [`commerce-model.md`](../admin/billing-management/commerce-model.md)  
**运营台订单对读**：[`admin-console-billing-pages-reconciliation.md`](../admin/billing-management/admin-console-billing-pages-reconciliation.md) **§3.2.1**

---

## 0. Demo 对齐快照（2026-05-27 · 用户 H5）

| 项 | 原型 |
|----|------|
| **主账单页** | `/subaccount/billing` · **一页同窗** **配额摘要 + 明细 Tab**（**SC-WEB-07**） |
| **页眉** | 「账单与消耗」；简介 **Capability 核销** |
| **上限区块** | `CommerceQuotaOverview`：档位 · 周期 · Capability 进度条 · 用尽告警 · 升级/加购；**无**自动续费 |
| **Tab · 核销流水** | `me/commerce/consumptions` · Capability/核销状态/**执行 ID（纯数字 `executionId`）** · **成本观测**列 · CSV |
| **Tab · 月度汇总** | Capability 核销次数 + **成本观测** |
| **订阅与购买** | `/subscription` · 仅 **升级/买包入口** + 链回主账单 |
| **Crypto 结账** | `/subscription/checkout?kind=&sku=` · 见 **§0.1** |
| **兼容** | `/subaccount/agent-billing` · `/billing/summary` → `/subaccount/billing`；`?tab=legacy` → 核销流水 |
| **Deeplink** | [`commerce-deeplink.md`](commerce-deeplink.md) · 终态 **`/subaccount/billing`** |

**刻意非主链（Demo）**：Crypto checkout 为 **购买演示**（FR-B18 PSP **量产 MR**）；到账以 PSP/Webhook 为准。

### 0.1 Crypto 结账（`SubscriptionCheckoutPage` · `CryptoPaymentPanel`）

| 项 | 原型 |
|----|------|
| **订单号** | **纯数字 14～20 位**（同窗运营台 · `commerceOrderId.ts`） |
| **用户支付地址** | 完整收款地址（按网络切换）；标签 **「用户支付地址」**；可复制 |
| **步骤** | 确认订单 → 链上转账（倒计时）→ 确认中 → 完成 / 过期 |
| **与运营台** | 同一 `COMMERCE_RECEIVE_ADDRESSES` 演示地址族；运营 **`OrdersPanel` 详情** 展示 **`paymentAddress`** |
| **订单列表联动** | **演示不自动写入** Admin `MOCK_COMMERCE_CRYPTO_ORDERS`（Web/Admin **分端口**） |

---

## 0.2 原型实现清单（改代码时对照）

| 路径（`src/Web/src/`） | 说明 |
|------------------------|------|
| `pages/subaccount/BillingPage.tsx` | 主账单 · `parseBillingDetailTab` |
| `copy/agentBillingCopy.ts` | 页眉/Tab/配额文案 |
| `components/billing/CommerceQuotaOverview.tsx` | FR-B17 配额区 |
| `components/billing/CommerceConsumptionLedger.tsx` | 核销流水 · 执行 ID 列 · CSV |
| `components/billing/CommerceMeteringMonthlyCard.tsx` | 月度汇总 |
| `hooks/useMeCommerceSummary.ts` · `useMeCommerceConsumptions.ts` | `me/commerce` 数据 |
| `data/meCommerceConsumptionMock.ts` | 演示数据 · 纯数字 `executionId` |
| `lib/commerceDeeplink.ts` | Deeplink 拼装 |
| `lib/commerceOrderId.ts` · `data/commercePaymentAddresses.ts` | 结账 |
| `pages/subscription/*` · `hooks/useCryptoCheckout.ts` | 订阅购买 · Crypto 结账 |
| `layout/WebShell.tsx` | **账单与消耗** 导航 |

---

## 2. 维护约定

- **改 IA/列/文案**：先改 **本篇 §0**，再改 [`agent-billing.md` §5](agent-billing.md)、[`src/Web/README.md`](../../../../src/Web/README.md)、`agentBillingCopy.ts` · `subscriptionCopy.ts`。
- **改订单/支付字段**：同窗 **运营台** [`admin-console-billing-pages-reconciliation.md` §3.2.1](../admin/billing-management/admin-console-billing-pages-reconciliation.md)。
- **实质需求变更**：同窗 [`product/roadmap.md`](../../../../product/roadmap.md) 横切 · Web 账单行。

---

**文档版本**：0.5.0 · **2026-05-27** · **移除轨 A / `me/billing` 原型**
