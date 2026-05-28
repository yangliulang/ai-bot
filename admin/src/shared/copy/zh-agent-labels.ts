/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-14
 * 修改功能: **`OPERATIONAL`** 门禁中文；附录 A 聚合态补充
 * 日期: 2026-05-12
 * 修改功能: Agent 实例门禁/运行态/子账户中文标签（与 product-doc zhLabels 对齐）
 */

const AGENT_STATE: Record<string, string> = {
  OPERATIONAL: '可运营',
  NORMAL: '正常',
  BILLING_BLOCKED: '计费受限',
  GLOBAL_OFF: '总闸关闭',
  OPS_SUSPENDED: '运营熔断',
  MEMBERSHIP_BLOCKED: '会员/准入受限',
  AGENT_SUBACCOUNT_BLOCKED: '子账户受阻',
}

const RUNTIME_STATE: Record<string, string> = {
  RUNNING: '运行中',
  PAUSED: '已暂停',
  STOPPED: '已停止',
  STARTING: '启动中',
  ERROR: '异常',
}

const SUB_ACCOUNT_LINK: Record<string, string> = {
  LINKED: '已关联',
  PENDING: '待关联',
  NONE: '未关联',
}

export function zhAgentState(s: string): string {
  return AGENT_STATE[s] ?? s
}

export function zhRuntimeState(s: string): string {
  return RUNTIME_STATE[s] ?? s
}

export function zhSubAccountStatus(s: string): string {
  return SUB_ACCOUNT_LINK[s] ?? s
}
