import { useCallback, useState } from "react";
import { SCENARIO_MAPPING_SEED, type BillingScenarioMappingRow } from "../data/billingRulesSeed";

const STORAGE_KEY = "coobit-admin-scenario-billing-map-v1";

function normalizeRow(raw: unknown): BillingScenarioMappingRow | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  if (typeof o.scenarioId !== "string" || typeof o.capabilitySkuId !== "string") return null;
  const scenarioId = o.scenarioId.trim();
  if (!scenarioId) return null;
  return { scenarioId, capabilitySkuId: o.capabilitySkuId };
}

function loadFromStorage(): BillingScenarioMappingRow[] {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as unknown[];
      if (Array.isArray(parsed) && parsed.length > 0) {
        const rows = parsed.map(normalizeRow).filter((r): r is BillingScenarioMappingRow => !!r);
        if (rows.length > 0) return rows;
      }
    }
  } catch {
    /* seed */
  }
  return SCENARIO_MAPPING_SEED.map((r) => ({ ...r }));
}

function persist(rows: BillingScenarioMappingRow[]) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(rows));
}

export function useScenarioBillingMap() {
  const [rows, setRowsState] = useState<BillingScenarioMappingRow[]>(loadFromStorage);

  const setRows = useCallback((next: BillingScenarioMappingRow[]) => {
    setRowsState(next);
    persist(next);
  }, []);

  const upsertRow = useCallback((row: BillingScenarioMappingRow) => {
    const scenarioId = row.scenarioId.trim();
    const withId = { ...row, scenarioId };
    setRowsState((prev) => {
      const idx = prev.findIndex((r) => r.scenarioId === scenarioId);
      const next = idx >= 0 ? prev.map((r, i) => (i === idx ? withId : r)) : [...prev, withId];
      persist(next);
      return next;
    });
  }, []);

  const deleteRow = useCallback((scenarioId: string) => {
    setRowsState((prev) => {
      const next = prev.filter((r) => r.scenarioId !== scenarioId);
      persist(next);
      return next;
    });
  }, []);

  const resetToSeed = useCallback(() => {
    setRows(SCENARIO_MAPPING_SEED.map((r) => ({ ...r })));
  }, [setRows]);

  return { rows, upsertRow, deleteRow, resetToSeed };
}
