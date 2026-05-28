/** Telegram Bot 打开链接（与 deeplink `onboarding.ts` 生产默认一致） */
export const TELEGRAM_BOT_URL =
  process.env.NEXT_PUBLIC_TELEGRAM_BOT_URL?.trim() ||
  "https://t.me/chainup_online_ai_bot";

/** Agent 产品线 H5 绑定入口（deeplink `/onboarding/validate`） */
export const DEEPLINK_BIND_URL =
  process.env.NEXT_PUBLIC_DEEPLINK_BIND_URL?.trim() ||
  (process.env.NODE_ENV === "production"
    ? "https://deeplink.dw2nn.com/onboarding/validate"
    : "http://localhost:5174/onboarding/validate");

export function displayBindUrl(url: string): string {
  try {
    const parsed = new URL(url);
    return `${parsed.host}${parsed.pathname}`;
  } catch {
    return url;
  }
}
