# Web · `me/commerce` 本地 Staging Runbook

**用途**：`src/Web` Dev BFF 走读 **用户侧** Capability 计费读路径，与 Admin [`staging-mr-bill-runbook.md`](../admin/billing-management/staging-mr-bill-runbook.md) **分工**（Admin `5173/5174` · Web `5175`）。

**证据**：[`closure-staging-evidence-log.md`](../../closure-staging-evidence-log.md) **§2.4**。

---

## 1. 启动

```bash
cd src/Web
# .env.development
# VITE_AGENT_API_BASE_URL=http://localhost:5175
# VITE_USE_ME_COMMERCE_API=true
npm run dev
```

---

## 2. 一键探针（与 Admin 同窗脚本）

```bash
# 仅 Web（用户侧）
WEB_ORIGIN=http://localhost:5175 ./scripts/staging-mr-bill-probe.sh --web-only

# Admin + Web（推荐）
ADMIN_ORIGIN=http://localhost:5173 WEB_ORIGIN=http://localhost:5175 ./scripts/staging-mr-bill-probe.sh
```

| 路径 | FR |
|------|-----|
| `GET …/me/commerce/entitlements/summary` | FR-B17 |
| `GET …/me/commerce/consumptions?cursor=&pageSize=` | FR-WEB08～09 |

实现：`src/Web/dev/meCommerceBffMiddleware.ts`。

---

## 3. Deeplink 点验（手工）

| 步骤 | URL |
|------|-----|
| 配额摘要 | `/subaccount/billing` |
| 核销流水 Tab | `/subaccount/billing`（默认 Tab） |
| Telegram 升级 | `/subscription/upgrade?from=telegram` |
| Crypto 结账 | `/subscription/checkout?kind=upgrade&sku=` · **用户支付地址** · 纯数字订单号 |
| intent 兼容 | `/subaccount/agent-billing?intent=buy-pack` → `/subscription/pack` |

参数表：[`commerce-deeplink.md`](commerce-deeplink.md)。

---

**文档版本**：0.3.0 · **2026-05-27** · **移除 `me/billing` 探针**
