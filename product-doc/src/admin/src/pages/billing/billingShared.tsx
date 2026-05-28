import { Tag } from "antd";

export function commerceSourceTag(source: "mock" | "remote" | "remote+fallback") {
  if (source === "remote") return <Tag color="processing">已接 Commerce API</Tag>;
  if (source === "remote+fallback") return <Tag color="warning">接口不可用 · 已回退 mock</Tag>;
  return <Tag>本地预览</Tag>;
}

export function orderStatusTag(status: string) {
  if (status === "SETTLED") return <Tag color="success">已到账</Tag>;
  if (status === "CONFIRMING") return <Tag color="processing">确认中</Tag>;
  if (status === "EXPIRED") return <Tag color="error">已过期</Tag>;
  return <Tag>待支付</Tag>;
}

export function grantStatusTag(status: string) {
  if (status === "APPLIED") return <Tag color="success">已入账</Tag>;
  if (status === "PENDING") return <Tag color="processing">待入账</Tag>;
  if (status === "FAILED") return <Tag color="error">入账失败</Tag>;
  return <Tag bordered={false}>—</Tag>;
}

export function formatBillingDate(iso: string | null): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString("zh-CN");
  } catch {
    return iso;
  }
}

export function formatBillingDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("zh-CN", { hour12: false });
  } catch {
    return iso;
  }
}

export function zhCommerceOrderKind(kind: "upgrade" | "pack"): string {
  return kind === "upgrade" ? "订阅升级" : "资源加购";
}

export function zhPaymentNetwork(network: string): string {
  if (network === "USDT_TRC20") return "TRC20";
  if (network === "USDT_ERC20") return "ERC20";
  return network;
}
