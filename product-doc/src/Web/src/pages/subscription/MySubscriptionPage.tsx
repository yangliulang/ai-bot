import { ShoppingCartOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { Button, Card, Space, Typography } from "antd";
import { Link } from "react-router-dom";
import { SUBSCRIPTION_COPY } from "@/copy/subscriptionCopy";
import { useMeCommerceSummary } from "@/hooks/useMeCommerceSummary";

const { Paragraph, Text, Title } = Typography;

/** 订阅购买入口（配额与流水在账单页） */
export default function MySubscriptionPage() {
  const commerce = useMeCommerceSummary();
  const tier = commerce.summary.subscriptionTierDisplay ?? "未订阅";

  return (
    <div className="coolbit-billing-page">
      <header className="coolbit-billing-page__header">
        <h1 className="coolbit-page-title coolbit-billing-page__title">{SUBSCRIPTION_COPY.mySubscriptionTitle}</h1>
        <Paragraph className="coolbit-billing-page__intro">{SUBSCRIPTION_COPY.mySubscriptionIntro}</Paragraph>
      </header>

      <Card bordered={false} className="coolbit-billing-hero" loading={commerce.loading}>
        <Text type="secondary" style={{ fontSize: 13 }}>
          {SUBSCRIPTION_COPY.currentTierLabel}
        </Text>
        <Title level={4} style={{ margin: "4px 0 20px" }}>
          {tier}
        </Title>
        <Space wrap size={12} style={{ width: "100%" }}>
          <Link to="/subscription/upgrade" style={{ flex: "1 1 140px" }}>
            <Button type="primary" size="large" block icon={<ThunderboltOutlined />}>
              {SUBSCRIPTION_COPY.upgradeNow}
            </Button>
          </Link>
          <Link to="/subscription/pack" style={{ flex: "1 1 140px" }}>
            <Button size="large" block icon={<ShoppingCartOutlined />}>
              {SUBSCRIPTION_COPY.buyPackNow}
            </Button>
          </Link>
          <Link to="/subaccount/billing">
            <Button type="link" block>
              {SUBSCRIPTION_COPY.viewBilling}
            </Button>
          </Link>
        </Space>
      </Card>
    </div>
  );
}
