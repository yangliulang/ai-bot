import type { MockPromptPack } from "../../data/types";

/** 列表 URL 参数 life= */
export type PromptLifecycleListFilter =
  | "all"
  | "draft"
  | "published"
  | "locked"
  | "iterate"
  | "deprecated";

export function parsePromptLifecycleListFilter(raw: string | null | undefined): PromptLifecycleListFilter {
  const u = (raw ?? "").toLowerCase();
  if (u === "draft" || u === "published" || u === "locked" || u === "iterate" || u === "deprecated") return u;
  return "all";
}

export function packMatchesLifecycleFilter(p: MockPromptPack, f: PromptLifecycleListFilter): boolean {
  if (f === "all") return true;
  if (f === "deprecated") return Boolean(p.deprecatedAt);
  if (f === "draft") return p.lockState === "DRAFT";
  if (f === "published") return p.lockState === "PUBLISHED";
  if (f === "locked") return p.lockState === "LOCKED";
  if (f === "iterate") return p.hasDraft === true && p.lockState !== "DRAFT";
  return true;
}

/** 列表「阶段」列：主标签 + 辅色 */
export function promptPackLifecycleSummary(p: MockPromptPack): { label: string; color: string } {
  if (p.deprecatedAt) return { label: "下线中", color: "default" };
  if (p.lockState === "DRAFT") return { label: "草稿线", color: "processing" };
  if (p.hasDraft && p.lockState !== "DRAFT") return { label: "生效·迭代草稿", color: "warning" };
  if (p.lockState === "LOCKED") return { label: "已锁定包", color: "magenta" };
  if (p.lockState === "PUBLISHED") return { label: "已发布", color: "success" };
  return { label: p.lockState, color: "default" };
}

/** 详情/编辑器侧「建议下一步」短句 */
export function promptPackNextStepHints(p: MockPromptPack): string[] {
  const lines: string[] = [];
  if (p.deprecatedAt) {
    lines.push("已标记下线：确认运行侧引用已切换或已安排回滚。");
    return lines;
  }
  if (p.lockState === "DRAFT") {
    lines.push("继续完善正文与场景键，校验通过后再发布。");
    if (p.kind === "SAFETY") lines.push("护栏包正式发布前走审批与会签（域 rules）。");
    return lines;
  }
  if (p.lockState === "LOCKED") {
    lines.push("系统包已锁定：先「复制草稿」再改，改完后再发布。");
    return lines;
  }
  if (p.hasDraft) {
    lines.push("存在未发布草稿：确认变更后在编辑器发布，或丢弃草稿。");
  }
  if (p.lockState === "PUBLISHED") {
    lines.push("已发布生效：新版本从快照开草稿再发布；异常可用版本回滚。");
  }
  return lines.length ? lines : ["建议在编辑器中试跑单包后再发布。"];
}

/** 编辑器顶栏 Steps：草稿 → 已发布 → LOCKED → 下线 */
export function promptEditorHorizontalStep(p: MockPromptPack): number {
  if (p.deprecatedAt) return 3;
  if (p.lockState === "LOCKED") return 2;
  if (p.lockState === "PUBLISHED") return 1;
  return 0;
}
