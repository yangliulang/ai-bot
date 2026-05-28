// 作者: 杨永的Agent
// 日期: 2026-05-27
// 修改功能: scenarioId ↔ pp-* 治理映射（对齐 server prompt_governance_catalog · FE_HANDOFF 0030）

/** 写路径 scenarioId → 治理 promptPackId（与 governance-map.md 一致） */
export const WRITE_SCENARIO_TO_GOVERNANCE_PACK_ID: Readonly<Record<string, string>> = {
  'trade.spot.limit_order': 'pp-trading-spot-limit',
  'trade.spot.flash_convert': 'pp-trading-spot-flash',
  'trade.spot.amend_limit_order': 'pp-trading-spot-amend',
  'trade.futures.market_order': 'pp-trading-futures-market',
  'trade.futures.limit_order': 'pp-trading-futures-limit',
  'trade.futures.amend_limit_order': 'pp-trading-futures-amend',
  'trade.futures.take_profit_stop': 'pp-trading-futures-tpsl',
  'futures.condition.order_create': 'pp-trading-futures-tpsl',
  'margin.cross.market_order': 'pp-trading-margin-market',
  'margin.cross.limit_order': 'pp-trading-margin-limit',
  'wealth.subscribe': 'pp-trading-wealth-subscribe',
  'wealth.redeem': 'pp-trading-wealth-redeem',
}

const READ_ANALYSIS_EXACT = new Set([
  'wealth.holdings_read',
  'read.account.balance',
  'read.market.ticker',
  'read.market.depth',
  'read.market.trades',
])

const READ_ANALYSIS_PREFIXES = [
  'read.market.',
  'market.read_',
  'research.',
  'monitoring.',
  'orders.read_',
  'portfolio.',
  'futures.read_',
] as const

export const PLATFORM_SYSTEM_SCENARIO_ID = 'agent.runtime.platform_system'
export const PLATFORM_SAFETY_SCENARIO_ID = 'agent.runtime.platform_safety'
export const ANALYSIS_CORE_SCENARIO_ID = 'agent.runtime.analysis_core'

/** 平台 / 横切 / 读侧分析 · 治理包 id */
export const GOVERNANCE_PLATFORM_PACK_BY_SCENARIO: Readonly<Record<string, string>> = {
  [PLATFORM_SYSTEM_SCENARIO_ID]: 'pp-system-core',
  [PLATFORM_SAFETY_SCENARIO_ID]: 'pp-safety-global',
  [ANALYSIS_CORE_SCENARIO_ID]: 'pp-analysis-core',
}

/** 迁移 0030 后由 pp-* 替代的 legacy pack_*（列表默认隐藏，deprecated 筛选可见） */
export const LEGACY_PACK_IDS_SUPERSEDED: ReadonlySet<string> = new Set([
  'pack_platform_system_v1',
  'pack_platform_safety_v1',
  'pack_trading_spot_flash_convert_v1',
  'pack_trading_spot_limit_order_v1',
  'pack_trading_spot_amend_limit_order_v1',
  'pack_trading_futures_market_order_v1',
  'pack_trading_futures_limit_order_v1',
  'pack_trading_margin_cross_market_order_v1',
  'pack_trading_margin_cross_limit_order_v1',
  'pack_trading_read_market_ticker_v1',
  'pack_trading_read_market_depth_v1',
  'pack_trading_read_market_trades_v1',
  'pack_trading_read_account_balance_v1',
  'pack_trading_wealth_holdings_read_v1',
])

export function isGovernancePromptPackId(promptPackId: string): boolean {
  return promptPackId.trim().startsWith('pp-')
}

function isAnalysisGovernanceScenario(scenarioId: string): boolean {
  const sid = scenarioId.trim()
  if (!sid || sid in WRITE_SCENARIO_TO_GOVERNANCE_PACK_ID) return false
  if (READ_ANALYSIS_EXACT.has(sid)) return sid !== 'chat.faq'
  return READ_ANALYSIS_PREFIXES.some((p) => sid.startsWith(p))
}

/** 治理条文 id；无映射时返回 null（如 chat.faq 仍用 legacy pack） */
export function governancePackIdForScenario(scenarioId: string): string | null {
  const sid = scenarioId.trim()
  if (!sid) return null
  const platform = GOVERNANCE_PLATFORM_PACK_BY_SCENARIO[sid]
  if (platform) return platform
  const write = WRITE_SCENARIO_TO_GOVERNANCE_PACK_ID[sid]
  if (write) return write
  if (isAnalysisGovernanceScenario(sid)) return 'pp-analysis-core'
  return null
}

export interface PromptPackListRowLike {
  promptPackId: string
  scenarioId?: string | null
  lifecycle?: string | null
}

/**
 * 策略列表：默认隐藏已被 pp-* 替代的 legacy 行；仅在「下线标记」筛选中展示。
 */
export function filterSupersededLegacyPacks<T extends PromptPackListRowLike>(
  rows: T[],
  lifecycleFilter: string,
): T[] {
  if (lifecycleFilter === 'deprecated') return rows
  return rows.filter((row) => !LEGACY_PACK_IDS_SUPERSEDED.has(row.promptPackId))
}

/** 场景快捷筛选 chip 的治理包提示（非 DB 主键，仅 UI 文案） */
export function governancePackHintForScenarioChip(scenarioId: string): string | null {
  return governancePackIdForScenario(scenarioId)
}
