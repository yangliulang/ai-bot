/**
 * `admin/observability.yaml` · `listObservabilityExecutions`
 * 需 `VITE_API_BASE_URL` + `VITE_USE_OBSERVABILITY_API=true`。
 */
import { executionIdFromCorrelationQuery } from "../lib/executionId";
import { apiFetch, getApiBaseUrl } from "./http";
import { ORCHESTRATION_VERSION_DISPLAY } from "../data/orchestrationConstants";
import type { MockObsExecutionRow, MockObsTimelineEventRow } from "../data/types";

export function isObservabilityApiEnabled(): boolean {
  return import.meta.env.VITE_USE_OBSERVABILITY_API === "true" && !!getApiBaseUrl();
}

export type ObservabilityExecutionsPageJson = {
  items?: Record<string, unknown>[];
  nextCursor?: string | null;
};

export type ListObservabilityExecutionsParams = {
  userId?: string;
  scenarioId?: string;
  executionId?: string;
  intentContains?: string;
  status?: string;
  timeFrom?: string;
  timeTo?: string;
  pageSize?: number;
  cursor?: string;
};

/**
 * 列表「合并检索」→ `listObservabilityExecutions` 独立 query（OpenAPI 无单字段 OR 时的启发式）。
 * **优先** 「显式 `?scenario=`」—— 由调用方在组装 params 时覆盖 `scenarioId`。
 */
export function correlationQueryToListApiParams(raw: string): {
  userId?: string;
  executionId?: string;
  scenarioId?: string;
} {
  const q = raw.trim();
  if (!q) return {};
  const lower = q.toLowerCase();
  if (lower.startsWith("u-")) return { userId: q };
  const executionId = executionIdFromCorrelationQuery(q);
  if (executionId) return { executionId };
  if (/^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$/.test(q)) return { scenarioId: q };
  return {};
}

export type ObservabilityTimelineResponseJson =
  | { items?: Record<string, unknown>[] }
  | Record<string, unknown>;

/**
 * BFF 仅返回时间线而无 mock 行时，用最小行驱动详情壳（工具/队列为空）。
 */
export function buildMinimalExecFromApiTimeline(
  executionId: string,
  events: MockObsTimelineEventRow[],
): MockObsExecutionRow {
  const firstTs = events[0]?.at && events[0].at.length > 0 ? events[0].at : new Date().toISOString();
  return {
    executionId,
    sessionId: "",
    userIdMasked: "",
    scenarioId: "",
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: "（API：mock 无此行；摘要来自 listObservabilityExecutions 或仅时间线）",
    status: "RUNNING",
    currentStage: "RUNNING",
    retries: 0,
    createdAt: firstTs,
    stageTimeline: ["CREATED", "RUNNING"],
    durationMs: 0,
    startedAt: firstTs,
    outcome: "RUNNING",
    timelineEvents: events,
  };
}

export function mapObservabilityTimelineEventToRow(raw: Record<string, unknown>): MockObsTimelineEventRow {
  const ts = String(raw.ts ?? raw.at ?? "");
  const summaryRaw = raw.summary;
  let summaryStr: string | undefined;
  if (typeof summaryRaw === "string") summaryStr = summaryRaw;
  else if (summaryRaw != null && typeof summaryRaw === "object") {
    try {
      summaryStr = JSON.stringify(summaryRaw);
    } catch {
      summaryStr = String(summaryRaw);
    }
  }
  const tt = raw.transitionTrigger;
  return {
    at: ts,
    eventName: raw.eventName != null ? String(raw.eventName) : undefined,
    summary: summaryStr,
    transitionTrigger: tt != null && tt !== "" ? String(tt) : undefined,
  };
}

export async function fetchObservabilityExecutionTimeline(executionId: string): Promise<MockObsTimelineEventRow[]> {
  const enc = encodeURIComponent(executionId);
  const data = await apiFetch<ObservabilityTimelineResponseJson>(
    `/api/v1/admin/observability/executions/${enc}/timeline`,
  );
  const items = Array.isArray((data as { items?: unknown }).items)
    ? ((data as { items: Record<string, unknown>[] }).items ?? [])
    : [];
  return items.map((row) => mapObservabilityTimelineEventToRow(row));
}

function toIso(v: unknown, fallback: string): string {
  if (typeof v === "string" && v.length > 0) return v;
  return fallback;
}

/** 将 OpenAPI ObservabilityExecutionSummary 近似映射为 Demo 行（列表/预览共用类型） */
export function mapExecutionSummaryToMockRow(raw: Record<string, unknown>): MockObsExecutionRow {
  const executionId = String(raw.executionId ?? "");
  const status = String(raw.status ?? "CREATED");
  const currentStage = String(raw.currentStage ?? status ?? "CREATED");
  const stageTimeline = Array.isArray(raw.stageTimeline)
    ? (raw.stageTimeline as unknown[]).map((s) => String(s))
    : [currentStage || "CREATED"];
  const created = toIso(raw.createdAt, new Date().toISOString());
  const retries = typeof raw.retries === "number" ? raw.retries : Number(raw.retries) || 0;
  const durationMs = typeof raw.durationMs === "number" ? raw.durationMs : Number(raw.durationMs) || 0;

  return {
    executionId,
    sessionId: String(raw.sessionId ?? ""),
    userIdMasked: String(raw.userIdMasked ?? ""),
    scenarioId: String(raw.scenarioId ?? ""),
    orchestrationVersion: String(raw.orchestrationVersion ?? ORCHESTRATION_VERSION_DISPLAY),
    intent: String(raw.intent ?? ""),
    status,
    currentStage: currentStage || "CREATED",
    retries,
    createdAt: created,
    stageTimeline: stageTimeline.length > 0 ? stageTimeline : ["CREATED"],
    durationMs,
    startedAt: raw.startedAt != null && String(raw.startedAt) ? String(raw.startedAt) : created,
    outcome: String(raw.outcome ?? status),
    timelineEvents: undefined,
  };
}

export async function fetchObservabilityExecutions(
  params: ListObservabilityExecutionsParams,
): Promise<{ items: MockObsExecutionRow[]; nextCursor: string | null }> {
  const search = new URLSearchParams();
  if (params.userId) search.set("userId", params.userId);
  if (params.scenarioId) search.set("scenarioId", params.scenarioId);
  if (params.executionId) search.set("executionId", params.executionId);
  if (params.intentContains) search.set("intentContains", params.intentContains);
  if (params.status) search.set("status", params.status);
  if (params.timeFrom) search.set("timeFrom", params.timeFrom);
  if (params.timeTo) search.set("timeTo", params.timeTo);
  if (params.cursor) search.set("cursor", params.cursor);
  search.set("pageSize", String(params.pageSize ?? 100));

  const q = search.toString();
  const data = await apiFetch<ObservabilityExecutionsPageJson>(`/api/v1/admin/observability/executions?${q}`);
  const items = (data.items ?? []).map((row) => mapExecutionSummaryToMockRow(row));
  return {
    items,
    nextCursor: data.nextCursor == null || data.nextCursor === "" ? null : String(data.nextCursor),
  };
}
