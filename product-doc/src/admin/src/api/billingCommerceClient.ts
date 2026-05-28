/**
 * `admin/billing-admin.yaml` · commerce_phase2（FR-MC509～512）
 * 需 `VITE_API_BASE_URL` + `VITE_USE_BILLING_COMMERCE_API=true`。
 */
import { apiFetch, getApiBaseUrl } from "./http";
import type { MockCommercePhase2AdminSnapshot, MockCommerceUserSubscription } from "../data/types";

export function isBillingCommerceApiEnabled(): boolean {
  return import.meta.env.VITE_USE_BILLING_COMMERCE_API === "true" && !!getApiBaseUrl();
}

export type AdminCommerceCapabilityCatalogJson = {
  catalogVersion?: string;
  items?: Array<{
    capabilitySkuId?: string;
    displayLabel?: string;
    remaining?: number;
    resetsAt?: string | null;
    [key: string]: unknown;
  }>;
};

export type AdminCommerceQuotaBlockedSummaryJson = {
  window?: string;
  blockedEventCountByCapability?: Record<string, number>;
  topUsersSample?: Array<{ userId?: string; userIdMasked?: string; blockCount?: number }>;
};

export type AdminCommerceUserOverviewJson = {
  userId?: string;
  subscriptions?: Array<{
    displayLabel?: string;
    tierDisplay?: string;
    tierSku?: string;
    status?: string;
    periodEnd?: string | null;
    [key: string]: unknown;
  }>;
  packGrants?: Array<{
    capabilitySkuId?: string;
    displayLabel?: string;
    remaining?: number;
    resetsAt?: string | null;
    [key: string]: unknown;
  }>;
  recentExecutionAnchorsSample?: string[];
};

export function mapCatalogAndQuotaToSnapshot(
  catalog: AdminCommerceCapabilityCatalogJson,
  quota: AdminCommerceQuotaBlockedSummaryJson,
): MockCommercePhase2AdminSnapshot {
  const buckets =
    catalog.items?.map((item) => ({
      capabilitySkuId: String(item.capabilitySkuId ?? ""),
      displayLabel: String(item.displayLabel ?? item.capabilitySkuId ?? "—"),
      remaining: typeof item.remaining === "number" ? item.remaining : 0,
      quotaTotal: typeof item.quotaTotal === "number" ? item.quotaTotal : undefined,
      debitUnitsPerExecution:
        typeof item.debitUnitsPerExecution === "number" ? item.debitUnitsPerExecution : 1,
      resetsAt: item.resetsAt ?? null,
    })) ?? [];

  const topUsers =
    quota.topUsersSample?.map((u) => ({
      userIdMasked: String(u.userId ?? u.userIdMasked ?? ""),
      blockCount: typeof u.blockCount === "number" ? u.blockCount : 0,
    })) ?? [];

  return {
    phase2RailsEnabled: true,
    catalogVersion: catalog.catalogVersion ?? "api",
    capabilityBuckets: buckets,
    quotaBlockedSummary: {
      window: quota.window ?? "—",
      blockedEventCountByCapability: quota.blockedEventCountByCapability ?? {},
      topUsersSample: topUsers,
    },
  };
}

export function mapUserOverviewToBucketRows(overview: AdminCommerceUserOverviewJson) {
  const fromPacks =
    overview.packGrants?.map((p) => ({
      capabilitySkuId: String(p.capabilitySkuId ?? ""),
      displayLabel: String(p.displayLabel ?? p.capabilitySkuId ?? "—"),
      remaining: typeof p.remaining === "number" ? p.remaining : 0,
      resetsAt: p.resetsAt ?? null,
    })) ?? [];

  if (fromPacks.length > 0) return fromPacks;

  return (
    overview.subscriptions?.map((s, i) => ({
      capabilitySkuId: `subscription.${i}`,
      displayLabel: String(s.displayLabel ?? s.tierDisplay ?? "订阅"),
      remaining: 0,
      resetsAt: null,
    })) ?? []
  );
}

export async function fetchCommerceAdminSnapshot(): Promise<MockCommercePhase2AdminSnapshot> {
  const [catalog, quota] = await Promise.all([
    apiFetch<AdminCommerceCapabilityCatalogJson>("/api/v1/admin/billing/commerce/capability-catalog"),
    apiFetch<AdminCommerceQuotaBlockedSummaryJson>(
      "/api/v1/admin/billing/commerce/quota-blocked-summary",
    ),
  ]);
  return mapCatalogAndQuotaToSnapshot(catalog, quota);
}

export async function patchAdminBillingCommerceCapabilityCatalog(
  body: AdminCommerceCapabilityCatalogJson,
  opts?: { ifMatch?: string },
): Promise<AdminCommerceCapabilityCatalogJson> {
  const headers: Record<string, string> = {};
  if (opts?.ifMatch?.trim()) {
    headers["If-Match"] = opts.ifMatch.trim();
  }
  return apiFetch<AdminCommerceCapabilityCatalogJson>(
    "/api/v1/admin/billing/commerce/capability-catalog",
    { method: "PATCH", headers, body: JSON.stringify(body) },
  );
}

export function mapUserSubscription(
  overview: AdminCommerceUserOverviewJson,
): MockCommerceUserSubscription | null {
  const sub = overview.subscriptions?.[0];
  if (!sub) return null;
  const status = String(sub.status ?? "active");
  const normalized =
    status === "active" || status === "expired" || status === "none" ? status : "active";
  return {
    tierDisplay: String(sub.tierDisplay ?? sub.displayLabel ?? "—"),
    tierSku: String(sub.tierSku ?? ""),
    status: normalized,
    periodEnd: sub.periodEnd ?? null,
  };
}

export async function fetchCommerceUserOverview(userId: string): Promise<{
  rows: ReturnType<typeof mapUserOverviewToBucketRows>;
  executionAnchors: string[];
  subscription: MockCommerceUserSubscription | null;
}> {
  const overview = await apiFetch<AdminCommerceUserOverviewJson>(
    `/api/v1/admin/billing/commerce/users/${encodeURIComponent(userId.trim())}/overview`,
  );
  return {
    rows: mapUserOverviewToBucketRows(overview),
    executionAnchors: overview.recentExecutionAnchorsSample ?? [],
    subscription: mapUserSubscription(overview),
  };
}
