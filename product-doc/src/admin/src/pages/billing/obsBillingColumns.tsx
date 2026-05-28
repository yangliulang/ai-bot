import { Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { ledgerFailureReasonText, zhCapabilitySku } from "../../copy/billingLabels";
import { entitlementDebitStatusTag } from "./debitStatusTag";
import type { MockObsBillingRow } from "../../data/types";

const { Text } = Typography;

export function obsBillingColumns(opts?: {
  formatTime?: (iso: string) => string;
}): ColumnsType<MockObsBillingRow> {
  const formatTime = opts?.formatTime ?? ((iso: string) => iso);
  return [
    {
      title: "计费链路 ID",
      dataIndex: "billingTraceId",
      width: 130,
      ellipsis: true,
      render: (id: string) => <Text code style={{ fontSize: 12 }}>{id}</Text>,
    },
    {
      title: "Capability",
      dataIndex: "capabilitySkuId",
      width: 100,
      ellipsis: true,
      render: (sku: string) => zhCapabilitySku(sku),
    },
    {
      title: "核销状态",
      dataIndex: "debitStatus",
      width: 96,
      render: (s: MockObsBillingRow["debitStatus"]) => entitlementDebitStatusTag(s),
    },
    {
      title: "失败原因",
      key: "fr",
      width: 88,
      render: (_: unknown, row: MockObsBillingRow) =>
        ledgerFailureReasonText(row.debitStatus, row.failureReason),
    },
    {
      title: "扣减",
      dataIndex: "consumedUnits",
      width: 56,
      align: "right" as const,
      render: (n: number | undefined, row: MockObsBillingRow) =>
        row.debitStatus === "SUCCESS" && n != null ? n : "—",
    },
    {
      title: "时间",
      dataIndex: "at",
      width: 160,
      render: (t: string) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {formatTime(t)}
        </Text>
      ),
    },
  ];
}
