/**
 * 商业订单号规则（运营台 / Web checkout 同窗）
 *
 * - **展示与存储键均为纯数字字符串**（不含字母、符号、空格）
 * - **长度** 14～20 位（推荐：UTC `yyyyMMddHHmmss` + 3 位日内序号）
 * - **示例** `202605111420001`（2026-05-11 14:20:00 · 序号 001）
 */
export const COMMERCE_ORDER_ID_MIN_LEN = 14;
export const COMMERCE_ORDER_ID_MAX_LEN = 20;
export const COMMERCE_ORDER_ID_PATTERN = /^\d{14,20}$/;

export function isCommerceOrderId(value: string): boolean {
  return COMMERCE_ORDER_ID_PATTERN.test(value.trim());
}

/** UI 展示：仅输出数字订单号；非法值回退为去非数字（便于迁移旧 demo 数据） */
export function formatCommerceOrderIdDisplay(orderId: string): string {
  const trimmed = orderId.trim();
  if (isCommerceOrderId(trimmed)) return trimmed;
  const digits = trimmed.replace(/\D/g, "");
  return digits.length >= COMMERCE_ORDER_ID_MIN_LEN
    ? digits.slice(0, COMMERCE_ORDER_ID_MAX_LEN)
    : digits || trimmed;
}
