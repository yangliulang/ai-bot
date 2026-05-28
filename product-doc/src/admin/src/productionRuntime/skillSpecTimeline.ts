/**
 * Production Runtime · `agent.skill.spec_read` 演示时间线（FR-MC801 / SC-OM-05）
 */

import type { MockObsTimelineEventRow } from "../data/types";

export const SKILL_SPEC_READ_EVENT = "agent.skill.spec_read" as const;
export const SKILL_SPEC_LOADED_TRIGGER = "skill.spec_loaded" as const;

/** 写路径 scenarioId → 登记 skillId（Demo 对签 trade-assistance §8） */
const WRITE_SCENARIO_SKILL: Record<string, string> = {
  "trade.spot.limit_order": "skill.spot.limit_order",
  "trade.spot.flash_convert": "skill.spot.flash_convert",
  "trade.futures.market_order": "skill.futures.market_order",
  "trade.futures.limit_order": "skill.futures.limit_order",
};

const DEFAULT_SKILL_VERSION: Record<string, string> = {
  "skill.spot.limit_order": "0.1.0-mvp",
  "skill.spot.flash_convert": "0.1.0-mvp",
  "skill.futures.market_order": "0.1.0-mvp",
  "skill.futures.limit_order": "0.1.0-mvp",
};

export type SkillSpecReadPhase = "success" | "fail";

export function skillIdForWriteScenario(scenarioId: string): string | undefined {
  return WRITE_SCENARIO_SKILL[scenarioId];
}

export function defaultSkillSpecVersion(skillId: string): string {
  return DEFAULT_SKILL_VERSION[skillId] ?? "0.1.0-mvp";
}

export function formatSkillSpecReadSummary(params: {
  skillId: string;
  skillSpecVersion: string;
  phase: SkillSpecReadPhase;
  specDigest?: string;
}): string {
  const parts = [
    `skillId=${params.skillId}`,
    `skillSpecVersion=${params.skillSpecVersion}`,
    `phase=${params.phase}`,
  ];
  if (params.specDigest) parts.push(`specDigest=${params.specDigest.slice(0, 16)}…`);
  return parts.join("; ");
}

export function buildSkillSpecReadTimelineRow(
  at: string,
  params: {
    skillId: string;
    skillSpecVersion: string;
    phase?: SkillSpecReadPhase;
    specDigest?: string;
  },
): MockObsTimelineEventRow {
  const phase = params.phase ?? "success";
  return {
    at,
    eventName: SKILL_SPEC_READ_EVENT,
    summary: formatSkillSpecReadSummary({ ...params, phase }),
    transitionTrigger: SKILL_SPEC_LOADED_TRIGGER,
    skillSpecRead: {
      skillId: params.skillId,
      skillSpecVersion: params.skillSpecVersion,
      phase,
      specDigest: params.specDigest,
    },
  };
}

/** 在 dispatched 之后、confirmation.required 之前插入 spec_read（若尚无） */
export function ensureWritePathSkillSpecRead(
  events: MockObsTimelineEventRow[],
  scenarioId: string,
  opts?: { specDigest?: string; phase?: SkillSpecReadPhase },
): MockObsTimelineEventRow[] {
  const skillId = skillIdForWriteScenario(scenarioId);
  if (!skillId) return events;
  if (events.some((e) => e.eventName === SKILL_SPEC_READ_EVENT)) return events;

  const version = defaultSkillSpecVersion(skillId);
  const dispatchedIdx = events.findIndex(
    (e) => e.transitionTrigger === "execution.dispatched" || e.eventName === "execution.dispatched",
  );
  const confirmIdx = events.findIndex(
    (e) => e.transitionTrigger === "confirmation.required" || e.eventName === "confirmation.required",
  );

  const anchor = dispatchedIdx >= 0 ? events[dispatchedIdx]! : events[0];
  const next = confirmIdx >= 0 ? events[confirmIdx]! : anchor;
  const at =
    dispatchedIdx >= 0 && confirmIdx > dispatchedIdx
      ? isoBetween(anchor.at, next.at)
      : isoAddMs(anchor.at, 400);

  const row = buildSkillSpecReadTimelineRow(at, {
    skillId,
    skillSpecVersion: version,
    phase: opts?.phase ?? "success",
    specDigest: opts?.specDigest ?? "demo-spec-digest-a1b2c3d4e5f6",
  });

  const insertAt = confirmIdx >= 0 ? confirmIdx : dispatchedIdx >= 0 ? dispatchedIdx + 1 : 0;
  const out = [...events];
  out.splice(insertAt, 0, row);
  return out;
}

export function parseSkillSpecReadFromTimeline(
  events: MockObsTimelineEventRow[] | undefined,
): MockObsTimelineEventRow["skillSpecRead"] | undefined {
  if (!events?.length) return undefined;
  for (const e of events) {
    if (e.skillSpecRead) return e.skillSpecRead;
    if (e.eventName !== SKILL_SPEC_READ_EVENT || !e.summary) continue;
    const skillId = e.summary.match(/skillId=([^;]+)/)?.[1]?.trim();
    const skillSpecVersion = e.summary.match(/skillSpecVersion=([^;]+)/)?.[1]?.trim();
    const phase = e.summary.match(/phase=(success|fail)/)?.[1] as SkillSpecReadPhase | undefined;
    const digestMatch = e.summary.match(/specDigest=([^;]+)/)?.[1]?.trim();
    if (skillId && skillSpecVersion && phase) {
      return {
        skillId,
        skillSpecVersion,
        phase,
        specDigest: digestMatch?.replace(/…$/, ""),
      };
    }
  }
  return undefined;
}

function isoAddMs(iso: string, ms: number): string {
  const d = new Date(iso);
  d.setTime(d.getTime() + ms);
  return d.toISOString().replace(/\.\d{3}Z$/, "Z");
}

function isoBetween(a: string, b: string): string {
  const ta = new Date(a).getTime();
  const tb = new Date(b).getTime();
  return isoAddMs(a, Math.max(200, Math.floor((tb - ta) / 2)));
}
