import { getAgentApiBase } from "./meAgent";
import type { MeCommerceEntitlementsSummary } from "@/data/meCommerceMock";
import type { MeCommerceConsumptionRow } from "@/data/meCommerceConsumptionMock";
import { isExecutionId } from "@/lib/executionId";

export function isMeCommerceApiEnabled(): boolean {
  return import.meta.env.VITE_USE_ME_COMMERCE_API === "true" && !!getAgentApiBase();
}

export type MeCommerceConsumptionsListJson = {
  items?: MeCommerceConsumptionRow[];
  nextCursor?: string | null;
};

function pickExecutionId(raw: Record<string, unknown>): string {
  for (const candidate of [raw.executionId, raw.executionRef]) {
    const s = String(candidate ?? "").trim();
    if (isExecutionId(s)) return s;
  }
  return "";
}

export function mapConsumptionItem(raw: Record<string, unknown>): MeCommerceConsumptionRow {
  const executionId = pickExecutionId(raw);
  const billingTraceId = String(raw.billingTraceId ?? "");
  return {
    key: String(raw.key ?? (billingTraceId || executionId || `row-${Math.random()}`)),
    time: String(raw.time ?? raw.recordedAt ?? ""),
    sceneType: String(raw.sceneType ?? "分析") as MeCommerceConsumptionRow["sceneType"],
    capabilitySkuId: String(raw.capabilitySkuId ?? "cap.agent.trade"),
    debitStatus: String(raw.debitStatus ?? "AWAITING_FINAL") as MeCommerceConsumptionRow["debitStatus"],
    consumedUnits: typeof raw.consumedUnits === "number" ? raw.consumedUnits : undefined,
    tokens: typeof raw.tokens === "number" ? raw.tokens : undefined,
    executionId,
    billingTraceId,
  };
}

async function commerceGetJson<T>(path: string): Promise<T> {
  const base = getAgentApiBase();
  const res = await fetch(`${base}${path}`, {
    credentials: "include",
    headers: { Accept: "application/json" },
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(text || `HTTP ${res.status}`);
  }
  return JSON.parse(text) as T;
}

export async function fetchMeCommerceConsumptions(
  cursor?: string,
  pageSize = 10,
): Promise<{ items: MeCommerceConsumptionRow[]; nextCursor: string | null }> {
  const params = new URLSearchParams({ pageSize: String(pageSize) });
  if (cursor) params.set("cursor", cursor);
  const body = await commerceGetJson<MeCommerceConsumptionsListJson>(
    `/api/v1/me/commerce/consumptions?${params}`,
  );
  return {
    items: (body.items ?? []).map((row) => mapConsumptionItem(row as Record<string, unknown>)),
    nextCursor: body.nextCursor ?? null,
  };
}

export async function fetchMeCommerceEntitlementsSummary(): Promise<MeCommerceEntitlementsSummary> {
  return commerceGetJson<MeCommerceEntitlementsSummary>(
    "/api/v1/me/commerce/entitlements/summary",
  );
}
