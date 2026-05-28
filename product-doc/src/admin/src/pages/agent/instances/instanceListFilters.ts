import type { AgentInstance } from "../../../data/types";

/** 列表页增补条件（用户 UID、最近活跃日期区间） */
export type InstanceListExtraFilters = {
  /** 用户 UID 子串（模糊，不含邮箱） */
  userIdContains?: string;
  /** `YYYY-MM-DD`，含当日 · 按 `lastActiveAt` ISO 日历片段（演示视为 UTC 日期） */
  lastActiveFromDay?: string;
  lastActiveToDay?: string;
};

/** 单行关键字 + 结构化筛选（关键字：`instanceId` / `userId` / `agentSubAccountUid` 模糊） */
export function filterInstanceRows(
  rows: AgentInstance[],
  keyword: string,
  agentState: string,
  runtimeState: string,
  extra: InstanceListExtraFilters = {},
): AgentInstance[] {
  const k = keyword.trim().toLowerCase();
  const uidPart = extra.userIdContains?.trim().toLowerCase() ?? "";
  const fromD = extra.lastActiveFromDay?.trim() ?? "";
  const toD = extra.lastActiveToDay?.trim() ?? "";

  return rows.filter((i) => {
    if (uidPart && !i.userId.toLowerCase().includes(uidPart)) return false;

    const day = i.lastActiveAt.slice(0, 10);
    if (fromD && day < fromD) return false;
    if (toD && day > toD) return false;

    if (k) {
      const hitUid = i.userId.toLowerCase().includes(k);
      const hitInst = i.instanceId.toLowerCase().includes(k);
      const hitSub = (i.agentSubAccountUid ?? "").toLowerCase().includes(k);
      if (!hitUid && !hitInst && !hitSub) return false;
    }
    if (agentState !== "all" && i.agentState !== agentState) return false;
    if (runtimeState !== "all" && i.runtimeState !== runtimeState) return false;
    return true;
  });
}
