import { Card, Descriptions, Tag, Typography, theme } from "antd";
import { Link } from "react-router-dom";
import { OpsHintAlert } from "../../components/OpsHintAlert";
import { EXECUTION_SKILL_SPEC, formatOpsEventRef } from "../../copy/opsPanelHints";
import type { MockObsTimelineEventRow } from "../../data/types";
import { parseSkillSpecReadFromTimeline } from "../../productionRuntime/skillSpecTimeline";

const { Text } = Typography;

function phaseTag(phase: "success" | "fail") {
  if (phase === "success") return <Tag color="success">已加载</Tag>;
  return <Tag color="error">加载失败</Tag>;
}

export type SkillSpecReadSummaryProps = {
  scenarioId: string;
  timelineEvents?: MockObsTimelineEventRow[];
  embedded?: boolean;
};

export function SkillSpecReadSummary({ scenarioId, timelineEvents, embedded = false }: SkillSpecReadSummaryProps) {
  const { token } = theme.useToken();
  const read = parseSkillSpecReadFromTimeline(timelineEvents);

  if (!read) {
    const empty = embedded ? (
      <Text type="secondary" style={{ fontSize: 12 }}>
        {EXECUTION_SKILL_SPEC.emptyMessage}（场景 <Text code>{scenarioId}</Text>）
      </Text>
    ) : (
      <OpsHintAlert
        type="info"
        showIcon
        message={EXECUTION_SKILL_SPEC.emptyMessage}
        description={
          <span>
            {EXECUTION_SKILL_SPEC.emptyDescription} 当前场景：<Text code>{scenarioId}</Text>
          </span>
        }
        technicalDetail={formatOpsEventRef("skillSpecRead")}
      />
    );
    if (embedded) return empty;
    return (
      <Card size="small" className="admin-panel-card" title={EXECUTION_SKILL_SPEC.cardTitle}>
        {empty}
      </Card>
    );
  }

  const descriptions = (
    <Descriptions
      bordered
      size="small"
      column={{ xs: 1, sm: 2 }}
      styles={{ label: { width: 128, color: token.colorTextSecondary } }}
    >
      <Descriptions.Item label={EXECUTION_SKILL_SPEC.labelSkillId}>
        <Text code>{read.skillId}</Text>
      </Descriptions.Item>
      <Descriptions.Item label={EXECUTION_SKILL_SPEC.labelVersion}>{read.skillSpecVersion}</Descriptions.Item>
      <Descriptions.Item label={EXECUTION_SKILL_SPEC.labelReadResult}>{phaseTag(read.phase)}</Descriptions.Item>
      <Descriptions.Item label={EXECUTION_SKILL_SPEC.labelDigest}>
        {read.specDigest ? (
          <Text code copyable>
            {read.specDigest}
          </Text>
        ) : (
          <Text type="secondary">—</Text>
        )}
      </Descriptions.Item>
      {!embedded ? (
        <Descriptions.Item label={EXECUTION_SKILL_SPEC.labelObsEvent} span={2}>
          {formatOpsEventRef("skillSpecRead")}
          <Text type="secondary"> · {EXECUTION_SKILL_SPEC.obsEventSuffix}</Text>
        </Descriptions.Item>
      ) : null}
    </Descriptions>
  );

  if (embedded) {
    return (
      <>
        <div style={{ marginBottom: 8, textAlign: "right" }}>
          <Link to="/ai/tool-registry">{EXECUTION_SKILL_SPEC.registryLink}</Link>
        </div>
        {descriptions}
      </>
    );
  }

  return (
    <Card
      size="small"
      className="admin-panel-card"
      title={EXECUTION_SKILL_SPEC.cardTitle}
      extra={<Link to="/ai/tool-registry">{EXECUTION_SKILL_SPEC.registryLink}</Link>}
    >
      {descriptions}
    </Card>
  );
}
