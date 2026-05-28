# `src/Web` — Coolbit Agent 用户侧原型

独立 Vite + React 应用（**非生产前端 SSOT**），用于对齐规格中的首次开通、Telegram Deeplink 与 **Agent 账单（me/commerce · Capability 核销）** 叙事。

**触点 UX（FR-WEB）**：[`specs/requirements/domains/web/README.md`](../../specs/requirements/domains/web/README.md)  
**账单对齐 SSOT**：[`admin-console-web-billing-reconciliation.md`](../../specs/requirements/domains/web/admin-console-web-billing-reconciliation.md) **§0**

**视觉**：**`/onboarding`** 为 **独立全屏落地页**。**其余路由**在 **`WebShell`** 内：桌面侧栏 + 主区；窄屏 **底栏「账单」** → **`/subaccount/billing`**。

## 运行

```bash
cd src/Web && npm install && npm run dev
```

默认端口 **5175**。本地 BFF：

```bash
VITE_AGENT_API_BASE_URL=http://localhost:5175 VITE_USE_ME_COMMERCE_API=true npm run dev
```

## 环境变量（可选）

| 变量 | 说明 |
|------|------|
| `VITE_AGENT_API_BASE_URL` | BFF 基址（无尾斜杠） |
| `VITE_USE_ME_COMMERCE_API` | `me/commerce` 摘要 + consumptions |
| `VITE_COMMERCE_UPGRADE_URL` / `VITE_COMMERCE_PACK_URL` | 默认 `/subscription/upgrade` · `/subscription/pack` |
| `VITE_TELEGRAM_BOT_URL` | 开通成功页 Bot 链接 |

## 路由（Agent 账单 · 2026-05-27）

| 路由 | 说明 |
|------|------|
| `/onboarding` | 单页绑定（`me/agent`） |
| `/subaccount/billing` | **账单与消耗**：配额 + 核销流水 + 月度汇总 |
| `/subscription` | 订阅与购买（升级/买包） |
| `/subscription/upgrade` · `/pack` · `/checkout` | 购买演示 · **纯数字订单号** · **用户支付地址**（同窗 Admin 地址族；**订单不自动进运营台列表**） |
| `/subaccount/agent-billing` | 兼容 → `/subaccount/billing` |
| `/billing/summary` | 兼容 → `/subaccount/billing` |
| `/commerce/*` | → `/subscription/*` |

**Deeplink**：[`commerce-deeplink.md`](../../specs/requirements/domains/web/commerce-deeplink.md) · [`commerceDeeplink.ts`](src/lib/commerceDeeplink.ts)

**探针**：`WEB_ORIGIN=http://localhost:5175 ./scripts/staging-mr-bill-probe.sh --web-only`

## 关键实现（与规格 §0 同窗）

| 路径 | 说明 |
|------|------|
| `src/pages/subaccount/BillingPage.tsx` | 主账单 |
| `src/copy/agentBillingCopy.ts` | 页眉 **账单与消耗** |
| `src/components/billing/*` | 配额 · 核销流水 · 月度 |
| `src/lib/commerceDeeplink.ts` | Telegram / H5 Deeplink |
| `src/lib/commerceOrderId.ts` | 结账纯数字订单号 |
| `src/hooks/useCryptoCheckout.ts` | Crypto 结账状态机 |

域 FR：[`agent-billing.md`](../../specs/requirements/domains/web/agent-billing.md) **§5** · 文件索引 **§5.2**

端到端：[`flow/e2e-closed-loop.md`](../../flow/e2e-closed-loop.md)
