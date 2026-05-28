/**
 * Runtime · `read_skill_operation_spec` 演示读路径（FR-T11 / FR-PM08 同窗）
 */

import type { EffectiveSkillSpecResponse } from "../api/types/skillOperationSpec";
import { getEffectiveSkillOperationSpecRemote, isSkillApiEnabled } from "../api/skillSpecClient";
import { SkillPublishError } from "./skillPublishErrors";
import {
  getEffectiveSkillOperationSpecLocal,
  seedAllPublishRequiredSkills,
} from "./skillPublishService";

export type ReadSkillSpecOptions = {
  /** 演示：缺发布记录时自动 seed（默认 true） */
  autoSeed?: boolean;
};

/**
 * 加载已发布技能全文 §1～§6；未发布 → `PROMPT_SKILL_REF_INVALID`
 */
export async function readSkillOperationSpec(
  skillId: string,
  skillSpecVersion: string,
  opts?: ReadSkillSpecOptions,
): Promise<EffectiveSkillSpecResponse> {
  if (isSkillApiEnabled()) {
    return getEffectiveSkillOperationSpecRemote(skillId, skillSpecVersion);
  }
  try {
    return getEffectiveSkillOperationSpecLocal(skillId, skillSpecVersion);
  } catch (e) {
    if (
      opts?.autoSeed !== false &&
      e instanceof SkillPublishError &&
      e.code === "PROMPT_SKILL_REF_INVALID"
    ) {
      await seedAllPublishRequiredSkills();
      return getEffectiveSkillOperationSpecLocal(skillId, skillSpecVersion);
    }
    throw e;
  }
}

export { SkillPublishError };
