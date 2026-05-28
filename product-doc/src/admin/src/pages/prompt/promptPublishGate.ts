import type { MockPromptPack } from "../../data/types";
import { validateSkillSpecRefForPublish } from "../../skillPublish/validateSkillSpecRefForPublish";
import {
  buildGateTrace,
  skillScopeToRejection,
  validatePublishDemoStructured,
  type PromptPublishGateTrace,
} from "./promptPublishRejectTrace";

export type { PromptPublishGateTrace } from "./promptPublishRejectTrace";

/** @deprecated 使用 PromptPublishGateTrace */
export type PromptPublishGateResult = PromptPublishGateTrace;

/** 发布前门禁：场景/体积/锁定（同步）+ Runtime 技能范围（异步） */
export async function runPromptPublishGate(
  pack: MockPromptPack,
  scenarioId: string,
  body: string,
): Promise<PromptPublishGateTrace> {
  const rejections = [...validatePublishDemoStructured(pack, scenarioId, body)];

  const skill = await validateSkillSpecRefForPublish({
    promptPackKind: pack.kind,
    skillSpecRef: pack.skillSpecRef,
    scenarioId,
  });
  const skillRejection = skillScopeToRejection(skill);
  if (skillRejection) rejections.push(skillRejection);

  return buildGateTrace(rejections);
}
