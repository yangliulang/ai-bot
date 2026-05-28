import { Tabs } from "antd";
import { useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { ProductPageShell } from "../../components/product";
import { BILLING_OPERATIONS } from "../../copy/opsPanelHints";
import { billingOpsLink, isBillingOpsTab, type BillingOpsTab } from "./billingPaths";
import {
  BillingRulesPanel,
  ConsumptionPanel,
  OrdersPanel,
  ResourcesPanel,
  SubscriptionsPanel,
} from "./billingOperationsPanels";

const TAB_ITEMS: { key: BillingOpsTab; label: string; hint: string }[] = [
  { key: "subscriptions", label: "订阅套餐", hint: "" },
  { key: "packs", label: "资源管理", hint: "" },
  { key: "rules", label: "计费规则", hint: "" },
  { key: "orders", label: "订阅订单", hint: "" },
  { key: "consumption", label: "用户消耗", hint: "" },
];

const CLEAN_SHELL_TABS: BillingOpsTab[] = ["subscriptions", "packs", "rules", "orders", "consumption"];

export function BillingOperationsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const rawTab = searchParams.get("tab");
  const activeTab: BillingOpsTab = isBillingOpsTab(rawTab) ? rawTab : "subscriptions";

  const onTabChange = useCallback(
    (key: string) => {
      const p = new URLSearchParams();
      p.set("tab", key);
      if (key === "orders") {
        for (const k of ["userId", "orderId", "productId", "kind", "status", "network"] as const) {
          const v = searchParams.get(k);
          if (v) p.set(k, v);
        }
        const legacySku = searchParams.get("sku");
        if (legacySku && !searchParams.get("productId")) p.set("productId", legacySku);
      } else {
        const userId = searchParams.get("userId");
        if (userId && key === "consumption") p.set("userId", userId);
        const productId = searchParams.get("productId") ?? searchParams.get("sku");
        if (productId && key === "subscriptions") p.set("productId", productId);
      }
      setSearchParams(p);
    },
    [searchParams, setSearchParams],
  );

  return (
    <ProductPageShell
      pageId="billing.operations"
      showPageId={false}
      title={BILLING_OPERATIONS.title}
      description={CLEAN_SHELL_TABS.includes(activeTab) ? undefined : BILLING_OPERATIONS.description}
    >
      <Tabs
        className="billing-ops-tabs"
        type="card"
        activeKey={activeTab}
        onChange={onTabChange}
        destroyInactiveTabPane={false}
        items={TAB_ITEMS.map((t) => ({
          key: t.key,
          label: t.label,
          children: (
            <>
              {t.key === "subscriptions" ? (
                <SubscriptionsPanel />
              ) : t.key === "packs" ? (
                <ResourcesPanel />
              ) : t.key === "rules" ? (
                <BillingRulesPanel />
              ) : t.key === "orders" ? (
                <OrdersPanel />
              ) : (
                <ConsumptionPanel />
              )}
            </>
          ),
        }))}
      />
    </ProductPageShell>
  );
}

export { billingOpsLink };
