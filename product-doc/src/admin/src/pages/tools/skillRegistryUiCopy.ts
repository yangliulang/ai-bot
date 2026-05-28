/**
 * 技能与工具 · 控制台用户可见文案（运营/产品向，非工程术语）。
 */

export const SKILL_REGISTRY_PAGE = {
  title: "技能与工具",
  tagTrading: "可下单技能",
  tagPreview: "预览环境",
  description:
    "管理智能体可帮用户完成的下单类技能，以及查询类、外网类工具。点击表格中的技能行，在右侧查看用户流程与对话要求。",
  resetButton: "恢复默认开关",
  resetSuccess: "已恢复默认启用状态，并清空变更记录",
  statTradingEnabled: "可下单技能 · 已启用",
  statToolsEnabled: "查询与外部工具 · 已启用",
  statAudit: "开关变更记录",
  tabTrading: "可帮用户下单",
  tabReadonly: "查询类工具",
  tabExternal: "外部检索",
  tabAudit: "变更记录",
  searchPlaceholder: "搜索技能名称、用户流程或下单方式",
  enableWarning: "该技能尚未对用户开放，预览环境下不建议开启",
  cardTitle: "能力清单",
} as const;

export const TOOL_REGISTRY_TABLE = {
  colTool: "工具",
  colDesc: "能做什么",
  colStatus: "状态",
  colEnabled: "是否启用",
  auditTime: "时间",
  auditType: "类型",
  auditId: "名称",
  auditAction: "变更",
  auditActor: "操作人",
  auditEmpty: "尚无开关变更",
  listEmpty: "暂无数据",
} as const;

export const SKILL_TABLE = {
  colSkill: "技能",
  colUserFlow: "用户怎么用",
  colScenarios: "适用场景",
  colExchange: "实际下单方式",
  colEnabled: "是否启用",
  empty: "没有匹配的技能",
} as const;

export const SKILL_DRAWER = {
  fallbackTitle: "技能说明",
  switchHint: "点击列表中的其他技能，可切换查看",
  copyId: "复制技能编号",
  copySuccess: "已复制技能编号",
  copyFail: "复制失败，请手动选择复制",
  close: "关闭",
  tabOverview: "概览",
  tabSpec: "对话与下单要求",
  labelSkillId: "技能编号",
  labelVersion: "规范版本",
  labelScenario: "主场景",
  labelMatrix: "能力开放",
  labelPreviewEnabled: "预览启用",
  labelContract: "规范完整度",
  labelBusiness: "业务说明",
  labelSpecQuickNav: "规范分段",
  enabledOn: "已启用",
  enabledOff: "未启用",
  contractComplete: "§1～§6 已齐",
  contractIncomplete: "正文待补全",
  contractNa: "无 Git 正文",
  labelUserFlow: "用户怎么用",
  labelExchange: "实际下单方式",
  viewConfirmDetail: "查看全部",
  viewAllParams: (more: number) => `还有 ${more} 项`,
  requiredSummary: (required: number, total: number) =>
    `其中 ${required} 项为必填 · 共 ${total} 项参数`,
  gotoSpec: "查看对话与下单要求",
  loading: "正在加载说明…",
  emptySpec: "该技能暂无详细的对话与下单说明。",
  emptyEntry: "未找到该技能",
  rawCollapse: "查看完整原文（研发对照）",
} as const;

export const SKILL_MATRIX_STATUS = {
  frozen: "已开放",
  tbd: "暂未开放",
  draft: "规划中",
} as const;

export type SkillSpecSectionKey =
  | "params"
  | "validation"
  | "confirm"
  | "unknown"
  | "refusal"
  | "api";

export const SKILL_SPEC_SECTION = {
  params: { label: "需要的信息", title: "需要向用户收集哪些信息" },
  validation: { label: "校验规则", title: "下单前须满足的条件" },
  confirm: { label: "确认内容", title: "二次确认时要展示什么" },
  unknown: { label: "待澄清", title: "信息不全时如何追问" },
  refusal: { label: "不予办理", title: "什么情况下不能代办" },
  api: { label: "对接交易所", title: "会调用哪些交易所能力" },
} as const;

export const SKILL_OVERVIEW_METRICS = {
  required: "必填项",
  validation: "校验条数",
  confirm: "确认展示项",
  refusal: "拒答情形",
  unitItem: "项",
  unitRule: "条",
} as const;

export const SKILL_SPEC_EMPTY = {
  params: "暂无参数说明",
  validation: "暂无校验说明",
  confirm: "暂无确认项说明",
  unknown: "暂无追问说明",
  refusal: "暂无拒答说明",
  api: "暂未说明对接方式",
  noConfirmFields: "暂无需要在确认卡展示的字段",
} as const;

export const SKILL_SPEC_NOTE = {
  orchestration: "对话前注意",
} as const;
