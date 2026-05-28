import { describe, expect, it } from "vitest";
import { getSkillMarkdown } from "./skillRegistryCatalog";
import {
  getSkillMarkdownFromBundle,
  SKILL_MARKDOWN_BUNDLE_COUNT,
} from "./skillRegistryMarkdown";

describe("skillRegistryMarkdown · 正文加载", () => {
  it("Vite glob 或 Vitest 磁盘回退须能读到金样", () => {
    const fromBundle = getSkillMarkdownFromBundle("spot/skill.spot.limit_order.md");
    const fromLoader = getSkillMarkdown("spot/skill.spot.limit_order.md");
    const body = fromBundle ?? fromLoader;
    expect(body?.includes("## 1. Required")).toBe(true);
    expect(
      SKILL_MARKDOWN_BUNDLE_COUNT + (fromLoader && !fromBundle ? 1 : 0),
    ).toBeGreaterThanOrEqual(1);
  });
});
