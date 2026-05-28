/** 准入 Demo：联调前本地快照（路线图 §1.4 门禁叙事） */

export interface WhitelistEntry {
  listId: string
  userIdMasked: string
  note: string
  addedAt: string
  addedBy: string
}

export interface UserBanRow {
  banId: string
  userUid: string
  reasonCode: string
  scope: string
  expiresAt: string
  createdAt: string
  linkedPause: boolean
  createdBy: string
}

export interface KycMirrorRow {
  userIdMasked: string
  kycTier: string
  region: string
  lastSyncedAt: string
  i02Impact: string
}

export interface MembershipVipLevel {
  tier: number
  label: string
}

export const DEMO_VIP_LEVELS: MembershipVipLevel[] = [
  { tier: 0, label: 'VIP0 · 普通' },
  { tier: 1, label: 'VIP1' },
  { tier: 2, label: 'VIP2' },
  { tier: 3, label: 'VIP3' },
  { tier: 4, label: 'VIP4' },
  { tier: 5, label: 'VIP5' },
  { tier: 6, label: 'VIP6' },
  { tier: 7, label: 'VIP7' },
  { tier: 8, label: 'VIP8' },
  { tier: 9, label: 'VIP9 · 尊享' },
]

export const DEMO_WHITELIST: WhitelistEntry[] = [
  {
    listId: '20260402000001',
    userIdMasked: 'u-10482',
    note: '内测交易白名单',
    addedAt: '2026-04-02T08:00:00Z',
    addedBy: 'ops.admin',
  },
  {
    listId: '20260402000001',
    userIdMasked: 'u-50001',
    note: '运营手工添加',
    addedAt: '2026-04-05T11:20:00Z',
    addedBy: 'ops.admin',
  },
]

export const DEMO_USER_BANS: UserBanRow[] = [
  {
    banId: 'ban-001',
    userUid: '1000283765008847361',
    reasonCode: 'AGENT_USER_BLOCKED',
    scope: 'AGENT_PRODUCT',
    expiresAt: '2026-06-01T00:00:00Z',
    createdAt: '2026-05-02T14:00:00Z',
    linkedPause: true,
    createdBy: 'risk.ops',
  },
]

export const DEMO_KYC_MIRRORS: KycMirrorRow[] = [
  {
    userIdMasked: 'u-10482',
    kycTier: 'T2',
    region: 'HK',
    lastSyncedAt: '2026-05-07T00:40:00Z',
    i02Impact: '通过',
  },
  {
    userIdMasked: 'u-22001',
    kycTier: 'T1',
    region: 'CN',
    lastSyncedAt: '2026-05-06T22:10:00Z',
    i02Impact: '与 VIP 并列校验',
  },
]

/** 路线图 1.4 错误码镜像（运营可读） */
export const GATE_BLOCK_REASON_CODES: { code: string; desc: string }[] = [
  { code: 'AGENT_COMPLIANCE_RESTRICTED', desc: '合规限制' },
  { code: 'AGENT_USER_BLOCKED', desc: '用户封禁' },
  { code: 'AGENT_REGION_BLOCKED', desc: '地域限制' },
  { code: 'AGENT_KYC_REQUIRED', desc: 'KYC 不足' },
  { code: 'AGENT_ROLLOUT_BLOCKED', desc: '灰度未开放' },
  { code: 'AGENT_MEMBERSHIP_BLOCKED', desc: '会员 / VIP 不达标' },
]
