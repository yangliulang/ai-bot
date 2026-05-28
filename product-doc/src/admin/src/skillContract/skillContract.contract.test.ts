import { describe, expect, it } from "vitest";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { EVAL_SKILL_FIXTURES } from "./fixtures";
import {
  canProceedToTypeA,
  isValidAmendWriteSequence,
  marginCrossWriteAllowed,
} from "./gates";
import { assertPublishRequiredContractFiles } from "./repoManifest";

const REPO_ROOT = join(import.meta.dirname, "../../../..");

/**
 * 对应 specs/requirements/evals/skill-contract.md P0 束 +
 * specs/requirements/skill-specs/scripts/check_skill_contract_complete.py（TS 同窗下限）。
 */
describe("skill contract · Git manifest（publishRequired）", () => {
  it("11 篇 publishRequired 须含 §1～§6 与 contract-complete", () => {
    const errors = assertPublishRequiredContractFiles();
    expect(errors, errors.join("\n")).toEqual([]);
  });
});

describe("skill contract · Runtime Publish bundle", () => {
  it("runtime-bundle.json 含 11 篇 publishRequired 全文", () => {
    const bundlePath = join(REPO_ROOT, "specs/requirements/skill-specs/published/runtime-bundle.json");
    expect(existsSync(bundlePath)).toBe(true);
    const bundle = JSON.parse(readFileSync(bundlePath, "utf-8")) as {
      itemCount: number;
      items: { skillId: string; bodyMarkdown: string }[];
    };
    expect(bundle.itemCount).toBe(11);
    expect(bundle.items.length).toBe(11);
    for (const item of bundle.items) {
      expect(item.bodyMarkdown).toContain("## 1.");
      expect(item.bodyMarkdown).toContain("contract-complete");
    }
  });
});

describe("skill contract · OpenAPI 骨架", () => {
  it("skill-operation-spec-schemas 与 prompt-management 路径存在", () => {
    const schema = join(
      REPO_ROOT,
      "specs/openapi/components/skill-operation-spec-schemas.yaml",
    );
    const api = join(REPO_ROOT, "specs/openapi/admin/prompt-management.yaml");
    expect(existsSync(schema)).toBe(true);
    expect(existsSync(api)).toBe(true);
    const apiText = readFileSync(api, "utf-8");
    expect(apiText).toContain("/api/v1/internal/skills/effective");
    expect(apiText).toContain("publishSkillOperationSpec");
  });
});

describe("eval.skill.* · 槽位门禁（gates.ts 演示实现）", () => {
  for (const fx of EVAL_SKILL_FIXTURES) {
    it(fx.evalSetId, () => {
      const gate = canProceedToTypeA(fx.skillId, fx.slots);
      if (fx.expectTypeA) {
        expect(gate.ok, gate.missing.join(",")).toBe(true);
      } else {
        expect(gate.ok).toBe(false);
      }

      if (fx.amendSequence) {
        expect(isValidAmendWriteSequence(fx.amendSequence)).toBe(true);
        const bad = [...fx.amendSequence].reverse();
        expect(isValidAmendWriteSequence(bad)).toBe(false);
      }

      if (fx.marginConfirmCount !== undefined) {
        expect(marginCrossWriteAllowed(fx.marginConfirmCount)).toBe(fx.expectWrite);
      } else if (fx.amendSequence) {
        expect(isValidAmendWriteSequence(fx.amendSequence)).toBe(true);
      } else {
        expect(fx.expectWrite).toBe(false);
      }
    });
  }
});
