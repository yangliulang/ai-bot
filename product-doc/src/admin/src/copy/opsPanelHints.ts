/**
 * 运营面板 · 提示卡片文案 SSOT（用户可见叙事；契约字段名不在此改）。
 * 组件用 OpsHintAlert 时可将 technicalDetail 折叠为「技术对照」。
 */

/** 观测 / 审计事件：运营简称 + 契约 eventName */
export const OPS_EVENT_LABEL = {
  promptBindingResolved: {
    label: "Prompt 拼装绑定",
    code: "agent.prompt.binding_resolved",
  },
  skillSpecRead: {
    label: "技能规范载入",
    code: "agent.skill.spec_read",
  },
  publishBlocked: {
    label: "发布拦截",
    code: "admin.prompt.publish_blocked",
  },
} as const;

export function formatOpsEventRef(key: keyof typeof OPS_EVENT_LABEL): string {
  const e = OPS_EVENT_LABEL[key];
  return `${e.label}（${e.code}）`;
}

export const PROMPT_GOVERNANCE_INTRO = {
  description:
    "Prompt 只写 LLM 如何理解与表达（Identity、场景、行为、澄清、输出契约）；校验、计费、网关与技能契约由 Runtime 负责。写路径按场景拆包；读侧/分析共用「分析对话（统一）」包。",
} as const;

export const PROMPT_DETAIL = {
  labelScenarioId: "场景键",
  labelSkillScope: "关联技能",
  skillScopeEmpty: "未填写（写路径可由场景推断）",
} as const;

export const PROMPT_TABLE = {
  colSkillScope: "技能范围",
  colScenario: "场景键",
} as const;

export const PROMPT_PUBLISH_MODAL = {
  remoteConfirm: "将按环境策略把当前草稿升为对外生效版本（以服务端为准）。发布前须已在技能登记册完成技能发布。",
  localConfirm: "当前为本地预览：预检已通过；连接生产服务后才会真实生效。",
  localSuccess: "本地预览：发布流程已完成（技能登记校验已通过）",
  rollbackLocalHint: "本地预览不会修改远端版本。",
} as const;

export const PROMPT_SAFETY = {
  apiFallbackMessage: "列表暂用本地样例",
  apiFallbackDescription: "连接生产 Prompt 服务后将展示服务端数据。",
  tagApiUnavailable: "接口不可用",
  tagLocalPreview: "本地预览",
  tagApiConnected: "已接服务",
} as const;

/** 提示词治理列表 · 数据来源 Tag（策略页 / 安全页同窗） */
export const PROMPT_LIST_SOURCE = {
  tagMock: "本地预览",
  tagRemote: "已接 API",
  tagRemoteMerged: "已接 API · 16 包补齐",
  tagRemoteFallback: "接口不可用",
  mergeHint: (n: number) => `远端列表缺 ${n} 个治理包 · 已用本地 SSOT 补齐`,
} as const;

export const PROMPT_EDITOR = {
  pageDescription: "维护对话规则与场景说明；写路径在「技能与工具」登记册配置操作规范。",
  labelPackId: "包标识",
  labelScenarioId: "适用场景",
  labelSkillScope: "关联技能",
  skillScopeHint: "发布前校验登记册中是否已有对应技能版本；参数与确认卡不在此页编辑。",
  unifiedAnalysisBanner:
    "本包覆盖所有只读分析对话（行情、持仓、舆情、监控等）。正文只写分析纪律，不按主题拆包；具体可读范围由对话上下文提供。",
  labelAnalysisCapabilities: "覆盖的只读能力（清单参考）",
  analysisCapabilitiesHint:
    "下列为能力清单参考，细则不写入 Prompt 正文。",
  contentHint:
    "支持标题、列表、加粗与代码块；可使用 {{name}} 形占位符。预览为安全渲染。",
  assemblyTraceTitle: "拼装层来源（预览）",
  assemblyTraceHint:
    "展示一次请求可能叠合的 Prompt 层及来源包版本；正式环境由运行时在回合开端写入绑定快照，并可在执行详情查看。",
  publishFooterRemote:
    "发布后由运行时按场景选技能并拼装 Prompt；编排与模板绑定在「运行场景」等页维护。",
  publishRejectTraceTitle: "发布校验结果",
  publishPreflightButton: "预检发布条件",
  localDraftBanner: "本地草稿仅存于当前浏览器，刷新或换设备会丢失。",
  lockedVersionMessage: "已发布版本正文已冻结",
  lockedVersionDescription: "请先复制草稿后再改写正文。",
  draftReadyMessage: "草稿副本就绪，可编辑正文。",
  demoSaveHint: "本地预览：保存/发布不与真实服务端联动。",
  savedLocal: "已保存（本地草稿）",
  savedPreview: "已保存（本地预览）",
  localDraftVersionHint: "本地草稿不参与远端版本树。",
} as const;

export const PROMPT_PUBLISH_GATE = {
  checking: "正在检查发布条件…",
  titlePending: "发布条件检查",
  titleOk: "满足发布条件",
  titleFail: "暂不满足发布条件",
  labelScenario: "场景键",
  labelSkillRef: "关联技能",
  okResolved: "登记册中已找到对应技能",
  legacyHint: "（由场景推断，建议在包上填写「技能@版本」）",
  parsePrefix: "解析为",
} as const;

export const PROMPT_PUBLISH_REJECT = {
  preflightOk: "发布预检通过",
  preflightOkDetail: "可按流程继续发布；若正文或场景有改动，请重新预检。",
  preflightOkCompact: "预检通过",
  blockedTitle: "暂不可发布",
  blockedLead: "请先处理下列检查项，再执行发布。",
  traceCardTitle: "发布校验结果",
  colCheck: "检查项",
  colCode: "编号",
  colDetail: "说明",
  colFix: "处理建议",
} as const;

export const EXECUTION_PROMPT_TRACE = {
  cardTitle: "Prompt 拼装追溯",
  alertMessage: "回合开端冻结快照（不含 Prompt 正文）",
  sourceFromTimeline: "数据来自执行时间线",
  sourceFromSummary: "数据来自执行摘要",
  sourceInferred: "按场景推断（预览数据）",
  skillSpecCrossLink: "技能能力见「技能规范」卡，不在此重复。",
} as const;

export const EXECUTION_SKILL_SPEC = {
  cardTitle: "技能规范载入",
  emptyMessage: "本条为只读或未挂载写路径载入事件",
  emptyDescription:
    "写路径须在用户确认前完成技能规范读取并记入观测。分析类场景可能不出现本卡数据。",
  registryLink: "技能与工具",
  labelSkillId: "技能 ID",
  labelVersion: "版本",
  labelReadResult: "载入结果",
  labelDigest: "规范摘要",
  labelObsEvent: "观测事件",
  obsEventSuffix: "须在用户确认提示之前",
  readOpFootnote: "read_skill_operation_spec",
} as const;

export const EXECUTION_CANONICAL_NOTES = {
  readOnly: "读侧场景无写路径出站语义；查询类能力见只读工具说明。",
  unmappedSkill: "写场景尚未映射主技能，无法展示出站语义。",
  billingBlocked: "本条在计费环节被拦截；下方为回合开端预览快照，非真实出站载荷。",
  demoDefault: "预览载荷；正式环境以出站门禁审计与领域模型规范为准。",
  unknownPending: "终态未确认，出站门禁结果待对账，不展示通过结论。",
} as const;

export const EXECUTION_CANONICAL = {
  cardTitle: "出站语义检视（预览）",
  alertMessage: "领域动词与核心对象（与交易所原始字段解耦）",
  notApplicable: "本条执行不适用写路径出站语义展示。",
  labelCanonicalOp: "领域操作",
  labelSkillId: "技能 ID",
  labelGateway: "出站门禁",
  gatewayPass: "通过（预览）",
  payloadTitle: "拟出站载荷",
  confirmationTitle: "用户确认快照（类型 A）",
  provenanceTitle: "经济字段溯源",
  colField: "字段",
  colSource: "来源",
} as const;

export const SCENARIO_SKILL_SCOPE = {
  alertMessage: "本场景技能范围（只读）",
  alertDescription:
    "列出本场景下运行时可选的写操作技能；不等于 Prompt 托管技能。规范编辑见「技能与工具」。",
  colSkillId: "技能 ID",
  colSummary: "摘要",
  colVersion: "版本",
  colRegistry: "登记册",
  colDemoEnabled: "本环境启用",
  colMatrix: "矩阵",
  readOnlyHint: "无主要写技能 · 只读工具面见运行场景说明。",
  missingPrimarySkill: "写场景尚未映射主技能",
  labelPromptPack: "场景策略 Prompt 包",
  labelGatePointer: "发布门禁指针",
} as const;

/** FR-MC801 · eventName 运营简称（契约码见技术对照） */
const MC801_EVENT_LABEL: Record<string, string> = {
  "agent.prompt.binding_resolved": OPS_EVENT_LABEL.promptBindingResolved.label,
  "agent.skill.spec_read": OPS_EVENT_LABEL.skillSpecRead.label,
  "execution.dispatched": "执行已下发",
  "confirmation.required": "待用户确认",
  "user.confirmed": "用户已确认",
  "tool.round_complete": "工具轮次完成",
  "tool.final_failed": "工具最终失败",
  "reconciliation.success": "对账成功",
  "reconciliation.inconclusive": "对账无结论",
  "settlement.failed": "结算失败",
  "exchange.504": "交易所超时",
};

/** transitionTrigger 运营简称（常与 eventName 不同） */
const MC801_TRIGGER_LABEL: Record<string, string> = {
  ...MC801_EVENT_LABEL,
  "prompt.binding_resolved": "Prompt 拼装已绑定",
  "skill.spec_loaded": "技能规范已载入",
};

/** 演示数据 summary 原文 → 运营可读说明 */
const MC801_SUMMARY_LABEL: Record<string, string> = {
  "stepKind:init; accepted→planning": "已受理，进入规划",
  "writePath:typeA": "写路径：等待用户确认",
  "ADR-001 ok; waiting_confirmation→executing": "用户已确认，开始执行",
  "order.submitted; executing→settling": "订单已提交，进入结算",
  "billing eligible; settling→completed": "计费通过，执行完成",
  "order.submitted（演示）": "订单已提交",
  "billing gate; entitlement quota REJECTED": "Capability 配额门禁拒绝（S2）",
  "billing gate; chargeStatus preview REJECTED": "Capability 配额门禁拒绝（S2）",
  "accepted→planning（演示）": "已受理，进入规划",
  "终态不可判; executing→unknown_pending": "终态不可判，待对账",
  "证据不足; settling子路径挂起": "对账证据不足，结算挂起",
  "invocationState:FAILED; executing→failed": "工具调用失败，执行终止",
};

export function labelMc801Event(eventName: string): string {
  return MC801_EVENT_LABEL[eventName] ?? eventName;
}

export function labelMc801TransitionTrigger(trigger: string): string {
  return MC801_TRIGGER_LABEL[trigger] ?? labelMc801Event(trigger);
}

export function labelMc801SummaryText(summary: string): string {
  const trimmed = summary.trim();
  return MC801_SUMMARY_LABEL[trimmed] ?? trimmed;
}

export const MC801_TIMELINE = {
  cardTitle: "状态迁移时间线",
  colTime: "时间",
  colEvent: "事件",
  colSummary: "说明",
  colTrigger: "触发原因",
  tableEmpty: "暂无事件行",
  emptyMessage: "暂无时间线数据",
  emptyApiTable: "暂无时间线事件",
  summaryPromptBinding: "回合开端 Prompt 层已绑定（不含正文）",
  summarySkillSpecOk: "技能规范载入成功",
  summarySkillSpecFail: "技能规范载入失败",
} as const;

export const ORCHESTRATION_SCENARIO = {
  techCollapseLabel: "技术对照（可选展开）",
  labelScenarioId: "场景键",
  labelOrchVersion: "编排版本",
  labelClosureKey: "闭环状态键",
  labelFlowAnchor: "流程锚点（内部）",
  labelSpecRefs: "相关规格路径",
  labelPromptHint: "Prompt 装配说明",
  searchPlaceholder: "场景名称、流程摘要、目标、场景键…",
} as const;

export const EXECUTION_DETAIL = {
  pageTitle: "执行详情",
  labelExecutionId: "执行 ID",
  labelSessionId: "会话 ID",
  labelUserId: "用户 UID",
  labelScenarioId: "场景键",
  labelOrchVersion: "编排版本",
  labelIntent: "意图摘要",
  labelRuntimeStatus: "运行状态",
  labelStage: "当前阶段",
  labelOutcome: "业务终态",
  labelRetries: "重试次数",
  labelCreatedAt: "创建时间",
  labelDuration: "持续时间",
  summaryCardTitle: "执行摘要",
  governanceSectionTitle: "回合治理快照",
  governanceSkillScope: "场景 · 技能范围",
  governancePrompt: "Prompt 拼装",
  governanceSkillSpec: "技能规范载入",
  governanceCanonical: "出站语义检视",
  policyCollapseLabel: "会话策略对照（本环境预览）",
  usageCardTitle: "调用与计费",
  usageTabTools: "工具调用",
  usageTabLlm: "大模型",
  usageTabBilling: "计费记录",
  toolBudgetHint: "本会话工具调用步数（对照执行策略上限）",
  toolBudgetExceeded: "已超出当前会话内配置的工具步数上限，线上可能拒绝继续扩容工具调用。",
  unknownCardTitle: "终态待核对",
  unknownCardBody: "对账未完成，请在执行链路协查中核对日志与时间线。",
  retryReconcile: "对账 / 终态待核对",
  retryTransient: "瞬时故障 · 可重试",
  retryEmpty: "无重试记录",
  recoveryTitle: "恢复与对账",
  recoveryBody: "从日志检索与时间线核对终态；人工恢复操作将在接口就绪后开放。",
  retryAction: "重试（即将支持）",
  obsLink: "执行链路协查",
  backToList: "返回列表",
  tabOverview: "总览",
  tabTimeline: "时间线",
  tabQueue: "任务队列",
  tabEvents: "运行事件",
  tabRetries: "重试",
  tabRecovery: "恢复",
  stepsCardTitle: "执行阶段",
  stepsIntro: "编排机当前阶段快照（与上方状态迁移时间线互补）。",
  signalTimelineTitle: "业务信号时间线",
  signalTimelineIntro: "工具调用、模型与计费等业务侧信号，按时间排序（与上方状态迁移表互补）。",
  signalStart: "执行开始",
  signalTool: "工具",
  signalModel: "模型",
  signalBilling: "计费",
  signalOutcomeRunning: "运行中",
  signalOutcomeFinal: "终态",
  queueEmpty: "暂无关联任务",
  eventsEmpty: "暂无运行事件",
  toolsEmpty: "暂无工具调用",
  llmEmpty: "暂无大模型调用",
  billingEmpty: "暂无计费记录",
  billingMirrorTitle: "核销摘要（权益核销）",
  billingMirrorEmpty: "暂无 ENTITLEMENT_DEBIT 核销记录；写路径可能在 S2 被 Capability 配额阻断。",
  billingMirrorCapability: "Capability",
  billingMirrorDebit: "核销状态",
  billingMirrorTrace: "计费链路 ID",
  billingMirrorSettlement: "结算类型",
  billingMirrorFailure: "失败原因",
  billingMirrorUnits: "扣减单位",
  billingMirrorLedgerLink: "单笔追踪",
  billingMirrorExecLedgerLink: "按执行筛选账单",
  billingMirrorMoreRows: (n: number) => `另有 ${n} 条计费信号，见下方「调用与计费」。`,
  durationRunning: "进行中",
  notFound: "未找到该执行记录",
  missingId: "缺少执行 ID",
} as const;

export const EXECUTION_POLICY_TAB = {
  introMessage: "配置自动执行、人工确认、名义金额与杠杆上限，以及失败与超时策略。",
  introDescription: "当前修改保存在本浏览器会话；正式环境以服务端配置为准。",
} as const;

export const EXECUTION_LIST = {
  tag: "运行运营",
  apiEnabledMessage: "已连接运营观测 API",
  apiEnabledDescription: "列表来自服务端执行检索；支持按场景筛选与分页加载。",
  apiEnabledTechnical:
    "listObservabilityExecutions · 合并检索：u-*→用户、纯数字 10～19 位→执行 ID、点分串→场景键；?scenario= 覆盖场景。",
  loadMoreHint: "仍有下一页，可继续加载",
  loadMoreTechnical: "cursor 分页 · BFF",
} as const;

export const OBSERVABILITY = {
  tag: "执行协查",
  deepLinkRestored: "已从分享链接恢复检索条件",
  filterFooter:
    "检索条件在各视图通用；复制链接可分享当前协查上下文。计费检索支持 traceId（亦可用 traceKey 别名）。",
  filterTraceLabel: "计费链路 ID",
  filterTraceExtra: "与账单列表 billingTraceId 同窗",
  filterTracePlaceholder: "计费链路 ID",
  timelineCardTitle: "执行链路（时间线）",
  timelineLocked: "当前锁定执行",
  timelineEmpty: "输入精确执行 ID，或将列表筛选至仅一条执行，即可查看完整链路与关键节点。",
  narrativeDivider: "业务叙事时间线",
  narrativeHint: "由工具、模型与计费等信号合成的阅读顺序（非 API 原始字段）。",
  lifecycleCardTitle: "按生命周期查看明细",
  auditTabHint: "可按执行 ID 关联资源与操作记录。",
  drawerMc801Section: "状态迁移时间线",
  drawerToolsSection: "工具调用",
  drawerToolsEmpty: "暂无工具调用记录",
  drawerPromptSection: "Prompt 摘要",
  drawerLlmSection: "模型与输出",
  drawerLlmEmpty: "暂无大模型调用记录",
  drawerLlmOutputPending: "完整输出摘要将在接入存储后展示。",
  drawerRiskSection: "风控命中",
  tabAuditHint: "可按执行 ID 关联资源与动作。",
} as const;

/** 权益核销商业闭环 · 五步工作流（配置 → 订单 → 消耗 → 核销） */
export const BILLING_OPERATIONS = {
  title: "商业运营",
  description: "订阅套餐、资源管理、订单与用户消耗（同一页 Tab 切换，减少侧栏项）。",
} as const;

export const BILLING_WORKFLOW = {
  hint: "正向闭环：先配置可售商品，再看订单到账与用户余额，最后在执行维度核对 ENTITLEMENT_DEBIT。",
  steps: [
    { path: "/billing/operations?tab=subscriptions", title: "订阅套餐", description: "档位 · 标价 · 关联资源包" },
    { path: "/billing/operations?tab=packs", title: "资源管理", description: "可售卖资源 CRUD" },
    { path: "/billing/operations?tab=rules", title: "计费规则", description: "Capability · 场景映射" },
    { path: "/billing/operations?tab=orders", title: "订阅订单", description: "Crypto 到账 · Webhook" },
    { path: "/billing/operations?tab=consumption", title: "用户消耗", description: "权益余额 · 消耗流水" },
    { path: "/billing/ledger", title: "执行核销", description: "按 execution 事实" },
  ],
} as const;

export const BILLING_SUBSCRIPTIONS = {
  title: "订阅套餐",
  description:
    "管理对外售卖的订阅档位（套餐 ID · 周期 · 标价）；配额由关联的资源包汇总，不在套餐上手填数字。",
  webAlignHint: "与 Web `/subscription` 商品目录同窗；变更须双签 + PSP 商品同步（生产 MR）。",
  tableTitle: "订阅套餐列表",
  actionEdit: "修改",
  createTitle: "新建订阅套餐",
  editTitle: "修改套餐",
  configHint:
    "勾选本套餐包含的订阅类资源（可多选）；资源条目在「资源管理」维护，扣费桶规则见「计费规则」。",
  saveSuccess: "套餐已保存（演示 · 当前浏览器会话）",
  createSuccess: "套餐已创建",
  validateFailed: "请检查表单必填项",
  tierIdInvalid: "套餐 ID 仅允许数字",
  duplicateTierId: "套餐 ID 已存在，请更换",
  deleteConfirmTitle: "确认删除该套餐？",
  deleteConfirmDesc: "删除后不可恢复（演示环境仅影响当前浏览器会话）。",
  deleteSuccess: "套餐已删除",
  resetSuccess: "已恢复默认档位种子",
} as const;

export const BILLING_RESOURCES = {
  title: "资源管理",
  createTitle: "新建资源",
  editTitle: "修改资源",
  saveSuccess: "资源已保存",
  createSuccess: "资源已创建",
  validateFailed: "请检查表单必填项",
  resourceIdInvalid: "资源 ID 仅允许数字",
  duplicateResourceId: "资源 ID 已存在，请更换",
  deleteConfirmTitle: "确认删除该资源？",
  deleteSuccess: "资源已删除",
} as const;

export const BILLING_RULES = {
  title: "计费规则",
  pageIntro: "只定义扣费规则，不配置配额。",
  pageDetail:
    "周期配额在「资源管理」维护，经套餐/加购入账后写入用户权益。本页仅配置：每次执行扣多少单位、以及各类执行场景归入哪个 Capability 桶。",
  tabDebit: "扣减规则",
  tabMapping: "场景映射",
  debitRuleSectionTitle: "扣减规则",
  debitRuleSectionHint:
    "按能力类型定义核销扣减；周期配额在「资源管理」配置，经套餐/加购入账，不在此维护。",
  colDebitCapability: "能力类型",
  colDebitStandard: "扣减标准",
  debitUnitSuffix: "单位 / 次",
  debitPerSuccessHint: "每次执行核销成功",
  debitEditTitle: "编辑扣减规则",
  debitEditButton: "编辑规则",
  debitFieldDisplayLabel: "对外展示名",
  debitFieldAmount: "扣减标准",
  debitResetSeed: "恢复默认",
  debitResetConfirm: "将扣减规则恢复为系统默认，是否继续？",
  debitSaveSuccess: "扣减规则已保存（本地）",
  debitPushApi: "同步到服务端",
  debitPushApiHint: "将当前扣减规则写入 Capability 目录（须双签；配额字段沿用服务端快照）。",
  mappingSectionHint:
    "按执行场景键决定扣费桶：表内「自动」行为系统默认；其余行可增删改。未命中任何规则时由 Runtime 策略处理。",
  mappingAutoTag: "自动",
  mappingCreateTitle: "新建场景映射",
  mappingEditTitle: "修改场景映射",
  mappingCreateButton: "新建映射",
  mappingResetSeed: "恢复默认",
  mappingResetConfirm: "将可编辑映射恢复为系统默认（自动规则不变），是否继续？",
  mappingCreateSuccess: "场景映射已创建",
  mappingSaveSuccess: "场景映射已保存",
  mappingDeleteSuccess: "场景映射已删除",
  mappingDeleteConfirm: "删除后该场景将按自动规则或 Runtime 策略解析，是否继续？",
  validateFailed: "请检查表单必填项",
  scenarioIdInvalid: "场景键须为小写字母开头，可含数字、点、下划线与连字符",
  duplicateScenarioId: "该场景键已存在",
  colCapability: "归入类型",
  colScenario: "执行场景",
  colActions: "操作",
  localPreviewTag: "本地预览",
} as const;

/** @deprecated 使用 BILLING_RESOURCES */
export const BILLING_PACKS = BILLING_RESOURCES;

export const BILLING_ORDERS = {
  title: "订阅订单",
  description: "订阅升级与加购的加密货币支付订单（只读观测）；SETTLED 后写入用户权益。",
  filterUser: "用户",
  filterOrderId: "订单号",
  filterOrderIdPlaceholder: "纯数字，支持片段",
  statAll: "全部",
  emptyTable: "暂无匹配订单",
  filterStatus: "到账状态",
  filterKind: "订单类型",
  filterProduct: "商品",
  filterNetwork: "支付链",
  filterQuery: "查询",
  filterReset: "重置",
  filterClear: "清除筛选",
  filterResultCount: (n: number) => `共 ${n} 条`,
  filterProductBanner: (id: string) => `仅显示商品 ID ${id} 的订单`,
  statPending: "待支付",
  statConfirming: "确认中",
  statSettled: "已到账",
  statExpired: "已过期",
  colOrderId: "订单号",
  orderIdRuleHint: "纯数字 14～20 位（yyyyMMddHHmmss + 序号）",
  colCreatedAt: "下单时间",
  colUser: "用户",
  colKind: "类型",
  colProduct: "商品",
  colPayment: "支付",
  colStatus: "状态",
  colActions: "操作",
  viewDetail: "详情",
  detailTitle: "订单详情",
  detailSectionOrder: "订单信息",
  detailSectionPayment: "支付信息",
  detailSectionChain: "链上到账",
  detailSectionEntitlement: "权益入账",
  detailListPrice: "目录标价",
  detailExpiresAt: "支付截止",
  detailUserPaymentAddress: "用户支付地址",
  detailPayerAddress: "付款方地址",
  detailCopyAddress: "复制地址",
  detailConfirmations: "链上确认",
  detailPspRef: "PSP 参考号",
  detailSettledAt: "到账时间",
  detailTx: "链上交易",
  detailGrantStatus: "入账状态",
  detailGrantAppliedAt: "入账时间",
  detailPackGrantId: "加购授予 ID",
  detailCapability: "Capability",
  detailQuota: "授予额度",
  detailPeriod: "周期",
  detailTierSku: "生效档位",
  detailPeriodEnd: "订阅周期至",
  detailOpenConsumption: "查看用户权益",
  detailOpenProduct: "查看商品配置",
  packGrantDemo: "演示：手工加购入账",
  packGrantSuccess: "已记录 pack-grants 演示请求（未写真实额度）",
  packGrantHint: "仅演示占位，生产由 PSP Webhook 自动入账",
  localPreviewTag: "本地预览",
} as const;

export const BILLING_CONSUMPTION = {
  title: "用户消耗",
  description: "按 userId 查看订阅状态、Capability 余额与近期 ENTITLEMENT_DEBIT 消耗流水（FR-MC510）。",
  filterUser: "用户",
  queryButton: "查询",
  subscriptionLabel: "当前订阅",
  periodEndLabel: "到期",
  colCapability: "能力类型",
  colRemaining: "剩余额度",
  colTime: "时间",
  colStatus: "核销状态",
  colExecution: "执行",
  recentExecutions: "近期执行：",
  ledgerLink: "核销追踪 →",
  localPreviewTag: "本地预览",
  bucketEmpty: "该用户暂无权益桶数据",
  ledgerTitle: "近期消耗流水",
  ledgerEmpty: "该用户暂无核销记录",
} as const;

export const BILLING_LEDGER = {
  tagLocalPreview: "本地预览",
  description:
    "ENTITLEMENT_DEBIT 核销事实表：按 executionId 查 Capability 核销结果与协查链路。",
  tabLedger: "核销列表",
  tabCorrelate: "单笔追踪",
  listExpandHint: "点击行首展开可查看幂等键后缀、requestId、packGrantId 等工程字段。",
  correlateHitCount: "条匹配结果",
  correlateEmpty: "无匹配；可带线索跳转执行链路协查扩大检索。",
  demoDataTooltip: "本地预览数据，接口未接",
  tagApiConnected: "已接 traces API",
  tagApiFallback: "接口不可用 · 已回退 mock",
} as const;

export const BILLING_OVERVIEW = {
  description: "运行健康与商业到账观测；套餐标价、配额与扣次均在「商业运营」配置。",
  roleSplitTitle: "配置入口",
  roleSplitCommerce: "对用户卖什么、卖多少、怎么扣次 → 商业运营（订阅套餐 · 资源管理 · 计费规则 · 订阅订单）",
  sectionWorkflow: "商业运营入口",
  sectionUsage: "今日运行",
  trendCardTitle: "近 7 日执行量",
  colMonitoring: "监控",
  tokenTodayTitle: "Token（成本观测）",
  sectionHealth: "计费与网关健康",
  billingModeLabel: "清算模式",
  billingModeValue: "仅权益核销",
  gatewayErrorTitle: "网关错误分类",
  commerceSection: "配额阻断",
  commerceQuotaTitle: "近 24h 额度用尽阻断",
  commerceQuotaLink: "商业运营",
  commerceDisabledTitle: "商业轨未启用",
  commerceDisabledBody: "演示环境默认开启；生产需接入 Commerce Admin API。",
} as const;

/** FR-MC502 / FR-MC509 同窗双签（演示） */
export const BILLING_DUAL_SIGN = {
  title: "双签确认",
  body: "演示环境不调用真实审批流；所内须对接 IAM + 审计表。",
  confirm: "确认发布",
  idsRequired: "请填写操作人与复核人标识。",
  distinct: "操作人与复核人不能为同一人。",
  operatorPlaceholder: "操作人（如 ops-a）",
  approverPlaceholder: "复核人（如 fin-b）",
  operatorAck: "我确认本次变更内容正确",
  approverAck: "我作为复核人批准发布",
} as const;

export const BILLING_COMMERCE = {
  title: "订阅与能力包",
  description:
    "订阅档位、Capability 目录、场景映射、用户权益与 Crypto 到账观测（演示）；S5 核销真源为 entitlements/debit。",
  sectionTiers: "订阅档位（FR-MC509 · 套餐矩阵）",
  tiersHint: "标价与含配额同窗用户 Web；变更生产须双签 + PSP 商品同步 MR。",
  sectionCryptoOrders: "加密货币支付订单（演示 · Webhook MR）",
  cryptoOrdersHint: "只读观测用户 checkout；完整支付 UI 在用户 Web，不在运营台发起转账。",
  packGrantDemo: "演示：手工加购入账",
  packGrantSuccess: "已记录 pack-grants 演示请求（未写真实额度）",
  phaseTag: "Commerce · 演示",
  demoBanner: "本地预览 · 未接 Commerce Admin API",
  demoBannerBody: "字段对齐 OpenAPI commerce 包；目录 PATCH 双签为演示，生产 IAM/审计在所内 MR 接入。",
  linkOverview: "计费总览",
  linkPricing: "定价与策略",
  sectionCatalog: "Capability 目录（FR-MC509）",
  catalogHint: "套餐桶与加购包余额快照",
  sectionMapping: "场景 → Capability 映射（FR-MC509）",
  mappingHint: "与 trading-agent-config keys §5、Runtime S2 门禁同窗",
  mappingAnalysisNote:
    "只读分析类场景（analysis.* / market.query / qa.*）映射 cap.agent.analyze；含 monitor 映射 cap.agent.monitoring（见 billingCapabilityMap 小样）。",
  sectionUser: "用户权益协查（FR-MC510）",
  userEmpty: "输入 userId 后展示演示桶",
  userHint: "演示复用总览 Capability 桶；生产 join executionId 见 observability FR-MC503。",
  sectionQuotaHealth: "配额阻断健康（FR-MC512）",
  quotaCardTitle: "S2 阻断聚合",
  sourceMock: "本地预览",
  sourceRemote: "已接 Commerce API",
  sourceRemoteFallback: "接口不可用 · 已回退 mock",
  catalogEditTitle: "编辑 Capability 目录",
  catalogRulesEditTitle: "编辑扣减规则",
  catalogEditSubmit: "提交双签（演示）",
  catalogEditHint:
    "同窗 FR-MC502 双签纪律：生产须操作人与复核人分离；此处仅演示 PATCH capability-catalog，不落真实审计流水。",
  catalogRulesEditHint: "仅可改展示名与每次执行扣减；用户周期配额请在资源管理与套餐中配置。",
  catalogEditApiRequired: "须开启 VITE_USE_BILLING_COMMERCE_API 并配置 VITE_API_BASE_URL 后方可保存。",
  catalogEditValidateFailed: "请检查表单必填项。",
  catalogDualSignTitle: "双签确认（FR-MC509）",
  catalogDualSignBody: "演示环境不调用真实审批流；所内须对接 IAM + 审计表。",
  catalogDualSignConfirm: "确认发布",
  catalogDualSignRequired: "须勾选操作人与复核人确认。",
  catalogDualSignIdsRequired: "请填写操作人与复核人标识。",
  catalogDualSignDistinct: "操作人与复核人不能为同一人。",
  catalogOperatorPlaceholder: "操作人（如 ops-a）",
  catalogApproverPlaceholder: "复核人（如 fin-b）",
  catalogOperatorAck: "我确认本次目录变更内容正确",
  catalogApproverAck: "我作为复核人批准发布",
  catalogSaveSuccess: "目录已更新（演示 PATCH）",
  catalogSaveFailed: "保存失败，请稍后重试",
  catalogConflict: "目录版本冲突（409），请刷新后重试",
} as const;

export const AGENT_GLOBAL_GATE = {
  message: "智能体服务未对客开放",
  description: "暂不可启动或恢复实例；已接入实例仍可批量暂停、停止。",
  configLink: "前往准入管理",
  dismissToday: "今日不再提示",
} as const;

/** 实例管理 · 列表 / 详情 / 筛选 */
export const AGENT_INSTANCES = {
  listDescription: "按用户与运行状态检索实例；支持预览、批量暂停/停止与导出（演示环境不落库）。",
  filterInstantHint: "修改条件后列表即时刷新；「最近活跃」按 UTC 日历日筛选。",
  exportList: "导出列表",
  batchSelected: (n: number) => `已选 ${n} 台实例`,
  batchPause: "批量暂停",
  batchStop: "批量停止",
  modalDemoTitle: "演示说明",
  runtimeQuickContent: (action: string) =>
    `「${action}」在演示环境中不会调用后台接口。服务未开放时，启动与恢复不可用；批量暂停、停止仍可操作。`,
  batchPauseTitle: "批量暂停",
  batchPauseContent: (ids: string) =>
    `将对 ${ids} 下发暂停指令。演示环境仅模拟受理，不会写入生产数据。`,
  batchPauseOk: "确认暂停",
  batchPauseDone: "已模拟批量暂停受理。",
  batchStopTitle: "批量停止",
  batchStopContent: (ids: string) =>
    `将对 ${ids} 下发停止指令。演示环境仅模拟受理，不会写入生产数据。`,
  batchStopOk: "确认停止",
  batchStopDone: "已模拟批量停止受理。",
  exportTitle: "导出实例列表",
  exportContent: (count: number) =>
    `将按当前筛选条件导出 CSV（命中 ${count} 条）。演示环境不生成文件。`,
  modalOk: "知道了",
  startDisabledReason: "智能体服务未开放，暂不可启动",
  resumeDisabledReason: "智能体服务未开放，暂不可恢复运行",
  deleteDisabledReason: "实例启动中，请先停止后再删除",
  detailRuntimeQuick: (action: string) =>
    `「${action}」在演示环境中不会调用后台接口。服务未开放时，启动与恢复不可用。`,
  deleteConfirmTitle: "删除实例",
  deleteConfirmContent: "演示环境仅弹出确认，不会真实删除。生产环境须校验在途执行与持仓。",
  deleteConfirmOk: "确认删除",
  deleteDoneTitle: "演示说明",
  deleteDoneContent: "未删除实例。",
  logsCardTitle: "运行日志",
  logsNoExec: "该用户暂无执行记录，可从执行链路协查按用户检索。",
  logsNoConv: "暂无会话摘要。",
  logsNoTool: "暂无工具调用记录。",
  logsNoError: "暂无失败或阻断类执行记录。",
  logsNoErrorAllOk: "近期执行均为正常终局。",
  summaryCardTitle: "账户与准入",
  bindingCardTitle: "渠道与子账户绑定",
  bindingIntro: "仅展示绑定快照与公开标识，不含密钥。换绑前须先暂停实例并完成审计。",
  bindingLinkStage: "列表阶段",
  bindingAppendixStage: "运营快照",
  bindingNoEvents: "暂无绑定变更记录。",
  bindingEventsTitle: "最近绑定事件",
  paramsCardTitle: "实例覆盖参数",
  paramsIntro: "以下为当前实例的策略覆盖快照（只读）。",
  auditCardTitle: "操作审计",
  auditEmpty: "暂无与本实例相关的审计记录。",
  errSummary: "执行异常摘要",
  membershipLabel: "会员 / 准入等级",
  subAccountListLabel: "子账户（列表）",
  runtimeStateAppendix: "运行状态（快照）",
} as const;

export const EXECUTION_POLICY_DEV = {
  collapseLabel: "技术对照（契约字段镜像）",
  collapseIntro: "与运行编排、重试策略等规格对签；生产配置以服务端与 OpenAPI 为准。",
} as const;

export const PROMPT_EDITOR_EXTRA = {
  skillScopeEmptyInferred: "—（可由场景推断）",
} as const;
