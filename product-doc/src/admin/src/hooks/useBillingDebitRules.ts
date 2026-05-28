import { useCallback, useState } from "react";
import { DEBIT_RULE_SEED, type BillingDebitRule } from "../data/billingRulesSeed";

const STORAGE_KEY = "coobit-admin-billing-debit-rules-v1";

function seedSummaryFor(capabilitySkuId: string): string {
  return DEBIT_RULE_SEED.find((r) => r.capabilitySkuId === capabilitySkuId)?.summary ?? "";
}

function normalizeRule(raw: unknown): BillingDebitRule | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  if (typeof o.capabilitySkuId !== "string" || typeof o.displayLabel !== "string") return null;
  const debit = Number(o.debitUnitsPerExecution);
  if (!Number.isFinite(debit) || debit < 1) return null;
  const summary =
    typeof o.summary === "string" && o.summary.trim()
      ? o.summary.trim()
      : seedSummaryFor(o.capabilitySkuId);
  return {
    capabilitySkuId: o.capabilitySkuId,
    displayLabel: o.displayLabel.trim(),
    summary,
    debitUnitsPerExecution: debit,
  };
}

function loadFromStorage(): BillingDebitRule[] {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as unknown[];
      if (Array.isArray(parsed) && parsed.length > 0) {
        const rules = parsed.map(normalizeRule).filter((r): r is BillingDebitRule => !!r);
        if (rules.length > 0) return rules;
      }
    }
  } catch {
    /* seed */
  }
  return DEBIT_RULE_SEED.map((r) => ({ ...r }));
}

function persist(rules: BillingDebitRule[]) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(rules));
}

export function useBillingDebitRules() {
  const [rules, setRulesState] = useState<BillingDebitRule[]>(loadFromStorage);

  const setRules = useCallback((next: BillingDebitRule[]) => {
    setRulesState(next);
    persist(next);
  }, []);

  const upsertRules = useCallback((next: BillingDebitRule[]) => {
    setRules(next);
  }, [setRules]);

  const resetToSeed = useCallback(() => {
    setRules(DEBIT_RULE_SEED.map((r) => ({ ...r })));
  }, [setRules]);

  return { rules, upsertRules, resetToSeed };
}
