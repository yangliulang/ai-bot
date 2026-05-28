"use client";

import { useEffect } from "react";
import { usePathname } from "@/i18n/navigation";

function scrollToHash(retry = 0) {
  const hash = window.location.hash;
  if (!hash) return;

  const target = document.getElementById(hash.slice(1));
  if (target) {
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }

  if (retry < 8) {
    window.setTimeout(() => scrollToHash(retry + 1), 80);
  }
}

export function HashScrollHandler() {
  const pathname = usePathname();

  useEffect(() => {
    scrollToHash();
  }, [pathname]);

  useEffect(() => {
    const onHashChange = () => scrollToHash();
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  return null;
}
