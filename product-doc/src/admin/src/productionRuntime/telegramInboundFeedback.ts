/**
 * Telegram 入站反馈 · `sendChatAction(typing)` 调度小样
 *
 * 规格：specs/requirements/domains/agent/telegram/overview.md · §2.3.1
 *       specs/design/api.md · Telegram Bot API · send_chat_action
 *
 * **非** Bot HTTP 客户端 — 仅 **纯函数** 供所内 Webhook/BFF **对签** **何时发 typing**。
 */

/** Telegram 客户端展示 typing 约 5s；续发宜略早于过期。 */
export const TELEGRAM_TYPING_VISIBLE_MS = 5_000;

/** 建议续发间隔（小于 TELEGRAM_TYPING_VISIBLE_MS）。 */
export const TELEGRAM_TYPING_REFRESH_MS = 4_500;

/** 入站后首次 typing 宜在此时间内发出。 */
export const TELEGRAM_TYPING_INITIAL_DEADLINE_MS = 300;

export type InboundUpdateKind = "message" | "callback_query" | "other";

export type TypingScheduleInput = {
  updateKind: InboundUpdateKind;
  /** 编排是否仍会产出用户可见回复（早失败且已发短句时可 false） */
  expectsUserVisibleReply: boolean;
  /** 自 inbound 收到起的毫秒数 */
  elapsedSinceInboundMs: number;
  /** 上次 sendChatAction(typing) 成功时刻距 inbound 的毫秒；null = 尚未发 */
  lastTypingSentSinceInboundMs: number | null;
  /** 是否已发出首条用户可见 sendMessage/edit（含早失败短句） */
  firstUserVisibleReplySent: boolean;
};

export type TypingScheduleResult = {
  sendTyping: boolean;
  reason:
    | "initial_inbound"
    | "refresh_before_expiry"
    | "skip_callback_query"
    | "skip_no_reply_expected"
    | "skip_already_replied"
    | "skip_too_soon";
};

/**
 * 是否应在当前时刻调用 `sendChatAction(chat_id, { action: "typing" })`。
 */
export function planTelegramTypingAction(
  input: TypingScheduleInput,
): TypingScheduleResult {
  if (input.updateKind === "callback_query") {
    return { sendTyping: false, reason: "skip_callback_query" };
  }
  if (!input.expectsUserVisibleReply) {
    return { sendTyping: false, reason: "skip_no_reply_expected" };
  }
  if (input.firstUserVisibleReplySent) {
    return { sendTyping: false, reason: "skip_already_replied" };
  }

  if (input.lastTypingSentSinceInboundMs == null) {
    return { sendTyping: true, reason: "initial_inbound" };
  }

  const sinceLast =
    input.elapsedSinceInboundMs - input.lastTypingSentSinceInboundMs;
  if (sinceLast >= TELEGRAM_TYPING_REFRESH_MS) {
    return { sendTyping: true, reason: "refresh_before_expiry" };
  }

  return { sendTyping: false, reason: "skip_too_soon" };
}

/** 首次 typing 是否已超过产品 deadline（用于 SC-CH-TG-09 抽检）。 */
export function isInitialTypingLate(params: {
  firstTypingSentSinceInboundMs: number | null;
}): boolean {
  if (params.firstTypingSentSinceInboundMs == null) return true;
  return (
    params.firstTypingSentSinceInboundMs > TELEGRAM_TYPING_INITIAL_DEADLINE_MS
  );
}
