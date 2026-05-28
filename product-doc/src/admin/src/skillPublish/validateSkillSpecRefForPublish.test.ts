import { describe, expect, it } from "vitest";
import { validateSkillSpecRefForPublish } from "./validateSkillSpecRefForPublish";

describe("validateSkillSpecRefForPublish · 登记册（无 Runtime localStorage）", () => {
  it("TRADING + 有效 ref → ok", async () => {
    const r = await validateSkillSpecRefForPublish({
      promptPackKind: "TRADING",
      skillSpecRef: "skill.spot.limit_order@0.1.0-mvp",
      scenarioId: "trade.spot.limit_order",
    });
    expect(r.ok).toBe(true);
    expect(r.resolved?.skillId).toBe("skill.spot.limit_order");
  });

  it("TRADING + 未知版本 → PROMPT_SKILL_REF_INVALID", async () => {
    const r = await validateSkillSpecRefForPublish({
      promptPackKind: "TRADING",
      skillSpecRef: "skill.spot.limit_order@9.9.9-contract",
      scenarioId: "trade.spot.limit_order",
    });
    expect(r.ok).toBe(false);
    expect(r.code).toBe("PROMPT_SKILL_REF_INVALID");
  });

  it("SYSTEM 不要求 skill", async () => {
    const r = await validateSkillSpecRefForPublish({
      promptPackKind: "SYSTEM",
      skillSpecRef: "",
      scenarioId: "",
    });
    expect(r.ok).toBe(true);
  });
});
