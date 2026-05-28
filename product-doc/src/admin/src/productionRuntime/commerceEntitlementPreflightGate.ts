/**
 * Phase 2 · 商业额度 · S2 门禁（纯函数小样，无 IO）
 *
 * **规格**：[`consume-and-bill.md`](../../../../specs/requirements/flows/consume-and-bill.md) **S2** ·
 * [`commerce-model.md`](../../../../specs/requirements/domains/admin/billing-management/commerce-model.md) **§4** ·
 * OpenAPI **`GET /api/v1/internal/billing/entitlements/balance`**
 * [`billing-entitlements.yaml`](../../../../specs/openapi/internal/billing-entitlements.yaml)。
 *
 * 所内在 `executionId` **accepted** 之前：由调用方 **`GET`** balance（或等价缓存）填入 **`remainingForSku`** 再裁决。
 * **`phase2CommerceRailsEnabled === false`** 时等价 **轨 B 未接线**，恒通过。
 */
export type CommerceEntitlementPreflightInput = {
  /** `false` = 轨 B 未启用（默认），不拦截 */
  phase2CommerceRailsEnabled: boolean;
  /**
   * 当前请求在商业策略下归类的 **Capability SKU**；未归类时为 `undefined`。
   * 真实现应与 **`BILLING_CAPABILITY_MAP`** 同窗；小样在启用轨 B 且无 SKU 时 **放行**（由所内 MR 收紧）。
   */
  capabilitySkuId: string | undefined;
  /**
   * 该 SKU 桶在 balance 视图中的 **`remaining`**；未查到桶时可 `undefined`。
   * 小样 **仅在** **`remaining !== undefined && remaining <= 0`** **时阻断**；
   * **「启用 + 已有 SKU + 无余额视图」** 由所内决定是否 **fail-closed**（本小样不冒充生产策略）。
   */
  remainingForSku: number | undefined;
};

export const COMMERCE_ENTITLEMENT_PREFLIGHT_BLOCK = "COMMERCE_ENTITLEMENT_EXHAUSTED" as const;

export type CommerceEntitlementPreflightBlocked = {
  ok: false;
  code: typeof COMMERCE_ENTITLEMENT_PREFLIGHT_BLOCK;
  capabilitySkuId: string;
};

export type CommerceEntitlementPreflightOk = { ok: true };

export type CommerceEntitlementPreflightResult =
  | CommerceEntitlementPreflightOk
  | CommerceEntitlementPreflightBlocked;

/**
 * **`FR-T05` / stableReason**：所内可归 **`BUDGET_OR_QUOTA`** 族（与同篇编排预算并列由 Taxonomy MR 冻结）。
 */
export function runCommerceEntitlementPreflight(
  input: CommerceEntitlementPreflightInput,
): CommerceEntitlementPreflightResult {
  if (!input.phase2CommerceRailsEnabled) return { ok: true };
  const sku = input.capabilitySkuId?.trim();
  if (!sku) return { ok: true };

  const rem = input.remainingForSku;
  if (rem !== undefined && rem <= 0) {
    return { ok: false, code: COMMERCE_ENTITLEMENT_PREFLIGHT_BLOCK, capabilitySkuId: sku };
  }
  return { ok: true };
}
