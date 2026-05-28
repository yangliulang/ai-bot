import { ArrowLeftOutlined } from "@ant-design/icons";
import { Typography } from "antd";
import { Link, useSearchParams } from "react-router-dom";
import { CryptoPaymentPanel } from "@/components/subscription/CryptoPaymentPanel";
import { SUBSCRIPTION_COPY } from "@/copy/subscriptionCopy";
import type { CheckoutKind } from "@/hooks/useCryptoCheckout";

const { Title } = Typography;

function parseKind(raw: string | null): CheckoutKind {
  return raw === "pack" ? "pack" : "upgrade";
}

export default function SubscriptionCheckoutPage() {
  const [params] = useSearchParams();
  const kind = parseKind(params.get("kind"));
  const sku = params.get("sku") ?? "";
  const back =
    kind === "pack" ? "/subscription/pack" : "/subscription/upgrade";

  return (
    <>
      <header style={{ marginBottom: 20 }}>
        <Link to={back} className="coolbit-link-muted" style={{ fontSize: 14 }}>
          <ArrowLeftOutlined /> 返回上一步
        </Link>
        <Title level={3} style={{ marginTop: 12, marginBottom: 0 }}>
          {SUBSCRIPTION_COPY.checkoutTitle}
        </Title>
      </header>
      <CryptoPaymentPanel kind={kind} sku={sku} />
    </>
  );
}
