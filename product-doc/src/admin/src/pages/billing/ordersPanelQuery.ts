import type { MockCommerceCryptoOrder, MockCommerceCryptoOrderStatus } from "../../data/types";
import { formatCommerceOrderIdDisplay } from "./commerceOrderId";

export type OrdersPanelQuery = {
  orderId: string;
  userId: string;
  productId: string;
  kind: "" | "upgrade" | "pack";
  status: "" | MockCommerceCryptoOrderStatus;
  network: "" | "USDT_TRC20" | "USDT_ERC20";
};

export function parseOrdersPanelQuery(searchParams: URLSearchParams): OrdersPanelQuery {
  const status = searchParams.get("status")?.trim() ?? "";
  const kind = searchParams.get("kind")?.trim() ?? "";
  const network = searchParams.get("network")?.trim() ?? "";
  return {
    orderId: searchParams.get("orderId")?.trim() ?? "",
    userId: searchParams.get("userId")?.trim() ?? "",
    productId: (searchParams.get("productId") ?? searchParams.get("sku") ?? "").trim(),
    kind: kind === "upgrade" || kind === "pack" ? kind : "",
    status:
      status === "PENDING" ||
      status === "CONFIRMING" ||
      status === "SETTLED" ||
      status === "EXPIRED"
        ? status
        : "",
    network: network === "USDT_TRC20" || network === "USDT_ERC20" ? network : "",
  };
}

export function ordersPanelQueryToSearchParams(
  query: OrdersPanelQuery,
  base?: URLSearchParams,
): URLSearchParams {
  const p = new URLSearchParams(base);
  p.set("tab", "orders");

  const setOrDelete = (key: string, value: string) => {
    if (value) p.set(key, value);
    else p.delete(key);
  };

  setOrDelete("orderId", query.orderId.trim());
  setOrDelete("userId", query.userId.trim());
  setOrDelete("productId", query.productId.trim());
  p.delete("sku");
  setOrDelete("kind", query.kind);
  setOrDelete("status", query.status);
  setOrDelete("network", query.network);

  return p;
}

export function filterCommerceOrders(
  orders: MockCommerceCryptoOrder[],
  query: OrdersPanelQuery,
): MockCommerceCryptoOrder[] {
  const userQ = query.userId.trim().toLowerCase();
  const orderDigits = query.orderId.replace(/\D/g, "");
  const productId = query.productId.trim();

  return orders.filter((o) => {
    if (productId && o.productId !== productId) return false;
    if (query.kind && o.kind !== query.kind) return false;
    if (query.status && o.status !== query.status) return false;
    if (query.network && o.network !== query.network) return false;
    if (userQ && !o.userIdMasked.toLowerCase().includes(userQ)) return false;
    if (orderDigits) {
      const idDigits = formatCommerceOrderIdDisplay(o.orderId);
      if (!idDigits.includes(orderDigits)) return false;
    }
    return true;
  });
}

export function hasActiveOrdersQuery(query: OrdersPanelQuery): boolean {
  return Boolean(
    query.orderId.trim() ||
      query.userId.trim() ||
      query.productId.trim() ||
      query.kind ||
      query.status ||
      query.network,
  );
}
