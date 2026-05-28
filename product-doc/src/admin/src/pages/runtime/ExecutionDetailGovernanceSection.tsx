import { Card, Collapse } from "antd";
import type { MockObsTimelineEventRow, MockResolvedPromptBinding } from "../../data/types";
import { EXECUTION_DETAIL } from "../../copy/opsPanelHints";
import { ExecutionCanonicalInspector } from "./ExecutionCanonicalInspector";
import { ExecutionPromptAssemblyTrace } from "./ExecutionPromptAssemblyTrace";
import { ExecutionScenarioSkillScope } from "./ExecutionScenarioSkillScope";
import { SkillSpecReadSummary } from "./SkillSpecReadSummary";

type Props = {
  executionId: string;
  scenarioId: string;
  sessionId: string;
  outcome?: string;
  resolvedPromptBinding?: MockResolvedPromptBinding;
  timelineEvents?: MockObsTimelineEventRow[];
};

/** 执行详情总览 · 治理四块（折叠，默认展开前两项） */
export function ExecutionDetailGovernanceSection({
  executionId,
  scenarioId,
  sessionId,
  outcome,
  resolvedPromptBinding,
  timelineEvents,
}: Props) {
  return (
    <Card size="small" className="admin-panel-card" title={EXECUTION_DETAIL.governanceSectionTitle}>
      <Collapse
        ghost
        defaultActiveKey={["skill-scope", "prompt"]}
        items={[
          {
            key: "skill-scope",
            label: EXECUTION_DETAIL.governanceSkillScope,
            children: <ExecutionScenarioSkillScope scenarioId={scenarioId} embedded />,
          },
          {
            key: "prompt",
            label: EXECUTION_DETAIL.governancePrompt,
            children: (
              <ExecutionPromptAssemblyTrace
                embedded
                executionId={executionId}
                scenarioId={scenarioId}
                sessionId={sessionId}
                resolvedPromptBinding={resolvedPromptBinding}
                timelineEvents={timelineEvents}
              />
            ),
          },
          {
            key: "skill-spec",
            label: EXECUTION_DETAIL.governanceSkillSpec,
            children: (
              <SkillSpecReadSummary scenarioId={scenarioId} timelineEvents={timelineEvents} embedded />
            ),
          },
          {
            key: "canonical",
            label: EXECUTION_DETAIL.governanceCanonical,
            children: (
              <ExecutionCanonicalInspector
                embedded
                executionId={executionId}
                scenarioId={scenarioId}
                outcome={outcome ?? ""}
                timelineEvents={timelineEvents}
              />
            ),
          },
        ]}
      />
    </Card>
  );
}
