/**
 * 同窗 **`specs/openapi/internal/billing-entitlements.yaml`**
 *
 * **`getInternalBillingEntitlementsBalance`** → `operationId`: `getInternalBillingEntitlementsBalance`  
 * **`postInternalBillingEntitlementsDebit`** → `postInternalBillingEntitlementsDebit`  
 * **`postInternalCommercePackGrantsApply`** → `postInternalCommercePackGrantsApply`
 *
 * 所内：**mTLS/内网**：`BillingEntitlementsHttpDeps.baseUrl` 由部署注入；实现 MR 可换 gRPC **同窗语义**。
 * **SSOT schema**：[`billing-schemas.yaml`](../../../../specs/openapi/components/billing-schemas.yaml) · [`commerce-model.md`](../../../../specs/requirements/domains/admin/billing-management/commerce-model.md)
 */

/** 与 OpenAPI `paths` 键一致（`/api/v1` 前缀勿在 baseUrl 重复）。 */
export const INTERNAL_BILLING_ENTITLEMENTS_PATHS = {
  debit: "/api/v1/internal/billing/entitlements/debit",
  balance: "/api/v1/internal/billing/entitlements/balance",
  packGrantsApply: "/api/v1/internal/commerce/pack-grants/apply",
} as const;

export type BillingEntitlementsHttpDeps = {
  /** 网关 origin，例如 `https://bff.internal.invalid` — **不含**尾随 path */
  baseUrl: string;
  /** 所内 mTLS / 内网鉴权（可选） */
  headers?: Record<string, string>;
  /** 测试注入；缺省使用全局 **`fetch`** */
  fetchImpl?: (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
};

export type InternalEntitlementDebitRequestBody = {
  executionId: string;
  idempotencyKey: string;
  capabilitySkuId: string;
  packGrantId?: string;
};

export type InternalEntitlementDebitResultBody = {
  billingTraceId: string;
  traceKey?: string;
  commercialSettlementType: "ENTITLEMENT_DEBIT";
  status: "SUCCESS" | "INSUFFICIENT" | "FAILED";
  consumedUnits?: number;
  [key: string]: unknown;
};

export type InternalEntitlementsBalanceResponseBody = {
  userId: string;
  buckets: Array<{
    capabilitySkuId: string;
    remaining?: number;
    periodEndsAt?: string | null;
    [key: string]: unknown;
  }>;
  [key: string]: unknown;
};

export type InternalPackGrantApplyRequestBody = {
  userId: string;
  packSkuId: string;
  quantity: number;
  purchaseRef: string;
  idempotencyKey: string;
};

export type InternalPackGrantApplyResultBody = {
  billingTraceId?: string;
  commercialSettlementType: "PACK_GRANT";
  status: string;
  packGrantIds?: string[];
  grantedUnitsTotal?: number;
  [key: string]: unknown;
};

/**
 * 自 **`InternalEntitlementsBalanceResponse`** 取 **单行桶** **`remaining`**；无匹配桶或未返回 **`remaining`** → **`undefined`**
 *（同窗 **`runCommerceEntitlementPreflight`** 之「放行」语义）。
 */
export function pickRemainingForCapabilitySku(
  balance: InternalEntitlementsBalanceResponseBody,
  capabilitySkuId: string,
): number | undefined {
  const sku = capabilitySkuId.trim();
  const bucket = balance.buckets?.find((b) => b.capabilitySkuId === sku);
  if (bucket === undefined || bucket.remaining === undefined) return undefined;
  return bucket.remaining;
}

export type BillingProblemBody = {
  code?: string;
  message?: string;
  details?: Record<string, unknown>;
  [key: string]: unknown;
};

export class BillingEntitlementsHttpError extends Error {
  readonly status: number;
  readonly problem?: BillingProblemBody;

  constructor(
    message: string,
    init: { status: number; problem?: BillingProblemBody },
  ) {
    super(message);
    this.name = "BillingEntitlementsHttpError";
    this.status = init.status;
    this.problem = init.problem;
  }
}

function normalizeBase(baseUrl: string): string {
  return baseUrl.replace(/\/+$/, "");
}

function buildUrl(baseUrl: string, path: string, query?: Record<string, string>): string {
  const u = new URL(path, `${normalizeBase(baseUrl)}/`);
  if (query) {
    for (const [k, v] of Object.entries(query)) u.searchParams.set(k, v);
  }
  return u.toString();
}

async function readProblem(res: Response): Promise<BillingProblemBody | undefined> {
  try {
    const text = await res.text();
    if (!text.trim()) return undefined;
    return JSON.parse(text) as BillingProblemBody;
  } catch {
    return undefined;
  }
}

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (res.ok) {
    return res.json() as Promise<T>;
  }
  const problem = await readProblem(res);
  const msg =
    problem?.message ??
    `Billing entitlements HTTP ${res.status} ${res.statusText}`.trim();
  throw new BillingEntitlementsHttpError(msg, { status: res.status, problem });
}

/** `GET …/entitlements/balance` */
export async function getInternalBillingEntitlementsBalance(
  deps: BillingEntitlementsHttpDeps,
  params: { userId: string },
): Promise<InternalEntitlementsBalanceResponseBody> {
  const fetchFn = deps.fetchImpl ?? fetch;
  const url = buildUrl(deps.baseUrl, INTERNAL_BILLING_ENTITLEMENTS_PATHS.balance, {
    userId: params.userId,
  });
  const res = await fetchFn(url, {
    method: "GET",
    headers: { Accept: "application/json", ...deps.headers },
  });
  return jsonOrThrow<InternalEntitlementsBalanceResponseBody>(res);
}

/** `POST …/entitlements/debit` · SC-B20 */
export async function postInternalBillingEntitlementsDebit(
  deps: BillingEntitlementsHttpDeps,
  body: InternalEntitlementDebitRequestBody,
): Promise<InternalEntitlementDebitResultBody> {
  const fetchFn = deps.fetchImpl ?? fetch;
  const url = buildUrl(deps.baseUrl, INTERNAL_BILLING_ENTITLEMENTS_PATHS.debit);
  const res = await fetchFn(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...deps.headers,
    },
    body: JSON.stringify(body),
  });
  return jsonOrThrow<InternalEntitlementDebitResultBody>(res);
}

/** `POST …/pack-grants/apply` · FR-B18 后台作业 */
export async function postInternalCommercePackGrantsApply(
  deps: BillingEntitlementsHttpDeps,
  body: InternalPackGrantApplyRequestBody,
): Promise<InternalPackGrantApplyResultBody> {
  const fetchFn = deps.fetchImpl ?? fetch;
  const url = buildUrl(deps.baseUrl, INTERNAL_BILLING_ENTITLEMENTS_PATHS.packGrantsApply);
  const res = await fetchFn(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...deps.headers,
    },
    body: JSON.stringify(body),
  });
  return jsonOrThrow<InternalPackGrantApplyResultBody>(res);
}
