import { InfoCircleOutlined } from "@ant-design/icons";
import { Space, Tag, Typography, theme } from "antd";
import type { ReactNode } from "react";

const { Title, Paragraph, Text } = Typography;

/** 对齐交易所后台「数据更新时间」信息条，增强产品信任感 */
export function DataFreshnessBar() {
  const { token } = theme.useToken();
  const now = new Date().toLocaleString("zh-CN", { hour12: false });

  return (
    <div
      className="admin-data-freshness-bar"
      style={{
        background: `linear-gradient(90deg, ${token.colorInfoBg} 0%, #f0f9ff 100%)`,
        border: `1px solid ${token.colorPrimaryBorder}`,
        borderRadius: token.borderRadiusLG,
        padding: "10px 16px",
        marginBottom: 20,
        display: "flex",
        alignItems: "center",
        gap: 10,
        fontSize: 13,
        color: token.colorTextSecondary,
      }}
    >
      <InfoCircleOutlined style={{ color: token.colorInfo, fontSize: 16 }} />
      <span>
        数据更新时间：<Text strong style={{ color: token.colorText }}>{now}</Text>
        <Text type="secondary" style={{ marginLeft: 12 }}>
          演示环境 · 本地模拟数据，用于评审交互与信息架构
        </Text>
      </span>
    </div>
  );
}

export interface ProductPageShellProps {
  title: string;
  /** 稳定页面 ID，轻量展示便于研发/运营与规格对齐 */
  pageId?: string;
  /** 是否展示 pageId 标签（运营向页面可关） */
  showPageId?: boolean;
  description?: ReactNode;
  tags?: ReactNode;
  extra?: ReactNode;
  showFreshnessBar?: boolean;
  children: ReactNode;
}

/** 统一页眉：默认不显大号「数据更新时间」条，更接近正式运营后台；需要时在单页传入 showFreshnessBar */
export function ProductPageShell({
  title,
  pageId,
  showPageId = true,
  description,
  tags,
  extra,
  showFreshnessBar = false,
  children,
}: ProductPageShellProps) {
  return (
    <div className="admin-page-shell">
      {showFreshnessBar ? <DataFreshnessBar /> : null}
      <header className="admin-page-hero">
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 16,
            alignItems: "flex-start",
            justifyContent: "space-between",
          }}
        >
          <div style={{ flex: "1 1 280px", minWidth: 0 }}>
            <Title
              level={3}
              style={{
                margin: "0 0 8px",
                fontWeight: 600,
                letterSpacing: "-0.02em",
                lineHeight: 1.25,
              }}
            >
              {title}
            </Title>
            {description ? (
              <Paragraph
                type="secondary"
                style={{ marginBottom: tags || (pageId && showPageId) ? 10 : 0, fontSize: 14, maxWidth: 800 }}
              >
                {description}
              </Paragraph>
            ) : null}
            {tags || (pageId && showPageId) ? (
              <Space size={[8, 8]} wrap className="admin-page-tags">
                {tags}
                {pageId && showPageId ? (
                  <Tag
                    style={{
                      margin: 0,
                      fontSize: 12,
                      color: "rgba(0,0,0,0.45)",
                      borderColor: "rgba(0,0,0,0.15)",
                      background: "rgba(0,0,0,0.02)",
                    }}
                  >
                    {pageId}
                  </Tag>
                ) : null}
              </Space>
            ) : null}
          </div>
          {extra ? <Space wrap>{extra}</Space> : null}
        </div>
      </header>
      <div className="admin-page-body">{children}</div>
    </div>
  );
}
