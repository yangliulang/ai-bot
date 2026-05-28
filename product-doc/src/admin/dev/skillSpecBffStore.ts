/**
 * Dev BFF · 内存 Publish 库（种子来自 runtime-bundle.json）
 */

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { createHash } from "node:crypto";
import type {
  EffectiveSkillSpecResponse,
  SkillOperationSpecBody,
  SkillOperationSpecList,
  SkillOperationSpecSummary,
  SkillSpecPublishRequest,
  SkillSpecPublishResult,
  SkillSpecVersionHistory,
} from "../src/api/types/skillOperationSpec";
import { compareSkillSpecVersion, isSkillSpecVersionMonotonic } from "../src/skillPublish/versionCompare";

export type BffPublishedRecord = {
  skillId: string;
  skillSpecVersion: string;
  lifecycle: "PUBLISHED";
  bodyMarkdown: string;
  specDigest: string;
  publishedAt: string;
  sourceGitRef?: string | null;
};

export type BffStore = {
  effective: Record<string, string>;
  versions: Record<string, BffPublishedRecord>;
};

function versionKey(skillId: string, skillSpecVersion: string): string {
  return `${skillId}@${skillSpecVersion}`;
}

function digest(body: string): string {
  return createHash("sha256").update(body.replace(/\r\n/g, "\n"), "utf8").digest("hex");
}

function etag(specDigest: string, skillSpecVersion: string): string {
  return `"${specDigest.slice(0, 16)}-${skillSpecVersion}"`;
}

export class SkillPublishError extends Error {
  constructor(
    public code: "PROMPT_SKILL_REF_INVALID" | "SKILL_PUBLISH_GATE_FAILED" | "SKILL_VERSION_NOT_MONOTONIC",
    message: string,
    public status = 400,
  ) {
    super(message);
  }
}

export function loadBundleSeed(repoRoot: string): BffStore {
  const bundlePath = join(
    repoRoot,
    "specs/requirements/skill-specs/published/runtime-bundle.json",
  );
  if (!existsSync(bundlePath)) {
    throw new Error(`missing ${bundlePath} — run build_runtime_publish_bundle.mjs`);
  }
  const bundle = JSON.parse(readFileSync(bundlePath, "utf8")) as {
    items: Array<{
      skillId: string;
      skillSpecVersion: string;
      bodyMarkdown: string;
      specDigest?: string;
      sourceGitRef?: string | null;
    }>;
  };
  const store: BffStore = { effective: {}, versions: {} };
  const now = new Date().toISOString();
  for (const item of bundle.items) {
    const specDigest = item.specDigest ?? digest(item.bodyMarkdown);
    const record: BffPublishedRecord = {
      skillId: item.skillId,
      skillSpecVersion: item.skillSpecVersion,
      lifecycle: "PUBLISHED",
      bodyMarkdown: item.bodyMarkdown,
      specDigest,
      publishedAt: now,
      sourceGitRef: item.sourceGitRef ?? null,
    };
    const key = versionKey(item.skillId, item.skillSpecVersion);
    store.versions[key] = record;
    store.effective[item.skillId] = item.skillSpecVersion;
  }
  return store;
}

export function createSkillSpecBffStore(repoRoot: string): {
  store: BffStore;
  list(): SkillOperationSpecList;
  getSummary(skillId: string): SkillOperationSpecSummary;
  getVersions(skillId: string): SkillSpecVersionHistory;
  getVersionBody(skillId: string, skillSpecVersion: string): SkillOperationSpecBody;
  publish(skillId: string, req: SkillSpecPublishRequest): SkillSpecPublishResult;
  getEffective(skillId: string, skillSpecVersion: string): EffectiveSkillSpecResponse;
} {
  const store = loadBundleSeed(repoRoot);

  function getRecord(skillId: string, version: string): BffPublishedRecord | undefined {
    return store.versions[versionKey(skillId, version)];
  }

  function maxPublishedVersion(skillId: string): string | undefined {
    let max: string | undefined;
    for (const r of Object.values(store.versions)) {
      if (r.skillId !== skillId) continue;
      if (!max || compareSkillSpecVersion(r.skillSpecVersion, max) > 0) max = r.skillSpecVersion;
    }
    return max;
  }

  return {
    store,
    list(): SkillOperationSpecList {
      const ids = [...new Set(Object.keys(store.effective))];
      return { items: ids.map((id) => this.getSummary(id)) };
    },
    getSummary(skillId: string): SkillOperationSpecSummary {
      const effectiveVersion = store.effective[skillId];
      const published = effectiveVersion ? getRecord(skillId, effectiveVersion) : undefined;
      return {
        skillId,
        skillSpecVersion: effectiveVersion ?? "—",
        lifecycle: published ? "PUBLISHED" : "DRAFT",
        contractComplete: Boolean(published),
        specDigest: published?.specDigest,
        publishedAt: published?.publishedAt ?? null,
      };
    },
    getVersions(skillId: string): SkillSpecVersionHistory {
      const items = Object.values(store.versions)
        .filter((r) => r.skillId === skillId)
        .sort((a, b) => b.publishedAt.localeCompare(a.publishedAt))
        .map((r) => ({
          skillSpecVersion: r.skillSpecVersion,
          lifecycle: "PUBLISHED" as const,
          publishedAt: r.publishedAt,
        }));
      return { skillId, items };
    },
    getVersionBody(skillId: string, skillSpecVersion: string): SkillOperationSpecBody {
      const record = getRecord(skillId, skillSpecVersion);
      if (!record) {
        throw new SkillPublishError(
          "PROMPT_SKILL_REF_INVALID",
          `${skillId}@${skillSpecVersion} 未发布`,
          404,
        );
      }
      return {
        skillId,
        skillSpecVersion,
        bodyMarkdown: record.bodyMarkdown,
        specDigest: record.specDigest,
        sourceGitRef: record.sourceGitRef,
      };
    },
    publish(skillId: string, req: SkillSpecPublishRequest): SkillSpecPublishResult {
      const existing = getRecord(skillId, req.skillSpecVersion);
      if (existing) {
        return {
          skillId,
          skillSpecVersion: req.skillSpecVersion,
          lifecycle: "PUBLISHED",
          specDigest: existing.specDigest,
        };
      }
      const baseline = maxPublishedVersion(skillId);
      if (!isSkillSpecVersionMonotonic(req.skillSpecVersion, baseline)) {
        throw new SkillPublishError(
          "SKILL_VERSION_NOT_MONOTONIC",
          `版本 ${req.skillSpecVersion} 不得低于 ${baseline ?? "—"}`,
        );
      }
      if (!req.bodyMarkdown?.trim()) {
        throw new SkillPublishError("SKILL_PUBLISH_GATE_FAILED", "bodyMarkdown 必填（BFF 不从 Git 拉取）");
      }
      const specDigest = req.specDigest ?? digest(req.bodyMarkdown);
      const record: BffPublishedRecord = {
        skillId,
        skillSpecVersion: req.skillSpecVersion,
        lifecycle: "PUBLISHED",
        bodyMarkdown: req.bodyMarkdown,
        specDigest,
        publishedAt: new Date().toISOString(),
        sourceGitRef: req.sourceGitRef ?? null,
      };
      store.versions[versionKey(skillId, req.skillSpecVersion)] = record;
      store.effective[skillId] = req.skillSpecVersion;
      return {
        skillId,
        skillSpecVersion: req.skillSpecVersion,
        lifecycle: "PUBLISHED",
        specDigest,
      };
    },
    getEffective(skillId: string, skillSpecVersion: string): EffectiveSkillSpecResponse {
      const record = getRecord(skillId, skillSpecVersion);
      if (!record) {
        throw new SkillPublishError(
          "PROMPT_SKILL_REF_INVALID",
          `${skillId}@${skillSpecVersion} 未发布`,
          404,
        );
      }
      return {
        skillId,
        skillSpecVersion,
        bodyMarkdown: record.bodyMarkdown,
        specDigest: record.specDigest,
        etag: etag(record.specDigest, record.skillSpecVersion),
      };
    },
  };
}
