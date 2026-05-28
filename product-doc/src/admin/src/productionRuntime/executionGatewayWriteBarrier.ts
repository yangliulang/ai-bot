/**
 * Execution Gateway · Write Barrier（MR-B §9）
 * 规格：specs/requirements/skill-specs/MR-B-BFF-IMPLEMENTATION.md §9
 *       specs/requirements/Runtime/runtime-invariants.md §0、INV-008～010
 *
 * 纯函数、无 IO — 所内可在 HTTP 出站 / call_exchange_write 前调用。
 */

export const WRITE_PARAMETER_CONTRACT_TAXONOMY = "WRITE_PARAMETER_CONTRACT" as const;

/** 与 runtime-invariants INV-009 白名单一致（实现字段名可对齐）。 */
export const PROVENANCE_ALLOWLIST = new Set<string>([
  "user_input",
  "confirmation_echo",
  "runtime_read_balance",
  "runtime_read_position",
  "exchange_metadata_normalize",
]);

/** INV-009 明文禁止的占位 / 臆测来源（黑名单）。 */
export const PROVENANCE_BLOCKLIST = new Set<string>([
  "fallback_default",
  "parser_autofill",
  "adapter_placeholder",
  "llm_inferred_unconfirmed",
]);

export type GatewayFailedAssert =
  | "required_fields_complete"
  | "parameter_provenance_valid"
  | "confirmation_snapshot_matches_payload"
  | "validation_passed";

/** 映射 FR-T05 / stableReason — 典型枚举同窗 runtime-error-taxonomy。 */
export type GatewayBarrierReasonCode =
  | "WRITE_PARAMS_INCOMPLETE"
  | "INVALID_PARAMETER_SOURCE"
  | "CONFIRMATION_MISMATCH"
  | "VALIDATION_FAILED";

export type EconomicFieldSource = {
  /** 字段名，如 quantity、quoteQty、price */
  field: string;
  /** 未附带血缘视为非法（Gateway 须拒绝扩张写） */
  source: string | undefined;
  /**
   * 负例：`eval.gateway.metadata_normalize_empty_qty_no_default`
   * 规范化前数量为「空」却仅靠 normalize 「补」出经济数量 → Stop。
   */
  wasEmptyBeforeNormalize?: boolean;
};

export type ExecutionGatewayWriteBarrierInput = {
  /** 已由编排根据 L0 计算：仍缺的写槽名（含 quantity_or_quoteQty 等组合键） */
  missingRequiredSlots: readonly string[];
  /** 将进入交易所写载荷的经济敏感字段及其 provenance.source */
  economicFields: readonly EconomicFieldSource[];
  /** 拟出站 Canonical（写参） */
  canonicalPayload: Readonly<Record<string, unknown>>;
  /** 用户已确认快照 — 逐项须与 Canonical 对齐 */
  confirmationSnapshot: Readonly<Record<string, unknown>>;
  /** 业务/交易所校验器聚合态；非 pass 则断言 4 失败 */
  validationStatus: string;
  /**
   * INV-010：`eval.gateway.sell_all_without_balance_read_fail`
   * 满仓/清仓语义下，quantity/quoteQty 不得仅靠 normalize 或未登记读来源「变出」。
   */
  semanticFullBookIntent?: boolean;
};

export type ExecutionGatewayWriteBarrierFailure = {
  ok: false;
  taxonomy: typeof WRITE_PARAMETER_CONTRACT_TAXONOMY;
  failedAssert: GatewayFailedAssert;
  code: GatewayBarrierReasonCode;
  message: string;
};

export type ExecutionGatewayWriteBarrierOk = { ok: true };

export type ExecutionGatewayWriteBarrierResult =
  | ExecutionGatewayWriteBarrierOk
  | ExecutionGatewayWriteBarrierFailure;

function valuesAlignSnapshot(canonical: unknown, snapshot: unknown): boolean {
  if (canonical === snapshot) return true;
  if (canonical == null && snapshot == null) return true;
  if (canonical == null || snapshot == null) return false;
  return String(canonical).trim() === String(snapshot).trim();
}

/**
 * INV-009：单笔经济字段是否合法。
 */
export function validateSingleProvenance(params: EconomicFieldSource): {
  ok: true;
} | {
  ok: false;
  code: GatewayBarrierReasonCode;
  message: string;
} {
  const { field, source, wasEmptyBeforeNormalize } = params;
  if (source === undefined || String(source).trim() === "") {
    return {
      ok: false,
      code: "INVALID_PARAMETER_SOURCE",
      message: `经济字段 "${field}" 缺少 provenance.source（INV-009）。`,
    };
  }
  if (PROVENANCE_BLOCKLIST.has(source)) {
    return {
      ok: false,
      code: "INVALID_PARAMETER_SOURCE",
      message: `经济字段 "${field}" 血缘 "${source}" 在黑名单（INV-009）。`,
    };
  }
  if (!PROVENANCE_ALLOWLIST.has(source)) {
    return {
      ok: false,
      code: "INVALID_PARAMETER_SOURCE",
      message: `经济字段 "${field}" 血缘 "${source}" 不在允许列表（INV-009）。`,
    };
  }
  if (
    source === "exchange_metadata_normalize" &&
    wasEmptyBeforeNormalize === true
  ) {
    return {
      ok: false,
      code: "INVALID_PARAMETER_SOURCE",
      message: `字段 "${field}" 规范化前为空，不得以 exchange_metadata_normalize 单独捏造经济数量（eval.gateway.metadata_normalize_empty_qty_no_default）。`,
    };
  }
  return { ok: true };
}

function inv010FullBookProvenanceGuard(
  field: EconomicFieldSource,
  semanticFullBookIntent: boolean,
): { ok: true } | { ok: false; message: string } {
  if (!semanticFullBookIntent) return { ok: true };
  const n = field.field.toLowerCase();
  const isQty = n === "quantity" || n === "quoteqty";
  if (!isQty) return { ok: true };
  const s = field.source;
  if (s === "exchange_metadata_normalize") {
    return {
      ok: false,
      message:
        '满仓/清仓语义下 quantity/quoteQty 不得以 "exchange_metadata_normalize" 作为唯一落盘血缘（须有 runtime_read_balance/position 或用户明示）（INV-010）。',
    };
  }
  return { ok: true };
}

/**
 * 四断言顺序与 MR-B §9 表格一致；任一中止则返回失败，且不扩张交易所写。
 */
export function runExecutionGatewayWriteBarrier(
  input: ExecutionGatewayWriteBarrierInput,
): ExecutionGatewayWriteBarrierResult {
  const {
    missingRequiredSlots,
    economicFields,
    canonicalPayload,
    confirmationSnapshot,
    validationStatus,
    semanticFullBookIntent = false,
  } = input;

  if (missingRequiredSlots.length > 0) {
    return {
      ok: false,
      taxonomy: WRITE_PARAMETER_CONTRACT_TAXONOMY,
      failedAssert: "required_fields_complete",
      code: "WRITE_PARAMS_INCOMPLETE",
      message: `写槽未齐备：仍缺 ${missingRequiredSlots.join(", ")}（required_fields_complete / INV-008）。`,
    };
  }

  for (const ef of economicFields) {
    const pv = validateSingleProvenance(ef);
    if (!pv.ok) {
      return {
        ok: false,
        taxonomy: WRITE_PARAMETER_CONTRACT_TAXONOMY,
        failedAssert: "parameter_provenance_valid",
        code: pv.code,
        message: pv.message,
      };
    }
    const fb = inv010FullBookProvenanceGuard(ef, semanticFullBookIntent);
    if (!fb.ok) {
      return {
        ok: false,
        taxonomy: WRITE_PARAMETER_CONTRACT_TAXONOMY,
        failedAssert: "parameter_provenance_valid",
        code: "INVALID_PARAMETER_SOURCE",
        message: fb.message,
      };
    }
  }

  const snapKeys = Object.keys(confirmationSnapshot);
  for (const key of snapKeys) {
    if (!valuesAlignSnapshot(canonicalPayload[key], confirmationSnapshot[key])) {
      return {
        ok: false,
        taxonomy: WRITE_PARAMETER_CONTRACT_TAXONOMY,
        failedAssert: "confirmation_snapshot_matches_payload",
        code: "CONFIRMATION_MISMATCH",
        message: `确认快照与 Canonical 不一致：字段 "${key}"（confirmation_snapshot_matches_payload）。`,
      };
    }
  }

  if (validationStatus !== "pass") {
    return {
      ok: false,
      taxonomy: WRITE_PARAMETER_CONTRACT_TAXONOMY,
      failedAssert: "validation_passed",
      code: "VALIDATION_FAILED",
      message: `校验未通过：validationStatus=${String(validationStatus)}（validation_passed）。`,
    };
  }

  return { ok: true };
}

/** 中间件 / 编排抛错用（同窗 `WRITE_PARAMETER_CONTRACT` 观测）。 */
export class GatewayWriteBarrierViolationError extends Error {
  readonly failure: Omit<ExecutionGatewayWriteBarrierFailure, "ok">;

  constructor(failure: Omit<ExecutionGatewayWriteBarrierFailure, "ok">) {
    super(failure.message);
    this.name = "GatewayWriteBarrierViolationError";
    this.failure = failure;
  }
}

/**
 * 抛错版 — 便于所内在 HTTP 出站前一书到底。
 */
export function assertExecutionGatewayWriteBarrier(
  input: ExecutionGatewayWriteBarrierInput,
): void {
  const r = runExecutionGatewayWriteBarrier(input);
  if (!r.ok) {
    const { taxonomy, failedAssert, code, message } = r;
    throw new GatewayWriteBarrierViolationError({
      taxonomy,
      failedAssert,
      code,
      message,
    });
  }
}
