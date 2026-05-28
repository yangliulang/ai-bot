"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { CaretDown } from "@phosphor-icons/react";
import { cn } from "@/lib/utils";

const FAQ_KEYS = ["what", "subaccount", "confirm", "billing", "start", "safe"] as const;

export function FaqSection() {
  const t = useTranslations("faq");
  const [open, setOpen] = useState<string | null>(FAQ_KEYS[0]);

  return (
    <section id="tour-faq" className="py-16 md:py-24">
      <div className="mx-auto max-w-[1400px] px-4 md:px-8">
        <h2 className="text-center text-3xl font-bold tracking-tighter md:text-4xl">
          {t("title")}
        </h2>

        <div className="mx-auto mt-12 max-w-5xl divide-y divide-border/60 rounded-2xl border border-border/60 bg-surface">
          {FAQ_KEYS.map((key) => {
            const isOpen = open === key;
            return (
              <div key={key}>
                <button
                  type="button"
                  onClick={() => setOpen(isOpen ? null : key)}
                  className="flex w-full items-center justify-between gap-4 px-5 py-5 text-left transition-colors hover:bg-surface-elevated/50 md:px-6"
                  aria-expanded={isOpen}
                >
                  <span className="text-sm font-medium md:text-base">
                    {t(`items.${key}.question`)}
                  </span>
                  <CaretDown
                    size={18}
                    className={cn(
                      "shrink-0 text-muted transition-transform duration-200",
                      isOpen && "rotate-180",
                    )}
                  />
                </button>
                <div
                  className={cn(
                    "grid transition-all duration-200",
                    isOpen ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0",
                  )}
                >
                  <div className="overflow-hidden">
                    <p className="px-5 pb-5 text-sm leading-relaxed text-muted md:px-6">
                      {t(`items.${key}.answer`)}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
