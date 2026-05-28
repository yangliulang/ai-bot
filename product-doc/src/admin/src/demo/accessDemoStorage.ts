/** Demo：AGENT_MIN_VIP_TIER 演示值（sessionStorage）；准入页与 mock 兜底共用。
 * **同窗**：`access-control` / PRD 模块六 · I02；**不**替代生产 **eligibility** 接口与 **contract-closure** 矩阵登记。
 */

const VIP_STORAGE_KEY = "demo_admin_access_agent_min_vip_tier";

/** 产品约定：会员等级 0–9 */
const VIP_TIER_DEMO_MAX = 9;

function clampVipTierNum(n: number): number {
  if (!Number.isFinite(n)) return 0;
  return Math.min(VIP_TIER_DEMO_MAX, Math.max(0, Math.trunc(n)));
}

function normalizeFallbackString(fallback: string): string {
  const raw = String(fallback).replace(/（.*）/, "").trim();
  const n = Number.parseInt(raw, 10);
  return String(clampVipTierNum(Number.isFinite(n) ? n : 2));
}

export function readDemoAgentMinVipTier(fallback: string): string {
  const fb = normalizeFallbackString(fallback);
  try {
    if (typeof sessionStorage === "undefined") return fb;
    const v = sessionStorage.getItem(VIP_STORAGE_KEY);
    if (v != null && v !== "") {
      const parsed = Number.parseInt(v, 10);
      return String(clampVipTierNum(Number.isFinite(parsed) ? parsed : Number.parseInt(fb, 10)));
    }
    return fb;
  } catch {
    return fb;
  }
}

export function writeDemoAgentMinVipTier(value: string): void {
  try {
    const parsed = Number.parseInt(value, 10);
    const clamped = String(clampVipTierNum(Number.isFinite(parsed) ? parsed : 0));
    sessionStorage.setItem(VIP_STORAGE_KEY, clamped);
  } catch {
    /* ignore quota / private mode */
  }
}

/** 清除本机覆盖，下次读取将回落到 mock/config 默认值 */
export function clearDemoAgentMinVipTier(): void {
  try {
    sessionStorage.removeItem(VIP_STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

export const VIP_TIER_MAX = VIP_TIER_DEMO_MAX;
