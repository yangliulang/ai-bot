import { AGENT_INSTANCES } from "../copy/opsPanelHints";
import type { AgentInstance } from "../data/types";

export type RuntimeCommandKind = "start" | "pause" | "resume" | "stop";

/** 控制台详情页 Runtime 按钮可见性 / 禁用（对齐 functions §3 · G01） */
export interface InstanceRuntimeActionUi {
  showStart: boolean;
  showPause: boolean;
  showResume: boolean;
  showStop: boolean;
  showDelete: boolean;
  /** 主操作（用于 type="primary"） */
  primary: RuntimeCommandKind | null;
  /** G01：全局关闸时禁止 Start / Resume「恢复接单」 */
  disableStart: boolean;
  disableResume: boolean;
  startDisabledReason?: string;
  resumeDisabledReason?: string;
  deleteDisabled: boolean;
  deleteDisabledReason?: string;
}

/**
 * 按实例状态 `runtimeState` 展示不同操作；`GLOBAL_AGENT_SWITCH` OFF（含实例 `agentState === GLOBAL_OFF`）时禁用 Start / Resume（G01）。
 */
export function getInstanceRuntimeActionUi(
  inst: AgentInstance,
  opts?: { globalAgentSwitchOn?: boolean },
): InstanceRuntimeActionUi {
  const globalAgentSwitchOn = opts?.globalAgentSwitchOn ?? true;
  const rt = inst.runtimeState;
  const instanceGlobalOff = inst.agentState === "GLOBAL_OFF";
  const globalSwitchOffBlocks = !globalAgentSwitchOn;

  let showStart = false;
  let showPause = false;
  let showResume = false;
  let showStop = false;
  let primary: RuntimeCommandKind | null = null;

  switch (rt) {
    case "RUNNING":
      showPause = true;
      showStop = true;
      primary = "pause";
      break;
    case "PAUSED":
      showResume = true;
      showStop = true;
      primary = "resume";
      break;
    case "STOPPED":
      showStart = true;
      primary = "start";
      break;
    case "STARTING":
      showStop = true;
      primary = "stop";
      break;
    case "ERROR":
      showStart = true;
      showStop = true;
      primary = "start";
      break;
    default:
      break;
  }

  const disableStart = showStart && (instanceGlobalOff || globalSwitchOffBlocks);
  const disableResume = showResume && (instanceGlobalOff || globalSwitchOffBlocks);

  return {
    showStart,
    showPause,
    showResume,
    showStop,
    showDelete: true,
    primary,
    disableStart,
    disableResume,
    startDisabledReason: disableStart ? AGENT_INSTANCES.startDisabledReason : undefined,
    resumeDisabledReason: disableResume ? AGENT_INSTANCES.resumeDisabledReason : undefined,
    deleteDisabled: rt === "STARTING",
    deleteDisabledReason: rt === "STARTING" ? AGENT_INSTANCES.deleteDisabledReason : undefined,
  };
}
