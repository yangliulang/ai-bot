import type { ReactNode } from "react";
import { Link } from "react-router-dom";

type Props = {
  title: string;
  /** 标题下灰色补充说明（可选） */
  subtitle?: ReactNode;
  /** 右上角关闭跳转；**`false`** 时不展示关闭（独立落地页常用） */
  closeTo?: string | false;
  wide?: boolean;
  tone?: "default" | "success";
  /** 追加根节点 class（如独立落地页留白） */
  className?: string;
  children: ReactNode;
};

/** 对齐 Coolbit 账户类弹层：白底、顶线、圆角 */
export function OnboardingPanel({
  title,
  subtitle,
  closeTo = "/",
  wide,
  tone = "default",
  className,
  children,
}: Props) {
  const showClose = closeTo !== false;

  return (
    <div
      className={[
        "coolbit-onboarding-panel",
        wide ? "coolbit-onboarding-panel--wide" : "",
        tone === "success" ? "coolbit-onboarding-panel--tone-success" : "",
        className ?? "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="coolbit-onboarding-panel__head">
        <div className="coolbit-onboarding-panel__title-wrap">
          <h2 className="coolbit-onboarding-panel__title">{title}</h2>
          {subtitle ? <p className="coolbit-onboarding-panel__subtitle">{subtitle}</p> : null}
        </div>
        {showClose ? (
          <Link to={closeTo} className="coolbit-onboarding-panel__close" aria-label="关闭">
            ×
          </Link>
        ) : (
          <span className="coolbit-onboarding-panel__close-placeholder" aria-hidden />
        )}
      </div>
      {children}
    </div>
  );
}
