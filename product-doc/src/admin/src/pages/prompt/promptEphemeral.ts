import { buildPromptPackDraft } from "../../data/mock";
import type { MockPromptPack } from "../../data/types";
import type { EditorBootstrap } from "./promptEditorBootstrap";

const STORAGE_KEY_PREFIX = "admin.prompt.ephemeral:";

export const LOCAL_DRAFT_ID_PREFIX = "local-draft-";

export function isLocalDraftPromptPackId(id: string): boolean {
  return id.startsWith(LOCAL_DRAFT_ID_PREFIX);
}

export function persistEphemeralBootstrap(b: EditorBootstrap): void {
  try {
    sessionStorage.setItem(`${STORAGE_KEY_PREFIX}${b.pack.promptPackId}`, JSON.stringify(b));
  } catch {
    /* quota / private mode */
  }
}

export function loadEphemeralBootstrap(promptPackId: string): EditorBootstrap | null {
  try {
    const raw = sessionStorage.getItem(`${STORAGE_KEY_PREFIX}${promptPackId}`);
    if (!raw) return null;
    return JSON.parse(raw) as EditorBootstrap;
  } catch {
    return null;
  }
}

function newLocalDraftId(): string {
  return `${LOCAL_DRAFT_ID_PREFIX}${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

/** 空白本地草稿（演示：未调用服务端注册；刷新前位于 sessionStorage） */
export function createBlankEphemeralBootstrap(
  kind: MockPromptPack["kind"],
  title: string,
): EditorBootstrap {
  const id = newLocalDraftId();
  const pack: MockPromptPack = {
    promptPackId: id,
    kind,
    title: title.trim() || "未命名 Prompt 草稿",
    currentVersion: null,
    lockState: "DRAFT",
    hasDraft: true,
    updatedAt: new Date().toISOString(),
    description: "",
  };
  const draft = buildPromptPackDraft(pack);
  draft.promptPackId = id;
  draft.etag = '"local-draft"';
  draft.bodyMarkdown = `# ${pack.title}\n\n在此编写主提示词；支持占位符（如 {{symbol}}）。\n\n---\n（本地草稿：保存后写入浏览器会话）\n`;
  return {
    pack,
    draft,
    etag: draft.etag,
    versionHistory: [],
    remote: false,
  };
}

/** 从已加载的编辑态克隆新的本地草稿 id（不改变原包） */
export function cloneToEphemeralBootstrap(source: EditorBootstrap): EditorBootstrap {
  const id = newLocalDraftId();
  const pack: MockPromptPack = {
    ...source.pack,
    promptPackId: id,
    title: `${source.pack.title} · 草稿副本`,
    currentVersion: null,
    lockState: "DRAFT",
    hasDraft: true,
    publishedAt: undefined,
    deprecatedAt: undefined,
    deprecationNotice: undefined,
    publisher: undefined,
    contentHashShort: undefined,
  };
  const fs = source.draft.fewShots.map((row, i) => ({
    ...row,
    id: `${id}-fs-${i}-${row.id}`.slice(0, 64),
  }));
  const draft = {
    ...source.draft,
    promptPackId: id,
    etag: '"local-draft"',
    fewShots: fs,
  };
  return {
    pack,
    draft,
    etag: draft.etag,
    versionHistory: [],
    remote: false,
  };
}
