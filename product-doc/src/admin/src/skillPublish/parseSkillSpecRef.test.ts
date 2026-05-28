import { describe, expect, it } from "vitest";
import { formatSkillSpecRef, parseSkillSpecRef } from "./parseSkillSpecRef";

describe("parseSkillSpecRef", () => {
  it("解析 skillId@version", () => {
    const p = parseSkillSpecRef("skill.spot.limit_order@0.1.0-mvp", "trade.spot.limit_order");
    expect(p?.skillId).toBe("skill.spot.limit_order");
    expect(p?.skillSpecVersion).toBe("0.1.0-mvp");
    expect(p?.source).toBe("explicit");
  });

  it("legacy trade-assistant@ 由 scenario 推断", () => {
    const p = parseSkillSpecRef("trade-assistant@skill-v2026.04", "trade.spot.limit_order");
    expect(p?.skillId).toBe("skill.spot.limit_order");
    expect(p?.source).toBe("legacy");
  });

  it("空 ref + 写场景 scenario 推断", () => {
    const p = parseSkillSpecRef("", "trade.spot.flash_convert");
    expect(p?.skillId).toBe("skill.spot.flash_convert");
    expect(p?.source).toBe("scenario");
  });

  it("format 往返", () => {
    const p = parseSkillSpecRef("skill.futures.limit_order@0.1.0-mvp", undefined);
    expect(p && formatSkillSpecRef(p)).toBe("skill.futures.limit_order@0.1.0-mvp");
  });
});
