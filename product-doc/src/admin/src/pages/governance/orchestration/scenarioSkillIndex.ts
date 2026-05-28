/**
 * scenarioId ↔ skillId 反向索引（Demo · 与 scenarioSkillMap 同窗）
 */

import { SCENARIO_PRIMARY_SKILL } from "../../../skillPublish/scenarioSkillMap";

const SKILL_TO_SCENARIOS = (() => {
  const map = new Map<string, string[]>();
  for (const [scenarioId, skillId] of Object.entries(SCENARIO_PRIMARY_SKILL)) {
    const list = map.get(skillId) ?? [];
    list.push(scenarioId);
    map.set(skillId, list);
  }
  for (const [, ids] of map) {
    ids.sort((a, b) => a.localeCompare(b));
  }
  return map;
})();

export function listScenariosForSkill(skillId: string): string[] {
  return SKILL_TO_SCENARIOS.get(skillId.trim()) ?? [];
}

export function countScenariosForSkill(skillId: string): number {
  return listScenariosForSkill(skillId).length;
}
