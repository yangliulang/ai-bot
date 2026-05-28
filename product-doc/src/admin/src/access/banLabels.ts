/** 用户封禁 · 原因（枚举值 ↔ 中文名，表格与表单共用） */

export const BAN_REASON_OPTIONS: { value: string; label: string }[] = [
  { value: "AGENT_USER_BLOCKED", label: "通用封禁" },
  { value: "COMPLIANCE_ABUSE", label: "滥用与合规" },
  { value: "FRAUD_SUSPECT", label: "风控嫌疑" },
  { value: "SPAM", label: "垃圾与骚扰" },
];

export function banReasonZh(code: string): string {
  return BAN_REASON_OPTIONS.find((o) => o.value === code)?.label ?? code;
}

/** 本控制台范围固定：仅智能体产品 */
export const BAN_SCOPE_AGENT_PRODUCT = "AGENT_PRODUCT";

export const BAN_SCOPE_AGENT_PRODUCT_ZH = "智能体产品";
