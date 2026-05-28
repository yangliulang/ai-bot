import { Link } from "react-router-dom";
import { Space, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { ledgerFailureReasonText, zhCapabilitySku } from "../../copy/billingLabels";
import { entitlementDebitStatusTag } from "./debitStatusTag";
import type { MockBillingLedgerRow } from "../../data/types";

const { Text } = Typography;

export function formatBillingRecordedAt(iso: string): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("zh-CN", { hour12: false });
}

function executionRuntimeStatusTag(s: string) {
  const u = s.toUpperCase();
  if (u === "COMPLETED") return <Tag color="success">已完成</Tag>;
  if (u === "UNKNOWN") return <Tag color="warning">UNKNOWN</Tag>;
  if (u === "RUNNING") return <Tag color="processing">运行中</Tag>;
  if (u === "FAILED") return <Tag color="error">失败</Tag>;
  if (u === "BLOCKED") return <Tag color="error">阻断</Tag>;
  return <Tag>{s}</Tag>;
}

/** 执行核销追踪 · 主列表（幂等键等见行展开） */
export const runtimeBillingTraceColumns: ColumnsType<MockBillingLedgerRow> = [
  {
    title: "执行 ID",
    dataIndex: "executionId",
    key: "e",
    fixed: "left",
    width: 118,
    ellipsis: true,
    render: (id: string) => (
      <Link to={`/runtime/executions/${id}`}>
        <Text code>{id}</Text>
      </Link>
    ),
  },
  { title: "用户 UID", dataIndex: "userIdMasked", key: "u", width: 88, ellipsis: true },
  {
    title: "Capability",
    dataIndex: "capabilitySkuId",
    key: "cap",
    width: 108,
    ellipsis: true,
    render: (sku: string) => (
      <span title={sku}>
        <Text>{zhCapabilitySku(sku)}</Text>
      </span>
    ),
  },
  {
    title: "核销状态",
    dataIndex: "debitStatus",
    key: "deb",
    width: 96,
    render: (s: MockBillingLedgerRow["debitStatus"]) => entitlementDebitStatusTag(s),
  },
  {
    title: "失败原因",
    key: "fr",
    width: 100,
    ellipsis: true,
    render: (_: unknown, row: MockBillingLedgerRow) => {
      const fr = ledgerFailureReasonText(row.debitStatus, row.failureReason);
      if (fr === "—") {
        return (
          <Text type="secondary" style={{ fontSize: 12 }}>
            —
          </Text>
        );
      }
      return <Text style={{ fontSize: 12 }}>{fr}</Text>;
    },
  },
  {
    title: "扣减",
    dataIndex: "consumedUnits",
    key: "units",
    width: 64,
    align: "right" as const,
    render: (n: number | undefined, row: MockBillingLedgerRow) =>
      row.debitStatus === "SUCCESS" && n != null ? n : "—",
  },
  { title: "意图", dataIndex: "intentType", key: "intent", width: 72, ellipsis: true },
  {
    title: "执行状态",
    dataIndex: "executionStatus",
    key: "ex",
    width: 92,
    render: (s: string) => executionRuntimeStatusTag(s),
  },
  {
    title: "核销时间",
    dataIndex: "recordedAt",
    key: "r",
    width: 150,
    render: (iso: string) => formatBillingRecordedAt(iso),
  },
  {
    title: "链路 ID",
    dataIndex: "billingTraceId",
    key: "bt",
    width: 118,
    ellipsis: true,
    render: (s: string) => (
      <Text code style={{ fontSize: 12 }}>
        {s}
      </Text>
    ),
  },
];

export function billingTraceExpandedRowRender(row: MockBillingLedgerRow) {
  return (
    <div style={{ padding: "10px 16px 12px 48px", background: "var(--ant-color-fill-alter, #fafafa)" }}>
      <Text type="secondary" style={{ fontSize: 12, marginBottom: 6, display: "block" }}>
        高级调试（工程字段）
      </Text>
      <Space direction="vertical" size={4}>
        <Text style={{ fontSize: 12 }}>
          清算类型 <Text code>{row.commercialSettlementType}</Text>
        </Text>
        <Text style={{ fontSize: 12 }}>
          幂等键后缀 <Text code>{row.idempotencyKeySuffix}</Text>
        </Text>
        {row.requestId ? (
          <Text style={{ fontSize: 12 }}>
            requestId <Text code>{row.requestId}</Text>
          </Text>
        ) : null}
        {row.packGrantId ? (
          <Text style={{ fontSize: 12 }}>
            packGrantId <Text code>{row.packGrantId}</Text>
          </Text>
        ) : null}
      </Space>
    </div>
  );
}
