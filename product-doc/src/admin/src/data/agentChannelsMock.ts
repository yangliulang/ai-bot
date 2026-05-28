/**
 * Agent Interaction Channel — 演示数据（运营语义，非 config key）。
 * 真源与 OpenAPI 对齐后由接口替换。
 */

export type AgentChannelKind = "im";

export interface AgentChannelListRow {
  id: string;
  /** 展示名 */
  name: string;
  /** IM */
  kind: AgentChannelKind;
  kindLabel: string;
  /** 已接入 | 未接入 | 已启用 */
  status: "connected" | "disabled" | "enabled";
  statusLabel: string;
  /** 演示：覆盖用户数或「—」 */
  userScaleLabel: string;
  /** 列表操作 */
  action: "configure" | "onboard";
  actionLabel: string;
}

export const MOCK_AGENT_CHANNELS: AgentChannelListRow[] = [
  {
    id: "telegram",
    name: "Telegram",
    kind: "im",
    kindLabel: "IM",
    status: "connected",
    statusLabel: "已接入",
    userScaleLabel: "2,301",
    action: "configure",
    actionLabel: "配置",
  },
  {
    id: "discord",
    name: "Discord",
    kind: "im",
    kindLabel: "IM",
    status: "disabled",
    statusLabel: "未接入",
    userScaleLabel: "—",
    action: "onboard",
    actionLabel: "接入",
  },
  {
    id: "whatsapp",
    name: "WhatsApp",
    kind: "im",
    kindLabel: "IM",
    status: "disabled",
    statusLabel: "未接入",
    userScaleLabel: "—",
    action: "onboard",
    actionLabel: "接入",
  },
];

export function channelStatusTagColor(status: AgentChannelListRow["status"]): string {
  if (status === "connected" || status === "enabled") return "success";
  return "default";
}
