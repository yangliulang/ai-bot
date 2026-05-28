/**
 * Runtime Publish · localStorage 小样（Vitest / 接 BFF 前契约对签）。
 * Admin Demo **不** 用此 store 驱动 UI；运营可用性见工具登记 **启用/停用**。
 */

import type { SkillSpecLifecycle } from "../api/types/skillOperationSpec";

const STORAGE_KEY = "agent-admin-skill-publish-runtime-v1";

export type PublishedSkillRecord = {
  skillId: string;
  skillSpecVersion: string;
  lifecycle: Extract<SkillSpecLifecycle, "PUBLISHED">;
  bodyMarkdown: string;
  specDigest: string;
  publishedAt: string;
  sourceGitRef?: string | null;
};

export type SkillPublishStore = {
  /** skillId → 当前生效版本（Runtime 读路径） */
  effective: Record<string, string>;
  /** `${skillId}@${skillSpecVersion}` → 快照 */
  versions: Record<string, PublishedSkillRecord>;
};

function versionKey(skillId: string, skillSpecVersion: string): string {
  return `${skillId}@${skillSpecVersion}`;
}

export function emptySkillPublishStore(): SkillPublishStore {
  return { effective: {}, versions: {} };
}

export function loadSkillPublishStore(): SkillPublishStore {
  if (typeof localStorage === "undefined") return emptySkillPublishStore();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptySkillPublishStore();
    const parsed = JSON.parse(raw) as Partial<SkillPublishStore>;
    return {
      effective:
        parsed.effective && typeof parsed.effective === "object" ? { ...parsed.effective } : {},
      versions:
        parsed.versions && typeof parsed.versions === "object" ? { ...parsed.versions } : {},
    };
  } catch {
    return emptySkillPublishStore();
  }
}

export function saveSkillPublishStore(store: SkillPublishStore): void {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

export function upsertPublishedRecord(
  store: SkillPublishStore,
  record: PublishedSkillRecord,
): SkillPublishStore {
  const key = versionKey(record.skillId, record.skillSpecVersion);
  return {
    effective: { ...store.effective, [record.skillId]: record.skillSpecVersion },
    versions: { ...store.versions, [key]: record },
  };
}

export function getPublishedRecord(
  store: SkillPublishStore,
  skillId: string,
  skillSpecVersion: string,
): PublishedSkillRecord | undefined {
  return store.versions[versionKey(skillId, skillSpecVersion)];
}

export function getEffectiveVersion(store: SkillPublishStore, skillId: string): string | undefined {
  return store.effective[skillId];
}

export function listPublishedVersionsForSkill(
  store: SkillPublishStore,
  skillId: string,
): PublishedSkillRecord[] {
  return Object.values(store.versions).filter((r) => r.skillId === skillId);
}

export function resetSkillPublishStore(): SkillPublishStore {
  const fresh = emptySkillPublishStore();
  saveSkillPublishStore(fresh);
  return fresh;
}
