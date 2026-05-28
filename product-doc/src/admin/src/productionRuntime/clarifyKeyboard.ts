/**
 * 澄清 · Telegram inline_keyboard 载荷（规则/BFF · 非 LLM）
 *
 * 规格：prompts/shared/clarify-user-visible.md §6 P7、§7.1
 *       domains/agent/telegram/overview.md · §2.3.2（澄清键盘）
 */

export type EffectiveLocale = "zh-Hans" | "zh-Hant" | "en";

export type ClarifyKeyboardKind =
  | "spot_trade_mode"
  | "spot_side"
  | "confirm_symbol_default";

/** Telegram `InlineKeyboardButton` · callback 类 */
export type ClarifyInlineKeyboardButton = {
  text: string;
  /** UTF-8 ≤64B · 仅短键；明细服务端 session 解析 */
  callback_data: string;
};

export type ClarifyInlineKeyboard = {
  kind: ClarifyKeyboardKind;
  effectiveLocale: EffectiveLocale;
  rows: ClarifyInlineKeyboardButton[][];
};

const LABELS: Record<
  ClarifyKeyboardKind,
  Record<EffectiveLocale, ClarifyInlineKeyboardButton[]>
> = {
  spot_trade_mode: {
    "zh-Hans": [
      { text: "闪兑", callback_data: "cl:fc" },
      { text: "限价", callback_data: "cl:lo" },
    ],
    "zh-Hant": [
      { text: "閃兌", callback_data: "cl:fc" },
      { text: "限價", callback_data: "cl:lo" },
    ],
    en: [
      { text: "Flash", callback_data: "cl:fc" },
      { text: "Limit", callback_data: "cl:lo" },
    ],
  },
  spot_side: {
    "zh-Hans": [
      { text: "买入", callback_data: "cl:buy" },
      { text: "卖出", callback_data: "cl:sell" },
    ],
    "zh-Hant": [
      { text: "買入", callback_data: "cl:buy" },
      { text: "賣出", callback_data: "cl:sell" },
    ],
    en: [
      { text: "Buy", callback_data: "cl:buy" },
      { text: "Sell", callback_data: "cl:sell" },
    ],
  },
  confirm_symbol_default: {
    "zh-Hans": [
      { text: "对的", callback_data: "cl:sym:ok" },
      { text: "换一个", callback_data: "cl:sym:no" },
    ],
    "zh-Hant": [
      { text: "對的", callback_data: "cl:sym:ok" },
      { text: "換一個", callback_data: "cl:sym:no" },
    ],
    en: [
      { text: "Yes", callback_data: "cl:sym:ok" },
      { text: "Change", callback_data: "cl:sym:no" },
    ],
  },
};

export function buildClarifyInlineKeyboard(params: {
  kind: ClarifyKeyboardKind;
  effectiveLocale?: EffectiveLocale;
}): ClarifyInlineKeyboard {
  const locale = params.effectiveLocale ?? "zh-Hans";
  const buttons = LABELS[params.kind][locale];
  return {
    kind: params.kind,
    effectiveLocale: locale,
    rows: [buttons],
  };
}

/** 是否应对该 callback_data 字节长度告警（SC-CH-TG-08 同窗）。 */
export function clarifyCallbackDataWithinLimit(data: string): boolean {
  return new TextEncoder().encode(data).length <= 64;
}
