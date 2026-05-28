export type ExecutionStatusFilter = "all" | "CREATED" | "COMPLETED" | "RUNNING" | "UNKNOWN" | "FAILED" | "BLOCKED";

const KNOWN_RUNTIME_STATUSES = new Set<ExecutionStatusFilter>([
  "all",
  "CREATED",
  "RUNNING",
  "COMPLETED",
  "UNKNOWN",
  "FAILED",
  "BLOCKED",
]);

/** 将地址栏等非受控字符串解析为状态筛选项（非法值回退「全部」） */
export function parseExecutionStatusFilter(raw: string | null | undefined): ExecutionStatusFilter {
  if (!raw || raw === "all") return "all";
  const u = raw.toUpperCase();
  const candidate = u as ExecutionStatusFilter;
  if (KNOWN_RUNTIME_STATUSES.has(candidate) && candidate !== "all") return candidate;
  return "all";
}

export function executionMatchesStatus(status: ExecutionStatusFilter, rowStatus: string): boolean {
  if (status === "all") return true;
  return rowStatus === status;
}

export function executionInDateRange(isoDay: string, from: string, to: string): boolean {
  const day = isoDay.slice(0, 10);
  if (from && day < from) return false;
  if (to && day > to) return false;
  return true;
}

/** 单框关键字：匹配 executionId、用户掩码或 scenarioId 任一即保留（OR）；空则不过滤 */
export function executionMatchesCorrelationKeyword(
  row: { executionId: string; userIdMasked: string; scenarioId: string },
  raw: string,
): boolean {
  const k = raw.trim().toLowerCase();
  if (!k) return true;
  return (
    row.executionId.toLowerCase().includes(k) ||
    row.userIdMasked.toLowerCase().includes(k) ||
    row.scenarioId.toLowerCase().includes(k)
  );
}

/** 编排页深链：?scenario= 精确匹配 scenarioId；空则不过滤 */
export function executionMatchesScenarioParam(row: { scenarioId: string }, raw: string): boolean {
  const s = raw.trim();
  if (!s) return true;
  return row.scenarioId === s;
}
