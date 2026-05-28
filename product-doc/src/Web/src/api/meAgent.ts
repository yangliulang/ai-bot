/**
 * Agent 产品线 `me/agent/*` 开通 · 绑定 HTTP（对齐 `specs/openapi/user/onboarding.yaml`）。
 * 基址见 `getAgentApiBase()`；未配置时由页面走演示分支。
 */

export type TradingApiBindPayload = {
  idempotencyKey: string;
  /** 交易所侧子账户 UID（`subUid`）；可与 Key 归属交叉校验 */
  agentSubAccountUid: string;
  apiKey: string;
  apiSecret: string;
  /** Deeplink 签发的一次性票据（若有），非 Secret */
  deeplinkToken?: string;
};

export type TradingApiBindResult = {
  agentTradingApiBindingStatus?: string;
  agentTradingApiKeyId?: string;
  agentSubAccountId?: string;
};

/** 与 `specs/openapi/components/onboarding-schemas.yaml` · `TradingApiBindRejectCode` 同窗 */
export type TradingApiBindRejectCode =
  | "AGENT_BIND_KEY_NOT_SUBACCOUNT"
  | "AGENT_BIND_SUBACCOUNT_UID_MISMATCH"
  | "AGENT_BIND_SUBACCOUNT_DISABLED"
  | "AGENT_BIND_API_TRADING_DISABLED"
  | "AGENT_BIND_SPOT_PERMISSION_DISABLED"
  | "AGENT_BIND_MARGIN_PERMISSION_DISABLED"
  | "AGENT_BIND_FUTURES_PERMISSION_DISABLED"
  | "AGENT_BIND_PERMISSION_INCOMPLETE";

/** 与 `MissingPermissionKind` 同窗 */
export type MissingPermissionKind = "API_TRADING" | "SPOT" | "MARGIN" | "FUTURES";

export type ApiErrorBody = {
  title?: string;
  detail?: string;
  message?: string;
  status?: number;
  code?: string;
  details?: { missingPermissions?: MissingPermissionKind[] };
};

const MISSING_PERM_LABEL: Record<MissingPermissionKind, string> = {
  API_TRADING: "API 交易",
  SPOT: "币币",
  MARGIN: "杠杆",
  FUTURES: "合约",
};

const BIND_REJECT_MESSAGE: Record<TradingApiBindRejectCode, string> = {
  AGENT_BIND_KEY_NOT_SUBACCOUNT:
    "当前 API Key 属于主账户。Agent 仅支持子账户 API Key，请在交易所创建子账户并使用其子账户 Key。",
  AGENT_BIND_SUBACCOUNT_UID_MISMATCH:
    "子账户 UID 与当前 API Key 不匹配。请核对交易所子账户列表中的 UID，或改用属于该 UID 的子账户 Key。",
  AGENT_BIND_SUBACCOUNT_DISABLED: "该子账户当前为禁用状态，请在交易所激活子账户后再保存。",
  AGENT_BIND_API_TRADING_DISABLED: "请为该子账户 API Key 开启「API 交易」权限。",
  AGENT_BIND_SPOT_PERMISSION_DISABLED: "请为该子账户 API Key 开启「币币」交易权限。",
  AGENT_BIND_MARGIN_PERMISSION_DISABLED: "请为该子账户 API Key 开启「杠杆」权限。",
  AGENT_BIND_FUTURES_PERMISSION_DISABLED: "请为该子账户 API Key 开启「合约」权限。",
  AGENT_BIND_PERMISSION_INCOMPLETE:
    "请为该子账户 API Key 同时开启 API 交易、币币、杠杆与合约权限；以下为仍未开启的项：",
};

export class TradingApiBindError extends Error {
  readonly status: number;
  readonly code?: TradingApiBindRejectCode;
  readonly raw?: unknown;

  constructor(
    message: string,
    opts: { status: number; code?: TradingApiBindRejectCode; raw?: unknown },
  ) {
    super(message);
    this.name = "TradingApiBindError";
    this.status = opts.status;
    this.code = opts.code;
    this.raw = opts.raw;
  }
}

/** 将绑定接口错误体映射为可读中文（优先 `code`，否则 RFC7807-style `detail`/`title`/`message`）。 */
export function messageFromTradingApiBindProblem(body: unknown, httpStatus: number): string {
  const prob = body as ApiErrorBody | undefined;
  const code = prob?.code as TradingApiBindRejectCode | undefined;

  if (code && BIND_REJECT_MESSAGE[code]) {
    if (code === "AGENT_BIND_PERMISSION_INCOMPLETE") {
      const missing = prob?.details?.missingPermissions?.filter(Boolean);
      if (missing?.length) {
        const labels = missing.map((k) => MISSING_PERM_LABEL[k] ?? k);
        return `${BIND_REJECT_MESSAGE.AGENT_BIND_PERMISSION_INCOMPLETE}${labels.join("、")}。`;
      }
      return `${BIND_REJECT_MESSAGE.AGENT_BIND_PERMISSION_INCOMPLETE}API 交易、币币、杠杆、合约。`;
    }
    return BIND_REJECT_MESSAGE[code];
  }

  const fallback =
    prob?.detail ?? prob?.message ?? prob?.title ?? `绑定失败（HTTP ${httpStatus}）`;
  return fallback;
}

function stripTrailingSlash(base: string): string {
  return base.replace(/\/+$/, "");
}

export function getAgentApiBase(): string {
  const raw =
    import.meta.env.VITE_AGENT_API_BASE_URL?.trim() ||
    import.meta.env.VITE_COOBIT_API_BASE_URL?.trim();
  return raw ? stripTrailingSlash(raw) : "";
}

/** @deprecated 使用 {@link getAgentApiBase} */
export function getCoobitApiBase(): string {
  return getAgentApiBase();
}

export async function postTradingApiBinding(payload: TradingApiBindPayload): Promise<TradingApiBindResult> {
  const base = getAgentApiBase();
  const url = `${base}/api/v1/me/agent/bindings/trading-api`;
  const res = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
  });

  const text = await res.text();
  let data: unknown = undefined;
  try {
    data = text ? JSON.parse(text) : undefined;
  } catch {
    data = undefined;
  }

  if (!res.ok) {
    const msg = messageFromTradingApiBindProblem(data, res.status);
    const prob = data as ApiErrorBody | undefined;
    const code = prob?.code as TradingApiBindRejectCode | undefined;
    throw new TradingApiBindError(msg, { status: res.status, code, raw: data });
  }

  return (data ?? {}) as TradingApiBindResult;
}
