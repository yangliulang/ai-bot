import { Navigate, useSearchParams } from "react-router-dom";
import { resolveH5PathFromTelegramStart } from "@/lib/commerceDeeplink";

/** 兼容旧路由 `/subaccount/agent-billing` → `/subaccount/billing` */
export default function AgentBillingPage() {
  const [searchParams] = useSearchParams();

  const start = searchParams.get("start");
  if (start) {
    const target = resolveH5PathFromTelegramStart(start);
    if (target) {
      const u = new URL(target, window.location.origin);
      return <Navigate to={`${u.pathname}${u.search}`} replace />;
    }
  }

  const intent = searchParams.get("intent");
  const next = new URLSearchParams(searchParams);
  next.delete("intent");
  next.delete("start");
  const qs = next.toString() ? `?${next.toString()}` : "";

  if (intent === "upgrade") {
    return <Navigate to={`/subscription/upgrade${qs}`} replace />;
  }
  if (intent === "buy-pack") {
    return <Navigate to={`/subscription/pack${qs}`} replace />;
  }

  const tab = next.get("tab");
  if (tab === "quota") {
    next.delete("tab");
    next.set("tab", "overview");
  }
  const merged = next.toString();
  return <Navigate to={`/subaccount/billing${merged ? `?${merged}` : ""}`} replace />;
}
