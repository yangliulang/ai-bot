/**
 * Telegram Bot PATCH `runtimeParams` 键名与表单互转（对齐 keys.md §4.2 · FR-TG-ADMIN-02/06）。
 * 作者: 杨永的Agent
 * 日期: 2026-05-20
 * 修改: 2026-05-26 — 开通欢迎语三语独立字段（2026-05-26--telegram-welcome AC-8）
 */

/** 服务端 `runtimeParams` / `configKey`（camelCase 响应中的键名保持 TELEGRAM_*） */
export const TELEGRAM_RUNTIME_KEYS = {
  defaultLocale: 'TELEGRAM_DEFAULT_LOCALE',
  helpH5UrlTemplate: 'TELEGRAM_HELP_H5_URL_TEMPLATE',
  welcomeZhCn: 'TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN',
  welcomeZhTw: 'TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_TW',
  welcomeEn: 'TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_EN',
  /** §3 渠道能力（FE_HANDOFF 演示项；所内消费键名待 /be 与 keys.md 冻结） */
  channelTradeOk: 'TELEGRAM_CHANNEL_TRADE_OK',
  channelAutoExec: 'TELEGRAM_CHANNEL_AUTO_EXEC_OK',
  channelVoiceOk: 'TELEGRAM_CHANNEL_VOICE_OK',
  channelFileOk: 'TELEGRAM_CHANNEL_FILE_OK',
} as const

export type TelegramUiLocale = 'zh-CN' | 'zh-TW' | 'en-US'

export interface TelegramChannelUxForm {
  tradeOk: boolean
  autoExec: boolean
  voiceOk: boolean
  fileOk: boolean
  defaultLocale: TelegramUiLocale
  /** 开通欢迎语 · 简体中文 */
  welcomeZhCn: string
  /** 开通欢迎语 · 繁体中文 */
  welcomeZhTw: string
  /** 开通欢迎语 · English */
  welcomeEn: string
  deepLinkTemplate: string
}

export const DEFAULT_TELEGRAM_CHANNEL_UX: TelegramChannelUxForm = {
  tradeOk: true,
  autoExec: false,
  voiceOk: false,
  fileOk: true,
  defaultLocale: 'zh-CN',
  welcomeZhCn: '',
  welcomeZhTw: '',
  welcomeEn: '',
  deepLinkTemplate: '',
}

function strParam(params: Record<string, unknown> | undefined, key: string): string | undefined {
  const v = params?.[key]
  return typeof v === 'string' ? v : undefined
}

function boolParam(params: Record<string, unknown> | undefined, key: string): boolean | undefined {
  const v = params?.[key]
  if (typeof v === 'boolean') return v
  if (v === 'true') return true
  if (v === 'false') return false
  return undefined
}

/** BCP-47（产品 effectiveLocale 子集）→ 控制台 Select 值 */
export function bcp47ToUiLocale(bcp: string | undefined): TelegramUiLocale {
  const x = (bcp || '').trim().toLowerCase()
  if (x === 'zh-hant' || x === 'zh-tw') return 'zh-TW'
  if (x === 'en' || x === 'en-us') return 'en-US'
  return 'zh-CN'
}

export function uiLocaleToBcp47(ui: TelegramUiLocale): string {
  if (ui === 'zh-TW') return 'zh-Hant'
  if (ui === 'en-US') return 'en'
  return 'zh-Hans'
}

export function uxFormFromRuntimeParams(
  params: Record<string, unknown> | undefined,
): TelegramChannelUxForm {
  const base = { ...DEFAULT_TELEGRAM_CHANNEL_UX }
  if (!params) return base

  return {
    tradeOk: boolParam(params, TELEGRAM_RUNTIME_KEYS.channelTradeOk) ?? base.tradeOk,
    autoExec: boolParam(params, TELEGRAM_RUNTIME_KEYS.channelAutoExec) ?? base.autoExec,
    voiceOk: boolParam(params, TELEGRAM_RUNTIME_KEYS.channelVoiceOk) ?? base.voiceOk,
    fileOk: boolParam(params, TELEGRAM_RUNTIME_KEYS.channelFileOk) ?? base.fileOk,
    defaultLocale: bcp47ToUiLocale(strParam(params, TELEGRAM_RUNTIME_KEYS.defaultLocale)),
    welcomeZhCn: strParam(params, TELEGRAM_RUNTIME_KEYS.welcomeZhCn) ?? '',
    welcomeZhTw: strParam(params, TELEGRAM_RUNTIME_KEYS.welcomeZhTw) ?? '',
    welcomeEn: strParam(params, TELEGRAM_RUNTIME_KEYS.welcomeEn) ?? '',
    deepLinkTemplate:
      strParam(params, TELEGRAM_RUNTIME_KEYS.helpH5UrlTemplate) ?? base.deepLinkTemplate,
  }
}

export function runtimeParamsFromUxForm(form: TelegramChannelUxForm): Record<string, unknown> {
  return {
    [TELEGRAM_RUNTIME_KEYS.defaultLocale]: uiLocaleToBcp47(form.defaultLocale),
    [TELEGRAM_RUNTIME_KEYS.helpH5UrlTemplate]: form.deepLinkTemplate.trim(),
    [TELEGRAM_RUNTIME_KEYS.channelTradeOk]: form.tradeOk,
    [TELEGRAM_RUNTIME_KEYS.channelAutoExec]: form.autoExec,
    [TELEGRAM_RUNTIME_KEYS.channelVoiceOk]: form.voiceOk,
    [TELEGRAM_RUNTIME_KEYS.channelFileOk]: form.fileOk,
    [TELEGRAM_RUNTIME_KEYS.welcomeZhCn]: form.welcomeZhCn.trim(),
    [TELEGRAM_RUNTIME_KEYS.welcomeZhTw]: form.welcomeZhTw.trim(),
    [TELEGRAM_RUNTIME_KEYS.welcomeEn]: form.welcomeEn.trim(),
  }
}
