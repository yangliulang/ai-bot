/*
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 注释对齐多页 onboarding（/onboarding/validate 等）复用 OpenAPI 基准
日期: 2026-05-11
修改功能: Coobit 交易所 OpenAPI 基准 URL 默认值与会话持久化键（对齐 GitBook 文档说明的 base URL 概念）
 */
/**
 * GitBook「API Basic Information」中与 **REST 网关**对应的 **baseurl** 形如
 * [`https://openapi.xxx.xx`](https://exchangedocsv2.gitbook.io/open-api-doc-v2)（占位）。
 * Coobit 环境下默认 **`openapi.` + 主站域**（非 `www` 首页）；线上真源以运维/所内网关为准。
 */
export const DEFAULT_OPENAPI_BASE_URL = 'https://openapi.coobit.cc'

/** sessionStorage：onboarding 校验页与后续步骤复用基准地址（仅本浏览器标签会话）。 */
export const OPENAPI_BASE_STORAGE_KEY = 'chainup-deeplink-openapi-base-v1'

/**
 * 归一化为可拼 path 的根地址：去尾部 `/`，保留 path 前缀（若有）。
 * 非法输入时回退为 {@link DEFAULT_OPENAPI_BASE_URL}。
 */
export function normalizeOpenapiBaseUrl(raw: string): string {
  const t = raw.trim()
  const fallback = DEFAULT_OPENAPI_BASE_URL
  if (!t) return fallback
  try {
    const withScheme = /^https?:\/\//i.test(t) ? t : `https://${t}`
    const u = new URL(withScheme)
    if (u.protocol !== 'http:' && u.protocol !== 'https:') return fallback
    const path = u.pathname.replace(/\/+$/, '')
    if (!path || path === '/') return u.origin
    return `${u.origin}${path}`
  } catch {
    return fallback
  }
}

/** 用于输入框失焦校验提示（不改变内部值时返回 false）。 */
export function isProbablyValidOpenapiBaseUrl(raw: string): boolean {
  const t = raw.trim()
  if (!t) return true
  try {
    const withScheme = /^https?:\/\//i.test(t) ? t : `https://${t}`
    const u = new URL(withScheme)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}

/** 供非 Vue 组件或路由页读取当前会话配置的基准地址。 */
export function readStoredOpenapiBaseUrl(): string {
  try {
    const s = sessionStorage.getItem(OPENAPI_BASE_STORAGE_KEY)?.trim()
    if (s) return normalizeOpenapiBaseUrl(s)
  } catch {
    // ignore
  }
  return DEFAULT_OPENAPI_BASE_URL
}
