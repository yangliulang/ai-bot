import { Collapse, theme, Typography } from "antd";
import type { ReactNode } from "react";

const { Text } = Typography;

/** 页脚可折叠说明区 — 不占首屏，替代大块流程提示卡 */
export function BillingSpecCollapse({
  title,
  children,
  defaultOpen = false,
}: {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
}) {
  const { token } = theme.useToken();
  return (
    <Collapse
      bordered={false}
      defaultActiveKey={defaultOpen ? ["help"] : []}
      style={{
        marginTop: 24,
        background: token.colorFillAlter,
        borderRadius: token.borderRadiusLG,
      }}
      items={[
        {
          key: "help",
          label: <Text type="secondary">{title}</Text>,
          children: <div style={{ paddingBottom: 8, fontSize: 13, color: token.colorTextSecondary }}>{children}</div>,
        },
      ]}
    />
  );
}
