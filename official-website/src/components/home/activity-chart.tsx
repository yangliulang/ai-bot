"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useViewportCenterVisible } from "@/hooks/use-viewport-center-visible";

const BARS = [
  38, 52, 47, 61, 58, 72, 68, 84, 79, 91, 88, 96,
];

export function ActivityChart() {
  const t = useTranslations("chart");
  const { ref, visible } = useViewportCenterVisible();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return (
    <section
      id="tour-chart"
      ref={ref}
      className="bg-surface/30 py-16 md:py-24"
    >
      <div className="mx-auto max-w-[1400px] px-4 md:px-8">
        <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">
              {t("title")}
            </h2>
            <p className="mt-3 max-w-lg text-base text-muted">{t("subtitle")}</p>
          </div>
          <p className="stat-value text-sm text-muted">
            {t("period")} · <span className="text-accent">+47.2%</span>
          </p>
        </div>

        <div className="mt-10 flex h-48 items-end gap-2 md:h-56 md:gap-3">
          {BARS.map((height, i) => (
            <div
              key={i}
              className="relative flex-1 origin-bottom rounded-t-2xl bg-accent/20"
              style={{
                height: isClient && visible ? `${height}%` : "0%",
                transition: `height 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${i * 40}ms`,
              }}
            >
              <div
                className="absolute inset-x-0 bottom-0 rounded-t-2xl bg-accent/70"
                style={{ height: "100%" }}
              />
            </div>
          ))}
        </div>

        <div className="mt-4 flex justify-between text-[11px] text-muted">
          <span>{t("axisStart")}</span>
          <span>{t("axisEnd")}</span>
        </div>
      </div>
    </section>
  );
}
