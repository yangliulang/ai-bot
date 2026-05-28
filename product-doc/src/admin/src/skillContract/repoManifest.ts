import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

export type ManifestEntry = {
  skillId: string;
  path: string | null;
  publishRequired: boolean;
};

const REPO_ROOT = join(import.meta.dirname, "../../../..");
const SKILL_ROOT = join(REPO_ROOT, "specs/requirements/skill-specs");
const MANIFEST = join(SKILL_ROOT, "manifest.yaml");

const REQUIRED_SECTIONS = [
  "## 1. Required / Optional Params",
  "## 2. Validation Rules",
  "## 3. Confirmation Schema",
  "## 4. UNKNOWN / 缺槽策略",
  "## 5. Refusal Conditions",
  "## 6. API / 写路径",
];

/** 轻量解析 manifest.yaml（避免 Vitest 依赖 PyYAML） */
export function loadManifestEntries(): ManifestEntry[] {
  const text = readFileSync(MANIFEST, "utf-8");
  const entries: ManifestEntry[] = [];
  let current: Partial<ManifestEntry> = {};

  for (const line of text.split("\n")) {
    const id = line.match(/^\s+skillId:\s+(\S+)\s*$/);
    if (id) {
      if (current.skillId) entries.push(current as ManifestEntry);
      current = { skillId: id[1] };
      continue;
    }
    const path = line.match(/^\s+path:\s+(\S+)\s*$/);
    if (path) {
      current.path = path[1] === "null" ? null : path[1];
      continue;
    }
    const pub = line.match(/^\s+publishRequired:\s+(true|false)\s*$/);
    if (pub) current.publishRequired = pub[1] === "true";
  }
  if (current.skillId) entries.push(current as ManifestEntry);
  return entries;
}

export function assertPublishRequiredContractFiles(): string[] {
  const errors: string[] = [];
  for (const e of loadManifestEntries()) {
    if (!e.publishRequired) continue;
    if (!e.path) {
      errors.push(`${e.skillId}: publishRequired but path null`);
      continue;
    }
    const full = join(SKILL_ROOT, e.path);
    if (!existsSync(full)) {
      errors.push(`${e.skillId}: missing ${e.path}`);
      continue;
    }
    const body = readFileSync(full, "utf-8");
    for (const sec of REQUIRED_SECTIONS) {
      if (!body.includes(sec)) errors.push(`${e.skillId}: missing ${sec}`);
    }
    if (!body.includes("contract-complete")) {
      errors.push(`${e.skillId}: missing contract-complete status`);
    }
  }
  return errors;
}
