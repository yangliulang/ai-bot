import { useCallback, useState } from "react";
import { NUMERIC_RESOURCE_ID, normalizeResourceId } from "../data/resourcePackLegacy";
import { RESOURCE_PACK_SEED } from "../data/subscriptionCatalogMock";
import type { MockCommerceResourcePack } from "../data/types";

const STORAGE_KEY = "coobit-admin-resource-packs-v2";

function normalizePack(raw: unknown): MockCommerceResourcePack | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const idRaw =
    typeof o.resourceId === "string"
      ? o.resourceId
      : typeof o.sku === "string"
        ? o.sku
        : null;
  if (!idRaw) return null;
  const resourceId = normalizeResourceId(idRaw);
  if (!NUMERIC_RESOURCE_ID.test(resourceId)) return null;
  if (typeof o.name !== "string" || typeof o.capabilitySkuId !== "string") return null;
  return {
    resourceId,
    name: o.name,
    capabilitySkuId: o.capabilitySkuId,
    quotaUnits: Number(o.quotaUnits) || 0,
    periodLabel: String(o.periodLabel ?? "月"),
    packKind: o.packKind === "addon" ? "addon" : "subscription",
    priceUsdt: typeof o.priceUsdt === "string" ? o.priceUsdt : undefined,
    active: o.active !== false,
    description: typeof o.description === "string" ? o.description : undefined,
    createdAt:
      typeof o.createdAt === "string"
        ? o.createdAt
        : typeof o.updatedAt === "string"
          ? o.updatedAt
          : undefined,
    updatedAt: typeof o.updatedAt === "string" ? o.updatedAt : undefined,
  };
}

function loadFromStorage(): MockCommerceResourcePack[] {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as unknown[];
      if (Array.isArray(parsed) && parsed.length > 0) {
        const packs = parsed.map(normalizePack).filter((p): p is MockCommerceResourcePack => !!p);
        if (packs.length > 0) return packs;
      }
    }
  } catch {
    /* seed */
  }
  return RESOURCE_PACK_SEED.map((p) => ({ ...p }));
}

function persist(packs: MockCommerceResourcePack[]) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(packs));
}

export function useResourcePacks() {
  const [packs, setPacksState] = useState<MockCommerceResourcePack[]>(loadFromStorage);

  const setPacks = useCallback((next: MockCommerceResourcePack[]) => {
    setPacksState(next);
    persist(next);
  }, []);

  const upsertPack = useCallback((pack: MockCommerceResourcePack) => {
    const now = new Date().toISOString();
    setPacksState((prev) => {
      const idx = prev.findIndex((p) => p.resourceId === pack.resourceId);
      const existing = idx >= 0 ? prev[idx] : null;
      const withMeta: MockCommerceResourcePack = {
        ...pack,
        createdAt: existing?.createdAt ?? pack.createdAt ?? now,
        updatedAt: now,
      };
      const next = idx >= 0 ? prev.map((p, i) => (i === idx ? withMeta : p)) : [...prev, withMeta];
      persist(next);
      return next;
    });
  }, []);

  const deletePack = useCallback((resourceId: string) => {
    setPacksState((prev) => {
      const next = prev.filter((p) => p.resourceId !== resourceId);
      persist(next);
      return next;
    });
  }, []);

  const resetToSeed = useCallback(() => {
    const next = RESOURCE_PACK_SEED.map((p) => ({ ...p }));
    setPacks(next);
  }, [setPacks]);

  return { packs, upsertPack, deletePack, resetToSeed };
}
