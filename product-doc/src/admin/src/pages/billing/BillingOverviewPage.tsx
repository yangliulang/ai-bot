import { Alert, Card, Col, Row, Spin, Statistic, Table, Tag, Typography } from "antd";
import { Link } from "react-router-dom";
import { useMemo } from "react";
import { ProductPageShell } from "../../components/product";
import { BILLING_COMMERCE, BILLING_OVERVIEW } from "../../copy/opsPanelHints";
import { mockBillingGatewayErrors, mockBillingHealth, mockBillingRuntimeOverview } from "../../data/mock";
import { useCommerceAdminSnapshot } from "../../hooks/useCommerceAdminSnapshot";
import { billingOpsLink } from "./billingPaths";

const { Text, Paragraph } = Typography;

const WORKFLOW_ITEMS = [
  { to: billingOpsLink("subscriptions"), title: "订阅套餐", desc: "档位与标价" },
  { to: billingOpsLink("packs"), title: "资源管理", desc: "配额与售价" },
  { to: billingOpsLink("rules"), title: "计费规则", desc: "扣次与场景" },
  { to: billingOpsLink("orders"), title: "订阅订单", desc: "Crypto 到账" },
  { to: billingOpsLink("consumption"), title: "用户消耗", desc: "权益协查" },
  { to: "/billing/ledger", title: "执行核销", desc: "核销事实" },
] as const;

export function BillingOverviewPage() {
  const d = mockBillingRuntimeOverview;
  const { snapshot: commerce, source: commerceSource, loading: commerceLoading } = useCommerceAdminSnapshot();

  const quotaBlockedTotal = useMemo(
    () =>
      Object.values(commerce.quotaBlockedSummary.blockedEventCountByCapability).reduce((a, b) => a + b, 0),
    [commerce.quotaBlockedSummary.blockedEventCountByCapability],
  );

  return (
    <ProductPageShell
      pageId="billing.overview"
      showPageId={false}
      title="计费总览"
      description={BILLING_OVERVIEW.description}
    >
      <Alert
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        message={BILLING_OVERVIEW.roleSplitTitle}
        description={
          <Paragraph style={{ marginBottom: 0 }}>{BILLING_OVERVIEW.roleSplitCommerce}</Paragraph>
        }
      />

      <Card
        size="small"
        className="admin-panel-card"
        title={BILLING_OVERVIEW.sectionWorkflow}
        style={{ marginBottom: 16 }}
      >
        <Row gutter={[12, 12]}>
          {WORKFLOW_ITEMS.map((item) => (
            <Col key={item.to} xs={24} sm={12} md={8} lg={4}>
              <Link to={item.to} style={{ display: "block" }}>
                <Card size="small" hoverable styles={{ body: { padding: "10px 12px" } }}>
                  <Text strong style={{ fontSize: 13 }}>
                    {item.title}
                  </Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {item.desc}
                  </Text>
                </Card>
              </Link>
            </Col>
          ))}
        </Row>
      </Card>

      <Text type="secondary" style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
        {BILLING_OVERVIEW.sectionUsage}
      </Text>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={6}>
          <Card size="small" className="admin-panel-card">
            <Statistic title="今日执行" value={d.executionsToday} />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small" className="admin-panel-card">
            <Statistic title="成功率" value={d.successRatePct} suffix="%" valueStyle={{ color: "#3f8600" }} />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small" className="admin-panel-card">
            <Statistic title="活跃任务" value={d.activeTasks} />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small" className="admin-panel-card">
            <Statistic title={BILLING_OVERVIEW.tokenTodayTitle} value={d.tokenConsumptionToday} />
          </Card>
        </Col>
      </Row>

      <Card size="small" className="admin-panel-card" title={BILLING_OVERVIEW.trendCardTitle} style={{ marginBottom: 16 }}>
        <Table
          rowKey="day"
          size="small"
          pagination={false}
          dataSource={d.executionTrend7d}
          columns={[
            { title: "日期", dataIndex: "day", width: 120 },
            { title: "分析", dataIndex: "analyze", align: "right", width: 80 },
            { title: "交易", dataIndex: "trade", align: "right", width: 80 },
            { title: BILLING_OVERVIEW.colMonitoring, dataIndex: "monitoring", align: "right", width: 80 },
          ]}
        />
      </Card>

      <Text type="secondary" style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
        {BILLING_OVERVIEW.sectionHealth}
      </Text>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} md={10}>
          <Card size="small" className="admin-panel-card">
            <Statistic
              title={BILLING_OVERVIEW.billingModeLabel}
              value={BILLING_OVERVIEW.billingModeValue}
              valueStyle={{ fontSize: 16 }}
            />
            <Text type="secondary" style={{ fontSize: 12, display: "block", marginTop: 8 }}>
              网关错误率 {mockBillingHealth.gatewayErrorRatePct}%
            </Text>
          </Card>
        </Col>
        <Col xs={24} md={14}>
          <Card size="small" className="admin-panel-card" title={BILLING_OVERVIEW.gatewayErrorTitle}>
            <Table
              rowKey="errorClass"
              size="small"
              pagination={false}
              dataSource={mockBillingGatewayErrors}
              columns={[
                { title: "类型", dataIndex: "errorClass", ellipsis: true },
                { title: "次数", dataIndex: "count", align: "right", width: 72 },
              ]}
            />
          </Card>
        </Col>
      </Row>

      {commerce.phase2RailsEnabled ? (
        <Spin spinning={commerceLoading}>
          <Card
            size="small"
            className="admin-panel-card"
            title={BILLING_OVERVIEW.commerceSection}
            extra={<Link to={billingOpsLink("subscriptions")}>{BILLING_OVERVIEW.commerceQuotaLink}</Link>}
          >
            <Statistic title={BILLING_OVERVIEW.commerceQuotaTitle} value={quotaBlockedTotal} />
            {commerceSource === "remote" ? (
              <Tag color="processing" style={{ marginTop: 8 }}>
                {BILLING_COMMERCE.sourceRemote}
              </Tag>
            ) : null}
          </Card>
        </Spin>
      ) : (
        <Alert
          type="warning"
          showIcon
          message={BILLING_OVERVIEW.commerceDisabledTitle}
          description={BILLING_OVERVIEW.commerceDisabledBody}
        />
      )}
    </ProductPageShell>
  );
}
