export const VIEWPORT_CENTER_ROOT_MARGIN = "-32% 0px -32% 0px";

export const viewportCenterObserverOptions: IntersectionObserverInit = {
  root: null,
  rootMargin: VIEWPORT_CENTER_ROOT_MARGIN,
  threshold: 0,
};

type ObserveViewportCenterOptions = {
  once?: boolean;
  fallbackMs?: number;
};

/** Fire when the element enters the central band of the viewport (~36% height). */
export function observeWhenViewportCenter(
  element: Element,
  callback: () => void,
  options?: ObserveViewportCenterOptions,
): () => void {
  const { once = true, fallbackMs = 2400 } = options ?? {};

  const fallback = window.setTimeout(callback, fallbackMs);

  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        window.clearTimeout(fallback);
        callback();
        if (once) observer.disconnect();
      }
    },
    viewportCenterObserverOptions,
  );

  observer.observe(element);
  return () => {
    window.clearTimeout(fallback);
    observer.disconnect();
  };
}

/** Continuous center-band visibility (e.g. pause/resume looping demos). */
export function observeViewportCenterPresence(
  element: Element,
  onChange: (visible: boolean) => void,
): () => void {
  const observer = new IntersectionObserver(
    ([entry]) => onChange(entry?.isIntersecting ?? false),
    viewportCenterObserverOptions,
  );

  observer.observe(element);
  return () => observer.disconnect();
}
