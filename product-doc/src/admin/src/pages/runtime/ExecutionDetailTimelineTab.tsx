import { Card, Space, Steps, Typography } from "antd";
import { EXECUTION_DETAIL } from "../../copy/opsPanelHints";
import type { MockObsTimelineEventRow } from "../../data/types";
import { zhExecutionStage } from "../../copy/zhLabels";
import { Mc801TimelineAudit } from "./Mc801TimelineAudit";
import { ExecutionDetailSignalTimeline } from "./ExecutionDetailSignalTimeline";
import type { MockObsBillingRow, MockObsExecutionRow, MockObsLlmRow, MockObsToolRow } from "../../data/types";

const { Text } = Typography;

type Props = {
  exec: MockObsExecutionRow;
  displayMc801Events?: MockObsTimelineEventRow[];
  mc801Loading: boolean;
  mc801EmptyPresentation: "api-table" | "mock-alert";
  stageCurrent: number;
  tools: MockObsToolRow[];
  llms: MockObsLlmRow[];
  billing: MockObsBillingRow[];
  running: boolean;
  unknown: boolean;
  failed: boolean;
  endEventTime: string;
};

export function ExecutionDetailTimelineTab({
  exec,
  displayMc801Events,
  mc801Loading,
  mc801EmptyPresentation,
  stageCurrent,
  tools,
  llms,
  billing,
  running,
  unknown,
  failed,
  endEventTime,
}: Props) {
  return (
    <Space direction="vertical" size="middle" style={{ width: "100%" }}>
      <Mc801TimelineAudit
        timelineEvents={displayMc801Events}
        loading={mc801Loading}
        emptyPresentation={mc801EmptyPresentation}
      />

      <Card size="small" className="admin-panel-card" title={EXECUTION_DETAIL.stepsCardTitle}>
        <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 12 }}>
          {EXECUTION_DETAIL.stepsIntro}
        </Text>
        <Steps size="small" current={stageCurrent} items={exec.stageTimeline.map((s) => ({ title: zhExecutionStage(s) }))} />
      </Card>

      <ExecutionDetailSignalTimeline
        exec={exec}
        tools={tools}
        llms={llms}
        billing={billing}
        running={running}
        unknown={unknown}
        failed={failed}
        endEventTime={endEventTime}
      />
    </Space>
  );
}
