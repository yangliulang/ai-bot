"use client";

import { memo } from "react";
import { cn } from "@/lib/utils";

const ACCENT_POSITIONS = [
  "right-[8%] top-[12%] bg-accent/10",
  "left-[10%] top-[18%] bg-accent/8",
  "right-[12%] bottom-[20%] bg-accent/12",
  "left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-accent/14",
] as const;

function BindGuideStageBackgroundInner({
  activeStep,
}: {
  activeStep: number;
  reducedMotion: boolean;
}) {
  return (
    <div
      className="bind-guide-stage-bg pointer-events-none absolute inset-0 z-0 overflow-hidden rounded-[inherit]"
      aria-hidden
    >
      <div className="bind-guide-stage-base absolute inset-0" />
      <div className="bind-guide-stage-dots absolute inset-0" />

      <div
        className={cn(
          "bind-guide-stage-accent absolute h-56 w-56 rounded-full blur-3xl transition-all duration-700 md:h-72 md:w-72",
          ACCENT_POSITIONS[activeStep] ?? ACCENT_POSITIONS[0],
        )}
      />

      <div
        className={cn(
          "bind-guide-stage-layer bind-guide-stage-layer-0 absolute inset-0 transition-opacity duration-700",
          activeStep === 0 ? "opacity-100" : "opacity-0",
        )}
      />
      <div
        className={cn(
          "bind-guide-stage-layer bind-guide-stage-layer-1 absolute inset-0 transition-opacity duration-700",
          activeStep === 1 ? "opacity-100" : "opacity-0",
        )}
      />
      <div
        className={cn(
          "bind-guide-stage-layer bind-guide-stage-layer-2 absolute inset-0 transition-opacity duration-700",
          activeStep === 2 ? "opacity-100" : "opacity-0",
        )}
      />
      <div
        className={cn(
          "bind-guide-stage-layer bind-guide-stage-layer-3 absolute inset-0 transition-opacity duration-700",
          activeStep === 3 ? "opacity-100" : "opacity-0",
        )}
      />

      <div className="bind-guide-stage-edge absolute inset-0 rounded-[inherit]" />
    </div>
  );
}

export const BindGuideStageBackground = memo(BindGuideStageBackgroundInner);
