import { useCallback, useEffect, useState } from "react";
import { isBillingLedgerApiEnabled, searchAdminBillingTraces } from "../api/billingLedgerClient";
import { mockBillingLedger } from "../data/mock";
import type { MockBillingLedgerRow } from "../data/types";

export type BillingLedgerDataSource = "mock" | "remote" | "remote+fallback";

export function useBillingLedgerRows() {
  const apiOn = isBillingLedgerApiEnabled();
  const [rows, setRows] = useState<MockBillingLedgerRow[]>(mockBillingLedger);
  const [source, setSource] = useState<BillingLedgerDataSource>(apiOn ? "remote" : "mock");
  const [loading, setLoading] = useState(apiOn);

  const reload = useCallback(async () => {
    if (!apiOn) {
      setRows(mockBillingLedger);
      setSource("mock");
      return;
    }
    setLoading(true);
    try {
      const remote = await searchAdminBillingTraces();
      setRows(remote.length > 0 ? remote : mockBillingLedger);
      setSource(remote.length > 0 ? "remote" : "remote+fallback");
    } catch {
      setRows(mockBillingLedger);
      setSource("remote+fallback");
    } finally {
      setLoading(false);
    }
  }, [apiOn]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const searchCorrelate = useCallback(
    async (raw: string): Promise<MockBillingLedgerRow[]> => {
      const q = raw.trim();
      if (!q) return [];
      if (!apiOn) {
        const lower = q.toLowerCase();
        return mockBillingLedger.filter(
          (r) =>
            r.billingTraceId.toLowerCase().includes(lower) ||
            r.executionId.toLowerCase().includes(lower) ||
            r.userIdMasked.toLowerCase().includes(lower),
        );
      }
      try {
        const params =
          /^[0-9]{10,19}$/.test(q.trim()) ? { executionId: q.trim() }
          : /^bt-/i.test(q) || q.includes("-") ? { billingTraceId: q }
          : q.startsWith("u-") ? { userId: q }
          : { executionId: q, billingTraceId: q };
        const hits = await searchAdminBillingTraces(params);
        return hits.length > 0 ? hits : mockBillingLedger.filter(
          (r) =>
            r.billingTraceId.toLowerCase().includes(q.toLowerCase()) ||
            r.executionId.toLowerCase().includes(q.toLowerCase()),
        );
      } catch {
        const lower = q.toLowerCase();
        return mockBillingLedger.filter(
          (r) =>
            r.billingTraceId.toLowerCase().includes(lower) ||
            r.executionId.toLowerCase().includes(lower),
        );
      }
    },
    [apiOn],
  );

  return { rows, source, loading, apiOn, reload, searchCorrelate };
}
