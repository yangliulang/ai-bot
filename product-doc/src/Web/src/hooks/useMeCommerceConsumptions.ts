import { useCallback, useEffect, useState } from "react";
import { fetchMeCommerceConsumptions, isMeCommerceApiEnabled } from "@/api/meCommerce";
import { MOCK_ME_COMMERCE_CONSUMPTIONS, type MeCommerceConsumptionRow } from "@/data/meCommerceConsumptionMock";

export type ConsumptionDataSource = "mock" | "remote" | "remote+fallback";

const REMOTE_PAGE_SIZE = 10;

export function useMeCommerceConsumptions() {
  const apiOn = isMeCommerceApiEnabled();
  const [rows, setRows] = useState<MeCommerceConsumptionRow[]>(
    apiOn ? [] : MOCK_ME_COMMERCE_CONSUMPTIONS,
  );
  const [nextCursor, setNextCursor] = useState<string | null>(apiOn ? null : null);
  const [source, setSource] = useState<ConsumptionDataSource>(apiOn ? "remote" : "mock");
  const [loading, setLoading] = useState(apiOn);
  const [loadingMore, setLoadingMore] = useState(false);

  const reload = useCallback(async () => {
    if (!apiOn) {
      setRows(MOCK_ME_COMMERCE_CONSUMPTIONS);
      setNextCursor(null);
      setSource("mock");
      return;
    }
    setLoading(true);
    try {
      const { items, nextCursor: nc } = await fetchMeCommerceConsumptions(undefined, REMOTE_PAGE_SIZE);
      if (items.length > 0) {
        setRows(items);
        setNextCursor(nc);
        setSource("remote");
      } else {
        setRows(MOCK_ME_COMMERCE_CONSUMPTIONS);
        setNextCursor(null);
        setSource("remote+fallback");
      }
    } catch {
      setRows(MOCK_ME_COMMERCE_CONSUMPTIONS);
      setNextCursor(null);
      setSource("remote+fallback");
    } finally {
      setLoading(false);
    }
  }, [apiOn]);

  const loadMore = useCallback(async () => {
    if (!apiOn || !nextCursor || loadingMore) return;
    setLoadingMore(true);
    try {
      const { items, nextCursor: nc } = await fetchMeCommerceConsumptions(nextCursor, REMOTE_PAGE_SIZE);
      if (items.length > 0) {
        setRows((prev) => [...prev, ...items]);
        setNextCursor(nc);
      }
    } catch {
      /* 保留已加载页 */
    } finally {
      setLoadingMore(false);
    }
  }, [apiOn, nextCursor, loadingMore]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return {
    rows,
    source,
    loading,
    loadingMore,
    apiOn,
    hasMore: apiOn ? !!nextCursor : false,
    reload,
    loadMore,
  };
}
