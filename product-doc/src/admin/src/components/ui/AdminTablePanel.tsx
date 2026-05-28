import { theme } from "antd";
import type { CSSProperties, ReactNode } from "react";

type AdminTablePanelProps = {
  children: ReactNode;
  className?: string;
  /** 外边距顶部，实例列表等与上方工具条留缝 */
  marginTop?: number;
  style?: CSSProperties;
};

/**
 * 主数据表外框（白底 + 裁剪圆角溢出），不包含 Table 语义，仅统一壳层。
 */
export function AdminTablePanel({ children, className, marginTop = 0, style }: AdminTablePanelProps) {
  const { token } = theme.useToken();
  return (
    <div
      className={["admin-table-panel", className].filter(Boolean).join(" ")}
      style={{
        marginTop,
        borderRadius: token.borderRadiusLG,
        border: `1px solid ${token.colorBorderSecondary}`,
        overflow: "hidden",
        background: token.colorBgContainer,
        ...style,
      }}
    >
      {children}
    </div>
  );
}
