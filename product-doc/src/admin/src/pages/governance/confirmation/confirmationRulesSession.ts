import { CONFIRMATION_RULES_SESSION_KEY } from "../../../data/confirmationRulesConstants";
import {
  CONFIRMATION_RULES_CATALOG,
  type ConfirmationRuleDefinition,
  type RiskLevel,
  type RuleAction,
  type ScenarioKey,
  type TriggerConditionRow,
  type TriggerFieldKey,
  type TriggerOpKey,
  defaultOperatorForField,
  operatorsForField,
} from "./confirmationRulesCatalog";

export type ConfirmationRulesPersisted = {
  enabledMap: Record<string, boolean>;
  customRules: ConfirmationRuleDefinition[];
};

const VALID_RISK: RiskLevel[] = ["low", "medium", "high"];
const VALID_ACTION: RuleAction[] = ["force_confirm", "second_confirm", "otp_confirm", "block_auto_execute"];
const VALID_SCENARIO = new Set<ScenarioKey>([
  "spot",
  "futures",
  "convert",
  "wealth",
  "leverage",
  "transfer",
  "conditional_order",
]);
const VALID_FIELD: TriggerFieldKey[] = ["nominal_usdt", "leverage", "operation_scope", "custom"];
const VALID_OP: TriggerOpKey[] = ["gt", "gte", "lt", "lte", "eq", "contains"];

function isPlainObject(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null && !Array.isArray(x);
}

function sanitizeBoolMap(x: unknown): Record<string, boolean> {
  if (!isPlainObject(x)) return {};
  const out: Record<string, boolean> = {};
  for (const [k, v] of Object.entries(x)) {
    if (typeof v === "boolean") out[k] = v;
  }
  return out;
}

function sanitizeTriggerRows(x: unknown): TriggerConditionRow[] {
  if (!Array.isArray(x)) return [];
  const out: TriggerConditionRow[] = [];
  for (const row of x) {
    if (!isPlainObject(row)) continue;
    const fk = row.fieldKey;
    const op = row.operator;
    const val = row.value;
    if (!VALID_FIELD.includes(fk as TriggerFieldKey)) continue;
    if (!VALID_OP.includes(op as TriggerOpKey)) continue;
    if (typeof val !== "string" || !val.trim()) continue;
    let operator = op as TriggerOpKey;
    if (!operatorsForField(fk as TriggerFieldKey).includes(operator)) {
      operator = defaultOperatorForField(fk as TriggerFieldKey);
    }
    out.push({ fieldKey: fk as TriggerFieldKey, operator, value: val.trim() });
  }
  return out;
}

function sanitizeScenarios(x: unknown): ScenarioKey[] {
  if (!Array.isArray(x)) return [];
  const out: ScenarioKey[] = [];
  for (const s of x) {
    if (typeof s === "string" && VALID_SCENARIO.has(s as ScenarioKey)) out.push(s as ScenarioKey);
  }
  return [...new Set(out)];
}

function sanitizeCustomRules(x: unknown): ConfirmationRuleDefinition[] {
  if (!Array.isArray(x)) return [];
  const out: ConfirmationRuleDefinition[] = [];
  for (const item of x) {
    if (!isPlainObject(item)) continue;
    const r = item as Record<string, unknown>;
    const id = r.id;
    if (typeof id !== "string" || !id.startsWith("custom-")) continue;
    if (typeof r.title !== "string" || typeof r.summary !== "string") continue;
    const riskLevel = r.riskLevel;
    if (typeof riskLevel !== "string" || !VALID_RISK.includes(riskLevel as RiskLevel)) continue;
    const action = r.action;
    if (typeof action !== "string" || !VALID_ACTION.includes(action as RuleAction)) continue;
    const scenarios = sanitizeScenarios(r.scenarios);
    const triggerConditions = sanitizeTriggerRows(r.triggerConditions);
    if (!scenarios.length || !triggerConditions.length) continue;
    out.push({
      id,
      title: r.title,
      summary: r.summary,
      riskLevel: riskLevel as RiskLevel,
      scenarios,
      action: action as RuleAction,
      triggerConditions,
      defaultEnabled: typeof r.defaultEnabled === "boolean" ? r.defaultEnabled : true,
    });
  }
  return out;
}

export function isBuiltinConfirmationRuleId(id: string): boolean {
  return CONFIRMATION_RULES_CATALOG.some((r) => r.id === id);
}

export function mergeRuleList(customRules: ConfirmationRuleDefinition[]): ConfirmationRuleDefinition[] {
  return [...CONFIRMATION_RULES_CATALOG, ...customRules];
}

export function buildDefaultEnabledMap(customRules: ConfirmationRuleDefinition[]): Record<string, boolean> {
  const m: Record<string, boolean> = {};
  for (const r of CONFIRMATION_RULES_CATALOG) m[r.id] = r.defaultEnabled;
  for (const r of customRules) m[r.id] = r.defaultEnabled;
  return m;
}

export function mergeEnabledWithDefaults(
  stored: Record<string, boolean> | null | undefined,
  customRules: ConfirmationRuleDefinition[],
): Record<string, boolean> {
  const defaults = buildDefaultEnabledMap(customRules);
  if (!stored) return defaults;
  const next = { ...defaults };
  for (const k of Object.keys(stored)) {
    if (k in next) next[k] = stored[k];
  }
  return next;
}

export function readConfirmationRulesSession(): ConfirmationRulesPersisted | null {
  try {
    const raw = sessionStorage.getItem(CONFIRMATION_RULES_SESSION_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as unknown;
    if (isPlainObject(parsed) && "customRules" in parsed) {
      return {
        enabledMap: sanitizeBoolMap(parsed.enabledMap),
        customRules: sanitizeCustomRules(parsed.customRules),
      };
    }
    if (isPlainObject(parsed)) {
      const m = sanitizeBoolMap(parsed);
      if (Object.keys(m).length > 0) return { enabledMap: m, customRules: [] };
    }
    return null;
  } catch {
    return null;
  }
}

export function writeConfirmationRulesSession(data: ConfirmationRulesPersisted): void {
  try {
    sessionStorage.setItem(CONFIRMATION_RULES_SESSION_KEY, JSON.stringify(data));
  } catch {
    /* ignore quota */
  }
}

export function clearConfirmationRulesSession(): void {
  try {
    sessionStorage.removeItem(CONFIRMATION_RULES_SESSION_KEY);
  } catch {
    /* ignore */
  }
}

export function newCustomRuleId(): string {
  const c = globalThis.crypto;
  if (c?.randomUUID) return `custom-${c.randomUUID()}`;
  return `custom-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
