/** 比较 `skillSpecVersion`（如 `0.2.0-contract`）是否严格大于已发布版本 */

const VERSION_RE = /^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9._-]+))?$/;

export type ParsedSkillSpecVersion = {
  major: number;
  minor: number;
  patch: number;
  suffix: string;
};

export function parseSkillSpecVersion(v: string): ParsedSkillSpecVersion | null {
  const m = v.trim().match(VERSION_RE);
  if (!m) return null;
  return {
    major: Number(m[1]),
    minor: Number(m[2]),
    patch: Number(m[3]),
    suffix: m[4] ?? "",
  };
}

export function compareSkillSpecVersion(a: string, b: string): number {
  const pa = parseSkillSpecVersion(a);
  const pb = parseSkillSpecVersion(b);
  if (!pa || !pb) return a.localeCompare(b);
  if (pa.major !== pb.major) return pa.major - pb.major;
  if (pa.minor !== pb.minor) return pa.minor - pb.minor;
  if (pa.patch !== pb.patch) return pa.patch - pb.patch;
  return pa.suffix.localeCompare(pb.suffix);
}

/** `candidate` 须严格大于 `baseline`（同窗单调 Publish） */
export function isSkillSpecVersionMonotonic(candidate: string, baseline: string | undefined): boolean {
  if (!baseline) return true;
  return compareSkillSpecVersion(candidate, baseline) > 0;
}
