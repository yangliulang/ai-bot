"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import { observeWhenViewportCenter } from "@/lib/viewport-center-observer";

const STAT_CONFIG = [
  { key: "executions", target: 18427, decimals: 0, suffix: "" },
  { key: "reads", target: 1.8, decimals: 1, suffix: "s" },
  { key: "confirmRate", target: 97.3, decimals: 1, suffix: "%" },
  { key: "agents", target: 2841, decimals: 0, suffix: "" },
] as const;

function formatStatValue(value: number, decimals: number, suffix: string) {
  if (suffix === "s") return `${value.toFixed(decimals)}${suffix}`;
  if (suffix === "%") return `${value.toFixed(decimals)}${suffix}`;
  return Math.round(value).toLocaleString("en-US");
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

function AnimatedStatNumber({
  target,
  decimals,
  suffix,
  active,
  delay,
  reducedMotion,
}: {
  target: number;
  decimals: number;
  suffix: string;
  active: boolean;
  delay: number;
  reducedMotion: boolean;
}) {
  const [display, setDisplay] = useState(reducedMotion ? target : 0);
  const [revealed, setRevealed] = useState(reducedMotion);

  useEffect(() => {
    if (!active) return;

    if (reducedMotion) {
      setDisplay(target);
      setRevealed(true);
      return;
    }

    const revealTimer = window.setTimeout(() => setRevealed(true), delay);
    const duration = 1100;
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
      setDisplay(target * eased);
      if (t < 1) frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    return () => {
      window.clearTimeout(revealTimer);
      cancelAnimationFrame(frame);
    };
  }, [active, delay, reducedMotion, target]);

  return (
    <span
      className={cn(
        "stat-value inline-block text-4xl font-semibold tracking-tight text-foreground md:text-5xl lg:text-6xl",
        revealed ? "stat-number-revealed" : "stat-number-pending",
      )}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {formatStatValue(display, decimals, suffix)}
    </span>
  );
}

function StatCell({
  target,
  decimals,
  suffix,
  index,
  active,
  reducedMotion,
  label,
  hint,
}: {
  target: number;
  decimals: number;
  suffix: string;
  index: number;
  active: boolean;
  reducedMotion: boolean;
  label: string;
  hint: string;
}) {
  const delay = index * 120;

  return (
    <div
      className={cn(
        "stat-cell relative flex flex-col items-start bg-surface px-5 py-9 text-left md:px-8 md:py-11",
        active && "stat-cell-active",
      )}
      style={{ "--stat-index": index } as React.CSSProperties}
    >
      <dt className="text-sm font-medium text-muted md:text-base">{label}</dt>
      <dd className="mt-3">
        <AnimatedStatNumber
          target={target}
          decimals={decimals}
          suffix={suffix}
          active={active}
          delay={delay}
          reducedMotion={reducedMotion}
        />
      </dd>
      <dd className="mt-2 text-xs text-muted/90 md:text-sm">{hint}</dd>
    </div>
  );
}

export function PlatformStats() {
  const t = useTranslations("stats");
  const sectionRef = useRef<HTMLElement>(null);
  const [visible, setVisible] = useState(false);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;

    return observeWhenViewportCenter(el, () => setVisible(true), {
      once: true,
      fallbackMs: 2400,
    });
  }, []);

  return (
    <section
      id="tour-stats"
      ref={sectionRef}
      className="relative overflow-hidden bg-surface/40 py-16 md:py-24"
    >
      <div
        className="pointer-events-none absolute -left-24 -top-24 h-64 w-64 rounded-full bg-accent/6 blur-3xl"
        aria-hidden
      />

      <div className="relative mx-auto max-w-[1400px] px-4 md:px-8">
        <div className="max-w-2xl">
          <h2 className="text-3xl font-bold tracking-tighter text-foreground md:text-4xl">
            {t("title")}
          </h2>
          <p className="mt-4 text-base leading-relaxed text-muted md:text-lg">
            {t("subtitle")}
          </p>
        </div>

        <dl className="mt-12 grid grid-cols-1 gap-px overflow-hidden rounded-[1.75rem] border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
          {STAT_CONFIG.map((stat, index) => (
            <StatCell
              key={stat.key}
              target={stat.target}
              decimals={stat.decimals}
              suffix={stat.suffix}
              index={index}
              active={visible}
              reducedMotion={reducedMotion}
              label={t(`items.${stat.key}.label`)}
              hint={t(`items.${stat.key}.hint`)}
            />
          ))}
        </dl>
      </div>
    </section>
  );
}
