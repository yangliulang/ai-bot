const TAB_KEYS = ["ledger", "monthly"] as const;

export type BillingDetailTab = (typeof TAB_KEYS)[number];

/** 旧 Deeplink `?tab=legacy` 等归并到核销流水 */
export function parseBillingDetailTab(raw: string | null): BillingDetailTab {
  if (raw === "monthly") return "monthly";
  if (raw === "ledger" || raw === "consumptions" || raw === "legacy" || raw === "quota" || raw === "overview") {
    return "ledger";
  }
  return "ledger";
}
