const LS_KEY = "admin.agent.g01Banner.dismissedUtcDay";

function utcCalendarDay(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export function isG01BannerDismissedForUtcToday(): boolean {
  try {
    return localStorage.getItem(LS_KEY) === utcCalendarDay(new Date());
  } catch {
    return false;
  }
}

/** 「当日不再显示」— UTC 日历日复位后再显（config §1.1） */
export function dismissG01BannerForUtcToday(): void {
  try {
    localStorage.setItem(LS_KEY, utcCalendarDay(new Date()));
  } catch {
    /* ignore quota / private mode */
  }
}
