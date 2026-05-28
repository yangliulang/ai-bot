/*
作者: 杨永的Agent
日期: 2026-05-20
修改功能: Bot 默认链接按环境区分（dev → yangliulang_bot · prod → chainup_online_ai_bot）
作者: 杨永的Agent
日期: 2026-05-12
修改功能: buildTelegramInboundPayload（随校验/绑定 POST 提交 telegram 上下文，snake_case 与 query 对齐）
日期: 2026-05-11
修改功能: Telegram Deeplink 预填工具（query 解析；空预填 / merge / effective；开通账号名与 Bot URL）
 */
const ACCOUNT_SUFFIX_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

/** 占位：正式上线由服务端下发助手子账户标识 */
export function generateAssistantAccountName(): string {
  const alphabet = ACCOUNT_SUFFIX_ALPHABET
  const pick = (): string =>
    alphabet[Math.floor(Math.random() * alphabet.length)] ?? '?'
  let suffix = ''
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
      const bytes = new Uint8Array(6)
      crypto.getRandomValues(bytes)
      for (let i = 0; i < bytes.length; i++) {
        suffix += alphabet[bytes[i]! % alphabet.length]
      }
    }
  } catch {
    suffix = ''
  }
  if (!suffix) suffix = Array.from({ length: 6 }, pick).join('')
  return `助手-${suffix}`
}

/** 本地 / `vite dev` 默认 Bot */
export const TELEGRAM_BOT_URL_DEV = 'https://t.me/yangliulang_bot'
/** 生产构建（`vite build`）默认 Bot */
export const TELEGRAM_BOT_URL_PROD = 'https://t.me/chainup_online_ai_bot'

/** 未配置 `VITE_TELEGRAM_BOT_URL` 时按 `import.meta.env.PROD` 选择默认 Bot */
export function defaultTelegramBotUrl(): string {
  const envUrl = import.meta.env.VITE_TELEGRAM_BOT_URL?.trim()
  if (envUrl) return envUrl
  return import.meta.env.PROD ? TELEGRAM_BOT_URL_PROD : TELEGRAM_BOT_URL_DEV
}

export function telegramBotOpenUrlFromSearch(searchParams: URLSearchParams): string {
  const fromQuery = searchParams.get('tg_bot')?.trim()
  if (fromQuery && /^https:\/\/t\.me\//i.test(fromQuery)) return fromQuery
  return defaultTelegramBotUrl()
}

export function normalizeTelegramUsername(raw: string): string {
  const t = raw.trim()
  if (!t) return ''
  const handle = t.startsWith('@') ? t.slice(1) : t
  if (!handle) return ''
  return `@${handle}`
}

/** Phase1 bind URL query from ``application.telegram_inbound`` (see ``server/docs/BACKEND_SPEC.md`` §3.1). */
export type TelegramDeeplinkPrefill = {
  tgId: string
  tgUsername: string
  firstName: string
  lastName: string
  languageCode: string
}

/** 与入站 query 键名一致，供 POST JSON 的 `telegram` 字段（全 optional；服务端 /be 可再收敛 schema） */
export type TelegramInboundPayload = {
  tg_id?: string
  tg_username?: string
  tg_first_name?: string
  tg_last_name?: string
  tg_lang?: string
}

export function emptyTelegramDeeplinkPrefill(): TelegramDeeplinkPrefill {
  return { tgId: '', tgUsername: '', firstName: '', lastName: '', languageCode: '' }
}

/** Non-empty fields in ``patch`` override ``base`` (URL / 新会话链优先覆盖). */
export function mergeTelegramDeeplinkPrefill(
  base: TelegramDeeplinkPrefill,
  patch: TelegramDeeplinkPrefill,
): TelegramDeeplinkPrefill {
  return {
    tgId: patch.tgId || base.tgId,
    tgUsername: patch.tgUsername || base.tgUsername,
    firstName: patch.firstName || base.firstName,
    lastName: patch.lastName || base.lastName,
    languageCode: patch.languageCode || base.languageCode,
  }
}

/** 持久化态 + 当前路由 query：同名字段以路由为准（非空时）. */
export function effectiveTelegramPrefill(
  persisted: TelegramDeeplinkPrefill,
  routeQuery: Record<string, unknown>,
): TelegramDeeplinkPrefill {
  return mergeTelegramDeeplinkPrefill(persisted, telegramDeeplinkPrefillFromRouteQuery(routeQuery))
}

export function telegramDeeplinkPrefillFromRouteQuery(raw: Record<string, unknown>): TelegramDeeplinkPrefill {
  const one = (key: string): string => {
    const v = raw[key]
    if (v == null) return ''
    if (Array.isArray(v)) return String(v[0] ?? '').trim()
    return String(v).trim()
  }
  return {
    tgId: one('tg_id'),
    tgUsername: one('tg_username'),
    firstName: one('tg_first_name'),
    lastName: one('tg_last_name'),
    languageCode: one('tg_lang'),
  }
}

/**
 * Stable display for onboarding: prefer normalized @username; otherwise a non-spoofing id label.
 * Legacy query keys (`tg_username`, `telegram_username`, `tg_user`) are handled by the caller for precedence.
 */
export function telegramDisplayHandleFromPrefill(
  prefill: TelegramDeeplinkPrefill,
  normalizedLegacyUsername: string,
): string {
  if (normalizedLegacyUsername) return normalizedLegacyUsername
  const u = prefill.tgUsername.trim()
  if (u) return normalizeTelegramUsername(u)
  const idPart = prefill.tgId.trim()
  if (idPart) return `TG id ${idPart}（未公开用户名）`
  return ''
}

/**
 * 从会话/URL 预填与 legacy 用户名构造服务端负载；无任一字段则 `undefined`（不传 `telegram`）。
 * `legacyUsernamePlain`：`telegram_username` / `tg_user` 等 query（可带或不带 @）。
 */
export function buildTelegramInboundPayload(
  prefill: TelegramDeeplinkPrefill,
  legacyUsernamePlain?: string,
): TelegramInboundPayload | undefined {
  const o: TelegramInboundPayload = {}
  const id = prefill.tgId.trim()
  if (id) o.tg_id = id
  const uPref = prefill.tgUsername.trim().replace(/^@/, '')
  const uLeg = (legacyUsernamePlain ?? '').trim().replace(/^@/, '')
  const u = uPref || uLeg
  if (u) o.tg_username = u
  const fn = prefill.firstName.trim()
  if (fn) o.tg_first_name = fn
  const ln = prefill.lastName.trim()
  if (ln) o.tg_last_name = ln
  const lang = prefill.languageCode.trim()
  if (lang) o.tg_lang = lang
  return Object.keys(o).length > 0 ? o : undefined
}
