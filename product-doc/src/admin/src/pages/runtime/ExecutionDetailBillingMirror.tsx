import { Card, Descriptions, Space, Tag, Typography } from "antd";
import { Link } from "react-router-dom";
import { ledgerFailureReasonText, zhCapabilitySku } from "../../copy/billingLabels";
import { EXECUTION_DETAIL } from "../../copy/opsPanelHints";
import type { MockObsBillingRow } from "../../data/types";
import { entitlementDebitStatusTag } from "../billing/debitStatusTag";

const { Text } = Typography;

type Props = {
  executionId: string;
  billing: MockObsBillingRow[];
};

/** 总览 Tab · 权益核销摘要（FR-MC503 同窗 · 明细见「调用与计费」） */
export function ExecutionDetailBillingMirror({ executionId, billing }: Props) {
  const primary = billing[0];

  return (
    <Card size="small" className="admin-panel-card" title={EXECUTION_DETAIL.billingMirrorTitle}>
      {!primary ? (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {EXECUTION_DETAIL.billingMirrorEmpty}
        </Text>
      ) : (
        <Space direction="vertical" size="middle" style={{ width: "100%" }}>
          <Descriptions
            bordered
            size="small"
            column={{ xs: 1, sm: 2 }}
            items={[
              {
                label: EXECUTION_DETAIL.billingMirrorCapability,
                children: (
                  <Text code style={{ fontSize: 12 }}>
                    {zhCapabilitySku(primary.capabilitySkuId)}
                  </Text>
                ),
              },
              {
                label: EXECUTION_DETAIL.billingMirrorDebit,
                children: entitlementDebitStatusTag(primary.debitStatus),
              },
              {
                label: EXECUTION_DETAIL.billingMirrorTrace,
                children: (
                  <Text code style={{ fontSize: 12 }}>
                    {primary.billingTraceId}
                  </Text>
                ),
              },
              {
                label: EXECUTION_DETAIL.billingMirrorSettlement,
                children: <Tag>{primary.commercialSettlementType}</Tag>,
              },
              {
                label: EXECUTION_DETAIL.billingMirrorFailure,
                span: 2,
                children: ledgerFailureReasonText(primary.debitStatus, primary.failureReason),
              },
              ...(primary.debitStatus === "SUCCESS" && primary.consumedUnits != null
                ? [
                    {
                      label: EXECUTION_DETAIL.billingMirrorUnits,
                      children: primary.consumedUnits,
                    },
                  ]
                : []),
            ]}
          />
          <Space wrap size="small">
            <Link to={`/billing/ledger?tab=correlate&q=${encodeURIComponent(primary.billingTraceId)}`}>
              {EXECUTION_DETAIL.billingMirrorLedgerLink}
            </Link>
            <Link to={`/billing/ledger?q=${encodeURIComponent(executionId)}`}>
              {EXECUTION_DETAIL.billingMirrorExecLedgerLink}
            </Link>
          </Space>
          {billing.length > 1 ? (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {EXECUTION_DETAIL.billingMirrorMoreRows(billing.length - 1)}
            </Text>
          ) : null}
        </Space>
      )}
    </Card>
  );
}
