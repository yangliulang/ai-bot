"use client";

import { useRef } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import {
  ArrowRight,
  CaretRight,
  ChatCircle,
  CheckCircle,
  GearSix,
  PaperPlaneTilt,
  PlayCircle,
  ShieldCheck,
  type Icon,
} from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { cn } from "@/lib/utils";
import { TELEGRAM_BOT_URL } from "@/lib/bind-links";
import { useGuideSectionSpy } from "@/hooks/use-guide-section-spy";
import { GuideProgressVisual } from "./guide-progress-visual";

const sectionKeys = [
  "prerequisites",
  "onboarding",
  "firstTrade",
  "safety",
] as const;

type SectionKey = (typeof sectionKeys)[number];

const sectionItemCounts: Record<SectionKey, number> = {
  prerequisites: 3,
  onboarding: 4,
  firstTrade: 4,
  safety: 4,
};

const sectionIcons: Record<SectionKey, Icon> = {
  prerequisites: CheckCircle,
  onboarding: GearSix,
  firstTrade: ChatCircle,
  safety: ShieldCheck,
};

export function GuideContent() {
  const t = useTranslations("guide");
  const tNav = useTranslations("nav");
  const sectionRefs = useRef<(HTMLElement | null)[]>([]);
  const { activeSection, setActiveSection } = useGuideSectionSpy(
    sectionRefs,
    sectionKeys.length,
  );

  const scrollToSection = (index: number) => {
    setActiveSection(index);
    sectionRefs.current[index]?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  return (
    <div className="relative isolate">
      {/* 装饰层单独裁剪，避免 overflow 打断 sticky，也避免 -right-32 撑出横向滚动条 */}
      <div
        className="pointer-events-none absolute inset-0 overflow-hidden"
        aria-hidden
      >
        <div className="absolute inset-x-0 top-0 h-[520px] pulsar-grid-bg opacity-60" />
        <div className="absolute -right-32 top-24 h-80 w-80 rounded-full bg-accent/6 blur-[100px]" />
      </div>

      <div className="relative mx-auto max-w-[1400px] px-4 pb-20 md:px-8 md:pb-28">
        <header className="grid gap-10 pt-12 md:grid-cols-[minmax(0,1fr)_minmax(280px,380px)] md:items-end md:gap-12 md:pt-16 lg:gap-16">
          <div className="max-w-2xl animate-fade-up">
            <p className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-accent">
              <span className="h-1.5 w-1.5 rounded-full bg-accent" aria-hidden />
              {t("eyebrow")}
            </p>
            <h1 className="mt-5 text-4xl font-bold tracking-tighter text-foreground md:text-5xl lg:text-6xl">
              {t("title")}
            </h1>
            <p className="mt-5 max-w-[65ch] text-base leading-relaxed text-muted md:text-lg">
              {t("subtitle")}
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <a href={TELEGRAM_BOT_URL} target="_blank" rel="noopener noreferrer">
                <Button variant="primary" size="lg" className="w-full sm:w-auto">
                  <PaperPlaneTilt size={20} weight="fill" />
                  {tNav("openTelegram")}
                </Button>
              </a>
              <Link href="/">
                <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                  <PlayCircle size={20} weight="duotone" />
                  {tNav("startTour")}
                </Button>
              </Link>
            </div>
          </div>

          <GuideProgressVisual
            activeStep={activeSection}
            labels={sectionKeys.map((key) => t(`sections.${key}.title`))}
            stepsLabel={t("stepsLabel")}
          />
        </header>

        <div className="mt-16 grid gap-10 lg:mt-20 lg:grid-cols-[220px_minmax(0,1fr)] lg:gap-14 xl:grid-cols-[240px_minmax(0,1fr)]">
          <div className="relative hidden min-h-0 lg:block">
            <nav
              className="sticky top-16 z-20 w-full py-4"
              aria-label={t("stepsLabel")}
            >
              <p className="mb-5 text-xs font-medium uppercase tracking-[0.16em] text-muted">
                {t("stepsLabel")}
              </p>
              <ol className="relative space-y-1">
                <span
                  className="bind-guide-rail pointer-events-none absolute bottom-7 left-6 top-7 w-px -translate-x-1/2"
                  aria-hidden
                />
                {sectionKeys.map((key, index) => {
                  const IconComponent = sectionIcons[key];
                  const isActive = activeSection === index;

                  return (
                    <li key={key}>
                      <button
                        type="button"
                        onClick={() => scrollToSection(index)}
                        className={cn(
                          "group flex w-full items-center gap-3 rounded-xl px-2 py-3 text-left transition-all duration-200",
                          isActive
                            ? "bg-accent/10 text-foreground"
                            : "text-muted hover:bg-surface-elevated/60 hover:text-foreground",
                        )}
                        aria-current={isActive ? "step" : undefined}
                      >
                        <span
                          className={cn(
                            "relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border text-xs font-semibold transition-colors",
                            isActive
                              ? "border-accent/40 bg-accent text-zinc-950"
                              : "border-border bg-surface text-muted group-hover:border-accent/25",
                          )}
                        >
                          {index + 1}
                        </span>
                        <span className="min-w-0 flex-1">
                          <span className="block truncate text-sm font-medium">
                            {t(`sections.${key}.title`)}
                          </span>
                        </span>
                        <span className="flex size-4 shrink-0 items-center justify-center">
                          <IconComponent
                            size={16}
                            weight="duotone"
                            className={cn(
                              "size-4 transition-opacity",
                              isActive
                                ? "text-accent opacity-100"
                                : "opacity-0 group-hover:opacity-60",
                            )}
                            aria-hidden
                          />
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ol>
            </nav>
          </div>

          <div className="min-w-0 space-y-8 md:space-y-10">
            {sectionKeys.map((key, index) => {
              const IconComponent = sectionIcons[key];
              const isSafety = key === "safety";

              return (
                <ScrollReveal key={key} delay={index * 80}>
                  <section
                    id={`guide-${key}`}
                    ref={(el) => {
                      sectionRefs.current[index] = el;
                    }}
                    className={cn(
                      "scroll-mt-24 rounded-4xl border p-6 md:p-8 lg:p-10",
                      isSafety
                        ? "border-accent/25 bg-accent/5 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]"
                        : "glass-panel border-white/10",
                    )}
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div className="flex items-start gap-4">
                        <span
                          className={cn(
                            "flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl",
                            isSafety ? "bg-accent/15 text-accent" : "bg-accent/10 text-accent",
                          )}
                        >
                          <IconComponent size={26} weight="duotone" aria-hidden />
                        </span>
                        <div>
                          <p className="text-xs font-medium uppercase tracking-[0.14em] text-accent/80">
                            {t("stepLabel", { step: index + 1 })}
                          </p>
                          <h2 className="mt-1 text-2xl font-semibold tracking-tight md:text-3xl">
                            {t(`sections.${key}.title`)}
                          </h2>
                          <p className="mt-2 max-w-[60ch] text-sm leading-relaxed text-muted md:text-base">
                            {t(`sections.${key}.summary`)}
                          </p>
                        </div>
                      </div>
                      <span className="hidden font-mono text-5xl font-bold leading-none text-white/5 sm:block">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                    </div>

                    <ol className="mt-8 space-y-3">
                      {Array.from({ length: sectionItemCounts[key] }, (_, idx) => (
                        <li
                          key={idx}
                          className={cn(
                            "group flex gap-4 rounded-2xl border px-4 py-4 transition-colors md:px-5 md:py-4",
                            isSafety
                              ? "border-accent/15 bg-surface/60 hover:border-accent/30"
                              : "border-border/80 bg-surface-elevated/40 hover:border-accent/20 hover:bg-surface-elevated/70",
                          )}
                          style={{ animationDelay: `${idx * 60}ms` }}
                        >
                          <span
                            className={cn(
                              "mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
                              isSafety
                                ? "bg-accent/15 text-accent"
                                : "bg-accent/10 text-accent",
                            )}
                          >
                            {idx + 1}
                          </span>
                          <p className="text-sm leading-relaxed text-zinc-200 md:text-base">
                            {t(`sections.${key}.items.${idx}`)}
                          </p>
                          <CaretRight
                            size={16}
                            className="ml-auto mt-1 shrink-0 text-muted opacity-0 transition-all group-hover:translate-x-0.5 group-hover:opacity-60"
                            aria-hidden
                          />
                        </li>
                      ))}
                    </ol>
                  </section>
                </ScrollReveal>
              );
            })}

            <ScrollReveal delay={320}>
              <aside className="glass-panel rounded-4xl border-white/10 p-6 md:p-8">
                <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                  <div className="max-w-xl">
                    <h2 className="text-xl font-semibold tracking-tight md:text-2xl">
                      {t("ctaTitle")}
                    </h2>
                    <p className="mt-2 text-sm leading-relaxed text-muted md:text-base">
                      {t("ctaSubtitle")}
                    </p>
                  </div>
                  <div className="flex flex-col gap-3 sm:flex-row">
                    <a href={TELEGRAM_BOT_URL} target="_blank" rel="noopener noreferrer">
                      <Button variant="primary" size="md" className="w-full sm:w-auto">
                        <PaperPlaneTilt size={18} weight="fill" />
                        {tNav("openTelegram")}
                      </Button>
                    </a>
                    <Link href="/">
                      <Button variant="secondary" size="md" className="w-full sm:w-auto">
                        {t("tourHint")}
                        <ArrowRight size={16} weight="bold" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </aside>
            </ScrollReveal>
          </div>
        </div>
      </div>
    </div>
  );
}
