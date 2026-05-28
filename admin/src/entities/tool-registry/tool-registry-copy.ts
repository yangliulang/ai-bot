/** 技能与工具 · 控制台文案（对齐 product-doc skillRegistryUiCopy） */

export const SKILL_REGISTRY_PAGE = {
  title: '技能与工具',
  tagTrading: '可下单技能',
  tagPreview: '预览环境',
  description:
    '管理智能体可帮用户完成的下单类技能，以及查询类、外网类工具。点击表格中的技能行，在右侧查看用户流程与对话要求。',
  resetButton: '恢复默认开关',
  resetSuccess: '已恢复默认启用状态，并清空变更记录',
  alertTitle: '预览说明',
  alertDescription:
    '本页为产品预览：启用开关仅保存在当前浏览器，不会同步到线上环境。点击技能行可在右侧查看详情。',
  statTradingEnabled: '可下单技能 · 已启用',
  statSpecReady: '说明文档已就绪',
  statToolsEnabled: '查询与外部工具 · 已启用',
  statAudit: '开关变更记录',
  tabTrading: '可帮用户下单',
  tabReadonly: '查询类工具',
  tabExternal: '外部检索',
  tabAudit: '变更记录',
  searchPlaceholder: '搜索技能名称、用户流程或下单方式',
  filterPublishedOnly: '仅 Runtime 已发布',
  enableWarning: '该技能尚未对用户开放，预览环境下不建议开启',
  cardTitle: '能力清单',
} as const

export const SKILL_REGISTRY_RUNTIME = {
  statPublished: 'Runtime 已发布',
} as const

export const TOOL_REGISTRY_TABLE = {
  colTool: '工具',
  colDesc: '能做什么',
  colStatus: '状态',
  colEnabled: '是否启用',
  auditTime: '时间',
  auditType: '类型',
  auditId: '名称',
  auditAction: '变更',
  auditActor: '操作人',
  auditEmpty: '尚无开关变更',
} as const

export const SKILL_TABLE = {
  colSkill: '技能',
  colUserFlow: '用户怎么用',
  colExchange: '实际下单方式',
  colEnabled: '是否启用',
  empty: '没有匹配的技能',
} as const

export const SKILL_DRAWER = {
  fallbackTitle: '技能说明',
  switchHint: '点击列表中的其他技能，可切换查看',
  copyId: '复制技能编号',
  copySuccess: '已复制技能编号',
  copyFail: '复制失败，请手动选择复制',
  close: '关闭',
  tabOverview: '概览',
  tabSpec: '对话与下单要求',
  labelUserFlow: '用户怎么用',
  labelExchange: '实际下单方式',
  gotoSpec: '查看对话与下单要求',
  loading: '正在加载说明…',
  emptySpec: '该技能暂无详细的对话与下单说明。',
  emptyEntry: '未找到该技能',
  rawCollapse: '查看完整原文（研发对照）',
  publishRequired: '需正式上线',
  registerOnly: '仅备案、不对用户开放',
  version: (v: string) => `版本 ${v}`,
  runtimePublished: 'Runtime 已发布',
  runtimeDraft: 'Runtime 未发布',
  publishRuntime: '发布到 Runtime',
  publishRuntimeHint:
    '将 Git 全文快照写入本地 Runtime 存储（演示）；生产由 prompt-management API 落库。',
  publishSuccess: '已发布，编排可通过 read_skill_operation_spec 读取',
  publishFail: '发布失败',
  publishGate: '说明未齐全，无法发布',
  publishAlready: '当前 Git 版本已在 Runtime 生效',
  publishing: '发布中…',
} as const

export const SKILL_CONTRACT_STATUS = {
  complete: '说明已齐全',
  missing: '说明待完善',
  na: '暂无详细说明',
} as const

export const SKILL_MATRIX_STATUS = {
  frozen: '已开放',
  tbd: '暂未开放',
  draft: '规划中',
} as const

export type SkillSpecSectionKey =
  | 'params'
  | 'validation'
  | 'confirm'
  | 'unknown'
  | 'refusal'
  | 'api'

export const SKILL_SPEC_SECTION = {
  params: { label: '需要的信息', title: '需要向用户收集哪些信息' },
  validation: { label: '校验规则', title: '下单前须满足的条件' },
  confirm: { label: '确认内容', title: '二次确认时要展示什么' },
  unknown: { label: '待澄清', title: '信息不全时如何追问' },
  refusal: { label: '不予办理', title: '什么情况下不能代办' },
  api: { label: '对接交易所', title: '会调用哪些交易所能力' },
} as const

export const SKILL_OVERVIEW_METRICS = {
  required: '必填项',
  validation: '校验条数',
  confirm: '确认展示项',
  refusal: '拒答情形',
  unitItem: '项',
  unitRule: '条',
} as const

export const SKILL_SPEC_EMPTY = {
  params: '暂无参数说明',
  validation: '暂无校验说明',
  confirm: '暂无确认项说明',
  unknown: '暂无追问说明',
  refusal: '暂无拒答说明',
  api: '暂未说明对接方式',
  noConfirmFields: '暂无需要在确认卡展示的字段',
} as const

export const SKILL_SPEC_NOTE = {
  orchestration: '对话前注意',
} as const
