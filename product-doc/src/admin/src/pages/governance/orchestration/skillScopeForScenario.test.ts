import { describe, expect, it } from "vitest";
import { resolveScenarioSkillScope } from "./skillScopeForScenario";

describe("resolveScenarioSkillScope", () => {
  it("write scenario maps primary skill", () => {
    const s = resolveScenarioSkillScope("trade.spot.limit_order", "write");
    expect(s.mode).toBe("write_skill");
    expect(s.skills[0]?.skillId).toBe("skill.spot.limit_order");
    expect(s.promptStrategyPackId).toBe("pp-trading-spot-limit");
  });

  it("read scenario has no write skill", () => {
    const s = resolveScenarioSkillScope("market.read_quote", "read");
    expect(s.mode).toBe("read_only");
    expect(s.skills).toHaveLength(0);
  });

  it("unmapped write scenario", () => {
    const s = resolveScenarioSkillScope("margin.cross.transfer_in", "write");
    expect(s.mode).toBe("unmapped_write");
  });
});
