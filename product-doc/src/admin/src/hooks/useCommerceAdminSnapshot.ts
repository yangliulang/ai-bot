import { useCallback, useEffect, useState } from "react";
import {
  fetchCommerceAdminSnapshot,
  fetchCommerceUserOverview,
  isBillingCommerceApiEnabled,
} from "../api/billingCommerceClient";
import { mockCommercePhase2AdminSnapshot } from "../data/mock";
import type { MockCommercePhase2AdminSnapshot, MockCommerceUserSubscription } from "../data/types";

export type CommerceDataSource = "mock" | "remote" | "remote+fallback";

export function useCommerceAdminSnapshot() {
  const apiOn = isBillingCommerceApiEnabled();
  const [snapshot, setSnapshot] = useState<MockCommercePhase2AdminSnapshot>(
    mockCommercePhase2AdminSnapshot,
  );
  const [source, setSource] = useState<CommerceDataSource>(apiOn ? "remote" : "mock");
  const [loading, setLoading] = useState(apiOn);

  const reload = useCallback(async () => {
    if (!apiOn) {
      setSnapshot(mockCommercePhase2AdminSnapshot);
      setSource("mock");
      return;
    }
    setLoading(true);
    try {
      const remote = await fetchCommerceAdminSnapshot();
      setSnapshot(remote);
      setSource("remote");
    } catch {
      setSnapshot(mockCommercePhase2AdminSnapshot);
      setSource("remote+fallback");
    } finally {
      setLoading(false);
    }
  }, [apiOn]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { snapshot, source, loading, apiOn, reload };
}

const DEMO_USER_SUBSCRIPTION: MockCommerceUserSubscription = {
  tierDisplay: "Pro",
  tierSku: "1002",
  status: "active",
  periodEnd: "2026-06-01T00:00:00Z",
};

export function useCommerceUserOverview(userId: string, apiOn: boolean) {
  const [rows, setRows] = useState(() =>
    mockCommercePhase2AdminSnapshot.capabilityBuckets.map((b) => ({ ...b, key: b.capabilitySkuId })),
  );
  const [executionAnchors, setExecutionAnchors] = useState<string[]>([]);
  const [subscription, setSubscription] = useState<MockCommerceUserSubscription | null>(DEMO_USER_SUBSCRIPTION);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const id = userId.trim();
    if (!id) {
      setRows([]);
      setExecutionAnchors([]);
      setSubscription(null);
      return;
    }

    if (!apiOn) {
      setRows(
        mockCommercePhase2AdminSnapshot.capabilityBuckets.map((b) => ({
          ...b,
          key: b.capabilitySkuId,
        })),
      );
      setExecutionAnchors([]);
      setSubscription(DEMO_USER_SUBSCRIPTION);
      return;
    }

    let cancelled = false;
    setLoading(true);
    void fetchCommerceUserOverview(id)
      .then(({ rows: r, executionAnchors: anchors, subscription: sub }) => {
        if (cancelled) return;
        setRows(r.map((b) => ({ ...b, key: b.capabilitySkuId })));
        setExecutionAnchors(anchors);
        setSubscription(sub);
      })
      .catch(() => {
        if (cancelled) return;
        setRows(
          mockCommercePhase2AdminSnapshot.capabilityBuckets.map((b) => ({
            ...b,
            key: b.capabilitySkuId,
          })),
        );
        setExecutionAnchors([]);
        setSubscription(DEMO_USER_SUBSCRIPTION);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [userId, apiOn]);

  return { rows, executionAnchors, subscription, loading };
}
