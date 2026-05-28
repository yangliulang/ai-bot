/**
 * 演示用 Registry 镜像：与 trade-assistance §4·§8 骨架同窗，非第二真源。
 * 生产须与文档 MR + DB 幂等（ADR-002 / CC-P1-03）。
 */

export type { RegistryEntryClass, ToolRegistryRow } from "./toolRegistryTypes";

import type { ToolRegistryRow } from "./toolRegistryTypes";
import { buildSkillRegistryRows } from "../pages/tools/skillRegistryCatalog";

/** A 类写 — 单源 skillRegistryCatalog（§4/§8.2 + manifest + Git 规范版本） */
export const MOCK_SKILL_REGISTRY_ROWS: ToolRegistryRow[] = buildSkillRegistryRows();

/** B 类摘录 — trade-assistance §8.3 */
export const MOCK_TOOL_B_ROWS: ToolRegistryRow[] = [
  {
    stableId: "tool.market.ticker",
    entryClass: "B",
    summary: "实时价量摘要",
    anchor: "查询交易对实时价格与成交量",
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    stableId: "tool.analytics.symbol_deep_dive",
    entryClass: "B",
    summary: "K 线/深度 + 解读",
    anchor: "K 线、深度与行情解读",
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    stableId: "tool.market.orderbook",
    entryClass: "B",
    summary: "盘口",
    anchor: "查询买卖盘口",
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    stableId: "tool.orders.open_orders",
    entryClass: "B",
    summary: "在途委托",
    anchor: "查询当前在途委托",
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    stableId: "tool.account.risk_snapshot",
    entryClass: "B",
    summary: "保证金/风险快照",
    anchor: "查询保证金与风险概况",
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
];

/** C 类摘录 — trade-assistance §8.4 */
export const MOCK_TOOL_C_ROWS: ToolRegistryRow[] = [
  {
    stableId: "tool.web.search",
    entryClass: "C",
    summary: "外网检索",
    anchor: "合规外网检索（默认关闭）",
    matrixStatus: "draft",
    defaultEnabled: false,
  },
  {
    stableId: "tool.web.news_search",
    entryClass: "C",
    summary: "新闻检索",
    anchor: "合规新闻检索（默认关闭）",
    matrixStatus: "draft",
    defaultEnabled: false,
  },
  {
    stableId: "tool.i18n.translate",
    entryClass: "C",
    summary: "翻译",
    anchor: "多语言翻译（受配额限制）",
    matrixStatus: "draft",
    defaultEnabled: true,
  },
];

export const TOOL_REGISTRY_SSOT_HINT =
  "清单与线上配置以产品规格为准；本页为预览，启用状态仅保存在当前浏览器。";
