import type { MockPromptPack } from "../../data/types";

/** 与 OpenAPI `PromptPackType`、需求域同窗；顺序：系统→交易→分析→安全防护 */
export const PROMPT_PACK_KINDS_ORDERED = ["SYSTEM", "TRADING", "ANALYSIS", "SAFETY"] as const satisfies readonly MockPromptPack["kind"][];

/** 「提示词治理」列表：筛选与空白草稿（不含 SAFETY，护栏见 `/prompts/safety`） */
export const PROMPT_GOVERNANCE_LIST_KINDS = PROMPT_PACK_KINDS_ORDERED.filter(
  (k): k is Exclude<MockPromptPack["kind"], "SAFETY"> => k !== "SAFETY",
);

/** 判断是否合法包类型（接口或查询参数容错） */
export function isPromptPackKind(v: string): v is MockPromptPack["kind"] {
  return (PROMPT_PACK_KINDS_ORDERED as readonly string[]).includes(v);
}
