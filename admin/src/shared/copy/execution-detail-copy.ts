// 作者: 杨永的Agent
// 日期: 2026-05-27
// 修改功能: 执行详情文案 SSOT（对齐 product-doc opsPanelHints EXECUTION_DETAIL）

export const EXECUTION_DETAIL_COPY = {
  pageTitle: '执行详情',
  summaryCardTitle: '执行摘要',
  labelExecutionId: '执行 ID',
  labelUserId: '用户 UID',
  labelScenarioId: '场景键',
  labelRuntimeStatus: '运行状态',
  labelChannel: '渠道',
  labelSource: '来源',
  labelNote: '备注',
  labelPromptPackVersion: 'Prompt 版本',
  labelPromptBinding: 'Prompt 绑定摘要',
  labelCreatedAt: '创建时间',
  labelUpdatedAt: '更新时间',
  tabOverview: '总览',
  tabTimeline: '时间线',
  tabQueue: '任务队列',
  tabEvents: '运行事件',
  tabRetries: '重试',
  tabRecovery: '恢复',
  queueEmpty: '暂无关联任务',
  eventsEmpty: '暂无运行事件',
  retryEmpty: '无重试记录',
  recoveryTitle: '恢复与对账',
  recoveryBody: '从日志检索与时间线核对终态；人工恢复操作将在接口就绪后开放。',
  retryAction: '重试（即将支持）',
  obsLink: '执行链路协查',
  backToList: '返回列表',
  memoryStmHintTitle: '会话记忆（STM）',
  memoryLtmHintTitle: '长期记忆（LTM）',
} as const

export {
  MEMORY_LTM_REVOKE_USER_HINT,
  MEMORY_STM_CLEAR_USER_HINT,
} from '@/shared/lib/write-path-display'
