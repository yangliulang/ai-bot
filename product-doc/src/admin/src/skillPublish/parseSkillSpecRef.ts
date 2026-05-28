import { resolveSkillSpecVersion } from "../pages/tools/skillRegistryCatalog";
import { resolveSkillIdForScenario } from "./scenarioSkillMap";

const SKILL_ID_RE = /^skill\.[a-z0-9_.]+$/;

export type ParsedSkillSpecRef = {
  skillId: string;
  skillSpecVersion: string;
  source: "explicit" | "scenario" | "legacy";
};

function parseExplicitRef(raw: string): { skillId: string; skillSpecVersion: string } | null {
  const t = raw.trim();
  if (!t) return null;
  try {
    const j = JSON.parse(t) as { skillId?: string; skillSpecVersion?: string };
    if (j.skillId && j.skillSpecVersion && SKILL_ID_RE.test(j.skillId)) {
      return { skillId: j.skillId, skillSpecVersion: String(j.skillSpecVersion) };
    }
  } catch {
    /* not JSON */
  }
  const at = t.match(/^(skill\.[a-z0-9_.]+)@([^\s]+)$/);
  if (at) return { skillId: at[1]!, skillSpecVersion: at[2]! };
  const colon = t.match(/^(skill\.[a-z0-9_.]+):([^\s]+)$/);
  if (colon) return { skillId: colon[1]!, skillSpecVersion: colon[2]! };
  if (SKILL_ID_RE.test(t)) {
    const ver = resolveSkillSpecVersion(t);
    if (ver) return { skillId: t, skillSpecVersion: ver };
  }
  return null;
}

/**
 * 解析 `skillSpecRef` + 可选 `scenarioId` 回退（含 legacy `trade-assistant@…`）
 */
export function parseSkillSpecRef(
  skillSpecRef: string | undefined,
  scenarioId: string | undefined,
): ParsedSkillSpecRef | null {
  const ref = skillSpecRef?.trim() ?? "";
  const scenario = scenarioId?.trim() ?? "";

  const explicit = ref ? parseExplicitRef(ref) : null;
  if (explicit) {
    return { ...explicit, source: "explicit" };
  }

  if (ref.startsWith("trade-assistant@") && scenario) {
    const skillId = resolveSkillIdForScenario(scenario);
    const ver = skillId ? resolveSkillSpecVersion(skillId) : undefined;
    if (skillId && ver) {
      return { skillId, skillSpecVersion: ver, source: "legacy" };
    }
  }

  if (scenario) {
    const skillId = resolveSkillIdForScenario(scenario);
    const ver = skillId ? resolveSkillSpecVersion(skillId) : undefined;
    if (skillId && ver) {
      return { skillId, skillSpecVersion: ver, source: "scenario" };
    }
  }

  return null;
}

export function formatSkillSpecRef(parsed: ParsedSkillSpecRef): string {
  return `${parsed.skillId}@${parsed.skillSpecVersion}`;
}
