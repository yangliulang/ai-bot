"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { cn } from "@/lib/utils";
import { observeWhenViewportCenter } from "@/lib/viewport-center-observer";

type ScrollRevealProps = {
  children: ReactNode;
  className?: string;
  delay?: number;
};

export function ScrollReveal({ children, className, delay = 0 }: ScrollRevealProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    el.classList.add("reveal-pending");

    const fallback = window.setTimeout(() => {
      el.classList.add("is-visible");
    }, 2400);

    const cleanup = observeWhenViewportCenter(
      el,
      () => {
        window.clearTimeout(fallback);
        el.style.transitionDelay = `${delay}ms`;
        el.classList.add("is-visible");
      },
      { once: true, fallbackMs: 2400 },
    );

    return () => {
      window.clearTimeout(fallback);
      cleanup();
    };
  }, [delay]);

  return (
    <div ref={ref} className={cn("reveal-on-scroll", className)}>
      {children}
    </div>
  );
}
