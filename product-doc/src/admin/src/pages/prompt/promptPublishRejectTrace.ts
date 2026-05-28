/** Prompt 发布校验 · 结构化拒绝项（Demo / 预检） */

import { isUnifiedAnalysisPromptPack } from "../../data/mockPromptData";
import type { MockPromptPack } from "../../data/types";
import type { SkillSpecPublishValidation } from "../../skillPublish/validateSkillSpecRefForPublish";

export type PromptPublishGateId =
  | "scenario"
  | "body_size"
  | "skill_scope"
  | "pack_locked";

export type PromptPublishRejection = {
  code: string;
  gate: PromptPublishGateId;
  title: string;
  detail: string;
  remediation?: string;
};

export type PromptPublishGateTrace = {
  ok: boolean;
  checkedAt: string;
  rejections: PromptPublishRejection[];
  /** 兼容旧 UI：detail 拼接 */
  reasons: string[];
};

const GATE_LABEL: Record<PromptPublishGateId, string> = {
  scenario: "场景键",
  body_size: "正文体积",
  skill_scope: "技能登记",
  pack_locked: "版本状态",
};

export function rejectionToReason(r: PromptPublishRejection): string {
  return `[${r.code}] ${r.detail}`;
}

export function buildGateTrace(rejections: PromptPublishRejection[]): PromptPublishGateTrace {
  return {
    ok: rejections.length === 0,
    checkedAt: new Date().toISOString(),
    rejections,
    reasons: rejections.map(rejectionToReason),
  };
}

export function validatePublishDemoStructured(
  pack: MockPromptPack,
  scenarioIdField: string,
  body: string,
): PromptPublishRejection[] {
  const rejections: PromptPublishRejection[] = [];

  if (pack.lockState === "LOCKED") {
    rejections.push({
      code: "PROMPT_PACK_LOCKED",
      gate: "pack_locked",
      title: GATE_LABEL.pack_locked,
      detail: "系统包等已锁定版本须走新版本线，不可在原位直接发布。",
      remediation: "使用「复制草稿」或新建版本线后再发布。",
    });
  }

  if (pack.kind === "TRADING" && !scenarioIdField.trim()) {
    rejections.push({
      code: "PROMPT_SCENARIO_INVALID",
      gate: "scenario",
      title: GATE_LABEL.scenario,
      detail: "交易类场景包发布前须填写场景键（与 routing-engine 对齐）。",
      remediation: "在「运行场景」目录核对场景键，或在包元数据中补齐。",
    });
  }

  if (pack.kind === "ANALYSIS" && !isUnifiedAnalysisPromptPack(pack) && !scenarioIdField.trim()) {
    rejections.push({
      code: "PROMPT_SCENARIO_INVALID",
      gate: "scenario",
      title: GATE_LABEL.scenario,
      detail: "分析类提示词应使用统一分析包；勿按主题拆多个 ANALYSIS 包。",
      remediation: "读侧请使用「分析对话（统一）」包；具体能力在运行场景与能力寄存器中配置。",
    });
  }

  if (body.length > 256 * 1024) {
    rejections.push({
      code: "PROMPT_BODY_TOO_LARGE",
      gate: "body_size",
      title: GATE_LABEL.body_size,
      detail: `正文约 ${(body.length / 1024).toFixed(0)}KB，超过平台上限（约 256KB）。`,
      remediation: "删减正文、移出 Few-shot 快照或拆分场景包。",
    });
  }

  return rejections;
}

export function skillScopeToRejection(skill: SkillSpecPublishValidation): PromptPublishRejection | null {
  if (skill.ok) return null;
  const code = skill.code ?? "PROMPT_SKILL_REF_INVALID";
  return {
    code,
    gate: "skill_scope",
    title: GATE_LABEL.skill_scope,
    detail: skill.reason ?? "技能范围无法解析或未在登记册就绪。",
    remediation:
      code === "PROMPT_SKILL_REF_MISSING"
        ? "在包上填写「技能@版本」，或配置写路径场景键；见「技能与工具」登记册。"
        : "打开「技能与工具」核对技能版本是否已发布；勿在提示词正文维护技能内容。",
  };
}
