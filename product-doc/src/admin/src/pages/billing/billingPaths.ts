export const BILLING_OPS_PATH = "/billing/operations";

export const BILLING_OPS_TABS = ["subscriptions", "packs", "rules", "orders", "consumption"] as const;
export type BillingOpsTab = (typeof BILLING_OPS_TABS)[number];

export function isBillingOpsTab(v: string | null): v is BillingOpsTab {
  return BILLING_OPS_TABS.includes(v as BillingOpsTab);
}

export function billingOpsLink(tab: BillingOpsTab, query?: Record<string, string | undefined>): string {
  const p = new URLSearchParams({ tab });
  if (query) {
    for (const [k, val] of Object.entries(query)) {
      if (val != null && val !== "") p.set(k, val);
    }
  }
  return `${BILLING_OPS_PATH}?${p.toString()}`;
}

export function billingOverviewLink(): string {
  return "/billing/overview";
}
