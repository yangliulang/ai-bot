import {
  CrownOutlined,
  InfoCircleOutlined,
  ShoppingCartOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { Alert, Button, Col, Progress, Row, Space, Spin, Tag, Tooltip, Typography } from "antd";
import { Link } from "react-router-dom";
import { quotaBucketAccent } from "@/components/billing/billingUi";
import { AGENT_BILLING_COPY } from "@/copy/agentBillingCopy";
import { labelCapabilitySku } from "@/data/meCommerceMock";
import type { MeCommerceEntitlementsSummary } from "@/data/meCommerceMock";
import type { MeCommerceDataSource } from "@/hooks/useMeCommerceSummary";

const { Paragraph, Text, Title } = Typography;

type Props = {
  summary: MeCommerceEntitlementsSummary;
  source: MeCommerceDataSource;
  loading: boolean;
};

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString("zh-CN");
  } catch {
    return iso;
  }
}

function sourceTag(source: MeCommerceDataSource) {
  if (source === "remote") return <Tag bordered={false}>已接 API</Tag>;
  if (source === "remote+fallback") return <Tag color="warning">回退演示数据</Tag>;
  return <Tag bordered={false}>演示</Tag>;
}

/** 配额摘要（FR-B17 / SC-WEB-07） */
export function CommerceQuotaOverview({ summary, source, loading }: Props) {
  const hasExhausted = summary.buckets.some((b) => b.remaining <= 0);
  const tier = summary.subscriptionTierDisplay ?? "未订阅";
  const totalRemaining = summary.buckets.reduce((s, b) => s + Math.max(0, b.remaining), 0);

  return (
    <section id="commerce-quota-overview" className="coolbit-billing-quota" aria-label="订阅与能力配额">
      <div className="coolbit-billing-hero">
        <Spin spinning={loading}>
          <div className="coolbit-billing-hero__inner">
            <div className="coolbit-billing-hero__main">
              <div className="coolbit-billing-hero__badges">
                <span className="coolbit-billing-rail-pill">Capability 配额</span>
                <Tag color="gold" icon={<CrownOutlined />} bordered={false}>
                  {AGENT_BILLING_COPY.tierActiveTag}
                </Tag>
                {sourceTag(source)}
              </div>
              <Title level={3} className="coolbit-billing-hero__tier">
                {tier}
              </Title>
              <Space wrap size={[12, 4]} className="coolbit-billing-hero__meta">
                <Text type="secondary">
                  {AGENT_BILLING_COPY.periodEndLabel} {formatDate(summary.periodEnd)}
                </Text>
                <Text type="secondary">
                  合计剩余 <Text strong>{totalRemaining.toLocaleString("zh-CN")}</Text> 单位
                </Text>
              </Space>
              <Paragraph type="secondary" className="coolbit-billing-hero__intro">
                {AGENT_BILLING_COPY.quotaSectionIntro}
                <Tooltip title={AGENT_BILLING_COPY.billingPolicyDetail}>
                  <InfoCircleOutlined className="coolbit-billing-hero__info-icon" aria-label="计费说明" />
                </Tooltip>
              </Paragraph>
            </div>
            <div className="coolbit-billing-hero__actions">
              <Link to="/subscription/upgrade">
                <Button type="primary" size="large" block icon={<ThunderboltOutlined />}>
                  {AGENT_BILLING_COPY.upgradeCta}
                </Button>
              </Link>
              <Link to="/subscription/pack">
                <Button size="large" block icon={<ShoppingCartOutlined />}>
                  {AGENT_BILLING_COPY.buyPackCta}
                </Button>
              </Link>
            </div>
          </div>
        </Spin>
      </div>

      {hasExhausted ? (
        <Alert
          type="warning"
          showIcon
          className="coolbit-billing-exhausted-alert"
          message={AGENT_BILLING_COPY.quotaExhaustedTitle}
          description={
            <>
              {AGENT_BILLING_COPY.quotaExhaustedBody}
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                billCode（演示）：{AGENT_BILLING_COPY.quotaExhaustedBillCode} · 非{" "}
                {AGENT_BILLING_COPY.usdtInsufficientBillCode}
              </Text>
            </>
          }
          action={
            <Link to="/subscription/upgrade">
              <Button size="small" type="primary">
                去升级
              </Button>
            </Link>
          }
        />
      ) : null}

      <div className="coolbit-billing-quota__grid-label">{AGENT_BILLING_COPY.capabilityBucketsTitle}</div>
      <Spin spinning={loading}>
        <Row gutter={[12, 12]} className="coolbit-billing-quota__grid">
          {summary.buckets.map((b) => {
            const used = Math.max(0, b.quotaTotal - b.remaining);
            const pct = b.quotaTotal > 0 ? Math.round((used / b.quotaTotal) * 100) : 0;
            const exhausted = b.remaining <= 0;
            const accent = quotaBucketAccent(b.capabilitySkuId);
            return (
              <Col xs={24} sm={12} lg={8} key={b.capabilitySkuId}>
                <div
                  className={[
                    "coolbit-billing-quota-card",
                    `coolbit-billing-quota-card--${accent}`,
                    exhausted ? "coolbit-billing-quota-card--exhausted" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                >
                  <div className="coolbit-billing-quota-card__head">
                    <Text strong className="coolbit-billing-quota-card__title">
                      {b.displayLabel || labelCapabilitySku(b.capabilitySkuId)}
                    </Text>
                    {exhausted ? (
                      <Tag color="error" bordered={false}>
                        用尽
                      </Tag>
                    ) : (
                      <Tag color="success" bordered={false}>
                        可用
                      </Tag>
                    )}
                  </div>
                  <Progress
                    percent={pct}
                    showInfo={false}
                    strokeWidth={8}
                    status={exhausted ? "exception" : "active"}
                    className="coolbit-billing-quota-card__progress"
                  />
                  <div className="coolbit-billing-quota-card__stats">
                    <Text className="coolbit-billing-quota-card__remain">
                      {b.remaining.toLocaleString("zh-CN")}
                      <span className="coolbit-billing-quota-card__remain-label"> 剩余</span>
                    </Text>
                    <Text type="secondary" className="coolbit-billing-quota-card__used">
                      / {b.quotaTotal.toLocaleString("zh-CN")}
                      {b.resetsAt
                        ? ` · ${formatDate(b.resetsAt)} 重置`
                        : ` · ${AGENT_BILLING_COPY.packGranularityHint}`}
                    </Text>
                  </div>
                </div>
              </Col>
            );
          })}
        </Row>
        <Paragraph type="secondary" className="coolbit-billing-quota__footnote">
          {AGENT_BILLING_COPY.usdtFundsHint}
          <br />
          {AGENT_BILLING_COPY.billCodeFootnote}
        </Paragraph>
      </Spin>
    </section>
  );
}
