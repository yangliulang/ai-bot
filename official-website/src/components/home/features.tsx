import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import type { Icon } from "@phosphor-icons/react";
import {
  ChartLineUp,
  ChatCircleText,
  CheckCircle,
  CurrencyCircleDollar,
  Globe,
  Lock,
} from "@phosphor-icons/react/dist/ssr";

const featureKeys = [
  "nl",
  "subaccount",
  "confirm",
  "billing",
  "observability",
  "i18n",
] as const;

const icons: Record<(typeof featureKeys)[number], Icon> = {
  nl: ChatCircleText,
  subaccount: Lock,
  confirm: CheckCircle,
  billing: CurrencyCircleDollar,
  observability: ChartLineUp,
  i18n: Globe,
};

type FeaturesProps = {
  detailed?: boolean;
};

export function Features({ detailed = false }: FeaturesProps) {
  const t = useTranslations("features");

  return (
    <section className={cn("mx-auto max-w-[1400px] px-4 md:px-8", detailed ? "py-0" : "py-20 md:py-28")}>
      {!detailed && (
        <header className="mb-14 max-w-2xl">
          <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">
            {t("sectionTitle")}
          </h2>
          <p className="mt-4 text-base leading-relaxed text-muted">{t("sectionSubtitle")}</p>
        </header>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {featureKeys.map((key, i) => {
          const IconComponent = icons[key];
          const isWide = i === 0 || i === 3;
          return (
            <article
              key={key}
              className={cn(
                "group rounded-[2rem] border border-border bg-surface p-8 transition-all hover:border-accent/25",
                isWide && "md:col-span-1",
              )}
            >
              <IconComponent
                size={28}
                weight="duotone"
                className="text-accent"
                aria-hidden
              />
              <h3 className="mt-5 text-lg font-semibold tracking-tight">
                {t(`items.${key}.title`)}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-muted">
                {t(`items.${key}.description`)}
              </p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
