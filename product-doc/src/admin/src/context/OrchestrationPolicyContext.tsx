import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import {
  DEFAULT_EXECUTION_POLICY,
  type ExecutionPolicyState,
} from "../pages/governance/orchestration/executionPolicyModel";
import { ORCHESTRATION_POLICY_SESSION_KEY } from "../data/orchestrationConstants";

function readStoredPolicy(): ExecutionPolicyState {
  try {
    const raw = sessionStorage.getItem(ORCHESTRATION_POLICY_SESSION_KEY);
    if (!raw) return DEFAULT_EXECUTION_POLICY;
    const p = JSON.parse(raw) as Partial<ExecutionPolicyState>;
    return { ...DEFAULT_EXECUTION_POLICY, ...p };
  } catch {
    return DEFAULT_EXECUTION_POLICY;
  }
}

type Ctx = {
  effectivePolicy: ExecutionPolicyState;
  applyPolicy: (p: ExecutionPolicyState) => void;
  resetPolicyToDefault: () => void;
};

const OrchestrationPolicyContext = createContext<Ctx | null>(null);

export function OrchestrationPolicyProvider({ children }: { children: ReactNode }) {
  const [effectivePolicy, setEffectivePolicy] = useState<ExecutionPolicyState>(() => readStoredPolicy());

  const applyPolicy = useCallback((p: ExecutionPolicyState) => {
    setEffectivePolicy(p);
    try {
      sessionStorage.setItem(ORCHESTRATION_POLICY_SESSION_KEY, JSON.stringify(p));
    } catch {
      /* ignore quota */
    }
  }, []);

  const resetPolicyToDefault = useCallback(() => {
    setEffectivePolicy(DEFAULT_EXECUTION_POLICY);
    try {
      sessionStorage.removeItem(ORCHESTRATION_POLICY_SESSION_KEY);
    } catch {
      /* ignore */
    }
  }, []);

  const value = useMemo(
    () => ({ effectivePolicy, applyPolicy, resetPolicyToDefault }),
    [effectivePolicy, applyPolicy, resetPolicyToDefault],
  );

  return <OrchestrationPolicyContext.Provider value={value}>{children}</OrchestrationPolicyContext.Provider>;
}

export function useOrchestrationPolicy(): Ctx {
  const ctx = useContext(OrchestrationPolicyContext);
  if (!ctx) {
    throw new Error("useOrchestrationPolicy must be used within OrchestrationPolicyProvider");
  }
  return ctx;
}
