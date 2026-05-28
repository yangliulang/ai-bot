import type {
  EffectivePromptResponse,
  FewShotExample,
  FewShotListResponse,
  PromptPackCreateRequest,
  PromptPackDetail,
  PromptPackListResponse,
  PromptPackPatch,
  PromptPublishResult,
  PromptRollbackRequest,
  PromptSandboxRunRequest,
  PromptSandboxRunResult,
  PromptVersionHistoryResponse,
} from "./types/promptManagement";
import { apiFetch } from "./http";

/** OpenAPI: listPromptPacks */
export function listPromptPacks(params: { promptPackType?: string; scenarioId?: string }): Promise<PromptPackListResponse> {
  const sp = new URLSearchParams();
  if (params.promptPackType) sp.set("promptPackType", params.promptPackType);
  if (params.scenarioId) sp.set("scenarioId", params.scenarioId);
  const q = sp.toString();
  return apiFetch(`/api/v1/admin/prompt-packs${q ? `?${q}` : ""}`);
}

/** OpenAPI: createPromptPack */
export function createPromptPack(body: PromptPackCreateRequest): Promise<PromptPackDetail> {
  return apiFetch(`/api/v1/admin/prompt-packs`, { method: "POST", body: JSON.stringify(body) });
}

/** OpenAPI: getPromptPack */
export function getPromptPackRemote(promptPackId: string): Promise<PromptPackDetail> {
  return apiFetch(`/api/v1/admin/prompt-packs/${encodeURIComponent(promptPackId)}`);
}

/** OpenAPI: patchPromptPack · PM-C03 */
export function patchPromptPack(
  promptPackId: string,
  body: PromptPackPatch,
  ifMatch?: string,
): Promise<PromptPackDetail> {
  const headers: Record<string, string> = {};
  if (ifMatch) headers["If-Match"] = ifMatch;
  return apiFetch(`/api/v1/admin/prompt-packs/${encodeURIComponent(promptPackId)}`, {
    method: "PATCH",
    body: JSON.stringify(body),
    headers,
  });
}

/** OpenAPI: getPromptPackVersions */
export function getPromptPackVersions(promptPackId: string): Promise<PromptVersionHistoryResponse> {
  return apiFetch(`/api/v1/admin/prompt-packs/${encodeURIComponent(promptPackId)}/versions`);
}

/** OpenAPI: publishPromptPack */
export function publishPromptPack(promptPackId: string): Promise<PromptPublishResult> {
  return apiFetch(`/api/v1/admin/prompt-packs/${encodeURIComponent(promptPackId)}/publish`, { method: "POST" });
}

/** OpenAPI: rollbackPromptPack */
export function rollbackPromptPack(promptPackId: string, body: PromptRollbackRequest): Promise<PromptPublishResult> {
  return apiFetch(`/api/v1/admin/prompt-packs/${encodeURIComponent(promptPackId)}/rollback`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** OpenAPI: listPromptPackFewShots */
export function listPromptPackFewShots(promptPackId: string): Promise<FewShotListResponse> {
  return apiFetch(`/api/v1/admin/prompt-packs/${encodeURIComponent(promptPackId)}/few-shots`);
}

/** OpenAPI: createPromptPackFewShot */
export function createPromptPackFewShot(promptPackId: string, body: { role?: string; content?: string }): Promise<FewShotExample> {
  return apiFetch(`/api/v1/admin/prompt-packs/${encodeURIComponent(promptPackId)}/few-shots`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** OpenAPI: deletePromptPackFewShot */
export function deletePromptPackFewShot(promptPackId: string, fewShotId: string): Promise<void> {
  return apiFetch(`/api/v1/admin/prompt-packs/${encodeURIComponent(promptPackId)}/few-shots/${encodeURIComponent(fewShotId)}`, {
    method: "DELETE",
  });
}

/** OpenAPI: createPromptSandboxRun */
export function createPromptSandboxRun(body: PromptSandboxRunRequest): Promise<PromptSandboxRunResult> {
  return apiFetch(`/api/v1/admin/prompt-packs/sandbox/runs`, { method: "POST", body: JSON.stringify(body) });
}

/** OpenAPI: getEffectivePrompt · FR-PM08 */
export function getEffectivePrompt(
  scenarioId: string,
  opts?: { promptPackVersion?: string; ifNoneMatch?: string },
): Promise<EffectivePromptResponse> {
  const sp = new URLSearchParams({ scenarioId });
  if (opts?.promptPackVersion) sp.set("promptPackVersion", opts.promptPackVersion);
  const headers: Record<string, string> = {};
  if (opts?.ifNoneMatch) headers["If-None-Match"] = opts.ifNoneMatch;
  return apiFetch(`/api/v1/internal/prompts/effective?${sp.toString()}`, { headers });
}
