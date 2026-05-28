import { beforeEach, describe, expect, it } from "vitest";
import { assertPublishRequiredContractFiles } from "../skillContract/repoManifest";
import { readSkillOperationSpec, SkillPublishError } from "./readSkillOperationSpec";
import {
  countRuntimePublishedSkills,
  publishSkillOperationSpecLocal,
  reloadSkillPublishStoreFromDisk,
  seedAllPublishRequiredSkills,
} from "./skillPublishService";
import { resetSkillPublishStore } from "./skillPublishStore";

describe("skill Publish · Runtime 演示", () => {
  beforeEach(() => {
    resetSkillPublishStore();
    reloadSkillPublishStoreFromDisk();
  });

  it("Git publishRequired 通过后可 seed 并 read_skill_operation_spec", async () => {
    expect(assertPublishRequiredContractFiles()).toEqual([]);
    const seeded = await seedAllPublishRequiredSkills();
    expect(seeded).toBeGreaterThanOrEqual(11);
    const { published, total } = countRuntimePublishedSkills();
    expect(published).toBe(total);
    expect(total).toBe(11);

    const body = await readSkillOperationSpec("skill.spot.limit_order", "0.1.0-mvp", {
      autoSeed: false,
    });
    expect(body.bodyMarkdown).toContain("## 1.");
    expect(body.bodyMarkdown).toContain("contract-complete");
    expect(body.specDigest).toMatch(/^[a-f0-9]{64}$/);
  });

  it("未发布版本返回 PROMPT_SKILL_REF_INVALID", async () => {
    await expect(
      readSkillOperationSpec("skill.spot.limit_order", "9.9.9-contract", { autoSeed: false }),
    ).rejects.toMatchObject({ code: "PROMPT_SKILL_REF_INVALID" });
  });

  it("Publish 幂等：同版本重复发布不报错", async () => {
    await publishSkillOperationSpecLocal("skill.spot.flash_convert");
    const again = await publishSkillOperationSpecLocal("skill.spot.flash_convert");
    expect(again.lifecycle).toBe("PUBLISHED");
  });
});

describe("skill Publish · versionCompare", () => {
  it("SkillPublishError 可转 problem", () => {
    const err = new SkillPublishError("PROMPT_SKILL_REF_INVALID", "test", 404);
    expect(err.toProblem().code).toBe("PROMPT_SKILL_REF_INVALID");
  });
});
