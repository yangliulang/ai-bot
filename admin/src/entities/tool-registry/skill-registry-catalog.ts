/**
 * A 类写技能 · 产品登记元数据（对齐 product-doc `skillRegistryCatalog` / manifest 同序）。
 * 版本 / lifecycle / contractComplete 由 API 覆盖。
 */

import { SKILL_MATRIX_STATUS } from '@/entities/tool-registry/tool-registry-copy'
import type { SkillOperationSpecSummary } from '@/shared/api/admin-skill-specs'

export type SkillMatrixStatus = 'frozen' | 'tbd' | 'draft'

export interface SkillRegistryCatalogEntry {
  skillId: string
  summary: string
  userFlow: string
  exchangeAction: string
  publishRequired: boolean
  matrixStatus: SkillMatrixStatus
  defaultEnabled: boolean
  specNote?: string
}

export interface SkillRegistryRowView {
  skillId: string
  summary: string
  userFlow: string
  exchangeAction: string
  matrixStatus: SkillMatrixStatus
  publishRequired: boolean
  defaultEnabled: boolean
  specNote?: string
  skillSpecVersion: string | null
  lifecycle: string | null
  contractComplete: boolean
  specDigest: string | null
  publishedAt: string | null
  isRuntimePublished: boolean
}

/** 与 specs/requirements/skill-specs/manifest.yaml 同序 */
export const SKILL_REGISTRY_CATALOG: SkillRegistryCatalogEntry[] = [
  {
    skillId: 'skill.spot.flash_convert',
    summary: '现货市价 / 闪兑',
    userFlow: '用户说明买/卖币种与金额 → 确认无杠杆相关表述 → 二次确认 → 按市价或闪兑成交',
    exchangeAction: '币币市价或闪兑下单（不设委托价）',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.spot.limit_order',
    summary: '现货限价',
    userFlow: '收集交易对、方向、限价与数量 → 展示限价确认信息 → 用户确认后挂单',
    exchangeAction: '币币限价挂单；改单须先撤单再挂新单',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.spot.amend_limit_order',
    summary: '现货限价 · 逻辑改单',
    userFlow: '确认原单与新参数 → 一次二次确认 → 先撤原单再挂新限价单',
    exchangeAction: '先撤销原限价单，再挂新的限价单',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.spot.oco',
    summary: '现货 OCO',
    userFlow: '本阶段不在对话内提供 OCO 下单闭环',
    exchangeAction: '对话内暂不支持下单',
    publishRequired: false,
    matrixStatus: 'tbd',
    defaultEnabled: false,
    specNote: '仅作备案；请引导用户前往主站，或分步说明如何自行操作',
  },
  {
    skillId: 'skill.spot.bracket',
    summary: '现货 Bracket',
    userFlow: '本阶段不在对话内提供 Bracket 下单闭环',
    exchangeAction: '对话内暂不支持下单',
    publishRequired: false,
    matrixStatus: 'tbd',
    defaultEnabled: false,
    specNote: '仅作备案；请引导用户前往主站，或分步说明如何自行操作',
  },
  {
    skillId: 'skill.futures.market_order',
    summary: '合约市价',
    userFlow: '确认合约、方向、数量与杠杆相关说明 → 二次确认 → 永续/合约市价开仓或平仓',
    exchangeAction: '合约市价下单',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.futures.limit_order',
    summary: '合约限价',
    userFlow: '收集合约、方向、限价与张数 → 展示合约限价确认信息 → 用户确认后挂单',
    exchangeAction: '合约限价挂单',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.futures.amend_limit_order',
    summary: '合约限价 · 逻辑改单',
    userFlow: '一次二次确认覆盖撤单与新挂单，中间不再重复确认',
    exchangeAction: '先撤原单，再挂新的合约限价单',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.futures.take_profit_stop',
    summary: '止盈止损 / 条件离场',
    userFlow: '区分即时开仓与条件离场 → 澄清触发价与方向 → 展示条件单确认信息',
    exchangeAction: '条件单（止盈止损等，以交易所实际支持为准）',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.margin.cross_market_order',
    summary: '全仓杠杆 · 市价',
    userFlow: '识别借币/全仓语境 → 说明风险与杠杆 → 必要时双重确认 → 市价下单',
    exchangeAction: '全仓杠杆市价下单',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.margin.cross_limit_order',
    summary: '全仓杠杆 · 限价',
    userFlow: '全仓限价参数齐备 → 展示全仓限价确认信息 → 用户确认后挂单',
    exchangeAction: '全仓杠杆限价挂单',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.margin.transfer_spot_to_cross',
    summary: '现货↔全仓划转',
    userFlow: '引导用户前往主站完成划转，对话内不代办',
    exchangeAction: '须在主站完成划转',
    publishRequired: false,
    matrixStatus: 'tbd',
    defaultEnabled: false,
    specNote: '对话内不提供划转；请引导用户前往主站操作',
  },
  {
    skillId: 'skill.wealth.subscribe',
    summary: '理财申购',
    userFlow: '澄清产品、金额与期限 → 高风险二次确认 → 提交申购',
    exchangeAction: '理财申购；不支持时引导用户前往主站',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    skillId: 'skill.wealth.redeem',
    summary: '理财赎回',
    userFlow: '确认份额与产品 → 二次确认 → 提交赎回',
    exchangeAction: '理财赎回',
    publishRequired: true,
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
]

const BY_SKILL_ID = new Map(SKILL_REGISTRY_CATALOG.map((e) => [e.skillId, e]))

export function getSkillRegistryEntry(skillId: string): SkillRegistryCatalogEntry | undefined {
  return BY_SKILL_ID.get(skillId)
}

export function mergeSkillRegistryWithApi(
  items: SkillOperationSpecSummary[],
): SkillRegistryRowView[] {
  const apiMap = new Map(items.map((i) => [i.skillId, i]))
  const rows: SkillRegistryRowView[] = SKILL_REGISTRY_CATALOG.map((entry) => {
    const api = apiMap.get(entry.skillId)
    return overlayEntry(entry, api)
  })
  for (const api of items) {
    if (!BY_SKILL_ID.has(api.skillId)) {
      rows.push({
        skillId: api.skillId,
        summary: api.skillId,
        userFlow: '—',
        exchangeAction: '—',
        matrixStatus: 'frozen',
        publishRequired: true,
        defaultEnabled: true,
        skillSpecVersion: api.skillSpecVersion,
        lifecycle: api.lifecycle,
        contractComplete: api.contractComplete,
        specDigest: api.specDigest,
        publishedAt: api.publishedAt,
        isRuntimePublished: api.lifecycle === 'PUBLISHED',
      })
    }
  }
  return rows
}

function overlayEntry(
  entry: SkillRegistryCatalogEntry,
  api: SkillOperationSpecSummary | undefined,
): SkillRegistryRowView {
  return {
    skillId: entry.skillId,
    summary: entry.summary,
    userFlow: entry.userFlow,
    exchangeAction: entry.exchangeAction,
    matrixStatus: entry.matrixStatus,
    publishRequired: entry.publishRequired,
    defaultEnabled: entry.defaultEnabled,
    specNote: entry.specNote,
    skillSpecVersion: api?.skillSpecVersion ?? null,
    lifecycle: api?.lifecycle ?? null,
    contractComplete: api?.contractComplete ?? false,
    specDigest: api?.specDigest ?? null,
    publishedAt: api?.publishedAt ?? null,
    isRuntimePublished: api?.lifecycle === 'PUBLISHED',
  }
}

export function countSpecReadyStats(rows: SkillRegistryRowView[]): {
  complete: number
  publishRequired: number
} {
  const pub = rows.filter((r) => r.publishRequired)
  const complete = pub.filter((r) => r.contractComplete).length
  return { complete, publishRequired: pub.length }
}

export function countRuntimePublishedStats(rows: SkillRegistryRowView[]): {
  published: number
  total: number
} {
  const pub = rows.filter((r) => r.publishRequired)
  const published = pub.filter((r) => r.isRuntimePublished).length
  return { published, total: pub.length }
}

export function matrixStatusLabel(status: SkillMatrixStatus): string {
  if (status === 'frozen') return SKILL_MATRIX_STATUS.frozen
  if (status === 'tbd') return SKILL_MATRIX_STATUS.tbd
  return SKILL_MATRIX_STATUS.draft
}

export function skillDomainLabel(skillId: string): string | null {
  if (skillId.startsWith('skill.spot.')) return '现货'
  if (skillId.startsWith('skill.futures.')) return '合约'
  if (skillId.startsWith('skill.margin.')) return '全仓'
  if (skillId.startsWith('skill.wealth.')) return '理财'
  return null
}

export function matrixStatusClass(status: SkillMatrixStatus): string {
  if (status === 'frozen') {
    return 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200'
  }
  if (status === 'tbd') {
    return 'border-amber-500/40 bg-amber-500/10 text-amber-200'
  }
  return 'border-slate-600 bg-slate-800/50 text-slate-400'
}
