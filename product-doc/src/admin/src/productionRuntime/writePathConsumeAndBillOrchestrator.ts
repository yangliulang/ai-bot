/**
 * **可计费写路径 · S2 → S5 编排对照**（**MR-RT-B4 × MR-BILL-B1/B2** 同窗接线）
 *
 * **规格**：[`consume-and-bill.md`](../../../../specs/requirements/flows/consume-and-bill.md) **S2/S5** ·
 * [`commerce-model.md` §5.3](../../../../specs/requirements/domains/admin/billing-management/commerce-model.md)。
 *
 * 所内 Runtime：**FR-T02 序内** 调 **S2**；**S4 终局后** 调 **S5**（**ENTITLEMENT_ONLY**）。
 */

import { CONSUMPTION_SETTLEMENT_ENTITLEMENT_INSUFFICIENT } from "./commerceEntitlementS5Settle";
import {
  type ConsumptionBillingHostConfig,
  runConsumeAndBillS2CommerceGate,
  runConsumeAndBillS5Settlement,
  type RunConsumeAndBillS2Blocked,
} from "./consumptionBillingHost";
import { BillingEntitlementsHttpError } from "./internalBillingEntitlementsAdapter";

export const COMMERCE_ENTITLEMENT_BALANCE_HTTP_ERROR =
  "COMMERCE_ENTITLEMENT_BALANCE_HTTP_ERROR" as const;

export type WritePathConsumeAndBillInput = {
  userId: string;
  scenarioId: string;
  executionId: string;
  packGrantId?: string;
};

export type WritePathConsumeAndBillBlockedS2Http = {
  ok: false;
  stage: "S2";
  code: typeof COMMERCE_ENTITLEMENT_BALANCE_HTTP_ERROR;
  stableReason: "BUDGET_OR_QUOTA";
  httpStatus: number;
};

export type WritePathConsumeAndBillBlockedS2 =
  | RunConsumeAndBillS2Blocked
  | WritePathConsumeAndBillBlockedS2Http;

export type WritePathConsumeAndBillBlockedS5 = {
  ok: false;
  stage: "S5";
  code: typeof CONSUMPTION_SETTLEMENT_ENTITLEMENT_INSUFFICIENT;
  executionId: string;
  capabilitySkuId: string;
};

export type WritePathConsumeAndBillOk = {
  ok: true;
  executionId: string;
  /** 轨 B 关或未映射 SKU 时为空串（所内 staged · 不发 debit） */
  billingTraceId: string;
  commercialSettlementType: "ENTITLEMENT_DEBIT";
  railsSkipped: boolean;
};

export type WritePathConsumeAndBillOutcome =
  | WritePathConsumeAndBillOk
  | WritePathConsumeAndBillBlockedS2
  | WritePathConsumeAndBillBlockedS5;

/**
 * **一键**：S2 额度门禁 → S5 **`ENTITLEMENT_DEBIT`**
 */
export async function runWritePathConsumeAndBill(
  config: ConsumptionBillingHostConfig,
  input: WritePathConsumeAndBillInput,
): Promise<WritePathConsumeAndBillOutcome> {
  let s2;
  try {
    s2 = await runConsumeAndBillS2CommerceGate(config, {
      userId: input.userId,
      scenarioId: input.scenarioId,
    });
  } catch (e) {
    if (e instanceof BillingEntitlementsHttpError) {
      return {
        ok: false,
        stage: "S2",
        code: COMMERCE_ENTITLEMENT_BALANCE_HTTP_ERROR,
        stableReason: "BUDGET_OR_QUOTA",
        httpStatus: e.status,
      };
    }
    throw e;
  }

  if (!s2.ok) return s2;

  const s5 = await runConsumeAndBillS5Settlement(config, {
    executionId: input.executionId,
    scenarioId: input.scenarioId,
    packGrantId: input.packGrantId,
  });

  if (!s5.ok) {
    return {
      ok: false,
      stage: "S5",
      code: s5.code,
      executionId: s5.executionId,
      capabilitySkuId: s5.capabilitySkuId,
    };
  }

  const debit = s5.result.entitlementDebit;
  const railsSkipped =
    !config.phase2CommerceRailsEnabled || debit === undefined;

  return {
    ok: true,
    executionId: input.executionId,
    billingTraceId: debit?.billingTraceId ?? "",
    commercialSettlementType: "ENTITLEMENT_DEBIT",
    railsSkipped,
  };
}
