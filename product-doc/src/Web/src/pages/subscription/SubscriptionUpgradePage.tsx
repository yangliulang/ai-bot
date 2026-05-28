import { ArrowLeftOutlined, CheckOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Col, Row, Tag, Typography } from "antd";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { SUBSCRIPTION_COPY } from "@/copy/subscriptionCopy";
import { SUBSCRIPTION_PLANS } from "@/data/subscriptionCatalogMock";
import { useMeCommerceSummary } from "@/hooks/useMeCommerceSummary";

const { Paragraph, Text, Title } = Typography;

export default function SubscriptionUpgradePage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const fromTelegram = params.get("from") === "telegram";
  const commerce = useMeCommerceSummary();
  const currentSku = commerce.summary.subscriptionTierSku;

  return (
    <>
      <header style={{ marginBottom: 20 }}>
        <Link to="/subscription" className="coolbit-link-muted" style={{ fontSize: 14 }}>
          <ArrowLeftOutlined /> 返回我的订阅
        </Link>
        <Title level={3} style={{ marginTop: 12, marginBottom: 8 }}>
          {SUBSCRIPTION_COPY.upgradePageTitle}
        </Title>
        <Paragraph style={{ marginBottom: 0, color: "#666" }}>
          {SUBSCRIPTION_COPY.upgradePageIntro}
          {commerce.summary.subscriptionTierDisplay ? (
            <>
              {" "}
              当前：<Text strong>{commerce.summary.subscriptionTierDisplay}</Text>
            </>
          ) : null}
        </Paragraph>
      </header>

      {fromTelegram ? (
        <Alert type="info" showIcon style={{ marginBottom: 16 }} message="来自 Telegram 的升级请求" />
      ) : null}

      <Row gutter={[16, 16]}>
        {SUBSCRIPTION_PLANS.map((plan) => {
          const isCurrent = plan.sku === currentSku;
          return (
            <Col xs={24} md={8} key={plan.sku}>
              <Card
                bordered={false}
                className={[
                  "coolbit-plan-card",
                  plan.recommended ? "coolbit-plan-card--featured" : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
              >
                {plan.recommended ? (
                  <Tag color="blue" className="coolbit-plan-card__badge">
                    推荐
                  </Tag>
                ) : null}
                {isCurrent ? <Tag>当前档位</Tag> : null}
                <Title level={4}>{plan.name}</Title>
                <Paragraph type="secondary">{plan.tagline}</Paragraph>
                <div className="coolbit-plan-card__price">
                  <Text strong style={{ fontSize: 28 }}>
                    {plan.priceUsdt}
                  </Text>
                  <Text type="secondary"> USDT / {plan.periodLabel}</Text>
                </div>
                <ul className="coolbit-plan-card__list">
                  {plan.highlights.map((h) => (
                    <li key={h}>
                      <CheckOutlined /> {h}
                    </li>
                  ))}
                </ul>
                <Button
                  type="primary"
                  block
                  disabled={isCurrent}
                  onClick={() =>
                    navigate(
                      `/subscription/checkout?kind=upgrade&sku=${encodeURIComponent(plan.sku)}${fromTelegram ? "&from=telegram" : ""}`,
                    )
                  }
                >
                  {isCurrent ? "当前套餐" : "选择并支付"}
                </Button>
              </Card>
            </Col>
          );
        })}
      </Row>
    </>
  );
}
