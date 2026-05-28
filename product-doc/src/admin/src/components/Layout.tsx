import {
  App,
  Avatar,
  Badge,
  Button,
  Divider,
  Dropdown,
  Grid,
  Layout as AntLayout,
  Menu,
  Space,
  Tooltip,
  Typography,
  theme,
} from "antd";
import {
  BellOutlined,
  BookOutlined,
  DownOutlined,
  FileTextOutlined,
  UserOutlined,
} from "@ant-design/icons";
import type { MenuProps } from "antd";
import { useMemo, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { EXCHANGE_SIDE_MENU_ITEMS, getSideMenuSelectedKey } from "../layout/sideMenu";
import { FloatingAssistDock } from "./FloatingAssistDock";

const { Header, Sider, Content } = AntLayout;
const { Text } = Typography;

export function Layout() {
  const { token } = theme.useToken();
  const screens = Grid.useBreakpoint();
  const { message } = App.useApp();
  const navigate = useNavigate();
  const location = useLocation();
  const [siderCollapsed, setSiderCollapsed] = useState(false);

  const selectedKey = getSideMenuSelectedKey(location.pathname);

  const headerMuted = "rgba(255, 255, 255, 0.85)";

  const accountMenu: MenuProps = useMemo(
    () => ({
      items: [
        {
          key: "changelog",
          icon: <FileTextOutlined />,
          label: "更新说明",
        },
        {
          key: "guide",
          icon: <BookOutlined />,
          label: "控制台导览",
        },
        { type: "divider" },
        {
          key: "locale",
          disabled: true,
          label: "语言 · 简体中文",
        },
      ],
      onClick: ({ key }) => {
        if (key === "changelog") {
          message.info("演示环境：更新说明以内部发布记录为准。");
        }
        if (key === "guide") {
          message.info("演示环境：请通过左侧菜单进入各功能模块。");
        }
      },
    }),
    [message],
  );

  const onSideMenuClick: MenuProps["onClick"] = ({ key }) => {
    navigate(key);
  };

  return (
    <AntLayout style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Header
        className="admin-shell-header"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          paddingInline: token.paddingLG,
          columnGap: token.marginMD,
          height: 48,
          lineHeight: undefined,
        }}
      >
        <div
          className="admin-shell-header-left"
          style={{
            display: "flex",
            alignItems: "center",
            flex: 1,
            minWidth: 0,
            columnGap: token.marginSM,
          }}
        >
          <Text
            strong
            style={{
              color: "#fff",
              fontSize: 16,
              margin: 0,
              lineHeight: 1,
              flexShrink: 0,
            }}
          >
            ChainUp
          </Text>
          <Divider
            type="vertical"
            style={{ borderColor: "rgba(255,255,255,0.18)", height: 20, margin: 0, flexShrink: 0 }}
          />
          <Text
            className="admin-shell-header-product"
            ellipsis
            style={{
              color: headerMuted,
              fontSize: 14,
              margin: 0,
              minWidth: 0,
              lineHeight: 1,
            }}
          >
            运营控制台 · AI 智能体
          </Text>
        </div>

        <Space size="small" align="center" style={{ flexShrink: 0 }} wrap={false}>
          <Tooltip title="暂无新通知（演示）">
            <Badge dot>
              <Button
                type="text"
                className="admin-header-icon-btn"
                icon={<BellOutlined style={{ fontSize: 18 }} />}
                aria-label="通知"
              />
            </Badge>
          </Tooltip>
          <Dropdown menu={accountMenu} placement="bottomRight" trigger={["click"]}>
            <Button type="text" className="admin-header-text-btn" style={{ height: 40, paddingInline: 10 }}>
              <Space size={8} wrap={false} align="center">
                <Avatar size="small" icon={<UserOutlined />} style={{ backgroundColor: token.colorPrimary }} />
                {screens.md ? (
                  <Text ellipsis style={{ color: headerMuted, maxWidth: 96, margin: 0, lineHeight: 1 }}>
                    运营
                  </Text>
                ) : null}
                <DownOutlined style={{ color: "rgba(255,255,255,0.55)", fontSize: 10 }} />
              </Space>
            </Button>
          </Dropdown>
        </Space>
      </Header>

      <AntLayout className="admin-workspace-shell" style={{ flex: 1, minHeight: 0 }}>
        <Sider
          className="admin-pro-sider"
          width={236}
          collapsedWidth={72}
          theme="dark"
          collapsible
          collapsed={siderCollapsed}
          onCollapse={setSiderCollapsed}
          style={{
            overflow: "hidden",
            height: "calc(100vh - 48px)",
            position: "sticky",
            top: 0,
            left: 0,
          }}
        >
          {!siderCollapsed ? (
            <div className="admin-sider-brand">
              <Text strong style={{ color: "rgba(255,255,255,0.95)", fontSize: 14, display: "block" }}>
                AI 交易智能体
              </Text>
              <Text style={{ color: "rgba(255,255,255,0.42)", fontSize: 12, lineHeight: 1.4 }}>
                扁平入口 · 运行态视图为主
              </Text>
            </div>
          ) : null}
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[selectedKey]}
            items={EXCHANGE_SIDE_MENU_ITEMS}
            onClick={onSideMenuClick}
            inlineCollapsed={siderCollapsed}
            style={{
              borderInlineEnd: "none",
              background: "transparent",
            }}
          />
        </Sider>

        <Content
          className="admin-layout-content admin-workspace-main"
          style={{
            margin: 0,
            minHeight: "calc(100vh - 48px)",
            background: "#f5f7fa",
            overflow: "auto",
          }}
        >
          <div className="admin-page-root">
            <Outlet />
          </div>
        </Content>
      </AntLayout>

      <FloatingAssistDock />
    </AntLayout>
  );
}
