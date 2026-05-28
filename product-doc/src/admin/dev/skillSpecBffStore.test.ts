import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { createSkillSpecBffStore } from "./skillSpecBffStore";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "../../..");

describe("skillSpecBffStore · runtime-bundle seed", () => {
  it("加载 11 篇且 effective 可读", () => {
    const api = createSkillSpecBffStore(repoRoot);
    const list = api.list();
    expect(list.items.length).toBe(11);
    const eff = api.getEffective("skill.spot.limit_order", "0.1.0-mvp");
    expect(eff.bodyMarkdown).toContain("## 3.");
    expect(eff.etag).toBeTruthy();
  });

  it("未知版本 → PROMPT_SKILL_REF_INVALID", () => {
    const api = createSkillSpecBffStore(repoRoot);
    expect(() => api.getEffective("skill.spot.limit_order", "9.9.9-contract")).toThrow();
  });
});
