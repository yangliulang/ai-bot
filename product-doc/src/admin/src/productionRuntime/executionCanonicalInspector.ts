/**
 * 执行详情 · Canonical Inspector（Demo）
 * 对齐 specs/design/canonical-trading-model.md · executionGatewayWriteBarrier
 */

import type { MockObsTimelineEventRow } from "../data/types";
import { EXECUTION_CANONICAL_NOTES } from "../copy/opsPanelHints";
import { runExecutionGatewayWriteBarrier } from "./executionGatewayWriteBarrier";
import { parseSkillSpecReadFromTimeline } from "./skillSpecTimeline";
import { isWriteScenario, resolveSkillIdForScenario } from "../skillPublish/scenarioSkillMap";

export type CanonicalProvenanceRow = { field: string; source: string };

export type ExecutionCanonicalInspectView = {
  applicable: boolean;
  scenarioId: string;
  skillId: string | null;
  canonicalOp: string | null;
  canonicalPayload: Record<string, unknown> | null;
  confirmationSnapshot: Record<string, unknown> | null;
  provenance: CanonicalProvenanceRow[];
  barrierOk: boolean | null;
  barrierCode: string | null;
  barrierMessage: string | null;
  note: string;
};

const CANONICAL_OP_BY_SKILL: Record<string, string> = {
  "skill.spot.flash_convert": "place_market_order",
  "skill.spot.limit_order": "place_limit_order",
  "skill.spot.amend_limit_order": "amend_limit_order",
  "skill.futures.market_order": "place_market_order",
  "skill.futures.limit_order": "place_limit_order",
  "skill.futures.amend_limit_order": "amend_limit_order",
  "skill.futures.take_profit_stop": "place_conditional_order",
  "skill.margin.cross_market_order": "place_market_order",
  "skill.margin.cross_limit_order": "place_limit_order",
  "skill.wealth.subscribe": "wealth_subscribe",
  "skill.wealth.redeem": "wealth_redeem",
};

function demoPayloadForSkill(skillId: string): Record<string, unknown> {
  if (skillId.includes("flash") || skillId.includes("market_order")) {
    return { symbol: "BTCUSDT", side: "BUY", quantity: "0.01" };
  }
  if (skillId.includes("limit")) {
    return { symbol: "BTCUSDT", side: "BUY", quantity: "0.01", price: "65000" };
  }
  if (skillId.startsWith("skill.wealth")) {
    return { productId: "flex-usdt", amount: "100" };
  }
  return { symbol: "BTCUSDT", side: "BUY", quantity: "0.01" };
}

function hasWritePathConfirmation(events: MockObsTimelineEventRow[] | undefined): boolean {
  return (
    events?.some(
      (e) =>
        e.eventName === "user.confirmed" ||
        e.transitionTrigger === "user.confirmed" ||
        e.eventName === "confirmation.required",
    ) ?? false
  );
}

function demoInspectForFailure(
  scenarioId: string,
  skillId: string,
  mode: "billing_blocked" | "tool_failed" | "snapshot_mismatch",
): ExecutionCanonicalInspectView {
  const payload = demoPayloadForSkill(skillId);
  const snapshot =
    mode === "snapshot_mismatch"
      ? { ...payload, quantity: "0.02" }
      : { ...payload };
  const barrier = runExecutionGatewayWriteBarrier({
    missingRequiredSlots: [],
    economicFields: [{ field: "quantity", source: "runtime_read_balance" }],
    canonicalPayload: payload,
    confirmationSnapshot: snapshot,
    validationStatus: mode === "tool_failed" ? "fail" : "pass",
  });

  return {
    applicable: true,
    scenarioId,
    skillId,
    canonicalOp: CANONICAL_OP_BY_SKILL[skillId] ?? "write_op",
    canonicalPayload: payload,
    confirmationSnapshot: snapshot,
    provenance: [
      { field: "quantity", source: "runtime_read_balance" },
      { field: "symbol", source: "user_utterance" },
    ],
    barrierOk: barrier.ok,
    barrierCode: barrier.ok ? null : barrier.code,
    barrierMessage: barrier.ok
      ? null
      : mode === "billing_blocked"
        ? "预览：计费门禁在出站前阻断（未真实出站）。"
        : barrier.message,
    note:
      mode === "billing_blocked"
        ? EXECUTION_CANONICAL_NOTES.billingBlocked
        : EXECUTION_CANONICAL_NOTES.demoDefault,
  };
}

export function buildExecutionCanonicalInspect(params: {
  executionId: string;
  scenarioId: string;
  outcome?: string;
  timelineEvents?: MockObsTimelineEventRow[];
}): ExecutionCanonicalInspectView {
  const { executionId, scenarioId, outcome, timelineEvents } = params;

  if (!isWriteScenario(scenarioId)) {
    return {
      applicable: false,
      scenarioId,
      skillId: null,
      canonicalOp: null,
      canonicalPayload: null,
      confirmationSnapshot: null,
      provenance: [],
      barrierOk: null,
      barrierCode: null,
      barrierMessage: null,
      note: EXECUTION_CANONICAL_NOTES.readOnly,
    };
  }

  const skillId =
    parseSkillSpecReadFromTimeline(timelineEvents)?.skillId ?? resolveSkillIdForScenario(scenarioId) ?? null;

  if (!skillId) {
    return {
      applicable: false,
      scenarioId,
      skillId: null,
      canonicalOp: null,
      canonicalPayload: null,
      confirmationSnapshot: null,
      provenance: [],
      barrierOk: null,
      barrierCode: null,
      barrierMessage: null,
      note: EXECUTION_CANONICAL_NOTES.unmappedSkill,
    };
  }

  if (executionId === "20260501002002" || outcome === "BILLING_BLOCKED") {
    return demoInspectForFailure(scenarioId, skillId, "billing_blocked");
  }
  if (executionId === "20260501004001" || outcome === "FAILED") {
    return demoInspectForFailure(scenarioId, skillId, "tool_failed");
  }
  if (executionId === "20260501003099") {
    return {
      applicable: true,
      scenarioId,
      skillId,
      canonicalOp: CANONICAL_OP_BY_SKILL[skillId] ?? "write_op",
      canonicalPayload: demoPayloadForSkill(skillId),
      confirmationSnapshot: null,
      provenance: [],
      barrierOk: null,
      barrierCode: "UNKNOWN_PENDING",
      barrierMessage: "终态未确认 · 出站结果待对账",
      note: EXECUTION_CANONICAL_NOTES.unknownPending,
    };
  }

  const payload = demoPayloadForSkill(skillId);
  const snapshot = { ...payload };
  const confirmed = hasWritePathConfirmation(timelineEvents);
  const barrier = runExecutionGatewayWriteBarrier({
    missingRequiredSlots: [],
    economicFields: [{ field: "quantity", source: "runtime_read_balance" }],
    canonicalPayload: payload,
    confirmationSnapshot: snapshot,
    validationStatus: "pass",
  });

  return {
    applicable: true,
    scenarioId,
    skillId,
    canonicalOp: CANONICAL_OP_BY_SKILL[skillId] ?? "write_op",
    canonicalPayload: payload,
    confirmationSnapshot: confirmed ? snapshot : null,
    provenance: [
      { field: "quantity", source: "runtime_read_balance" },
      { field: "symbol", source: "user_utterance" },
    ],
    barrierOk: confirmed ? barrier.ok : null,
    barrierCode: confirmed && !barrier.ok ? barrier.code : null,
    barrierMessage:
      confirmed && !barrier.ok
        ? barrier.message
        : confirmed
          ? null
          : "尚未到达用户确认（无确认快照）",
    note: EXECUTION_CANONICAL_NOTES.demoDefault,
  };
}
