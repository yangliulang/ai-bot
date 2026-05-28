import { describe, expect, it } from "vitest";
import { getSkillMarkdownFromDisk } from "./skillRegistryNodeFs";
import {
  formatConfirmRuleTitle,
  operationBrief,
  parseConfirmRules,
  parseSkillOperationView,
} from "./parseSkillOperationView";

describe("parseSkillOperationView", () => {
  it("解析金样 limit_order §1～§6 表格", () => {
    const body = getSkillMarkdownFromDisk("spot/skill.spot.limit_order.md");
    expect(body).toBeTruthy();
    const view = parseSkillOperationView(body!);
    expect(view.requiredParams.rows.length).toBeGreaterThanOrEqual(5);
    expect(view.confirmation.rows.length).toBeGreaterThanOrEqual(5);
    expect(view.refusals.rows.length).toBeGreaterThanOrEqual(1);
    expect(view.skillId).toContain("skill.spot.limit_order");
    expect(operationBrief(view)).toMatch(/必填/);
    expect(view.confirmRules.length).toBeGreaterThanOrEqual(3);
    expect(formatConfirmRuleTitle(view.confirmRules[0].title)).toMatch(/确认之前/);
  });

  it("parseConfirmRules 将 §3 prose 拆条且不含表格残留", () => {
    const body = getSkillMarkdownFromDisk("spot/skill.spot.limit_order.md");
    const s3 = body!.match(
      /## 3\. Confirmation[\s\S]*?(?=\n## 4\.)/,
    )?.[0];
    expect(s3).toBeTruthy();
    const prose = s3!
      .split("\n")
      .filter((l) => !l.trim().startsWith("|"))
      .join("\n")
      .replace(/^##[^\n]*\n/, "")
      .trim();
    const rules = parseConfirmRules(prose);
    expect(rules.some((r) => /步骤|确认之前/i.test(r.title))).toBe(true);
    expect(rules.every((r) => !r.body.includes("|"))).toBe(true);
  });
});
