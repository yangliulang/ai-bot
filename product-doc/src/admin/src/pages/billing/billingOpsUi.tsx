import { Alert, Col, Row, Space, Statistic, Tag, Typography } from "antd";
import type { ReactNode } from "react";
import type { MockCommerceResourcePack, MockCommerceSubscriptionTier } from "../../data/types";
import { BillingSpecCollapse } from "./billingWorkspace";
import { formatEffectiveQuotaSummary, resolvePacksForTier } from "./subscriptionPackUtils";

const { Text } = Typography;

/** 各 Tab 顶部一行说明（可折叠细则） */
export function BillingOpsTabIntro({
  message,
  detail,
}: {
  message: ReactNode;
  detail?: ReactNode;
}) {
  return (
    <div style={{ marginBottom: 16 }}>
      <Alert type="info" showIcon message={message} style={{ marginBottom: detail ? 8 : 0 }} />
      {detail ? <BillingSpecCollapse title="说明与边界">{detail}</BillingSpecCollapse> : null}
    </div>
  );
}

export function BillingOpsStatRow({
  items,
}: {
  items: { title: string; value: number | string; suffix?: string }[];
}) {
  return (
    <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
      {items.map((item) => (
        <Col xs={12} sm={8} key={item.title}>
          <div className="admin-stat-card admin-panel-card" style={{ padding: "14px 16px" }}>
            <Statistic title={item.title} value={item.value} suffix={item.suffix} valueStyle={{ fontSize: 22 }} />
          </div>
        </Col>
      ))}
    </Row>
  );
}

export function TierLinkedPackTags({
  tier,
  packs,
}: {
  tier: Pick<MockCommerceSubscriptionTier, "resourcePackIds">;
  packs: MockCommerceResourcePack[];
}) {
  const linked = resolvePacksForTier(tier, packs);
  if (linked.length === 0) {
    return <Text type="secondary">未关联</Text>;
  }
  return (
    <Space size={[4, 4]} wrap>
      {linked.map((p) => (
        <Tag key={p.resourceId} style={{ margin: 0 }}>
          {p.name}
        </Tag>
      ))}
    </Space>
  );
}

export function TierEffectiveQuotaText({
  tier,
  packs,
}: {
  tier: Pick<MockCommerceSubscriptionTier, "resourcePackIds" | "periodLabel">;
  packs: MockCommerceResourcePack[];
}) {
  const linked = resolvePacksForTier(tier, packs);
  return (
    <Text type="secondary" style={{ fontSize: 12 }}>
      {formatEffectiveQuotaSummary(linked, tier.periodLabel)}
    </Text>
  );
}
