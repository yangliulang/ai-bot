import { Card, Empty, Spin, Table } from "antd";
import { MC801_TIMELINE } from "../../copy/opsPanelHints";
import type { MockObsTimelineEventRow } from "../../data/types";
import { buildMc801TimelineColumns } from "./mc801TimelineDisplay";

export { formatMc801DisplayTime } from "./mc801TimelineDisplay";

export type Mc801TimelineAuditProps = {
  timelineEvents?: MockObsTimelineEventRow[];
  /** 默认带 Card；抽屉内可用 plain 避免双层卡片感 */
  variant?: "card" | "plain";
  cardTitle?: string;
  loading?: boolean;
  emptyPresentation?: "api-table" | "mock-alert";
};

export function Mc801TimelineAudit({
  timelineEvents,
  variant = "card",
  cardTitle = MC801_TIMELINE.cardTitle,
  loading = false,
  emptyPresentation = "mock-alert",
}: Mc801TimelineAuditProps) {
  const cols = buildMc801TimelineColumns();

  const inner = loading ? (
    <div style={{ padding: "24px 0", textAlign: "center" }}>
      <Spin />
    </div>
  ) : timelineEvents?.length ? (
    <Table
      size="small"
      rowKey={(r, i) => `${r.at}-${r.eventName ?? ""}-${i}`}
      columns={cols}
      dataSource={timelineEvents}
      pagination={false}
      locale={{ emptyText: MC801_TIMELINE.tableEmpty }}
      scroll={{ x: 900 }}
    />
  ) : emptyPresentation === "api-table" ? (
    <Table
      size="small"
      rowKey={() => "empty"}
      columns={cols}
      dataSource={[]}
      pagination={false}
      locale={{ emptyText: MC801_TIMELINE.emptyApiTable }}
      scroll={{ x: 900 }}
    />
  ) : (
    <Empty
      image={Empty.PRESENTED_IMAGE_SIMPLE}
      description={MC801_TIMELINE.emptyMessage}
      styles={{ description: { fontSize: 13 } }}
    />
  );

  const body = inner;

  if (variant === "plain") {
    return body;
  }

  return (
    <Card size="small" className="admin-panel-card" title={cardTitle}>
      {body}
    </Card>
  );
}
