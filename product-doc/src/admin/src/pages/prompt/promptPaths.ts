import type { MockPromptPack } from "../../data/types";
import { isLocalDraftPromptPackId } from "./promptEphemeral";

/** 返回列表页并打开同 Prompt 抽屉（或护栏页） */
export function promptPackListHref(p: Pick<MockPromptPack, "kind" | "promptPackId">): string {
  if (isLocalDraftPromptPackId(p.promptPackId)) {
    return p.kind === "SAFETY" ? "/prompts/safety" : "/prompts/strategy";
  }
  const id = encodeURIComponent(p.promptPackId);
  if (p.kind === "SAFETY") {
    return `/prompts/safety?panel=strategy&pack=${id}`;
  }
  return `/prompts/strategy?pack=${id}`;
}

export function promptPackEditorPath(promptPackId: string): string {
  return `/prompts/editor/${encodeURIComponent(promptPackId)}`;
}

/** 全页详情（与抽屉共用内容） */
export function promptPackViewPath(promptPackId: string): string {
  return `/prompts/view/${encodeURIComponent(promptPackId)}`;
}
