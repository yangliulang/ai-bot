import type { MetadataRoute } from "next";
import { locales } from "@/i18n/routing";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://chainup-ai-agent.com";

const paths = ["", "/features", "/guide"] as const;

export default function sitemap(): MetadataRoute.Sitemap {
  const entries: MetadataRoute.Sitemap = [];

  for (const locale of locales) {
    const prefix = locale === "en" ? "" : `/${locale}`;

    for (const path of paths) {
      entries.push({
        url: `${siteUrl}${prefix}${path}`,
        lastModified: new Date(),
        changeFrequency: path === "" ? "weekly" : "monthly",
        priority: path === "" ? 1 : 0.8,
        alternates: {
          languages: Object.fromEntries(
            locales.map((l) => [
              l,
              `${siteUrl}${l === "en" ? "" : `/${l}`}${path}`,
            ]),
          ),
        },
      });
    }
  }

  return entries;
}
