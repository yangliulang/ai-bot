import { describe, expect, it } from "vitest";
import { countScenariosForSkill, listScenariosForSkill } from "./scenarioSkillIndex";

describe("scenarioSkillIndex", () => {
  it("lists scenarios for limit_order skill", () => {
    const ids = listScenariosForSkill("skill.spot.limit_order");
    expect(ids).toContain("trade.spot.limit_order");
    expect(countScenariosForSkill("skill.spot.limit_order")).toBeGreaterThan(0);
  });

  it("returns empty for unknown skill", () => {
    expect(listScenariosForSkill("skill.unknown")).toEqual([]);
  });
});
