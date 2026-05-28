"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type ReactNode,
} from "react";
import { useTranslations } from "next-intl";
import { driver, type DriveStep } from "driver.js";
import "driver.js/dist/driver.css";

type ProductTourContextValue = {
  startTour: () => void;
};

const ProductTourContext = createContext<ProductTourContextValue | null>(null);

export function useProductTour() {
  const ctx = useContext(ProductTourContext);
  if (!ctx) {
    throw new Error("useProductTour must be used within ProductTourProvider");
  }
  return ctx;
}

export function ProductTourProvider({ children }: { children: ReactNode }) {
  const t = useTranslations("tour");

  const steps = useMemo<DriveStep[]>(
    () => [
      {
        popover: {
          title: t("welcome.title"),
          description: t("welcome.description"),
          side: "over",
          align: "center",
        },
      },
      {
        element: "#tour-hero",
        popover: {
          title: t("hero.title"),
          description: t("hero.description"),
          side: "bottom",
          align: "start",
        },
      },
      {
        element: "#tour-demo",
        popover: {
          title: t("demo.title"),
          description: t("demo.description"),
          side: "left",
          align: "center",
        },
      },
      {
        element: "#tour-stats",
        popover: {
          title: t("stats.title"),
          description: t("stats.description"),
          side: "top",
          align: "center",
        },
      },
      {
        element: "#tour-bind",
        popover: {
          title: t("bind.title"),
          description: t("bind.description"),
          side: "top",
          align: "start",
        },
      },
      {
        element: "#tour-estimator",
        popover: {
          title: t("estimator.title"),
          description: t("estimator.description"),
          side: "top",
          align: "center",
        },
      },
      {
        element: "#tour-chart",
        popover: {
          title: t("chart.title"),
          description: t("chart.description"),
          side: "top",
          align: "center",
        },
      },
      {
        element: "#tour-faq",
        popover: {
          title: t("faq.title"),
          description: t("faq.description"),
          side: "top",
          align: "center",
        },
      },
      {
        element: "#tour-cta",
        popover: {
          title: t("cta.title"),
          description: t("cta.description"),
          side: "top",
          align: "center",
        },
      },
      {
        popover: {
          title: t("done.title"),
          description: t("done.description"),
          side: "over",
          align: "center",
        },
      },
    ],
    [t],
  );

  const startTour = useCallback(() => {
    const driverObj = driver({
      showProgress: true,
      animate: true,
      smoothScroll: true,
      overlayOpacity: 0.72,
      stagePadding: 10,
      stageRadius: 16,
      popoverClass: "chainup-tour",
      nextBtnText: t("next"),
      prevBtnText: t("prev"),
      doneBtnText: t("done_btn"),
      steps,
    });

    driverObj.drive();
  }, [steps, t]);

  const value = useMemo(() => ({ startTour }), [startTour]);

  return (
    <ProductTourContext.Provider value={value}>
      {children}
    </ProductTourContext.Provider>
  );
}
