/**
 * 轻量 fetch 封装（与 `specs/openapi/admin/prompt-management.yaml` 路径一致）。
 * 认证头由网关 / 后续中间件注入；此处仅占位。
 */

export class ApiError extends Error {
  constructor(
    public status: number,
    public problem?: { title?: string; detail?: string; type?: string },
  ) {
    super(problem?.detail ?? problem?.title ?? `HTTP ${status}`);
    this.name = "ApiError";
  }
}

export function getApiBaseUrl(): string {
  const u = import.meta.env.VITE_API_BASE_URL;
  return typeof u === "string" ? u.replace(/\/$/, "") : "";
}

/** 为 true 且配置了 base URL 时走远程 Prompt API */
export function isPromptApiEnabled(): boolean {
  return import.meta.env.VITE_USE_PROMPT_API === "true" && !!getApiBaseUrl();
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const base = getApiBaseUrl();
  if (!base) {
    throw new Error("VITE_API_BASE_URL 未配置");
  }
  const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;
  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string>),
  };
  if (init?.body != null && !headers["Content-Type"] && !headers["content-type"]) {
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(url, { ...init, headers });
  const text = await res.text();
  if (!res.ok) {
    let problem: { title?: string; detail?: string; type?: string } | undefined;
    try {
      problem = text ? (JSON.parse(text) as { title?: string; detail?: string; type?: string }) : undefined;
    } catch {
      problem = { detail: text || res.statusText };
    }
    throw new ApiError(res.status, problem);
  }
  if (res.status === 204 || !text) {
    return undefined as T;
  }
  return JSON.parse(text) as T;
}
