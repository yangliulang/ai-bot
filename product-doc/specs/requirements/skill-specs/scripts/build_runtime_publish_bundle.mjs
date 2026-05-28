#!/usr/bin/env node
/**
 * 构建 Runtime Publish 快照 bundle（Git §1～§6 全文 + skillSpecVersion + digest）
 * 用途：MR-B / prompt-management 落库对账；CI 门禁
 *
 *   node specs/requirements/skill-specs/scripts/build_runtime_publish_bundle.mjs
 *   node specs/requirements/skill-specs/scripts/build_runtime_publish_bundle.mjs --check
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, "../../../..");
const SKILL_ROOT = join(REPO_ROOT, "specs/requirements/skill-specs");
const MANIFEST = join(SKILL_ROOT, "manifest.yaml");
const OUT = join(SKILL_ROOT, "published/runtime-bundle.json");
const REQUIRED_SECTIONS = [
  "## 1.",
  "## 2.",
  "## 3.",
  "## 4.",
  "## 5.",
  "## 6.",
];

function normalizeBody(body) {
  return body.replace(/\r\n/g, "\n");
}

function digest(body) {
  return createHash("sha256").update(normalizeBody(body), "utf8").digest("hex");
}

function parseVersion(body) {
  const m = body.match(/\|\s*\*\*`skillSpecVersion`\*\*\s*\|\s*`([^`]+)`\s*\|/);
  return m?.[1]?.trim() ?? null;
}

function loadManifest() {
  const raw = readFileSync(MANIFEST, "utf8");
  const skills = [];
  let cur = {};
  for (const line of raw.split("\n")) {
    const id = line.match(/^\s+-?\s*skillId:\s+(\S+)\s*$/);
    if (id) {
      if (cur.skillId) skills.push(cur);
      cur = { skillId: id[1] };
      continue;
    }
    const path = line.match(/^\s+-?\s*path:\s+(\S+)\s*$/);
    if (path) cur.path = path[1] === "null" ? null : path[1];
    const req = line.match(/^\s+-?\s*publishRequired:\s+(true|false)\s*$/);
    if (req) cur.publishRequired = req[1] === "true";
  }
  if (cur.skillId) skills.push(cur);
  return skills.filter((s) => s.publishRequired && s.path);
}

function buildBundle() {
  const skills = loadManifest();
  const items = [];
  const errors = [];

  for (const s of skills) {
    const abs = join(SKILL_ROOT, s.path);
    if (!existsSync(abs)) {
      errors.push(`${s.skillId}: missing ${s.path}`);
      continue;
    }
    const bodyMarkdown = readFileSync(abs, "utf8");
    if (!bodyMarkdown.includes("contract-complete")) {
      errors.push(`${s.skillId}: missing contract-complete`);
    }
    for (const sec of REQUIRED_SECTIONS) {
      if (!bodyMarkdown.includes(sec)) errors.push(`${s.skillId}: missing ${sec}`);
    }
    const skillSpecVersion = parseVersion(bodyMarkdown);
    if (!skillSpecVersion) errors.push(`${s.skillId}: missing skillSpecVersion metadata`);
    items.push({
      skillId: s.skillId,
      skillSpecVersion,
      lifecycle: "PUBLISHED",
      bodyMarkdown: normalizeBody(bodyMarkdown),
      specDigest: digest(bodyMarkdown),
      sourceGitRef: process.env.GITHUB_SHA ?? null,
    });
  }

  if (errors.length) {
    console.error(errors.join("\n"));
    process.exit(1);
  }

  return {
    bundleVersion: "1.0.0",
    generatedAt: new Date().toISOString(),
    gitRoot: "specs/requirements/skill-specs",
    itemCount: items.length,
    items,
  };
}

const checkOnly = process.argv.includes("--check");

const bundle = buildBundle();
const json = `${JSON.stringify(bundle, null, 2)}\n`;

function fingerprint(b) {
  return b.items
    .map((i) => `${i.skillId}\t${i.skillSpecVersion}\t${i.specDigest}\t${i.bodyMarkdown.length}`)
    .sort()
    .join("\n");
}

if (checkOnly) {
  if (!existsSync(OUT)) {
    console.error(`missing ${OUT} — run without --check to generate`);
    process.exit(1);
  }
  const onDisk = JSON.parse(readFileSync(OUT, "utf8"));
  if (onDisk.itemCount !== bundle.itemCount || fingerprint(onDisk) !== fingerprint(bundle)) {
    console.error("runtime-bundle.json is stale — regenerate with build_runtime_publish_bundle.mjs");
    process.exit(1);
  }
  console.log(`OK · ${bundle.itemCount} skills · ${OUT}`);
  process.exit(0);
}

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, json);
console.log(`Wrote ${bundle.itemCount} skills → ${OUT}`);
