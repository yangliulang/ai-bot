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

function decodePathSegment(seg: string): string {
  try {
    return decodeURIComponent(seg);
  } catch {
    return seg;
  }
}

type CatalogState = {
  catalogVersion: string;
  items: Array<{
    capabilitySkuId: string;
    displayLabel: string;
    remaining: number;
    quotaTotal?: number;
    debitUnitsPerExecution?: number;
    resetsAt: string | null;
  }>;
};

let catalogOverride: CatalogState | null = null;

function currentCatalog(): CatalogState {
  if (catalogOverride) return catalogOverride;
  const snap = mockCommercePhase2AdminSnapshot;
  return {
    catalogVersion: snap.catalogVersion,
    items: snap.capabilityBuckets.map((b) => ({
      capabilitySkuId: b.capabilitySkuId,
      displayLabel: b.displayLabel,
      remaining: b.remaining,
      quotaTotal: b.quotaTotal,
      debitUnitsPerExecution: b.debitUnitsPerExecution ?? 1,
      resetsAt: b.resetsAt,
    })),
  };
}

/** Vite dev · OpenAPI `admin/billing/commerce/*`（同窗 mockCommercePhase2AdminSnapshot） */
export function createBillingCommerceBffMiddleware(): Connect.NextHandleFunction {
  return (req, res, next) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    const path = url.pathname;
    const snap = mockCommercePhase2AdminSnapshot;

    if (path === "/api/v1/admin/billing/commerce/capability-catalog") {
      if (req.method === "GET") {
        sendJson(res, 200, currentCatalog());
        return;
      }
      if (req.method === "PATCH") {
        void readJsonBody(req)
          .then((body) => {
            const ifMatch = req.headers["if-match"];
            const base = currentCatalog();
            if (ifMatch && ifMatch !== base.catalogVersion) {
              sendJson(res, 409, {
                type: "about:blank",
                title: "Conflict",
                detail: "catalogVersion stale; reload and retry",
              });
              return;
            }
            const b = body as Partial<CatalogState>;
            catalogOverride = {
              catalogVersion: String(b.catalogVersion ?? `${base.catalogVersion}-patched`),
              items: Array.isArray(b.items)
                ? b.items.map((item) => {
                    const row = item as CatalogState["items"][number];
                    return {
                      capabilitySkuId: String(row.capabilitySkuId ?? ""),
                      displayLabel: String(row.displayLabel ?? ""),
                      remaining: typeof row.remaining === "number" ? row.remaining : 0,
                      quotaTotal: typeof row.quotaTotal === "number" ? row.quotaTotal : undefined,
                      debitUnitsPerExecution:
                        typeof row.debitUnitsPerExecution === "number" ? row.debitUnitsPerExecution : 1,
                      resetsAt: row.resetsAt ?? null,
                    };
                  })
                : base.items,
            };
            sendJson(res, 200, catalogOverride);
          })
          .catch(() => sendJson(res, 400, { title: "Bad Request" }));
        return;
      }
    }

    if (req.method !== "GET") {
      next();
      return;
    }

    if (path === "/api/v1/admin/billing/commerce/quota-blocked-summary") {
      sendJson(res, 200, {
        window: snap.quotaBlockedSummary.window,
        blockedEventCountByCapability: snap.quotaBlockedSummary.blockedEventCountByCapability,
        topUsersSample: snap.quotaBlockedSummary.topUsersSample.map((u) => ({
          userId: u.userIdMasked,
          blockCount: u.blockCount,
        })),
      });
      return;
    }

    const userOverview = path.match(/^\/api\/v1\/admin\/billing\/commerce\/users\/([^/]+)\/overview$/);
    if (userOverview) {
      const userId = decodePathSegment(userOverview[1]!);
      const catalog = currentCatalog();
      sendJson(res, 200, {
        userId,
        subscriptions: [
          {
            tierDisplay: "Pro",
            tierSku: "1002",
            status: "active",
            periodEnd: "2026-06-01T00:00:00Z",
          },
        ],
        packGrants: catalog.items.map((b) => ({
          capabilitySkuId: b.capabilitySkuId,
          displayLabel: b.displayLabel,
          remaining: b.remaining,
          resetsAt: b.resetsAt,
        })),
        recentExecutionAnchorsSample: ["20260501998001", "20260501998002"],
      });
      return;
    }

    if (path === "/api/v1/admin/billing/commerce/revenue-export-template") {
      sendJson(res, 200, {
        schemaVersion: "2026-05-demo",
        columns: ["userId", "capabilitySkuId", "packGrantId", "amountUsdt", "settledAt"],
      });
      return;
    }

    next();
  };
}
