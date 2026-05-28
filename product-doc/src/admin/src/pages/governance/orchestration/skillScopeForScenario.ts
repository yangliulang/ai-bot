/**
 * 按 scenarioId 解析 Runtime 可用 Skill 范围（只读 · Demo）
 * 对齐 SCENARIO_PRIMARY_SKILL · 技能登记册 · Prompt 场景策略槽（非 Prompt 正文）
 */

import { getPromptPack, mockPromptPacks } from "../../../data/mock";
import { buildDefaultResolvedPromptBinding } from "../../../productionRuntime/promptBindingTimeline";
import { isWriteScenario, resolveSkillIdForScenario } from "../../../skillPublish/scenarioSkillMap";
import {
  getSkillRegistryEntry,
  resolveSkillContractStatus,
  resolveSkillSpecVersion,
  SKILL_REGISTRY_ENTRIES,
  type SkillRegistryEntry,
} from "../../tools/skillRegistryCatalog";
import { loadToolRegistryState } from "../../tools/toolRegistryStorage";
import type { ScenarioCategory } from "./scenarioRegistryMock";

export type ScenarioSkillScopeEntry = {
  skillId: string;
  skillSpecVersion: string | null;
  summary: string;
  contractStatus: "complete" | "missing" | "n/a";
  demoEnabled: boolean;
  matrixStatus: string;
  role: "primary_write" | "registry";
};

export type ScenarioSkillScopeView = {
  scenarioId: string;
  category: ScenarioCategory;
  mode: "write_skill" | "read_only" | "unmapped_write";
  skills: ScenarioSkillScopeEntry[];
  promptStrategyPackId: string | null;
  promptStrategyVersion: number | null;
  promptSkillScopeRef: string | null;
  narrative: string;
};

function resolveDemoEnabled(entry: SkillRegistryEntry): boolean {
  const store = loadToolRegistryState(
    SKILL_REGISTRY_ENTRIES.map((e) => e.skillId),
    Object.fromEntries(SKILL_REGISTRY_ENTRIES.map((e) => [e.skillId, e.defaultEnabled])),
  );
  return store.enabled[entry.skillId] ?? entry.defaultEnabled;
}

function entryFromRegistry(skillId: string, role: ScenarioSkillScopeEntry["role"]): ScenarioSkillScopeEntry | null {
  const reg = getSkillRegistryEntry(skillId);
  if (!reg) return null;
  return {
    skillId,
    skillSpecVersion: resolveSkillSpecVersion(skillId) ?? null,
    summary: reg.summary,
    contractStatus: resolveSkillContractStatus(skillId),
    demoEnabled: resolveDemoEnabled(reg),
    matrixStatus: reg.matrixStatus,
    role,
  };
}

function resolvePromptStrategy(scenarioId: string): {
  packId: string | null;
  version: number | null;
  skillScopeRef: string | null;
} {
  const published = mockPromptPacks.find(
    (p) => p.scenarioId === scenarioId && p.lockState !== "DRAFT" && p.currentVersion != null,
  );
  if (published) {
    const skillId = resolveSkillIdForScenario(scenarioId);
    const ver = skillId ? resolveSkillSpecVersion(skillId) : undefined;
    const inferredRef = skillId && ver ? `${skillId}@${ver}` : null;
    return {
      packId: published.promptPackId,
      version: published.currentVersion ?? null,
      skillScopeRef: published.skillSpecRef?.trim() || inferredRef,
    };
  }

  try {
    const binding = buildDefaultResolvedPromptBinding({ scenarioId });
    if (!binding.tradingPromptPackId) {
      return { packId: null, version: null, skillScopeRef: null };
    }
    const pack = getPromptPack(binding.tradingPromptPackId);
    const skillId = resolveSkillIdForScenario(scenarioId);
    const ver = skillId ? resolveSkillSpecVersion(skillId) : undefined;
    return {
      packId: binding.tradingPromptPackId,
      version: binding.tradingPromptPackVersion ?? pack?.currentVersion ?? null,
      skillScopeRef: pack?.skillSpecRef?.trim() || (skillId && ver ? `${skillId}@${ver}` : null),
    };
  } catch {
    return { packId: null, version: null, skillScopeRef: null };
  }
}

const READ_NARRATIVE: Record<ScenarioCategory, string> = {
  read: "读侧场景：Runtime 走 B/C 类 Tool 链（行情、持仓、检索等），无单一 A 类 write Skill；写路径须切换至交易类 scenarioId。",
  write: "",
  wealth: "理财场景：若已映射 skillId，写路径读 skill 规范；否则见登记册与矩阵 PATH。",
  monitoring: "监控/自动化：通常无用户写 Skill；Prompt UX 与观测告警同窗配置。",
};

export function resolveScenarioSkillScope(
  scenarioId: string,
  category: ScenarioCategory,
): ScenarioSkillScopeView {
  const prompt = resolvePromptStrategy(scenarioId);
  const primaryId = resolveSkillIdForScenario(scenarioId);

  if (category === "read" || (!primaryId && category !== "write" && category !== "wealth")) {
    return {
      scenarioId,
      category,
      mode: "read_only",
      skills: [],
      promptStrategyPackId: prompt.packId,
      promptStrategyVersion: prompt.version,
      promptSkillScopeRef: prompt.skillScopeRef,
      narrative: READ_NARRATIVE[category] ?? READ_NARRATIVE.read,
    };
  }

  if (!primaryId) {
    return {
      scenarioId,
      category,
      mode: "unmapped_write",
      skills: [],
      promptStrategyPackId: prompt.packId,
      promptStrategyVersion: prompt.version,
      promptSkillScopeRef: prompt.skillScopeRef,
      narrative:
        "写路径场景键尚未在 SCENARIO_PRIMARY_SKILL 登记主 Skill；须在 routing-engine 与 skill-specs/manifest 同窗补齐后再开放对话写操作。",
    };
  }

  const primary = entryFromRegistry(primaryId, "primary_write");
  const skills = primary ? [primary] : [];

  return {
    scenarioId,
    category,
    mode: "write_skill",
    skills,
    promptStrategyPackId: prompt.packId,
    promptStrategyVersion: prompt.version,
    promptSkillScopeRef: prompt.skillScopeRef,
    narrative: isWriteScenario(scenarioId)
      ? "写路径：Runtime 在类型 A 前 read_skill_operation_spec；Skill 正文在登记册，Prompt 仅承载场景叙事与发布门禁指针。"
      : "—",
  };
}
