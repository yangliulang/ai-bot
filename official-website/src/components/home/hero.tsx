"use client";

import { useTranslations } from "next-intl";
import { PaperPlaneTilt, Play } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { useProductTour } from "@/components/guide/product-tour-provider";
import { HeroTelegramPreview } from "./hero-telegram-preview";
import { HeroAgentBackground } from "./hero-agent-background";
import { TELEGRAM_BOT_URL } from "@/lib/bind-links";

export function Hero() {
  const t = useTranslations("hero");
  const { startTour } = useProductTour();

  return (
    <section
      id="tour-hero"
      className="relative flex min-h-[100dvh] items-center overflow-x-clip"
    >
      <div className="pulsar-grid-bg pointer-events-none absolute inset-0 z-0" aria-hidden />
      <HeroAgentBackground />
      <div
        className="pointer-events-none absolute -left-32 top-0 z-0 h-[480px] w-[480px] rounded-full bg-accent/5 blur-3xl"
        aria-hidden
      />

      <div className="relative z-10 mx-auto grid w-full max-w-[1400px] gap-12 px-4 py-12 md:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)] md:items-center md:gap-10 md:px-8 md:py-16">
        <div className="animate-fade-up max-w-xl">
          <p className="text-xs font-medium uppercase tracking-[0.25em] text-accent">
            {t("eyebrow")}
          </p>
          <p className="mt-4 text-lg font-medium tracking-tight text-muted md:text-xl">
            {t("tagline")}
          </p>
          <h1 className="mt-3 text-4xl font-bold tracking-tighter leading-[1.05] md:text-5xl lg:text-6xl">
            {t("title")}
          </h1>
          <p className="mt-6 max-w-[55ch] text-base leading-relaxed text-muted md:text-lg">
            {t("subtitle")}
          </p>

          <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
            <a href={TELEGRAM_BOT_URL} target="_blank" rel="noopener noreferrer">
              <Button variant="primary" size="lg" className="w-full sm:w-auto">
                <PaperPlaneTilt size={20} weight="fill" />
                {t("ctaTelegram")}
              </Button>
            </a>
            <Button
              variant="secondary"
              size="lg"
              onClick={startTour}
              className="w-full sm:w-auto"
            >
              <Play size={18} weight="fill" />
              {t("ctaTour")}
            </Button>
          </div>
        </div>

        <div
          className="animate-fade-up relative ml-auto flex w-full max-w-[34rem] justify-end overflow-visible md:max-w-none"
          style={{ animationDelay: "120ms" }}
        >
          <div
            className="demo-stage-glow pointer-events-none absolute -inset-10 md:-inset-16"
            aria-hidden
          />
          <HeroTelegramPreview />
        </div>
      </div>
    </section>
  );
}
