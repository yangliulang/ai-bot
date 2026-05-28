import { describe, expect, it } from "vitest";
import { mockPromptPacks } from "../../data/mock";
import { runPromptPublishGate } from "./promptPublishGate";

describe("runPromptPublishGate", () => {
  it("TRADING 无 scenarioId → PROMPT_SCENARIO_INVALID", async () => {
    const pack = mockPromptPacks.find((p) => p.promptPackId === "pp-trading-spot-limit")!;
    const trace = await runPromptPublishGate({ ...pack, scenarioId: undefined }, "", "body");
    expect(trace.ok).toBe(false);
    expect(trace.rejections.some((r) => r.code === "PROMPT_SCENARIO_INVALID")).toBe(true);
  });

  it("错误 skill 版本 → PROMPT_SKILL_REF_INVALID", async () => {
    const pack = mockPromptPacks.find((p) => p.promptPackId === "pp-trading-futures-market")!;
    const trace = await runPromptPublishGate(
      { ...pack, skillSpecRef: "skill.futures.market_order@9.9.9-invalid" },
      pack.scenarioId ?? "",
      "ok",
    );
    expect(trace.ok).toBe(false);
    expect(trace.rejections.some((r) => r.code === "PROMPT_SKILL_REF_INVALID")).toBe(true);
  });

  it("有效 spot limit → ok", async () => {
    const pack = mockPromptPacks.find((p) => p.promptPackId === "pp-trading-spot-limit")!;
    const trace = await runPromptPublishGate(pack, "trade.spot.limit_order", "rules only");
    expect(trace.ok).toBe(true);
    expect(trace.rejections).toHaveLength(0);
  });
});
