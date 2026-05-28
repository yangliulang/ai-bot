/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 服务端 API 前缀（通常为 ''，经 Vite 代理转发） */
  readonly VITE_API_BASE_URL?: string
  /** Telegram Bot 外链（须为 https://t.me/…），可被 URL 查询参数 tg_bot 覆盖 */
  readonly VITE_TELEGRAM_BOT_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
