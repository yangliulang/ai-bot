/**
 * Vite 嵌入 skill-specs Markdown（@skill-specs 别名 → 仓库 specs/requirements/skill-specs）。
 */

const RAW_RELATIVE = import.meta.glob("../../specs/requirements/skill-specs/**/skill.*.md", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

const RAW_ALIAS = import.meta.glob("@skill-specs/**/skill.*.md", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

const RAW_MARKDOWN = { ...RAW_RELATIVE, ...RAW_ALIAS };

/** 构建期嵌入的 skill 正文篇数 */
export const SKILL_MARKDOWN_BUNDLE_COUNT = Object.keys(RAW_MARKDOWN).length;

export function getSkillMarkdownFromBundle(relPath: string): string | undefined {
  const suffix = `/${relPath.replace(/^\//, "")}`;
  const key = Object.keys(RAW_MARKDOWN).find((k) => k.endsWith(suffix));
  return key ? RAW_MARKDOWN[key] : undefined;
}
