import { Tag } from "antd";
import { zhEntitlementDebitStatus } from "../../copy/billingLabels";
import type { MockEntitlementDebitDisplayStatus } from "../../data/types";

export function entitlementDebitStatusTag(status: MockEntitlementDebitDisplayStatus) {
  if (status === "SUCCESS") return <Tag color="success">{zhEntitlementDebitStatus(status)}</Tag>;
  if (status === "INSUFFICIENT") return <Tag color="error">{zhEntitlementDebitStatus(status)}</Tag>;
  if (status === "FAILED") return <Tag color="error">{zhEntitlementDebitStatus(status)}</Tag>;
  return <Tag color="warning">{zhEntitlementDebitStatus(status)}</Tag>;
}
