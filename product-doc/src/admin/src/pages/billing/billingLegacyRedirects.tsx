import { Navigate, useSearchParams } from "react-router-dom";
import { billingOpsLink, isBillingOpsTab } from "./billingPaths";

function opsRedirect(tab: "subscriptions" | "packs" | "rules" | "orders" | "consumption") {
  return function BillingLegacyRedirect() {
    const [searchParams] = useSearchParams();
    const merged: Record<string, string> = {};
    searchParams.forEach((v, k) => {
      if (k !== "tab") merged[k] = v;
    });
    return <Navigate to={billingOpsLink(tab, merged)} replace />;
  };
}

export const BillingSubscriptionsPage = opsRedirect("subscriptions");
export const BillingPacksPage = opsRedirect("packs");
export const BillingOrdersPage = opsRedirect("orders");
export const BillingUserConsumptionPage = opsRedirect("consumption");

export function BillingCommercePage() {
  return <Navigate to="/billing/operations?tab=rules" replace />;
}

/** @deprecated 计量定价已下线，书签统一进计费总览 */
export function BillingPricingPage() {
  return <Navigate to="/billing/overview" replace />;
}

export function BillingLegacyOpsRedirect() {
  const [searchParams] = useSearchParams();
  const tab = searchParams.get("tab");
  const target = isBillingOpsTab(tab) ? tab : "subscriptions";
  const merged: Record<string, string> = {};
  searchParams.forEach((v, k) => merged[k] = v);
  return <Navigate to={billingOpsLink(target, merged)} replace />;
}
