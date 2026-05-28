/**
 * Prompt 扩展 · 仅 **TRADING 写路径场景包**
 * 读侧 / 分析 / 监控 → 统一 `pp-analysis-core` + **ANALYSIS_CAPABILITY_REGISTRY**
 */

export type ExtendedPackSpec = {
  promptPackId: string;
  kind: "TRADING";
  title: string;
  scenarioId: string;
  skillId: string;
  description: string;
  effectiveBodyPreview: string;
  fewShotCount?: number;
  publisher?: string;
};

const MVP_SKILL_VER = "0.1.0-mvp";

export function skillRef(skillId: string): string {
  return `${skillId}@${MVP_SKILL_VER}`;
}

export const EXTENDED_TRADING_PACK_SPECS: ExtendedPackSpec[] = [
  {
    promptPackId: "pp-trading-spot-amend",
    kind: "TRADING",
    title: "现货限价改单",
    scenarioId: "trade.spot.amend_limit_order",
    skillId: "skill.spot.amend_limit_order",
    description: "适用：修改现货限价委托。须先定位订单再走确认。",
    effectiveBodyPreview: "改单：先定位订单，再走确认，不催促连点",
    fewShotCount: 1,
    publisher: "editor.li@ex.co",
  },
  {
    promptPackId: "pp-trading-futures-amend",
    kind: "TRADING",
    title: "合约限价改单",
    scenarioId: "trade.futures.amend_limit_order",
    skillId: "skill.futures.amend_limit_order",
    description: "适用：修改合约限价委托（单次确认完成改单）。",
    effectiveBodyPreview: "合约改单：参数确认后执行",
    publisher: "editor.chen@ex.co",
  },
  {
    promptPackId: "pp-trading-futures-tpsl",
    kind: "TRADING",
    title: "合约止盈止损/条件单",
    scenarioId: "trade.futures.take_profit_stop",
    skillId: "skill.futures.take_profit_stop",
    description: "适用：合约止盈止损或条件委托。",
    effectiveBodyPreview: "条件单：参数+风险说明+确认",
    fewShotCount: 1,
    publisher: "editor.li@ex.co",
  },
  {
    promptPackId: "pp-trading-margin-market",
    kind: "TRADING",
    title: "全仓杠杆市价",
    scenarioId: "margin.cross.market_order",
    skillId: "skill.margin.cross_market_order",
    description: "适用：全仓杠杆市价。先说明杠杆风险。",
    effectiveBodyPreview: "杠杆市价：先风险说明再确认",
    publisher: "editor.li@ex.co",
  },
  {
    promptPackId: "pp-trading-margin-limit",
    kind: "TRADING",
    title: "全仓杠杆限价",
    scenarioId: "margin.cross.limit_order",
    skillId: "skill.margin.cross_limit_order",
    description: "适用：全仓杠杆限价挂单。",
    effectiveBodyPreview: "杠杆限价：价格数量齐备后确认",
    publisher: "editor.chen@ex.co",
  },
  {
    promptPackId: "pp-trading-wealth-subscribe",
    kind: "TRADING",
    title: "理财申购",
    scenarioId: "wealth.subscribe",
    skillId: "skill.wealth.subscribe",
    description: "适用：理财产品申购。含高危确认（以编排为准）。",
    effectiveBodyPreview: "申购：产品金额澄清 → 确认 → 执行",
    fewShotCount: 1,
    publisher: "editor.zhao@ex.co",
  },
  {
    promptPackId: "pp-trading-wealth-redeem",
    kind: "TRADING",
    title: "理财赎回",
    scenarioId: "wealth.redeem",
    skillId: "skill.wealth.redeem",
    description: "适用：理财产品赎回。",
    effectiveBodyPreview: "赎回：份额与产品确认后执行",
    publisher: "editor.zhao@ex.co",
  },
];

/** 正文 SSOT：`promptBodyTemplates.ts` → `PROMPT_BODY_BY_PACK_ID` */

export const UNIFIED_ANALYSIS_PROMPT_PACK_ID = "pp-analysis-core" as const;

export type AnalysisCapabilityDomain = "market" | "research" | "portfolio" | "wealth" | "monitoring";

export type AnalysisCapabilityRow = {
  scenarioId: string;
  domain: AnalysisCapabilityDomain;
  capabilityKey: string;
  title: string;
  summary: string;
};

export const ANALYSIS_CAPABILITY_REGISTRY: AnalysisCapabilityRow[] = [
  { scenarioId: "market.read_quote", domain: "market", capabilityKey: "quote", title: "标价摘要", summary: "现货/合约最新价量" },
  { scenarioId: "market.read_microstructure", domain: "market", capabilityKey: "orderbook", title: "盘口/微观结构", summary: "深度、买卖档、成交摘要" },
  { scenarioId: "market.read_deep_analysis", domain: "market", capabilityKey: "technical", title: "深度分析", summary: "指标/形态教学性解读" },
  { scenarioId: "futures.read_funding", domain: "market", capabilityKey: "funding_rate", title: "资金费率", summary: "费率须基于查询结果" },
  { scenarioId: "research.rss_or_macro", domain: "research", capabilityKey: "macro", title: "宏观/简报", summary: "来源与时间须可见" },
  { scenarioId: "research.sentiment_and_news", domain: "research", capabilityKey: "sentiment", title: "舆情/新闻", summary: "情绪不等于买卖建议" },
  { scenarioId: "orders.read_activity", domain: "portfolio", capabilityKey: "orders", title: "委托/成交", summary: "私有读订单活动" },
  { scenarioId: "portfolio.read_pnl_exposure", domain: "portfolio", capabilityKey: "pnl", title: "盈亏/敞口", summary: "勿用现价冒充已实现盈亏" },
  { scenarioId: "wealth.holdings_read", domain: "wealth", capabilityKey: "holdings", title: "理财持仓", summary: "只读持仓/收益" },
  { scenarioId: "wealth.recommend", domain: "wealth", capabilityKey: "recommend", title: "理财推荐", summary: "只读推荐/排序" },
  { scenarioId: "monitoring.price_condition", domain: "monitoring", capabilityKey: "price_alert", title: "到价/条件监控", summary: "标的+阈值+方向可复述" },
  { scenarioId: "monitoring.scheduled_pull", domain: "monitoring", capabilityKey: "scheduled", title: "定时 Pull", summary: "频率与范围澄清" },
  { scenarioId: "monitoring.event_trigger", domain: "monitoring", capabilityKey: "event", title: "事件触发", summary: "触发条件与通知方式" },
];

export const ANALYSIS_CAPABILITY_SCENARIO_IDS = ANALYSIS_CAPABILITY_REGISTRY.map((r) => r.scenarioId);

export function isAnalysisCapabilityScenario(scenarioId: string): boolean {
  return ANALYSIS_CAPABILITY_SCENARIO_IDS.includes(scenarioId);
}

export function skillSpecRefForTradingSpec(spec: ExtendedPackSpec): string {
  return skillRef(spec.skillId);
}
