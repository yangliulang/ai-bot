/**
 * **`consume-and-bill` · S2 / S5 宿主接线**（MR-BILL-B1 / MR-BILL-B2 对照小样）
 *
 * **规格**：[`consume-and-bill.md`](../../../../specs/requirements/flows/consume-and-bill.md) ·
 * [`commerce-model.md` §4～§5.1](../../../../specs/requirements/domains/admin/billing-management/commerce-model.md)。
 *
 * 所内 Runtime/BFF：**在 FR-T02 序内** 调 **`runConsumeAndBillS2CommerceGate`**；
 * **S4 终局后** 调 **`runConsumeAndBillS5Settlement`**。
 */

import {
  type BillingCapabilityMapEntry,
  resolveCapabilitySkuForScenario,
} from "./billingCapabilityMap";
import {
  COMMERCE_ENTITLEMENT_PREFLIGHT_BLOCK,
  type CommerceEntitlementPreflightResult,
} from "./commerceEntitlementPreflightGate";
import { evaluateCommerceEntitlementS2Gate } from "./commerceEntitlementS2Evaluate";
import type { BillingEntitlementsHttpDeps } from "./internalBillingEntitlementsAdapter";
import {
  type ExecuteConsumptionSettlementInput,
  type ExecuteConsumptionSettlementOutcome,
  executeConsumptionSettlement,
} from "./commerceEntitlementS5Settle";

export type ConsumptionBillingHostConfig = {
  /** 同窗 **`PHASE2_COMMERCE_RAILS_ENABLED`** · 默认关 */
  phase2CommerceRailsEnabled: boolean;
  /** **`INTERNAL_BILLING_BASE_URL`** · internal BFF origin（**`billing-entitlements`**） */
  internalBillingBaseUrl: string;
  /** 所内 mTLS / 内网鉴权头（小样可选） */
  requestHeaders?: Record<string, string>;
  capabilityMap?: Record<string, BillingCapabilityMapEntry>;
  fetchImpl?: typeof fetch;
};

export function buildConsumptionBillingHttpDeps(
  config: ConsumptionBillingHostConfig,
): BillingEntitlementsHttpDeps {
  return {
    baseUrl: config.internalBillingBaseUrl,
    headers: config.requestHeaders,
    fetchImpl: config.fetchImpl,
  };
}

/** 从进程环境解析（**BFF / Worker** 侧；**勿** 暴露密钥到浏览器 bundle） */
export function parseConsumptionBillingHostConfigFromEnv(
  env: Record<string, string | undefined>,
): ConsumptionBillingHostConfig {
  const flag = env.PHASE2_COMMERCE_RAILS_ENABLED?.trim().toLowerCase();
  return {
    phase2CommerceRailsEnabled: flag === "true" || flag === "1",
    internalBillingBaseUrl: env.INTERNAL_BILLING_BASE_URL?.trim() ?? "",
    requestHeaders: undefined,
  };
}

export type RunConsumeAndBillS2Input = {
  userId: string;
  scenarioId: string | undefined;
};

export type RunConsumeAndBillS2Blocked = {
  ok: false;
  stage: "S2";
  code: typeof COMMERCE_ENTITLEMENT_PREFLIGHT_BLOCK;
  capabilitySkuId: string;
  /** **`FR-T05` / stableReason** 族占位 — Taxonomy MR 终裁 */
  stableReason: "BUDGET_OR_QUOTA";
};

export type RunConsumeAndBillS2Outcome =
  | { ok: true }
  | RunConsumeAndBillS2Blocked;

function mapS2GateResult(
  gate: CommerceEntitlementPreflightResult,
): RunConsumeAndBillS2Outcome {
  if (gate.ok) return { ok: true };
  return {
    ok: false,
    stage: "S2",
    code: gate.code,
    capabilitySkuId: gate.capabilitySkuId,
    stableReason: "BUDGET_OR_QUOTA",
  };
}

/**
 * **MR-BILL-B1**：**scenario → capability** + **`evaluateCommerceEntitlementS2Gate`**
 */
export async function runConsumeAndBillS2CommerceGate(
  config: ConsumptionBillingHostConfig,
  input: RunConsumeAndBillS2Input,
): Promise<RunConsumeAndBillS2Outcome> {
  const capabilitySkuId = resolveCapabilitySkuForScenario(
    input.scenarioId,
    config.capabilityMap,
  );

  const gate = await evaluateCommerceEntitlementS2Gate(
    buildConsumptionBillingHttpDeps(config),
    {
      phase2CommerceRailsEnabled: config.phase2CommerceRailsEnabled,
      userId: input.userId,
      capabilitySkuId,
    },
  );

  return mapS2GateResult(gate);
}

export type RunConsumeAndBillS5Input = {
  executionId: string;
  scenarioId: string | undefined;
  packGrantId?: string;
};

/**
 * **MR-BILL-B2**：**scenario → entitlementDebit** + **`executeConsumptionSettlement`**（**默认仅轨 B**）
 */
export async function runConsumeAndBillS5Settlement(
  config: ConsumptionBillingHostConfig,
  input: RunConsumeAndBillS5Input,
): Promise<ExecuteConsumptionSettlementOutcome> {
  const capabilitySkuId = resolveCapabilitySkuForScenario(
    input.scenarioId,
    config.capabilityMap,
  );

  const settlementInput: ExecuteConsumptionSettlementInput = {
    phase2CommerceRailsEnabled: config.phase2CommerceRailsEnabled,
    executionId: input.executionId,
  };

  if (config.phase2CommerceRailsEnabled && capabilitySkuId) {
    settlementInput.entitlementDebit = {
      capabilitySkuId,
      packGrantId: input.packGrantId,
    };
  }

  return executeConsumptionSettlement(
    buildConsumptionBillingHttpDeps(config),
    settlementInput,
  );
}
