import type {
  BillingFailureReason,
  MockEntitlementDebitDisplayStatus,
} from "../data/types";

const CAPABILITY_LABEL: Record<string, string> = {
  "cap.agent.analyze": "AI 分析",
  "cap.agent.trade": "自动交易",
  "cap.agent.monitoring": "盯盘监控",
  "cap.pack.execution.100": "加购包·100次",
};

const DEBIT_STATUS_LABEL: Record<MockEntitlementDebitDisplayStatus, string> = {
  SUCCESS: "核销成功",
  INSUFFICIENT: "额度不足",
  FAILED: "核销失败",
  AWAITING_FINAL: "待终局",
};

const FAILURE_REASON_LABEL: Record<BillingFailureReason, string> = {
  none: "—",
  quota: "配额用尽",
  gateway: "账务网关",
  policy: "终局未满足",
  not_applicable: "—",
};

export function zhCapabilitySku(sku: string): string {
  return CAPABILITY_LABEL[sku] ?? sku;
}

export function zhEntitlementDebitStatus(s: MockEntitlementDebitDisplayStatus): string {
  return DEBIT_STATUS_LABEL[s] ?? s;
}

export function zhBillingFailureReason(r: BillingFailureReason): string {
  return FAILURE_REASON_LABEL[r] ?? r;
}

export function ledgerFailureReasonText(
  debitStatus: MockEntitlementDebitDisplayStatus,
  failureReason: BillingFailureReason,
): string {
  if (debitStatus === "SUCCESS") return "—";
  return zhBillingFailureReason(failureReason);
}
