"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { useViewportCenterVisible } from "@/hooks/use-viewport-center-visible";
import { cn } from "@/lib/utils";

type Mode = "light" | "active";

const MODE_MULTIPLIER: Record<Mode, number> = {
  light: 1,
  active: 2.6,
};

const PROJECTION_DAYS = [30, 60, 90] as const;

function estimateMonthly(usdt: number, mode: Mode, days: number) {
  const baseDaily = 0.08 + (usdt / 10000) * 0.35;
  const daily = baseDaily * MODE_MULTIPLIER[mode];
  return daily * days;
}

function formatUsd(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Math.round(value));
}

function useReducedMotion() {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  return reduced;
}

function useAnimatedNumber(
  target: number,
  active: boolean,
  reducedMotion: boolean,
  delay = 0,
) {
  const [display, setDisplay] = useState(reducedMotion ? target : 0);
  const [revealed, setRevealed] = useState(reducedMotion);
  const displayRef = useRef(display);
  const hasAnimatedRef = useRef(false);

  useEffect(() => {
    displayRef.current = display;
  }, [display]);

  useEffect(() => {
    if (!active) return;

    if (reducedMotion) {
      setDisplay(target);
      setRevealed(true);
      return;
    }

    const from = hasAnimatedRef.current ? displayRef.current : 0;
    hasAnimatedRef.current = true;

    const revealTimer = window.setTimeout(() => setRevealed(true), delay);
    const duration = 950;
    const startAt = performance.now() + delay;
    let frame = 0;

    const tick = (now: number) => {
      const elapsed = now - startAt;
      if (elapsed < 0) {
        frame = requestAnimationFrame(tick);
        return;
      }
      const t = Math.min(elapsed / duration, 1);
      const eased = 1 - (1 - t) ** 3;
      setDisplay(from + (target - from) * eased);
      if (t < 1) frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    return () => {
      window.clearTimeout(revealTimer);
      cancelAnimationFrame(frame);
    };
  }, [active, delay, reducedMotion, target]);

  return { display, revealed };
}

function AnimatedBalance({
  value,
  active,
  reducedMotion,
}: {
  value: number;
  active: boolean;
  reducedMotion: boolean;
}) {
  const { display, revealed } = useAnimatedNumber(value, active, reducedMotion, 80);

  return (
    <span
      className={cn(
        "stat-value text-4xl font-semibold tracking-tight",
        revealed ? "stat-number-revealed" : "stat-number-pending",
      )}
    >
      {Math.round(display).toLocaleString("en-US")}
    </span>
  );
}

function AnimatedProjection({
  value,
  active,
  reducedMotion,
  delay,
  label,
}: {
  value: number;
  active: boolean;
  reducedMotion: boolean;
  delay: number;
  label: string;
}) {
  const { display, revealed } = useAnimatedNumber(value, active, reducedMotion, delay);

  return (
    <div
      className={cn(
        "rounded-2xl border border-border bg-surface-elevated px-3 py-5 text-center transition-colors duration-300 md:px-4",
        revealed ? "estimator-card-revealed" : "estimator-card-pending",
      )}
      style={{ transitionDelay: `${delay}ms` }}
    >
      <p className="text-xs text-muted">{label}</p>
      <p
        className={cn(
          "stat-value mt-2 text-xl font-semibold text-accent md:text-2xl",
          revealed ? "stat-number-revealed" : "stat-number-pending",
        )}
        style={{ transitionDelay: `${delay + 60}ms` }}
      >
        {formatUsd(display)}
      </p>
    </div>
  );
}

export function UsageEstimator() {
  const t = useTranslations("estimator");
  const [amount, setAmount] = useState(1250);
  const [mode, setMode] = useState<Mode>("light");
  const reducedMotion = useReducedMotion();
  const { ref, visible } = useViewportCenterVisible();

  const projections = useMemo(
    () =>
      PROJECTION_DAYS.map((days) => ({
        days,
        value: estimateMonthly(amount, mode, days),
      })),
    [amount, mode],
  );

  return (
    <section id="tour-estimator" ref={ref} className="py-16 md:py-24">
      <div className="mx-auto max-w-[1400px] px-4 md:px-8">
        <div
          className={cn(
            "max-w-2xl transition-all duration-700",
            visible ? "translate-y-0 opacity-100" : "translate-y-5 opacity-0",
          )}
        >
          <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">
            {t("title")}
          </h2>
          <p className="mt-4 text-base leading-relaxed text-muted">{t("subtitle")}</p>
        </div>

        <div
          className={cn(
            "glass-panel mx-auto mt-12 max-w-3xl rounded-[2rem] p-6 transition-all duration-700 md:p-10",
            visible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0",
          )}
          style={{ transitionDelay: visible ? "120ms" : "0ms" }}
        >
          <label className="block text-sm font-medium text-muted">
            {t("balanceLabel")}
          </label>
          <div className="mt-3 flex items-baseline gap-2">
            <AnimatedBalance
              value={amount}
              active={visible}
              reducedMotion={reducedMotion}
            />
            <span className="text-sm text-muted">USDT</span>
          </div>
          <div className="relative mt-4">
            <div className="h-1.5 overflow-hidden rounded-full bg-border">
              <div
                className="h-full rounded-full bg-accent transition-[width] duration-300 ease-out"
                style={{
                  width: visible
                    ? `${((amount - 200) / (10000 - 200)) * 100}%`
                    : "0%",
                }}
              />
            </div>
            <input
              type="range"
              min={200}
              max={10000}
              step={50}
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              className="absolute inset-0 h-1.5 w-full cursor-pointer appearance-none bg-transparent accent-accent"
            />
          </div>

          <p className="mt-8 text-sm font-medium text-muted">{t("modeLabel")}</p>
          <div className="mt-3 grid grid-cols-2 gap-3">
            {(["light", "active"] as const).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setMode(m)}
                className={cn(
                  "rounded-2xl border px-4 py-4 text-left transition-all duration-300 active:scale-[0.98]",
                  mode === m
                    ? "border-accent/50 bg-accent-dim"
                    : "border-border bg-surface hover:border-border/80",
                )}
              >
                <span className="block text-sm font-semibold">{t(`modes.${m}.title`)}</span>
                <span className="mt-1 block text-xs text-muted">
                  {t(`modes.${m}.description`)}
                </span>
              </button>
            ))}
          </div>

          <div className="mt-8 grid grid-cols-3 gap-3">
            {projections.map(({ days, value }, index) => (
              <AnimatedProjection
                key={days}
                value={value}
                active={visible}
                reducedMotion={reducedMotion}
                delay={180 + index * 110}
                label={t("days", { count: days })}
              />
            ))}
          </div>

          <p
            className={cn(
              "mt-6 text-center text-[11px] leading-relaxed text-muted transition-opacity duration-700",
              visible ? "opacity-100" : "opacity-0",
            )}
            style={{ transitionDelay: "520ms" }}
          >
            {t("disclaimer")}
          </p>
        </div>
      </div>
    </section>
  );
}
