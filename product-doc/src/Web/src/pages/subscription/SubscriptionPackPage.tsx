import { ArrowLeftOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Col, Row, Typography } from "antd";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { SUBSCRIPTION_COPY } from "@/copy/subscriptionCopy";
import { ADD_ON_PACKS } from "@/data/subscriptionCatalogMock";

const { Paragraph, Text, Title } = Typography;

export default function SubscriptionPackPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const fromTelegram = params.get("from") === "telegram";

  return (
    <>
      <header style={{ marginBottom: 20 }}>
        <Link to="/subscription" className="coolbit-link-muted" style={{ fontSize: 14 }}>
          <ArrowLeftOutlined /> 返回我的订阅
        </Link>
        <Title level={3} style={{ marginTop: 12, marginBottom: 8 }}>
          {SUBSCRIPTION_COPY.packPageTitle}
        </Title>
        <Paragraph style={{ marginBottom: 0, color: "#666" }}>
          {SUBSCRIPTION_COPY.packPageIntro}
        </Paragraph>
      </header>

      {fromTelegram ? (
        <Alert type="info" showIcon style={{ marginBottom: 16 }} message="来自 Telegram 的买包请求" />
      ) : null}

      <Row gutter={[16, 16]}>
        {ADD_ON_PACKS.map((pack) => (
          <Col xs={24} md={8} key={pack.sku}>
            <Card bordered={false} className="coolbit-plan-card">
              <Title level={4}>{pack.name}</Title>
              <Paragraph type="secondary">{pack.description}</Paragraph>
              <div className="coolbit-plan-card__price">
                <Text strong style={{ fontSize: 24 }}>
                  {pack.priceUsdt}
                </Text>
                <Text type="secondary"> USDT</Text>
              </div>
              <Paragraph style={{ marginTop: 8 }}>
                +{pack.units} 次 · <Text code>{pack.capabilitySkuId}</Text>
              </Paragraph>
              <Button
                type="primary"
                block
                onClick={() =>
                  navigate(
                    `/subscription/checkout?kind=pack&sku=${encodeURIComponent(pack.sku)}${fromTelegram ? "&from=telegram" : ""}`,
                  )
                }
              >
                购买并支付
              </Button>
            </Card>
          </Col>
        ))}
      </Row>
    </>
  );
}
