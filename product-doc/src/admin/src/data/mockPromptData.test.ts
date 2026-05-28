import { describe, expect, it } from "vitest";
import { SCENARIO_PRIMARY_SKILL } from "../skillPublish/scenarioSkillMap";
import {
  ANALYSIS_CAPABILITY_REGISTRY,
  UNIFIED_ANALYSIS_PROMPT_PACK_ID,
} from "./mockPromptDataCatalog";
import {
  MOCK_SCENARIO_PROMPT_PACK,
  UNIFIED_ANALYSIS_PROMPT_PACK,
  mockPromptPacks,
  getPromptPackDraft,
} from "./mockPromptData";

describe("mockPromptData", () => {
  it("Prompt 总量收敛：SYSTEM/SAFETY 各 1 · ANALYSIS 仅统一包 · TRADING 按写场景", () => {
    const kinds = mockPromptPacks.map((p) => p.kind);
    expect(kinds.filter((k) => k === "SYSTEM")).toHaveLength(3);
    expect(kinds.filter((k) => k === "SAFETY")).toHaveLength(1);
    expect(kinds.filter((k) => k === "ANALYSIS")).toHaveLength(1);
    expect(kinds.filter((k) => k === "TRADING")).toHaveLength(11);
    expect(mockPromptPacks).toHaveLength(16);
    expect(mockPromptPacks.find((p) => p.kind === "ANALYSIS")?.promptPackId).toBe(
      UNIFIED_ANALYSIS_PROMPT_PACK_ID,
    );
  });

  it("TRADING 包 scenarioId 与映射一致", () => {
    for (const p of mockPromptPacks) {
      if (p.kind !== "TRADING") continue;
      expect(p.scenarioId?.trim()).toBeTruthy();
      expect(MOCK_SCENARIO_PROMPT_PACK[p.scenarioId!]?.promptPackId).toBe(p.promptPackId);
    }
  });

  it("读侧 capability 均映射统一分析包（非每能力一包）", () => {
    for (const cap of ANALYSIS_CAPABILITY_REGISTRY) {
      expect(MOCK_SCENARIO_PROMPT_PACK[cap.scenarioId]).toEqual(UNIFIED_ANALYSIS_PROMPT_PACK);
    }
  });

  it("写路径 scenario 各有 TRADING 策略包", () => {
    for (const sid of Object.keys(SCENARIO_PRIMARY_SKILL)) {
      const binding = MOCK_SCENARIO_PROMPT_PACK[sid];
      expect(binding?.promptPackId).toMatch(/^pp-trading-/);
    }
    expect(MOCK_SCENARIO_PROMPT_PACK["futures.condition.order_create"]?.promptPackId).toBe(
      "pp-trading-futures-tpsl",
    );
  });

  it("每包均有运营向 Markdown 正文", () => {
    for (const p of mockPromptPacks) {
      const draft = getPromptPackDraft(p.promptPackId);
      expect(draft?.bodyMarkdown.length, `${p.promptPackId} 正文过短`).toBeGreaterThan(65);
      expect(draft?.bodyMarkdown).toMatch(/## Identity/);
      expect(draft?.bodyMarkdown).not.toMatch(
        /发布门禁|Runtime 技能范围|call_exchange_write|Analysis Capability Registry|场景键：`|Execution Gateway|登记册技能/,
      );
    }
  });
});
