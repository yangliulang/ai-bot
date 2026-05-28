import { useCallback, useEffect, useState, type RefObject } from "react";

/** Sticky header (4rem) + section scroll-margin (6rem), slightly tightened */
const GUIDE_SCROLL_ANCHOR_PX = 112;

export function resolveGuideActiveSection(sections: HTMLElement[]): number {
  if (sections.length === 0) return 0;

  let active = 0;
  for (let i = 0; i < sections.length; i++) {
    if (sections[i].getBoundingClientRect().top <= GUIDE_SCROLL_ANCHOR_PX) {
      active = i;
    }
  }
  return active;
}

export function useGuideSectionSpy(
  sectionRefs: RefObject<(HTMLElement | null)[]>,
  sectionCount: number,
) {
  const [activeSection, setActiveSection] = useState(0);

  const readSections = useCallback(() => {
    return (sectionRefs.current ?? [])
      .slice(0, sectionCount)
      .filter((node): node is HTMLElement => node != null);
  }, [sectionRefs, sectionCount]);

  useEffect(() => {
    let raf = 0;

    const update = () => {
      const nodes = readSections();
      if (nodes.length === 0) return;

      const next = resolveGuideActiveSection(nodes);
      setActiveSection((prev) => (prev === next ? prev : next));
    };

    const scheduleUpdate = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(update);
    };

    const boot = window.setTimeout(scheduleUpdate, 0);
    window.addEventListener("scroll", scheduleUpdate, { passive: true });
    window.addEventListener("resize", scheduleUpdate, { passive: true });

    return () => {
      window.clearTimeout(boot);
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", scheduleUpdate);
      window.removeEventListener("resize", scheduleUpdate);
    };
  }, [readSections]);

  return { activeSection, setActiveSection };
}
