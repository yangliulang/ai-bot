"use client";

import { memo, useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { observeViewportCenterPresence } from "@/lib/viewport-center-observer";
import {
  ArrowRight,
  ChatCircle,
  Key,
  LinkSimple,
  PaperPlaneTilt,
} from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  DEEPLINK_BIND_URL,
  displayBindUrl,
  TELEGRAM_BOT_URL,
} from "@/lib/bind-links";
import { BindGuideStageBackground } from "@/components/home/bind-guide-stage-background";

const STEP_COUNT = 4;
const STEP_MS = 4200;

const stepIcons = [PaperPlaneTilt, LinkSimple, Key, ChatCircle] as const;

function BindGuideVisual({
  activeStep,
  reducedMotion,
  className,
}: {
  activeStep: number;
  reducedMotion: boolean;
  className?: string;
}) {
  const t = useTranslations("bindGuide.visual");

  return (
    <div
      className={cn(
        "bind-guide-stage relative min-h-88 w-full flex-1 overflow-hidden rounded-4xl border border-white/10 shadow-[0_28px_56px_-28px_rgba(0,0,0,0.55)] sm:min-h-104 md:min-h-136 lg:min-h-152",
        className,
      )}
    >
      <BindGuideStageBackground activeStep={activeStep} reducedMotion={reducedMotion} />
      <div className="bind-guide-scan pointer-events-none absolute inset-0 z-10" aria-hidden />

      <div
        className={cn(
          "absolute inset-0 z-20 flex w-full min-w-0 flex-col p-6 transition-opacity duration-500 sm:p-8 md:p-10",
          activeStep === 0 ? "opacity-100" : "pointer-events-none opacity-0",
          reducedMotion && activeStep !== 0 && "hidden",
        )}
        aria-hidden={activeStep !== 0}
      >
        <div className="mb-5 flex shrink-0 items-center gap-3 border-b border-white/8 pb-4 md:mb-6 md:pb-5">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-accent/20 text-accent md:h-12 md:w-12">
            <PaperPlaneTilt size={22} weight="fill" />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-medium text-zinc-100 md:text-base">{t("botName")}</p>
            <p className="text-xs text-zinc-500 md:text-sm">{t("botStatus")}</p>
          </div>
        </div>
        <div className="flex min-h-0 w-full flex-1 flex-col justify-center gap-3 md:gap-4">
          <div className="ml-auto w-fit max-w-[min(100%,16rem)] rounded-2xl rounded-br-md bg-accent px-4 py-2.5 text-sm text-zinc-950 sm:max-w-[min(100%,18rem)] md:px-5 md:py-3 md:text-base">
            {t("userHello")}
          </div>
          <div className="mr-auto w-fit max-w-[min(100%,22rem)] rounded-2xl rounded-bl-md bg-[#182533] px-4 py-3 text-sm leading-relaxed text-zinc-200 sm:max-w-[min(100%,26rem)] md:px-5 md:py-3.5 md:text-base">
            {t("botWelcome")}
          </div>
          <div
            className={cn(
              "bind-guide-pulse mr-auto flex w-fit max-w-full items-center gap-2 rounded-full border border-accent/40 bg-accent/15 px-4 py-2 text-xs font-medium whitespace-nowrap text-accent md:px-5 md:py-2.5 md:text-sm",
              !reducedMotion && activeStep === 0 && "bind-guide-pulse-active",
            )}
          >
            <LinkSimple size={16} weight="bold" className="shrink-0" />
            {t("bindButton")}
          </div>
        </div>
      </div>

      <div
        className={cn(
          "absolute inset-0 z-20 flex w-full min-w-0 flex-col justify-center p-6 transition-opacity duration-500 sm:p-8 md:p-10",
          activeStep === 1 ? "opacity-100" : "pointer-events-none opacity-0",
          reducedMotion && activeStep !== 1 && "hidden",
        )}
        aria-hidden={activeStep !== 1}
      >
        <div className="bind-guide-stage-panel w-full rounded-2xl border border-white/10 bg-[#141416]/90 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)] backdrop-blur-sm md:p-5">
          <div className="mb-3 flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-red-400/80" />
            <span className="h-2.5 w-2.5 rounded-full bg-amber-400/80" />
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/80" />
          </div>
          <p className="truncate font-mono text-xs text-accent/90 md:text-sm">
            {displayBindUrl(DEEPLINK_BIND_URL)}
          </p>
        </div>
        <div className="bind-guide-stage-panel mt-5 w-full space-y-2 rounded-2xl border border-accent/25 bg-accent/8 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] backdrop-blur-sm md:mt-6 md:p-5">
          <p className="text-xs uppercase tracking-wider text-accent/80 md:text-sm">{t("deeplinkTag")}</p>
          <p className="text-sm leading-relaxed text-zinc-300 md:text-base">{t("deeplinkHint")}</p>
        </div>
      </div>

      <div
        className={cn(
          "absolute inset-0 z-20 flex w-full min-w-0 flex-col justify-center p-6 transition-opacity duration-500 sm:p-8 md:p-10",
          activeStep === 2 ? "opacity-100" : "pointer-events-none opacity-0",
          reducedMotion && activeStep !== 2 && "hidden",
        )}
        aria-hidden={activeStep !== 2}
      >
        <div className="bind-guide-stage-panel w-full rounded-2xl border border-white/10 bg-[#0d1117]/85 p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.07)] backdrop-blur-md md:p-7">
          <p className="mb-4 text-sm font-medium text-zinc-100 md:mb-5 md:text-base">{t("formTitle")}</p>
          <div className="space-y-3 md:space-y-4">
            {(["fieldUid", "fieldKey", "fieldSecret"] as const).map((key, i) => (
              <div
                key={key}
                className={cn(
                  "rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 transition-colors duration-300 md:px-5 md:py-4",
                  activeStep === 2 && i === 1 && !reducedMotion && "border-accent/40 bg-accent/8 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)]",
                )}
              >
                <p className="text-[10px] uppercase tracking-wider text-zinc-500 md:text-xs">{t(`${key}Label`)}</p>
                <p className="mt-1 font-mono text-xs text-zinc-400 md:text-sm">{t(`${key}Placeholder`)}</p>
              </div>
            ))}
          </div>
          <div className="bind-guide-pulse mt-5 inline-flex rounded-full bg-accent px-4 py-2 text-xs font-medium whitespace-nowrap text-zinc-950 md:mt-6 md:px-5 md:py-2.5 md:text-sm">
            {t("confirmBind")}
          </div>
        </div>
      </div>

      <div
        className={cn(
          "absolute inset-0 z-20 flex w-full min-w-0 flex-col items-center justify-center p-6 text-center transition-opacity duration-500 sm:p-8 md:p-10",
          activeStep === 3 ? "opacity-100" : "pointer-events-none opacity-0",
          reducedMotion && activeStep !== 3 && "hidden",
        )}
        aria-hidden={activeStep !== 3}
      >
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-accent/20 text-accent md:h-20 md:w-20">
          <ChatCircle size={36} weight="duotone" />
        </span>
        <p className="mt-4 text-base font-medium text-zinc-100 md:mt-5 md:text-lg">{t("doneTitle")}</p>
        <p className="mt-2 max-w-xs text-sm leading-relaxed text-zinc-400 md:max-w-sm md:text-base">{t("doneHint")}</p>
      </div>
    </div>
  );
}

const BindGuideVisualMemo = memo(BindGuideVisual);

export function TelegramBindGuide() {
  const t = useTranslations("bindGuide");
  const [activeStep, setActiveStep] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [inView, setInView] = useState(false);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => setReducedMotion(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);

  useEffect(() => {
    const node = sectionRef.current;
    if (!node) return;
    return observeViewportCenterPresence(node, setInView);
  }, []);

  useEffect(() => {
    if (!inView || reducedMotion) return;
    const timer = window.setInterval(() => {
      setActiveStep((prev) => (prev + 1) % STEP_COUNT);
    }, STEP_MS);
    return () => window.clearInterval(timer);
  }, [inView, reducedMotion]);

  const steps = Array.from({ length: STEP_COUNT }, (_, i) => ({
    title: t(`steps.${i}.title`),
    description: t(`steps.${i}.description`),
    Icon: stepIcons[i]!,
  }));

  return (
    <section
      id="tour-bind"
      ref={sectionRef}
      className="relative overflow-hidden bg-surface/40 py-20 md:py-28"
    >
      <div className="relative z-10 mx-auto grid max-w-[1400px] gap-10 px-4 md:grid-cols-2 md:items-stretch md:gap-12 lg:gap-16 md:px-8">
        <div className="flex max-w-xl flex-col md:max-w-none md:py-1">
          <p className="text-xs font-medium uppercase tracking-[0.25em] text-accent">
            {t("eyebrow")}
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tighter md:text-4xl">{t("title")}</h2>
          <p className="mt-4 text-base leading-relaxed text-muted">{t("subtitle")}</p>

          <ol className="mt-8 space-y-3">
            {steps.map((step, index) => {
              const isActive = activeStep === index;
              const Icon = step.Icon;
              return (
                <li key={step.title}>
                  <button
                    type="button"
                    onClick={() => setActiveStep(index)}
                    className={cn(
                      "group flex w-full items-start gap-3 rounded-2xl border px-4 py-3.5 text-left transition-all duration-300 active:scale-[0.99]",
                      isActive
                        ? "border-accent/35 bg-accent/10"
                        : "border-border bg-surface/40 hover:border-accent/20 hover:bg-surface/70",
                    )}
                  >
                    <span
                      className={cn(
                        "mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border transition-colors",
                        isActive
                          ? "border-accent/40 bg-accent/15 text-accent"
                          : "border-white/10 bg-white/5 text-muted group-hover:text-foreground",
                      )}
                    >
                      <Icon size={18} weight={isActive ? "fill" : "regular"} />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="flex items-center gap-2">
                        <span className="font-mono text-[10px] text-muted/80">
                          {String(index + 1).padStart(2, "0")}
                        </span>
                        <span className="text-sm font-medium text-foreground">{step.title}</span>
                      </span>
                      <span className="mt-1 block text-xs leading-relaxed text-muted">
                        {step.description}
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ol>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <a href={TELEGRAM_BOT_URL} target="_blank" rel="noopener noreferrer">
              <Button variant="primary" size="lg" className="w-full sm:w-auto">
                <PaperPlaneTilt size={18} weight="fill" />
                {t("openBot")}
              </Button>
            </a>
            <a href={DEEPLINK_BIND_URL} target="_blank" rel="noopener noreferrer">
              <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                <LinkSimple size={18} weight="bold" />
                {t("openBindPage")}
                <ArrowRight size={16} className="ml-0.5 opacity-70" />
              </Button>
            </a>
          </div>

          <p className="mt-4 font-mono text-[11px] text-muted/80">{displayBindUrl(DEEPLINK_BIND_URL)}</p>
          <p className="mt-2 text-xs leading-relaxed text-muted/90">{t("safetyNote")}</p>
        </div>

        <div className="relative flex min-h-88 flex-col sm:min-h-104 md:min-h-0">
          <BindGuideVisualMemo
            activeStep={activeStep}
            reducedMotion={reducedMotion}
            className="relative flex-1"
          />
        </div>
      </div>
    </section>
  );
}
