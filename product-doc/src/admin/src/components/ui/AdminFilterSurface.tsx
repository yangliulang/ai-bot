import { Typography, theme } from "antd";
import type { CSSProperties, ReactNode } from "react";

const { Text } = Typography;

type AdminFilterSurfaceProps = {
  children: ReactNode;
  /** 左上标题，例如「查询条件」 */
  title?: ReactNode;
  /** 右上辅助信息（如命中条数、状态 Tag） */
  extra?: ReactNode;
  /** 底部灰字说明（如 URL 同步规则） */
  footer?: ReactNode;
  className?: string;
  style?: CSSProperties;
};

/**
 * 列表页过滤器统一外壳：留白、分割线、轻微阴影，与主内容区分开。
 */
export function AdminFilterSurface({ children, title, extra, footer, className, style }: AdminFilterSurfaceProps) {
  const { token } = theme.useToken();
  const showHead = title != null || extra != null;

  const mergedClass = ["admin-filter-surface", className].filter(Boolean).join(" ");

  return (
    <div
      className={mergedClass}
      style={{
        padding: "20px 22px",
        marginBottom: 16,
        borderRadius: token.borderRadiusLG,
        background: token.colorBgContainer,
        border: `1px solid ${token.colorBorderSecondary}`,
        boxShadow: "0 1px 3px rgba(15, 23, 42, 0.05), 0 1px 2px rgba(15, 23, 42, 0.04)",
        ...style,
      }}
    >
      {showHead ? (
        <div
          className="admin-filter-surface__head"
          style={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: 12,
            flexWrap: "wrap",
            marginBottom: 16,
            paddingBottom: 12,
            borderBottom: `1px solid ${token.colorBorderSecondary}`,
          }}
        >
          <div className="admin-filter-surface__title" style={{ minWidth: 0 }}>
            {typeof title === "string" ? (
              <Text strong style={{ fontSize: 15, color: token.colorText }}>
                {title}
              </Text>
            ) : (
              title
            )}
          </div>
          {extra ? (
            <div className="admin-filter-surface__extra" style={{ flexShrink: 0 }}>
              {extra}
            </div>
          ) : null}
        </div>
      ) : null}

      <div className="admin-filter-surface__body">{children}</div>

      {footer ? (
        <div className="admin-filter-surface__footer" style={{ marginTop: 14, paddingTop: 2 }}>
          {footer}
        </div>
      ) : null}
    </div>
  );
}
