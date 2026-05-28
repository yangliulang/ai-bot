import { Space, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { ReactNode } from "react";
import {
  labelMc801Event,
  labelMc801SummaryText,
  labelMc801TransitionTrigger,
  MC801_TIMELINE,
} from "../../copy/opsPanelHints";
import type { MockObsTimelineEventRow } from "../../data/types";
import { SKILL_SPEC_READ_EVENT } from "../../productionRuntime/skillSpecTimeline";

const { Text } = Typography;

export function formatMc801DisplayTime(iso: string): string {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 19);
}

function codeFootnote(code: string, label: string): ReactNode {
  if (code === label) return null;
  return (
    <Text type="secondary" code style={{ fontSize: 10 }}>
      {code}
    </Text>
  );
}

export function renderMc801EventCell(v: string | undefined, row: MockObsTimelineEventRow): ReactNode {
  if (!v) return <Text type="secondary">—</Text>;
  const label = labelMc801Event(v);
  if (v === SKILL_SPEC_READ_EVENT) {
    const phase = row.skillSpecRead?.phase;
    return (
      <Space direction="vertical" size={0}>
        <Text style={{ fontSize: 12 }}>{label}</Text>
        {phase === "fail" ? (
          <Text type="danger" style={{ fontSize: 11 }}>
            载入失败
          </Text>
        ) : null}
        {codeFootnote(v, label)}
      </Space>
    );
  }
  return (
    <Space direction="vertical" size={0}>
      <Text style={{ fontSize: 12 }}>{label}</Text>
      {codeFootnote(v, label)}
    </Space>
  );
}

export function renderMc801TriggerCell(v: string | undefined): ReactNode {
  if (!v) return <Text type="secondary">—</Text>;
  const label = labelMc801TransitionTrigger(v);
  return (
    <Space direction="vertical" size={0}>
      <Text style={{ fontSize: 12 }}>{label}</Text>
      {codeFootnote(v, label)}
    </Space>
  );
}

export function renderMc801SummaryCell(row: MockObsTimelineEventRow): ReactNode {
  if (row.promptBindingResolved) {
    return <Text style={{ fontSize: 12 }}>{MC801_TIMELINE.summaryPromptBinding}</Text>;
  }
  if (row.skillSpecRead) {
    const { skillId, skillSpecVersion, phase } = row.skillSpecRead;
    const lead =
      phase === "fail" ? MC801_TIMELINE.summarySkillSpecFail : MC801_TIMELINE.summarySkillSpecOk;
    return (
      <Text style={{ fontSize: 12 }}>
        {lead} · <Text code>{skillId}</Text> @ {skillSpecVersion}
      </Text>
    );
  }
  const raw = row.summary?.trim();
  if (!raw) return <Text type="secondary">—</Text>;
  const label = labelMc801SummaryText(raw);
  if (label !== raw) {
    return (
      <Space direction="vertical" size={0}>
        <Text style={{ fontSize: 12 }}>{label}</Text>
        {codeFootnote(raw, label)}
      </Space>
    );
  }
  return <Text style={{ fontSize: 12 }}>{raw}</Text>;
}

export function buildMc801TimelineColumns(): ColumnsType<MockObsTimelineEventRow> {
  return [
    {
      title: MC801_TIMELINE.colTime,
      dataIndex: "at",
      width: 176,
      render: (t: string) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {formatMc801DisplayTime(t)}
        </Text>
      ),
    },
    {
      title: MC801_TIMELINE.colEvent,
      dataIndex: "eventName",
      width: 200,
      render: (v: string | undefined, row) => renderMc801EventCell(v, row),
    },
    {
      title: MC801_TIMELINE.colSummary,
      dataIndex: "summary",
      ellipsis: true,
      render: (_: string | undefined, row) => renderMc801SummaryCell(row),
    },
    {
      title: MC801_TIMELINE.colTrigger,
      dataIndex: "transitionTrigger",
      width: 168,
      render: (v: string | undefined) => renderMc801TriggerCell(v),
    },
  ];
}
