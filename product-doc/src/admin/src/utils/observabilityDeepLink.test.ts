import { describe, expect, it } from "vitest";
import {
  buildObservabilitySearch,
  buildObservabilitySearchFromCorrelateHint,
  readObservabilityTraceQuery,
} from "./observabilityDeepLink";

describe("readObservabilityTraceQuery", () => {
  it("prefers traceId over traceKey", () => {
    const sp = new URLSearchParams("traceId=a&traceKey=b");
    expect(readObservabilityTraceQuery(sp)).toBe("a");
  });

  it("reads traceKey when traceId absent", () => {
    const sp = new URLSearchParams("traceKey=z9");
    expect(readObservabilityTraceQuery(sp)).toBe("z9");
  });

  it("trims and returns empty when missing", () => {
    expect(readObservabilityTraceQuery(new URLSearchParams())).toBe("");
    expect(readObservabilityTraceQuery(new URLSearchParams("traceId=  x  "))).toBe("x");
  });
});

describe("buildObservabilitySearch", () => {
  it("maps traceKey to traceId query key (D-5 alias)", () => {
    expect(buildObservabilitySearch({ traceKey: "bt-1" })).toBe("?traceId=bt-1");
  });

  it("traceId wins when both provided", () => {
    expect(buildObservabilitySearch({ traceId: "first", traceKey: "second" })).toBe("?traceId=first");
  });

  it("includes tab and other filters", () => {
    const q = buildObservabilitySearch({
      executionId: "20260501000001",
      userId: "u-2",
      traceId: "t3",
      tab: "billing",
    });
    expect(q).toContain("executionId=20260501000001");
    expect(q).toContain("userId=u-2");
    expect(q).toContain("traceId=t3");
    expect(q).toContain("tab=billing");
  });

  it("returns empty string when no params", () => {
    expect(buildObservabilitySearch({})).toBe("");
  });
});

describe("buildObservabilitySearchFromCorrelateHint", () => {
  it("empty hint yields billing tab only", () => {
    expect(buildObservabilitySearchFromCorrelateHint("")).toBe("?tab=billing");
  });

  it("纯数字 maps to executionId", () => {
    expect(buildObservabilitySearchFromCorrelateHint("20260501001001")).toBe(
      "?executionId=20260501001001&tab=billing",
    );
  });

  it("u- prefix maps to userId", () => {
    expect(buildObservabilitySearchFromCorrelateHint("u-me")).toBe("?userId=u-me&tab=billing");
  });

  it("otherwise passes value as traceId", () => {
    expect(buildObservabilitySearchFromCorrelateHint("bt-xyz")).toBe("?traceId=bt-xyz&tab=billing");
  });
});
