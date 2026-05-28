import { describe, expect, it } from 'vitest'

import {
  runtimeParamsFromUxForm,
  TELEGRAM_RUNTIME_KEYS,
  uxFormFromRuntimeParams,
  type TelegramChannelUxForm,
} from '../telegram-runtime-params'

describe('telegram-runtime-params welcome trilingual', () => {
  it('maps three welcome keys from runtimeParams', () => {
    const form = uxFormFromRuntimeParams({
      [TELEGRAM_RUNTIME_KEYS.welcomeZhCn]: '简体',
      [TELEGRAM_RUNTIME_KEYS.welcomeZhTw]: '繁體',
      [TELEGRAM_RUNTIME_KEYS.welcomeEn]: 'Hello',
    })
    expect(form.welcomeZhCn).toBe('简体')
    expect(form.welcomeZhTw).toBe('繁體')
    expect(form.welcomeEn).toBe('Hello')
  })

  it('writes all three welcome keys on PATCH payload', () => {
    const form: TelegramChannelUxForm = {
      tradeOk: true,
      autoExec: false,
      voiceOk: false,
      fileOk: true,
      defaultLocale: 'zh-CN',
      welcomeZhCn: '欢迎 {displayName}',
      welcomeZhTw: '歡迎 {displayName}',
      welcomeEn: 'Hi {displayName}',
      deepLinkTemplate: '',
    }
    const params = runtimeParamsFromUxForm(form)
    expect(params[TELEGRAM_RUNTIME_KEYS.welcomeZhCn]).toBe('欢迎 {displayName}')
    expect(params[TELEGRAM_RUNTIME_KEYS.welcomeZhTw]).toBe('歡迎 {displayName}')
    expect(params[TELEGRAM_RUNTIME_KEYS.welcomeEn]).toBe('Hi {displayName}')
  })
})
