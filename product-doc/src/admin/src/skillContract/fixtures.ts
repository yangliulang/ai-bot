/**
 * 对齐 specs/requirements/evals/skill-contract.md · P0 回归束
 */

import type { SlotBag } from "./gates";

export type SkillEvalFixture = {
  evalSetId: string;
  skillId: string;
  scenarioId: string;
  slots: SlotBag;
  expectTypeA: boolean;
  expectWrite: boolean;
  amendSequence?: string[];
  marginConfirmCount?: number;
};

export const EVAL_SKILL_FIXTURES: SkillEvalFixture[] = [
  {
    evalSetId: "eval.skill.missing_qty_no_confirm",
    skillId: "skill.spot.limit_order",
    scenarioId: "trade.spot.limit_order",
    slots: { symbol: "BTCUSDT", side: "BUY", type: "LIMIT", price: "95000" },
    expectTypeA: false,
    expectWrite: false,
  },
  {
    evalSetId: "eval.skill.flash_no_limit_price",
    skillId: "skill.spot.flash_convert",
    scenarioId: "trade.spot.flash_convert",
    slots: { symbol: "BTCUSDT", side: "BUY", quantity: "0.01", price: "95000" },
    expectTypeA: false,
    expectWrite: false,
  },
  {
    evalSetId: "eval.skill.margin_double_confirm",
    skillId: "skill.margin.cross_market_order",
    scenarioId: "margin.cross.market_order",
    slots: { symbol: "BTC_USDT", side: "BUY", quoteQty: "1000" },
    expectTypeA: true,
    expectWrite: false,
    marginConfirmCount: 1,
  },
  {
    evalSetId: "eval.skill.amend_cancel_before_order",
    skillId: "skill.spot.amend_limit_order",
    scenarioId: "trade.spot.amend_limit_order",
    slots: {
      originalOrderId: "ord-1",
      symbol: "BTCUSDT",
      side: "BUY",
      price: "96000",
      quantity: "0.01",
    },
    expectTypeA: true,
    expectWrite: true,
    amendSequence: ["cancel", "order"],
  },
];
