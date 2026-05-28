"use client";

import { useLocale } from "next-intl";
import { CaretDown } from "@phosphor-icons/react";
import { usePathname, useRouter } from "@/i18n/navigation";
import { localeLabels, locales, type Locale } from "@/i18n/routing";
import { cn } from "@/lib/utils";

export function LocaleSwitcher({ className }: { className?: string }) {
  const locale = useLocale() as Locale;
  const router = useRouter();
  const pathname = usePathname();

  return (
    <div className={cn("relative inline-flex", className)}>
      <label className="sr-only" htmlFor="locale-switcher">
        Language
      </label>
      <select
        id="locale-switcher"
        value={locale}
        onChange={(e) =>
          router.replace(pathname, { locale: e.target.value as Locale })
        }
        className="h-9 min-w-[7.5rem] cursor-pointer appearance-none rounded-full border border-border bg-surface py-0 pl-3 pr-9 text-sm leading-none text-foreground transition-colors hover:border-accent/40 focus:outline-none focus:ring-2 focus:ring-accent/30"
      >
        {locales.map((l) => (
          <option key={l} value={l}>
            {localeLabels[l]}
          </option>
        ))}
      </select>
      <span
        className="pointer-events-none absolute inset-y-0 right-2.5 flex w-4 items-center justify-center text-muted"
        aria-hidden
      >
        <CaretDown size={14} weight="bold" />
      </span>
    </div>
  );
}
