import {
  AppstoreOutlined,
  BellOutlined,
  BulbOutlined,
  CrownOutlined,
  DownOutlined,
  DownloadOutlined,
  FileProtectOutlined,
  GiftOutlined,
  HomeOutlined,
  LineChartOutlined,
  PartitionOutlined,
  RightOutlined,
  SearchOutlined,
  SettingOutlined,
  ShoppingCartOutlined,
  SwapOutlined,
  TeamOutlined,
  ThunderboltOutlined,
  UnorderedListOutlined,
  UserOutlined,
  WalletOutlined,
} from "@ant-design/icons";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

const TOP_MENUS = ["快捷买币", "行情", "交易", "合约", "理财", "任务中心", "更多"] as const;

function sidenavCls(isActive: boolean) {
  return ["coolbit-sidenav__link", isActive ? "coolbit-sidenav__link--active" : ""].filter(Boolean).join(" ");
}

function SidebarDisabled({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <span className="coolbit-sidenav__link coolbit-sidenav__link--disabled">
      <span className="coolbit-sidenav__icon">{icon}</span>
      <span className="coolbit-sidenav__text">{children}</span>
    </span>
  );
}

function SidebarSubPlaceholder({ children }: { children: ReactNode }) {
  return <span className="coolbit-sidenav__nest-placeholder">{children}</span>;
}

function SubaccountSidebarGroup() {
  const location = useLocation();
  const subActive =
    location.pathname.startsWith("/subaccount") ||
    location.pathname.startsWith("/subscription");
  const [expanded, setExpanded] = useState(subActive);

  useEffect(() => {
    if (subActive) setExpanded(true);
  }, [subActive]);

  const billingActive =
    location.pathname.startsWith("/subaccount/billing") ||
    location.pathname.startsWith("/subaccount/agent-billing");
  const subscriptionActive = location.pathname.startsWith("/subscription");
  const [subMenuExpanded, setSubMenuExpanded] = useState(subscriptionActive);

  useEffect(() => {
    if (subscriptionActive) setSubMenuExpanded(true);
  }, [subscriptionActive]);

  return (
    <div className="coolbit-sidenav__group">
      <button
        type="button"
        className="coolbit-sidenav__link coolbit-sidenav__group-trigger"
        onClick={() => setExpanded((e) => !e)}
        aria-expanded={expanded}
      >
        <PartitionOutlined className="coolbit-sidenav__icon" />
        <span className="coolbit-sidenav__text">子账户</span>
        <span className="coolbit-sidenav__group-chevron" aria-hidden>
          {expanded ? <DownOutlined /> : <RightOutlined />}
        </span>
      </button>
      {expanded ? (
        <div className="coolbit-sidenav__nest">
          <SidebarSubPlaceholder>账户管理</SidebarSubPlaceholder>
          <SidebarSubPlaceholder>API 管理</SidebarSubPlaceholder>
          <SidebarSubPlaceholder>资产管理</SidebarSubPlaceholder>
          <SidebarSubPlaceholder>订单管理</SidebarSubPlaceholder>
          <NavLink
            to="/subaccount/billing"
            className={({ isActive }) =>
              [
                "coolbit-sidenav__nest-link",
                isActive || billingActive ? "coolbit-sidenav__nest-link--active" : "",
              ]
                .filter(Boolean)
                .join(" ")
            }
          >
            <WalletOutlined style={{ marginRight: 6 }} />
            账单与消耗
          </NavLink>
          <button
            type="button"
            className="coolbit-sidenav__nest-trigger"
            onClick={() => setSubMenuExpanded((e) => !e)}
            aria-expanded={subMenuExpanded}
          >
            <CrownOutlined style={{ marginRight: 6 }} />
            订阅与购买
            <span className="coolbit-sidenav__nest-trigger-chevron" aria-hidden>
              {subMenuExpanded ? <DownOutlined /> : <RightOutlined />}
            </span>
          </button>
          {subMenuExpanded ? (
            <div className="coolbit-sidenav__nest coolbit-sidenav__nest--deep">
              <NavLink
                to="/subscription"
                end
                className={({ isActive }) =>
                  ["coolbit-sidenav__nest-link", isActive ? "coolbit-sidenav__nest-link--active" : ""]
                    .filter(Boolean)
                    .join(" ")
                }
              >
                订阅与购买
              </NavLink>
              <NavLink
                to="/subscription/upgrade"
                className={({ isActive }) =>
                  ["coolbit-sidenav__nest-link", isActive ? "coolbit-sidenav__nest-link--active" : ""]
                    .filter(Boolean)
                    .join(" ")
                }
              >
                <ThunderboltOutlined style={{ marginRight: 6 }} />
                升级套餐
              </NavLink>
              <NavLink
                to="/subscription/pack"
                className={({ isActive }) =>
                  ["coolbit-sidenav__nest-link", isActive ? "coolbit-sidenav__nest-link--active" : ""]
                    .filter(Boolean)
                    .join(" ")
                }
              >
                <ShoppingCartOutlined style={{ marginRight: 6 }} />
                购买加购包
              </NavLink>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function H5TabBar() {
  const { pathname } = useLocation();
  const assetsActive =
    pathname.startsWith("/subaccount") ||
    pathname.startsWith("/subscription") ||
    pathname.startsWith("/billing");

  const tabItemCls = (active: boolean) =>
    ["coolbit-h5-tabbar__item", active ? "coolbit-h5-tabbar__item--active" : ""].filter(Boolean).join(" ");

  return (
    <nav className="coolbit-h5-tabbar" aria-label="底部导航">
      <NavLink to="/" end className={({ isActive }) => tabItemCls(isActive)}>
        <HomeOutlined className="coolbit-h5-tabbar__icon" aria-hidden />
        <span className="coolbit-h5-tabbar__label">首页</span>
      </NavLink>
      <NavLink to="/h5/market" className={({ isActive }) => tabItemCls(isActive)}>
        <LineChartOutlined className="coolbit-h5-tabbar__icon" aria-hidden />
        <span className="coolbit-h5-tabbar__label">行情</span>
      </NavLink>
      <NavLink to="/onboarding" className={({ isActive }) => tabItemCls(isActive)}>
        <span className="coolbit-h5-tabbar__trade" aria-hidden>
          <SwapOutlined />
        </span>
        <span className="coolbit-h5-tabbar__label">交易</span>
      </NavLink>
      <NavLink to="/h5/futures" className={({ isActive }) => tabItemCls(isActive)}>
        <FileProtectOutlined className="coolbit-h5-tabbar__icon" aria-hidden />
        <span className="coolbit-h5-tabbar__label">合约</span>
      </NavLink>
      <NavLink
        to="/subaccount/billing"
        className={({ isActive }) => tabItemCls(isActive || assetsActive)}
      >
        <WalletOutlined className="coolbit-h5-tabbar__icon" aria-hidden />
        <span className="coolbit-h5-tabbar__label">账单</span>
      </NavLink>
    </nav>
  );
}

export default function WebShell() {
  return (
    <div className="coolbit-app">
      <header className="coolbit-topnav">
        <NavLink to="/" className="coolbit-topnav__brand">
          Coolbit
        </NavLink>
        <nav className="coolbit-topnav__menus" aria-label="主导航（示意）">
          {TOP_MENUS.map((label) => (
            <span key={label} className="coolbit-topnav__menu-item">
              {label}
            </span>
          ))}
        </nav>
        <div className="coolbit-topnav__tools">
          <button type="button" className="coolbit-topnav__tool" aria-label="搜索">
            <SearchOutlined />
          </button>
          <button type="button" className="coolbit-topnav__tool" aria-label="资产">
            <WalletOutlined />
          </button>
          <button type="button" className="coolbit-topnav__tool" aria-label="订单">
            <UnorderedListOutlined />
          </button>
          <button type="button" className="coolbit-topnav__tool" aria-label="下载">
            <DownloadOutlined />
          </button>
          <button type="button" className="coolbit-topnav__tool" aria-label="主题">
            <BulbOutlined />
          </button>
          <button type="button" className="coolbit-topnav__tool" aria-label="通知">
            <BellOutlined />
          </button>
          <button type="button" className="coolbit-topnav__tool" aria-label="账户">
            <UserOutlined />
          </button>
        </div>
      </header>

      <div className="coolbit-body">
        <aside className="coolbit-sidebar" aria-label="页面导航">
          <NavLink to="/" end className={({ isActive }) => sidenavCls(isActive)}>
            <AppstoreOutlined className="coolbit-sidenav__icon" />
            <span className="coolbit-sidenav__text">总览</span>
          </NavLink>
          <SidebarDisabled icon={<UserOutlined />}>账户</SidebarDisabled>
          <SidebarDisabled icon={<GiftOutlined />}>任务中心</SidebarDisabled>
          <SidebarDisabled icon={<TeamOutlined />}>现货经纪人</SidebarDisabled>
          <SubaccountSidebarGroup />
          <SidebarDisabled icon={<SettingOutlined />}>设置</SidebarDisabled>
        </aside>

        <main className="coolbit-main">
          <div className="coolbit-main__inner">
            <Outlet />
          </div>
        </main>
      </div>

      <footer className="coolbit-footer-note">交互原型 · 正式规则以 Coolbit 官网协议为准</footer>
      <H5TabBar />
    </div>
  );
}
