import { describe, expect, it } from "vitest";
import { mockObsExecutions } from "../data/mock";
import { assertWritePathPipelineOrder } from "./writePathPipelineOrder";

import { DEMO_EXEC_AA11, DEMO_EXEC_FAIL01 } from "../data/demoExecutionIds";

const WRITE_PATH_EXEC_IDS = [DEMO_EXEC_AA11, DEMO_EXEC_FAIL01] as const;

describe("eval.runtime.pipeline_write_order（写路径 Demo 时间线）", () => {
  for (const id of WRITE_PATH_EXEC_IDS) {
    it(`${id} 满足五段序`, () => {
      const row = mockObsExecutions.find((e) => e.executionId === id);
      expect(row, id).toBeDefined();
      expect(() => assertWritePathPipelineOrder(row!.timelineEvents ?? [])).not.toThrow();
    });
  }
});
