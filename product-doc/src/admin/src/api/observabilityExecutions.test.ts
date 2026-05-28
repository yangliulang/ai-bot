import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { apiFetch } from "./http";
import { DEMO_EXEC_AA11 } from "../data/demoExecutionIds";
import {
  buildMinimalExecFromApiTimeline,
  correlationQueryToListApiParams,
  fetchObservabilityExecutionTimeline,
  mapExecutionSummaryToMockRow,
  mapObservabilityTimelineEventToRow,
} from "./observabilityExecutions";

vi.mock("./http", () => ({
  apiFetch: vi.fn(),
  getApiBaseUrl: vi.fn(() => "http://test"),
}));

describe("correlationQueryToListApiParams", () => {
  it("u- 前缀 → userId", () => {
    expect(correlationQueryToListApiParams("u-10482")).toEqual({ userId: "u-10482" });
  });
  it("纯数字 → executionId", () => {
    expect(correlationQueryToListApiParams(DEMO_EXEC_AA11)).toEqual({ executionId: DEMO_EXEC_AA11 });
  });
  it("点分 scenarioId → scenarioId", () => {
    expect(correlationQueryToListApiParams("trade.spot.limit_order")).toEqual({
      scenarioId: "trade.spot.limit_order",
    });
  });
  it("非数字短串 → 空", () => {
    expect(correlationQueryToListApiParams("aa11")).toEqual({});
  });
});

describe("mapExecutionSummaryToMockRow", () => {
  it("将 ObservabilityExecutionSummary 映射为列表行（补全 stageTimeline 等）", () => {
    const row = mapExecutionSummaryToMockRow({
      executionId: "20260501009999",
      createdAt: "2026-05-07T00:00:00Z",
      status: "RUNNING",
      currentStage: "RUNNING",
    });
    expect(row.executionId).toBe("20260501009999");
    expect(row.stageTimeline).toEqual(["RUNNING"]);
    expect(row.retries).toBe(0);
    expect(row.durationMs).toBe(0);
  });
});

describe("mapObservabilityTimelineEventToRow", () => {
  it("ts → at，summary 对象序列化，保留 transitionTrigger", () => {
    const row = mapObservabilityTimelineEventToRow({
      ts: "2026-05-07T01:00:00Z",
      eventName: "STAGE",
      summary: { foo: 1 },
      transitionTrigger: "MC801.A",
    });
    expect(row.at).toBe("2026-05-07T01:00:00Z");
    expect(row.eventName).toBe("STAGE");
    expect(row.summary).toBe('{"foo":1}');
    expect(row.transitionTrigger).toBe("MC801.A");
  });
});

describe("buildMinimalExecFromApiTimeline", () => {
  it("用首条时间填充 createdAt / timelineEvents", () => {
    const exec = buildMinimalExecFromApiTimeline("20260501008888", [
      { at: "2026-05-07T02:00:00Z", eventName: "X", transitionTrigger: "T" },
    ]);
    expect(exec.executionId).toBe("20260501008888");
    expect(exec.createdAt).toBe("2026-05-07T02:00:00Z");
    expect(exec.timelineEvents).toHaveLength(1);
  });
});

describe("fetchObservabilityExecutionTimeline", () => {
  beforeEach(() => {
    vi.mocked(apiFetch).mockReset();
  });
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("解析 items 数组为时间线行", async () => {
    vi.mocked(apiFetch).mockResolvedValue({
      items: [{ ts: "2026-05-07T03:00:00Z", eventName: "E", transitionTrigger: "TR" }],
    });

    const rows = await fetchObservabilityExecutionTimeline("20260501007777");

    expect(apiFetch).toHaveBeenCalledWith(
      "/api/v1/admin/observability/executions/20260501007777/timeline",
    );
    expect(rows).toEqual([
      { at: "2026-05-07T03:00:00Z", eventName: "E", summary: undefined, transitionTrigger: "TR" },
    ]);
  });
});
