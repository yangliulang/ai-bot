/** 实例列表 / 详情 / 预览抽屉共用的展示辅助 */

export function agentStateTagColor(state: string): string {
  if (state === "NORMAL") return "success";
  if (state === "BILLING_BLOCKED" || state === "MEMBERSHIP_BLOCKED") return "warning";
  if (
    state === "GLOBAL_OFF" ||
    state === "OPS_SUSPENDED" ||
    state === "AGENT_SUBACCOUNT_BLOCKED"
  )
    return "error";
  return "default";
}

export function runtimeStateTagColor(state: string): string {
  if (state === "RUNNING") return "success";
  if (state === "PAUSED") return "warning";
  if (state === "STARTING") return "processing";
  if (state === "ERROR") return "error";
  return "default";
}

export function formatInstanceAt(iso: string): string {
  if (!iso) return "—";
  return iso.slice(0, 16).replace("T", " ");
}

/** §3.1 渠道列：chat id 掩码；仅有 username 时展示 @username */
export function formatTelegramChannelCell(i: {
  telegramNumericId?: string;
  telegramUsername?: string;
}): string {
  if (i.telegramNumericId) {
    const id = i.telegramNumericId;
    if (id.length <= 6) return `${id.slice(0, 2)}***`;
    return `${id.slice(0, 3)}***${id.slice(-3)}`;
  }
  if (i.telegramUsername) return i.telegramUsername;
  return "—";
}

