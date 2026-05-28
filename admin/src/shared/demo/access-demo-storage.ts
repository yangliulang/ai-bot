/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-12
 * 修改功能: AGENT_MIN_VIP_TIER 演示存储（sessionStorage），与 product-doc accessDemoStorage 一致
 */
const VIP_STORAGE_KEY = 'demo_admin_access_agent_min_vip_tier'

const VIP_TIER_DEMO_MAX = 9

function clampVipTierNum(n: number): number {
  if (!Number.isFinite(n)) return 0
  return Math.min(VIP_TIER_DEMO_MAX, Math.max(0, Math.trunc(n)))
}

function normalizeFallbackString(fallback: string): string {
  const raw = String(fallback).replace(/（.*）/, '').trim()
  const n = Number.parseInt(raw, 10)
  return String(clampVipTierNum(Number.isFinite(n) ? n : 2))
}

export function readDemoAgentMinVipTier(fallback: string): string {
  const fb = normalizeFallbackString(fallback)
  try {
    if (typeof sessionStorage === 'undefined') return fb
    const v = sessionStorage.getItem(VIP_STORAGE_KEY)
    if (v != null && v !== '') {
      const parsed = Number.parseInt(v, 10)
      return String(clampVipTierNum(Number.isFinite(parsed) ? parsed : Number.parseInt(fb, 10)))
    }
    return fb
  } catch {
    return fb
  }
}

export function writeDemoAgentMinVipTier(value: string): void {
  try {
    const parsed = Number.parseInt(value, 10)
    const clamped = String(clampVipTierNum(Number.isFinite(parsed) ? parsed : 0))
    sessionStorage.setItem(VIP_STORAGE_KEY, clamped)
  } catch {
    /* ignore quota / private mode */
  }
}

export function clearDemoAgentMinVipTier(): void {
  try {
    sessionStorage.removeItem(VIP_STORAGE_KEY)
  } catch {
    /* ignore */
  }
}

export const VIP_TIER_MAX = VIP_TIER_DEMO_MAX
