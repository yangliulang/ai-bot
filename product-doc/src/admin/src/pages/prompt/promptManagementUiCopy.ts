/**
 * Prompt 治理 · 控制台用户可见文案（运营向）。
 * 契约字段名（skillSpecRef、scenarioId）不变；仅改展示口径。
 * SSOT 叙事：product/end-to-end-guide.md §2 · specs/.../prompt-management/
 */

import type { MockPromptPack } from "../../data/types";
import {
  PROMPT_DETAIL,
  PROMPT_GOVERNANCE_INTRO,
  PROMPT_EDITOR,
  PROMPT_PUBLISH_GATE,
  PROMPT_TABLE,
} from "../../copy/opsPanelHints";
import {
  bindingToAssemblyLayers,
  buildDefaultResolvedPromptBinding,
  PROMPT_ASSEMBLY_LAYER,
} from "../../productionRuntime/promptBindingTimeline";
import { formatSkillSpecRef, parseSkillSpecRef } from "../../skillPublish/parseSkillSpecRef";

export { PROMPT_DETAIL, PROMPT_GOVERNANCE_INTRO, PROMPT_EDITOR, PROMPT_PUBLISH_GATE, PROMPT_TABLE };

/** 拼装大类 → 治理四层（人类阅读） */
export const PROMPT_GOVERNANCE_LAYER: Record<
  MockPromptPack["kind"],
  { layer: string; role: string }
> = {
  SYSTEM: { layer: "基础", role: "全局行为与铁闸" },
  TRADING: { layer: "场景", role: "交易场景对话策略" },
  ANALYSIS: { layer: "分析", role: "行情/解读叙事" },
  SAFETY: { layer: "体验", role: "护栏与遥测横幅" },
};

/** 列表/详情单元格：场景优先，技能范围次之 */
export function formatRuntimeSkillScopeCell(pack: MockPromptPack): {
  primary: string;
  secondary?: string;
  title: string;
} {
  if (pack.promptPackId === "pp-analysis-core") {
    return {
      primary: "统一分析包",
      secondary: "读侧能力由系统按轮次注入",
      title: "行情/持仓/舆情/监控等共用本包，不按主题拆包",
    };
  }
  const scenario = pack.scenarioId?.trim();
  const ref = pack.skillSpecRef?.trim();
  if (pack.kind !== "TRADING") {
    return { primary: "—", title: "本类型无写路径技能范围" };
  }
  const parsed = parseSkillSpecRef(ref, scenario);
  const primary = scenario || "（未配置场景键）";
  const secondary = parsed
    ? `范围：${formatSkillSpecRef(parsed)}`
    : ref
      ? `范围：${ref}`
      : scenario
        ? "范围：由场景推断"
        : undefined;
  return {
    primary,
    secondary,
    title: [scenario && `场景 ${scenario}`, ref && `范围 ${ref}`].filter(Boolean).join(" · "),
  };
}

/** 演示用拼装层（优先按 scenario 推断完整绑定，否则仅当前包） */
export function buildDemoPromptAssemblyTrace(pack: MockPromptPack) {
  if (pack.scenarioId?.trim()) {
    const binding = buildDefaultResolvedPromptBinding({
      scenarioId: pack.scenarioId,
      sessionId: null,
    });
    if (pack.kind === "TRADING" || pack.kind === "ANALYSIS") {
      binding.tradingPromptPackId = pack.promptPackId;
      binding.tradingPromptPackVersion = pack.currentVersion;
    }
    return bindingToAssemblyLayers(binding);
  }
  const layer = PROMPT_GOVERNANCE_LAYER[pack.kind]?.layer ?? pack.kind;
  return [
    {
      layer: PROMPT_ASSEMBLY_LAYER.base,
      source:
        pack.kind === "SYSTEM"
          ? `${pack.promptPackId}@v${pack.currentVersion ?? "—"}`
          : "pp-system-core@v1（示意）",
    },
    {
      layer: layer,
      source: `${pack.promptPackId}@v${pack.currentVersion ?? "—"}`,
      promptPackId: pack.promptPackId,
      promptPackVersion: pack.currentVersion,
    },
    { layer: PROMPT_ASSEMBLY_LAYER.runtime, source: "澄清规则 · 会话记忆 · 行情叙事（示意）" },
    { layer: PROMPT_ASSEMBLY_LAYER.output, source: "回复契约（示意）" },
  ];
}
