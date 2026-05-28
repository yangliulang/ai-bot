/** 与 `specs/openapi/components/skill-operation-spec-schemas.yaml` 同窗 */

export type SkillSpecLifecycle = "DRAFT" | "PUBLISHED" | "DEPRECATED";

export type SkillOperationSpecSummary = {
  skillId: string;
  skillSpecVersion: string;
  lifecycle: SkillSpecLifecycle;
  scenarioIds?: string[];
  contractComplete?: boolean;
  specDigest?: string;
  publishedAt?: string | null;
};

export type SkillOperationSpecList = {
  items: SkillOperationSpecSummary[];
};

export type SkillOperationSpecBody = {
  skillId: string;
  skillSpecVersion: string;
  bodyMarkdown: string;
  specDigest?: string;
  sourceGitRef?: string | null;
};

export type SkillSpecPublishRequest = {
  skillSpecVersion: string;
  bodyMarkdown?: string;
  sourceGitRef?: string | null;
  specDigest?: string;
};

export type SkillSpecPublishResult = {
  skillId: string;
  skillSpecVersion: string;
  lifecycle: SkillSpecLifecycle;
  specDigest?: string;
};

export type EffectiveSkillSpecResponse = {
  skillId: string;
  skillSpecVersion: string;
  bodyMarkdown: string;
  specDigest?: string;
  etag?: string;
};

export type SkillSpecVersionHistory = {
  skillId: string;
  items: Array<{
    skillSpecVersion: string;
    lifecycle: SkillSpecLifecycle;
    publishedAt?: string;
  }>;
};

export type SkillPublishProblem = {
  type?: string;
  title?: string;
  detail?: string;
  code?: "PROMPT_SKILL_REF_INVALID" | "SKILL_PUBLISH_GATE_FAILED" | "SKILL_VERSION_NOT_MONOTONIC";
};
