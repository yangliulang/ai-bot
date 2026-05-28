/**
 * 治理 SSOT · 16 运营包 id（与 mockPromptData / product/prompt-governance-checklist 同窗）
 */

import { mockPromptPacks } from "./mockPromptData";

export const GOVERNANCE_PROMPT_PACK_COUNT = 16 as const;

export const GOVERNANCE_PROMPT_PACK_IDS = mockPromptPacks.map(
  (p) => p.promptPackId,
) as readonly string[];

export function isGovernancePromptPackId(id: string): boolean {
  return GOVERNANCE_PROMPT_PACK_IDS.includes(id);
}
