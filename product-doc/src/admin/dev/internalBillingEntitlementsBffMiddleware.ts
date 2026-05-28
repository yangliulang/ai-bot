import type { IncomingMessage, ServerResponse } from "node:http";
import type { Connect } from "vite";
import { mockCommercePhase2AdminSnapshot } from "../src/data/mock";

function readJsonBody(req: IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf8");
      if (!raw.trim()) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

function sendJson(res: ServerResponse, status: number, body: unknown): void {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(body));
}

const debitStore = new Map<string, Record<string, unknown>>();

/** Vite dev · `internal/billing-entitlements.yaml`（MR-BILL-B1/B2 staging 探针） */
export function createInternalBillingEntitlementsBffMiddleware(): Connect.NextHandleFunction {
  return (req, res, next) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    const path = url.pathname;

    if (req.method === "GET" && path === "/api/v1/internal/billing/entitlements/balance") {
      const userId = url.searchParams.get("userId")?.trim() ?? "unknown";
      sendJson(res, 200, {
        userId,
        buckets: mockCommercePhase2AdminSnapshot.capabilityBuckets.map((b) => ({
          capabilitySkuId: b.capabilitySkuId,
          remaining: b.remaining,
          periodEndsAt: b.resetsAt,
        })),
      });
      return;
    }

    if (req.method === "POST" && path === "/api/v1/internal/billing/entitlements/debit") {
      void readJsonBody(req)
        .then((body) => {
          const b = body as {
            executionId?: string;
            idempotencyKey?: string;
            capabilitySkuId?: string;
          };
          const key = String(b.idempotencyKey ?? "");
          const existing = debitStore.get(key);
          if (existing) {
            sendJson(res, 200, existing);
            return;
          }
          const capabilitySkuId = String(b.capabilitySkuId ?? "cap.agent.trade");
          const bucket = mockCommercePhase2AdminSnapshot.capabilityBuckets.find(
            (x) => x.capabilitySkuId === capabilitySkuId,
          );
          const remaining = bucket?.remaining ?? 0;
          const result =
            remaining <= 0
              ? {
                  billingTraceId: `bt-insuff-${String(b.executionId ?? "x").slice(-4)}`,
                  commercialSettlementType: "ENTITLEMENT_DEBIT",
                  status: "INSUFFICIENT",
                }
              : {
                  billingTraceId: `bt-${String(b.executionId ?? "x")}`,
                  commercialSettlementType: "ENTITLEMENT_DEBIT",
                  status: "SUCCESS",
                  consumedUnits: 1,
                };
          if (key) debitStore.set(key, result);
          sendJson(res, 200, result);
        })
        .catch(() => sendJson(res, 400, { title: "Bad Request" }));
      return;
    }

    next();
  };
}
