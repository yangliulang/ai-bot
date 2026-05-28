"use client";

import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";
import { useLocale, useTranslations } from "next-intl";
import { PaperPlaneRight } from "@phosphor-icons/react";
import { ChainUpAgentLogo } from "@/components/brand/chainup-agent-logo";
import { cn } from "@/lib/utils";
import { DemoChatBackground } from "./demo-chat-background";

type Message = { id: string; role: "user" | "agent"; text: string };
type Turn = { user: string; agent: string };
type Script = { turns: Turn[] };

function TypingIndicator() {
  return (
    <div
      className="self-start flex gap-1 rounded-2xl rounded-bl-md bg-[#182533] px-4 py-3"
      aria-label="Agent typing"
    >
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="demo-typing-dot h-1.5 w-1.5 rounded-full bg-zinc-400"
          style={{ animationDelay: `${i * 0.16}s` }}
        />
      ))}
    </div>
  );
}

export function HeroTelegramPreview() {
  const t = useTranslations("demo");
  const locale = useLocale();
  const uid = useId();
  const msgId = useRef(0);
  const autoTimers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const replyTimers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const scriptRef = useRef(0);
  const messagesRef = useRef<Message[]>([]);
  const sendLockedRef = useRef(false);
  const typingRef = useRef(false);
  const modeRef = useRef<"auto" | "interactive">("auto");
  const mounted = useRef(true);

  const scripts = useMemo(
    () => t.raw("scripts") as Script[],
    [locale],
  );
  const advanceAutoRef = useRef<(scriptIndex: number, turnIndex: number) => void>(
    () => {},
  );

  const [userEngaged, setUserEngaged] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [autoSendReady, setAutoSendReady] = useState(false);
  const [isClient, setIsClient] = useState(false);

  messagesRef.current = messages;
  typingRef.current = typing;

  const nextMsgId = () => {
    msgId.current += 1;
    return `${uid}-${msgId.current}`;
  };

  const clearAutoTimers = useCallback(() => {
    autoTimers.current.forEach(clearTimeout);
    autoTimers.current = [];
  }, []);

  const clearReplyTimers = useCallback(() => {
    replyTimers.current.forEach(clearTimeout);
    replyTimers.current = [];
  }, []);

  const scheduleAuto = useCallback((fn: () => void, ms: number) => {
    const id = setTimeout(() => {
      if (mounted.current) fn();
    }, ms);
    autoTimers.current.push(id);
  }, []);

  const scheduleReply = useCallback((fn: () => void, ms: number) => {
    const id = setTimeout(() => {
      if (mounted.current) fn();
    }, ms);
    replyTimers.current.push(id);
  }, []);

  const appendAgent = useCallback(
    (text: string, onDone?: () => void) => {
      setTyping(true);
      scheduleReply(() => {
        setTyping(false);
        setMessages((prev) => [
          ...prev,
          { id: nextMsgId(), role: "agent", text },
        ]);
        onDone?.();
      }, 880 + Math.min(text.length * 8, 640));
    },
    [scheduleReply],
  );

  const matchesAny = (text: string, keywords: string[]) =>
    keywords.some((kw) => text.includes(kw));

  const resolveResponse = useCallback(
    (text: string, history: Message[]) => {
      const lower = text.toLowerCase();
      const lastAgent = [...history].reverse().find((m) => m.role === "agent")?.text ?? "";

      if (
        matchesAny(lower, ["confirm", "确认", "確認", "確定", "confirmar"]) &&
        matchesAny(lastAgent, ["Type A", "类型 A", "類型 A", "Type A Confirm"])
      ) {
        return t("responses.confirmed");
      }

      if (
        matchesAny(lower, [
          "telegram",
          "tg",
          "bind",
          "link",
          "connect",
          "绑定",
          "綁定",
          "連結",
          "连接",
          "連接",
          "テレグラム",
          "連携",
          "텔레그램",
          "연동",
        ])
      ) {
        return t("responses.bindTelegram");
      }

      if (
        matchesAny(lower, [
          "hello",
          "hi",
          "hey",
          "你好",
          "您好",
          "こんにちは",
          "안녕",
        ])
      ) {
        return t("responses.greeting");
      }

      if (
        matchesAny(lower, [
          "help",
          "what can",
          "how do",
          "帮助",
          "幫助",
          "怎么用",
          "怎麼用",
          "能做什么",
          "能做什麼",
          "使い方",
          "help me",
          "도움",
        ])
      ) {
        return t("responses.help");
      }

      if (
        matchesAny(lower, [
          "thanks",
          "thank you",
          "谢谢",
          "謝謝",
          "ありがとう",
          "감사",
        ])
      ) {
        return t("responses.thanks");
      }

      if (
        matchesAny(lower, [
          "balance",
          "余额",
          "餘額",
          "残高",
          "잔액",
          "account",
          "账户",
          "帳戶",
        ])
      ) {
        return t("responses.balance");
      }

      if (
        matchesAny(lower, [
          "order",
          "委托",
          "委託",
          "注文",
          "주문",
          "open order",
          "pending",
          "未成交",
        ])
      ) {
        return t("responses.orders");
      }

      if (
        matchesAny(lower, [
          "buy",
          "sell",
          "买",
          "買",
          "卖",
          "賣",
          "매수",
          "limit",
          "限价",
          "限價",
          "指値",
          "place",
          "下单",
          "下單",
        ])
      ) {
        return t("responses.order");
      }

      if (
        matchesAny(lower, [
          "eth",
          "funding",
          "资金",
          "資金",
          "费率",
          "費率",
        ])
      ) {
        return t("responses.eth");
      }

      if (
        matchesAny(lower, [
          "btc",
          "usdt",
          "price",
          "价格",
          "價格",
          "多少钱",
          "多少錢",
          "行情",
          "quote",
          "market",
          "ticker",
        ])
      ) {
        return t("responses.price");
      }

      return t("responses.bindTelegram");
    },
    [t],
  );

  const send = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || typingRef.current || sendLockedRef.current) return;

      sendLockedRef.current = true;
      modeRef.current = "interactive";
      setUserEngaged(true);
      clearAutoTimers();
      setAutoSendReady(false);
      setInput("");

      const userMsg: Message = { id: nextMsgId(), role: "user", text: trimmed };
      const history = [...messagesRef.current, userMsg];
      setMessages(history);

      const response = resolveResponse(trimmed, history);
      appendAgent(response, () => {
        sendLockedRef.current = false;
      });
    },
    [clearAutoTimers, appendAgent, resolveResponse],
  );

  const typewriterInput = useCallback(
    (text: string, onComplete: () => void) => {
      const reducedMotion =
        typeof window !== "undefined" &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

      if (reducedMotion) {
        setInput(text);
        scheduleAuto(onComplete, 200);
        return;
      }

      let charIndex = 0;
      const typeNext = () => {
        charIndex += 1;
        setInput(text.slice(0, charIndex));
        if (charIndex < text.length) {
          scheduleAuto(typeNext, 32 + Math.floor(Math.random() * 22));
        } else {
          scheduleAuto(onComplete, 260);
        }
      };
      scheduleAuto(typeNext, 320);
    },
    [scheduleAuto],
  );

  const advanceAuto = useCallback(
    (scriptIndex: number, turnIndex: number) => {
      if (!mounted.current) return;

      const script = scripts[scriptIndex];
      if (!script) return;

      if (turnIndex >= script.turns.length) {
        scheduleAuto(() => {
          scriptRef.current = (scriptIndex + 1) % scripts.length;
          advanceAutoRef.current(scriptRef.current, 0);
        }, 3200);
        return;
      }

      if (turnIndex === 0) {
        setMessages([]);
        setInput("");
        setTyping(false);
        setAutoSendReady(false);
      }

      const turn = script.turns[turnIndex];

      typewriterInput(turn.user, () => {
        setAutoSendReady(true);
        scheduleAuto(() => {
          setAutoSendReady(false);
          setInput("");
          setMessages((prev) => [
            ...prev,
            { id: nextMsgId(), role: "user", text: turn.user },
          ]);

          appendAgent(turn.agent, () => {
            scheduleAuto(() => advanceAutoRef.current(scriptIndex, turnIndex + 1), 1200);
          });
        }, 480);
      });
    },
    [scripts, typewriterInput, scheduleAuto, appendAgent],
  );

  advanceAutoRef.current = advanceAuto;

  const startAutoDemo = useCallback(() => {
    if (modeRef.current !== "auto") return;
    clearAutoTimers();
    scheduleAuto(() => {
      if (modeRef.current === "auto") {
        advanceAutoRef.current(scriptRef.current, 0);
      }
    }, 400);
  }, [clearAutoTimers, scheduleAuto]);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient) return;

    mounted.current = true;
    modeRef.current = "auto";
    startAutoDemo();

    return () => {
      mounted.current = false;
      clearAutoTimers();
      clearReplyTimers();
    };
  }, [isClient, startAutoDemo, clearAutoTimers, clearReplyTimers]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  const prompts = Array.from(
    { length: Math.min(3, scripts.length) },
    (_, i) => t(`prompts.${i}`),
  );
  const isAuto = isClient && !userEngaged;

  const engageInteractive = useCallback(() => {
    modeRef.current = "interactive";
    clearAutoTimers();
    setUserEngaged(true);
  }, [clearAutoTimers]);

  return (
    <div
      id="tour-demo"
      className="glass-panel relative ml-auto w-full max-w-xl overflow-visible rounded-[2rem] p-1 md:max-w-2xl lg:max-w-[34rem]"
    >
      <div
        className="demo-card-ambient pointer-events-none absolute -inset-6 z-0 overflow-visible md:-inset-10"
        aria-hidden
      >
        <div className="demo-card-blob-a absolute right-0 top-[4%] h-80 w-80 translate-x-[48%] rounded-full bg-accent/[0.045] blur-[96px]" />
        <div className="demo-card-blob-b absolute -left-20 bottom-[10%] h-56 w-56 rounded-full bg-accent/[0.035] blur-[76px]" />
      </div>

      <div className="relative isolate z-10 overflow-hidden rounded-[1.85rem] bg-[#0a121c]">
        <DemoChatBackground />
        <div className="relative z-10 flex items-center gap-3 border-b border-white/8 bg-[#0e1621]/80 px-5 py-4 backdrop-blur-sm">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-accent/15 ring-1 ring-accent/25">
            <ChainUpAgentLogo size={28} variant="glyph" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-zinc-100">ChainUp Agent</p>
            <p className="text-xs text-zinc-500" suppressHydrationWarning>
              {isAuto ? t("autoLabel") : t("interactiveLabel")}
            </p>
          </div>
        </div>

        <div
          ref={scrollRef}
          className="relative z-10 flex h-[22rem] flex-col items-end gap-2.5 overflow-y-auto p-4 md:h-[26rem] lg:h-[28rem]"
        >
          {messages.length === 0 && isAuto && (
            <p className="w-full self-stretch py-12 text-center text-xs text-zinc-600">{t("autoSubtitle")}</p>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "max-w-[92%] animate-fade-up rounded-2xl px-3.5 py-2.5 text-[13px] leading-relaxed whitespace-pre-line md:text-sm",
                msg.role === "user"
                  ? "rounded-br-md bg-accent text-zinc-950"
                  : "self-start rounded-bl-md bg-[#182533] text-zinc-100",
              )}
            >
              {msg.text}
            </div>
          ))}
          {typing && <TypingIndicator />}
        </div>

        <div className="relative z-10 space-y-2.5 border-t border-white/8 bg-[#0e1621]/85 p-4 backdrop-blur-sm">
          <div className="flex flex-wrap justify-end gap-1.5">
            {prompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => {
                  engageInteractive();
                  send(prompt);
                }}
                disabled={typing}
                className={cn(
                  "rounded-full border border-white/10 px-2.5 py-1 text-[11px] text-zinc-400 transition-colors active:scale-[0.98] hover:border-accent/30 hover:text-zinc-200 md:text-xs",
                  typing && "opacity-40",
                )}
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              readOnly={!isClient || isAuto}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key !== "Enter" || e.nativeEvent.isComposing) return;
                e.preventDefault();
                send(input);
              }}
              onFocus={engageInteractive}
              placeholder={t("placeholder")}
              className={cn(
                "flex-1 rounded-full bg-white/5 px-4 py-3 text-sm text-zinc-100 ring-1 ring-white/10 placeholder:text-zinc-500 transition-shadow duration-300 focus:outline-none focus:ring-2 focus:ring-accent/40",
                isAuto && input && "text-zinc-300",
              )}
            />
            <button
              type="button"
              onClick={() => send(input || prompts[0])}
              disabled={typing || (isAuto && !autoSendReady && !input)}
              aria-label={t("send")}
              className={cn(
                "flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-accent text-zinc-950 transition-transform active:scale-95 disabled:opacity-40",
                isAuto && autoSendReady && "demo-send-guide",
              )}
            >
              <PaperPlaneRight size={18} weight="fill" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
