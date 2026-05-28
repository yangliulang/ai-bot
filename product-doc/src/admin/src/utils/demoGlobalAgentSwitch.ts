import { globalGateConfigKeys } from "../data/mock";

/** 读 Demo `globalGateConfigKeys` 中 `GLOBAL_AGENT_SWITCH`；默认视为 ON */
export function isDemoGlobalAgentSwitchOn(): boolean {
  const row = globalGateConfigKeys.find((k) => k.configKey === "GLOBAL_AGENT_SWITCH");
  if (!row) return true;
  const v = row.demoValue.trim().toLowerCase();
  return v !== "false" && v !== "0" && v !== "off";
}

/** G01 横幅文案下限（与附录 A / trading-agent-config 叙事同窗） */
export const DEMO_GLOBAL_AGENT_OFF_SUMMARY =
  "GLOBAL_AGENT_SWITCH=OFF：禁止承接类 Start / Resume（G01）；实例列表批量 Pause / Stop 仍可用。";
