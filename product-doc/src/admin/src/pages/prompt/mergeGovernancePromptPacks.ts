/**
 * 远端 Prompt 列表与 Demo 治理 SSOT（16 包）合并。
 * BFF 未齐套时仍以 mock 补齐缺失 `promptPackId`，避免运营页缺包。
 */

import type { MockPromptPack } from "../../data/types";
import { GOVERNANCE_PROMPT_PACK_IDS } from "../../data/governancePromptPackIds";

const GOVERNANCE_ID_SET = new Set<string>(GOVERNANCE_PROMPT_PACK_IDS);

export type MergeGovernancePromptPacksResult = {
  rows: MockPromptPack[];
  /** 远端未返回、由 mock 补齐的包 id */
  supplementedFromMock: string[];
};

/** 远端字段覆盖 mock；缺失 id 保留 mock 行 */
export function mergePackRow(mockBase: MockPromptPack, remote: MockPromptPack): MockPromptPack {
  return {
    ...mockBase,
    ...remote,
    promptPackId: mockBase.promptPackId,
    kind: remote.kind ?? mockBase.kind,
    title: remote.title?.trim() ? remote.title : mockBase.title,
    description: remote.description?.trim() ? remote.description : mockBase.description,
    scenarioId: remote.scenarioId ?? mockBase.scenarioId,
    skillSpecRef: remote.skillSpecRef ?? mockBase.skillSpecRef,
    effectiveBodyPreview: remote.effectiveBodyPreview?.trim()
      ? remote.effectiveBodyPreview
      : mockBase.effectiveBodyPreview,
  };
}

export function mergeRemotePacksWithGovernanceMock(
  remoteRows: MockPromptPack[],
  mockRows: MockPromptPack[],
): MergeGovernancePromptPacksResult {
  const mockById = new Map(mockRows.map((p) => [p.promptPackId, p]));
  const remoteById = new Map(remoteRows.map((p) => [p.promptPackId, p]));
  const supplementedFromMock: string[] = [];
  const merged: MockPromptPack[] = [];

  for (const id of GOVERNANCE_PROMPT_PACK_IDS) {
    const mock = mockById.get(id);
    const remote = remoteById.get(id);
    if (mock && remote) {
      merged.push(mergePackRow(mock, remote));
    } else if (mock) {
      merged.push(mock);
      supplementedFromMock.push(id);
    } else if (remote) {
      merged.push(remote);
    }
  }

  for (const remote of remoteRows) {
    if (!GOVERNANCE_ID_SET.has(remote.promptPackId)) {
      merged.push(remote);
    }
  }

  return { rows: merged, supplementedFromMock };
}
