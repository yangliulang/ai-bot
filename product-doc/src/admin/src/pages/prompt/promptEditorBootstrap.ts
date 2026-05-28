import type { MockPromptPack, MockPromptPackDraft, MockPromptPackVersionHistoryRow } from "../../data/types";

/** 编辑器首屏载荷（演示 / API 对齐） */
export interface EditorBootstrap {
  pack: MockPromptPack;
  draft: MockPromptPackDraft;
  etag: string;
  versionHistory: MockPromptPackVersionHistoryRow[];
  remote: boolean;
}
