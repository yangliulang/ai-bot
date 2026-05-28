// 作者: Cursor Agent
// 日期: 2026-05-26
// 修改功能: Admin skill-specs Publish 链 · 对齐 handoff 2026-05-27--skill-publish-effective

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const PREFIX = 'v1/admin/skill-specs'

export const PROMPT_SKILL_REF_INVALID = 'PROMPT_SKILL_REF_INVALID'
export const PROMPT_SKILL_VERSION_ROLLBACK = 'PROMPT_SKILL_VERSION_ROLLBACK'
export const PROMPT_SKILL_CONTRACT_INCOMPLETE = 'PROMPT_SKILL_CONTRACT_INCOMPLETE'

export interface SkillOperationSpecSummary {
  skillId: string
  skillSpecVersion: string
  lifecycle: string
  scenarioIds: string[]
  contractComplete: boolean
  specDigest: string | null
  publishedAt: string | null
}

export interface SkillOperationSpecListResponse {
  items: SkillOperationSpecSummary[]
}

export interface SkillSpecVersionEntry {
  skillSpecVersion: string
  lifecycle: string
  publishedAt: string | null
}

export interface SkillSpecVersionHistoryResponse {
  skillId: string
  items: SkillSpecVersionEntry[]
}

export interface SkillOperationSpecBody {
  skillId: string
  skillSpecVersion: string
  bodyMarkdown: string
  specDigest: string | null
  sourceGitRef: string | null
}

export interface SkillSpecPublishBody {
  skillSpecVersion: string
  bodyMarkdown?: string | null
  specDigest?: string | null
  sourceGitRef?: string | null
}

export interface SkillSpecPublishResult {
  skillId: string
  skillSpecVersion: string
  lifecycle: string
  specDigest: string | null
}

async function normalizeKyError(error: unknown): Promise<never> {
  if (error instanceof HTTPError) {
    const cloned = error.response.clone()
    const body: unknown = await cloned.json().catch(() => null)
    if (body !== null && typeof body === 'object') {
      const msg =
        'message' in body && typeof (body as { message: unknown }).message === 'string'
          ? (body as { message: string }).message
          : 'detail' in body && typeof (body as { detail: unknown }).detail === 'string'
            ? (body as { detail: string }).detail
            : undefined
      if (msg) {
        const code =
          'code' in body && typeof (body as { code: unknown }).code === 'string'
            ? (body as { code: string }).code
            : undefined
        throw new AppError(msg, {
          status: error.response.status,
          code,
        })
      }
    }
  }
  throw await toAppError(error)
}

export function explainSkillSpecApiError(e: unknown, fallback: string): string {
  if (!(e instanceof AppError)) return fallback
  const msg = e.message || fallback
  if (e.code === PROMPT_SKILL_REF_INVALID) {
    return `${msg}（技能未发布或版本无效；请先在「技能与工具」Publish。）`
  }
  if (e.code === PROMPT_SKILL_VERSION_ROLLBACK) {
    return `${msg}（版本号须单调递增，不可回退。）`
  }
  if (e.code === PROMPT_SKILL_CONTRACT_INCOMPLETE) {
    return `${msg}（正文须含 §1 且满足 contract-complete；请补全后再 Publish。）`
  }
  return msg
}

export async function listSkillOperationSpecs(params?: {
  lifecycle?: string
}): Promise<SkillOperationSpecListResponse> {
  try {
    const search = new URLSearchParams()
    if (params?.lifecycle) search.set('lifecycle', params.lifecycle)
    const q = search.toString()
    return await httpClient
      .get(q ? `${PREFIX}?${q}` : PREFIX)
      .json<SkillOperationSpecListResponse>()
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function getSkillOperationSpec(skillId: string): Promise<SkillOperationSpecSummary> {
  try {
    return await httpClient
      .get(`${PREFIX}/${encodeURIComponent(skillId)}`)
      .json<SkillOperationSpecSummary>()
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function getSkillOperationSpecVersions(
  skillId: string,
): Promise<SkillSpecVersionHistoryResponse> {
  try {
    return await httpClient
      .get(`${PREFIX}/${encodeURIComponent(skillId)}/versions`)
      .json<SkillSpecVersionHistoryResponse>()
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function getSkillOperationSpecVersionBody(
  skillId: string,
  skillSpecVersion: string,
): Promise<SkillOperationSpecBody> {
  try {
    return await httpClient
      .get(
        `${PREFIX}/${encodeURIComponent(skillId)}/versions/${encodeURIComponent(skillSpecVersion)}`,
      )
      .json<SkillOperationSpecBody>()
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function publishSkillOperationSpec(
  skillId: string,
  body: SkillSpecPublishBody,
): Promise<SkillSpecPublishResult> {
  try {
    return await httpClient
      .post(`${PREFIX}/${encodeURIComponent(skillId)}/publish`, { json: body })
      .json<SkillSpecPublishResult>()
  } catch (e) {
    return normalizeKyError(e)
  }
}
