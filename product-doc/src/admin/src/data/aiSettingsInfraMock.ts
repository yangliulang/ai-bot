/**
 * AI Settings · 厂商与其下模型一体化 Demo 台账（对齐 FR-MC401～402）。
 * 模型归属于厂商（嵌套）；不落真实密钥；`secretRef` 仅为引用示意。
 */

export type LlmHealthStatus = "healthy" | "degraded" | "unknown";

export type MockLlmProvider = {
  providerId: string;
  displayName: string;
  baseUrl: string;
  /** KMS / Secret 资源名示意，禁止回填明文 Key */
  secretRef: string;
  enabled: boolean;
  healthStatus: LlmHealthStatus;
  lastProbedAt: string | null;
};

/** 挂在某厂商下的模型（目录项），不含 providerId — 由父级承载 */
export type MockLlmModelEntry = {
  modelId: string;
  displayLabel: string;
  contextWindow: number;
  capabilities: ("chat" | "tools" | "vision")[];
  enabled: boolean;
  deprecated: boolean;
};

/** 接入底座类型：决定可选模型目录（预置清单），与厂商展示名独立 */
export type LlmVendorCatalogKind = "openai" | "anthropic" | "deepseek" | "none";

export const LLM_VENDOR_CATALOG_LABELS: Record<LlmVendorCatalogKind, string> = {
  openai: "OpenAI",
  anthropic: "Anthropic（Claude）",
  deepseek: "DeepSeek",
  none: "暂无预置模型目录",
};

/** 新建厂商时按接入类型填充默认 Base URL（可改） */
export const DEFAULT_BASE_URL_BY_CATALOG: Record<Exclude<LlmVendorCatalogKind, "none">, string> = {
  openai: "https://api.openai.com/v1",
  anthropic: "https://api.anthropic.com",
  deepseek: "https://api.deepseek.com/v1",
};

export type MockLlmProviderWithModels = MockLlmProvider & {
  /** 实际接入底座，用于「添加模型」时仅允许从对应预置列表选择 */
  catalogKind: LlmVendorCatalogKind;
  models: MockLlmModelEntry[];
};

/** 扁平化（观测/下拉等）；仅运行时派生 */
export type MockLlmModelFlat = MockLlmModelEntry & { providerId: string };

export const MOCK_LLM_GATEWAY_INITIAL: MockLlmProviderWithModels[] = [
  {
    providerId: "openai",
    displayName: "OpenAI",
    catalogKind: "openai",
    baseUrl: "https://api.openai.com/v1",
    secretRef: "kms://coobit/prod/llm/openai-primary",
    enabled: true,
    healthStatus: "healthy",
    lastProbedAt: "2026-05-13T06:00:00.000Z",
    models: [
      {
        modelId: "gpt-4.1",
        displayLabel: "GPT-4.1",
        contextWindow: 1_047_576,
        capabilities: ["chat", "tools"],
        enabled: true,
        deprecated: false,
      },
      {
        modelId: "gpt-4.1-mini",
        displayLabel: "GPT-4.1 Mini",
        contextWindow: 1_047_576,
        capabilities: ["chat", "tools"],
        enabled: true,
        deprecated: false,
      },
      {
        modelId: "gpt-4o-legacy",
        displayLabel: "GPT-4o（Legacy）",
        contextWindow: 128_000,
        capabilities: ["chat", "tools"],
        enabled: false,
        deprecated: true,
      },
    ],
  },
  {
    providerId: "anthropic",
    displayName: "Anthropic（Claude）",
    catalogKind: "anthropic",
    baseUrl: "https://api.anthropic.com",
    secretRef: "kms://coobit/prod/llm/anthropic-primary",
    enabled: true,
    healthStatus: "healthy",
    lastProbedAt: "2026-05-13T05:30:00.000Z",
    models: [
      {
        modelId: "claude-3-5-sonnet-20241022",
        displayLabel: "Claude 3.5 Sonnet",
        contextWindow: 200_000,
        capabilities: ["chat", "tools", "vision"],
        enabled: true,
        deprecated: false,
      },
      {
        modelId: "claude-3-haiku-20240307",
        displayLabel: "Claude 3 Haiku",
        contextWindow: 200_000,
        capabilities: ["chat", "tools"],
        enabled: true,
        deprecated: false,
      },
    ],
  },
  {
    providerId: "deepseek",
    displayName: "DeepSeek",
    catalogKind: "deepseek",
    baseUrl: "https://api.deepseek.com/v1",
    secretRef: "kms://coobit/prod/llm/deepseek-primary",
    enabled: true,
    healthStatus: "degraded",
    lastProbedAt: "2026-05-12T18:20:00.000Z",
    models: [
      {
        modelId: "deepseek-chat",
        displayLabel: "DeepSeek Chat",
        contextWindow: 128_000,
        capabilities: ["chat", "tools"],
        enabled: true,
        deprecated: false,
      },
      {
        modelId: "deepseek-reasoner",
        displayLabel: "DeepSeek Reasoner",
        contextWindow: 128_000,
        capabilities: ["chat", "tools"],
        enabled: true,
        deprecated: false,
      },
    ],
  },
];

export function flattenProviderModels(providers: MockLlmProviderWithModels[]): MockLlmModelFlat[] {
  const out: MockLlmModelFlat[] = [];
  for (const p of providers) {
    for (const m of p.models) {
      out.push({ ...m, providerId: p.providerId });
    }
  }
  return out;
}

/** 各接入底座可选模型清单（添加模型时仅允许从此处选择；禁手输 modelId） */
export const LLM_MODEL_PRESETS: Record<Exclude<LlmVendorCatalogKind, "none">, MockLlmModelEntry[]> = {
  openai: [
    {
      modelId: "gpt-4.1",
      displayLabel: "GPT-4.1",
      contextWindow: 1_047_576,
      capabilities: ["chat", "tools"],
      enabled: true,
      deprecated: false,
    },
    {
      modelId: "gpt-4.1-mini",
      displayLabel: "GPT-4.1 Mini",
      contextWindow: 1_047_576,
      capabilities: ["chat", "tools"],
      enabled: true,
      deprecated: false,
    },
    {
      modelId: "gpt-4o",
      displayLabel: "GPT-4o",
      contextWindow: 128_000,
      capabilities: ["chat", "tools", "vision"],
      enabled: true,
      deprecated: false,
    },
    {
      modelId: "gpt-4o-legacy",
      displayLabel: "GPT-4o（Legacy）",
      contextWindow: 128_000,
      capabilities: ["chat", "tools"],
      enabled: false,
      deprecated: true,
    },
    {
      modelId: "o4-mini",
      displayLabel: "o4-mini",
      contextWindow: 200_000,
      capabilities: ["chat", "tools"],
      enabled: true,
      deprecated: false,
    },
  ],
  anthropic: [
    {
      modelId: "claude-3-5-sonnet-20241022",
      displayLabel: "Claude 3.5 Sonnet",
      contextWindow: 200_000,
      capabilities: ["chat", "tools", "vision"],
      enabled: true,
      deprecated: false,
    },
    {
      modelId: "claude-3-haiku-20240307",
      displayLabel: "Claude 3 Haiku",
      contextWindow: 200_000,
      capabilities: ["chat", "tools"],
      enabled: true,
      deprecated: false,
    },
    {
      modelId: "claude-3-opus-20240229",
      displayLabel: "Claude 3 Opus",
      contextWindow: 200_000,
      capabilities: ["chat", "tools", "vision"],
      enabled: true,
      deprecated: false,
    },
  ],
  deepseek: [
    {
      modelId: "deepseek-chat",
      displayLabel: "DeepSeek Chat",
      contextWindow: 128_000,
      capabilities: ["chat", "tools"],
      enabled: true,
      deprecated: false,
    },
    {
      modelId: "deepseek-reasoner",
      displayLabel: "DeepSeek Reasoner",
      contextWindow: 128_000,
      capabilities: ["chat", "tools"],
      enabled: true,
      deprecated: false,
    },
    {
      modelId: "deepseek-v3",
      displayLabel: "DeepSeek V3",
      contextWindow: 128_000,
      capabilities: ["chat", "tools"],
      enabled: true,
      deprecated: false,
    },
  ],
};

/** 添加模型下拉：排除已接入（全局 modelId 唯一）与弃用预置项 */
export function getAddablePresetModelsForProvider(
  parent: MockLlmProviderWithModels,
  allProviders: MockLlmProviderWithModels[],
): MockLlmModelEntry[] {
  if (parent.catalogKind === "none") return [];
  const takenIds = new Set(flattenProviderModels(allProviders).map((m) => m.modelId));
  return LLM_MODEL_PRESETS[parent.catalogKind].filter((p) => !p.deprecated && !takenIds.has(p.modelId));
}

/** 使用策略 / Runtime 下拉：仅启用厂商下、启用且未弃用的目录模型 */
export function buildRuntimeModelSelectOptions(
  providers: MockLlmProviderWithModels[],
): { value: string; label: string }[] {
  const out: { value: string; label: string }[] = [];
  for (const p of providers) {
    if (!p.enabled) continue;
    for (const m of p.models) {
      if (!m.enabled || m.deprecated) continue;
      out.push({
        value: m.modelId,
        label: `${m.displayLabel}（${p.displayName}）`,
      });
    }
  }
  return out;
}

export function healthStatusTag(h: LlmHealthStatus): { color: string; label: string } {
  if (h === "healthy") return { color: "success", label: "健康" };
  if (h === "degraded") return { color: "warning", label: "降级 / 待确认" };
  return { color: "default", label: "未探测" };
}

export function capabilityLabel(c: MockLlmModelEntry["capabilities"][number]): string {
  const map = { chat: "对话", tools: "工具调用", vision: "视觉" } as const;
  return map[c];
}
