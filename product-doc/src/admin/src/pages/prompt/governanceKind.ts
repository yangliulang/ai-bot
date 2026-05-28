import type { MockPromptPack } from "../../data/types";
import { PROMPT_GOVERNANCE_LIST_KINDS } from "./promptPackKinds";

export type GovernanceKindFilter = "all" | Exclude<MockPromptPack["kind"], "SAFETY">;

/** 地址栏 kind= 与下拉同步；护栏 SAFETY 不在本页筛选 */
export function parseGovernanceKind(raw: string | null | undefined): GovernanceKindFilter {
  const u = (raw ?? "").toUpperCase();
  if ((PROMPT_GOVERNANCE_LIST_KINDS as readonly string[]).includes(u)) return u as GovernanceKindFilter;
  return "all";
}
