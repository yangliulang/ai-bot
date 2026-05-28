export type DependencyHealth = "ok" | "warn" | "off";

export interface AgentTemplate {
  templateId: string;
  internalName: string;
  displayName: string;
  /** 业务描述（运营可读） */
  description: string;
  /** 标签，如 spot、futures */
  tags: string[];
  publishedVersion: string | null;
  enabled: boolean;
  promptSummary: DependencyHealth;
  toolSummary: DependencyHealth;
  modelSummary: DependencyHealth;
  updatedAt: string;
  /** agent-management/config §5 templateStatus 示意 */
  templateStatus: "DRAFT" | "PUBLISHED" | "DISABLED";
  /** Prompt 包引用（已发布） */
  boundPromptPackRef: string;
  boundPromptPackVersion: string | null;
  /** 工具画像 */
  toolProfileRef: string;
  /** ai-settings 默认模型 */
  defaultModelRef: string;
  /** 模板级风控摘要 */
  riskProfileSummary: string;
  /** 平台闸 revision 高于包内快照时黄灯（T04） */
  promptGateRevisionStale?: boolean;
}

/** 模板版本履历（演示） */
export interface TemplateVersionHistoryEntry {
  templateVersion: string;
  publishedAt: string;
  summary: string;
  actor: string;
}

/** 实例相关审计行（演示） */
export interface AgentInstanceAuditRow {
  at: string;
  actor: string;
  action: string;
  resource: string;
}

export type AgentState =
  | "NORMAL"
  | "GLOBAL_OFF"
  | "BILLING_BLOCKED"
  | "OPS_SUSPENDED"
  | "MEMBERSHIP_BLOCKED"
  | "AGENT_SUBACCOUNT_BLOCKED";

export interface Appendix82Summary {
  vipTier: number;
  agentMinVipTier: number;
  agentSubAccountId: string;
  agentSubAccountStatus: string;
  agentTradingApiBindingStatus: string;
  agentTradingApiKeyId: string | null;
  agentState: AgentState;
  lastProductBlockReason: string;
}

/** 绑定 Tab · 演示用事件行（非审计 SSOT） */
export interface AgentInstanceBindingEventMock {
  at: string;
  event: string;
  detail: string;
}

/**
 * 实例详情「绑定」Tab 演示扩展（无 Secret；契约以 OpenAPI 为准）。
 */
export interface AgentInstanceBindingSnapshot {
  /** 最近一次校验/绑定成功（ISO） */
  lastBindVerifiedAt?: string;
  /** 托管绑定 revision（演示） */
  tradingApiBindingRevision?: string;
  /** 最近绑定相关事件（演示） */
  bindEventRows?: AgentInstanceBindingEventMock[];
}

export interface AgentInstance {
  instanceId: string;
  userId: string;
  /** 交易所子账户 UID（`subUid`）；未绑定／未知可省略 */
  agentSubAccountUid?: string;
  /** 已绑定 Telegram @username（脱敏展示规则以 OpenAPI 为准） */
  telegramUsername?: string;
  /** Telegram 数值 user id（运营协查；演示） */
  telegramNumericId?: string;
  templateId: string;
  /** 列表展示用模板名（与模板 displayName 对齐） */
  templateDisplayName: string;
  templateVersion: string;
  agentState: AgentState;
  runtimeState: "RUNNING" | "PAUSED" | "STOPPED" | "STARTING" | "ERROR";
  subAccountStatus: "LINKED" | "PENDING" | "NONE";
  /** 列表「运行状态」短因，附录 A 对齐 */
  lastProductBlockReason: string;
  lastActiveAt: string;
  createdAt: string;
  /** 创建者展示（IAM / 控制台账号；OpenAPI 未返回时可省略） */
  createdByDisplay?: string;
  appendix82: Appendix82Summary;
  /** 白名单覆盖（OpenAPI 冻结键；演示 JSON） */
  instanceOverrides: Record<string, unknown>;
  /** 详情「绑定」Tab 扩展演示（无 Secret） */
  bindingSnapshot?: AgentInstanceBindingSnapshot;
}

export interface MockPromptPack {
  promptPackId: string;
  kind: "SYSTEM" | "TRADING" | "SAFETY" | "ANALYSIS";
  title: string;
  /** 当前生效发布号（无则 null） */
  currentVersion: number | null;
  lockState: string;
  scenarioId?: string;
  /** 运营简介（列表/详情） */
  description?: string;
  /** ISO · 列表元数据 */
  updatedAt?: string;
  publishedAt?: string;
  /** 演示：是否存在未发布草稿（FR-PM 流程提示） */
  hasDraft?: boolean;
  /** config §1 · 引用 trade-assistance skillSpecVersion（不拷贝正文） */
  skillSpecRef?: string;
  /** 最近发布人（审计 / UI） */
  publisher?: string;
  /** 乐观锁 etag / contentHash 短串（functions §7） */
  contentHashShort?: string;
  /** 平台闸门修订号（runtime-injection §2.3） */
  placeholderDenylistRevision?: string;
  safetyPhraseBlocklistRevision?: string;
  /** SC-PM-20：Publish 成功时固化的快照 */
  publishedWithPlaceholderDenylistRevision?: string;
  publishedWithSafetyPhraseBlocklistRevision?: string;
  /** PM-C07 软下线 */
  deprecatedAt?: string;
  deprecationNotice?: string;
  /** FR-PM05：生效版 Few-shot 条目数（演示） */
  fewShotCount?: number;
  /** PM-C04：正文载体体量示意（KiB） */
  bodySizeKiBApprox?: number;
  /** runtime-injection §5 */
  targetModelFamily?: string;
  /** runtime-injection §7.1.2 */
  safetyPhraseScanScope?: "FULL_PACK" | "TRADING_BODY_FEWSHOT";
  /** 抽屉内只读正文摘要（非 SSOT） */
  effectiveBodyPreview?: string;
}

/** 版本履历行（FR-PM02 详情 · FR-PM07 审计） */
export interface MockPromptPackVersionHistoryRow {
  promptPackVersion: number;
  publishedAt: string;
  actor: string;
  event: "PUBLISH" | "ROLLBACK";
  summary: string;
}

/** Few-shot 条目（FR-PM05 · OpenAPI role enum） */
export interface MockFewShotRow {
  id: string;
  role: "system" | "user" | "assistant";
  content: string;
  name?: string;
}

/** 草稿编辑器载体（演示；真源为 PromptPackPatch + etag） */
export interface MockPromptPackDraft {
  promptPackId: string;
  /** PM-C03 乐观锁 */
  etag: string;
  /** Prompt 正文（Markdown/结构化二选由 design 冻结；此处统一 Markdown 演示） */
  bodyMarkdown: string;
  fewShots: MockFewShotRow[];
  /** variableSchema JSON 字符串 */
  variableSchemaJson: string;
  /** 沙箱 fixture JSON */
  sandboxFixtureJson: string;
}

/** 最近审计尾行（FR-PM01；演示） */
export interface MockPromptAuditRow {
  at: string;
  actor: string;
  action: string;
  detail: string;
}

export interface MockProvider {
  providerId: string;
  displayName: string;
  baseUrl: string;
  secretRef: string;
  enabled: boolean;
  healthStatus: string;
}

export interface MockModel {
  modelId: string;
  providerId: string;
  contextWindow: number;
  deprecated: boolean;
  enabled: boolean;
}

/** billing-management · FR-MC502 · Demo 定价真源（含 Runtime 产品与 Token 成本层） */
export interface MockBillingHealth {
  billingMode: string;
  /** Runtime 产品层：按场景每笔固定价 USDT */
  executionFeeAnalyzeUsdt: string;
  executionFeeTradeUsdt: string;
  executionFeeMonitoringUsdt: string;
  /** 运营语义：按执行 / 按 Token / 混合 */
  billingChargeModel: "BY_EXECUTION" | "BY_TOKEN" | "HYBRID";
  /** 每用户每日免费执行次数（演示文案） */
  freeQuotaExecutionsPerDay: string;
  /** USDT / 千 Token（高级） */
  tokenInputPer1kUsdt: string;
  tokenOutputPer1kUsdt: string;
  effectiveMinChargeUsdt: string;
  /** 内部枚举；UI 用中文「结算时机」 */
  settlementPolicy: string;
  gatewayErrorRatePct: string;
  lastReconciledAt: string;
}

export type MockEntitlementDebitDisplayStatus = "SUCCESS" | "INSUFFICIENT" | "FAILED" | "AWAITING_FINAL";

/** billing-management · 执行核销追踪（MC503/504 · Demo） */
export interface MockBillingLedgerRow {
  recordedAt: string;
  billingTraceId: string;
  userIdMasked: string;
  executionId: string;
  capabilitySkuId: string;
  commercialSettlementType: "ENTITLEMENT_DEBIT";
  debitStatus: MockEntitlementDebitDisplayStatus;
  failureReason: "none" | "quota" | "gateway" | "policy" | "not_applicable";
  consumedUnits?: number;
  idempotencyKeySuffix: string;
  requestId?: string;
  packGrantId?: string;
  intentType: string;
  executionStatus: string;
}

export type BillingFailureReason = MockBillingLedgerRow["failureReason"];

/** 计费总览 · Runtime Consumption + 收入侧（Demo；运营视角非纯财务） */
export interface MockBillingRuntimeOverview {
  currency: "USDT";
  /** 今日可计费执行次数（演示口径） */
  executionsToday: number;
  /** 成功终态 / 已完成评估的占比 % */
  successRatePct: number;
  /** 当前 RUNNING / 队列中的任务估数 */
  activeTasks: number;
  /** 今日 Token 消耗展示（input+output 合并文案） */
  tokenConsumptionToday: string;
  /** UNKNOWN 等未决终态占比（损耗提示） */
  unknownOrPendingSharePct: number;
  /** 近 7 日按日、按场景执行量 */
  executionTrend7d: { day: string; analyze: number; trade: number; monitoring: number }[];
  commercialSettledTodayUsdt: string;
  commercialSettled7dUsdt: string;
  packGrantsApplied7d: number;
  meteringEstCost7dUsdt: string;
  /** Runtime usage 分类（运营可读，非模型成本拆分） */
  usageBreakdown: {
    label: string;
    executions7d: number;
    tokens7d: string;
    sharePct: number;
  }[];
}

/** billing-management · FR-MC506 */
export interface MockBillingGatewayError {
  window: string;
  errorClass: string;
  count: number;
  lastBillingTraceId: string;
}

/** access-control · FR-MC601 */
export interface MockRolloutRule {
  channel: string;
  strategy: string;
  audience: string;
  updatedAt: string;
  updatedBy: string;
}

/** access-control · FR-MC602；名单ID 规则见 admin `access/whitelistListId.ts` */
export interface MockWhitelistEntry {
  listId: string;
  userIdMasked: string;
  note: string;
  addedAt: string;
  /** 最近写入操作人（演示） */
  addedBy?: string;
}

/** access-control · FR-MC603～604；用户 UID 管理台完整展示 */
export interface MockUserBan {
  banId: string;
  userUid: string;
  reasonCode: string;
  /** Demo 固定为智能体产品（AGENT_PRODUCT） */
  scope: string;
  expiresAt: string | null;
  createdAt: string;
  linkedPause: boolean;
  /** 创建人（演示审计） */
  createdBy?: string;
}

/** 会员 VIP 等级清单（接口 Mock，正式环境由接口下发） */
export interface MockMembershipVipLevel {
  tier: number;
  label: string;
}

/** access-control · FR-MC605 */
export interface MockKycMirror {
  userIdMasked: string;
  kycTier: string;
  region: string;
  lastSyncedAt: string;
  i02Impact: string;
}

/** `agent.skill.spec_read` 结构化字段（Demo；生产 BFF 可仅返 summary 键） */
export interface MockSkillSpecReadPayload {
  skillId: string;
  skillSpecVersion: string;
  phase: "success" | "fail";
  specDigest?: string;
}

/** OpenAPI `ResolvedPromptBinding` 子集（SC-PM-22 / observability §2.3） */
export interface MockResolvedPromptBinding {
  scenarioId: string;
  sessionId?: string | null;
  systemPromptPackId: string;
  systemPromptPackVersion: number;
  safetyPromptPackId: string;
  safetyPromptPackVersion: number;
  tradingPromptPackId: string | null;
  tradingPromptPackVersion: number | null;
  runtimeClarifyPromptPackId: string;
  runtimeClarifyPromptPackVersion: number;
  runtimeOutputContractPromptPackId: string;
  runtimeOutputContractPromptPackVersion: number;
  fewShotDigest?: string | null;
  placeholderDenylistRevision?: string;
  safetyPhraseBlocklistRevision?: string;
}

/** OpenAPI `ObservabilityTimelineEvent` 子集；主态边 × `transitionTrigger` 见 observability §2.4 */
export interface MockObsTimelineEventRow {
  at: string;
  eventName?: string;
  summary?: string;
  /** 与 execution-transition-matrix §2.2 Trigger 字面或已登记别名同窗（若返回须在 UI 可读） */
  transitionTrigger?: string;
  /** Production Runtime · `agent.skill.spec_read`（SC-OM-05） */
  skillSpecRead?: MockSkillSpecReadPayload;
  /** Production Runtime · `agent.prompt.binding_resolved`（SC-PM-22） */
  promptBindingResolved?: MockResolvedPromptBinding;
}

/** observability-management · 执行 FR-MC801；列表 API 见 OpenAPI `listObservabilityExecutions` / `ObservabilityExecutionSummary`；MVP 列表字段见 admin-console page-specs（Runtime-first） */
export interface MockObsExecutionRow {
  executionId: string;
  sessionId: string;
  userIdMasked: string;
  scenarioId: string;
  /** 与运行编排页登记版本对齐（Demo；须与 scenario 寄存器同窗迭代） */
  orchestrationVersion: string;
  /** 用户/业务意图摘要（运营可读） */
  intent: string;
  /** 运行态：CREATED / RUNNING / COMPLETED / UNKNOWN / FAILED / BLOCKED */
  status: string;
  /** 当前阶段（编排机读或展示） */
  currentStage: string;
  retries: number;
  createdAt: string;
  /** 阶段快照（时间线 Steps） */
  stageTimeline: string[];
  durationMs: number;
  startedAt: string;
  outcome: string;
  /** FR-MC801 API 时间线（演示）；线上对齐 `getObservabilityExecutionTimeline` */
  timelineEvents?: MockObsTimelineEventRow[];
  /** Demo · `agent.prompt.binding_resolved` 快照（执行详情治理区） */
  resolvedPromptBinding?: MockResolvedPromptBinding;
}

/** Runtime · 运行域事件摘录（挂 execution；聚合页见运行事件） */
export interface MockRuntimeEventRow {
  executionId: string;
  at: string;
  eventType: string;
  summary: string;
}

/** Runtime Operations · Tasks（Demo；API TBD） */
export interface MockRuntimeTask {
  taskId: string;
  executionId: string;
  state: "PENDING" | "RUNNING" | "BLOCKED";
  scheduledAt: string;
}

/** observability-management · 工具 FR-MC803 */
export interface MockObsToolRow {
  executionId: string;
  toolId: string;
  toolCallSeq: number;
  invocationState: string;
  pathSummary: string;
  at: string;
}

/** observability-management · LLM FR-MC804 */
export interface MockObsLlmRow {
  executionId: string;
  modelId: string;
  inputTokens: number;
  outputTokens: number;
  at: string;
}

/** observability-management · 计费协查 FR-MC503（轨 B） */
export interface MockObsBillingRow {
  executionId: string;
  billingTraceId: string;
  capabilitySkuId: string;
  commercialSettlementType: "ENTITLEMENT_DEBIT";
  debitStatus: MockEntitlementDebitDisplayStatus;
  failureReason: MockBillingLedgerRow["failureReason"];
  consumedUnits?: number;
  idempotencyKeySuffix: string;
  at: string;
}

/** observability-management · 审计 FR-MC806 */
export interface MockObsAuditRow {
  at: string;
  actor: string;
  action: string;
  resource: string;
}

/** Phase 2 · 轨 B 运营演示 */
export interface MockCommercePhase2AdminSnapshot {
  phase2RailsEnabled: boolean;
  catalogVersion: string;
  quotaBlockedSummary: {
    window: string;
    blockedEventCountByCapability: Record<string, number>;
    topUsersSample: { userIdMasked: string; blockCount: number }[];
  };
  capabilityBuckets: {
    capabilitySkuId: string;
    displayLabel: string;
    remaining: number;
    quotaTotal?: number;
    debitUnitsPerExecution?: number;
    resetsAt: string | null;
  }[];
}

export type MockCommerceResourcePackKind = "subscription" | "addon";

/** 资源 · 配额真源（套餐 M:N 关联；加购可单独售卖） */
export interface MockCommerceResourcePack {
  resourceId: string;
  name: string;
  capabilitySkuId: string;
  quotaUnits: number;
  periodLabel: string;
  packKind: MockCommerceResourcePackKind;
  priceUsdt?: string;
  active: boolean;
  description?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface MockCommerceSubscriptionTier {
  tierId: string;
  name: string;
  tagline: string;
  priceUsdt: string;
  periodLabel: string;
  /** 关联资源 ID（配额由资源汇总，不在此手填） */
  resourcePackIds: string[];
  highlights: string[];
  recommended?: boolean;
  active: boolean;
  internalNote?: string;
  createdAt?: string;
  updatedAt?: string;
}

export type MockCommerceCryptoPaymentNetwork = "USDT_TRC20" | "USDT_ERC20";

export type MockCommerceCryptoOrderStatus = "PENDING" | "CONFIRMING" | "SETTLED" | "EXPIRED";

/** 到账后权益写入状态（FR-B18 · pack-grants） */
export type MockCommerceGrantStatus = "NOT_APPLICABLE" | "PENDING" | "APPLIED" | "FAILED";

export type MockCommerceCryptoOrder = {
  /** 纯数字订单号，14～20 位；见 `commerceOrderId.ts` */
  orderId: string;
  userIdMasked: string;
  kind: "upgrade" | "pack";
  /** 套餐 tierId 或加购 resourceId */
  productId: string;
  /** 实付 USDT */
  amountUsdt: string;
  /** 目录标价（对账） */
  listPriceUsdt: string;
  network: MockCommerceCryptoPaymentNetwork;
  status: MockCommerceCryptoOrderStatus;
  createdAt: string;
  /** 支付窗口截止 */
  expiresAt?: string | null;
  settledAt?: string | null;
  /** 用户须转账至此的完整收款地址（同窗 Web 结账页） */
  paymentAddress: string;
  /** 列表/摘要用脱敏（可选） */
  depositAddressMasked?: string | null;
  /** 链上识别的用户付款钱包（脱敏） */
  payerAddressMasked?: string | null;
  txHashMasked?: string | null;
  confirmationsReceived?: number;
  confirmationsRequired?: number;
  /** PSP / Webhook 对账键 */
  pspReference?: string | null;
  packGrantId?: string | null;
  grantStatus: MockCommerceGrantStatus;
  grantAppliedAt?: string | null;
  capabilitySkuId?: string | null;
  quotaUnits?: number | null;
  periodLabel?: string | null;
  /** 升级到账：档位 SKU（演示用 tierId） */
  subscriptionTierSku?: string | null;
  entitlementPeriodEnd?: string | null;
};

export type MockCommerceUserSubscription = {
  tierDisplay: string;
  tierSku: string;
  status: "active" | "expired" | "none";
  periodEnd: string | null;
};
