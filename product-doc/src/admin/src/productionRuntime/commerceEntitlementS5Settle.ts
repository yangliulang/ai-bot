/**
 * **`consume-and-bill` · S5** · **权益核销**（**`ENTITLEMENT_DEBIT`**）
 *
 * **规格**：[`commerce-model.md` §4](../../../../specs/requirements/domains/admin/billing-management/commerce-model.md) ·
 * **`SC-B20`** · **`FR-B21`**（**禁止 fallback Token 扣费**）。
 *
 * **`phase2CommerceRailsEnabled === false`** 或未传 **`entitlementDebit`** → **跳过 S5**（**所内 staged**）。
 */

import type { InternalEntitlementDebitResultBody } from "./internalBillingEntitlementsAdapter";
import {
  type BillingEntitlementsHttpDeps,
  postInternalBillingEntitlementsDebit,
} from "./internalBillingEntitlementsAdapter";

/** 与 runtime **FR-B05** 同窗：键 **绑定** **`executionId`** */
export const RAIL_B_DEBIT_IDEMPOTENCY_SUFFIX = ":rail-b:entitlement-debit" as const;

export function deriveEntitlementDebitIdempotencyKey(executionId: string): string {
  return `${executionId}${RAIL_B_DEBIT_IDEMPOTENCY_SUFFIX}`;
}

export type EntitlementDebitLegInput = {
  capabilitySkuId: string;
  packGrantId?: string;
  /** 默认 **`deriveEntitlementDebitIdempotencyKey(executionId)`** */
  idempotencyKey?: string;
};

export type ExecuteConsumptionSettlementInput = {
  phase2CommerceRailsEnabled: boolean;
  executionId: string;
  entitlementDebit?: EntitlementDebitLegInput;
};

export type ExecuteConsumptionSettlementResult = {
  entitlementDebit?: InternalEntitlementDebitResultBody;
};

export const CONSUMPTION_SETTLEMENT_ENTITLEMENT_INSUFFICIENT =
  "CONSUMPTION_SETTLEMENT_ENTITLEMENT_INSUFFICIENT" as const;

export type ConsumptionSettlementEntitlementInsufficient = {
  ok: false;
  code: typeof CONSUMPTION_SETTLEMENT_ENTITLEMENT_INSUFFICIENT;
  executionId: string;
  capabilitySkuId: string;
  debitResult: InternalEntitlementDebitResultBody;
};

export type ConsumptionSettlementOk = {
  ok: true;
  result: ExecuteConsumptionSettlementResult;
};

export type ExecuteConsumptionSettlementOutcome =
  | ConsumptionSettlementOk
  | ConsumptionSettlementEntitlementInsufficient;

export async function executeConsumptionSettlement(
  deps: BillingEntitlementsHttpDeps,
  input: ExecuteConsumptionSettlementInput,
): Promise<ExecuteConsumptionSettlementOutcome> {
  const result: ExecuteConsumptionSettlementResult = {};
  const { executionId } = input;

  if (input.phase2CommerceRailsEnabled && input.entitlementDebit) {
    const leg = input.entitlementDebit;
    const debitResult = await postInternalBillingEntitlementsDebit(deps, {
      executionId,
      idempotencyKey:
        leg.idempotencyKey ?? deriveEntitlementDebitIdempotencyKey(executionId),
      capabilitySkuId: leg.capabilitySkuId,
      packGrantId: leg.packGrantId,
    });
    result.entitlementDebit = debitResult;

    if (debitResult.status === "INSUFFICIENT") {
      return {
        ok: false,
        code: CONSUMPTION_SETTLEMENT_ENTITLEMENT_INSUFFICIENT,
        executionId,
        capabilitySkuId: leg.capabilitySkuId,
        debitResult,
      };
    }
  }

  return { ok: true, result };
}
