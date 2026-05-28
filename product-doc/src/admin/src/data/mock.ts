import {
  buildDefaultResolvedPromptBinding,
  ensureWritePathObservabilityTimeline,
} from "../productionRuntime/promptBindingTimeline";
import {
  buildBillingBlockedTimeline,
  buildDemoObsTimeline,
  buildWritePathRunningTimeline,
  resolvedPromptBindingForDemo,
} from "./mockObsTimeline";
export {
  lookupBillingCorrelate,
  mockBillingLedger,
  mockObsBilling,
} from "./mockBillingData";
import type {
  AgentTemplate,
  AgentInstance,
  AgentInstanceAuditRow,
  Appendix82Summary,
  TemplateVersionHistoryEntry,
  MockProvider,
  MockModel,
  DependencyHealth,
  MockBillingHealth,
  MockBillingRuntimeOverview,
  MockBillingGatewayError,
  MockCommercePhase2AdminSnapshot,
  MockRolloutRule,
  MockWhitelistEntry,
  MockUserBan,
  MockKycMirror,
  MockMembershipVipLevel,
  MockObsExecutionRow,
  MockObsToolRow,
  MockObsLlmRow,
  MockObsAuditRow,
  MockRuntimeTask,
  MockRuntimeEventRow,
} from "./types";
import { ORCHESTRATION_VERSION_DISPLAY } from "./orchestrationConstants";

export const mockTemplates: AgentTemplate[] = [
  {
    templateId: "tmpl-spot-default",
    internalName: "现货·运营默认",
    displayName: "Coobit 现货 Agent",
    description: "现货交易辅助：行情解读、下单确认门、持仓与风险摘要；与全局护栏及子账户 scope 对签。",
    tags: ["spot", "trading"],
    publishedVersion: "14",
    enabled: true,
    promptSummary: "ok",
    toolSummary: "ok",
    modelSummary: "warn",
    updatedAt: "2026-05-06T08:12:00Z",
    templateStatus: "PUBLISHED",
    boundPromptPackRef: "pp-trading-spot-limit",
    boundPromptPackVersion: "12",
    toolProfileRef: "tp-spot-matrix-v2",
    defaultModelRef: "gpt-4.1-mini",
    riskProfileSummary: "价格偏离 80bps · symbol allowlist · 单用户净敞口上限 50k USDT（与交易智能体配置合并）",
    promptGateRevisionStale: true,
  },
  {
    templateId: "tmpl-futures-beta",
    internalName: "合约·内测",
    displayName: "合约交易（内测）",
    description: "合约场景内测模板；工具矩阵含 TBD 项时不允许发布。",
    tags: ["futures", "beta"],
    publishedVersion: null,
    enabled: false,
    promptSummary: "ok",
    toolSummary: "warn",
    modelSummary: "ok",
    updatedAt: "2026-05-04T02:00:00Z",
    templateStatus: "DRAFT",
    boundPromptPackRef: "pp-trading-futures-market",
    boundPromptPackVersion: "3",
    toolProfileRef: "tp-futures-partial",
    defaultModelRef: "gpt-4.1",
    riskProfileSummary: "合约杠杆上限与强平提示（草稿；待风控会签）",
    promptGateRevisionStale: false,
  },
];

/** 模板版本履历（配置 §2.3） */
export const mockTemplateVersionHistory: Record<string, TemplateVersionHistoryEntry[]> = {
  "tmpl-spot-default": [
    {
      templateVersion: "14",
      publishedAt: "2026-05-06T08:12:00Z",
      summary: "默认模型 gpt-4.1-mini；Prompt 包 v12",
      actor: "ops.admin",
    },
    {
      templateVersion: "13",
      publishedAt: "2026-04-18T14:20:00Z",
      summary: "工具画像 tp-spot-matrix-v2；价格偏离收紧 80bps",
      actor: "risk.admin",
    },
    {
      templateVersion: "12",
      publishedAt: "2026-03-01T09:00:00Z",
      summary: "首版矩阵冻结路径对齐",
      actor: "ops.admin",
    },
  ],
  "tmpl-futures-beta": [],
};

/** 实例维度审计（§3.2 审计 Tab） */
export const mockInstanceAudits: Record<string, AgentInstanceAuditRow[]> = {
  "inst-7a2f9c": [
    {
      at: "2026-05-07T00:10:00Z",
      actor: "ops.admin",
      action: "RUNTIME_RESUME",
      resource: "inst-7a2f9c",
    },
    {
      at: "2026-05-01T11:22:00Z",
      actor: "system",
      action: "INSTANCE_CREATED",
      resource: "inst-7a2f9c · tmpl-spot-default v14",
    },
  ],
  "inst-3b81d0": [
    {
      at: "2026-05-06T18:40:00Z",
      actor: "billing.job",
      action: "AGENT_STATE_BILLING_BLOCKED",
      resource: "inst-3b81d0",
    },
  ],
  "inst-9e4412": [],
  "inst-c91fba": [
    {
      at: "2026-03-28T00:05:00Z",
      actor: "system",
      action: "INSTANCE_CREATED",
      resource: "inst-c91fba · tmpl-spot-default v13",
    },
  ],
  "inst-d02ecc": [
    {
      at: "2026-05-06T11:58:00Z",
      actor: "ops.admin",
      action: "OPS_BATCH_SUSPEND",
      resource: "inst-d02ecc · batch bf-20260506-01",
    },
  ],
  "inst-e17fff": [
    {
      at: "2026-05-05T08:00:00Z",
      actor: "risk.bot",
      action: "TRADING_API_PROBE_FAILED",
      resource: "inst-e17fff",
    },
  ],
  "inst-f558aa": [
    {
      at: "2026-05-04T22:14:00Z",
      actor: "runtime",
      action: "RUNTIME_ERROR",
      resource: "inst-f558aa · exit 137",
    },
  ],
  "inst-a99001": [
    {
      at: "2026-05-03T06:00:00Z",
      actor: "system",
      action: "INSTANCE_CREATED",
      resource: "inst-a99001 · 待绑定",
    },
  ],
  "inst-g66301": [
    {
      at: "2026-05-07T02:01:00Z",
      actor: "ops.admin",
      action: "RUNTIME_START",
      resource: "inst-g66301",
    },
  ],
};

function appendix(
  agentState: AgentInstance["agentState"],
  reason: string,
  subId: string,
  extras?: Partial<Omit<Appendix82Summary, "agentState" | "lastProductBlockReason">>,
): Appendix82Summary {
  const base: Appendix82Summary = {
    vipTier: 3,
    agentMinVipTier: 2,
    agentSubAccountId: subId,
    agentSubAccountStatus: "ACTIVE",
    agentTradingApiBindingStatus: "BOUND",
    agentTradingApiKeyId: "key-***",
    agentState,
    lastProductBlockReason: reason,
  };
  return { ...base, ...extras, agentState, lastProductBlockReason: reason };
}

export const mockInstances: AgentInstance[] = [
  {
    instanceId: "inst-7a2f9c",
    userId: "u-10482",
    agentSubAccountUid: "881042991",
    telegramUsername: "@coolbit_trader_j",
    telegramNumericId: "612884729103",
    templateId: "tmpl-spot-default",
    templateDisplayName: "Coobit 现货 Agent",
    templateVersion: "14",
    agentState: "NORMAL",
    runtimeState: "RUNNING",
    subAccountStatus: "LINKED",
    lastProductBlockReason: "—",
    lastActiveAt: "2026-05-07T01:20:00Z",
    createdAt: "2026-04-01T00:00:00Z",
    createdByDisplay: "console_ops_zhang",
    appendix82: appendix("NORMAL", "—", "sub-acc-001"),
    instanceOverrides: {
      preferredLocale: "zh-CN",
      maxConcurrentOrders: 3,
    },
    bindingSnapshot: {
      lastBindVerifiedAt: "2026-05-07T00:45:00Z",
      tradingApiBindingRevision: "bind-rev-20260506T184001Z-u10482",
      bindEventRows: [
        {
          at: "2026-05-07T00:45:00Z",
          event: "BINDING_VERIFY_OK",
          detail: "§1.2 校验通过 · UID≡subUid",
        },
      ],
    },
  },
  /** 与 inst-7a2f9c 同一 userId：演示「每用户多实例」列表与筛选 */
  {
    instanceId: "inst-c91fba",
    userId: "u-10482",
    agentSubAccountUid: "881042992",
    telegramUsername: "@coolbit_trader_j",
    telegramNumericId: "612884729103",
    templateId: "tmpl-spot-default",
    templateDisplayName: "Coobit 现货 Agent",
    templateVersion: "13",
    agentState: "MEMBERSHIP_BLOCKED",
    runtimeState: "PAUSED",
    subAccountStatus: "LINKED",
    lastProductBlockReason: "母账号 vipTier=1 < agentMinVipTier=4 · MEMBERSHIP_BLOCKED",
    lastActiveAt: "2026-05-06T09:00:00Z",
    createdAt: "2026-03-28T00:00:00Z",
    createdByDisplay: "console_ops_zhang",
    appendix82: appendix("MEMBERSHIP_BLOCKED", "MEMBERSHIP_BLOCKED", "sub-acc-10482-alt", {
      vipTier: 1,
      agentMinVipTier: 4,
    }),
    instanceOverrides: {
      preferredLocale: "zh-CN",
    },
    bindingSnapshot: {
      lastBindVerifiedAt: "2026-03-28T00:18:00Z",
      tradingApiBindingRevision: "bind-rev-20260328T001800Z-u10482-alt",
      bindEventRows: [
        {
          at: "2026-03-28T00:18:00Z",
          event: "BINDING_VERIFY_OK",
          detail: "第二实例 · 幂等校验通过",
        },
      ],
    },
  },
  {
    instanceId: "inst-3b81d0",
    userId: "u-88301",
    agentSubAccountUid: "883019002",
    telegramUsername: "@alice_spot_dev",
    telegramNumericId: "5987654321",
    templateId: "tmpl-spot-default",
    templateDisplayName: "Coobit 现货 Agent",
    templateVersion: "14",
    agentState: "BILLING_BLOCKED",
    runtimeState: "PAUSED",
    subAccountStatus: "LINKED",
    lastProductBlockReason: "子账户 USDT 可用不足 · BILLING_BLOCKED",
    lastActiveAt: "2026-05-06T18:40:00Z",
    createdAt: "2026-03-15T00:00:00Z",
    createdByDisplay: "support_li",
    appendix82: appendix(
      "BILLING_BLOCKED",
      "BILLING_BLOCKED",
      "sub-acc-882",
    ),
    instanceOverrides: {
      preferredLocale: "zh-CN",
    },
    bindingSnapshot: {
      lastBindVerifiedAt: "2026-03-15T09:30:00Z",
      tradingApiBindingRevision: "bind-rev-20260315T093000Z-u88301",
      bindEventRows: [
        {
          at: "2026-03-15T09:30:00Z",
          event: "TRADING_API_BOUND",
          detail: "初次绑定成功",
        },
      ],
    },
  },
  {
    instanceId: "inst-d02ecc",
    userId: "u-55100",
    agentSubAccountUid: "551001001",
    telegramUsername: "@ops_sandbox_u",
    telegramNumericId: "6011223344",
    templateId: "tmpl-spot-default",
    templateDisplayName: "Coobit 现货 Agent",
    templateVersion: "14",
    agentState: "OPS_SUSPENDED",
    runtimeState: "PAUSED",
    subAccountStatus: "LINKED",
    lastProductBlockReason: "批次熔断 batchId=bf-20260506-01 · OPS_SUSPENDED",
    lastActiveAt: "2026-05-06T12:00:00Z",
    createdAt: "2026-02-10T00:00:00Z",
    createdByDisplay: "sandbox_automation",
    appendix82: appendix("OPS_SUSPENDED", "OPS_SUSPENDED", "sub-acc-551"),
    instanceOverrides: {},
    bindingSnapshot: {
      lastBindVerifiedAt: "2026-02-10T14:00:00Z",
      tradingApiBindingRevision: "bind-rev-20260210T140000Z-u55100",
      bindEventRows: [
        {
          at: "2026-05-06T11:58:00Z",
          event: "OPS_BATCH_SUSPEND",
          detail: "熔断批次 · Runtime Pause",
        },
      ],
    },
  },
  {
    instanceId: "inst-e17fff",
    userId: "u-66200",
    agentSubAccountUid: "662009876",
    telegramUsername: "@li_agent_cn",
    telegramNumericId: "628817263547",
    templateId: "tmpl-spot-default",
    templateDisplayName: "Coobit 现货 Agent",
    templateVersion: "14",
    agentState: "AGENT_SUBACCOUNT_BLOCKED",
    runtimeState: "PAUSED",
    subAccountStatus: "LINKED",
    lastProductBlockReason: "交易 API 吊销探测失败 · AGENT_SUBACCOUNT_BLOCKED",
    lastActiveAt: "2026-05-05T08:30:00Z",
    createdAt: "2026-01-22T00:00:00Z",
    createdByDisplay: "console_ops_wang",
    appendix82: appendix(
      "AGENT_SUBACCOUNT_BLOCKED",
      "AGENT_SUBACCOUNT_BLOCKED",
      "sub-acc-662",
      {
        agentSubAccountStatus: "API_REVOKED",
        agentTradingApiBindingStatus: "INVALID",
        agentTradingApiKeyId: null,
      },
    ),
    instanceOverrides: {},
    bindingSnapshot: {
      lastBindVerifiedAt: "2026-01-22T11:00:00Z",
      tradingApiBindingRevision: "bind-rev-20260122T110000Z-u66200",
      bindEventRows: [
        {
          at: "2026-05-05T08:00:00Z",
          event: "TRADING_API_PROBE_FAILED",
          detail: "探测失败 · INVALID",
        },
      ],
    },
  },
  {
    instanceId: "inst-f558aa",
    userId: "u-77300",
    agentSubAccountUid: "773001112",
    telegramUsername: "@wang_trade_user",
    telegramNumericId: "629914883920",
    templateId: "tmpl-spot-default",
    templateDisplayName: "Coobit 现货 Agent",
    templateVersion: "14",
    agentState: "NORMAL",
    runtimeState: "ERROR",
    subAccountStatus: "LINKED",
    lastProductBlockReason: "Runtime healthcheck failed · lastExitCode=137",
    lastActiveAt: "2026-05-04T22:15:00Z",
    createdAt: "2026-04-05T00:00:00Z",
    createdByDisplay: "api_i02_worker",
    appendix82: appendix("NORMAL", "—", "sub-acc-773"),
    instanceOverrides: {},
    bindingSnapshot: {
      lastBindVerifiedAt: "2026-04-05T10:00:00Z",
      tradingApiBindingRevision: "bind-rev-20260405T100000Z-u77300",
      bindEventRows: [
        {
          at: "2026-04-05T10:00:00Z",
          event: "TRADING_API_BOUND",
          detail: "绑定与健康实例一致",
        },
      ],
    },
  },
  {
    instanceId: "inst-a99001",
    userId: "u-88400",
    templateId: "tmpl-spot-default",
    templateDisplayName: "Coobit 现货 Agent",
    templateVersion: "14",
    agentState: "NORMAL",
    runtimeState: "STOPPED",
    subAccountStatus: "NONE",
    lastProductBlockReason: "—",
    lastActiveAt: "2026-05-03T06:00:00Z",
    createdAt: "2026-05-03T06:00:00Z",
    appendix82: appendix("NORMAL", "—", "—", {
      agentSubAccountStatus: "NONE",
      agentTradingApiBindingStatus: "NONE",
      agentTradingApiKeyId: null,
    }),
    instanceOverrides: {},
    bindingSnapshot: {
      bindEventRows: [
        {
          at: "2026-05-03T06:00:00Z",
          event: "INSTANCE_CREATED",
          detail: "I02 · 待绑定",
        },
      ],
    },
  },
  {
    instanceId: "inst-g66301",
    userId: "u-99510",
    agentSubAccountUid: "995100055",
    telegramUsername: "@start_quick_demo",
    telegramNumericId: "631009928471",
    templateId: "tmpl-spot-default",
    templateDisplayName: "Coobit 现货 Agent",
    templateVersion: "14",
    agentState: "NORMAL",
    runtimeState: "STARTING",
    subAccountStatus: "LINKED",
    lastProductBlockReason: "—",
    lastActiveAt: "2026-05-07T02:05:00Z",
    createdAt: "2026-05-07T02:00:00Z",
    createdByDisplay: "console_ops_zhang",
    appendix82: appendix("NORMAL", "—", "sub-acc-995"),
    instanceOverrides: {},
    bindingSnapshot: {
      lastBindVerifiedAt: "2026-05-07T02:03:00Z",
      tradingApiBindingRevision: "bind-rev-20260507T020300Z-u99510",
      bindEventRows: [
        {
          at: "2026-05-07T02:03:00Z",
          event: "RUNTIME_START_REQUESTED",
          detail: "Start · 快照就绪",
        },
      ],
    },
  },
  {
    instanceId: "inst-9e4412",
    userId: "u-22001",
    telegramUsername: "@k_beta_future",
    telegramNumericId: "640022911883",
    templateId: "tmpl-futures-beta",
    templateDisplayName: "合约交易（内测）",
    templateVersion: "3",
    agentState: "GLOBAL_OFF",
    runtimeState: "STOPPED",
    subAccountStatus: "PENDING",
    lastProductBlockReason: "GLOBAL_AGENT_SWITCH=OFF",
    lastActiveAt: "2026-05-01T10:00:00Z",
    createdAt: "2026-02-20T00:00:00Z",
    createdByDisplay: "qa_internal_bot",
    appendix82: {
      vipTier: 1,
      agentMinVipTier: 2,
      agentSubAccountId: "— 待绑定",
      agentSubAccountStatus: "PENDING",
      agentTradingApiBindingStatus: "NONE",
      agentTradingApiKeyId: null,
      agentState: "GLOBAL_OFF",
      lastProductBlockReason: "GLOBAL_OFF",
    },
    instanceOverrides: {},
    bindingSnapshot: {
      bindEventRows: [
        {
          at: "2026-02-20T15:00:00Z",
          event: "INSTANCE_CREATED",
          detail: "内测实例 · 待 onboarding",
        },
      ],
    },
  },
];

export {
  MOCK_SAFETY_PROMPT_PACK,
  MOCK_SCENARIO_PROMPT_PACK,
  MOCK_SYSTEM_PROMPT_PACK,
  buildPromptPackDraft,
  getPromptAuditTail,
  getPromptPack,
  getPromptPackDraft,
  getPromptPackVersionHistory,
  mockPromptPacks,
} from "./mockPromptData";



export const mockProviders: MockProvider[] = [
  {
    providerId: "prov-openai-1",
    displayName: "OpenAI 生产",
    baseUrl: "https://api.openai.com/v1",
    secretRef: "kms/prod/openai-main",
    enabled: true,
    healthStatus: "OK",
  },
];

export const mockModels: MockModel[] = [
  {
    modelId: "gpt-4.1-mini",
    providerId: "prov-openai-1",
    contextWindow: 128000,
    deprecated: false,
    enabled: true,
  },
  {
    modelId: "gpt-4.1",
    providerId: "prov-openai-1",
    contextWindow: 128000,
    deprecated: false,
    enabled: true,
  },
];

/** 配置页可绑定的工具画像（演示；matrixHealth 用于发布前校验） */
export const mockAgentToolProfiles: { id: string; label: string; matrixHealth: DependencyHealth }[] = [
  { id: "tp-spot-matrix-v2", label: "tp-spot-matrix-v2 · 现货矩阵已冻结", matrixHealth: "ok" },
  { id: "tp-futures-partial", label: "tp-futures-partial · 含未定 PATH（发布将提示）", matrixHealth: "warn" },
];

export const mockBillingHealth: MockBillingHealth = {
  billingMode: "shadow",
  executionFeeAnalyzeUsdt: "0.01",
  executionFeeTradeUsdt: "0.03",
  executionFeeMonitoringUsdt: "0.005",
  billingChargeModel: "BY_TOKEN",
  freeQuotaExecutionsPerDay: "20",
  tokenInputPer1kUsdt: "0.002",
  tokenOutputPer1kUsdt: "0.006",
  effectiveMinChargeUsdt: "0.01",
  settlementPolicy: "ENTITLEMENT_ONLY",
  gatewayErrorRatePct: "0.12",
  lastReconciledAt: "2026-05-07T00:15:00Z",
};

export const mockBillingRuntimeOverview: MockBillingRuntimeOverview = {
  currency: "USDT",
  executionsToday: 4280,
  successRatePct: 94.2,
  activeTasks: 126,
  tokenConsumptionToday: "842M",
  unknownOrPendingSharePct: 1.8,
  executionTrend7d: [
    { day: "05-01", analyze: 1180, trade: 920, monitoring: 280 },
    { day: "05-02", analyze: 1220, trade: 990, monitoring: 305 },
    { day: "05-03", analyze: 1195, trade: 875, monitoring: 298 },
    { day: "05-04", analyze: 1310, trade: 1010, monitoring: 322 },
    { day: "05-05", analyze: 1240, trade: 965, monitoring: 315 },
    { day: "05-06", analyze: 1288, trade: 1002, monitoring: 331 },
    { day: "05-07", analyze: 1262, trade: 978, monitoring: 308 },
  ],
  commercialSettledTodayUsdt: "412.00",
  commercialSettled7dUsdt: "2,847.00",
  packGrantsApplied7d: 156,
  meteringEstCost7dUsdt: "6,104.88",
  usageBreakdown: [
    { label: "分析执行", executions7d: 18_695, tokens7d: "312M", sharePct: 38 },
    { label: "交易执行", executions7d: 15_705, tokens7d: "401M", sharePct: 32 },
    { label: "Monitoring", executions7d: 9224, tokens7d: "89M", sharePct: 19 },
    { label: "Tool 增值能力", executions7d: 5291, tokens7d: "40M", sharePct: 11 },
  ],
};

/** Phase 2 · 轨 B 运营演示（OpenAPI · `admin/billing/commerce/*` + `me/commerce` 同窗字段） */
export const mockCommercePhase2AdminSnapshot: MockCommercePhase2AdminSnapshot = {
  phase2RailsEnabled: true,
  catalogVersion: "2026-05-26-demo",
  quotaBlockedSummary: {
    window: "近 24h",
    blockedEventCountByCapability: {
      "cap.agent.analyze": 42,
      "cap.agent.trade": 18,
      "cap.agent.monitoring": 7,
    },
    topUsersSample: [
      { userIdMasked: "u-10482", blockCount: 12 },
      { userIdMasked: "u-88301", blockCount: 9 },
      { userIdMasked: "u-22001", blockCount: 6 },
    ],
  },
  capabilityBuckets: [
    {
      capabilitySkuId: "cap.agent.analyze",
      displayLabel: "AI 分析 · 月度配额",
      remaining: 1280,
      quotaTotal: 3000,
      debitUnitsPerExecution: 1,
      resetsAt: "2026-06-01T00:00:00Z",
    },
    {
      capabilitySkuId: "cap.agent.trade",
      displayLabel: "自动交易 · 月度配额",
      remaining: 0,
      quotaTotal: 1500,
      debitUnitsPerExecution: 1,
      resetsAt: "2026-06-01T00:00:00Z",
    },
    {
      capabilitySkuId: "cap.pack.execution.100",
      displayLabel: "加购包 · 100 次执行",
      remaining: 37,
      quotaTotal: 100,
      debitUnitsPerExecution: 1,
      resetsAt: null,
    },
  ],
};

/** 用户侧 me/commerce 摘要 Demo（同窗 OpenAPI · MeCommerceEntitlementsSummary） */
export function getMockMeCommerceEntitlementsSummary() {
  const snap = mockCommercePhase2AdminSnapshot;
  return {
    subscriptionTierDisplay: "Pro（演示）",
    buckets: snap.capabilityBuckets.map((b) => ({
      capabilitySkuId: b.capabilitySkuId,
      displayLabel: b.displayLabel,
      remaining: b.remaining,
      resetsAt: b.resetsAt,
    })),
  };
}

export const mockBillingGatewayErrors: MockBillingGatewayError[] = [
  {
    window: "24h",
    errorClass: "CHARGE_GATEWAY_TIMEOUT",
    count: 14,
    lastBillingTraceId: "bt-gw-09x",
  },
  {
    window: "24h",
    errorClass: "CHARGE_GATEWAY_ERROR",
    count: 3,
    lastBillingTraceId: "bt-gw-02m",
  },
];

export const mockRolloutRules: MockRolloutRule[] = [
  {
    channel: "TELEGRAM",
    strategy: "percentile_rollout",
    audience: "bucket 0–18%（userId hash）",
    updatedAt: "2026-05-01T12:00:00Z",
    updatedBy: "ops.admin",
  },
  {
    channel: "H5",
    strategy: "deny_all",
    audience: "V1 未开通",
    updatedAt: "2026-04-10T00:00:00Z",
    updatedBy: "product.bot",
  },
];

/** 会员 VIP 等级（生产由接口 GET；此处 Mock 静态列表） */
export const mockMembershipVipLevels: MockMembershipVipLevel[] = [
  { tier: 0, label: "VIP0 · 普通" },
  { tier: 1, label: "VIP1" },
  { tier: 2, label: "VIP2" },
  { tier: 3, label: "VIP3" },
  { tier: 4, label: "VIP4" },
  { tier: 5, label: "VIP5" },
  { tier: 6, label: "VIP6" },
  { tier: 7, label: "VIP7" },
  { tier: 8, label: "VIP8" },
  { tier: 9, label: "VIP9 · 尊享" },
];

export const mockAccessWhitelist: MockWhitelistEntry[] = [
  {
    listId: "20260402000001",
    userIdMasked: "u-10482",
    note: "内测交易白名单",
    addedAt: "2026-04-02T08:00:00Z",
    addedBy: "ops.admin",
  },
  {
    listId: "20260402000001",
    userIdMasked: "u-50001",
    note: "运营手工添加 · 尾号 50001 段（演示 userIdMasked）",
    addedAt: "2026-04-05T11:20:00Z",
    addedBy: "ops.admin",
  },
];

export const mockUserBans: MockUserBan[] = [
  {
    banId: "ban-001",
    userUid: "1000283765008847361",
    reasonCode: "AGENT_USER_BLOCKED",
    scope: "AGENT_PRODUCT",
    expiresAt: "2026-06-01T00:00:00Z",
    createdAt: "2026-05-02T14:00:00Z",
    linkedPause: true,
    createdBy: "risk.ops",
  },
];

export const mockKycMirrors: MockKycMirror[] = [
  {
    userIdMasked: "u-10482",
    kycTier: "T2",
    region: "HK",
    lastSyncedAt: "2026-05-07T00:40:00Z",
    i02Impact: "通过",
  },
  {
    userIdMasked: "u-22001",
    kycTier: "T1",
    region: "CN",
    lastSyncedAt: "2026-05-06T22:10:00Z",
    i02Impact: "与 VIP 并列校验",
  },
];

/** Demo 执行：`executionId` **纯数字 10～19 位**；会话 `sess-*`；`scenarioId` 点分 — 同窗 `identity-schemas.yaml` / `naming-standard.md` §1。 */
export const mockObsExecutions: MockObsExecutionRow[] = [
  {
    executionId: "20260501001001",
    sessionId: "sess-aa11",
    userIdMasked: "u-10482",
    scenarioId: "trade.spot.limit_order",
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: "现货 · 限价下单",
    status: "COMPLETED",
    currentStage: "COMPLETED",
    retries: 0,
    createdAt: "2026-05-07T01:17:50Z",
    stageTimeline: ["CREATED", "CONFIRM_PENDING", "RUNNING", "COMPLETED"],
    durationMs: 8420,
    startedAt: "2026-05-07T01:17:50Z",
    outcome: "PER_EXECUTION_FINAL",
    resolvedPromptBinding: buildDefaultResolvedPromptBinding({
      scenarioId: "trade.spot.limit_order",
      sessionId: "sess-aa11",
    }),
    timelineEvents: ensureWritePathObservabilityTimeline(
      [
        {
          at: "2026-05-07T01:17:50.000Z",
          eventName: "execution.dispatched",
          summary: "stepKind:init; accepted→planning",
          transitionTrigger: "execution.dispatched",
        },
        {
          at: "2026-05-07T01:17:51.200Z",
          eventName: "confirmation.required",
          summary: "writePath:typeA",
          transitionTrigger: "confirmation.required",
        },
        {
          at: "2026-05-07T01:17:52.400Z",
          eventName: "user.confirmed",
          summary: "ADR-001 ok; waiting_confirmation→executing",
          transitionTrigger: "user.confirmed",
        },
        {
          at: "2026-05-07T01:18:03.100Z",
          eventName: "tool.round_complete",
          summary: "order.submitted; executing→settling",
          transitionTrigger: "tool.round_complete",
        },
        {
          at: "2026-05-07T01:18:18.320Z",
          eventName: "reconciliation.success",
          summary: "billing eligible; settling→completed",
          transitionTrigger: "reconciliation.success",
        },
      ],
      "trade.spot.limit_order",
      "sess-aa11",
    ),
  },
  {
    executionId: "20260501002002",
    sessionId: "sess-bb22",
    userIdMasked: "u-88301",
    scenarioId: "trade.spot.limit_order",
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: "现货 · 限价下单",
    status: "BLOCKED",
    currentStage: "BILLING_GATE",
    retries: 1,
    createdAt: "2026-05-06T18:40:55Z",
    stageTimeline: ["CREATED", "RUNNING", "BLOCKED"],
    durationMs: 2100,
    startedAt: "2026-05-06T18:40:55Z",
    outcome: "BILLING_BLOCKED",
    resolvedPromptBinding: buildDefaultResolvedPromptBinding({
      scenarioId: "trade.spot.limit_order",
      sessionId: "sess-bb22",
    }),
    timelineEvents: buildBillingBlockedTimeline(
      "trade.spot.limit_order",
      "sess-bb22",
      "2026-05-06T18:40:55Z",
    ),
  },
  {
    executionId: "20260501003099",
    sessionId: "sess-un99",
    userIdMasked: "u-10482",
    scenarioId: "trade.spot.flash_convert",
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: "现货 · 闪兑演练 / 对账不确定性",
    status: "UNKNOWN",
    currentStage: "RECONCILING",
    retries: 2,
    createdAt: "2026-05-07T02:05:12Z",
    stageTimeline: ["CREATED", "RUNNING", "UNKNOWN", "RECOVERING"],
    durationMs: 0,
    startedAt: "2026-05-07T02:05:12Z",
    outcome: "UNKNOWN",
    resolvedPromptBinding: buildDefaultResolvedPromptBinding({
      scenarioId: "trade.spot.flash_convert",
      sessionId: "sess-un99",
    }),
    timelineEvents: ensureWritePathObservabilityTimeline(
      [
        {
          at: "2026-05-07T02:05:13.000Z",
          eventName: "execution.dispatched",
          summary: "accepted→planning（演示）",
          transitionTrigger: "execution.dispatched",
        },
        {
          at: "2026-05-07T02:05:18.000Z",
          eventName: "exchange.504",
          summary: "终态不可判; executing→unknown_pending",
          transitionTrigger: "exchange.504",
        },
        {
          at: "2026-05-07T02:05:45.000Z",
          eventName: "reconciliation.inconclusive",
          summary: "证据不足; settling子路径挂起",
          transitionTrigger: "reconciliation.inconclusive",
        },
      ],
      "trade.spot.flash_convert",
      "sess-un99",
    ),
  },
  {
    executionId: "20260501004001",
    sessionId: "sess-fail01",
    userIdMasked: "u-22001",
    scenarioId: "trade.futures.market_order",
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: "合约 · 市价单失败",
    status: "FAILED",
    currentStage: "TOOL_FAILED",
    retries: 1,
    createdAt: "2026-05-07T00:30:00Z",
    stageTimeline: ["CREATED", "RUNNING", "FAILED"],
    durationMs: 800,
    startedAt: "2026-05-07T00:30:00Z",
    outcome: "FAILED",
    timelineEvents: ensureWritePathObservabilityTimeline(
      [
        {
          at: "2026-05-07T00:30:05.000Z",
          eventName: "execution.dispatched",
          summary: "stepKind:init; accepted→planning",
          transitionTrigger: "execution.dispatched",
        },
        {
          at: "2026-05-07T00:30:08.000Z",
          eventName: "confirmation.required",
          summary: "writePath:typeA",
          transitionTrigger: "confirmation.required",
        },
        {
          at: "2026-05-07T00:30:09.000Z",
          eventName: "user.confirmed",
          summary: "ADR-001 ok; waiting_confirmation→executing",
          transitionTrigger: "user.confirmed",
        },
        {
          at: "2026-05-07T00:30:10.000Z",
          eventName: "tool.final_failed",
          summary: "invocationState:FAILED; executing→failed",
          transitionTrigger: "tool.final_failed",
        },
      ],
      "trade.futures.market_order",
      "sess-fail01",
    ),
  },
  {
    executionId: "20260501005001",
    sessionId: "sess-run01",
    userIdMasked: "u-10482",
    scenarioId: "trade.spot.limit_order",
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: "现货 · 限价进行中",
    status: "RUNNING",
    currentStage: "RUNNING",
    retries: 0,
    createdAt: "2026-05-07T02:10:00Z",
    stageTimeline: ["CREATED", "CONFIRM_PENDING", "RUNNING"],
    durationMs: 0,
    startedAt: "2026-05-07T02:10:00Z",
    outcome: "RUNNING",
    resolvedPromptBinding: buildDefaultResolvedPromptBinding({
      scenarioId: "trade.spot.limit_order",
      sessionId: "sess-run01",
    }),
    timelineEvents: buildWritePathRunningTimeline(
      "trade.spot.limit_order",
      "sess-run01",
      "2026-05-07T02:10:00Z",
    ),
  },
  ...Array.from({ length: 28 }, (_, i) => {
    const n = i + 50;
    const day = 1 + (i % 6);
    const hour = 9 + (i % 10);
    const statuses = ["COMPLETED", "RUNNING", "CREATED", "FAILED", "BLOCKED", "UNKNOWN"] as const;
    const st = statuses[i % 6];
    const scenarios = [
      "trade.spot.limit_order",
      "trade.spot.flash_convert",
      "orders.read_activity",
      "wealth.holdings_read",
    ];
    const intents = ["现货 · 限价", "现货 · 闪兑", "订单 · 活动摘要", "理财 · 持仓只读"];
    const scenarioId = scenarios[i % scenarios.length]!;
    const sessionId = `sess-demo-${String(n).padStart(3, "0")}`;
    const startedAt = `2026-05-0${Math.min(day, 9)}T${String(hour).padStart(2, "0")}:00:00Z`;
    return {
      executionId: `20260501${String(100000 + n).padStart(6, "0")}`,
      sessionId,
      userIdMasked: `u-${20000 + ((i * 7919) % 50000)}`,
      scenarioId,
      orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
      intent: `${intents[i % intents.length]} · #${n}`,
      status: st,
      currentStage:
        st === "COMPLETED"
          ? "COMPLETED"
          : st === "RUNNING"
            ? "RUNNING"
            : st === "CREATED"
              ? "CREATED"
              : st === "FAILED"
                ? "TOOL_FAILED"
                : st === "BLOCKED"
                  ? "BILLING_GATE"
                  : "RECONCILING",
      retries: i % 4,
      createdAt: `2026-05-0${Math.min(day, 9)}T${String(hour).padStart(2, "0")}:${String((i * 7) % 60).padStart(2, "0")}:00Z`,
      stageTimeline: ["CREATED", "RUNNING"],
      durationMs: st === "COMPLETED" ? 1200 + i * 100 : 0,
      startedAt,
      outcome:
        st === "COMPLETED"
          ? "PER_EXECUTION_FINAL"
          : st === "FAILED"
            ? "FAILED"
            : st === "BLOCKED"
              ? "BILLING_BLOCKED"
              : st === "UNKNOWN"
                ? "UNKNOWN"
                : "RUNNING",
      resolvedPromptBinding: resolvedPromptBindingForDemo(scenarioId, sessionId),
      timelineEvents: buildDemoObsTimeline({
        status: st,
        scenarioId,
        sessionId,
        startedAt,
      }),
    } satisfies MockObsExecutionRow;
  }),
];

export const mockRuntimeTasks: MockRuntimeTask[] = [
  {
    taskId: "task-001",
    executionId: "20260501001001",
    state: "PENDING",
    scheduledAt: "2026-05-07T01:17:50Z",
  },
  {
    taskId: "task-002",
    executionId: "20260501003099",
    state: "BLOCKED",
    scheduledAt: "2026-05-07T02:05:14Z",
  },
  {
    taskId: "task-003",
    executionId: "20260501002002",
    state: "PENDING",
    scheduledAt: "2026-05-06T18:41:12Z",
  },
  {
    taskId: "task-004",
    executionId: "20260501005001",
    state: "RUNNING",
    scheduledAt: "2026-05-07T02:10:05Z",
  },
  {
    taskId: "task-005",
    executionId: "20260501004001",
    state: "PENDING",
    scheduledAt: "2026-05-07T00:30:02Z",
  },
];

/** 挂 execution 的运行事件流（MVP 摘录；完整检索走日志检索 FR-MC802） */
export const mockRuntimeEvents: MockRuntimeEventRow[] = [
  {
    executionId: "20260501001001",
    at: "2026-05-07T01:17:50Z",
    eventType: "execution.created",
    summary: "CREATED",
  },
  {
    executionId: "20260501001001",
    at: "2026-05-07T01:17:55Z",
    eventType: "confirm.pending",
    summary: "CONFIRM_PENDING",
  },
  {
    executionId: "20260501001001",
    at: "2026-05-07T01:17:58Z",
    eventType: "tool.started",
    summary: "tool.exchange.account.balance",
  },
  {
    executionId: "20260501001001",
    at: "2026-05-07T01:18:05Z",
    eventType: "tool.started",
    summary: "tool.exchange.spot.order",
  },
  {
    executionId: "20260501001001",
    at: "2026-05-07T01:18:22Z",
    eventType: "reconciliation.completed",
    summary: "billing settled",
  },
  {
    executionId: "20260501002002",
    at: "2026-05-06T18:40:55Z",
    eventType: "execution.created",
    summary: "CREATED",
  },
  {
    executionId: "20260501002002",
    at: "2026-05-06T18:41:00Z",
    eventType: "tool.succeeded",
    summary: "tool.exchange.account.balance",
  },
  {
    executionId: "20260501002002",
    at: "2026-05-06T18:41:04Z",
    eventType: "billing.preflight.failed",
    summary: "INSUFFICIENT_BALANCE",
  },
  {
    executionId: "20260501005001",
    at: "2026-05-07T02:10:00Z",
    eventType: "execution.created",
    summary: "CREATED",
  },
  {
    executionId: "20260501005001",
    at: "2026-05-07T02:10:03Z",
    eventType: "llm.completed",
    summary: "planner round 1",
  },
  {
    executionId: "20260501005001",
    at: "2026-05-07T02:10:08Z",
    eventType: "order.pending",
    summary: "partial fill · awaiting",
  },
  {
    executionId: "20260501003099",
    at: "2026-05-07T02:05:12Z",
    eventType: "execution.created",
    summary: "CREATED",
  },
  {
    executionId: "20260501003099",
    at: "2026-05-07T02:05:13Z",
    eventType: "retry.started",
    summary: "attempt 2",
  },
  {
    executionId: "20260501003099",
    at: "2026-05-07T02:05:14Z",
    eventType: "tool.failed",
    summary: "reconciliation timeout",
  },
  {
    executionId: "20260501004001",
    at: "2026-05-07T00:30:00Z",
    eventType: "execution.created",
    summary: "CREATED",
  },
  {
    executionId: "20260501004001",
    at: "2026-05-07T00:30:01Z",
    eventType: "tool.failed",
    summary: "market depth insufficient",
  },
];

export const mockObsTools: MockObsToolRow[] = [
  {
    executionId: "20260501001001",
    toolId: "tool.exchange.spot.order",
    toolCallSeq: 1,
    invocationState: "SUCCEEDED",
    pathSummary: "POST /sapi/v1/agent/order · 201",
    at: "2026-05-07T01:18:05Z",
  },
  {
    executionId: "20260501001001",
    toolId: "tool.exchange.account.balance",
    toolCallSeq: 0,
    invocationState: "SUCCEEDED",
    pathSummary: "GET /sapi/v1/agent/balance · 200",
    at: "2026-05-07T01:17:58Z",
  },
  {
    executionId: "20260501002002",
    toolId: "tool.exchange.account.balance",
    toolCallSeq: 0,
    invocationState: "SUCCEEDED",
    pathSummary: "GET /sapi/v1/agent/balance · 200",
    at: "2026-05-06T18:41:00Z",
  },
  {
    executionId: "20260501002002",
    toolId: "tool.billing.preflight",
    toolCallSeq: 1,
    invocationState: "SUCCEEDED",
    pathSummary: "POST /internal/billing/preflight · 402 simulate insufficient",
    at: "2026-05-06T18:41:03Z",
  },
  {
    executionId: "20260501003099",
    toolId: "tool.reconcile.execution",
    toolCallSeq: 0,
    invocationState: "FAILED",
    pathSummary: "POST /internal/reconcile · 504 gateway timeout",
    at: "2026-05-07T02:05:14Z",
  },
  {
    executionId: "20260501004001",
    toolId: "tool.exchange.spot.market",
    toolCallSeq: 0,
    invocationState: "FAILED",
    pathSummary: "POST /sapi/v1/agent/order/market · depth insufficient",
    at: "2026-05-07T00:30:01Z",
  },
  {
    executionId: "20260501005001",
    toolId: "tool.llm.router.plan",
    toolCallSeq: 0,
    invocationState: "SUCCEEDED",
    pathSummary: "orchestration · scenario trade.spot.limit_order",
    at: "2026-05-07T02:10:02Z",
  },
  {
    executionId: "20260501005001",
    toolId: "tool.exchange.spot.order",
    toolCallSeq: 1,
    invocationState: "SUCCEEDED",
    pathSummary: "POST /sapi/v1/agent/order · 202 pending fill",
    at: "2026-05-07T02:10:08Z",
  },
];

export const mockObsLlms: MockObsLlmRow[] = [
  {
    executionId: "20260501001001",
    modelId: "gpt-4.1-mini",
    inputTokens: 1204,
    outputTokens: 356,
    at: "2026-05-07T01:18:10Z",
  },
  {
    executionId: "20260501002002",
    modelId: "gpt-4.1-mini",
    inputTokens: 980,
    outputTokens: 240,
    at: "2026-05-06T18:40:58Z",
  },
  {
    executionId: "20260501003099",
    modelId: "gpt-4.1-mini",
    inputTokens: 612,
    outputTokens: 128,
    at: "2026-05-07T02:05:13Z",
  },
  {
    executionId: "20260501004001",
    modelId: "gpt-4.1-mini",
    inputTokens: 410,
    outputTokens: 96,
    at: "2026-05-07T00:30:00Z",
  },
  {
    executionId: "20260501005001",
    modelId: "gpt-4.1",
    inputTokens: 2104,
    outputTokens: 418,
    at: "2026-05-07T02:10:03Z",
  },
];

export const mockObsAudits: MockObsAuditRow[] = [
  {
    at: "2026-05-07T01:00:00Z",
    actor: "finance.admin",
    action: "billing.export.request",
    resource: "ledger:202605",
  },
  {
    at: "2026-05-06T16:22:00Z",
    actor: "ops.admin",
    action: "access.whitelist.append",
    resource: "20260402000001",
  },
];

export function getTemplate(id: string): AgentTemplate | undefined {
  return mockTemplates.find((t) => t.templateId === id);
}

/** 全所唯一主智能体配置（Demo：配置页单条形态；与 OpenAPI templateId 对应） */
export const PRIMARY_AGENT_TEMPLATE_ID = "tmpl-spot-default";

export function getPrimaryAgentTemplate(): AgentTemplate | undefined {
  return getTemplate(PRIMARY_AGENT_TEMPLATE_ID);
}

export function getInstance(id: string): AgentInstance | undefined {
  return mockInstances.find((i) => i.instanceId === id);
}

export function getTemplateVersionHistory(templateId: string): TemplateVersionHistoryEntry[] {
  return mockTemplateVersionHistory[templateId] ?? [];
}

export function getInstanceAuditRows(instanceId: string): AgentInstanceAuditRow[] {
  return mockInstanceAudits[instanceId] ?? [];
}

export function getObsExecution(executionId: string): MockObsExecutionRow | undefined {
  return mockObsExecutions.find((r) => r.executionId === executionId);
}

/** Demo：与实例 userId（= mockObs*.userIdMasked）对齐的执行记录 */
export function getObsExecutionsForUser(userId: string): MockObsExecutionRow[] {
  return mockObsExecutions.filter((r) => r.userIdMasked === userId);
}

export function getObsToolRowsForExecution(executionId: string): MockObsToolRow[] {
  return mockObsTools
    .filter((t) => t.executionId === executionId)
    .slice()
    .sort((a, b) => a.toolCallSeq - b.toolCallSeq);
}

export function getRuntimeTasksForExecution(executionId: string): MockRuntimeTask[] {
  return mockRuntimeTasks.filter((t) => t.executionId === executionId).slice();
}

export function getRuntimeEventsForExecution(executionId: string): MockRuntimeEventRow[] {
  return mockRuntimeEvents
    .filter((e) => e.executionId === executionId)
    .slice()
    .sort((a, b) => a.at.localeCompare(b.at));
}

/** 与 `trading-agent-config/keys.md` 对齐的 Demo 行；控制台按 `config.md` §1.1 拆页引用 */
export type ConfigKeyRow = { configKey: string; typeHint: string; demoValue: string };

/** keys §1（`GLOBAL_AGENT_SWITCH` 等）· 演示数据；`src/admin` 不设独立总闸页，供 API/bundle 对齐 */
export const globalGateConfigKeys: ConfigKeyRow[] = [
  { configKey: "GLOBAL_AGENT_SWITCH", typeHint: "bool", demoValue: "false" },
  { configKey: "OPS_GLOBAL_AGENT_PAUSE", typeHint: "bool | enum", demoValue: "false" },
];

/** keys §2 特性矩阵（`FEATURE_*` 等）· 演示数据；`src/admin` 不设独立功能开关页，供 API/bundle 对齐 */
export type FeatureFlagConfigRow = ConfigKeyRow & { productName: string; owner: string };

export const featureFlagConfigKeys: FeatureFlagConfigRow[] = [
  { configKey: "FEATURE_TRADING", typeHint: "bool", demoValue: "true", productName: "交易写总能力", owner: "交易产品" },
  { configKey: "FEATURE_ANALYSIS", typeHint: "bool", demoValue: "true", productName: "分析类能力", owner: "数据产品" },
  { configKey: "FEATURE_AGENT_SPOT", typeHint: "bool", demoValue: "true", productName: "现货 Agent", owner: "交易产品" },
  { configKey: "FEATURE_AGENT_FUTURES", typeHint: "bool", demoValue: "false", productName: "合约 Agent（灰度）", owner: "交易产品" },
  { configKey: "FEATURE_AGENT_WEALTH", typeHint: "bool", demoValue: "true", productName: "理财 Agent", owner: "财富产品" },
  { configKey: "CHANNEL_TELEGRAM", typeHint: "bool", demoValue: "true", productName: "Telegram 触达产品线", owner: "渠道与增长" },
  {
    configKey: "BILLING_SHADOW_EXPORT",
    typeHint: "bool",
    demoValue: "false",
    productName: "计费影子导出（财务）",
    owner: "财务运营",
  },
];

/** Telegram 运行时参数（keys §4.2～4.3）；供 API/bundle 对齐，**非**渠道管理运营页主表 */
export const telegramChannelConfigKeys: ConfigKeyRow[] = [
  { configKey: "TELEGRAM_DEFAULT_LOCALE", typeHint: "string", demoValue: "zh-CN" },
  { configKey: "TELEGRAM_HELP_H5_URL_TEMPLATE", typeHint: "string", demoValue: "https://h5…/help/{locale}" },
  { configKey: "TELEGRAM_BOT_TOKEN_SECRET_REF", typeHint: "secretRef", demoValue: "vault/telegram/bot-main（不可见）" },
  { configKey: "TELEGRAM_LINK_PREVIEW_DEFAULT", typeHint: "bool", demoValue: "false" },
];

/** 交易护栏 + 计费边界键（keys §3、§5）；供 allConfigKeyRows / 接口对齐（控制台无独立页） */
export const tradingConfigTabGroups: { tab: string; keys: ConfigKeyRow[] }[] = [
  {
    tab: "交易护栏",
    keys: [
      { configKey: "AGENT_MIN_VIP_TIER", typeHint: "int", demoValue: "2" },
      { configKey: "SYMBOL_POLICY_MODE", typeHint: "enum", demoValue: "allowlist" },
      { configKey: "AGENT_PRICE_DEVIATION_BPS", typeHint: "int", demoValue: "80" },
      { configKey: "AGENT_COOLDOWN_SEC", typeHint: "int", demoValue: "2" },
      { configKey: "AGENT_MAX_NET_EXPOSURE_USDT", typeHint: "decimal", demoValue: "50000" },
    ],
  },
  {
    tab: "BILLING（边界）",
    keys: [
      { configKey: "BILLING_MODE", typeHint: "enum", demoValue: "shadow" },
      { configKey: "effectiveMinChargeUsdt", typeHint: "decimal", demoValue: "0.01" },
      { configKey: "BILLING_TOKEN_RATE", typeHint: "JSON", demoValue: "{…}（计费域 SSOT）" },
    ],
  },
];

/** 跨页查找演示默认值（准入 VIP、联调等） */
export const allConfigKeyRows: ConfigKeyRow[] = [
  ...globalGateConfigKeys,
  ...featureFlagConfigKeys,
  ...tradingConfigTabGroups.flatMap((g) => g.keys),
  ...telegramChannelConfigKeys,
];

/** 配置矩阵表「类型」列中文（演示） */
export function configTypeHintZh(t: string): string {
  const m: Record<string, string> = {
    bool: "布尔",
    int: "整数",
    "bool | enum": "布尔或枚举",
    string: "字符串",
    secretRef: "密钥引用",
    enum: "枚举",
    decimal: "小数",
    JSON: "JSON",
  };
  return m[t] ?? t;
}
