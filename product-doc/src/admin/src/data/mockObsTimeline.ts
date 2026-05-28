import {
  buildDefaultResolvedPromptBinding,
  ensureWritePathObservabilityTimeline,
} from "../productionRuntime/promptBindingTimeline";
import { isWriteScenario } from "../skillPublish/scenarioSkillMap";
import type { MockObsExecutionRow, MockObsTimelineEventRow } from "./types";

function isoAddMs(iso: string, ms: number): string {
  const d = new Date(iso);
  return new Date(d.getTime() + ms).toISOString();
}

function normalizeIso(iso: string): string {
  if (iso.includes(".")) return iso;
  return iso.replace(/Z$/, ".000Z");
}

/** 写路径 · 进行中（至工具回合，未收尾） */
export function buildWritePathRunningTimeline(
  scenarioId: string,
  sessionId: string,
  startedAt: string,
): MockObsTimelineEventRow[] {
  const t0 = normalizeIso(startedAt);
  return ensureWritePathObservabilityTimeline(
    [
      {
        at: t0,
        eventName: "execution.dispatched",
        summary: "accepted→planning",
        transitionTrigger: "execution.dispatched",
      },
      {
        at: isoAddMs(t0, 1100),
        eventName: "confirmation.required",
        summary: "writePath:typeA",
        transitionTrigger: "confirmation.required",
      },
      {
        at: isoAddMs(t0, 2200),
        eventName: "user.confirmed",
        summary: "waiting_confirmation→executing",
        transitionTrigger: "user.confirmed",
      },
      {
        at: isoAddMs(t0, 4800),
        eventName: "tool.round_complete",
        summary: "order.submitted; executing→settling",
        transitionTrigger: "tool.round_complete",
      },
    ],
    scenarioId,
    sessionId,
  );
}

/** 写路径 · 计费闸门阻断 */
export function buildBillingBlockedTimeline(
  scenarioId: string,
  sessionId: string,
  startedAt: string,
): MockObsTimelineEventRow[] {
  const t0 = normalizeIso(startedAt);
  return ensureWritePathObservabilityTimeline(
    [
      {
        at: t0,
        eventName: "execution.dispatched",
        summary: "accepted→planning",
        transitionTrigger: "execution.dispatched",
      },
      {
        at: isoAddMs(t0, 900),
        eventName: "confirmation.required",
        summary: "writePath:typeA",
        transitionTrigger: "confirmation.required",
      },
      {
        at: isoAddMs(t0, 1800),
        eventName: "user.confirmed",
        summary: "waiting_confirmation→executing",
        transitionTrigger: "user.confirmed",
      },
      {
        at: isoAddMs(t0, 3200),
        eventName: "tool.round_complete",
        summary: "order.submitted",
        transitionTrigger: "tool.round_complete",
      },
      {
        at: isoAddMs(t0, 4100),
        eventName: "settlement.failed",
        summary: "billing gate; entitlement quota REJECTED",
        transitionTrigger: "settlement.failed",
      },
    ],
    scenarioId,
    sessionId,
  );
}

/** 只读场景 · 无 binding/spec_read */
function buildReadOnlyTimeline(
  startedAt: string,
  status: MockObsExecutionRow["status"],
): MockObsTimelineEventRow[] {
  const t0 = normalizeIso(startedAt);
  const rows: MockObsTimelineEventRow[] = [
    {
      at: t0,
      eventName: "execution.dispatched",
      summary: "只读请求已受理",
      transitionTrigger: "execution.dispatched",
    },
    {
      at: isoAddMs(t0, 600),
      eventName: "tool.round_complete",
      summary: "查询回合完成",
      transitionTrigger: "tool.round_complete",
    },
  ];
  if (status === "COMPLETED") {
    rows.push({
      at: isoAddMs(t0, 1200),
      eventName: "reconciliation.success",
      summary: "回合收尾",
      transitionTrigger: "reconciliation.success",
    });
  }
  return rows;
}

/** 列表批量演示行 · 按 status / 场景生成 MC801 下限 */
export function buildDemoObsTimeline(params: {
  status: MockObsExecutionRow["status"];
  scenarioId: string;
  sessionId: string;
  startedAt: string;
}): MockObsTimelineEventRow[] {
  const { status, scenarioId, sessionId, startedAt } = params;
  if (!isWriteScenario(scenarioId)) {
    return buildReadOnlyTimeline(startedAt, status);
  }

  const t0 = normalizeIso(startedAt);

  switch (status) {
    case "COMPLETED":
      return ensureWritePathObservabilityTimeline(
        [
          {
            at: t0,
            eventName: "execution.dispatched",
            summary: "accepted→planning",
            transitionTrigger: "execution.dispatched",
          },
          {
            at: isoAddMs(t0, 1000),
            eventName: "confirmation.required",
            summary: "writePath:typeA",
            transitionTrigger: "confirmation.required",
          },
          {
            at: isoAddMs(t0, 2000),
            eventName: "user.confirmed",
            summary: "waiting_confirmation→executing",
            transitionTrigger: "user.confirmed",
          },
          {
            at: isoAddMs(t0, 4500),
            eventName: "tool.round_complete",
            summary: "order.submitted",
            transitionTrigger: "tool.round_complete",
          },
          {
            at: isoAddMs(t0, 6200),
            eventName: "reconciliation.success",
            summary: "billing eligible",
            transitionTrigger: "reconciliation.success",
          },
        ],
        scenarioId,
        sessionId,
      );
    case "RUNNING":
      return buildWritePathRunningTimeline(scenarioId, sessionId, startedAt);
    case "CREATED":
      return ensureWritePathObservabilityTimeline(
        [
          {
            at: t0,
            eventName: "execution.dispatched",
            summary: "accepted→planning",
            transitionTrigger: "execution.dispatched",
          },
        ],
        scenarioId,
        sessionId,
      );
    case "FAILED":
      return ensureWritePathObservabilityTimeline(
        [
          {
            at: t0,
            eventName: "execution.dispatched",
            summary: "accepted→planning",
            transitionTrigger: "execution.dispatched",
          },
          {
            at: isoAddMs(t0, 900),
            eventName: "confirmation.required",
            summary: "writePath:typeA",
            transitionTrigger: "confirmation.required",
          },
          {
            at: isoAddMs(t0, 1600),
            eventName: "user.confirmed",
            summary: "waiting_confirmation→executing",
            transitionTrigger: "user.confirmed",
          },
          {
            at: isoAddMs(t0, 2200),
            eventName: "tool.final_failed",
            summary: "invocationState:FAILED",
            transitionTrigger: "tool.final_failed",
          },
        ],
        scenarioId,
        sessionId,
      );
    case "BLOCKED":
      return buildBillingBlockedTimeline(scenarioId, sessionId, startedAt);
    case "UNKNOWN":
      return ensureWritePathObservabilityTimeline(
        [
          {
            at: t0,
            eventName: "execution.dispatched",
            summary: "accepted→planning",
            transitionTrigger: "execution.dispatched",
          },
          {
            at: isoAddMs(t0, 3500),
            eventName: "exchange.504",
            summary: "终态不可判",
            transitionTrigger: "exchange.504",
          },
          {
            at: isoAddMs(t0, 8000),
            eventName: "reconciliation.inconclusive",
            summary: "证据不足",
            transitionTrigger: "reconciliation.inconclusive",
          },
        ],
        scenarioId,
        sessionId,
      );
    default:
      return buildReadOnlyTimeline(startedAt, status);
  }
}

export function resolvedPromptBindingForDemo(
  scenarioId: string,
  sessionId: string,
): MockObsExecutionRow["resolvedPromptBinding"] | undefined {
  if (!isWriteScenario(scenarioId)) return undefined;
  return buildDefaultResolvedPromptBinding({ scenarioId, sessionId });
}
