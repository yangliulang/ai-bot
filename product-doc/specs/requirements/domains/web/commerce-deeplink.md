# Web · Commerce / Billing Deeplink（Telegram ↔ 交易所站内 H5）

**路径**：`specs/requirements/domains/web/commerce-deeplink.md`  
**上级**：[`agent-billing.md`](agent-billing.md) · [`../agent/telegram/overview.md`](../agent/telegram/overview.md) · [`../../integrations/telegram/deeplink.md`](../../integrations/telegram/deeplink.md)

---

## 1. 目的

冻结 **配额用尽 / 升级 / 买包 / 查流水** 从 **Telegram 类型 B 按钮** 跳进 **交易所官方 H5** 时的 **路径与 query 下限**；**不**定义 PSP 支付实现。

---

## 2. H5 路径（SSOT）

| 用户意图 | H5 路径 | 主要 query |
|----------|---------|------------|
| 账单与消耗（配额 + 流水） | `/subaccount/billing` | 默认 **核销流水** Tab；`?tab=overview` / `quota` **滚动至配额区** |
| 月度 Capability 汇总 | `/subaccount/billing` | `tab=monthly` |
| 订阅与购买 | `/subscription` | 升级/买包入口 |
| 升级套餐 | `/subscription/upgrade` → `/subscription/checkout?kind=upgrade&sku=` | `from=telegram`（可选） |
| 购买加购包 | `/subscription/pack` → checkout `kind=pack` | 同上 |
| Crypto 结账 | `/subscription/checkout` | `kind` · `sku` · **纯数字订单号** · **用户支付地址**（同窗 [`agent-billing` §5.1](agent-billing.md)） |
| 兼容旧链 | `/subaccount/agent-billing` | `intent=upgrade\|buy-pack` · `tab` · `start` → 重定向 |
| 兼容 | `/billing/summary` · `/commerce/*` | → `/subaccount/billing` 或 `/subscription/*` |

**原型实现**：[`src/Web/src/lib/commerceDeeplink.ts`](../../../../src/Web/src/lib/commerceDeeplink.ts)。

**环境覆盖**：`VITE_H5_PUBLIC_ORIGIN`（绝对 URL 前缀）· `VITE_COMMERCE_UPGRADE_URL` · `VITE_COMMERCE_PACK_URL`。

---

## 3. Telegram Bot `?start=` payload（≤64 字符）

| payload | 落地 H5（示意） |
|---------|----------------|
| `ab` | `/subaccount/billing?from=telegram`（配额 + 核销流水 · **同窗** §2） |
| `ab_sub` | `/subscription?from=telegram`（订阅与购买入口） |
| `ab_ld` | `/subaccount/billing?from=telegram`（核销流水；默认 Tab，**可省略** `tab=ledger`） |
| `ab_up` | `/subscription/upgrade?from=telegram` |
| `ab_pk` | `/subscription/pack?from=telegram` |

Bot 收到 `/start <payload>` 后 **须** 打开 **官方域名** WebView / 外链，**禁止** 非官方域。

---

## 4. 与 `billCode` / FR-B19 分工

| 场景 | 用户可见 | Deeplink 目标 |
|------|----------|----------------|
| Capability 配额用尽 | 升级/买包（**非** INSUFFICIENT_BALANCE 若 Token 仍足） | `ab_up` / `ab_pk` |
| 子账户 USDT 不足（交易写） | 充值/划转指引 | **子账户资产页**（非本篇路径） |
| 查消耗明细 | 核销流水 Tab | `ab_ld` |

---

## 5. Staging 探针

同窗 [`staging-me-commerce-runbook.md`](staging-me-commerce-runbook.md) · 脚本 [`scripts/staging-mr-bill-probe.sh`](../../../../scripts/staging-mr-bill-probe.sh)（`WEB_ORIGIN` 默认 `5175`）。

---

**文档版本**：0.2.1 · **2026-05-27** · **`ab` / `ab_sub` 分轨** · **维护**：Web 触点 + Telegram 编排 owner · **同窗** [`admin-console-web-billing-reconciliation.md` §0](admin-console-web-billing-reconciliation.md)
