"use client";

import { useTranslations } from "next-intl";
import { PaperPlaneTilt } from "@phosphor-icons/react";
import { Link } from "@/i18n/navigation";
import { ChainUpAgentLogo } from "@/components/brand/chainup-agent-logo";
import { LocaleSwitcher } from "./locale-switcher";
import { Button } from "@/components/ui/button";
import { useProductTour } from "@/components/guide/product-tour-provider";
import { TELEGRAM_BOT_URL } from "@/lib/bind-links";

const homeSectionLinks = [
  { href: "/#tour-stats", label: "performance" },
  { href: "/#tour-bind", label: "bind" },
  { href: "/#tour-estimator", label: "estimator" },
  { href: "/#tour-faq", label: "faq" },
] as const;

export function Header() {
  const t = useTranslations("nav");
  const { startTour } = useProductTour();

  return (
    <header className="sticky top-0 z-40 border-b border-border/50 bg-background/90 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between gap-4 px-4 md:px-8">
        <Link
          href="/"
          className="group flex items-center gap-2.5 font-semibold tracking-tight"
        >
          <ChainUpAgentLogo size={32} className="transition-opacity group-hover:opacity-90" />
          <span className="hidden text-sm uppercase tracking-[0.2em] text-muted sm:inline">
            ChainUp Agent
          </span>
        </Link>

        <nav className="hidden items-center gap-8 text-sm text-muted md:flex">
          {homeSectionLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className="transition-colors hover:text-foreground"
            >
              {t(label)}
            </Link>
          ))}
          <Link href="/guide" className="transition-colors hover:text-foreground">
            {t("guide")}
          </Link>
        </nav>

        <div className="flex items-center gap-2 sm:gap-3">
          <LocaleSwitcher className="hidden sm:block" />
          <Button
            variant="ghost"
            size="sm"
            onClick={startTour}
            className="hidden lg:inline-flex"
          >
            {t("startTour")}
          </Button>
          <a href={TELEGRAM_BOT_URL} target="_blank" rel="noopener noreferrer">
            <Button variant="primary" size="sm">
              <PaperPlaneTilt size={16} weight="fill" />
              {t("openTelegram")}
            </Button>
          </a>
        </div>
      </div>
    </header>
  );
}
