import { Alert, Button, Card, Input, Space, Table, Tag, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { zhCapabilitySku } from "../../copy/billingLabels";
import { BILLING_CONSUMPTION } from "../../copy/opsPanelHints";
import { mockBillingLedger } from "../../data/mockBillingData";
import { useCommerceUserOverview } from "../../hooks/useCommerceAdminSnapshot";
import { billingOpsLink } from "./billingPaths";
import { formatBillingDate } from "./billingShared";
import { entitlementDebitStatusTag } from "./debitStatusTag";
import type { MockEntitlementDebitDisplayStatus } from "../../data/types";

const { Text } = Typography;

export function ConsumptionPanel() {
  const [searchParams, setSearchParams] = useSearchParams();
  const userFromUrl = searchParams.get("userId")?.trim() ?? "";
  const [userLookup, setUserLookup] = useState(userFromUrl || "u-10482");
  const apiOn = false;
  const { rows: bucketRows, executionAnchors, subscription, loading } = useCommerceUserOverview(
    userLookup,
    apiOn,
  );

  useEffect(() => {
    if (userFromUrl) setUserLookup(userFromUrl);
  }, [userFromUrl]);

  const ledgerRows = useMemo(() => {
    const q = userLookup.trim().toLowerCase();
    if (!q) return [];
    return mockBillingLedger
      .filter((r) => r.userIdMasked.toLowerCase() === q)
      .sort((a, b) => b.recordedAt.localeCompare(a.recordedAt));
  }, [userLookup]);

  const applyUser = () => {
    const p = new URLSearchParams(searchParams);
    p.set("tab", "consumption");
    const id = userLookup.trim();
    if (id) p.set("userId", id);
    else p.delete("userId");
    setSearchParams(p);
  };

  return (
    <>
      <Card size="small" className="admin-panel-card" style={{ marginBottom: 16 }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12,
            marginBottom: 12,
          }}
        >
          <Space wrap>
            <Input
              addonBefore={BILLING_CONSUMPTION.filterUser}
              value={userLookup}
              onChange={(e) => setUserLookup(e.target.value)}
              onPressEnter={applyUser}
              style={{ width: 260 }}
              allowClear
            />
            <Button type="primary" size="small" onClick={applyUser}>
              {BILLING_CONSUMPTION.queryButton}
            </Button>
          </Space>
          <Tag>{BILLING_CONSUMPTION.localPreviewTag}</Tag>
        </div>

        {subscription ? (
          <Alert
            type="info"
            showIcon
            style={{ marginBottom: 12 }}
            message={
              <>
                {BILLING_CONSUMPTION.subscriptionLabel}{" "}
                <Text strong>{subscription.tierDisplay}</Text>
                {subscription.periodEnd ? (
                  <>
                    {" "}
                    · {BILLING_CONSUMPTION.periodEndLabel} {formatBillingDate(subscription.periodEnd)}
                  </>
                ) : null}
              </>
            }
          />
        ) : null}

        <Table
          rowKey={(r) => `${r.capabilitySkuId}-${r.displayLabel}`}
          size="small"
          pagination={false}
          loading={loading}
          locale={{ emptyText: BILLING_CONSUMPTION.bucketEmpty }}
          dataSource={bucketRows}
          columns={[
            {
              title: BILLING_CONSUMPTION.colCapability,
              dataIndex: "capabilitySkuId",
              render: (s: string) => zhCapabilitySku(s),
            },
            {
              title: BILLING_CONSUMPTION.colRemaining,
              dataIndex: "remaining",
              width: 120,
              align: "right",
              render: (n: number) => n.toLocaleString("zh-CN"),
            },
          ]}
        />
        {executionAnchors.length > 0 ? (
          <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: "block" }}>
            {BILLING_CONSUMPTION.recentExecutions}{" "}
            {executionAnchors.map((id) => (
              <Link key={id} to={`/runtime/executions/${encodeURIComponent(id)}`}>
                <Text code style={{ fontSize: 11 }}>
                  {id}
                </Text>
              </Link>
            ))}
          </Text>
        ) : null}
      </Card>

      <Card
        size="small"
        className="admin-panel-card"
        title={BILLING_CONSUMPTION.ledgerTitle}
        extra={
          <Link to={`/billing/ledger?userId=${encodeURIComponent(userLookup.trim())}`}>
            {BILLING_CONSUMPTION.ledgerLink}
          </Link>
        }
      >
        <Table
          rowKey="billingTraceId"
          size="small"
          pagination={{ pageSize: 6, hideOnSinglePage: true }}
          locale={{ emptyText: BILLING_CONSUMPTION.ledgerEmpty }}
          dataSource={ledgerRows}
          columns={[
            {
              title: BILLING_CONSUMPTION.colTime,
              dataIndex: "recordedAt",
              width: 132,
              render: (v: string) => v.slice(0, 16).replace("T", " "),
            },
            {
              title: BILLING_CONSUMPTION.colCapability,
              dataIndex: "capabilitySkuId",
              render: (s: string) => zhCapabilitySku(s),
            },
            {
              title: BILLING_CONSUMPTION.colStatus,
              dataIndex: "debitStatus",
              width: 96,
              render: (s: string) => entitlementDebitStatusTag(s as MockEntitlementDebitDisplayStatus),
            },
            {
              title: BILLING_CONSUMPTION.colExecution,
              dataIndex: "executionId",
              ellipsis: true,
              render: (id: string) => (
                <Link to={`/runtime/executions/${encodeURIComponent(id)}`}>
                  <Text code style={{ fontSize: 11 }}>
                    {id}
                  </Text>
                </Link>
              ),
            },
          ]}
        />
      </Card>
    </>
  );
}
