/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-16
 * 修改功能: Admin **`/api/v1/admin/access-control/*`**（FE_HANDOFF · OpenAPI access-control.yaml）
 */

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const PREFIX = 'v1/admin/access-control'

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

export interface WhitelistEntryDto {
  entryId: string
  listId: string
  userUid: string
  userIdMasked: string
  note?: string | null
  addedAt: string
  addedBy?: string | null
}

export interface WhitelistListResponse {
  items: WhitelistEntryDto[]
  total: number
}

export interface WhitelistCreateBody {
  listId: string
  userUid: string
  userIdMasked?: string | null
  note?: string | null
}

export interface BanItemDto {
  banId: string
  userUid: string
  reasonCode: string
  scope: string
  expiresAt?: string | null
  linkedPause: boolean
  createdAt: string
  createdBy?: string | null
}

export interface BanListResponse {
  items: BanItemDto[]
  total: number
}

export interface BanCreateBody {
  userUid: string
  reasonCode: string
  scope?: string
  expiresAt?: string | null
  linkedPause?: boolean
}

export interface MinVipTierResponse {
  configKey: string
  minVipTier: number
  updatedAt?: string | null
}

export interface RolloutPolicyResponse {
  rolloutWhitelistEnforced: boolean
}

export async function listAccessControlWhitelist(params?: {
  listId?: string
  q?: string
}): Promise<WhitelistListResponse> {
  try {
    const sp = new URLSearchParams()
    if (params?.listId?.trim()) sp.set('listId', params.listId.trim())
    if (params?.q?.trim()) sp.set('q', params.q.trim())
    const qs = sp.toString()
    const path = qs ? `${PREFIX}/whitelist?${qs}` : `${PREFIX}/whitelist`
    return await httpClient.get(path).json<WhitelistListResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function createAccessControlWhitelistEntry(
  body: WhitelistCreateBody,
): Promise<WhitelistEntryDto> {
  try {
    return await httpClient.post(`${PREFIX}/whitelist`, { json: body }).json<WhitelistEntryDto>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function deleteAccessControlWhitelistEntry(entryId: string): Promise<void> {
  try {
    await httpClient.delete(`${PREFIX}/whitelist/${encodeURIComponent(entryId)}`)
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function listAccessControlBans(params?: { q?: string }): Promise<BanListResponse> {
  try {
    const sp = new URLSearchParams()
    if (params?.q?.trim()) sp.set('q', params.q.trim())
    const qs = sp.toString()
    const path = qs ? `${PREFIX}/bans?${qs}` : `${PREFIX}/bans`
    return await httpClient.get(path).json<BanListResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function createAccessControlBan(body: BanCreateBody): Promise<BanItemDto> {
  try {
    return await httpClient.post(`${PREFIX}/bans`, { json: body }).json<BanItemDto>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function deleteAccessControlBan(banId: string): Promise<void> {
  try {
    await httpClient.delete(`${PREFIX}/bans/${encodeURIComponent(banId)}`)
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAccessControlMinVipTier(): Promise<MinVipTierResponse> {
  try {
    return await httpClient.get(`${PREFIX}/membership/min-vip-tier`).json<MinVipTierResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function patchAccessControlMinVipTier(minVipTier: number): Promise<MinVipTierResponse> {
  try {
    return await httpClient
      .patch(`${PREFIX}/membership/min-vip-tier`, { json: { minVipTier } })
      .json<MinVipTierResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAccessControlRollout(): Promise<RolloutPolicyResponse> {
  try {
    return await httpClient.get(`${PREFIX}/rollout`).json<RolloutPolicyResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function patchAccessControlRollout(
  rolloutWhitelistEnforced: boolean,
): Promise<RolloutPolicyResponse> {
  try {
    return await httpClient
      .patch(`${PREFIX}/rollout`, { json: { rolloutWhitelistEnforced } })
      .json<RolloutPolicyResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
