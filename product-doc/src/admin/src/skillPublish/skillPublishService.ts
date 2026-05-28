/**
 * Runtime Publish · 演示实现（Git 全文 → 版本化快照 → read_skill_operation_spec）
 * 对齐 specs/requirements/skill-specs/PUBLISH.md · OpenAPI `getEffectiveSkillOperationSpec`
 */

import type {
  EffectiveSkillSpecResponse,
  SkillOperationSpecBody,
  SkillOperationSpecList,
  SkillOperationSpecSummary,
  SkillSpecPublishRequest,
  SkillSpecPublishResult,
  SkillSpecVersionHistory,
} from "../api/types/skillOperationSpec";
import {
  getSkillMarkdown,
  getSkillRegistryEntry,
  resolveSkillContractStatus,
  resolveSkillSpecVersion,
  SKILL_REGISTRY_ENTRIES,
} from "../pages/tools/skillRegistryCatalog";
import { computeSpecDigest, etagFromDigest } from "./specDigest";
import { SkillPublishError } from "./skillPublishErrors";
import {
  getEffectiveVersion,
  getPublishedRecord,
  listPublishedVersionsForSkill,
  loadSkillPublishStore,
  saveSkillPublishStore,
  upsertPublishedRecord,
  type PublishedSkillRecord,
  type SkillPublishStore,
} from "./skillPublishStore";
import { compareSkillSpecVersion, isSkillSpecVersionMonotonic } from "./versionCompare";

let memoryStore: SkillPublishStore | null = null;

function getStore(): SkillPublishStore {
  if (!memoryStore) memoryStore = loadSkillPublishStore();
  return memoryStore;
}

function commitStore(next: SkillPublishStore): void {
  memoryStore = next;
  saveSkillPublishStore(next);
}

export function reloadSkillPublishStoreFromDisk(): void {
  memoryStore = loadSkillPublishStore();
}

function requirePublishableSkill(skillId: string): {
  specPath: string;
  skillSpecVersion: string;
  bodyMarkdown: string;
} {
  const entry = getSkillRegistryEntry(skillId);
  if (!entry?.publishRequired || !entry.specPath) {
    throw new SkillPublishError(
      "SKILL_PUBLISH_GATE_FAILED",
      `${skillId} 非 publishRequired 或无 Git 正文`,
    );
  }
  if (resolveSkillContractStatus(skillId) !== "complete") {
    throw new SkillPublishError(
      "SKILL_PUBLISH_GATE_FAILED",
      `${skillId} 未 contract-complete，须先完善 §1～§6`,
    );
  }
  const bodyMarkdown = getSkillMarkdown(entry.specPath);
  if (!bodyMarkdown?.trim()) {
    throw new SkillPublishError("SKILL_PUBLISH_GATE_FAILED", `${skillId} 正文未加载`);
  }
  const skillSpecVersion = resolveSkillSpecVersion(skillId);
  if (!skillSpecVersion) {
    throw new SkillPublishError(
      "SKILL_PUBLISH_GATE_FAILED",
      `${skillId} 元数据缺少 skillSpecVersion`,
    );
  }
  return { specPath: entry.specPath, skillSpecVersion, bodyMarkdown };
}

export async function publishSkillOperationSpecLocal(
  skillId: string,
  request?: SkillSpecPublishRequest,
): Promise<SkillSpecPublishResult> {
  const { skillSpecVersion: gitVersion, bodyMarkdown: gitBody } = requirePublishableSkill(skillId);
  const skillSpecVersion = request?.skillSpecVersion?.trim() || gitVersion;
  if (skillSpecVersion !== gitVersion) {
    throw new SkillPublishError(
      "SKILL_PUBLISH_GATE_FAILED",
      `请求版本 ${skillSpecVersion} 与 Git 元数据 ${gitVersion} 不一致`,
    );
  }
  const bodyMarkdown = request?.bodyMarkdown?.trim() ? request.bodyMarkdown : gitBody;
  if (bodyMarkdown !== gitBody) {
    throw new SkillPublishError(
      "SKILL_PUBLISH_GATE_FAILED",
      "bodyMarkdown 与 Git 全文不一致（禁止控制台成为第二 SSOT）",
    );
  }

  const store = getStore();
  const existing = getPublishedRecord(store, skillId, skillSpecVersion);
  if (existing) {
    return {
      skillId,
      skillSpecVersion,
      lifecycle: "PUBLISHED",
      specDigest: existing.specDigest,
    };
  }

  const versions = listPublishedVersionsForSkill(store, skillId);
  let maxPublished: string | undefined;
  for (const v of versions) {
    if (!maxPublished || compareSkillSpecVersion(v.skillSpecVersion, maxPublished) > 0) {
      maxPublished = v.skillSpecVersion;
    }
  }
  if (!isSkillSpecVersionMonotonic(skillSpecVersion, maxPublished)) {
    throw new SkillPublishError(
      "SKILL_VERSION_NOT_MONOTONIC",
      `版本 ${skillSpecVersion} 不得低于已发布 ${maxPublished ?? "—"}`,
    );
  }

  const specDigest = request?.specDigest ?? (await computeSpecDigest(bodyMarkdown));
  const record: PublishedSkillRecord = {
    skillId,
    skillSpecVersion,
    lifecycle: "PUBLISHED",
    bodyMarkdown,
    specDigest,
    publishedAt: new Date().toISOString(),
    sourceGitRef: request?.sourceGitRef ?? null,
  };
  commitStore(upsertPublishedRecord(store, record));
  return {
    skillId,
    skillSpecVersion,
    lifecycle: "PUBLISHED",
    specDigest,
  };
}

/** 编排读路径 · 仅 PUBLISHED；未知版 → PROMPT_SKILL_REF_INVALID */
export function getEffectiveSkillOperationSpecLocal(
  skillId: string,
  skillSpecVersion: string,
): EffectiveSkillSpecResponse {
  const record = getPublishedRecord(getStore(), skillId, skillSpecVersion);
  if (!record || record.lifecycle !== "PUBLISHED") {
    throw new SkillPublishError(
      "PROMPT_SKILL_REF_INVALID",
      `${skillId}@${skillSpecVersion} 未发布或未知`,
      404,
    );
  }
  return {
    skillId: record.skillId,
    skillSpecVersion: record.skillSpecVersion,
    bodyMarkdown: record.bodyMarkdown,
    specDigest: record.specDigest,
    etag: etagFromDigest(record.specDigest, record.skillSpecVersion),
  };
}

export function getSkillOperationSpecSummaryLocal(skillId: string): SkillOperationSpecSummary {
  const entry = getSkillRegistryEntry(skillId);
  const store = getStore();
  const effectiveVersion = getEffectiveVersion(store, skillId);
  const gitVersion = resolveSkillSpecVersion(skillId);
  const skillSpecVersion = effectiveVersion ?? gitVersion ?? "—";
  const published = effectiveVersion
    ? getPublishedRecord(store, skillId, effectiveVersion)
    : undefined;
  return {
    skillId,
    skillSpecVersion,
    lifecycle: published ? "PUBLISHED" : "DRAFT",
    contractComplete: entry?.publishRequired
      ? resolveSkillContractStatus(skillId) === "complete"
      : undefined,
    specDigest: published?.specDigest,
    publishedAt: published?.publishedAt ?? null,
  };
}

export function listSkillOperationSpecsLocal(): SkillOperationSpecList {
  const items = SKILL_REGISTRY_ENTRIES.filter((e) => e.publishRequired).map((e) =>
    getSkillOperationSpecSummaryLocal(e.skillId),
  );
  return { items };
}

export function getSkillOperationSpecVersionBodyLocal(
  skillId: string,
  skillSpecVersion: string,
): SkillOperationSpecBody {
  const record = getPublishedRecord(getStore(), skillId, skillSpecVersion);
  if (record) {
    return {
      skillId,
      skillSpecVersion,
      bodyMarkdown: record.bodyMarkdown,
      specDigest: record.specDigest,
      sourceGitRef: record.sourceGitRef,
    };
  }
  const { bodyMarkdown } = requirePublishableSkill(skillId);
  const gitVersion = resolveSkillSpecVersion(skillId)!;
  if (skillSpecVersion !== gitVersion) {
    throw new SkillPublishError(
      "PROMPT_SKILL_REF_INVALID",
      `${skillId}@${skillSpecVersion} 未发布`,
      404,
    );
  }
  return {
    skillId,
    skillSpecVersion: gitVersion,
    bodyMarkdown,
    sourceGitRef: null,
  };
}

export function getSkillOperationSpecVersionsLocal(skillId: string): SkillSpecVersionHistory {
  const items = listPublishedVersionsForSkill(getStore(), skillId)
    .sort((a, b) => b.publishedAt.localeCompare(a.publishedAt))
    .map((r) => ({
      skillSpecVersion: r.skillSpecVersion,
      lifecycle: "PUBLISHED" as const,
      publishedAt: r.publishedAt,
    }));
  return { skillId, items };
}

/** 首次进入控制台：将 11 篇 contract-complete 技能发布到 Runtime（幂等） */
export async function seedAllPublishRequiredSkills(): Promise<number> {
  let n = 0;
  for (const e of SKILL_REGISTRY_ENTRIES) {
    if (!e.publishRequired || !e.specPath) continue;
    if (resolveSkillContractStatus(e.skillId) !== "complete") continue;
    const effective = getEffectiveVersion(getStore(), e.skillId);
    const gitVersion = resolveSkillSpecVersion(e.skillId);
    if (!gitVersion) continue;
    if (effective === gitVersion && getPublishedRecord(getStore(), e.skillId, gitVersion)) continue;
    await publishSkillOperationSpecLocal(e.skillId);
    n += 1;
  }
  return n;
}

export function countRuntimePublishedSkills(): { published: number; total: number } {
  const required = SKILL_REGISTRY_ENTRIES.filter((e) => e.publishRequired);
  const store = getStore();
  let published = 0;
  for (const e of required) {
    const v = getEffectiveVersion(store, e.skillId);
    if (v && getPublishedRecord(store, e.skillId, v)) published += 1;
  }
  return { published, total: required.length };
}
