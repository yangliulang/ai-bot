import { describe, expect, it } from "vitest";
import {
  isInitialTypingLate,
  planTelegramTypingAction,
  TELEGRAM_TYPING_INITIAL_DEADLINE_MS,
  TELEGRAM_TYPING_REFRESH_MS,
} from "./telegramInboundFeedback";

describe("planTelegramTypingAction", () => {
  it("message inbound：首次须发 typing", () => {
    const r = planTelegramTypingAction({
      updateKind: "message",
      expectsUserVisibleReply: true,
      elapsedSinceInboundMs: 50,
      lastTypingSentSinceInboundMs: null,
      firstUserVisibleReplySent: false,
    });
    expect(r).toEqual({ sendTyping: true, reason: "initial_inbound" });
  });

  it("callback_query：不发 typing（靠 answerCallbackQuery）", () => {
    const r = planTelegramTypingAction({
      updateKind: "callback_query",
      expectsUserVisibleReply: true,
      elapsedSinceInboundMs: 50,
      lastTypingSentSinceInboundMs: null,
      firstUserVisibleReplySent: false,
    });
    expect(r.reason).toBe("skip_callback_query");
  });

  it("长耗时：距上次 typing 超过 refresh 间隔须续发", () => {
    const r = planTelegramTypingAction({
      updateKind: "message",
      expectsUserVisibleReply: true,
      elapsedSinceInboundMs: TELEGRAM_TYPING_REFRESH_MS + 100,
      lastTypingSentSinceInboundMs: 0,
      firstUserVisibleReplySent: false,
    });
    expect(r).toEqual({ sendTyping: true, reason: "refresh_before_expiry" });
  });

  it("已发首条回复：停止 typing", () => {
    const r = planTelegramTypingAction({
      updateKind: "message",
      expectsUserVisibleReply: true,
      elapsedSinceInboundMs: 10_000,
      lastTypingSentSinceInboundMs: 0,
      firstUserVisibleReplySent: true,
    });
    expect(r.reason).toBe("skip_already_replied");
  });
});

describe("isInitialTypingLate", () => {
  it("300ms 内发出不算迟", () => {
    expect(
      isInitialTypingLate({
        firstTypingSentSinceInboundMs: TELEGRAM_TYPING_INITIAL_DEADLINE_MS,
      }),
    ).toBe(false);
  });

  it("超过 deadline 算迟", () => {
    expect(
      isInitialTypingLate({
        firstTypingSentSinceInboundMs:
          TELEGRAM_TYPING_INITIAL_DEADLINE_MS + 1,
      }),
    ).toBe(true);
  });
});
