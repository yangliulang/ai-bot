import { resolveCapabilitySkuForScenario } from "../productionRuntime/billingCapabilityMap";
import type { MockBillingLedgerRow, MockObsBillingRow } from "./types";

type Seed = {
  recordedAt: string;
  billingTraceId: string;
  userIdMasked: string;
  executionId: string;
  scenarioId: string;
  requestId?: string;
  intentType: string;
  executionStatus: string;
  debitStatus: MockBillingLedgerRow["debitStatus"];
  failureReason: MockBillingLedgerRow["failureReason"];
  consumedUnits?: number;
  idempotencyKeySuffix: string;
};

const SEEDS: Seed[] = [
  {
    recordedAt: "2026-05-07T01:18:22Z",
    billingTraceId: "bt-7f2a-001",
    userIdMasked: "u-10482",
    executionId: "20260501001001",
    scenarioId: "trade.spot.limit_order",
    requestId: "req-7f2a-001",
    intentType: "交易",
    executionStatus: "COMPLETED",
    debitStatus: "SUCCESS",
    failureReason: "none",
    consumedUnits: 1,
    idempotencyKeySuffix: ":rail-b:entitlement-debit",
  },
  {
    recordedAt: "2026-05-06T18:41:05Z",
    billingTraceId: "bt-883-fail",
    userIdMasked: "u-88301",
    executionId: "20260501002002",
    scenarioId: "trade.spot.limit_order",
    requestId: "req-883-x",
    intentType: "交易",
    executionStatus: "BLOCKED",
    debitStatus: "INSUFFICIENT",
    failureReason: "quota",
    idempotencyKeySuffix: ":rail-b:entitlement-debit",
  },
  {
    recordedAt: "2026-05-07T02:05:48Z",
    billingTraceId: "bt-recon-pending-9",
    userIdMasked: "u-10482",
    executionId: "20260501003099",
    scenarioId: "trade.spot.flash_convert",
    intentType: "交易",
    executionStatus: "UNKNOWN",
    debitStatus: "AWAITING_FINAL",
    failureReason: "policy",
    idempotencyKeySuffix: ":rail-b:entitlement-debit",
  },
  {
    recordedAt: "2026-05-07T00:30:02Z",
    billingTraceId: "bt-no-settlement",
    userIdMasked: "u-22001",
    executionId: "20260501004001",
    scenarioId: "trade.futures.market_order",
    intentType: "交易",
    executionStatus: "FAILED",
    debitStatus: "AWAITING_FINAL",
    failureReason: "not_applicable",
    idempotencyKeySuffix: ":rail-b:entitlement-debit",
  },
  {
    recordedAt: "2026-05-07T02:10:10Z",
    billingTraceId: "bt-inflight-open",
    userIdMasked: "u-10482",
    executionId: "20260501005001",
    scenarioId: "trade.spot.limit_order",
    intentType: "交易",
    executionStatus: "RUNNING",
    debitStatus: "AWAITING_FINAL",
    failureReason: "policy",
    idempotencyKeySuffix: ":rail-b:entitlement-debit",
  },
  {
    recordedAt: "2026-05-07T03:12:00Z",
    billingTraceId: "bt-demo-050",
    userIdMasked: "u-29119",
    executionId: "20260501100050",
    scenarioId: "trade.spot.limit_order",
    intentType: "交易",
    executionStatus: "COMPLETED",
    debitStatus: "SUCCESS",
    failureReason: "none",
    consumedUnits: 1,
    idempotencyKeySuffix: ":rail-b:entitlement-debit",
  },
  {
    recordedAt: "2026-05-06T14:22:11Z",
    billingTraceId: "bt-gw-09x",
    userIdMasked: "u-22001",
    executionId: "20260501050052",
    scenarioId: "trade.spot.flash_convert",
    intentType: "交易",
    executionStatus: "COMPLETED",
    debitStatus: "FAILED",
    failureReason: "gateway",
    idempotencyKeySuffix: ":rail-b:entitlement-debit",
  },
];

function toLedgerRow(s: Seed): MockBillingLedgerRow {
  const capabilitySkuId =
    resolveCapabilitySkuForScenario(s.scenarioId) ?? "cap.agent.trade";
  return {
    recordedAt: s.recordedAt,
    billingTraceId: s.billingTraceId,
    userIdMasked: s.userIdMasked,
    executionId: s.executionId,
    capabilitySkuId,
    commercialSettlementType: "ENTITLEMENT_DEBIT",
    debitStatus: s.debitStatus,
    failureReason: s.failureReason,
    consumedUnits: s.consumedUnits,
    idempotencyKeySuffix: s.idempotencyKeySuffix,
    requestId: s.requestId,
    intentType: s.intentType,
    executionStatus: s.executionStatus,
  };
}

function toObsRow(s: Seed): MockObsBillingRow {
  const capabilitySkuId =
    resolveCapabilitySkuForScenario(s.scenarioId) ?? "cap.agent.trade";
  return {
    executionId: s.executionId,
    billingTraceId: s.billingTraceId,
    capabilitySkuId,
    commercialSettlementType: "ENTITLEMENT_DEBIT",
    debitStatus: s.debitStatus,
    failureReason: s.failureReason,
    consumedUnits: s.consumedUnits,
    idempotencyKeySuffix: s.idempotencyKeySuffix,
    at: s.recordedAt,
  };
}

export const mockBillingLedger: MockBillingLedgerRow[] = SEEDS.map(toLedgerRow);
export const mockObsBilling: MockObsBillingRow[] = SEEDS.map(toObsRow);

/** Demo：单笔追踪 · 匹配 execution / trace / user / capability / 幂等后缀 */
export function lookupBillingCorrelate(raw: string): MockBillingLedgerRow[] {
  const q = raw.trim().toLowerCase();
  if (!q) return [];
  return mockBillingLedger.filter(
    (r) =>
      r.billingTraceId.toLowerCase().includes(q) ||
      r.executionId.toLowerCase().includes(q) ||
      r.userIdMasked.toLowerCase().includes(q) ||
      r.capabilitySkuId.toLowerCase().includes(q) ||
      r.idempotencyKeySuffix.toLowerCase().includes(q) ||
      (r.requestId?.toLowerCase().includes(q) ?? false),
  );
}
