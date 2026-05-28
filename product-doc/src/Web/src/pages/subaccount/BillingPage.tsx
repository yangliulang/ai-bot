import { Alert, Tabs, Typography } from "antd";
import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { CommerceConsumptionLedger } from "@/components/billing/CommerceConsumptionLedger";
import { CommerceMeteringMonthlyCard } from "@/components/billing/CommerceMeteringMonthlyCard";
import { CommerceQuotaOverview } from "@/components/billing/CommerceQuotaOverview";
import { AGENT_BILLING_COPY } from "@/copy/agentBillingCopy";
import { useMeCommerceConsumptions } from "@/hooks/useMeCommerceConsumptions";
import { useMeCommerceSummary } from "@/hooks/useMeCommerceSummary";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { parseBillingDetailTab, type BillingDetailTab } from "@/lib/billingPageTabs";

const { Paragraph } = Typography;

const COMPACT_LAYOUT_QUERY = "(max-width: 1024px)";

/** 子账户 · 账单与消耗（Capability 核销 · me/commerce） */
export default function BillingPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const commerce = useMeCommerceSummary();
  const consumptions = useMeCommerceConsumptions();
  const compactLayout = useMediaQuery(COMPACT_LAYOUT_QUERY);
  const quotaSectionRef = useRef<HTMLDivElement>(null);

  const tabParam = searchParams.get("tab");
  const [activeTab, setActiveTab] = useState<BillingDetailTab>(() => parseBillingDetailTab(tabParam));

  const fromTelegram = searchParams.get("from") === "telegram";

  useEffect(() => {
    const next = parseBillingDetailTab(tabParam);
    if (tabParam === "quota" || tabParam === "overview") {
      setActiveTab("ledger");
      requestAnimationFrame(() => {
        quotaSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      return;
    }
    setActiveTab(next);
  }, [tabParam]);

  const onTabChange = useCallback(
    (key: string) => {
      const parsed = parseBillingDetailTab(key);
      setActiveTab(parsed);
      setSearchParams(
        (prev) => {
          const n = new URLSearchParams(prev);
          if (parsed === "ledger") n.delete("tab");
          else n.set("tab", parsed);
          return n;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  return (
    <div className="coolbit-billing-page">
      <header className="coolbit-billing-page__header">
        <h1 className="coolbit-page-title coolbit-billing-page__title">{AGENT_BILLING_COPY.pageTitle}</h1>
        <Paragraph className="coolbit-billing-page__intro">{AGENT_BILLING_COPY.pageIntro}</Paragraph>
      </header>

      {fromTelegram ? (
        <Alert
          type="info"
          showIcon
          closable
          className="coolbit-billing-page__telegram"
          message={AGENT_BILLING_COPY.telegramEntryHint}
        />
      ) : null}

      <div ref={quotaSectionRef}>
        <CommerceQuotaOverview
          summary={commerce.summary}
          source={commerce.source}
          loading={commerce.loading}
        />
      </div>

      <section className="coolbit-billing-records" aria-label="消耗记录">
        <div className="coolbit-billing-records__head">
          <h2 className="coolbit-billing-records__title">{AGENT_BILLING_COPY.recordsSectionTitle}</h2>
          <Paragraph type="secondary" className="coolbit-billing-records__subtitle">
            {AGENT_BILLING_COPY.recordsSectionSubtitle}
          </Paragraph>
        </div>

        <Tabs
          className="coolbit-billing-tabs"
          activeKey={activeTab}
          onChange={onTabChange}
          destroyInactiveTabPane={false}
          items={[
            {
              key: "ledger",
              label: AGENT_BILLING_COPY.tabConsumptions,
              children: (
                <CommerceConsumptionLedger
                  embedded
                  rows={consumptions.rows}
                  source={consumptions.source}
                  loading={consumptions.loading}
                  compactLayout={compactLayout}
                  apiPagination={
                    consumptions.apiOn
                      ? {
                          hasMore: consumptions.hasMore,
                          loadingMore: consumptions.loadingMore,
                          onLoadMore: consumptions.loadMore,
                        }
                      : undefined
                  }
                />
              ),
            },
            {
              key: "monthly",
              label: AGENT_BILLING_COPY.tabMonthly,
              children: <CommerceMeteringMonthlyCard embedded compactLayout={compactLayout} />,
            },
          ]}
        />
      </section>
    </div>
  );
}
