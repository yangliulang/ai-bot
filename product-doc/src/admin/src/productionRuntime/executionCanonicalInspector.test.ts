import { describe, expect, it } from "vitest";
import { buildExecutionCanonicalInspect } from "./executionCanonicalInspector";

describe("buildExecutionCanonicalInspect", () => {
  it("read scenario not applicable", () => {
    const v = buildExecutionCanonicalInspect({
      executionId: "20260501000099",
      scenarioId: "market.read_quote",
    });
    expect(v.applicable).toBe(false);
  });

  it("20260501001001 write path passes barrier demo", () => {
    const v = buildExecutionCanonicalInspect({
      executionId: "20260501001001",
      scenarioId: "trade.spot.limit_order",
      outcome: "PER_EXECUTION_FINAL",
      timelineEvents: [
        { at: "t", eventName: "user.confirmed", transitionTrigger: "user.confirmed" },
      ],
    });
    expect(v.applicable).toBe(true);
    expect(v.canonicalOp).toBe("place_limit_order");
    expect(v.barrierOk).toBe(true);
  });

  it("20260501004001 shows barrier failure", () => {
    const v = buildExecutionCanonicalInspect({
      executionId: "20260501004001",
      scenarioId: "trade.futures.market_order",
      outcome: "FAILED",
    });
    expect(v.barrierOk).toBe(false);
  });
});
