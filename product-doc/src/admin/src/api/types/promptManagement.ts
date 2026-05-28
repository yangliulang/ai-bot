/**
 * 与 `specs/openapi/components/prompt-management-schemas.yaml` 同窗的 TS 形状（运行时仍为 `additionalProperties` 宽松解析）。
 */

export type PromptPackType = "SYSTEM" | "TRADING" | "SAFETY" | "ANALYSIS";
export type PromptPackLifecycle = "DRAFT" | "PUBLISHED" | "LOCKED";

export interface PromptPackCreateRequest {
  promptPackType: PromptPackType;
  scenarioId?: string | null;
  [key: string]: unknown;
}

export interface PromptPackSummary {
  promptPackId: string;
  promptPackType: PromptPackType;
  scenarioId?: string | null;
  promptPackVersion?: string;
  lifecycle?: PromptPackLifecycle;
  etag?: string;
  [key: string]: unknown;
}

export interface PromptPackListResponse {
  items?: PromptPackSummary[];
  [key: string]: unknown;
}

export interface PromptPackDetail {
  promptPackId: string;
  promptPackType: PromptPackType;
  scenarioId?: string | null;
  promptPackVersion?: string;
  lifecycle?: PromptPackLifecycle;
  etag?: string;
  placeholderDenylistRevision?: string;
  safetyPhraseBlocklistRevision?: string;
  [key: string]: unknown;
}

export interface PromptPackPatch {
  [key: string]: unknown;
}

export interface PromptVersionEntry {
  promptPackVersion?: string;
  publishedAt?: string;
  lifecycle?: PromptPackLifecycle;
  actor?: string;
  summary?: string;
  event?: string;
  [key: string]: unknown;
}

export interface PromptVersionHistoryResponse {
  items?: PromptVersionEntry[];
  [key: string]: unknown;
}

export interface PromptPublishResult {
  promptPackId?: string;
  promptPackVersion?: string;
  lifecycle?: PromptPackLifecycle;
  [key: string]: unknown;
}

export interface PromptRollbackRequest {
  promptPackVersion: string;
}

export interface FewShotExample {
  fewShotId: string;
  role?: string;
  content?: string;
  [key: string]: unknown;
}

export interface FewShotListResponse {
  items?: FewShotExample[];
  [key: string]: unknown;
}

export interface PromptSandboxRunRequest {
  promptPackId?: string;
  scenarioId?: string | null;
  modelId?: string;
  fixture?: unknown;
  variables?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface PromptSandboxRunResult {
  runId?: string;
  status?: string;
  [key: string]: unknown;
}

export interface EffectivePromptResponse {
  scenarioId: string;
  promptPackVersion: string;
  etag?: string;
  [key: string]: unknown;
}
