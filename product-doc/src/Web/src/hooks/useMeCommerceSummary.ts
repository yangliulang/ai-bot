import { useCallback, useEffect, useState } from "react";
import { fetchMeCommerceEntitlementsSummary, isMeCommerceApiEnabled } from "@/api/meCommerce";
import { MOCK_ME_COMMERCE_SUMMARY, type MeCommerceEntitlementsSummary } from "@/data/meCommerceMock";

export type MeCommerceDataSource = "mock" | "remote" | "remote+fallback";

export function useMeCommerceSummary() {
  const apiOn = isMeCommerceApiEnabled();
  const [summary, setSummary] = useState<MeCommerceEntitlementsSummary>(MOCK_ME_COMMERCE_SUMMARY);
  const [source, setSource] = useState<MeCommerceDataSource>(apiOn ? "remote" : "mock");
  const [loading, setLoading] = useState(apiOn);

  const reload = useCallback(async () => {
    if (!apiOn) {
      setSummary(MOCK_ME_COMMERCE_SUMMARY);
      setSource("mock");
      return;
    }
    setLoading(true);
    try {
      const remote = await fetchMeCommerceEntitlementsSummary();
      setSummary(remote);
      setSource("remote");
    } catch {
      setSummary(MOCK_ME_COMMERCE_SUMMARY);
      setSource("remote+fallback");
    } finally {
      setLoading(false);
    }
  }, [apiOn]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { summary, source, loading, apiOn, reload };
}
