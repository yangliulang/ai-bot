import type { ThemeConfig } from "antd";

/** 对齐 Coolbit 主站：白底工作台、黑色胶囊主按钮、中性灰文案 */
export const coolbitTheme: ThemeConfig = {
  token: {
    colorPrimary: "#000000",
    borderRadius: 10,
    fontFamily:
      'system-ui, -apple-system, "PingFang SC", "Helvetica Neue", "Microsoft YaHei", sans-serif',
    colorBgLayout: "#ffffff",
    colorBgContainer: "#ffffff",
    colorText: "#1a1a1a",
    colorTextSecondary: "#666666",
    colorTextTertiary: "#999999",
    colorBorder: "#ebebeb",
    controlOutline: "transparent",
    lineHeight: 1.5,
  },
  components: {
    Button: {
      primaryShadow: "none",
      borderRadius: 999,
      controlHeightLG: 48,
      fontWeight: 500,
      colorPrimaryHover: "#333333",
      colorPrimaryActive: "#1a1a1a",
      colorBgContainerDisabled: "#e8e8e8",
      colorTextDisabled: "#ffffff",
    },
    Input: {
      colorBgContainer: "#f5f5f5",
      hoverBg: "#f0f0f0",
      activeBorderColor: "#d9d9d9",
      hoverBorderColor: "#d0d0d0",
      borderRadius: 10,
      paddingBlock: 10,
      paddingInline: 14,
    },
    Select: {
      colorBgContainer: "#f5f5f5",
      borderRadius: 10,
      optionSelectedBg: "#f0f0f0",
    },
    Card: {
      borderRadiusLG: 12,
      paddingLG: 24,
    },
    Descriptions: {
      borderRadiusLG: 12,
      labelBg: "#fafafa",
    },
    Table: {
      headerBg: "#fafafa",
      headerColor: "#666666",
      rowHoverBg: "#fafafa",
      borderColor: "#f0f0f0",
    },
    Steps: {
      colorPrimary: "#000000",
      colorSplit: "#e8e8e8",
    },
  },
};
