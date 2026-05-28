/**
 * A 类写技能 · 演示控制台单源（须与 manifest.yaml + trade-assistance §4/§8.2 同窗）。
 * 改 manifest 时同步更新 SKILL_REGISTRY_ENTRIES。
 */

import type { ToolRegistryRow } from "../../data/toolRegistryTypes";
import {
  operationBrief,
  parseSkillOperationView,
  type SkillOperationView,
} from "./parseSkillOperationView";
import { getSkillMarkdownFromBundle } from "./skillRegistryMarkdown";

export type SkillRegistryEntry = {
  skillId: string;
  summary: string;
  /** 用户侧流程（产品文案，非文档路径） */
  userFlow: string;
  /** 交易所写操作说明（产品文案） */
  exchangeAction: string;
  specPath: string | null;
  publishRequired: boolean;
  matrixStatus: ToolRegistryRow["matrixStatus"];
  defaultEnabled: boolean;
  /** 无 Git 正文时的登记版本（如 oco / bracket） */
  fallbackSkillSpecVersion?: string;
  specNote?: string;
};

/** 与 specs/requirements/skill-specs/manifest.yaml 同序、同 skillId */
export const SKILL_REGISTRY_ENTRIES: SkillRegistryEntry[] = [
  {
    skillId: "skill.spot.flash_convert",
    summary: "现货市价 / 闪兑",
    userFlow: "用户说明买/卖币种与金额 → 确认无杠杆相关表述 → 二次确认 → 按市价或闪兑成交",
    exchangeAction: "币币市价或闪兑下单（不设委托价）",
    specPath: "spot/skill.spot.flash_convert.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.spot.limit_order",
    summary: "现货限价",
    userFlow: "收集交易对、方向、限价与数量 → 展示限价确认信息 → 用户确认后挂单",
    exchangeAction: "币币限价挂单；改单须先撤单再挂新单",
    specPath: "spot/skill.spot.limit_order.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.spot.amend_limit_order",
    summary: "现货限价 · 逻辑改单",
    userFlow: "确认原单与新参数 → 一次二次确认 → 先撤原单再挂新限价单",
    exchangeAction: "先撤销原限价单，再挂新的限价单",
    specPath: "spot/skill.spot.amend_limit_order.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.spot.oco",
    summary: "现货 OCO",
    userFlow: "本阶段不在对话内提供 OCO 下单闭环",
    exchangeAction: "对话内暂不支持下单",
    specPath: null,
    publishRequired: false,
    matrixStatus: "tbd",
    defaultEnabled: false,
    fallbackSkillSpecVersion: "0.1.0-draft",
    specNote: "仅作备案；请引导用户前往主站，或分步说明如何自行操作",
  },
  {
    skillId: "skill.spot.bracket",
    summary: "现货 Bracket",
    userFlow: "本阶段不在对话内提供 Bracket 下单闭环",
    exchangeAction: "对话内暂不支持下单",
    specPath: null,
    publishRequired: false,
    matrixStatus: "tbd",
    defaultEnabled: false,
    fallbackSkillSpecVersion: "0.1.0-draft",
    specNote: "仅作备案；请引导用户前往主站，或分步说明如何自行操作",
  },
  {
    skillId: "skill.futures.market_order",
    summary: "合约市价",
    userFlow: "确认合约、方向、数量与杠杆相关说明 → 二次确认 → 永续/合约市价开仓或平仓",
    exchangeAction: "合约市价下单",
    specPath: "futures/skill.futures.market_order.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.futures.limit_order",
    summary: "合约限价",
    userFlow: "收集合约、方向、限价与张数 → 展示合约限价确认信息 → 用户确认后挂单",
    exchangeAction: "合约限价挂单",
    specPath: "futures/skill.futures.limit_order.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.futures.amend_limit_order",
    summary: "合约限价 · 逻辑改单",
    userFlow: "一次二次确认覆盖撤单与新挂单，中间不再重复确认",
    exchangeAction: "先撤原单，再挂新的合约限价单",
    specPath: "futures/skill.futures.amend_limit_order.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.futures.take_profit_stop",
    summary: "止盈止损 / 条件离场",
    userFlow: "区分即时开仓与条件离场 → 澄清触发价与方向 → 展示条件单确认信息",
    exchangeAction: "条件单（止盈止损等，以交易所实际支持为准）",
    specPath: "futures/skill.futures.take_profit_stop.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.margin.cross_market_order",
    summary: "全仓杠杆 · 市价",
    userFlow: "识别借币/全仓语境 → 说明风险与杠杆 → 必要时双重确认 → 市价下单",
    exchangeAction: "全仓杠杆市价下单",
    specPath: "margin/skill.margin.cross_market_order.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.margin.cross_limit_order",
    summary: "全仓杠杆 · 限价",
    userFlow: "全仓限价参数齐备 → 展示全仓限价确认信息 → 用户确认后挂单",
    exchangeAction: "全仓杠杆限价挂单",
    specPath: "margin/skill.margin.cross_limit_order.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.margin.transfer_spot_to_cross",
    summary: "现货↔全仓划转",
    userFlow: "引导用户前往主站完成划转，对话内不代办",
    exchangeAction: "须在主站完成划转",
    specPath: null,
    publishRequired: false,
    matrixStatus: "tbd",
    defaultEnabled: false,
    specNote: "对话内不提供划转；请引导用户前往主站操作",
  },
  {
    skillId: "skill.wealth.subscribe",
    summary: "理财申购",
    userFlow: "澄清产品、金额与期限 → 高风险二次确认 → 提交申购",
    exchangeAction: "理财申购；不支持时引导用户前往主站",
    specPath: "wealth/skill.wealth.subscribe.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
  {
    skillId: "skill.wealth.redeem",
    summary: "理财赎回",
    userFlow: "确认份额与产品 → 二次确认 → 提交赎回",
    exchangeAction: "理财赎回",
    specPath: "wealth/skill.wealth.redeem.md",
    publishRequired: true,
    matrixStatus: "frozen",
    defaultEnabled: true,
  },
];

const BY_SKILL_ID = new Map(SKILL_REGISTRY_ENTRIES.map((e) => [e.skillId, e]));

export function getSkillRegistryEntry(skillId: string): SkillRegistryEntry | undefined {
  return BY_SKILL_ID.get(skillId);
}

type MarkdownLoader = (relPath: string) => string | undefined;

let diskLoader: MarkdownLoader | undefined;

/** Vitest 专用：在 import `toolRegistryMock` 之前注册磁盘加载器 */
export function setSkillMarkdownDiskLoader(loader: MarkdownLoader | undefined): void {
  diskLoader = loader;
}

export function getSkillMarkdown(relPath: string): string | undefined {
  return getSkillMarkdownFromBundle(relPath) ?? diskLoader?.(relPath);
}

export function parseSkillSpecVersionFromBody(body: string): string | undefined {
  const m = body.match(/\|\s*\*\*`skillSpecVersion`\*\*\s*\|\s*`([^`]+)`\s*\|/);
  return m?.[1];
}

export function resolveSkillSpecVersion(skillId: string): string | undefined {
  const entry = getSkillRegistryEntry(skillId);
  if (!entry) return undefined;
  if (entry.specPath) {
    const body = getSkillMarkdown(entry.specPath);
    if (body) {
      const fromMd = parseSkillSpecVersionFromBody(body);
      if (fromMd) return fromMd;
    }
  }
  return entry.fallbackSkillSpecVersion;
}

export type SkillContractStatus = "complete" | "missing" | "n/a";

export function parseContractStatus(body: string): "complete" | "missing" {
  if (!body.includes("contract-complete")) return "missing";
  const sections = [
    "## 1. Required",
    "## 2. Validation",
    "## 3. Confirmation",
    "## 4. UNKNOWN",
    "## 5. Refusal",
    "## 6. API",
  ];
  return sections.every((s) => body.includes(s)) ? "complete" : "missing";
}

export function resolveSkillContractStatus(skillId: string): SkillContractStatus {
  const entry = getSkillRegistryEntry(skillId);
  if (!entry?.specPath) return "n/a";
  const body = getSkillMarkdown(entry.specPath);
  if (!body) return "missing";
  return parseContractStatus(body);
}

export function countPublishReadySpecs(): { complete: number; publishRequired: number } {
  const pub = SKILL_REGISTRY_ENTRIES.filter((e) => e.publishRequired);
  const complete = pub.filter((e) => resolveSkillContractStatus(e.skillId) === "complete").length;
  return { complete, publishRequired: pub.length };
}

export function resolveSkillOperationView(skillId: string): SkillOperationView | null {
  const entry = getSkillRegistryEntry(skillId);
  if (!entry?.specPath) return null;
  const body = getSkillMarkdown(entry.specPath);
  if (!body) return null;
  return parseSkillOperationView(body);
}

export function resolveOperationBrief(skillId: string): string {
  const view = resolveSkillOperationView(skillId);
  if (view) return operationBrief(view);
  const entry = getSkillRegistryEntry(skillId);
  return entry?.specNote ?? "—";
}

/** 合成 A 类表行（产品字段 + 规范版本） */
export function buildSkillRegistryRows(): ToolRegistryRow[] {
  return SKILL_REGISTRY_ENTRIES.map((e) => ({
    stableId: e.skillId,
    entryClass: "A" as const,
    summary: e.summary,
    userFlow: e.userFlow,
    exchangeAction: e.exchangeAction,
    anchor: e.exchangeAction,
    skillSpecVersion: resolveSkillSpecVersion(e.skillId),
    matrixStatus: e.matrixStatus,
    defaultEnabled: e.defaultEnabled,
  }));
}
