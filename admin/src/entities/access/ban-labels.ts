/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-16
 * 修改功能: 增补 **`OPS_MANUAL`**（与后端测试 / 运维封禁对齐）
 * 作者: 杨永的Agent
 * 日期: 2026-05-12
 * 修改功能: 封禁原因与范围文案（与 product-doc banLabels 对齐）
 */

export const BAN_REASON_OPTIONS: { value: string; label: string }[] = [
  { value: 'AGENT_USER_BLOCKED', label: '通用封禁' },
  { value: 'COMPLIANCE_ABUSE', label: '滥用与合规' },
  { value: 'FRAUD_SUSPECT', label: '风控嫌疑' },
  { value: 'SPAM', label: '垃圾与骚扰' },
  { value: 'OPS_MANUAL', label: '运维手工' },
]

export function banReasonZh(code: string): string {
  return BAN_REASON_OPTIONS.find((o) => o.value === code)?.label ?? code
}

export const BAN_SCOPE_AGENT_PRODUCT = 'AGENT_PRODUCT'

export const BAN_SCOPE_AGENT_PRODUCT_ZH = '智能体产品'
