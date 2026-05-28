import type { ServerResponse } from "node:http";
import type { Connect } from "vite";
import { mockBillingLedger } from "../src/data/mockBillingData";

function sendJson(res: ServerResponse, status: number, body: unknown): void {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(body));
}

function filterRows(
  rows: typeof mockBillingLedger,
  q: URLSearchParams,
): typeof mockBillingLedger {
  let out = rows;
  const userId = q.get("userId")?.trim().toLowerCase();
  const executionId = q.get("executionId")?.trim().toLowerCase();
  const billingTraceId = q.get("billingTraceId")?.trim().toLowerCase();
  if (userId) out = out.filter((r) => r.userIdMasked.toLowerCase().includes(userId));
  if (executionId) out = out.filter((r) => r.executionId.toLowerCase().includes(executionId));
  if (billingTraceId) {
    out = out.filter((r) => r.billingTraceId.toLowerCase().includes(billingTraceId));
  }
  return out;
}

/** Vite dev · `GET /api/v1/admin/billing/traces`（同窗 mockBillingLedger） */
export function createBillingLedgerBffMiddleware(): Connect.NextHandleFunction {
  return (req, res, next) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    const path = url.pathname;

    if (req.method === "GET" && path === "/api/v1/admin/billing/traces") {
      const items = filterRows(mockBillingLedger, url.searchParams);
      sendJson(res, 200, { items });
      return;
    }

    const byId = path.match(/^\/api\/v1\/admin\/billing\/traces\/([^/]+)$/);
    if (req.method === "GET" && byId) {
      const id = decodeURIComponent(byId[1]!);
      const row = mockBillingLedger.find(
        (r) => r.billingTraceId === id || r.billingTraceId.includes(id),
      );
      if (!row) {
        sendJson(res, 404, { type: "about:blank", title: "Not Found", detail: id });
        return;
      }
      sendJson(res, 200, row);
      return;
    }

    next();
  };
}
