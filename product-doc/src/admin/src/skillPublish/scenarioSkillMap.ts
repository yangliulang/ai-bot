/**
 * 主 scenarioId → skillId（与 specs/requirements/prompts/library/scenarios/registry.md 写路径行同窗）
 */

export const SCENARIO_PRIMARY_SKILL: Record<string, string> = {
  "trade.spot.flash_convert": "skill.spot.flash_convert",
  "trade.spot.limit_order": "skill.spot.limit_order",
  "trade.spot.amend_limit_order": "skill.spot.amend_limit_order",
  "trade.futures.market_order": "skill.futures.market_order",
  "trade.futures.limit_order": "skill.futures.limit_order",
  "trade.futures.amend_limit_order": "skill.futures.amend_limit_order",
  "trade.futures.take_profit_stop": "skill.futures.take_profit_stop",
  "futures.condition.order_create": "skill.futures.take_profit_stop",
  "margin.cross.market_order": "skill.margin.cross_market_order",
  "margin.cross.limit_order": "skill.margin.cross_limit_order",
  "wealth.subscribe": "skill.wealth.subscribe",
  "wealth.redeem": "skill.wealth.redeem",
};

export function resolveSkillIdForScenario(scenarioId: string): string | undefined {
  const key = scenarioId.trim();
  return SCENARIO_PRIMARY_SKILL[key];
}

export function isWriteScenario(scenarioId: string): boolean {
  return Boolean(resolveSkillIdForScenario(scenarioId));
}
