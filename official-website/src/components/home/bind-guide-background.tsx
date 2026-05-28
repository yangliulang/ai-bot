"use client";

import { memo } from "react";

function BindGuideBackgroundInner() {
  return (
    <div
      className="bind-guide-bg pointer-events-none absolute inset-0 overflow-hidden"
      aria-hidden
    >
      <div className="bind-guide-wash absolute inset-0" />

      <div className="bind-guide-demo-glow absolute right-[6%] top-1/2 hidden -translate-y-1/2 md:block lg:right-[10%]" />

      <svg
        className="bind-guide-handoff absolute inset-0 h-full w-full opacity-[0.22] md:opacity-[0.32]"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        fill="none"
      >
        <defs>
          <linearGradient id="bind-handoff-grad" x1="0%" y1="50%" x2="100%" y2="50%">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0" />
            <stop offset="35%" stopColor="var(--accent)" stopOpacity="0.35" />
            <stop offset="65%" stopColor="var(--accent)" stopOpacity="0.35" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          d="M 8 58 C 32 38, 68 38, 92 58"
          stroke="url(#bind-handoff-grad)"
          strokeWidth="0.35"
          strokeDasharray="1.2 2.4"
          className="bind-guide-handoff-line"
          vectorEffect="non-scaling-stroke"
        />
      </svg>

      <div className="bind-guide-rail absolute bottom-[16%] left-[max(1.25rem,6%)] top-[20%] hidden w-px md:block" />

      <div className="bind-guide-edge-fade absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-background/70 to-transparent" />
    </div>
  );
}

export const BindGuideBackground = memo(BindGuideBackgroundInner);
