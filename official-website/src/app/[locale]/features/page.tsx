import { setRequestLocale } from "next-intl/server";
import { getTranslations } from "next-intl/server";
import { buildPageMetadata } from "@/lib/seo";
import type { Locale } from "@/i18n/routing";
import { Features } from "@/components/home/features";
import { ScrollReveal } from "@/components/ui/scroll-reveal";

type Props = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "metadata.features" });

  return buildPageMetadata({
    locale: locale as Locale,
    title: t("title"),
    description: t("description"),
    path: "/features",
  });
}

export default async function FeaturesPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("featuresPage");

  return (
    <div className="mx-auto max-w-[1400px] px-4 py-16 md:px-8 md:py-20">
      <header className="mb-12 max-w-2xl">
        <h1 className="text-4xl font-bold tracking-tighter">{t("title")}</h1>
        <p className="mt-4 text-lg text-muted">{t("subtitle")}</p>
      </header>
      <ScrollReveal>
        <Features detailed />
      </ScrollReveal>
    </div>
  );
}
