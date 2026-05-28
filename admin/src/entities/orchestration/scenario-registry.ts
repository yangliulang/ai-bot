/**
 * 与路线图 §1.3 核心 scenarioId 及编排寄存器叙事对齐的只读快照（首阶段 Demo）
 * 日期: 2026-05-18 — **`trade.spot.open_orders`** / **`trade.spot.cancel_order`**（FE_HANDOFF · 运营过滤器对齐）
 * 日期: 2026-05-14 — 纳入 **`read.market.depth`** / **`read.market.trades`**（FE_HANDOFF）
 */
export type ScenarioCategory = 'read' | 'trade' | 'margin' | 'wealth' | 'automation' | 'chat'

export type ClosureStatus = 'FROZEN' | 'TBD' | 'PLACEHOLDER'

export interface ScenarioRegistryEntry {
  scenarioId: string
  category: ScenarioCategory
  scenarioTitle: string
  flowSummary: string
  riskLevel: 'low' | 'medium' | 'high'
  closureStatus: ClosureStatus
}

export const ORCHESTRATION_VERSION_DISPLAY = '2026.05-orc-v1'

/** 路线图 1.3 + 交易所能力矩阵（节选） */
export const ROUTE_PHASE1_SCENARIOS: ScenarioRegistryEntry[] = [
  {
    scenarioId: 'read.market.ticker',
    category: 'read',
    scenarioTitle: '行情查询',
    flowSummary: '意图识别 → 读行情 → 返回摘要',
    riskLevel: 'low',
    closureStatus: 'FROZEN',
  },
  {
    scenarioId: 'read.market.depth',
    category: 'read',
    scenarioTitle: '盘口深度',
    flowSummary: '托管绑定 → GET /sapi/v2/depth · exchangeReadPreview（asks/bids）',
    riskLevel: 'low',
    closureStatus: 'FROZEN',
  },
  {
    scenarioId: 'read.market.trades',
    category: 'read',
    scenarioTitle: '近期成交',
    flowSummary: '托管绑定 → GET /sapi/v2/trades · exchangeReadPreview（items）',
    riskLevel: 'low',
    closureStatus: 'FROZEN',
  },
  {
    scenarioId: 'read.account.balance',
    category: 'read',
    scenarioTitle: '账户余额查询',
    flowSummary: '鉴权子账户 → 读余额',
    riskLevel: 'low',
    closureStatus: 'FROZEN',
  },
  {
    scenarioId: 'trade.spot.flash_convert',
    category: 'trade',
    scenarioTitle: '现货闪兑',
    flowSummary: '澄清参数 → 类型 A 确认 → 闪兑下单',
    riskLevel: 'high',
    closureStatus: 'FROZEN',
  },
  {
    scenarioId: 'trade.spot.limit_order',
    category: 'trade',
    scenarioTitle: '现货限价单',
    flowSummary: '定价与数量 → 确认 → 挂单',
    riskLevel: 'high',
    closureStatus: 'FROZEN',
  },
  {
    scenarioId: 'trade.spot.open_orders',
    category: 'trade',
    scenarioTitle: '现货当前委托',
    flowSummary: '托管绑定 → GET /sapi/v2/openOrders · orders[]',
    riskLevel: 'medium',
    closureStatus: 'FROZEN',
  },
  {
    scenarioId: 'trade.spot.cancel_order',
    category: 'trade',
    scenarioTitle: '现货撤单',
    flowSummary: 'symbol + orderId / clientOrderId → POST /sapi/v2/cancel · 时间线 cancel_order',
    riskLevel: 'high',
    closureStatus: 'FROZEN',
  },
  {
    scenarioId: 'trade.futures.market_order',
    category: 'trade',
    scenarioTitle: '合约市价',
    flowSummary: '杠杆/方向 → 确认 → 下单',
    riskLevel: 'high',
    closureStatus: 'TBD',
  },
  {
    scenarioId: 'trade.futures.limit_order',
    category: 'trade',
    scenarioTitle: '合约限价',
    flowSummary: '限价参数 → 确认 → 挂单',
    riskLevel: 'high',
    closureStatus: 'TBD',
  },
  {
    scenarioId: 'margin.cross.market_order',
    category: 'margin',
    scenarioTitle: '全仓杠杆市价',
    flowSummary: '全仓上下文 → 确认 → 下单',
    riskLevel: 'high',
    closureStatus: 'TBD',
  },
  {
    scenarioId: 'wealth.holdings_read',
    category: 'wealth',
    scenarioTitle: '理财持仓查询',
    flowSummary: '只读理财资产与收益摘要',
    riskLevel: 'low',
    closureStatus: 'PLACEHOLDER',
  },
  {
    scenarioId: 'automation.condition_order',
    category: 'automation',
    scenarioTitle: '条件单创建',
    flowSummary: '触发条件 → 确认 → 创建条件单',
    riskLevel: 'medium',
    closureStatus: 'TBD',
  },
  {
    scenarioId: 'chat.faq',
    category: 'chat',
    scenarioTitle: '纯对话问答',
    flowSummary: '无交易所写路径',
    riskLevel: 'low',
    closureStatus: 'FROZEN',
  },
]

export function opsRuntimeStatusLabel(status: ClosureStatus): string {
  if (status === 'FROZEN') return '已启用'
  if (status === 'TBD') return '测试中'
  return '已暂停'
}