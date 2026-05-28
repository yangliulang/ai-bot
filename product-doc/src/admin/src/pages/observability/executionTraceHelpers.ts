import {
  DEMO_EXEC_AA11,
  DEMO_EXEC_BB22,
  DEMO_EXEC_FAIL01,
  DEMO_EXEC_RUN01,
  DEMO_EXEC_UN99,
} from "../../data/demoExecutionIds";
import type { MockObsExecutionRow } from "../../data/types";

export type TraceStepState = "success" | "error" | "warning" | "default";

export interface TraceStep {
  time: string;
  title: string;
  detail?: string;
  state?: TraceStepState;
}

/** 列表/抽屉：终态高亮（运营可读枚举） */
export function executionTraceOutcomeTag(row: MockObsExecutionRow): { label: string; color: string } {
  const { outcome, status, currentStage, durationMs } = row;
  if (status === "COMPLETED" || outcome === "PER_EXECUTION_FINAL") {
    return { label: "SUCCESS", color: "success" };
  }
  if (outcome === "FAILED" && (currentStage === "TOOL_FAILED" || (durationMs > 0 && durationMs < 1500))) {
    return { label: "TIMEOUT", color: "magenta" };
  }
  if (outcome === "FAILED" || status === "FAILED") {
    return { label: "FAILED", color: "error" };
  }
  if (outcome === "BILLING_BLOCKED" || status === "BLOCKED") {
    return { label: "BLOCKED", color: "warning" };
  }
  if (status === "RUNNING" || outcome === "RUNNING") {
    return { label: "RUNNING", color: "processing" };
  }
  if (outcome === "UNKNOWN") {
    return { label: "UNKNOWN", color: "default" };
  }
  return { label: status || outcome || "—", color: "default" };
}

function hhmmssFromIso(iso: string): string {
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleTimeString("zh-CN", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return iso;
  }
}

/** 演示：核心 execution 的链路与通用回退 */
export function getTraceTimelineSteps(row: MockObsExecutionRow): TraceStep[] {
  const t0 = hhmmssFromIso(row.startedAt);
  const id = row.executionId;

  if (id === DEMO_EXEC_AA11) {
    return [
      { time: t0, title: "Intent 识别", detail: row.intent, state: "success" },
      { time: t0, title: "Route → trade.spot.limit_order", detail: `scenarioId: ${row.scenarioId}`, state: "success" },
      { time: t0, title: "调用 risk_check", detail: "限额 / 符号闸通过", state: "success" },
      { time: t0, title: "命中人工确认", detail: "大额限价单", state: "warning" },
      { time: t0, title: "用户确认", detail: "二次确认完成", state: "success" },
      { time: t0, title: "下单", detail: "exchange.order.place", state: "success" },
      { time: t0, title: "返回成功", detail: "PER_EXECUTION_FINAL", state: "success" },
    ];
  }

  if (id === DEMO_EXEC_BB22) {
    return [
      { time: t0, title: "Intent 识别", detail: row.intent, state: "success" },
      { time: t0, title: "Route → trade.spot.limit_order", state: "success" },
      { time: t0, title: "调用 risk_check", state: "success" },
      { time: t0, title: "计费闸口拦截", detail: "BILLING_BLOCKED", state: "warning" },
      { time: t0, title: "执行阻塞", detail: "待计费/人工处理", state: "warning" },
    ];
  }

  if (id === DEMO_EXEC_FAIL01) {
    return [
      { time: t0, title: "Intent 识别", detail: row.intent, state: "success" },
      { time: t0, title: "Route → trade.futures.market_order", state: "success" },
      { time: t0, title: "调用 risk_check", state: "success" },
      { time: t0, title: "工具调用超时", detail: "exchange.futures.order", state: "error" },
      { time: t0, title: "失败收尾", detail: "FAILED", state: "error" },
    ];
  }

  if (id === DEMO_EXEC_RUN01) {
    return [
      { time: t0, title: "Intent 识别", detail: row.intent, state: "success" },
      { time: t0, title: "Route → trade.spot.limit_order", state: "success" },
      { time: t0, title: "人工确认等待中", state: "warning" },
      { time: t0, title: "运行中", detail: "RUNNING", state: "default" },
    ];
  }

  if (id === DEMO_EXEC_UN99) {
    return [
      { time: t0, title: "Intent 识别", detail: row.intent, state: "success" },
      { time: t0, title: "Route → trade.spot.flash_convert", state: "success" },
      { time: t0, title: "对账不确定性", detail: "UNKNOWN / RECONCILING", state: "warning" },
    ];
  }

  const stageZh: Record<string, string> = {
    CREATED: "已创建",
    CONFIRM_PENDING: "待确认",
    RUNNING: "运行中",
    COMPLETED: "已完成",
    BLOCKED: "已阻塞",
    BILLING_GATE: "计费闸口",
    TOOL_FAILED: "工具失败",
    FAILED: "失败",
    RECONCILING: "对账中",
    UNKNOWN: "待核对",
  };

  return row.stageTimeline.map((stage, i) => ({
    time: t0,
    title: stageZh[stage] ?? stage,
    detail: i === row.stageTimeline.length - 1 ? `current: ${row.currentStage}` : undefined,
    state: stage === "FAILED" || stage === "BLOCKED" ? "error" : stage === "RUNNING" ? "default" : "success",
  }));
}

export function riskHitSummary(row: MockObsExecutionRow): string {
  if (row.executionId === DEMO_EXEC_BB22) return "计费闸口未通过（BILLING_BLOCKED）";
  if (row.executionId === DEMO_EXEC_FAIL01) return "工具侧超时 / 调用失败";
  if (row.outcome === "PER_EXECUTION_FINAL" || row.status === "COMPLETED") return "未命中阻断性风控（演示）";
  if (row.status === "BLOCKED") return "执行阶段阻塞，见终态与时间线";
  return "见执行阶段与时间线（演示）";
}

export function promptSummaryLine(row: MockObsExecutionRow): string {
  return `意图：${row.intent}；场景：${row.scenarioId}`;
}
