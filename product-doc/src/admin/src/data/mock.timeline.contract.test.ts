import { describe, expect, it } from "vitest";
import { assertWritePathPipelineOrder } from "../productionRuntime/writePathPipelineOrder";
import {
  DEMO_EXEC_AA11,
  DEMO_EXEC_BB22,
  DEMO_EXEC_DEMO_050,
  DEMO_EXEC_FAIL01,
  DEMO_EXEC_RUN01,
  DEMO_EXEC_UN99,
} from "./demoExecutionIds";
import { mockObsExecutions } from "./mock";

/**
 * 对应 specs/requirements/evals/scenarios.md · `eval.obs.timeline_transition_contract` /
 * SC-OBS08 之 **演示数据下限**：核心样例行须暴露 transitionTrigger，避免 UI 与契约漂移。
 */

describe("eval.obs.timeline_transition_contract（Mock 下限）", () => {
  it("核心写路径行须含 agent.prompt.binding_resolved 且早于 agent.skill.spec_read", async () => {
    const { mockObsExecutions } = await import("./mock");
    const row = mockObsExecutions.find((e) => e.executionId === DEMO_EXEC_AA11);
    const events = row?.timelineEvents ?? [];
    const bindIdx = events.findIndex((e) => e.eventName === "agent.prompt.binding_resolved");
    const specIdx = events.findIndex((e) => e.eventName === "agent.skill.spec_read");
    expect(bindIdx).toBeGreaterThanOrEqual(0);
    expect(specIdx).toBeGreaterThan(bindIdx);
  });

  it("核心写路径行写路径须含 agent.skill.spec_read 且早于 confirmation.required", async () => {
    const { mockObsExecutions } = await import("./mock");
    const row = mockObsExecutions.find((e) => e.executionId === DEMO_EXEC_AA11);
    const events = row?.timelineEvents ?? [];
    const specIdx = events.findIndex((e) => e.eventName === "agent.skill.spec_read");
    const confirmIdx = events.findIndex((e) => e.transitionTrigger === "confirmation.required");
    expect(specIdx).toBeGreaterThanOrEqual(0);
    expect(specIdx).toBeLessThan(confirmIdx);
  });

  it("核心写路径行满足 eval.runtime.pipeline_write_order 五段序（Mock）", () => {
    const row = mockObsExecutions.find((e) => e.executionId === DEMO_EXEC_AA11);
    assertWritePathPipelineOrder(row?.timelineEvents ?? []);
  });

  it("进行中写路径须含 binding 与 spec_read", () => {
    const row = mockObsExecutions.find((e) => e.executionId === DEMO_EXEC_RUN01);
    const events = row?.timelineEvents ?? [];
    expect(events.length).toBeGreaterThan(3);
    expect(events.some((e) => e.eventName === "agent.prompt.binding_resolved")).toBe(true);
    expect(events.some((e) => e.eventName === "agent.skill.spec_read")).toBe(true);
    assertWritePathPipelineOrder(events);
  });

  it("计费阻断须含完整写路径前缀与 settlement.failed", () => {
    const row = mockObsExecutions.find((e) => e.executionId === DEMO_EXEC_BB22);
    const events = row?.timelineEvents ?? [];
    expect(events.some((e) => e.transitionTrigger === "settlement.failed")).toBe(true);
    expect(events.some((e) => e.eventName === "agent.skill.spec_read")).toBe(true);
  });

  it("批量演示行须有 timelineEvents", () => {
    const row = mockObsExecutions.find((e) => e.executionId === DEMO_EXEC_DEMO_050);
    expect(row?.timelineEvents?.length).toBeGreaterThan(0);
  });

  it("核心演示 execution 须有 timelineEvents 且各行含 transitionTrigger", () => {
    const ids = [DEMO_EXEC_AA11, DEMO_EXEC_UN99, DEMO_EXEC_FAIL01, DEMO_EXEC_BB22, DEMO_EXEC_RUN01] as const;
    for (const id of ids) {
      const row = mockObsExecutions.find((e) => e.executionId === id);
      expect(row, id).toBeDefined();
      expect(row!.timelineEvents?.length, id).toBeGreaterThan(0);
      for (const ev of row!.timelineEvents!) {
        expect(ev.transitionTrigger?.trim(), `${id} ${ev.at}`).toBeTruthy();
      }
    }
  });
});
