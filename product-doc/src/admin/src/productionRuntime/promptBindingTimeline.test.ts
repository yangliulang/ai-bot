import { describe, expect, it } from "vitest";
import {
  PROMPT_BINDING_RESOLVED_EVENT,
  bindingToAssemblyLayers,
  buildDefaultResolvedPromptBinding,
  PROMPT_ASSEMBLY_LAYER,
  ensureWritePathObservabilityTimeline,
  isAnalysisStrategyBinding,
  parseBindingFromTimeline,
  resolvePromptBindingForExecution,
} from "./promptBindingTimeline";

describe("promptBindingTimeline", () => {
  it("builds default binding for spot limit_order", () => {
    const b = buildDefaultResolvedPromptBinding({
      scenarioId: "trade.spot.limit_order",
      sessionId: "sess-1",
    });
    expect(b.tradingPromptPackId).toBe("pp-trading-spot-limit");
    expect(b.systemPromptPackId).toBe("pp-system-core");
    expect(b.runtimeClarifyPromptPackId).toBe("pp-runtime-clarify");
    expect(b.runtimeOutputContractPromptPackId).toBe("pp-runtime-output-contract");
  });

  it("maps binding to assembly layers", () => {
    const layers = bindingToAssemblyLayers(
      buildDefaultResolvedPromptBinding({ scenarioId: "trade.spot.flash_convert" }),
    );
    expect(
      layers.some((l) => l.layer === PROMPT_ASSEMBLY_LAYER.scenario && l.source.includes("pp-trading-spot-flash")),
    ).toBe(true);
    expect(
      layers.some(
        (l) =>
          l.layer === PROMPT_ASSEMBLY_LAYER.runtime && l.source.includes("pp-runtime-clarify"),
      ),
    ).toBe(true);
    expect(
      layers.some(
        (l) =>
          l.layer === PROMPT_ASSEMBLY_LAYER.output && l.source.includes("pp-runtime-output-contract"),
      ),
    ).toBe(true);
  });

  it("labels market.read_quote as analysis layer with pp-analysis-core", () => {
    const binding = buildDefaultResolvedPromptBinding({ scenarioId: "market.read_quote" });
    expect(binding.tradingPromptPackId).toBe("pp-analysis-core");
    expect(isAnalysisStrategyBinding(binding)).toBe(true);
    const layers = bindingToAssemblyLayers(binding);
    expect(layers.some((l) => l.layer === PROMPT_ASSEMBLY_LAYER.analysis)).toBe(true);
    expect(layers.some((l) => l.layer === PROMPT_ASSEMBLY_LAYER.scenario)).toBe(false);
  });

  it("inserts binding before confirmation on write path timeline", () => {
    const events = ensureWritePathObservabilityTimeline(
      [
        {
          at: "2026-05-07T01:00:00.000Z",
          eventName: "execution.dispatched",
          transitionTrigger: "execution.dispatched",
        },
        {
          at: "2026-05-07T01:00:02.000Z",
          eventName: "confirmation.required",
          transitionTrigger: "confirmation.required",
        },
      ],
      "trade.spot.limit_order",
      "sess-x",
    );
    const bindingIdx = events.findIndex((e) => e.eventName === PROMPT_BINDING_RESOLVED_EVENT);
    const confirmIdx = events.findIndex((e) => e.eventName === "confirmation.required");
    expect(bindingIdx).toBeGreaterThanOrEqual(0);
    expect(bindingIdx).toBeLessThan(confirmIdx);
    expect(events[bindingIdx]?.promptBindingResolved?.tradingPromptPackId).toBe("pp-trading-spot-limit");
  });

  it("parses binding from timeline summary", () => {
    const binding = buildDefaultResolvedPromptBinding({ scenarioId: "trade.spot.limit_order" });
    const parsed = parseBindingFromTimeline([
      {
        at: "2026-05-07T01:00:00.000Z",
        eventName: PROMPT_BINDING_RESOLVED_EVENT,
        summary: `scenarioId=trade.spot.limit_order; system=pp-system-core@v1; safety=pp-safety-global@v1; strategy=pp-trading-spot-limit@v1`,
        promptBindingResolved: binding,
      },
    ]);
    expect(parsed?.tradingPromptPackVersion).toBe(1);
  });

  it("resolve prefers execution field over infer", () => {
    const explicit = buildDefaultResolvedPromptBinding({ scenarioId: "trade.spot.limit_order" });
    explicit.tradingPromptPackVersion = 99;
    const resolved = resolvePromptBindingForExecution({
      scenarioId: "trade.spot.limit_order",
      sessionId: "s",
      resolvedPromptBinding: explicit,
    });
    expect(resolved.tradingPromptPackVersion).toBe(99);
  });
});
