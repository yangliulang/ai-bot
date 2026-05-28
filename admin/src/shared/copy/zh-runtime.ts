/** 运行时状态/阶段等中文展示（运营屏） */

const RUNTIME_STATUS_ZH: Record<string, string> = {
  CREATED: '已创建',
  RUNNING: '运行中',
  COMPLETED: '已完成',
  UNKNOWN: '未决',
  FAILED: '失败',
  BLOCKED: '阻断',
  /** `agent_execution` 持久化状态（Admin Observability） */
  ACCEPTED: '已接受',
  SUCCEEDED: '已成功',
  CANCELLED: '已取消',
}

const STAGE_ZH: Record<string, string> = {
  CREATED: '已创建',
  CONFIRM_PENDING: '待确认',
  RUNNING: '执行中',
  COMPLETED: '已完成',
  BILLING_GATE: '计费门禁',
  RECONCILING: '对账中',
  RECOVERING: '恢复中',
  TOOL_FAILED: '工具失败',
}

const TASK_STATE_ZH: Record<string, string> = {
  PENDING: '待调度',
  RUNNING: '运行中',
  BLOCKED: '阻塞',
}

const TOOL_STATE_ZH: Record<string, string> = {
  SUCCEEDED: '成功',
  FAILED: '失败',
  PENDING: '进行中',
}

export function zhExecutionRuntimeStatus(s: string): string {
  return RUNTIME_STATUS_ZH[s] ?? s
}

export function zhExecutionStage(s: string): string {
  return STAGE_ZH[s] ?? s
}

export function zhTaskState(s: string): string {
  return TASK_STATE_ZH[s] ?? s
}

export function zhToolInvocation(s: string): string {
  return TOOL_STATE_ZH[s] ?? s
}

export function zhChargeStatus(s: string): string {
  if (s === 'SETTLED') return '已结算'
  if (s === 'REJECTED') return '拒绝'
  if (s === 'PENDING') return '待定'
  return s
}

/** 执行详情 · 运行事件 `eventType`（持久化名 · 未知回退原文） */
const RUNTIME_EVENT_TYPE_ZH: Record<string, string> = {
  'execution.created': '执行已创建',
  'execution.accept': '执行已接受',
  'execution.finalize': '执行已终结',
  'execution.dispatched': '执行已派发',
  'confirm.pending': '待用户确认',
  'confirmation.required': '需要确认',
  'confirmation.accepted': '用户已确认',
  'tool.started': '工具已开始',
  'tool.succeeded': '工具已成功',
  'tool.failed': '工具已失败',
  'agent.tool.invoked': '工具已调用',
  'llm.completed': '模型调用完成',
  'llm.chat.faq': '闲聊模型调用',
  'billing.preflight.failed': '计费预检失败',
  'reconciliation.completed': '对账已完成',
  'order.pending': '订单待处理',
  'retry.started': '重试已开始',
  'trading.exchange_private': '交易所私有接口',
  'trading.exchange_public': '交易所公开接口',
  'trading.reconcile': '交易对账',
  'agent.execution.step': '执行步骤',
  'agent.prompt.binding_resolved': 'Prompt 绑定已解析',
  'agent.skill.spec_read': 'Skill 规范已读取',
  'llm.agent.runtime.runtime_clarify': '运行时澄清（LLM 润色）',
  'agent.memory.session_cleared': '会话记忆已清空（STM）',
  'agent.memory.ltm_revoke_requested': '长期记忆撤销已请求（LTM）',
  'agent.memory.resume_classified': 'Resume 分类（resume_classified）',
  'prompt.snapshot': 'Prompt 快照',
  'routing.read.failed': '只读路由失败',
}

export function zhRuntimeEventType(s: string): string {
  const key = s.trim()
  if (!key) return '—'
  return RUNTIME_EVENT_TYPE_ZH[key] ?? key
}

/** API 时点（UTC）→ 运营墙钟 / UTC · 详见 `@/shared/lib/admin-datetime-display` */
export { formatAdminApiTime as formatIsoTime } from '@/shared/lib/admin-datetime-display'
