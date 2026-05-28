/**
 * 商业订单号 · 同窗 `src/admin/src/pages/billing/commerceOrderId.ts` · `identity-schemas` ExecutionId
 */
export const COMMERCE_ORDER_ID_PATTERN = /^\d{14,20}$/;

export function createDemoCommerceOrderId(date = new Date()): string {
  const p = (n: number) => String(n).padStart(2, "0");
  const seq = String(Math.floor(Math.random() * 900) + 100);
  return `${date.getUTCFullYear()}${p(date.getUTCMonth() + 1)}${p(date.getUTCDate())}${p(date.getUTCHours())}${p(date.getUTCMinutes())}${p(date.getUTCSeconds())}${seq}`;
}

export function isCommerceOrderId(value: string): boolean {
  return COMMERCE_ORDER_ID_PATTERN.test(value.trim());
}
