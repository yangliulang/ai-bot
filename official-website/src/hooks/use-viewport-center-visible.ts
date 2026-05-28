"use client";

import { useEffect, useRef, useState } from "react";
import { observeWhenViewportCenter } from "@/lib/viewport-center-observer";

export function useViewportCenterVisible(fallbackMs = 2400) {
  const ref = useRef<HTMLElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    return observeWhenViewportCenter(el, () => setVisible(true), {
      once: true,
      fallbackMs,
    });
  }, [fallbackMs]);

  return { ref, visible };
}
