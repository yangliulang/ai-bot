import { useCallback, useState } from "react";
import { normalizeResourceId } from "../data/resourcePackLegacy";
import { SUBSCRIPTION_TIER_SEED } from "../data/subscriptionCatalogMock";
import type { MockCommerceSubscriptionTier } from "../data/types";

const STORAGE_KEY = "coobit-admin-subscription-tiers-v5";

const NUMERIC_TIER_ID = /^\d+$/;

function normalizeTier(raw: unknown): MockCommerceSubscriptionTier | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const tierId =
    typeof o.tierId === "string" ? o.tierId : typeof o.sku === "string" ? o.sku : null;
  const packIdsRaw = Array.isArray(o.resourcePackIds)
    ? o.resourcePackIds
    : Array.isArray(o.resourcePackSkus)
      ? o.resourcePackSkus
      : null;
  if (!tierId || !NUMERIC_TIER_ID.test(tierId) || !packIdsRaw) return null;
  return {
    tierId,
    name: String(o.name ?? ""),
    tagline: String(o.tagline ?? ""),
    priceUsdt: String(o.priceUsdt ?? ""),
    periodLabel: String(o.periodLabel ?? "月"),
    resourcePackIds: (packIdsRaw as string[]).map((id) => normalizeResourceId(id)),
    highlights: Array.isArray(o.highlights) ? (o.highlights as string[]) : [],
    recommended: Boolean(o.recommended),
    active: o.active !== false,
    internalNote: typeof o.internalNote === "string" ? o.internalNote : undefined,
    createdAt:
      typeof o.createdAt === "string"
        ? o.createdAt
        : typeof o.updatedAt === "string"
          ? o.updatedAt
          : undefined,
    updatedAt: typeof o.updatedAt === "string" ? o.updatedAt : undefined,
  };
}

function loadFromStorage(): MockCommerceSubscriptionTier[] {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as unknown[];
      if (Array.isArray(parsed) && parsed.length > 0) {
        const tiers = parsed.map(normalizeTier).filter((t): t is MockCommerceSubscriptionTier => !!t);
        if (tiers.length > 0) return tiers;
      }
    }
  } catch {
    /* seed */
  }
  return SUBSCRIPTION_TIER_SEED.map((t) => ({ ...t }));
}

function persist(tiers: MockCommerceSubscriptionTier[]) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(tiers));
}

export function useSubscriptionTiers() {
  const [tiers, setTiersState] = useState<MockCommerceSubscriptionTier[]>(loadFromStorage);

  const setTiers = useCallback((next: MockCommerceSubscriptionTier[]) => {
    setTiersState(next);
    persist(next);
  }, []);

  const upsertTier = useCallback((tier: MockCommerceSubscriptionTier) => {
    const now = new Date().toISOString();
    setTiersState((prev) => {
      const idx = prev.findIndex((t) => t.tierId === tier.tierId);
      const existing = idx >= 0 ? prev[idx] : null;
      const withMeta: MockCommerceSubscriptionTier = {
        ...tier,
        createdAt: existing?.createdAt ?? tier.createdAt ?? now,
        updatedAt: now,
      };
      const next = idx >= 0 ? prev.map((t, i) => (i === idx ? withMeta : t)) : [...prev, withMeta];
      persist(next);
      return next;
    });
  }, []);

  const deleteTier = useCallback((tierId: string) => {
    setTiersState((prev) => {
      const next = prev.filter((t) => t.tierId !== tierId);
      persist(next);
      return next;
    });
  }, []);

  const resetToSeed = useCallback(() => {
    const next = SUBSCRIPTION_TIER_SEED.map((t) => ({ ...t }));
    setTiers(next);
  }, [setTiers]);

  return { tiers, upsertTier, deleteTier, resetToSeed };
}
