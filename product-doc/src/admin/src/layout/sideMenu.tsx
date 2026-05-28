import type { MenuProps } from "antd";
import {
  AccountBookOutlined,
  BranchesOutlined,
  CloudServerOutlined,
  DeploymentUnitOutlined,
  FileProtectOutlined,
  FileSearchOutlined,
  FileTextOutlined,
  ShopOutlined,
  MessageOutlined,
  SafetyCertificateOutlined,
  SearchOutlined,
  SolutionOutlined,
  UnorderedListOutlined,
  UserSwitchOutlined,
} from "@ant-design/icons";
import { adminMenuModuleLabels } from "../copy/adminNaming";
import { ADMIN_NAV_LEAVES, ADMIN_NAV_MODULE_ORDER, type AdminNavLeaf } from "./adminNavCatalog";

import { getPromptPack } from "../data/mock";

function iconForLeaf(leaf: AdminNavLeaf) {
  const { path } = leaf;
  if (path === "/runtime/executions") return <UnorderedListOutlined />;
  if (path === "/agents/instances") return <DeploymentUnitOutlined />;
  if (path === "/prompts/strategy") return <FileTextOutlined />;
  if (path === "/prompts/safety") return <FileProtectOutlined />;
  if (path === "/ai/runtime-orchestration") return <BranchesOutlined />;
  if (path === "/ai-settings") return <CloudServerOutlined />;
  if (path === "/ai/confirmation-rules") return <UserSwitchOutlined />;
  if (path === "/access") return <SafetyCertificateOutlined />;
  if (path === "/billing/overview") return <AccountBookOutlined />;
  if (path === "/billing/operations") return <ShopOutlined />;
  if (path === "/billing/ledger") return <FileSearchOutlined />;
  if (path === "/observability") return <SearchOutlined />;
  if (path === "/system/channels") return <MessageOutlined />;
  return <SolutionOutlined />;
}

/** 与命名 v3 / demo-routing 同源 */
export const EXCHANGE_SIDE_MENU_ITEMS: MenuProps["items"] = ADMIN_NAV_MODULE_ORDER.map((mod) => ({
  type: "group" as const,
  label: adminMenuModuleLabels[mod],
  children: ADMIN_NAV_LEAVES.filter((l) => l.module === mod).map((leaf) => ({
    key: leaf.path,
    label: leaf.label,
    icon: iconForLeaf(leaf),
  })),
}));

export function getSideMenuSelectedKey(pathname: string): string {
  if (pathname.startsWith("/runtime/executions")) return "/runtime/executions";

  if (pathname.startsWith("/runtime")) return "/runtime/executions";

  if (pathname.startsWith("/agents/instances")) return "/agents/instances";

  if (pathname === "/prompts/strategy" || pathname === "/prompts") return "/prompts/strategy";
  if (pathname === "/prompts/safety") return "/prompts/safety";

  {
    const m = pathname.match(/^\/prompts\/editor\/([^/]+)\/?$/);
    if (m) {
      const p = getPromptPack(decodeURIComponent(m[1]));
      if (p?.kind === "SAFETY") return "/prompts/safety";
      return "/prompts/strategy";
    }
  }

  if (pathname === "/ai/runtime-orchestration" || pathname.startsWith("/tools")) return "/ai/runtime-orchestration";
  if (pathname === "/ai-settings") return "/ai-settings";
  if (pathname.startsWith("/ai/confirmation-rules")) return "/ai/confirmation-rules";

  if (pathname.startsWith("/access")) return "/access";

  if (pathname.startsWith("/billing/ledger")) return "/billing/ledger";
  if (
    pathname.startsWith("/billing/operations") ||
    pathname.startsWith("/billing/subscriptions") ||
    pathname.startsWith("/billing/packs") ||
    pathname.startsWith("/billing/orders") ||
    pathname.startsWith("/billing/consumption") ||
    pathname.startsWith("/billing/commerce")
  ) {
    return "/billing/operations";
  }
  if (pathname.startsWith("/billing/pricing")) return "/billing/overview";
  if (pathname.startsWith("/billing/overview") || pathname === "/billing") return "/billing/overview";

  if (pathname.startsWith("/observability")) return "/observability";

  if (pathname.startsWith("/system/channels")) return "/system/channels";

  if (pathname === "/trading-config") return "/access";

  return "/runtime/executions";
}
