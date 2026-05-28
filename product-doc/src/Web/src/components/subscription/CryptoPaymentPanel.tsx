import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  CopyOutlined,
  QrcodeOutlined,
  SafetyOutlined,
} from "@ant-design/icons";
import { Alert, Button, Card, Descriptions, Radio, Space, Steps, Typography, message } from "antd";
import { Link } from "react-router-dom";
import { SUBSCRIPTION_COPY } from "@/copy/subscriptionCopy";
import type { CryptoCheckoutStep, CryptoNetworkId } from "@/hooks/useCryptoCheckout";
import { useCryptoCheckout } from "@/hooks/useCryptoCheckout";

const { Paragraph, Text, Title } = Typography;

type Props = {
  kind: "upgrade" | "pack";
  sku: string;
};

function formatCountdown(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

async function copyText(text: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text);
    message.success("已复制");
  } catch {
    message.error("复制失败");
  }
}

export function CryptoPaymentPanel({ kind, sku }: Props) {
  const c = useCryptoCheckout(kind, sku);

  if (!c.product) {
    return (
      <Alert
        type="error"
        message="无效商品"
        action={
          <Link to={kind === "upgrade" ? "/subscription/upgrade" : "/subscription/pack"}>返回选择</Link>
        }
      />
    );
  }

  const stepIndex: Record<CryptoCheckoutStep, number> = {
    review: 0,
    transfer: 1,
    confirming: 2,
    success: 3,
    expired: 1,
  };

  return (
    <div className="coolbit-crypto-checkout">
      <Steps
        current={stepIndex[c.step]}
        items={[
          { title: "确认订单" },
          { title: "链上转账" },
          { title: "确认中" },
          { title: "完成" },
        ]}
        style={{ marginBottom: 24 }}
      />

      <Alert type="info" showIcon style={{ marginBottom: 16 }} message={SUBSCRIPTION_COPY.demoDisclaimer} />

      {c.step === "review" ? (
        <Card bordered={false} className="coolbit-billing-card">
          <Title level={5}>{c.title}</Title>
          <Descriptions column={1} size="small" bordered>
            <Descriptions.Item label="订单号">{c.orderId}</Descriptions.Item>
            <Descriptions.Item label="应付金额">
              <Text strong style={{ fontSize: 18 }}>
                {c.amountUsdt} USDT
              </Text>
            </Descriptions.Item>
            <Descriptions.Item label="支付方式">{SUBSCRIPTION_COPY.payWithCrypto}</Descriptions.Item>
          </Descriptions>
          <Paragraph type="secondary" style={{ marginTop: 16, fontSize: 13 }}>
            <SafetyOutlined /> 继续后将展示<strong>用户支付地址</strong>（官方收款地址）；仅向该地址转账，勿信任 Telegram 私聊地址。
          </Paragraph>
          <Radio.Group
            style={{ width: "100%", marginBottom: 20 }}
            value={c.network}
            onChange={(e) => c.setNetwork(e.target.value as CryptoNetworkId)}
            options={c.networks.map((n) => ({ label: n.label, value: n.id }))}
          />
          <Button type="primary" block size="large" onClick={c.startTransfer}>
            继续支付
          </Button>
        </Card>
      ) : null}

      {c.step === "transfer" || c.step === "expired" ? (
        <Card bordered={false} className="coolbit-billing-card">
          <Space style={{ width: "100%", justifyContent: "space-between", marginBottom: 12 }}>
            <Text>
              <ClockCircleOutlined /> 支付剩余 {formatCountdown(c.secondsLeft)}
            </Text>
            <Text type="secondary">
              {c.amountUsdt} USDT · {c.networkMeta.label}
            </Text>
          </Space>
          {c.step === "expired" ? (
            <Alert type="error" message="订单已超时" style={{ marginBottom: 16 }} />
          ) : null}
          <div className="coolbit-crypto-checkout__qr" aria-hidden>
            <QrcodeOutlined style={{ fontSize: 64, color: "#94a3b8" }} />
            <Text type="secondary">收款二维码（演示占位）</Text>
          </div>
          <Descriptions column={1} size="small" bordered style={{ marginTop: 16 }}>
            <Descriptions.Item label="网络">{c.networkMeta.label}</Descriptions.Item>
            <Descriptions.Item label="用户支付地址">
              <Space>
                <Text code style={{ fontSize: 12, wordBreak: "break-all" }}>
                  {c.depositAddress}
                </Text>
                <Button
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => void copyText(c.depositAddress)}
                />
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="转账金额">
              <Text strong>{c.amountUsdt} USDT</Text>
            </Descriptions.Item>
            <Descriptions.Item label="备注/Tag">
              <Space>
                <Text code>{c.orderId}</Text>
                <Button size="small" icon={<CopyOutlined />} onClick={() => void copyText(c.orderId)} />
              </Space>
            </Descriptions.Item>
          </Descriptions>
          <Paragraph type="secondary" style={{ marginTop: 12, fontSize: 12 }}>
            请转入 <strong>精确金额</strong>；少付将需补款，多付按平台规则处理。到账后通常 {c.networkMeta.confirmBlocks}{" "}
            个区块确认生效。
          </Paragraph>
          {c.step === "transfer" ? (
            <Button type="primary" block size="large" style={{ marginTop: 16 }} onClick={c.markPaidDemo}>
              我已完成转账（演示）
            </Button>
          ) : (
            <Button block style={{ marginTop: 16 }} onClick={c.reset}>
              重新下单
            </Button>
          )}
        </Card>
      ) : null}

      {c.step === "confirming" ? (
        <Card bordered={false} className="coolbit-billing-card">
          <Paragraph>
            正在确认链上到账… {c.confirmProgress} / {c.networkMeta.confirmBlocks} 区块
          </Paragraph>
          <div className="coolbit-crypto-checkout__progress" />
        </Card>
      ) : null}

      {c.step === "success" ? (
        <Card bordered={false} className="coolbit-billing-card">
          <Alert
            type="success"
            showIcon
            icon={<CheckCircleOutlined />}
            message="支付成功（演示）"
            description={
              <>
                订单号 <Text code>{c.orderId}</Text>。配额将在数分钟内同步至「账单与消耗」页顶。
                {SUBSCRIPTION_COPY.checkoutAdminOrderNote}
              </>
            }
            style={{ marginBottom: 16 }}
          />
          <Space>
            <Link to="/subscription">
              <Button>返回订阅与购买</Button>
            </Link>
            <Link to="/subaccount/billing">
              <Button type="primary">查看账单与消耗</Button>
            </Link>
          </Space>
        </Card>
      ) : null}
    </div>
  );
}
