import { ShoppingCartOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { Button, Space, Typography } from "antd";
import { Link } from "react-router-dom";
import { AGENT_BILLING_COPY } from "@/copy/agentBillingCopy";

const { Text } = Typography;

type Props = {
  showExhaustedHint?: boolean;
  compact?: boolean;
};

export function CommerceUpgradeActions({ showExhaustedHint, compact }: Props) {
  return (
    <div style={{ marginTop: showExhaustedHint ? 12 : 0 }}>
      <Space wrap size={compact ? "small" : "middle"}>
        <Link to="/subscription/upgrade">
          <Button type="primary" icon={<ThunderboltOutlined />}>
            {AGENT_BILLING_COPY.upgradeCta}
          </Button>
        </Link>
        <Link to="/subscription/pack">
          <Button icon={<ShoppingCartOutlined />}>{AGENT_BILLING_COPY.buyPackCta}</Button>
        </Link>
      </Space>
      {showExhaustedHint ? (
        <Text type="secondary" style={{ display: "block", marginTop: 8, fontSize: 13 }}>
          {AGENT_BILLING_COPY.upgradeHint} {AGENT_BILLING_COPY.buyPackHint}
        </Text>
      ) : null}
    </div>
  );
}
