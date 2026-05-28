/**
 * Prompt 治理 · Demo 样例数据（运营可读 · 对齐 specs/requirements/prompts/）
 * SSOT 条文：prompts/library · routing-engine scenarioId · prompt-management 四层包
 */

import type {
  MockFewShotRow,
  MockPromptAuditRow,
  MockPromptPack,
  MockPromptPackDraft,
  MockPromptPackVersionHistoryRow,
} from "./types";
import {
  ANALYSIS_CAPABILITY_REGISTRY,
  EXTENDED_TRADING_PACK_SPECS,
  UNIFIED_ANALYSIS_PROMPT_PACK_ID,
  type ExtendedPackSpec,
  skillSpecRefForTradingSpec,
} from "./mockPromptDataCatalog";
import { PROMPT_BODY_BY_PACK_ID } from "./promptBodyTemplates";

export {
  ANALYSIS_CAPABILITY_REGISTRY,
  UNIFIED_ANALYSIS_PROMPT_PACK_ID,
} from "./mockPromptDataCatalog";

export const UNIFIED_ANALYSIS_PROMPT_PACK = {
  promptPackId: UNIFIED_ANALYSIS_PROMPT_PACK_ID,
  promptPackVersion: 1,
} as const;

export function isUnifiedAnalysisPromptPack(pack: MockPromptPack): boolean {
  return pack.promptPackId === UNIFIED_ANALYSIS_PROMPT_PACK_ID;
}

const GOV_REV = { pdr: "pdr-2026-05-10", spb: "spb-2026-05-10" };
const PUBLISHED_AT = "2026-05-10T11:00:00Z";

function buildExtendedTradingPack(spec: ExtendedPackSpec): MockPromptPack {
  const skillSpecRef = skillSpecRefForTradingSpec(spec);
  return {
    promptPackId: spec.promptPackId,
    kind: spec.kind,
    title: spec.title,
    currentVersion: 1,
    lockState: "PUBLISHED",
    scenarioId: spec.scenarioId,
    skillSpecRef,
    description: spec.description,
    updatedAt: PUBLISHED_AT,
    publishedAt: PUBLISHED_AT,
    hasDraft: false,
    publisher: spec.publisher ?? "editor.zhao@ex.co",
    contentHashShort: `sha256:ext…${spec.promptPackId.slice(-8)}`,
    placeholderDenylistRevision: GOV_REV.pdr,
    safetyPhraseBlocklistRevision: GOV_REV.spb,
    publishedWithPlaceholderDenylistRevision: GOV_REV.pdr,
    publishedWithSafetyPhraseBlocklistRevision: GOV_REV.spb,
    fewShotCount: spec.fewShotCount ?? 0,
    bodySizeKiBApprox: 4,
    targetModelFamily: spec.kind === "TRADING" ? "gpt-4.1-family" : "gpt-4.1-mini",
    safetyPhraseScanScope: spec.kind === "TRADING" ? "TRADING_BODY_FEWSHOT" : undefined,
    effectiveBodyPreview: spec.effectiveBodyPreview,
  };
}

const CORE_PROMPT_PACKS: MockPromptPack[] = [
  {
    promptPackId: "pp-system-core",
    kind: "SYSTEM",
    title: "系统内核（全局行为）",
    currentVersion: 1,
    lockState: "LOCKED",
    description: "全局 Identity 与行为原则；不含具体交易场景细则。",
    updatedAt: "2026-05-10T08:00:00Z",
    publishedAt: "2026-05-10T08:00:00Z",
    hasDraft: false,
    publisher: "ops-admin@ex.co",
    contentHashShort: "sha256:a1b2…core",
    placeholderDenylistRevision: "pdr-2026-05-10",
    safetyPhraseBlocklistRevision: "spb-2026-05-10",
    publishedWithPlaceholderDenylistRevision: "pdr-2026-05-10",
    publishedWithSafetyPhraseBlocklistRevision: "spb-2026-05-10",
    targetModelFamily: "gpt-4.1-family",
    bodySizeKiBApprox: 6,
    fewShotCount: 0,
    effectiveBodyPreview: "金融交易 Agent · 不猜测参数 · 先澄清再写 · 不伪造结果",
  },
  {
    promptPackId: "pp-runtime-clarify",
    kind: "SYSTEM",
    title: "澄清规则（运行时）",
    currentVersion: 1,
    lockState: "PUBLISHED",
    description: "参数不足时如何向用户提问；不含业务场景细则。",
    updatedAt: "2026-05-10T08:15:00Z",
    publishedAt: "2026-05-10T08:15:00Z",
    hasDraft: false,
    publisher: "ops-admin@ex.co",
    contentHashShort: "sha256:cl…rify",
    placeholderDenylistRevision: GOV_REV.pdr,
    safetyPhraseBlocklistRevision: GOV_REV.spb,
    publishedWithPlaceholderDenylistRevision: GOV_REV.pdr,
    publishedWithSafetyPhraseBlocklistRevision: GOV_REV.spb,
    targetModelFamily: "gpt-4.1-family",
    bodySizeKiBApprox: 2,
    fewShotCount: 0,
    effectiveBodyPreview: "缺参时指出缺失字段，不猜测 symbol/价格/数量",
  },
  {
    promptPackId: "pp-runtime-output-contract",
    kind: "SYSTEM",
    title: "输出契约（运行时）",
    currentVersion: 1,
    lockState: "PUBLISHED",
    description: "clarify / intent 结构化输出边界；不含 API 与 Schema 细节。",
    updatedAt: "2026-05-10T08:20:00Z",
    publishedAt: "2026-05-10T08:20:00Z",
    hasDraft: false,
    publisher: "ops-admin@ex.co",
    contentHashShort: "sha256:oc…tract",
    placeholderDenylistRevision: GOV_REV.pdr,
    safetyPhraseBlocklistRevision: GOV_REV.spb,
    publishedWithPlaceholderDenylistRevision: GOV_REV.pdr,
    publishedWithSafetyPhraseBlocklistRevision: GOV_REV.spb,
    targetModelFamily: "gpt-4.1-family",
    bodySizeKiBApprox: 2,
    fewShotCount: 0,
    effectiveBodyPreview: "缺参→clarify；齐备→intent；不混自然语言与 JSON",
  },
  {
    promptPackId: "pp-safety-global",
    kind: "SAFETY",
    title: "安全防护（全局）",
    currentVersion: 1,
    lockState: "PUBLISHED",
    description: "越狱、越权、违法与钓鱼类请求的拒答口径。",
    updatedAt: "2026-05-10T08:30:00Z",
    publishedAt: "2026-05-10T08:30:00Z",
    hasDraft: false,
    publisher: "approver.wang@ex.co",
    contentHashShort: "sha256:c3d4…safe",
    placeholderDenylistRevision: "pdr-2026-05-10",
    safetyPhraseBlocklistRevision: "spb-2026-05-10",
    publishedWithPlaceholderDenylistRevision: "pdr-2026-05-10",
    publishedWithSafetyPhraseBlocklistRevision: "spb-2026-05-10",
    fewShotCount: 0,
    bodySizeKiBApprox: 3,
    safetyPhraseScanScope: "FULL_PACK",
    effectiveBodyPreview: "安全与合规摘要：拒绝绕过确认、禁止假称已成交、违法请求短拒",
  },
  {
    promptPackId: "pp-trading-spot-limit",
    kind: "TRADING",
    title: "现货限价下单",
    currentVersion: 1,
    lockState: "PUBLISHED",
    scenarioId: "trade.spot.limit_order",
    skillSpecRef: "skill.spot.limit_order@0.1.0-mvp",
    description: "场景 trade.spot.limit_order · 现货限价认知与行为规则。",
    updatedAt: "2026-05-10T09:00:00Z",
    publishedAt: "2026-05-10T09:00:00Z",
    hasDraft: true,
    publisher: "editor.li@ex.co",
    contentHashShort: "sha256:e5f6…spot-lim",
    placeholderDenylistRevision: "pdr-2026-05-10",
    safetyPhraseBlocklistRevision: "spb-2026-05-10",
    publishedWithPlaceholderDenylistRevision: "pdr-2026-05-10",
    publishedWithSafetyPhraseBlocklistRevision: "spb-2026-05-10",
    fewShotCount: 2,
    bodySizeKiBApprox: 5,
    targetModelFamily: "gpt-4.1-family",
    safetyPhraseScanScope: "TRADING_BODY_FEWSHOT",
    effectiveBodyPreview: "须 symbol/side/quantity/price · 不猜价 · 确认前不下单",
  },
  {
    promptPackId: "pp-trading-spot-flash",
    kind: "TRADING",
    title: "现货闪兑/市价",
    currentVersion: 1,
    lockState: "PUBLISHED",
    scenarioId: "trade.spot.flash_convert",
    skillSpecRef: "skill.spot.flash_convert@0.1.0-mvp",
    description: "适用：现货闪兑或市价买卖。话术中不要求用户填写限价。",
    updatedAt: "2026-05-10T09:15:00Z",
    publishedAt: "2026-05-10T09:15:00Z",
    hasDraft: false,
    publisher: "editor.li@ex.co",
    contentHashShort: "sha256:f7a8…flash",
    placeholderDenylistRevision: "pdr-2026-05-10",
    safetyPhraseBlocklistRevision: "spb-2026-05-10",
    publishedWithPlaceholderDenylistRevision: "pdr-2026-05-10",
    publishedWithSafetyPhraseBlocklistRevision: "spb-2026-05-10",
    fewShotCount: 1,
    bodySizeKiBApprox: 4,
    targetModelFamily: "gpt-4.1-mini",
    safetyPhraseScanScope: "TRADING_BODY_FEWSHOT",
    effectiveBodyPreview: "市价/闪兑 · 禁止 limit price · 确认前不交易",
  },
  {
    promptPackId: "pp-trading-futures-market",
    kind: "TRADING",
    title: "合约市价开仓",
    currentVersion: 1,
    lockState: "PUBLISHED",
    scenarioId: "trade.futures.market_order",
    skillSpecRef: "skill.futures.market_order@0.1.0-mvp",
    description: "适用：合约市价开仓。须先风险说明与用户确认。",
    updatedAt: "2026-05-10T09:30:00Z",
    publishedAt: "2026-05-10T09:30:00Z",
    hasDraft: false,
    publisher: "editor.li@ex.co",
    contentHashShort: "sha256:b9c0…fut-mkt",
    placeholderDenylistRevision: "pdr-2026-05-10",
    safetyPhraseBlocklistRevision: "spb-2026-05-10",
    publishedWithPlaceholderDenylistRevision: "pdr-2026-05-10",
    publishedWithSafetyPhraseBlocklistRevision: "spb-2026-05-10",
    fewShotCount: 2,
    bodySizeKiBApprox: 5,
    targetModelFamily: "gpt-4.1-family",
    safetyPhraseScanScope: "TRADING_BODY_FEWSHOT",
    effectiveBodyPreview: "合约市价 · 高风险写操作 · 不自动加杠杆",
  },
  {
    promptPackId: "pp-trading-futures-limit",
    kind: "TRADING",
    title: "合约限价挂单",
    currentVersion: 1,
    lockState: "PUBLISHED",
    scenarioId: "trade.futures.limit_order",
    skillSpecRef: "skill.futures.limit_order@0.1.0-mvp",
    description: "场景 trade.futures.limit_order · 合约限价认知与行为规则。",
    updatedAt: "2026-05-10T09:45:00Z",
    publishedAt: "2026-05-10T09:45:00Z",
    hasDraft: false,
    publisher: "editor.chen@ex.co",
    contentHashShort: "sha256:d1e2…fut-lim",
    placeholderDenylistRevision: "pdr-2026-05-10",
    safetyPhraseBlocklistRevision: "spb-2026-05-10",
    publishedWithPlaceholderDenylistRevision: "pdr-2026-05-10",
    publishedWithSafetyPhraseBlocklistRevision: "spb-2026-05-10",
    fewShotCount: 1,
    bodySizeKiBApprox: 4,
    targetModelFamily: "gpt-4.1-family",
    safetyPhraseScanScope: "TRADING_BODY_FEWSHOT",
    effectiveBodyPreview: "合约限价 · 四要素齐备 · 确认前不下单",
  },
  {
    promptPackId: UNIFIED_ANALYSIS_PROMPT_PACK_ID,
    kind: "ANALYSIS",
    title: "分析对话（统一）",
    currentVersion: 1,
    lockState: "PUBLISHED",
    description: "统一分析场景：只读、基于数据、不代为下单；能力由对话上下文提供。",
    updatedAt: "2026-05-10T10:00:00Z",
    publishedAt: "2026-05-10T10:00:00Z",
    hasDraft: false,
    publisher: "editor.zhao@ex.co",
    contentHashShort: "sha256:an…core",
    placeholderDenylistRevision: "pdr-2026-05-10",
    safetyPhraseBlocklistRevision: "spb-2026-05-10",
    publishedWithPlaceholderDenylistRevision: "pdr-2026-05-10",
    publishedWithSafetyPhraseBlocklistRevision: "spb-2026-05-10",
    fewShotCount: 2,
    bodySizeKiBApprox: 5,
    targetModelFamily: "gpt-4.1-mini",
    effectiveBodyPreview: "分析场景 · 不写操作 · 有数据再说 · 不代为下单",
  },
];

const EXTENDED_TRADING_PACKS = EXTENDED_TRADING_PACK_SPECS.map(buildExtendedTradingPack);

/** 已发布包：SYSTEM/SAFETY + 统一 ANALYSIS + TRADING 写路径（按 scenario 拆） */
export const mockPromptPacks: MockPromptPack[] = [...CORE_PROMPT_PACKS, ...EXTENDED_TRADING_PACKS];

const PROMPT_PACK_VERSION_HISTORY: Record<string, MockPromptPackVersionHistoryRow[]> = {
  "pp-system-core": [
    {
      promptPackVersion: 1,
      publishedAt: "2026-05-10T08:00:00Z",
      actor: "ops-admin@ex.co",
      event: "PUBLISH",
      summary: "初版 SYSTEM 全局行为（Identity + Behavioral Rules）",
    },
  ],
  "pp-runtime-clarify": [
    {
      promptPackVersion: 1,
      publishedAt: "2026-05-10T08:15:00Z",
      actor: "ops-admin@ex.co",
      event: "PUBLISH",
      summary: "澄清规则（Clarify Rules）",
    },
  ],
  "pp-runtime-output-contract": [
    {
      promptPackVersion: 1,
      publishedAt: "2026-05-10T08:20:00Z",
      actor: "ops-admin@ex.co",
      event: "PUBLISH",
      summary: "输出契约（Output Contract）",
    },
  ],
  "pp-safety-global": [
    {
      promptPackVersion: 1,
      publishedAt: "2026-05-10T08:30:00Z",
      actor: "approver.wang@ex.co",
      event: "PUBLISH",
      summary: "初版 SAFETY 全局块",
    },
  ],
  "pp-trading-spot-limit": [
    {
      promptPackVersion: 1,
      publishedAt: "2026-05-10T09:00:00Z",
      actor: "editor.li@ex.co",
      event: "PUBLISH",
      summary: "现货限价场景叙事 v1",
    },
  ],
  "pp-trading-spot-flash": [
    {
      promptPackVersion: 1,
      publishedAt: "2026-05-10T09:15:00Z",
      actor: "editor.li@ex.co",
      event: "PUBLISH",
      summary: "现货闪兑场景叙事 v1",
    },
  ],
  "pp-trading-futures-market": [
    {
      promptPackVersion: 1,
      publishedAt: "2026-05-10T09:30:00Z",
      actor: "editor.li@ex.co",
      event: "PUBLISH",
      summary: "合约市价场景叙事 v1",
    },
  ],
  "pp-trading-futures-limit": [
    {
      promptPackVersion: 1,
      publishedAt: "2026-05-10T09:45:00Z",
      actor: "editor.chen@ex.co",
      event: "PUBLISH",
      summary: "合约限价场景叙事 v1",
    },
  ],
  [UNIFIED_ANALYSIS_PROMPT_PACK_ID]: [
    {
      promptPackVersion: 1,
      publishedAt: "2026-05-10T10:00:00Z",
      actor: "editor.zhao@ex.co",
      event: "PUBLISH",
      summary: "统一 ANALYSIS 包 v1（只读分析纪律）",
    },
  ],
  ...Object.fromEntries(
    EXTENDED_TRADING_PACK_SPECS.map((s) => [
      s.promptPackId,
      [
        {
          promptPackVersion: 1,
          publishedAt: PUBLISHED_AT,
          actor: s.publisher ?? "editor.zhao@ex.co",
          event: "PUBLISH" as const,
          summary: `${s.title} · ${s.scenarioId} v1`,
        },
      ],
    ]),
  ),
};

const DEFAULT_FIXTURE = `{
  "messages": [
    { "role": "user", "content": "帮我看一下 BTCUSDT 现在大概什么价" }
  ],
  "variables": { "symbol": "BTCUSDT" }
}`;

function defaultVariableSchema(kind: MockPromptPack["kind"]): string {
  if (kind === "TRADING") {
    return `{
  "type": "object",
  "properties": {
    "symbol": { "type": "string" },
    "quantity": { "type": "string" },
    "price": { "type": "string" },
    "side": { "type": "string" }
  },
  "required": ["symbol"]
}`;
  }
  if (kind === "ANALYSIS") {
    return `{
  "type": "object",
  "properties": {
    "symbol": { "type": "string" },
    "interval": { "type": "string" }
  }
}`;
  }
  return `{
  "type": "object",
  "properties": {
    "effective_locale": { "type": "string" },
    "operator_region": { "type": "string" }
  }
}`;
}

function seedFewShots(pack: MockPromptPack): MockFewShotRow[] {
  const n = pack.fewShotCount ?? 0;
  if (n <= 0) return [];

  const byPack: Record<string, MockFewShotRow[]> = {
    "pp-trading-spot-limit": [
      {
        id: "fs-spot-1",
        role: "user",
        content: "BTCUSDT 限价买 0.01，价格 95000",
      },
      {
        id: "fs-spot-2",
        role: "assistant",
        content: "收到。我会先汇总订单摘要并请您在确认卡上确认，确认后才会提交下单。",
      },
    ],
    "pp-trading-spot-flash": [
      {
        id: "fs-flash-1",
        role: "user",
        content: "用市价卖一点 ETH",
      },
      {
        id: "fs-flash-2",
        role: "assistant",
        content: "好的。请先确认交易对与数量；您确认后我才会继续市价/闪兑流程。",
      },
    ],
    "pp-trading-futures-market": [
      {
        id: "fs-fut-m-1",
        role: "user",
        content: "开多 BTCUSDT 永续，市价 100U",
      },
      {
        id: "fs-fut-m-2",
        role: "assistant",
        content: "合约市价属于高风险写操作。我会先说明风险要点并请您确认，确认后再继续。",
      },
    ],
    "pp-trading-futures-limit": [
      {
        id: "fs-fut-l-1",
        role: "user",
        content: "挂个空单，价格 68000，0.01 张",
      },
      {
        id: "fs-fut-l-2",
        role: "assistant",
        content: "请确认合约、方向、价格与数量是否无误；确认后才会提交限价单。",
      },
    ],
    [UNIFIED_ANALYSIS_PROMPT_PACK_ID]: [
      {
        id: "fs-q-1",
        role: "user",
        content: "BTC 现在多少钱？",
      },
      {
        id: "fs-q-2",
        role: "assistant",
        content: "我先查询行情数据。拿到结果后会给出价格并注明来源与时效；这不构成投资建议。",
      },
    ],
    "pp-trading-spot-amend": [
      { id: "fs-am-1", role: "user", content: "把刚才那个限价单价格改成 94000" },
      {
        id: "fs-am-2",
        role: "assistant",
        content: "好的。我先确认是哪一笔订单，再展示改单摘要请您确认。",
      },
    ],
    "pp-trading-futures-tpsl": [
      { id: "fs-tp-1", role: "user", content: "给多单设止盈 72000 止损 68000" },
      {
        id: "fs-tp-2",
        role: "assistant",
        content: "我会汇总条件单参数并走风险说明与确认，确认后才会提交。",
      },
    ],
    "pp-trading-wealth-subscribe": [
      { id: "fs-ws-1", role: "user", content: "申购 5000U 那个稳健理财" },
      {
        id: "fs-ws-2",
        role: "assistant",
        content: "我先确认产品名称与金额，并说明风险要点，随后请您在确认卡上确认。",
      },
    ],
  };

  const preset = byPack[pack.promptPackId];
  if (preset) return preset.slice(0, n);

  return [
    {
      id: "fs-default-1",
      role: "user" as const,
      content: "示例用户话术",
    },
  ].slice(0, n);
}

export function getPromptPack(promptPackId: string): MockPromptPack | undefined {
  return mockPromptPacks.find((p) => p.promptPackId === promptPackId);
}

export function getPromptPackVersionHistory(promptPackId: string): MockPromptPackVersionHistoryRow[] {
  return PROMPT_PACK_VERSION_HISTORY[promptPackId] ?? [];
}

export function buildPromptPackDraft(pack: MockPromptPack): MockPromptPackDraft {
  const body =
    PROMPT_BODY_BY_PACK_ID[pack.promptPackId] ??
    (pack.effectiveBodyPreview ?? "# 正文待运营录入\n\n<!-- 单包 ≤256KiB -->");
  return {
    promptPackId: pack.promptPackId,
    etag: pack.contentHashShort ?? '"demo-etag-1"',
    bodyMarkdown: body,
    fewShots: seedFewShots(pack),
    variableSchemaJson: defaultVariableSchema(pack.kind),
    sandboxFixtureJson: DEFAULT_FIXTURE,
  };
}

export function getPromptPackDraft(promptPackId: string): MockPromptPackDraft | undefined {
  const pack = getPromptPack(promptPackId);
  if (!pack) return undefined;
  return buildPromptPackDraft(pack);
}

const PROMPT_AUDIT_TAIL: Record<string, MockPromptAuditRow[]> = {
  "pp-system-core": [
    {
      at: "2026-05-10T08:00:01Z",
      actor: "ops-admin@ex.co",
      action: "PROMPT_PUBLISHED",
      detail: "SYSTEM v1 发布并锁定",
    },
  ],
  "pp-trading-spot-limit": [
    {
      at: "2026-05-10T09:05:00Z",
      actor: "editor.li@ex.co",
      action: "PROMPT_DRAFT_SAVED",
      detail: "Few-shot 微调（未发布）",
    },
    {
      at: "2026-05-10T09:00:01Z",
      actor: "editor.li@ex.co",
      action: "PROMPT_PUBLISHED",
      detail: "TRADING v1 生效",
    },
  ],
};

export function getPromptAuditTail(promptPackId: string): MockPromptAuditRow[] {
  return PROMPT_AUDIT_TAIL[promptPackId] ?? [];
}

function buildScenarioPromptPackMap(): Record<string, { promptPackId: string; promptPackVersion: number }> {
  const map: Record<string, { promptPackId: string; promptPackVersion: number }> = {};

  for (const p of mockPromptPacks) {
    if (p.kind !== "TRADING" || !p.scenarioId?.trim() || p.currentVersion == null) continue;
    if (p.lockState === "DRAFT" && !p.publishedAt) continue;
    map[p.scenarioId] = { promptPackId: p.promptPackId, promptPackVersion: p.currentVersion };
  }

  for (const cap of ANALYSIS_CAPABILITY_REGISTRY) {
    map[cap.scenarioId] = { ...UNIFIED_ANALYSIS_PROMPT_PACK };
  }

  const tpsl = map["trade.futures.take_profit_stop"];
  if (tpsl) {
    map["futures.condition.order_create"] = { ...tpsl };
  }
  return map;
}

/** scenarioId → 默认策略包（编排/执行详情 Demo） */
export const MOCK_SCENARIO_PROMPT_PACK = buildScenarioPromptPackMap();

export const MOCK_SYSTEM_PROMPT_PACK = { promptPackId: "pp-system-core", promptPackVersion: 1 };
export const MOCK_RUNTIME_CLARIFY_PACK = { promptPackId: "pp-runtime-clarify", promptPackVersion: 1 };
export const MOCK_RUNTIME_OUTPUT_CONTRACT_PACK = {
  promptPackId: "pp-runtime-output-contract",
  promptPackVersion: 1,
};
export const MOCK_SAFETY_PROMPT_PACK = { promptPackId: "pp-safety-global", promptPackVersion: 1 };
