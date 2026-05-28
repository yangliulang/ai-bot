/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_TELEGRAM_BOT_URL?: string;
  /** Agent / BFF API 基址（优先）；无尾斜杠 */
  readonly VITE_AGENT_API_BASE_URL?: string;
  /** 兼容旧名；无尾斜杠 */
  readonly VITE_COOBIT_API_BASE_URL?: string;
  readonly VITE_USE_ME_COMMERCE_API?: string;
  readonly VITE_COMMERCE_UPGRADE_URL?: string;
  readonly VITE_COMMERCE_PACK_URL?: string;
  readonly VITE_H5_PUBLIC_ORIGIN?: string;
}
