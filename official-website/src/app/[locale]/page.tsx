import { setRequestLocale } from "next-intl/server";
import { getTranslations } from "next-intl/server";
import { buildOrganizationJsonLd, buildPageMetadata } from "@/lib/seo";
import type { Locale } from "@/i18n/routing";
import { Hero } from "@/components/home/hero";
import { PlatformStats } from "@/components/home/platform-stats";
import { TelegramBindGuide } from "@/components/home/telegram-bind-guide";
import { UsageEstimator } from "@/components/home/usage-estimator";
import { ActivityChart } from "@/components/home/activity-chart";
import { FaqSection } from "@/components/home/faq-section";
import { TelegramCtaBand } from "@/components/home/telegram-cta-band";
import { ScrollReveal } from "@/components/ui/scroll-reveal";

type Props = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "metadata.home" });

  return buildPageMetadata({
    locale: locale as Locale,
    title: t("title"),
    description: t("description"),
  });
}

export default async function HomePage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);

  const jsonLd = buildOrganizationJsonLd(locale as Locale);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Hero />
      <PlatformStats />
      <ScrollReveal>
        <TelegramBindGuide />
      </ScrollReveal>
      <ScrollReveal delay={80}>
        <UsageEstimator />
      </ScrollReveal>
      <ScrollReveal delay={120}>
        <ActivityChart />
      </ScrollReveal>
      <ScrollReveal delay={120}>
        <FaqSection />
      </ScrollReveal>
      <TelegramCtaBand />
    </>
  );
}
