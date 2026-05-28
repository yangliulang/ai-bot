import { setRequestLocale } from "next-intl/server";
import { getTranslations } from "next-intl/server";
import { buildPageMetadata } from "@/lib/seo";
import type { Locale } from "@/i18n/routing";
import { GuideContent } from "@/components/guide/guide-content";

type Props = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "metadata.guide" });

  return buildPageMetadata({
    locale: locale as Locale,
    title: t("title"),
    description: t("description"),
    path: "/guide",
  });
}

export default async function GuidePage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);

  return <GuideContent />;
}
