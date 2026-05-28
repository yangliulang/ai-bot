import { describe, expect, it } from "vitest";
import {
  runExecutionGatewayWriteBarrier,
  validateSingleProvenance,
  PROVENANCE_BLOCKLIST,
} from "./executionGatewayWriteBarrier";

const baseOkInput = () =>
  ({
    missingRequiredSlots: [],
    economicFields: [
      { field: "quantity", source: "runtime_read_balance" },
    ] as const,
    canonicalPayload: {
      symbol: "BTCUSDT",
      side: "BUY",
      quantity: "0.01",
    },
    confirmationSnapshot: {
      symbol: "BTCUSDT",
      side: "BUY",
      quantity: "0.01",
    },
    validationStatus: "pass",
  }) as const;

describe("runExecutionGatewayWriteBarrier（MR-B §9 / eval.gateway.*）", () => {
  it("四断言均满足时 ok", () => {
    const r = runExecutionGatewayWriteBarrier(baseOkInput());
    expect(r).toEqual({ ok: true });
  });

  it("eval.gateway.missing_qty_blocks_exchange_write：缺槽 → required_fields_complete / WRITE_PARAMS_INCOMPLETE", () => {
    const r = runExecutionGatewayWriteBarrier({
      ...baseOkInput(),
      missingRequiredSlots: ["quantity_or_quoteQty"],
    });
    expect(r.ok).toBe(false);
    if (!r.ok) {
      expect(r.failedAssert).toBe("required_fields_complete");
      expect(r.code).toBe("WRITE_PARAMS_INCOMPLETE");
      expect(r.taxonomy).toBe("WRITE_PARAMETER_CONTRACT");
    }
  });

  it("eval.gateway.provenance_fallback_rejected：黑名单 source", () => {
    for (const bad of PROVENANCE_BLOCKLIST) {
      const r = runExecutionGatewayWriteBarrier({
        ...baseOkInput(),
        economicFields: [{ field: "quantity", source: bad }],
      });
      expect(r.ok).toBe(false);
      if (!r.ok) {
        expect(r.failedAssert).toBe("parameter_provenance_valid");
        expect(r.code).toBe("INVALID_PARAMETER_SOURCE");
      }
    }
  });

  it("eval.gateway.metadata_normalize_empty_qty_no_default：空→normalize 捏造", () => {
    const r = runExecutionGatewayWriteBarrier({
      ...baseOkInput(),
      economicFields: [
        {
          field: "quantity",
          source: "exchange_metadata_normalize",
          wasEmptyBeforeNormalize: true,
        },
      ],
    });
    expect(r.ok).toBe(false);
    if (!r.ok) {
      expect(r.failedAssert).toBe("parameter_provenance_valid");
      expect(r.code).toBe("INVALID_PARAMETER_SOURCE");
    }
  });

  it("eval.gateway.sell_all_without_balance_read_fail（近似）：满仓语义 + normalize-only qty", () => {
    const r = runExecutionGatewayWriteBarrier({
      ...baseOkInput(),
      semanticFullBookIntent: true,
      economicFields: [{ field: "quantity", source: "exchange_metadata_normalize" }],
    });
    expect(r.ok).toBe(false);
    if (!r.ok) {
      expect(r.failedAssert).toBe("parameter_provenance_valid");
    }
  });

  it("confirmation_snapshot_matches_payload：快照不一致", () => {
    const r = runExecutionGatewayWriteBarrier({
      ...baseOkInput(),
      confirmationSnapshot: {
        symbol: "BTCUSDT",
        side: "BUY",
        quantity: "0.02",
      },
    });
    expect(r.ok).toBe(false);
    if (!r.ok) {
      expect(r.failedAssert).toBe("confirmation_snapshot_matches_payload");
      expect(r.code).toBe("CONFIRMATION_MISMATCH");
    }
  });

  it("validation_passed：校验非 pass", () => {
    const r = runExecutionGatewayWriteBarrier({
      ...baseOkInput(),
      validationStatus: "fail_min_notional",
    });
    expect(r.ok).toBe(false);
    if (!r.ok) {
      expect(r.failedAssert).toBe("validation_passed");
      expect(r.code).toBe("VALIDATION_FAILED");
    }
  });

  it("validateSingleProvenance：缺 source → INVALID", () => {
    expect(validateSingleProvenance({ field: "quantity", source: undefined }).ok).toBe(
      false,
    );
  });
});
