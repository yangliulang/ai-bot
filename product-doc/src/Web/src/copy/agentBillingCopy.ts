/** 用户账单页文案 · me/commerce 主链 · 同窗 agent-billing.md FR-B17～19 / FR-WEB07～09 */

import {
  buildAgentBillingDeeplink,
  buildCommercePackDeeplink,
  buildCommerceUpgradeDeeplink,
  type AgentBillingTab,
} from "@/lib/commerceDeeplink";

export const AGENT_BILLING_COPY = {
  pageTitle: "账单与消耗",
  pageIntro:
    "按订阅档位与各 Capability 配额计费：每次可计费执行在下方核销流水中扣减额度。不会从子账户按 Token 事后扣 Agent 费。",

  billingPolicyDetail:
    "结算类型 ENTITLEMENT_DEBIT；配额用尽须升级套餐或购买加购包，不会自动改用子账户 USDT 扣费。",

  tierActiveTag: "当前档位",
  periodEndLabel: "周期到期",
  quotaSectionIntro: "以下为各 Capability 剩余额度；用尽后将阻断对应类型的 Agent 可计费执行。",
  capabilityBucketsTitle: "能力配额",
  packGranularityHint: "加购包粒度",

  recordsSectionTitle: "消耗记录",
  recordsSectionSubtitle: "核销流水与月度 Capability 汇总。",

  tabConsumptions: "核销流水",
  tabMonthly: "月度汇总",

  upgradeCta: "升级套餐",
  buyPackCta: "购买加购包",
  upgradeHint: "提升档位可获得更高 Capability 周期配额（演示链接，生产由主站商品页承接）。",
  buyPackHint: "加购包到账后额度将出现在上方配额卡片；支付流程由主站 PSP 承接（FR-B18）。",

  quotaExhaustedTitle: "部分能力配额已用尽",
  quotaExhaustedBody:
    "请升级套餐或购买加购包后继续使用。这与「子账户 USDT 余额不足」不同，不会从子账户按 Token 事后扣费（FR-B19）。",
  quotaExhaustedBillCode: "CAPABILITY_QUOTA_EXHAUSTED",
  usdtInsufficientBillCode: "INSUFFICIENT_BALANCE",
  billCodeFootnote:
    "配额用尽对应 CAPABILITY_QUOTA_EXHAUSTED；子账户 USDT 不足为 INSUFFICIENT_BALANCE（交易写路径）。二者勿混用。",

  usdtFundsHint:
    "子账户 USDT 用于交易/理财写路径门禁；Agent 消耗按 Capability 配额核销，不在此页按 Token 后付。",

  telegramEntryHint: "已从 Telegram 打开；配额与核销流水见下方。",

  ledgerDebitInsufficientHint:
    "列表「额度不足」为 Capability 配额拒绝（CAPABILITY_QUOTA_EXHAUSTED），非子账户 USDT 余额不足。",
} as const;

export function getCommerceUpgradeUrl(fromTelegram = false): string {
  return buildCommerceUpgradeDeeplink({ fromTelegram });
}

export function getCommercePackUrl(fromTelegram = false): string {
  return buildCommercePackDeeplink({ fromTelegram });
}

/** Deeplink 回跳账单页（兼容旧 `/subaccount/agent-billing`） */
export function agentBillingUrl(tab?: AgentBillingTab, extra?: { tgUser?: string }): string {
  return buildAgentBillingDeeplink({
    tab,
    fromTelegram: extra?.tgUser != null,
    tgUser: extra?.tgUser,
  });
}
