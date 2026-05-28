import type {
  EffectiveSkillSpecResponse,
  SkillOperationSpecBody,
  SkillOperationSpecList,
  SkillOperationSpecSummary,
  SkillSpecPublishRequest,
  SkillSpecPublishResult,
  SkillSpecVersionHistory,
} from "./types/skillOperationSpec";
import { apiFetch, getApiBaseUrl } from "./http";
import {
  getEffectiveSkillOperationSpecLocal,
  getSkillOperationSpecSummaryLocal,
  getSkillOperationSpecVersionBodyLocal,
  getSkillOperationSpecVersionsLocal,
  listSkillOperationSpecsLocal,
  publishSkillOperationSpecLocal,
} from "../skillPublish/skillPublishService";

export function isSkillApiEnabled(): boolean {
  return import.meta.env.VITE_USE_SKILL_API === "true" && !!getApiBaseUrl();
}

export function listSkillOperationSpecs(): Promise<SkillOperationSpecList> {
  if (!isSkillApiEnabled()) return Promise.resolve(listSkillOperationSpecsLocal());
  return apiFetch("/api/v1/admin/skill-specs");
}

export function getSkillOperationSpec(skillId: string): Promise<SkillOperationSpecSummary> {
  if (!isSkillApiEnabled()) return Promise.resolve(getSkillOperationSpecSummaryLocal(skillId));
  return apiFetch(`/api/v1/admin/skill-specs/${encodeURIComponent(skillId)}`);
}

export function getSkillOperationSpecVersions(skillId: string): Promise<SkillSpecVersionHistory> {
  if (!isSkillApiEnabled()) return Promise.resolve(getSkillOperationSpecVersionsLocal(skillId));
  return apiFetch(`/api/v1/admin/skill-specs/${encodeURIComponent(skillId)}/versions`);
}

export function getSkillOperationSpecVersionBody(
  skillId: string,
  skillSpecVersion: string,
): Promise<SkillOperationSpecBody> {
  if (!isSkillApiEnabled()) {
    return Promise.resolve(getSkillOperationSpecVersionBodyLocal(skillId, skillSpecVersion));
  }
  return apiFetch(
    `/api/v1/admin/skill-specs/${encodeURIComponent(skillId)}/versions/${encodeURIComponent(skillSpecVersion)}`,
  );
}

export function publishSkillOperationSpec(
  skillId: string,
  body: SkillSpecPublishRequest,
): Promise<SkillSpecPublishResult> {
  if (!isSkillApiEnabled()) return publishSkillOperationSpecLocal(skillId, body);
  return apiFetch(`/api/v1/admin/skill-specs/${encodeURIComponent(skillId)}/publish`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** OpenAPI: getEffectiveSkillOperationSpec · Runtime 读 */
export function getEffectiveSkillOperationSpecRemote(
  skillId: string,
  skillSpecVersion: string,
  opts?: { ifNoneMatch?: string },
): Promise<EffectiveSkillSpecResponse> {
  const sp = new URLSearchParams({ skillId, skillSpecVersion });
  const headers: Record<string, string> = {};
  if (opts?.ifNoneMatch) headers["If-None-Match"] = opts.ifNoneMatch;
  return apiFetch(`/api/v1/internal/skills/effective?${sp.toString()}`, { headers });
}

export async function getEffectiveSkillOperationSpec(
  skillId: string,
  skillSpecVersion: string,
): Promise<EffectiveSkillSpecResponse> {
  if (isSkillApiEnabled()) {
    return getEffectiveSkillOperationSpecRemote(skillId, skillSpecVersion);
  }
  const { readSkillOperationSpec } = await import("../skillPublish/readSkillOperationSpec");
  return readSkillOperationSpec(skillId, skillSpecVersion, { autoSeed: false });
}
