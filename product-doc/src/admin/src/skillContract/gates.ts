/**
 * 写路径槽位门禁（演示 / Vitest）— 对齐 specs/requirements/skill-specs 金样规则。
 * 非生产 Runtime；Orchestration 真源仍为 read_skill_operation_spec 正文。
 */

export type SlotBag = Record<string, unknown>;

export type GateResult = {
  ok: boolean;
  missing: string[];
  reason?: string;
};

function has(v: unknown): boolean {
  return v !== undefined && v !== null && v !== "";
}

function hasQtyOrQuote(slots: SlotBag): boolean {
  return has(slots.quantity) || has(slots.quoteQty);
}

/** 是否允许进入类型 A（步骤 3 之前） */
export function canProceedToTypeA(skillId: string, slots: SlotBag): GateResult {
  const missing: string[] = [];

  switch (skillId) {
    case "skill.spot.limit_order": {
      if (!has(slots.symbol)) missing.push("symbol");
      if (!has(slots.side)) missing.push("side");
      if (!has(slots.price)) missing.push("price");
      if (!hasQtyOrQuote(slots)) missing.push("quantity|quoteQty");
      if (has(slots.price) === false && missing.length === 0) missing.push("price");
      break;
    }
    case "skill.spot.flash_convert": {
      if (!has(slots.symbol)) missing.push("symbol");
      if (!has(slots.side)) missing.push("side");
      if (!hasQtyOrQuote(slots)) missing.push("quantity|quoteQty");
      if (has(slots.price)) {
        return { ok: false, missing: ["price"], reason: "flash_convert_must_not_carry_limit_price" };
      }
      break;
    }
    case "skill.spot.amend_limit_order": {
      if (!has(slots.originalOrderId) && !has(slots.originalClientOrderId)) {
        missing.push("originalOrderId|originalClientOrderId");
      }
      if (!has(slots.symbol)) missing.push("symbol");
      if (!has(slots.side)) missing.push("side");
      if (!has(slots.price)) missing.push("price");
      if (!has(slots.quantity)) missing.push("quantity");
      break;
    }
    case "skill.futures.limit_order": {
      if (!has(slots.symbol)) missing.push("symbol");
      if (!has(slots.positionSide)) missing.push("positionSide");
      if (!has(slots.price)) missing.push("price");
      if (!has(slots.quantity)) missing.push("quantity");
      break;
    }
    case "skill.margin.cross_market_order": {
      if (!has(slots.symbol)) missing.push("symbol");
      if (!has(slots.side)) missing.push("side");
      if (!hasQtyOrQuote(slots)) missing.push("quantity|quoteQty");
      if (has(slots.price)) {
        return { ok: false, missing: ["price"], reason: "cross_market_must_not_carry_limit_price" };
      }
      break;
    }
    default:
      return { ok: true, missing: [] };
  }

  return { ok: missing.length === 0, missing };
}

/** 逻辑改单写序：cancel 必须先于 order */
export function isValidAmendWriteSequence(actions: readonly string[]): boolean {
  const cancelIdx = actions.indexOf("cancel");
  const orderIdx = actions.indexOf("order");
  if (cancelIdx < 0 || orderIdx < 0) return false;
  return cancelIdx < orderIdx;
}

/** 全仓双确认：须两次 CONFIRMED 后才可写 */
export function marginCrossWriteAllowed(confirmCount: number): boolean {
  return confirmCount >= 2;
}
