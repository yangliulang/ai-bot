// 作者: 杨永的Agent
// 日期: 2026-05-27
// 修改功能: 写路径场景判定与 STM/LTM 运营文案（对齐 server write_path_pipeline · telegram_stm）

/** 与 server `runtime_skill_operation_spec._SCENARIO_SKILL_ID` 键集一致 */
export const WRITE_PATH_SCENARIO_IDS = new Set<string>([
  'trade.spot.limit_order',
  'trade.spot.amend_limit_order',
  'trade.spot.flash_convert',
  'trade.futures.market_order',
  'trade.futures.limit_order',
  'trade.futures.amend_limit_order',
  'trade.futures.take_profit_stop',
  'automation.condition_order',
  'automation.condition_order_cancel',
  'margin.cross.market_order',
  'margin.cross.limit_order',
  'wealth.subscribe',
  'wealth.redeem',
])

export function isWritePathScenario(scenarioId: string | null | undefined): boolean {
  const sid = (scenarioId ?? '').trim()
  return sid.length > 0 && WRITE_PATH_SCENARIO_IDS.has(sid)
}

export const MEMORY_SESSION_CLEARED_EVENT = 'agent.memory.session_cleared' as const
export const MEMORY_LTM_REVOKE_REQUESTED_EVENT = 'agent.memory.ltm_revoke_requested' as const
export { MEMORY_RESUME_CLASSIFIED_EVENT } from '@/shared/lib/clarify-session-display'

/** Telegram 用户侧「重新开始」· 仅清 STM（与后端 `_STM_CLEAR_REPLY` 同源语义） */
export const MEMORY_STM_CLEAR_USER_HINT =
  '用户说「重新开始」或「新话题」→ 清空本会话短期记忆（STM），下轮不再带旧 L0 上下文。'

/** Telegram 用户侧「清空记忆」· LTM 分流说明（与后端 `_LTM_REVOKE_REPLY` 同源） */
export const MEMORY_LTM_REVOKE_USER_HINT =
  '「清空记忆」会撤销跨会话偏好（长期记忆），与「重新开始」不同。长期记忆撤销功能尚在筹备；若仅需清空本会话，请说「重新开始」或「新话题」。'
