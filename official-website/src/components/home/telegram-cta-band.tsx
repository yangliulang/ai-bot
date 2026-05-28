"use client";

import { useTranslations } from "next-intl";
import { PaperPlaneTilt } from "@phosphor-icons/react";
import { Link } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";
import { TELEGRAM_BOT_URL } from "@/lib/bind-links";

export function TelegramCtaBand() {
  const t = useTranslations("ctaBand");

  return (
    <section
      id="tour-cta"
      className="relative overflow-hidden bg-surface/50 py-14 md:py-20"
    >
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_0%,color-mix(in_srgb,var(--accent)_8%,transparent),transparent_70%)]"
        aria-hidden
      />
      <div className="relative mx-auto flex max-w-[1400px] flex-col items-center gap-6 px-4 text-center md:px-8">
        <p className="text-sm text-muted">{t("support")}</p>
        <a href={TELEGRAM_BOT_URL} target="_blank" rel="noopener noreferrer">
          <Button variant="primary" size="lg">
            <PaperPlaneTilt size={20} weight="fill" />
            {t("telegram")}
          </Button>
        </a>
        <Link href="/guide" className="text-sm text-muted underline-offset-4 hover:text-foreground hover:underline">
          {t("guideLink")}
        </Link>
      </div>
    </section>
  );
}
