import type { ReactNode } from "react";

/** 独立落地页：不含主站顶栏、侧栏与 H5 底栏（Telegram Deeplink / 外部浏览器场景） */
export default function StandalonePageShell({ children }: { children: ReactNode }) {
  return (
    <div className="coolbit-standalone-root">
      <div className="coolbit-standalone-root__inner">{children}</div>
    </div>
  );
}
