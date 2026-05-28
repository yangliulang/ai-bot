import type { ServerResponse } from "node:http";
import type { Connect } from "vite";
import { MOCK_ME_COMMERCE_CONSUMPTIONS } from "../src/data/meCommerceConsumptionMock";
import { MOCK_ME_COMMERCE_SUMMARY } from "../src/data/meCommerceMock";

function sendJson(res: ServerResponse, status: number, body: unknown): void {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(body));
}

function paginate<T>(all: T[], cursor: string | null, pageSize: number): { items: T[]; nextCursor: string | null } {
  const offset = cursor ? Number.parseInt(cursor, 10) : 0;
  const start = Number.isFinite(offset) && offset >= 0 ? offset : 0;
  const end = start + pageSize;
  const items = all.slice(start, end);
  const nextCursor = end < all.length ? String(end) : null;
  return { items, nextCursor };
}

/** Vite dev · `me/commerce` mock BFF */
export function createMeCommerceBffMiddleware(): Connect.NextHandleFunction {
  return (req, res, next) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    if (req.method === "GET" && url.pathname === "/api/v1/me/commerce/entitlements/summary") {
      sendJson(res, 200, MOCK_ME_COMMERCE_SUMMARY);
      return;
    }
    if (req.method === "GET" && url.pathname === "/api/v1/me/commerce/consumptions") {
      const pageSize = Math.min(
        100,
        Math.max(1, Number.parseInt(url.searchParams.get("pageSize") ?? "10", 10) || 10),
      );
      const cursor = url.searchParams.get("cursor");
      sendJson(res, 200, paginate(MOCK_ME_COMMERCE_CONSUMPTIONS, cursor, pageSize));
      return;
    }
    next();
  };
}
