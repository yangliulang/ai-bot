/**
 * Production Runtime · `agent.prompt.binding_resolved`（SC-PM-22 / SC-OBS04）
 * 对齐 OpenAPI `ResolvedPromptBinding` · observability §2.3
 */

import type { MockObsTimelineEventRow, MockResolvedPromptBinding } from "../data/types";
import {
  MOCK_RUNTIME_CLARIFY_PACK,
  MOCK_RUNTIME_OUTPUT_CONTRACT_PACK,
  MOCK_SAFETY_PROMPT_PACK,
  MOCK_SCENARIO_PROMPT_PACK,
  MOCK_SYSTEM_PROMPT_PACK,
  UNIFIED_ANALYSIS_PROMPT_PACK,
} from "../data/mockPromptData";
import { isAnalysisCapabilityScenario } from "../data/mockPromptDataCatalog";
import { ensureWritePathSkillSpecRead } from "./skillSpecTimeline";

export const PROMPT_BINDING_RESOLVED_EVENT = "agent.prompt.binding_resolved" as const;
export const PROMPT_BINDING_LOADED_TRIGGER = "prompt.binding_resolved" as const;

/** 拼装追溯 · 层名称（运营 UI 中文 SSOT） */
export const PROMPT_ASSEMBLY_LAYER = {
  base: "基础",
  ux: "体验",
  scenario: "场景",
  analysis: "分析",
  runtime: "运行时",
  output: "输出",
} as const;

export type PromptAssemblyLayerRow = {
  layer: string;
  source: string;
  promptPackId?: string;
  promptPackVersion?: number | null;
};

const SYSTEM_PACK = MOCK_SYSTEM_PROMPT_PACK;
const SAFETY_PACK = MOCK_SAFETY_PROMPT_PACK;

/** scenarioId → 场景策略槽（`trading*` 亦承载 ANALYSIS 族） */
const SCENARIO_STRATEGY_PACK = MOCK_SCENARIO_PROMPT_PACK;

function formatOutputLayerSource(binding: MockResolvedPromptBinding): string {
  const base = formatPackRef(
    MOCK_RUNTIME_OUTPUT_CONTRACT_PACK.promptPackId,
    MOCK_RUNTIME_OUTPUT_CONTRACT_PACK.promptPackVersion,
  );
  const extras = [
    binding.placeholderDenylistRevision
      ? `占位符闸 ${binding.placeholderDenylistRevision}`
      : null,
    binding.fewShotDigest ? `示例集摘要 ${binding.fewShotDigest}` : null,
  ]
    .filter(Boolean)
    .join(" · ");
  return extras ? `${base} · ${extras}` : base;
}

/** 读侧 / 监控场景或已绑定统一分析包 → 分析槽（非 `analysis.` 前缀） */
export function isAnalysisStrategyBinding(binding: MockResolvedPromptBinding): boolean {
  if (binding.tradingPromptPackId === UNIFIED_ANALYSIS_PROMPT_PACK.promptPackId) {
    return true;
  }
  return isAnalysisCapabilityScenario(binding.scenarioId);
}

export function buildDefaultResolvedPromptBinding(params: {
  scenarioId: string;
  sessionId?: string | null;
}): MockResolvedPromptBinding {
  const strategy = SCENARIO_STRATEGY_PACK[params.scenarioId];
  return {
    scenarioId: params.scenarioId,
    sessionId: params.sessionId ?? null,
    systemPromptPackId: SYSTEM_PACK.promptPackId,
    systemPromptPackVersion: SYSTEM_PACK.promptPackVersion,
    safetyPromptPackId: SAFETY_PACK.promptPackId,
    safetyPromptPackVersion: SAFETY_PACK.promptPackVersion,
    tradingPromptPackId: strategy?.promptPackId ?? null,
    tradingPromptPackVersion: strategy?.promptPackVersion ?? null,
    runtimeClarifyPromptPackId: MOCK_RUNTIME_CLARIFY_PACK.promptPackId,
    runtimeClarifyPromptPackVersion: MOCK_RUNTIME_CLARIFY_PACK.promptPackVersion,
    runtimeOutputContractPromptPackId: MOCK_RUNTIME_OUTPUT_CONTRACT_PACK.promptPackId,
    runtimeOutputContractPromptPackVersion: MOCK_RUNTIME_OUTPUT_CONTRACT_PACK.promptPackVersion,
    fewShotDigest: strategy ? "sha256:fewshot-demo-7c2a…" : null,
    placeholderDenylistRevision: "pdr-2026-05-07",
    safetyPhraseBlocklistRevision: "spb-2026-05-05",
  };
}

function formatPackRef(id: string | null | undefined, version: number | null | undefined): string {
  if (!id) return "—";
  return version != null ? `${id}@v${version}` : id;
}

/** `ResolvedPromptBinding` → 运营可读拼装层（SC-PM-22） */
export function bindingToAssemblyLayers(binding: MockResolvedPromptBinding): PromptAssemblyLayerRow[] {
  const rows: PromptAssemblyLayerRow[] = [
    {
      layer: PROMPT_ASSEMBLY_LAYER.base,
      source: formatPackRef(binding.systemPromptPackId, binding.systemPromptPackVersion),
      promptPackId: binding.systemPromptPackId ?? undefined,
      promptPackVersion: binding.systemPromptPackVersion,
    },
    {
      layer: PROMPT_ASSEMBLY_LAYER.ux,
      source: formatPackRef(binding.safetyPromptPackId, binding.safetyPromptPackVersion),
      promptPackId: binding.safetyPromptPackId ?? undefined,
      promptPackVersion: binding.safetyPromptPackVersion,
    },
  ];

  if (binding.tradingPromptPackId) {
    rows.push({
      layer: isAnalysisStrategyBinding(binding)
        ? PROMPT_ASSEMBLY_LAYER.analysis
        : PROMPT_ASSEMBLY_LAYER.scenario,
      source: formatPackRef(binding.tradingPromptPackId, binding.tradingPromptPackVersion),
      promptPackId: binding.tradingPromptPackId,
      promptPackVersion: binding.tradingPromptPackVersion,
    });
  }

  rows.push(
    {
      layer: PROMPT_ASSEMBLY_LAYER.runtime,
      source: formatPackRef(
        MOCK_RUNTIME_CLARIFY_PACK.promptPackId,
        MOCK_RUNTIME_CLARIFY_PACK.promptPackVersion,
      ),
      promptPackId: MOCK_RUNTIME_CLARIFY_PACK.promptPackId,
      promptPackVersion: MOCK_RUNTIME_CLARIFY_PACK.promptPackVersion,
    },
    {
      layer: PROMPT_ASSEMBLY_LAYER.output,
      source: formatOutputLayerSource(binding),
      promptPackId: MOCK_RUNTIME_OUTPUT_CONTRACT_PACK.promptPackId,
      promptPackVersion: MOCK_RUNTIME_OUTPUT_CONTRACT_PACK.promptPackVersion,
    },
  );

  return rows;
}

export function formatPromptBindingSummary(binding: MockResolvedPromptBinding): string {
  return [
    `scenarioId=${binding.scenarioId}`,
    `system=${formatPackRef(binding.systemPromptPackId, binding.systemPromptPackVersion)}`,
    `safety=${formatPackRef(binding.safetyPromptPackId, binding.safetyPromptPackVersion)}`,
    `strategy=${formatPackRef(binding.tradingPromptPackId, binding.tradingPromptPackVersion)}`,
    `clarify=${formatPackRef(binding.runtimeClarifyPromptPackId, binding.runtimeClarifyPromptPackVersion)}`,
    `outputContract=${formatPackRef(binding.runtimeOutputContractPromptPackId, binding.runtimeOutputContractPromptPackVersion)}`,
  ].join("; ");
}

export function buildPromptBindingTimelineRow(
  at: string,
  binding: MockResolvedPromptBinding,
): MockObsTimelineEventRow {
  return {
    at,
    eventName: PROMPT_BINDING_RESOLVED_EVENT,
    summary: formatPromptBindingSummary(binding),
    transitionTrigger: PROMPT_BINDING_LOADED_TRIGGER,
    promptBindingResolved: binding,
  };
}

/** 在 dispatched 之后、spec_read / 首次模型调用之前插入 binding_resolved */
export function ensurePromptBindingResolved(
  events: MockObsTimelineEventRow[],
  binding: MockResolvedPromptBinding,
): MockObsTimelineEventRow[] {
  if (events.some((e) => e.eventName === PROMPT_BINDING_RESOLVED_EVENT || e.promptBindingResolved)) {
    return events;
  }

  const dispatchedIdx = events.findIndex(
    (e) => e.transitionTrigger === "execution.dispatched" || e.eventName === "execution.dispatched",
  );
  const anchor = dispatchedIdx >= 0 ? events[dispatchedIdx]! : events[0];
  const at = isoAddMs(anchor?.at ?? new Date().toISOString(), 120);
  const row = buildPromptBindingTimelineRow(at, binding);
  const insertAt = dispatchedIdx >= 0 ? dispatchedIdx + 1 : 0;
  const out = [...events];
  out.splice(insertAt, 0, row);
  return out;
}

export function parseBindingFromTimeline(
  events: MockObsTimelineEventRow[] | undefined,
): MockResolvedPromptBinding | undefined {
  if (!events?.length) return undefined;
  for (const e of events) {
    if (e.promptBindingResolved) return e.promptBindingResolved;
    if (e.eventName !== PROMPT_BINDING_RESOLVED_EVENT || !e.summary) continue;
    const scenarioId = e.summary.match(/scenarioId=([^;]+)/)?.[1]?.trim();
    if (!scenarioId) continue;
    const pick = (label: string) => e.summary!.match(new RegExp(`${label}=([^;]+)`))?.[1]?.trim();
    const parseRef = (raw: string | undefined) => {
      if (!raw || raw === "—") return { id: null as string | null, version: null as number | null };
      const m = raw.match(/^(.+)@v(\d+)$/);
      if (m) return { id: m[1]!, version: Number(m[2]) };
      return { id: raw, version: null };
    };
    const system = parseRef(pick("system"));
    const safety = parseRef(pick("safety"));
    const strategy = parseRef(pick("strategy"));
    const clarify = parseRef(pick("clarify"));
    const outputContract = parseRef(pick("outputContract"));
    return {
      scenarioId,
      sessionId: null,
      systemPromptPackId: system.id ?? SYSTEM_PACK.promptPackId,
      systemPromptPackVersion: system.version ?? SYSTEM_PACK.promptPackVersion,
      safetyPromptPackId: safety.id ?? SAFETY_PACK.promptPackId,
      safetyPromptPackVersion: safety.version ?? SAFETY_PACK.promptPackVersion,
      tradingPromptPackId: strategy.id,
      tradingPromptPackVersion: strategy.version,
      runtimeClarifyPromptPackId: clarify.id ?? MOCK_RUNTIME_CLARIFY_PACK.promptPackId,
      runtimeClarifyPromptPackVersion: clarify.version ?? MOCK_RUNTIME_CLARIFY_PACK.promptPackVersion,
      runtimeOutputContractPromptPackId:
        outputContract.id ?? MOCK_RUNTIME_OUTPUT_CONTRACT_PACK.promptPackId,
      runtimeOutputContractPromptPackVersion:
        outputContract.version ?? MOCK_RUNTIME_OUTPUT_CONTRACT_PACK.promptPackVersion,
    };
  }
  return undefined;
}

export function resolvePromptBindingForExecution(params: {
  scenarioId: string;
  sessionId: string;
  resolvedPromptBinding?: MockResolvedPromptBinding;
  timelineEvents?: MockObsTimelineEventRow[];
}): MockResolvedPromptBinding {
  return (
    params.resolvedPromptBinding ??
    parseBindingFromTimeline(params.timelineEvents) ??
    buildDefaultResolvedPromptBinding({
      scenarioId: params.scenarioId,
      sessionId: params.sessionId,
    })
  );
}

/** 写路径演示时间线：binding_resolved → spec_read（均在 confirmation 之前） */
export function ensureWritePathObservabilityTimeline(
  events: MockObsTimelineEventRow[],
  scenarioId: string,
  sessionId: string,
): MockObsTimelineEventRow[] {
  const binding = buildDefaultResolvedPromptBinding({ scenarioId, sessionId });
  const withBinding = ensurePromptBindingResolved(events, binding);
  return ensureWritePathSkillSpecRead(withBinding, scenarioId);
}

function isoAddMs(iso: string, ms: number): string {
  const d = new Date(iso);
  d.setTime(d.getTime() + ms);
  return d.toISOString().replace(/\.\d{3}Z$/, "Z");
}
