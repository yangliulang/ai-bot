import { isExecutionId } from "../lib/executionId";

/** 与 ObservabilityPage 查询参数约定一致 — observability-management/config.md §4 Deep link
 * **D-5**：`traceKey` 与 `billingTraceId` 同窗；URL 读写以 **`traceId`** 为统一键，**`traceKey`** 仅作入参别名。
 */

export type ObservabilityTab = "execution" | "tool" | "llm" | "billing" | "audit";

const TABS: ObservabilityTab[] = ["execution", "tool", "llm", "billing", "audit"];

export function isObservabilityTab(s: string): s is ObservabilityTab {
  return (TABS as string[]).includes(s);
}

/** 从地址栏读取计费协查键（traceId 优先，其次 D-5 别名 traceKey） */
export function readObservabilityTraceQuery(searchParams: URLSearchParams): string {
  return (searchParams.get("traceId") ?? searchParams.get("traceKey") ?? "").trim();
}

export function buildObservabilitySearch(params: {
  executionId?: string;
  userId?: string;
  /** 与计费 `billingTraceId` / 运营 `traceKey` 同窗（`observability` 计费表筛选用） */
  traceId?: string;
  /** D-5：与 `traceId` 等价；若同时提供则以 `traceId` 为准 */
  traceKey?: string;
  tab?: ObservabilityTab;
}): string {
  const sp = new URLSearchParams();
  if (params.executionId?.trim()) sp.set("executionId", params.executionId.trim());
  if (params.userId?.trim()) sp.set("userId", params.userId.trim());
  const tid = (params.traceId?.trim() || params.traceKey?.trim()) ?? "";
  if (tid) sp.set("traceId", tid);
  if (params.tab) sp.set("tab", params.tab);
  const q = sp.toString();
  return q ? `?${q}` : "";
}

/** 协查无命中时跳转日志检索：按前缀粗分 query 键，其余走 traceId 子串 */
export function buildObservabilitySearchFromCorrelateHint(raw: string): string {
  const t = raw.trim();
  if (!t) return buildObservabilitySearch({ tab: "billing" });
  const lower = t.toLowerCase();
  if (isExecutionId(t)) return buildObservabilitySearch({ executionId: t, tab: "billing" });
  if (lower.startsWith("u-")) return buildObservabilitySearch({ userId: t, tab: "billing" });
  return buildObservabilitySearch({ traceId: t, tab: "billing" });
}
