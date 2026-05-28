"use client";

import { memo } from "react";
import { cn } from "@/lib/utils";

type GuideProgressVisualProps = {
  activeStep: number;
  labels: string[];
  stepsLabel: string;
};

export const GuideProgressVisual = memo(function GuideProgressVisual({
  activeStep,
  labels,
  stepsLabel,
}: GuideProgressVisualProps) {
  return (
    <div
      className="glass-panel relative hidden overflow-hidden rounded-4xl border-white/10 p-6 md:block md:p-7"
      aria-hidden
    >
      <div
        className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-accent/10 blur-3xl"
        aria-hidden
      />
      <p className="text-xs font-medium uppercase tracking-[0.16em] text-muted">
        {stepsLabel}
      </p>
      <ol className="relative mt-6 space-y-0">
        <span className="bind-guide-rail absolute bottom-3 left-[11px] top-3 w-px opacity-60" />
        {labels.map((label, index) => {
          const isActive = activeStep === index;
          const isPast = activeStep > index;
          return (
            <li
              key={label}
              className={cn(
                "relative flex items-center gap-3 py-2.5 transition-opacity duration-300",
                !isActive && !isPast && "opacity-45",
              )}
            >
              <span
                className={cn(
                  "relative z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold transition-all duration-300",
                  isActive && "bind-guide-pulse-active scale-110 bg-accent text-zinc-950",
                  isPast && !isActive && "bg-accent/20 text-accent",
                  !isActive && !isPast && "border border-border bg-surface text-muted",
                )}
              >
                {index + 1}
              </span>
              <span
                className={cn(
                  "truncate text-sm transition-colors duration-300",
                  isActive ? "font-medium text-foreground" : "text-muted",
                )}
              >
                {label}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
});
