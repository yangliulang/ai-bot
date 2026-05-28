import {
  getSkillMarkdown,
  getSkillRegistryEntry,
  SKILL_REGISTRY_ENTRIES,
} from "./skillRegistryCatalog";
import {
  operationBrief,
  parseSkillOperationView,
  type SkillOperationView,
} from "./parseSkillOperationView";

const cache = new Map<string, SkillOperationView | null>();

function loadView(skillId: string): SkillOperationView | null {
  const entry = getSkillRegistryEntry(skillId);
  if (!entry?.specPath) return null;
  const body = getSkillMarkdown(entry.specPath);
  if (!body) return null;
  return parseSkillOperationView(body);
}

export function warmSkillOperationCache(force = false): void {
  if (force) cache.clear();
  for (const e of SKILL_REGISTRY_ENTRIES) {
    if (force || !cache.has(e.skillId)) {
      cache.set(e.skillId, e.specPath ? loadView(e.skillId) : null);
    }
  }
}

export function getCachedSkillOperationView(
  skillId: string,
): SkillOperationView | null {
  if (!cache.has(skillId)) {
    cache.set(skillId, loadView(skillId));
  }
  return cache.get(skillId) ?? null;
}

export function resolveOperationBriefCached(skillId: string): string {
  const view = getCachedSkillOperationView(skillId);
  if (view) return operationBrief(view);
  return getSkillRegistryEntry(skillId)?.specNote ?? "—";
}

warmSkillOperationCache();
