import { CopyOutlined } from "@ant-design/icons";
import { App, Button, Descriptions, Divider, Drawer, Space, Tag, Typography } from "antd";
import { Link } from "react-router-dom";
import { BILLING_ORDERS } from "../../copy/opsPanelHints";
import type { MockCommerceCryptoOrder } from "../../data/types";
import { billingOpsLink } from "./billingPaths";
import type { CommerceOrderProductView } from "./commerceOrderProduct";
import {
  formatBillingDateTime,
  grantStatusTag,
  orderStatusTag,
  zhCommerceOrderKind,
  zhPaymentNetwork,
} from "./billingShared";
import { formatCommerceOrderIdDisplay } from "./commerceOrderId";

const { Text, Title } = Typography;

type Props = {
  open: boolean;
  order: MockCommerceCryptoOrder | null;
  product: CommerceOrderProductView | null;
  onClose: () => void;
};

function confirmationsLine(order: MockCommerceCryptoOrder): string {
  const got = order.confirmationsReceived;
  const need = order.confirmationsRequired;
  if (got == null && need == null) return "—";
  if (need == null) return String(got ?? "—");
  return `${got ?? 0} / ${need}`;
}

export function CommerceOrderDetailDrawer({ open, order, product, onClose }: Props) {
  const { message } = App.useApp();

  const productTab = product?.productKind === "tier" ? "subscriptions" : "packs";

  return (
    <Drawer
      title={BILLING_ORDERS.detailTitle}
      width={600}
      open={open && !!order}
      onClose={onClose}
      destroyOnClose
      footer={
        order ? (
          <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
            <Space wrap>
              {order.kind === "pack" && order.status === "SETTLED" ? (
                <Button
                  onClick={() => {
                    message.success(BILLING_ORDERS.packGrantSuccess);
                  }}
                >
                  {BILLING_ORDERS.packGrantDemo}
                </Button>
              ) : null}
            </Space>
            <Button onClick={onClose}>关闭</Button>
          </div>
        ) : null
      }
    >
      {order && product ? (
        <>
          <Title level={5} style={{ marginTop: 0 }}>
            {BILLING_ORDERS.detailSectionOrder}
          </Title>
          <Descriptions size="small" column={1} bordered>
            <Descriptions.Item label={BILLING_ORDERS.colOrderId}>
              <Text code style={{ fontSize: 13 }}>
                {formatCommerceOrderIdDisplay(order.orderId)}
              </Text>
              <br />
              <Text type="secondary" style={{ fontSize: 11 }}>
                {BILLING_ORDERS.orderIdRuleHint}
              </Text>
            </Descriptions.Item>
            <Descriptions.Item label={BILLING_ORDERS.colStatus}>{orderStatusTag(order.status)}</Descriptions.Item>
            <Descriptions.Item label={BILLING_ORDERS.colKind}>
              <Tag color={order.kind === "upgrade" ? "blue" : "purple"}>{zhCommerceOrderKind(order.kind)}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label={BILLING_ORDERS.colProduct}>
              <div>
                <Text strong>{product.title}</Text>
                <br />
                <Text type="secondary" code style={{ fontSize: 12 }}>
                  {product.productId}
                </Text>
              </div>
            </Descriptions.Item>
            <Descriptions.Item label={BILLING_ORDERS.colUser}>
              <Link to={billingOpsLink("consumption", { userId: order.userIdMasked })}>
                {order.userIdMasked}
              </Link>
            </Descriptions.Item>
            <Descriptions.Item label={BILLING_ORDERS.colCreatedAt}>
              {formatBillingDateTime(order.createdAt)}
            </Descriptions.Item>
          </Descriptions>

          <Divider style={{ margin: "16px 0" }} />
          <Title level={5}>{BILLING_ORDERS.detailSectionPayment}</Title>
          <Descriptions size="small" column={1} bordered>
            <Descriptions.Item label={BILLING_ORDERS.colPayment}>
              <Text strong>{order.amountUsdt} USDT</Text>
              {" · "}
              {zhPaymentNetwork(order.network)}
            </Descriptions.Item>
            <Descriptions.Item label={BILLING_ORDERS.detailListPrice}>
              {order.listPriceUsdt} USDT
              {order.listPriceUsdt !== order.amountUsdt ? (
                <Text type="warning" style={{ marginLeft: 8 }}>
                  （与实付不一致，需对账）
                </Text>
              ) : null}
            </Descriptions.Item>
            {order.expiresAt ? (
              <Descriptions.Item label={BILLING_ORDERS.detailExpiresAt}>
                {formatBillingDateTime(order.expiresAt)}
              </Descriptions.Item>
            ) : null}
            <Descriptions.Item label={BILLING_ORDERS.detailUserPaymentAddress}>
              <Space align="start" wrap>
                <Text code style={{ fontSize: 12, wordBreak: "break-all", maxWidth: 420 }}>
                  {order.paymentAddress}
                </Text>
                <Button
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => {
                    void navigator.clipboard.writeText(order.paymentAddress).then(
                      () => message.success("已复制用户支付地址"),
                      () => message.error("复制失败"),
                    );
                  }}
                >
                  {BILLING_ORDERS.detailCopyAddress}
                </Button>
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label={BILLING_ORDERS.detailConfirmations}>
              {confirmationsLine(order)}
            </Descriptions.Item>
          </Descriptions>

          {(order.settledAt || order.txHashMasked || order.pspReference) && (
            <>
              <Divider style={{ margin: "16px 0" }} />
              <Title level={5}>{BILLING_ORDERS.detailSectionChain}</Title>
              <Descriptions size="small" column={1} bordered>
                {order.settledAt ? (
                  <Descriptions.Item label={BILLING_ORDERS.detailSettledAt}>
                    {formatBillingDateTime(order.settledAt)}
                  </Descriptions.Item>
                ) : null}
                {order.payerAddressMasked ? (
                  <Descriptions.Item label={BILLING_ORDERS.detailPayerAddress}>
                    <Text code style={{ wordBreak: "break-all" }}>
                      {order.payerAddressMasked}
                    </Text>
                  </Descriptions.Item>
                ) : null}
                {order.txHashMasked ? (
                  <Descriptions.Item label={BILLING_ORDERS.detailTx}>
                    <Text code>{order.txHashMasked}</Text>
                  </Descriptions.Item>
                ) : null}
                {order.pspReference ? (
                  <Descriptions.Item label={BILLING_ORDERS.detailPspRef}>
                    <Text code>{order.pspReference}</Text>
                  </Descriptions.Item>
                ) : null}
              </Descriptions>
            </>
          )}

          <Divider style={{ margin: "16px 0" }} />
          <Title level={5}>{BILLING_ORDERS.detailSectionEntitlement}</Title>
          <Descriptions size="small" column={1} bordered>
            <Descriptions.Item label={BILLING_ORDERS.detailGrantStatus}>
              {grantStatusTag(order.grantStatus)}
            </Descriptions.Item>
            {order.grantAppliedAt ? (
              <Descriptions.Item label={BILLING_ORDERS.detailGrantAppliedAt}>
                {formatBillingDateTime(order.grantAppliedAt)}
              </Descriptions.Item>
            ) : null}
            {order.kind === "pack" && order.packGrantId ? (
              <Descriptions.Item label={BILLING_ORDERS.detailPackGrantId}>
                <Text code>{order.packGrantId}</Text>
              </Descriptions.Item>
            ) : null}
            {(order.capabilitySkuId ?? product.capabilitySkuId) ? (
              <Descriptions.Item label={BILLING_ORDERS.detailCapability}>
                <Text code>{order.capabilitySkuId ?? product.capabilitySkuId}</Text>
              </Descriptions.Item>
            ) : null}
            {order.quotaUnits != null ? (
              <Descriptions.Item label={BILLING_ORDERS.detailQuota}>
                {order.quotaUnits.toLocaleString("zh-CN")} 单位
                {order.periodLabel ?? product.periodLabel
                  ? ` · ${order.periodLabel ?? product.periodLabel}`
                  : null}
              </Descriptions.Item>
            ) : order.kind === "upgrade" && product.periodLabel ? (
              <Descriptions.Item label={BILLING_ORDERS.detailPeriod}>
                {product.periodLabel}
              </Descriptions.Item>
            ) : null}
            {order.kind === "upgrade" && order.subscriptionTierSku ? (
              <Descriptions.Item label={BILLING_ORDERS.detailTierSku}>
                <Text code>{order.subscriptionTierSku}</Text>
                {product.tierDisplayName ? (
                  <Text type="secondary" style={{ marginLeft: 8 }}>
                    ({product.tierDisplayName})
                  </Text>
                ) : null}
              </Descriptions.Item>
            ) : null}
            {order.entitlementPeriodEnd ? (
              <Descriptions.Item label={BILLING_ORDERS.detailPeriodEnd}>
                {formatBillingDateTime(order.entitlementPeriodEnd)}
              </Descriptions.Item>
            ) : null}
          </Descriptions>

          <Space style={{ marginTop: 16 }} wrap>
            <Link to={billingOpsLink("consumption", { userId: order.userIdMasked })}>
              <Button type="link" style={{ padding: 0 }}>
                {BILLING_ORDERS.detailOpenConsumption}
              </Button>
            </Link>
            <Link to={billingOpsLink(productTab, { productId: product.productId })}>
              <Button type="link" style={{ padding: 0 }}>
                {BILLING_ORDERS.detailOpenProduct}
              </Button>
            </Link>
          </Space>
          {order.kind === "pack" ? (
            <Text type="secondary" style={{ display: "block", marginTop: 12, fontSize: 12 }}>
              {BILLING_ORDERS.packGrantHint}
            </Text>
          ) : null}
        </>
      ) : null}
    </Drawer>
  );
}
