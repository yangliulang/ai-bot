import type { ThemeConfig } from "antd";

/** 交易所运营后台风格 + 产品化层次（阴影、表格悬浮、动效） */
export const exchangeAdminTheme: ThemeConfig = {
  token: {
    colorPrimary: "#1890ff",
    colorSuccess: "#52c41a",
    colorWarning: "#faad14",
    colorError: "#ff4d4f",
    colorInfo: "#1890ff",
    borderRadius: 6,
    borderRadiusLG: 10,
    fontFamily:
      "'PingFang SC', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    boxShadowSecondary: "0 2px 8px rgba(0, 0, 0, 0.06)",
    motionDurationMid: "0.2s",
    controlHeight: 36,
    controlItemBgHover: "rgba(24, 144, 255, 0.06)",
    colorBgLayout: "#f5f7fa",
    colorText: "rgba(0, 0, 0, 0.88)",
    colorTextSecondary: "rgba(0, 0, 0, 0.45)",
    colorTextTertiary: "rgba(0, 0, 0, 0.35)",
    colorSplit: "rgba(0, 0, 0, 0.06)",
  },
  components: {
    Layout: {
      headerBg: "#1f2937",
      headerHeight: 48,
      headerPadding: "0 20px",
      bodyBg: "#f5f7fa",
      siderBg: "#1f2937",
    },
    Menu: {
      darkItemBg: "#1f2937",
      darkSubMenuItemBg: "#1f2937",
      itemBorderRadius: 6,
      itemMarginInline: 8,
      iconSize: 16,
    },
    Card: {
      borderRadiusLG: 10,
      paddingLG: 24,
      boxShadowTertiary: "0 1px 2px rgba(0, 0, 0, 0.04)",
    },
    Table: {
      headerBg: "#fafafa",
      headerColor: "rgba(0, 0, 0, 0.88)",
      rowHoverBg: "#f0f9ff",
      borderColor: "#f0f0f0",
      cellPaddingBlock: 12,
      cellPaddingInline: 16,
    },
    Button: {
      primaryShadow: "0 2px 0 rgba(0, 0, 0, 0.02)",
      controlHeight: 36,
    },
    Tabs: {
      horizontalMargin: "0 24px 0 0",
      titleFontSize: 14,
    },
    Input: {
      activeBorderColor: "#1890ff",
      hoverBorderColor: "#40a9ff",
    },
    Select: {
      optionSelectedBg: "#e6f7ff",
    },
    Alert: {
      borderRadiusLG: 8,
    },
    Tag: {
      borderRadiusSM: 4,
    },
  },
};
