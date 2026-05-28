/**
 * 写路径事件序下限 — 同窗 `eval.runtime.pipeline_write_order` / `pipeline-walkthrough-checklist` §2.9
 */
export type TimelineLike = {
  eventName?: string;
  transitionTrigger?: string;
};

function indexOfEvent(events: TimelineLike[], name: string): number {
  return events.findIndex(
    (e) => e.eventName === name || e.transitionTrigger === name,
  );
}

/** 须满足：dispatched → spec_read → confirmation → user.confirmed → 写类事件 */
export function assertWritePathPipelineOrder(events: TimelineLike[]): void {
  const dispatched = indexOfEvent(events, "execution.dispatched");
  const spec = indexOfEvent(events, "agent.skill.spec_read");
  const confirm = indexOfEvent(events, "confirmation.required");
  const userOk = indexOfEvent(events, "user.confirmed");
  const write = events.findIndex(
    (e) =>
      e.transitionTrigger === "tool.round_complete" ||
      e.eventName === "tool.round_complete" ||
      e.transitionTrigger === "tool.final_failed" ||
      e.eventName === "tool.final_failed" ||
      e.transitionTrigger === "trading.exchange_private" ||
      e.eventName === "trading.exchange_private",
  );

  if (dispatched < 0) throw new Error("missing execution.dispatched");
  if (spec < 0) throw new Error("missing agent.skill.spec_read");
  if (confirm < 0) throw new Error("missing confirmation.required");
  if (userOk < 0) throw new Error("missing user.confirmed");
  if (write < 0) throw new Error("missing write-path tool event");

  if (spec <= dispatched) {
    throw new Error("agent.skill.spec_read must be after execution.dispatched");
  }
  if (confirm <= spec) {
    throw new Error("confirmation.required must be after agent.skill.spec_read");
  }
  if (userOk <= confirm) {
    throw new Error("user.confirmed must be after confirmation.required");
  }
  if (write <= userOk) {
    throw new Error("write tool event must be after user.confirmed");
  }
}
