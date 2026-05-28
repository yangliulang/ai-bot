import type { Metadata } from "next";
import { locales, type Locale } from "@/i18n/routing";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://chainup-ai-agent.com";

type PageMetaInput = {
  locale: Locale;
  title: string;
  description: string;
  path?: string;
};

export function buildPageMetadata({
  locale,
  title,
  description,
  path = "",
}: PageMetaInput): Metadata {
  const url = `${siteUrl}${locale === "en" ? "" : `/${locale}`}${path}`;

  return {
    title,
    description,
    metadataBase: new URL(siteUrl),
    alternates: {
      canonical: url,
      languages: Object.fromEntries(
        locales.map((l) => [
          l,
          `${siteUrl}${l === "en" ? "" : `/${l}`}${path}`,
        ]),
      ),
    },
    openGraph: {
      title,
      description,
      url,
      siteName: "ChainUp AI Agent",
      locale,
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
    robots: {
      index: true,
      follow: true,
    },
  };
}

export function buildOrganizationJsonLd(locale: Locale) {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "ChainUp AI Agent",
    applicationCategory: "FinanceApplication",
    operatingSystem: "Telegram",
    inLanguage: locale,
    url: siteUrl,
    description:
      "Natural-language trading assistant for exchange users via Telegram.",
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
    },
  };
}
