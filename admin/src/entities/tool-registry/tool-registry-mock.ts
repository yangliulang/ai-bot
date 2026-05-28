/**
 * 作者: Cursor Agent
 * 日期: 2026-05-26
 * 修改功能: B/C 类工具登记演示数据（对齐 product-doc toolRegistryMock）
 */

import type { SkillMatrixStatus } from '@/entities/tool-registry/skill-registry-catalog'

export type RegistryEntryClass = 'A' | 'B' | 'C'

export interface ToolRegistryRow {
  stableId: string
  entryClass: RegistryEntryClass
  summary: string
  anchor: string
  userFlow?: string
  exchangeAction?: string
  skillSpecVersion?: string
  matrixStatus: SkillMatrixStatus
  defaultEnabled: boolean
}

export const MOCK_TOOL_B_ROWS: ToolRegistryRow[] = [
  {
    stableId: 'tool.market.ticker',
    entryClass: 'B',
    summary: '实时价量摘要',
    anchor: '查询交易对实时价格与成交量',
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    stableId: 'tool.analytics.symbol_deep_dive',
    entryClass: 'B',
    summary: 'K 线/深度 + 解读',
    anchor: 'K 线、深度与行情解读',
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    stableId: 'tool.market.orderbook',
    entryClass: 'B',
    summary: '盘口',
    anchor: '查询买卖盘口',
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    stableId: 'tool.orders.open_orders',
    entryClass: 'B',
    summary: '在途委托',
    anchor: '查询当前在途委托',
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
  {
    stableId: 'tool.account.risk_snapshot',
    entryClass: 'B',
    summary: '保证金/风险快照',
    anchor: '查询保证金与风险概况',
    matrixStatus: 'frozen',
    defaultEnabled: true,
  },
]

export const MOCK_TOOL_C_ROWS: ToolRegistryRow[] = [
  {
    stableId: 'tool.web.search',
    entryClass: 'C',
    summary: '外网检索',
    anchor: '合规外网检索（默认关闭）',
    matrixStatus: 'draft',
    defaultEnabled: false,
  },
  {
    stableId: 'tool.web.news_search',
    entryClass: 'C',
    summary: '新闻检索',
    anchor: '合规新闻检索（默认关闭）',
    matrixStatus: 'draft',
    defaultEnabled: false,
  },
  {
    stableId: 'tool.i18n.translate',
    entryClass: 'C',
    summary: '翻译',
    anchor: '多语言翻译（受配额限制）',
    matrixStatus: 'draft',
    defaultEnabled: false,
  },
]
