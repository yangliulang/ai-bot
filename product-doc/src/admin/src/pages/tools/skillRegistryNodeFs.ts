/**
 * Vitest / Node 回退：当 import.meta.glob 未嵌入仓库外路径时使用。
 * 勿在浏览器入口静态 import 本文件。
 */
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SKILL_ROOT = join(
  dirname(fileURLToPath(import.meta.url)),
  "../../../../..",
  "specs/requirements/skill-specs",
);

export function getSkillMarkdownFromDisk(relPath: string): string | undefined {
  const full = join(SKILL_ROOT, relPath);
  if (!existsSync(full)) return undefined;
  return readFileSync(full, "utf-8");
}
