import { Alert, Button, Card, Form, Input, Select, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { BILLING_ORDERS } from "../../copy/opsPanelHints";
import { MOCK_COMMERCE_CRYPTO_ORDERS } from "../../data/subscriptionCatalogMock";
import type { MockCommerceCryptoOrder, MockCommerceCryptoOrderStatus } from "../../data/types";
import { useResourcePacks } from "../../hooks/useResourcePacks";
import { useSubscriptionTiers } from "../../hooks/useSubscriptionTiers";
import { billingOpsLink } from "./billingPaths";
import { CommerceOrderDetailDrawer } from "./CommerceOrderDetailDrawer";
import { resolveCommerceOrderProduct } from "./commerceOrderProduct";
import {
  formatBillingDateTime,
  orderStatusTag,
  zhCommerceOrderKind,
  zhPaymentNetwork,
} from "./billingShared";
import { formatCommerceOrderIdDisplay } from "./commerceOrderId";
import {
  filterCommerceOrders,
  hasActiveOrdersQuery,
  ordersPanelQueryToSearchParams,
  parseOrdersPanelQuery,
  type OrdersPanelQuery,
} from "./ordersPanelQuery";

const { Text, Link: TypographyLink } = Typography;
const { CheckableTag } = Tag;

/** 列宽：商品收窄；支付、状态加宽 */
const COL = {
  orderId: 156,
  createdAt: 166,
  user: 100,
  product: 168,
  payment: 156,
  status: 112,
} as const;
const ORDERS_TABLE_SCROLL_X = Object.values(COL).reduce((a, b) => a + b, 0);

const STATUS_OPTIONS: { value: MockCommerceCryptoOrderStatus; label: string }[] = [
  { value: "PENDING", label: BILLING_ORDERS.statPending },
  { value: "CONFIRMING", label: BILLING_ORDERS.statConfirming },
  { value: "SETTLED", label: BILLING_ORDERS.statSettled },
  { value: "EXPIRED", label: BILLING_ORDERS.statExpired },
];

const KIND_OPTIONS = [
  { value: "upgrade", label: "订阅升级" },
  { value: "pack", label: "资源加购" },
] as const;

const NETWORK_OPTIONS = [
  { value: "USDT_TRC20", label: "TRC20" },
  { value: "USDT_ERC20", label: "ERC20" },
] as const;

const STATUS_CHIP_META: { key: MockCommerceCryptoOrderStatus; label: string }[] = [
  { key: "PENDING", label: BILLING_ORDERS.statPending },
  { key: "CONFIRMING", label: BILLING_ORDERS.statConfirming },
  { key: "SETTLED", label: BILLING_ORDERS.statSettled },
  { key: "EXPIRED", label: BILLING_ORDERS.statExpired },
];

const EMPTY_QUERY: OrdersPanelQuery = {
  orderId: "",
  userId: "",
  productId: "",
  kind: "",
  status: "",
  network: "",
};

export function OrdersPanel() {
  const [searchParams, setSearchParams] = useSearchParams();
  const appliedQuery = useMemo(() => parseOrdersPanelQuery(searchParams), [searchParams]);
  const [draftQuery, setDraftQuery] = useState<OrdersPanelQuery>(appliedQuery);

  useEffect(() => {
    setDraftQuery(appliedQuery);
  }, [
    appliedQuery.orderId,
    appliedQuery.userId,
    appliedQuery.productId,
    appliedQuery.kind,
    appliedQuery.status,
    appliedQuery.network,
  ]);

  const { tiers } = useSubscriptionTiers();
  const { packs } = useResourcePacks();

  const [selected, setSelected] = useState<MockCommerceCryptoOrder | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);

  const productResolver = useMemo(
    () => (order: MockCommerceCryptoOrder) =>
      resolveCommerceOrderProduct(order.kind, order.productId, tiers, packs),
    [tiers, packs],
  );

  const productOptions = useMemo(
    () => [
      {
        label: "订阅套餐",
        options: tiers.map((t) => ({
          value: t.tierId,
          label: `${t.name} · ${t.tierId}`,
        })),
      },
      {
        label: "加购资源",
        options: packs
          .filter((p) => p.packKind === "addon")
          .map((p) => ({
            value: p.resourceId,
            label: `${p.name} · ${p.resourceId}`,
          })),
      },
    ],
    [tiers, packs],
  );

  const filteredRows = useMemo(
    () =>
      filterCommerceOrders(MOCK_COMMERCE_CRYPTO_ORDERS, appliedQuery).sort((a, b) =>
        b.createdAt.localeCompare(a.createdAt),
      ),
    [appliedQuery],
  );

  const statusCounts = useMemo(() => {
    const base = filterCommerceOrders(MOCK_COMMERCE_CRYPTO_ORDERS, {
      ...appliedQuery,
      status: "",
    });
    return {
      PENDING: base.filter((o) => o.status === "PENDING").length,
      CONFIRMING: base.filter((o) => o.status === "CONFIRMING").length,
      SETTLED: base.filter((o) => o.status === "SETTLED").length,
      EXPIRED: base.filter((o) => o.status === "EXPIRED").length,
      all: base.length,
    };
  }, [appliedQuery]);

  const applyQuery = (next: OrdersPanelQuery) => {
    setDraftQuery(next);
    setSearchParams(ordersPanelQueryToSearchParams(next, searchParams));
  };

  const resetQuery = () => {
    setDraftQuery(EMPTY_QUERY);
    setSearchParams(ordersPanelQueryToSearchParams(EMPTY_QUERY));
  };

  const setDraftField = <K extends keyof OrdersPanelQuery>(key: K, value: OrdersPanelQuery[K]) => {
    setDraftQuery((prev) => ({ ...prev, [key]: value }));
  };

  const openDetail = (order: MockCommerceCryptoOrder) => {
    setSelected(order);
    setDetailOpen(true);
  };

  const columns: ColumnsType<MockCommerceCryptoOrder> = [
    {
      title: BILLING_ORDERS.colOrderId,
      dataIndex: "orderId",
      width: COL.orderId,
      ellipsis: true,
      render: (id: string, row) => (
        <TypographyLink
          onClick={() => openDetail(row)}
          style={{ fontFamily: "monospace", fontSize: 12 }}
        >
          {formatCommerceOrderIdDisplay(id)}
        </TypographyLink>
      ),
    },
    {
      title: BILLING_ORDERS.colCreatedAt,
      dataIndex: "createdAt",
      width: COL.createdAt,
      ellipsis: true,
      render: (v: string) => <Text style={{ fontSize: 13 }}>{formatBillingDateTime(v)}</Text>,
    },
    {
      title: BILLING_ORDERS.colUser,
      dataIndex: "userIdMasked",
      width: COL.user,
      ellipsis: true,
      render: (id: string) => (
        <Link
          to={billingOpsLink("consumption", { userId: id })}
          onClick={(e) => e.stopPropagation()}
        >
          {id}
        </Link>
      ),
    },
    {
      title: BILLING_ORDERS.colProduct,
      key: "product",
      width: COL.product,
      ellipsis: true,
      render: (_, row) => {
        const p = productResolver(row);
        return (
          <div style={{ minWidth: 0 }}>
            <Tag
              color={row.kind === "upgrade" ? "blue" : "purple"}
              style={{ margin: "0 0 2px", fontSize: 11, lineHeight: "18px" }}
            >
              {zhCommerceOrderKind(row.kind)}
            </Tag>
            <Text ellipsis style={{ display: "block", fontSize: 13, lineHeight: 1.35 }}>
              {p.title}
            </Text>
            <Text type="secondary" code style={{ fontSize: 11 }}>
              {p.productId}
            </Text>
          </div>
        );
      },
    },
    {
      title: BILLING_ORDERS.colPayment,
      key: "payment",
      width: COL.payment,
      align: "right",
      render: (_, row) => (
        <div style={{ lineHeight: 1.45, whiteSpace: "nowrap" }}>
          <Text strong>{row.amountUsdt} USDT</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {zhPaymentNetwork(row.network)}
          </Text>
        </div>
      ),
    },
    {
      title: BILLING_ORDERS.colStatus,
      dataIndex: "status",
      width: COL.status,
      align: "center",
      fixed: "right",
      render: (s: MockCommerceCryptoOrderStatus) => orderStatusTag(s),
    },
  ];

  const selectedProduct = selected ? productResolver(selected) : null;

  return (
    <Card size="small" className="admin-panel-card">
      <Form
        layout="inline"
        style={{ marginBottom: 12, rowGap: 8 }}
        onFinish={() => applyQuery(draftQuery)}
      >
        <Form.Item label={BILLING_ORDERS.filterOrderId} style={{ marginBottom: 0 }}>
          <Input
            allowClear
            inputMode="numeric"
            placeholder={BILLING_ORDERS.filterOrderIdPlaceholder}
            value={draftQuery.orderId}
            onChange={(e) => setDraftField("orderId", e.target.value.replace(/\D/g, ""))}
            style={{ width: 168 }}
          />
        </Form.Item>
        <Form.Item label={BILLING_ORDERS.filterUser} style={{ marginBottom: 0 }}>
          <Input
            allowClear
            value={draftQuery.userId}
            onChange={(e) => setDraftField("userId", e.target.value)}
            placeholder="u-10482"
            style={{ width: 120 }}
          />
        </Form.Item>
        <Form.Item label={BILLING_ORDERS.filterProduct} style={{ marginBottom: 0 }}>
          <Select
            allowClear
            showSearch
            optionFilterProp="label"
            placeholder="全部商品"
            style={{ width: 200 }}
            value={draftQuery.productId || undefined}
            onChange={(v) => setDraftField("productId", v ?? "")}
            options={productOptions}
          />
        </Form.Item>
        <Form.Item label={BILLING_ORDERS.filterKind} style={{ marginBottom: 0 }}>
          <Select
            allowClear
            placeholder="全部类型"
            style={{ width: 112 }}
            value={draftQuery.kind || undefined}
            onChange={(v) => setDraftField("kind", (v ?? "") as OrdersPanelQuery["kind"])}
            options={[...KIND_OPTIONS]}
          />
        </Form.Item>
        <Form.Item label={BILLING_ORDERS.filterStatus} style={{ marginBottom: 0 }}>
          <Select
            allowClear
            placeholder="全部状态"
            style={{ width: 112 }}
            value={draftQuery.status || undefined}
            onChange={(v) => setDraftField("status", (v ?? "") as OrdersPanelQuery["status"])}
            options={STATUS_OPTIONS}
          />
        </Form.Item>
        <Form.Item label={BILLING_ORDERS.filterNetwork} style={{ marginBottom: 0 }}>
          <Select
            allowClear
            placeholder="全部"
            style={{ width: 96 }}
            value={draftQuery.network || undefined}
            onChange={(v) => setDraftField("network", (v ?? "") as OrdersPanelQuery["network"])}
            options={[...NETWORK_OPTIONS]}
          />
        </Form.Item>
        <Form.Item style={{ marginBottom: 0 }}>
          <Space>
            <Button type="primary" htmlType="submit">
              {BILLING_ORDERS.filterQuery}
            </Button>
            <Button onClick={resetQuery}>{BILLING_ORDERS.filterReset}</Button>
          </Space>
        </Form.Item>
      </Form>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 8,
          marginBottom: 12,
        }}
      >
        <Space size={[8, 8]} wrap>
          <CheckableTag
            checked={!appliedQuery.status}
            onChange={() => applyQuery({ ...appliedQuery, status: "" })}
          >
            {BILLING_ORDERS.statAll} {statusCounts.all}
          </CheckableTag>
          {STATUS_CHIP_META.map(({ key, label }) => (
            <CheckableTag
              key={key}
              checked={appliedQuery.status === key}
              onChange={(checked) =>
                applyQuery({ ...appliedQuery, status: checked ? key : "" })
              }
            >
              {label} {statusCounts[key]}
            </CheckableTag>
          ))}
        </Space>
        <Space>
          <Text type="secondary" style={{ fontSize: 13 }}>
            {BILLING_ORDERS.filterResultCount(filteredRows.length)}
          </Text>
          <Tag>{BILLING_ORDERS.localPreviewTag}</Tag>
        </Space>
      </div>

      {hasActiveOrdersQuery(appliedQuery) ? (
        <Alert
          type="info"
          showIcon
          closable
          style={{ marginBottom: 12 }}
          onClose={resetQuery}
          message={
            <>
              {BILLING_ORDERS.filterResultCount(filteredRows.length)}
              {appliedQuery.productId ? (
                <>
                  {" "}
                  · {BILLING_ORDERS.filterProduct} {appliedQuery.productId}
                </>
              ) : null}
              {" · "}
              <TypographyLink onClick={resetQuery}>{BILLING_ORDERS.filterReset}</TypographyLink>
            </>
          }
        />
      ) : null}

      <Table
        rowKey="orderId"
        size="small"
        tableLayout="fixed"
        scroll={{ x: ORDERS_TABLE_SCROLL_X }}
        pagination={{ pageSize: 10, hideOnSinglePage: true, showTotal: (t) => `共 ${t} 条` }}
        dataSource={filteredRows}
        columns={columns}
        locale={{ emptyText: BILLING_ORDERS.emptyTable }}
        onRow={(row) => ({
          onClick: (e) => {
            if ((e.target as HTMLElement).closest("a")) return;
            openDetail(row);
          },
          style: { cursor: "pointer" },
        })}
      />

      <CommerceOrderDetailDrawer
        open={detailOpen}
        order={selected}
        product={selectedProduct}
        onClose={() => {
          setDetailOpen(false);
          setSelected(null);
        }}
      />
    </Card>
  );
}
