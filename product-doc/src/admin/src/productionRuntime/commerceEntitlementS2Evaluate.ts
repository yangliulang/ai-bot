/**
 * **`consume-and-bill` · S2** · **一键**：`GET balance` → **`remaining`** → **`runCommerceEntitlementPreflight`**
 *
 * **规格**：[`consume-and-bill.md`](../../../../specs/requirements/flows/consume-and-bill.md) ·
 * [`billing-entitlements.yaml`](../../../../specs/openapi/internal/billing-entitlements.yaml)。
 *
 * **网络/DNS/5xx**：**透传** **`BillingEntitlementsHttpError`**，由宿主映射 **`FR-T05`** / **`stableReason`**（所内 MR）。
 */

import type { CommerceEntitlementPreflightResult } from "./commerceEntitlementPreflightGate";
import { runCommerceEntitlementPreflight } from "./commerceEntitlementPreflightGate";
import {
  type BillingEntitlementsHttpDeps,
  getInternalBillingEntitlementsBalance,
  pickRemainingForCapabilitySku,
} from "./internalBillingEntitlementsAdapter";

export type EvaluateCommerceEntitlementS2GateInput = {
  /** `false` 时不发 HTTP，恒 `{ ok: true }` */
  phase2CommerceRailsEnabled: boolean;
  userId: string;
  capabilitySkuId: string | undefined;
};

/** `operationId`: **串联** **`getInternalBillingEntitlementsBalance`** + **`runCommerceEntitlementPreflight`** */
export async function evaluateCommerceEntitlementS2Gate(
  deps: BillingEntitlementsHttpDeps,
  input: EvaluateCommerceEntitlementS2GateInput,
): Promise<CommerceEntitlementPreflightResult> {
  if (!input.phase2CommerceRailsEnabled) return { ok: true };

  const balance = await getInternalBillingEntitlementsBalance(deps, {
    userId: input.userId,
  });

  const sku = input.capabilitySkuId?.trim();
  const remaining =
    sku && sku.length > 0 ? pickRemainingForCapabilitySku(balance, sku) : undefined;

  return runCommerceEntitlementPreflight({
    phase2CommerceRailsEnabled: true,
    capabilitySkuId: input.capabilitySkuId,
    remainingForSku: remaining,
  });
}
