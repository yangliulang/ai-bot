import { describe, expect, it } from "vitest";
import {
  buildSkillRegistryRows,
  resolveSkillContractStatus,
  resolveSkillSpecVersion,
  SKILL_REGISTRY_ENTRIES,
} from "./skillRegistryCatalog";
import { getSkillMarkdownFromDisk } from "./skillRegistryNodeFs";
import { getSkillMarkdownFromBundle } from "./skillRegistryMarkdown";

describe("skillRegistryCatalog · 单源与 manifest 同窗", () => {
  it("14 条登记与 build 行一一对应", () => {
    const rows = buildSkillRegistryRows();
    expect(rows).toHaveLength(SKILL_REGISTRY_ENTRIES.length);
    for (const e of SKILL_REGISTRY_ENTRIES) {
      const row = rows.find((r) => r.stableId === e.skillId);
      expect(row?.summary).toBe(e.summary);
      expect(row?.userFlow).toBe(e.userFlow);
      expect(row?.exchangeAction).toBe(e.exchangeAction);
    }
  });

  it("publishRequired 须从 Git 解析 skillSpecVersion", () => {
    for (const e of SKILL_REGISTRY_ENTRIES.filter((x) => x.publishRequired)) {
      const v = resolveSkillSpecVersion(e.skillId);
      expect(v, e.skillId).toBeTruthy();
      expect(v).not.toBe("0.1.0-demo");
    }
  });

  it("无正文项：oco/bracket/transfer 为 n/a 且默认停用", () => {
    for (const id of [
      "skill.spot.oco",
      "skill.spot.bracket",
      "skill.margin.transfer_spot_to_cross",
    ]) {
      expect(resolveSkillContractStatus(id)).toBe("n/a");
      const row = buildSkillRegistryRows().find((r) => r.stableId === id);
      expect(row?.defaultEnabled).toBe(false);
      expect(row?.matrixStatus).toBe("tbd");
    }
  });

  it("Vitest 下 glob 或磁盘至少能加载金样正文", () => {
    const sample =
      getSkillMarkdownFromBundle("spot/skill.spot.limit_order.md") ??
      getSkillMarkdownFromDisk("spot/skill.spot.limit_order.md");
    expect(sample?.includes("contract-complete")).toBe(true);
  });

  it("11 篇 publishRequired 为 contract-complete", () => {
    const pub = SKILL_REGISTRY_ENTRIES.filter((e) => e.publishRequired);
    expect(pub).toHaveLength(11);
    const errors = pub.filter((e) => resolveSkillContractStatus(e.skillId) !== "complete");
    expect(errors.map((e) => e.skillId)).toEqual([]);
  });
});
