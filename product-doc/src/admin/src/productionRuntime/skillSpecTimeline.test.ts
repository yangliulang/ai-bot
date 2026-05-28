import { describe, expect, it } from "vitest";
import {
  ensureWritePathSkillSpecRead,
  parseSkillSpecReadFromTimeline,
  SKILL_SPEC_READ_EVENT,
} from "./skillSpecTimeline";

describe("Production Runtime · skillSpecTimeline", () => {
  it("写路径须在 confirmation.required 之前插入 agent.skill.spec_read", () => {
    const events = ensureWritePathSkillSpecRead(
      [
        {
          at: "2026-05-07T01:00:00.000Z",
          eventName: "execution.dispatched",
          transitionTrigger: "execution.dispatched",
        },
        {
          at: "2026-05-07T01:00:02.000Z",
          eventName: "confirmation.required",
          transitionTrigger: "confirmation.required",
        },
      ],
      "trade.spot.limit_order",
    );
    const specIdx = events.findIndex((e) => e.eventName === SKILL_SPEC_READ_EVENT);
    const confirmIdx = events.findIndex((e) => e.transitionTrigger === "confirmation.required");
    expect(specIdx).toBeGreaterThanOrEqual(0);
    expect(specIdx).toBeLessThan(confirmIdx);
    expect(events[specIdx]!.skillSpecRead?.skillId).toBe("skill.spot.limit_order");
  });

  it("parseSkillSpecReadFromTimeline 可读结构化或 summary", () => {
    const parsed = parseSkillSpecReadFromTimeline([
      {
        at: "t",
        eventName: SKILL_SPEC_READ_EVENT,
        summary: "skillId=skill.spot.limit_order; skillSpecVersion=0.1.0-mvp; phase=success",
        skillSpecRead: {
          skillId: "skill.spot.limit_order",
          skillSpecVersion: "0.1.0-mvp",
          phase: "success",
        },
      },
    ]);
    expect(parsed?.phase).toBe("success");
  });

  it("只读场景不注入", () => {
    const events = ensureWritePathSkillSpecRead(
      [{ at: "t", eventName: "execution.dispatched" }],
      "orders.read_activity",
    );
    expect(events.some((e) => e.eventName === SKILL_SPEC_READ_EVENT)).toBe(false);
  });
});
