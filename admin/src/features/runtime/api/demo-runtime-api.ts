import { demoObsExecutions, getDemoExecution } from '@/shared/demo/runtime-mock'

/**
 * 首阶段：本地 Demo 数据集。后续替换为 `GET /api/v1/admin/...`（见 api-surface TBD）。
 */
export async function fetchDemoExecutions(): Promise<typeof demoObsExecutions> {
  await Promise.resolve()
  return demoObsExecutions
}

export async function fetchDemoExecutionById(id: string) {
  await Promise.resolve()
  return getDemoExecution(id)
}
