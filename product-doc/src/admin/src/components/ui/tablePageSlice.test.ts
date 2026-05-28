import { describe, expect, it } from "vitest";
import { sliceTablePage } from "./tablePageSlice";

describe("sliceTablePage", () => {
  it("按页码与每页条数切片", () => {
    const rows = Array.from({ length: 16 }, (_, i) => i + 1);
    expect(sliceTablePage(rows, 1, 10)).toHaveLength(10);
    expect(sliceTablePage(rows, 2, 10)).toEqual([11, 12, 13, 14, 15, 16]);
  });
});
