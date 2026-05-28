import { getEffectiveSkillOperationSpec, isSkillApiEnabled } from "../api/skillSpecClient";
import {
  getSkillRegistryEntry,
  resolveSkillContractStatus,
  resolveSkillSpecVersion,
} from "../pages/tools/skillRegistryCatalog";
import { SkillPublishError } from "./skillPublishErrors";
import { formatSkillSpecRef, parseSkillSpecRef, type ParsedSkillSpecRef } from "./parseSkillSpecRef";
import { isWriteScenario } from "./scenarioSkillMap";

export type SkillSpecPublishValidation = {
  ok: boolean;
  code?: "PROMPT_SKILL_REF_INVALID" | "PROMPT_SKILL_REF_MISSING";
  reason?: string;
  resolved?: ParsedSkillSpecRef;
};

/** Demo：技能为 Git 固定登记册，无「新建/发布」；校验 ref 与登记册 + 文档就绪（非 localStorage Runtime） */
function assertSkillCatalogBinding(skillId: string, skillSpecVersion: string): void {
  const entry = getSkillRegistryEntry(skillId);
  if (!entry) {
    throw new SkillPublishError("PROMPT_SKILL_REF_INVALID", `${skillId} 不在技能登记册`, 404);
  }
  if (entry.publishRequired && resolveSkillContractStatus(skillId) !== "complete") {
    throw new SkillPublishError(
      "PROMPT_SKILL_REF_INVALID",
      `${skillId} 说明未齐全（须 contract-complete）`,
      404,
    );
  }
  const gitVersion = resolveSkillSpecVersion(skillId);
  if (gitVersion && skillSpecVersion !== gitVersion) {
    throw new SkillPublishError(
      "PROMPT_SKILL_REF_INVALID",
      `版本 ${skillSpecVersion} 与登记册元数据 ${gitVersion} 不一致`,
      404,
    );
  }
}

/**
 * FR-PM07 §2.8 · SC-PM-21：Trading 包发布前 skillSpecRef 可解析且技能在登记册就绪。
 * 所内接 BFF 时改查 Runtime PUBLISHED（`getEffectiveSkillOperationSpec`）。
 */
export async function validateSkillSpecRefForPublish(params: {
  promptPackKind: string;
  skillSpecRef?: string;
  scenarioId?: string;
}): Promise<SkillSpecPublishValidation> {
  const kind = params.promptPackKind;
  const needsSkill = kind === "TRADING" || (kind === "ANALYSIS" && Boolean(params.skillSpecRef?.trim()));

  if (!needsSkill) {
    return { ok: true };
  }

  const scenario = params.scenarioId?.trim() ?? "";
  if (kind === "TRADING" && !params.skillSpecRef?.trim() && scenario && !isWriteScenario(scenario)) {
    return { ok: true };
  }

  const resolved = parseSkillSpecRef(params.skillSpecRef, params.scenarioId);
  if (!resolved) {
    return {
      ok: false,
      code: "PROMPT_SKILL_REF_MISSING",
      reason:
        "须填写 skillSpecRef（如 skill.spot.limit_order@0.1.0-mvp），或 scenarioId 对应写路径技能（见技能登记册）。",
    };
  }

  try {
    if (isSkillApiEnabled()) {
      await getEffectiveSkillOperationSpec(resolved.skillId, resolved.skillSpecVersion);
    } else {
      assertSkillCatalogBinding(resolved.skillId, resolved.skillSpecVersion);
    }
    return { ok: true, resolved };
  } catch (e) {
    const code =
      e instanceof SkillPublishError && e.code === "PROMPT_SKILL_REF_INVALID"
        ? "PROMPT_SKILL_REF_INVALID"
        : "PROMPT_SKILL_REF_INVALID";
    const detail = e instanceof Error ? e.message : String(e);
    return {
      ok: false,
      code,
      reason: `Runtime 技能范围无效：${formatSkillSpecRef(resolved)}。${detail}`,
      resolved,
    };
  }
}
