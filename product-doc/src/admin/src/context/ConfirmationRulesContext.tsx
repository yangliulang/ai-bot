import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { CONFIRMATION_RULES_CATALOG, cloneDemoCustomConfirmationRules, type ConfirmationRuleDefinition } from "../pages/governance/confirmation/confirmationRulesCatalog";
import {
  buildDefaultEnabledMap,
  clearConfirmationRulesSession,
  isBuiltinConfirmationRuleId,
  mergeEnabledWithDefaults,
  mergeRuleList,
  newCustomRuleId,
  readConfirmationRulesSession,
  writeConfirmationRulesSession,
} from "../pages/governance/confirmation/confirmationRulesSession";

type Ctx = {
  /** 内置 + 自定义合并列表（内置在前） */
  mergedRules: ConfirmationRuleDefinition[];
  customRules: ConfirmationRuleDefinition[];
  enabledMap: Record<string, boolean>;
  isBuiltinRule: (ruleId: string) => boolean;
  isRuleEnabled: (ruleId: string) => boolean;
  setRuleEnabled: (ruleId: string, enabled: boolean) => void;
  addCustomRule: (rule: Omit<ConfirmationRuleDefinition, "id">) => string;
  updateCustomRule: (id: string, rule: ConfirmationRuleDefinition) => void;
  removeCustomRule: (id: string) => void;
  resetRulesToCatalogDefaults: () => void;
};

const ConfirmationRulesContext = createContext<Ctx | null>(null);

function initFromSession(): { customRules: ConfirmationRuleDefinition[]; enabledMap: Record<string, boolean> } {
  const stored = readConfirmationRulesSession();
  if (!stored) {
    const customRules = cloneDemoCustomConfirmationRules();
    const enabledMap = mergeEnabledWithDefaults(null, customRules);
    writeConfirmationRulesSession({ enabledMap, customRules });
    return { customRules, enabledMap };
  }
  const customRules = stored.customRules ?? [];
  const enabledMap = mergeEnabledWithDefaults(stored.enabledMap, customRules);
  return { customRules, enabledMap };
}

export function ConfirmationRulesProvider({ children }: { children: ReactNode }) {
  const [{ customRules, enabledMap }, setState] = useState(initFromSession);

  const persistFull = useCallback((customRules_: ConfirmationRuleDefinition[], enabledMap_: Record<string, boolean>) => {
    const defaults = buildDefaultEnabledMap(customRules_);
    const keysMatch =
      Object.keys(enabledMap_).length === Object.keys(defaults).length &&
      Object.keys(defaults).every((id) => Object.prototype.hasOwnProperty.call(enabledMap_, id));
    const valuesMatch = keysMatch && Object.keys(defaults).every((id) => enabledMap_[id] === defaults[id]);
    if (valuesMatch && customRules_.length === 0) {
      clearConfirmationRulesSession();
      return;
    }
    writeConfirmationRulesSession({ enabledMap: enabledMap_, customRules: customRules_ });
  }, []);

  const mergedRules = useMemo(() => mergeRuleList(customRules), [customRules]);

  const isBuiltinRule = useCallback((ruleId: string) => isBuiltinConfirmationRuleId(ruleId), []);

  const isRuleEnabled = useCallback(
    (ruleId: string) =>
      enabledMap[ruleId] ??
      CONFIRMATION_RULES_CATALOG.find((r) => r.id === ruleId)?.defaultEnabled ??
      customRules.find((r) => r.id === ruleId)?.defaultEnabled ??
      false,
    [enabledMap, customRules],
  );

  const setRuleEnabled = useCallback(
    (ruleId: string, enabled: boolean) => {
      setState((prev) => {
        const nextEnabled = { ...prev.enabledMap, [ruleId]: enabled };
        persistFull(prev.customRules, nextEnabled);
        return { ...prev, enabledMap: nextEnabled };
      });
    },
    [persistFull],
  );

  const addCustomRule = useCallback(
    (rule: Omit<ConfirmationRuleDefinition, "id">): string => {
      const id = newCustomRuleId();
      const full: ConfirmationRuleDefinition = { ...rule, id };
      setState((prev) => {
        const nextCustom = [...prev.customRules, full];
        const nextEnabled = { ...prev.enabledMap, [id]: full.defaultEnabled };
        persistFull(nextCustom, nextEnabled);
        return { customRules: nextCustom, enabledMap: nextEnabled };
      });
      return id;
    },
    [persistFull],
  );

  const updateCustomRule = useCallback(
    (id: string, rule: ConfirmationRuleDefinition) => {
      if (isBuiltinConfirmationRuleId(id)) return;
      setState((prev) => {
        const nextCustom = prev.customRules.map((r) => (r.id === id ? rule : r));
        const nextEnabled = {
          ...prev.enabledMap,
          [id]: prev.enabledMap[id] ?? rule.defaultEnabled,
        };
        persistFull(nextCustom, nextEnabled);
        return { customRules: nextCustom, enabledMap: nextEnabled };
      });
    },
    [persistFull],
  );

  const removeCustomRule = useCallback(
    (id: string) => {
      if (isBuiltinConfirmationRuleId(id)) return;
      setState((prev) => {
        const nextCustom = prev.customRules.filter((r) => r.id !== id);
        const nextEnabled = { ...prev.enabledMap };
        delete nextEnabled[id];
        persistFull(nextCustom, nextEnabled);
        return { customRules: nextCustom, enabledMap: nextEnabled };
      });
    },
    [persistFull],
  );

  const resetRulesToCatalogDefaults = useCallback(() => {
    const customRules = cloneDemoCustomConfirmationRules();
    const nextEnabled = mergeEnabledWithDefaults(null, customRules);
    writeConfirmationRulesSession({ enabledMap: nextEnabled, customRules });
    setState({ customRules, enabledMap: nextEnabled });
  }, []);

  const value = useMemo(
    () => ({
      mergedRules,
      customRules,
      enabledMap,
      isBuiltinRule,
      isRuleEnabled,
      setRuleEnabled,
      addCustomRule,
      updateCustomRule,
      removeCustomRule,
      resetRulesToCatalogDefaults,
    }),
    [
      mergedRules,
      customRules,
      enabledMap,
      isBuiltinRule,
      isRuleEnabled,
      setRuleEnabled,
      addCustomRule,
      updateCustomRule,
      removeCustomRule,
      resetRulesToCatalogDefaults,
    ],
  );

  return <ConfirmationRulesContext.Provider value={value}>{children}</ConfirmationRulesContext.Provider>;
}

export function useConfirmationRules(): Ctx {
  const ctx = useContext(ConfirmationRulesContext);
  if (!ctx) {
    throw new Error("useConfirmationRules must be used within ConfirmationRulesProvider");
  }
  return ctx;
}
