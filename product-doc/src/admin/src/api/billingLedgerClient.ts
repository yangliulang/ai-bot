/**
 * `admin/billing-admin.yaml` · `searchAdminBillingTraces` / `getAdminBillingTrace`（FR-MC503/504）
 */
import { apiFetch, getApiBaseUrl } from "./http";
import type { MockBillingLedgerRow } from "../data/types";

export function isBillingLedgerApiEnabled(): boolean {
  return import.meta.env.VITE_USE_BILLING_LEDGER_API === "true" && !!getApiBaseUrl();
}

export type AdminBillingTracesListJson = {
  items?: Array<Record<string, unknown>>;
};

export type SearchBillingTracesParams = {
  userId?: string;
  executionId?: string;
  billingTraceId?: string;
};

export function mapBillingTraceItemToLedgerRow(raw: Record<string, unknown>): MockBillingLedgerRow {
  return {
    recordedAt: String(raw.recordedAt ?? raw.at ?? ""),
    billingTraceId: String(raw.billingTraceId ?? ""),
    userIdMasked: String(raw.userIdMasked ?? raw.userId ?? ""),
    executionId: String(raw.executionId ?? ""),
    capabilitySkuId: String(raw.capabilitySkuId ?? "cap.agent.trade"),
    commercialSettlementType: "ENTITLEMENT_DEBIT",
    debitStatus: (raw.debitStatus ?? "AWAITING_FINAL") as MockBillingLedgerRow["debitStatus"],
    failureReason: (raw.failureReason ?? "none") as MockBillingLedgerRow["failureReason"],
    consumedUnits: typeof raw.consumedUnits === "number" ? raw.consumedUnits : undefined,
    idempotencyKeySuffix: String(raw.idempotencyKeySuffix ?? ":rail-b:entitlement-debit"),
    requestId: raw.requestId != null ? String(raw.requestId) : undefined,
    intentType: String(raw.intentType ?? "—"),
    executionStatus: String(raw.executionStatus ?? "—"),
    packGrantId: raw.packGrantId != null ? String(raw.packGrantId) : undefined,
  };
}

export async function searchAdminBillingTraces(
  params: SearchBillingTracesParams = {},
): Promise<MockBillingLedgerRow[]> {
  const q = new URLSearchParams();
  if (params.userId?.trim()) q.set("userId", params.userId.trim());
  if (params.executionId?.trim()) q.set("executionId", params.executionId.trim());
  if (params.billingTraceId?.trim()) q.set("billingTraceId", params.billingTraceId.trim());
  const qs = q.toString();
  const path = `/api/v1/admin/billing/traces${qs ? `?${qs}` : ""}`;
  const body = await apiFetch<AdminBillingTracesListJson>(path);
  return (body.items ?? []).map(mapBillingTraceItemToLedgerRow);
}
