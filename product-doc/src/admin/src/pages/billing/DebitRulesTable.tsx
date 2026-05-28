import { Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { BILLING_RULES } from "../../copy/opsPanelHints";
import {
  debitCapabilityShortId,
  debitCapabilityTagColor,
  type BillingDebitRule,
} from "../../data/billingRulesSeed";

const { Text } = Typography;

type Props = {
  rules: BillingDebitRule[];
};

export function DebitRulesTable({ rules }: Props) {
  const columns: ColumnsType<BillingDebitRule> = [
    {
      title: BILLING_RULES.colDebitCapability,
      key: "capability",
      render: (_, row) => {
        const tagColor = debitCapabilityTagColor(row.capabilitySkuId);
        const shortId = debitCapabilityShortId(row.capabilitySkuId);
        return (
          <Space direction="vertical" size={4} style={{ maxWidth: 420 }}>
            <Space size="small" wrap>
              <Text strong style={{ fontSize: 14 }}>
                {row.displayLabel}
              </Text>
              {tagColor ? <Tag color={tagColor}>{shortId}</Tag> : <Tag>{shortId}</Tag>}
            </Space>
            <Text type="secondary" style={{ fontSize: 12, lineHeight: 1.5 }}>
              {row.summary}
            </Text>
            <Text type="secondary" code style={{ fontSize: 11 }}>
              {row.capabilitySkuId}
            </Text>
          </Space>
        );
      },
    },
    {
      title: BILLING_RULES.colDebitStandard,
      dataIndex: "debitUnitsPerExecution",
      width: 168,
      align: "right",
      render: (units: number) => (
        <Space direction="vertical" size={0} style={{ alignItems: "flex-end" }}>
          <span>
            <Text style={{ fontSize: 20, fontWeight: 600, lineHeight: 1.2 }}>{units}</Text>
            <Text type="secondary" style={{ marginLeft: 6, fontSize: 13 }}>
              {BILLING_RULES.debitUnitSuffix}
            </Text>
          </span>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {BILLING_RULES.debitPerSuccessHint}
          </Text>
        </Space>
      ),
    },
  ];

  return (
    <Table
      rowKey="capabilitySkuId"
      size="middle"
      pagination={false}
      dataSource={rules}
      columns={columns}
      showHeader
    />
  );
}
