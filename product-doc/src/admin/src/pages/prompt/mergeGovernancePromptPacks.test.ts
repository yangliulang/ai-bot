import { describe, expect, it } from "vitest";
import type { MockPromptPack } from "../../data/types";
import { GOVERNANCE_PROMPT_PACK_COUNT } from "../../data/governancePromptPackIds";
import { mockPromptPacks } from "../../data/mock";
import { mergeRemotePacksWithGovernanceMock } from "./mergeGovernancePromptPacks";

describe("mergeRemotePacksWithGovernanceMock", () => {
  it("returns all 16 governance packs when remote is empty", () => {
    const { rows, supplementedFromMock } = mergeRemotePacksWithGovernanceMock([], mockPromptPacks);
    expect(rows).toHaveLength(GOVERNANCE_PROMPT_PACK_COUNT);
    expect(supplementedFromMock).toHaveLength(GOVERNANCE_PROMPT_PACK_COUNT);
    expect(rows.map((p) => p.promptPackId).sort()).toEqual(
      mockPromptPacks.map((p) => p.promptPackId).sort(),
    );
  });

  it("overlays remote title while keeping mock-only fields", () => {
    const remote: MockPromptPack[] = [
      {
        ...mockPromptPacks[0]!,
        title: "远端覆盖标题",
        effectiveBodyPreview: "",
      },
    ];
    const { rows, supplementedFromMock } = mergeRemotePacksWithGovernanceMock(remote, mockPromptPacks);
    const core = rows.find((p) => p.promptPackId === "pp-system-core");
    expect(core?.title).toBe("远端覆盖标题");
    expect(core?.effectiveBodyPreview).toBe(mockPromptPacks[0]!.effectiveBodyPreview);
    expect(supplementedFromMock).not.toContain("pp-system-core");
    expect(supplementedFromMock.length).toBe(GOVERNANCE_PROMPT_PACK_COUNT - 1);
  });
});
