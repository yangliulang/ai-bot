/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-14
 * 修改功能: 实例日志 API 返回的 **`observability*Path`** → SPA **`/runtime/executions`** 路由（FE_HANDOFF L01–L03）
 */

/** 将后端 **`…/observability/executions/{id}`**（可选 **`/timeline`**）映射到执行详情 **时间线** Tab */
export function observabilityAdminApiPathToRouteHref(apiPath: string): string {
  const m = apiPath.trim().match(/\/observability\/executions\/([^/?]+)/i)
  if (!m?.[1]) return '/observability'
  const id = encodeURIComponent(m[1])
  return `/runtime/executions/${id}?tab=timeline`
}
