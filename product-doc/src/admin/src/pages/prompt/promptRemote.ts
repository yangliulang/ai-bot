import type { MockFewShotRow, MockPromptPack, MockPromptPackDraft, MockPromptPackVersionHistoryRow } from "../../data/types";
import {
  buildPromptPackDraft,
  getPromptAuditTail,
  getPromptPack,
  getPromptPackDraft,
  getPromptPackVersionHistory,
  mockPromptPacks,
} from "../../data/mock";
import { ApiError, isPromptApiEnabled } from "../../api/http";
import * as pm from "../../api/promptManagementClient";
import type { PromptPackDetail, PromptPackSummary, PromptVersionEntry } from "../../api/types/promptManagement";
import type { EditorBootstrap } from "./promptEditorBootstrap";
import { isLocalDraftPromptPackId, loadEphemeralBootstrap } from "./promptEphemeral";
import { isPromptPackKind } from "./promptPackKinds";
import { mergeRemotePacksWithGovernanceMock } from "./mergeGovernancePromptPacks";

export type { EditorBootstrap } from "./promptEditorBootstrap";

/** `remote+mock-ssot`：BFF 已通但列表未齐 16 包 · 以 mock 补齐治理 SSOT */
export type PromptDataSource = "mock" | "remote" | "remote+mock-ssot" | "remote+fallback";

function parseVersion(v: unknown): number | null {
  if (v == null || v === "") return null;
  const n = parseInt(String(v), 10);
  return Number.isFinite(n) ? n : null;
}

/** OpenAPI 摘要 → 控制台表格行（与 MockPromptPack 同桌） */
export function adaptPromptSummary(s: PromptPackSummary): MockPromptPack {
  const id = String(s.promptPackId ?? "");
  const pt = String(s.promptPackType ?? "SYSTEM");
  const kind: MockPromptPack["kind"] = isPromptPackKind(pt) ? pt : "ANALYSIS";
  const lifecycle = String(s.lifecycle ?? "DRAFT");
  const lockState =
    lifecycle === "DRAFT" || lifecycle === "PUBLISHED" || lifecycle === "LOCKED" ? lifecycle : "DRAFT";
  const row: MockPromptPack = {
    promptPackId: id,
    kind,
    title: s.title != null ? String(s.title) : id,
    currentVersion: parseVersion(s.promptPackVersion),
    lockState,
    scenarioId: s.scenarioId != null ? String(s.scenarioId) : undefined,
    description: s.description != null ? String(s.description) : undefined,
    updatedAt: s.updatedAt != null ? String(s.updatedAt) : undefined,
    publishedAt: s.publishedAt != null ? String(s.publishedAt) : undefined,
    hasDraft: s.hasDraft === true || lifecycle === "DRAFT",
    skillSpecRef: s.skillSpecRef != null ? String(s.skillSpecRef) : undefined,
    publisher: s.publisher != null ? String(s.publisher) : undefined,
    contentHashShort: s.etag != null ? String(s.etag) : undefined,
    placeholderDenylistRevision: s.placeholderDenylistRevision != null ? String(s.placeholderDenylistRevision) : undefined,
    safetyPhraseBlocklistRevision: s.safetyPhraseBlocklistRevision != null ? String(s.safetyPhraseBlocklistRevision) : undefined,
  };
  return row;
}

function mergeMockWithDetail(base: MockPromptPack | undefined, d: PromptPackDetail): MockPromptPack {
  const lifecycle = String(d.lifecycle ?? base?.lockState ?? "DRAFT");
  const lockState =
    lifecycle === "DRAFT" || lifecycle === "PUBLISHED" || lifecycle === "LOCKED"
      ? lifecycle
      : base?.lockState ?? "DRAFT";
  const pt = String(d.promptPackType ?? base?.kind ?? "SYSTEM");
  const kind: MockPromptPack["kind"] = isPromptPackKind(pt) ? pt : "SYSTEM";
  return {
    ...base,
    promptPackId: String(d.promptPackId),
    kind,
    scenarioId: d.scenarioId != null ? String(d.scenarioId) : base?.scenarioId,
    currentVersion: parseVersion(d.promptPackVersion) ?? base?.currentVersion ?? null,
    lockState,
    title: d.title != null ? String(d.title) : base?.title ?? d.promptPackId,
    description: d.description != null ? String(d.description) : base?.description,
    contentHashShort: d.etag != null ? String(d.etag) : base?.contentHashShort,
    placeholderDenylistRevision:
      d.placeholderDenylistRevision != null ? String(d.placeholderDenylistRevision) : base?.placeholderDenylistRevision,
    safetyPhraseBlocklistRevision:
      d.safetyPhraseBlocklistRevision != null ? String(d.safetyPhraseBlocklistRevision) : base?.safetyPhraseBlocklistRevision,
    effectiveBodyPreview:
      d.body != null
        ? String(d.body)
        : d.bodyMarkdown != null
          ? String(d.bodyMarkdown)
          : base?.effectiveBodyPreview,
    skillSpecRef: d.skillSpecRef != null ? String(d.skillSpecRef) : base?.skillSpecRef,
  };
}


export async function loadAllPromptPacks(): Promise<{
  rows: MockPromptPack[];
  source: PromptDataSource;
  error?: string;
  supplementedFromMock?: string[];
}> {
  if (!isPromptApiEnabled()) {
    return { rows: mockPromptPacks, source: "mock" };
  }
  try {
    const list = await pm.listPromptPacks({});
    const remoteRows = (list.items ?? []).map(adaptPromptSummary);
    const { rows, supplementedFromMock } = mergeRemotePacksWithGovernanceMock(remoteRows, mockPromptPacks);
    const source: PromptDataSource =
      supplementedFromMock.length > 0 ? "remote+mock-ssot" : "remote";
    return { rows, source, supplementedFromMock };
  } catch (err: unknown) {
    const msg =
      err instanceof ApiError
        ? `${err.status} ${err.message}`
        : err instanceof Error
          ? err.message
          : String(err);
    return { rows: mockPromptPacks, source: "remote+fallback", error: msg };
  }
}

export async function loadPackForDrawer(promptPackId: string): Promise<MockPromptPack | undefined> {
  const local = getPromptPack(promptPackId);
  if (!isPromptApiEnabled()) return local;
  try {
    const d = await pm.getPromptPackRemote(promptPackId);
    return mergeMockWithDetail(local, d);
  } catch {
    return local;
  }
}

function mapFewShotApiToRow(x: { fewShotId: string; role?: string; content?: string }): MockFewShotRow {
  const r = (x.role ?? "user") as MockFewShotRow["role"];
  return {
    id: x.fewShotId,
    role: r === "system" || r === "assistant" ? r : "user",
    content: x.content ?? "",
  };
}

function mapVersionEntry(e: PromptVersionEntry): MockPromptPackVersionHistoryRow {
  const ver = parseVersion(e.promptPackVersion) ?? 0;
  const ev = String(e.event ?? "").toUpperCase();
  const event: MockPromptPackVersionHistoryRow["event"] =
    ev === "ROLLBACK" || ev === "RB" ? "ROLLBACK" : "PUBLISH";
  return {
    promptPackVersion: ver,
    publishedAt: e.publishedAt ?? "",
    actor: e.actor != null ? String(e.actor) : "—",
    event,
    summary: e.summary != null ? String(e.summary) : String(e.lifecycle ?? ""),
  };
}

export async function loadEditorBootstrap(promptPackId: string): Promise<EditorBootstrap> {
  const localPack = getPromptPack(promptPackId);
  const localVersions = getPromptPackVersionHistory(promptPackId);

  if (!isPromptApiEnabled()) {
    if (!localPack) throw new Error("unknown prompt pack");
    const localDraft = getPromptPackDraft(promptPackId);
    if (!localDraft) throw new Error("unknown prompt pack");
    return {
      pack: localPack,
      draft: localDraft,
      etag: localDraft.etag,
      versionHistory: localVersions,
      remote: false,
    };
  }

  try {
    const [detail, versions, fewList] = await Promise.all([
      pm.getPromptPackRemote(promptPackId),
      pm.getPromptPackVersions(promptPackId),
      pm.listPromptPackFewShots(promptPackId).catch(() => ({ items: [] as { fewShotId: string; role?: string; content?: string }[] })),
    ]);
    const pack = mergeMockWithDetail(localPack, detail);
    const baseDraft = localPack
      ? getPromptPackDraft(promptPackId) ?? buildPromptPackDraft(pack)
      : buildPromptPackDraft(pack);
    const apiFs = (fewList.items ?? []).map(mapFewShotApiToRow);
    const draft: MockPromptPackDraft = {
      ...baseDraft,
      etag: detail.etag != null ? String(detail.etag) : baseDraft.etag,
      bodyMarkdown:
        detail.body != null
          ? String(detail.body)
          : detail.bodyMarkdown != null
            ? String(detail.bodyMarkdown)
            : baseDraft.bodyMarkdown,
      fewShots: apiFs.length > 0 ? apiFs : baseDraft.fewShots,
      variableSchemaJson:
        detail.variableSchema != null
          ? typeof detail.variableSchema === "string"
            ? detail.variableSchema
            : JSON.stringify(detail.variableSchema, null, 2)
          : baseDraft.variableSchemaJson,
    };
    const vh = (versions.items ?? []).map(mapVersionEntry);
    return {
      pack,
      draft,
      etag: draft.etag,
      versionHistory: vh.length > 0 ? vh : localVersions,
      remote: true,
    };
  } catch {
    if (!localPack) throw new Error("unknown prompt pack");
    const localDraft = getPromptPackDraft(promptPackId);
    if (!localDraft) throw new Error("unknown prompt pack");
    return {
      pack: localPack,
      draft: localDraft,
      etag: localDraft.etag,
      versionHistory: localVersions,
      remote: false,
    };
  }
}

export async function resolveEditorBootstrap(promptPackId: string): Promise<EditorBootstrap | null> {
  if (isLocalDraftPromptPackId(promptPackId)) {
    return loadEphemeralBootstrap(promptPackId);
  }
  try {
    return await loadEditorBootstrap(promptPackId);
  } catch {
    return null;
  }
}

export async function remoteSaveDraft(
  promptPackId: string,
  ifMatch: string | undefined,
  body: Record<string, unknown>,
): Promise<{ etag: string; detail?: PromptPackDetail }> {
  const detail = await pm.patchPromptPack(promptPackId, body, ifMatch);
  const etag = detail.etag != null ? String(detail.etag) : ifMatch ?? "";
  return { etag, detail };
}

export async function remotePublish(promptPackId: string): Promise<void> {
  await pm.publishPromptPack(promptPackId);
}

export async function remoteRollback(promptPackId: string, version: number): Promise<void> {
  await pm.rollbackPromptPack(promptPackId, { promptPackVersion: String(version) });
}

export async function remoteSandboxRun(body: Parameters<typeof pm.createPromptSandboxRun>[0]): Promise<Awaited<ReturnType<typeof pm.createPromptSandboxRun>>> {
  return pm.createPromptSandboxRun(body);
}

export function getAuditTailLocal(promptPackId: string) {
  return getPromptAuditTail(promptPackId);
}
