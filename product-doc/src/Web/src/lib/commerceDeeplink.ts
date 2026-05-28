/**
 * H5 / Telegram Deeplink 拼装 · 同窗 specs/requirements/domains/web/commerce-deeplink.md
 */

/** `quota`/`legacy` 等旧 tab 在账单页归并为 ledger */
export type AgentBillingTab = "quota" | "ledger" | "monthly";

export type CommerceDeeplinkParams = {
  fromTelegram?: boolean;
  tab?: AgentBillingTab;
  tgUser?: string;
};

function h5Path(path: string): string {
  const origin = import.meta.env.VITE_H5_PUBLIC_ORIGIN?.trim().replace(/\/$/, "");
  return origin ? `${origin}${path}` : path;
}

function withQuery(path: string, params: URLSearchParams): string {
  const qs = params.toString();
  return qs ? `${path}?${qs}` : path;
}

function baseQuery(p: CommerceDeeplinkParams): URLSearchParams {
  const q = new URLSearchParams();
  if (p.fromTelegram) q.set("from", "telegram");
  if (p.tgUser) q.set("tg_user", p.tgUser);
  if (p.tab) q.set("tab", p.tab);
  return q;
}

export function buildAgentBillingDeeplink(p: CommerceDeeplinkParams = {}): string {
  const q = baseQuery(p);
  if (p.tab === "quota") {
    q.delete("tab");
    q.set("tab", "overview");
  }
  return withQuery(h5Path("/subaccount/billing"), q);
}

export function buildCommerceUpgradeDeeplink(p: CommerceDeeplinkParams = {}): string {
  const env = import.meta.env.VITE_COMMERCE_UPGRADE_URL?.trim();
  if (env) return env;
  return withQuery(h5Path("/subscription/upgrade"), baseQuery(p));
}

export function buildCommercePackDeeplink(p: CommerceDeeplinkParams = {}): string {
  const env = import.meta.env.VITE_COMMERCE_PACK_URL?.trim();
  if (env) return env;
  return withQuery(h5Path("/subscription/pack"), baseQuery(p));
}

/** Telegram Bot `?start=` payload（须 ≤64 字符 · 与 Bot 解析同窗） */
export type TelegramCommerceStartIntent = "billing" | "upgrade" | "pack" | "ledger";

const START_PAYLOAD: Record<TelegramCommerceStartIntent, string> = {
  billing: "ab",
  upgrade: "ab_up",
  pack: "ab_pk",
  ledger: "ab_ld",
};

export function buildTelegramStartPayload(intent: TelegramCommerceStartIntent): string {
  return START_PAYLOAD[intent];
}

export function buildTelegramBotDeeplink(botUsername: string, intent: TelegramCommerceStartIntent): string {
  const user = botUsername.replace(/^@/, "");
  const payload = buildTelegramStartPayload(intent);
  return `https://t.me/${user}?start=${encodeURIComponent(payload)}`;
}

/** 将 Bot `start` payload 映射为 H5 路径（Bot/WebView 实现同窗） */
export function resolveH5PathFromTelegramStart(startPayload: string): string | null {
  const p = startPayload.trim();
  if (p === "ab" || p === "ab_billing") return buildAgentBillingDeeplink({ fromTelegram: true });
  if (p === "ab_up") return buildCommerceUpgradeDeeplink({ fromTelegram: true });
  if (p === "ab_pk") return buildCommercePackDeeplink({ fromTelegram: true });
  if (p === "ab_sub") return h5Path("/subscription");
  if (p === "ab_ld") return buildAgentBillingDeeplink({ fromTelegram: true, tab: "ledger" });
  return null;
}
