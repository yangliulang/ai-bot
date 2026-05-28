import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { ChainUpAgentLogo } from "@/components/brand/chainup-agent-logo";

export async function Footer() {
  const t = await getTranslations("footer");
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto grid max-w-[1400px] gap-10 px-4 py-12 md:grid-cols-4 md:px-8">
        <div className="md:col-span-1">
          <div className="flex items-center gap-2.5">
            <ChainUpAgentLogo size={28} />
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">
              ChainUp Agent
            </p>
          </div>
          <p className="mt-3 text-sm leading-relaxed text-muted">{t("tagline")}</p>
        </div>

        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-muted">
            {t("product")}
          </p>
          <ul className="mt-4 space-y-2.5 text-sm text-muted">
            <li>
              <Link href="/features" className="hover:text-foreground">
                {t("features")}
              </Link>
            </li>
            <li>
              <Link href="/guide" className="hover:text-foreground">
                {t("guide")}
              </Link>
            </li>
          </ul>
        </div>

        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-muted">
            {t("resources")}
          </p>
          <ul className="mt-4 space-y-2.5 text-sm text-muted">
            <li>
              <Link href="/#tour-faq" className="hover:text-foreground">
                {t("faq")}
              </Link>
            </li>
            <li>
              <a href="#" className="hover:text-foreground">
                {t("docs")}
              </a>
            </li>
          </ul>
        </div>

        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-muted">
            {t("legal")}
          </p>
          <ul className="mt-4 space-y-2.5 text-sm text-muted">
            <li>
              <a href="#" className="hover:text-foreground">
                {t("terms")}
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-foreground">
                {t("privacy")}
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-foreground">
                {t("risk")}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-border px-4 py-6 text-center text-xs text-muted md:px-8">
        {t("copyright", { year })}
      </div>
    </footer>
  );
}
