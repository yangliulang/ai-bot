import { Alert, Card, Space, Table, Tag, Typography } from "antd";
import { Link } from "react-router-dom";
import { PROMPT_PUBLISH_REJECT } from "../../copy/opsPanelHints";
import type { PromptPublishGateTrace, PromptPublishRejection } from "./promptPublishRejectTrace";

const { Text } = Typography;

function formatCheckedAt(iso: string): string {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 19);
}

export function PromptPublishRejectTraceTable({ rejections }: { rejections: PromptPublishRejection[] }) {
  return (
    <Table
      size="small"
      pagination={false}
      rowKey={(r) => `${r.code}-${r.gate}`}
      columns={[
        {
          title: PROMPT_PUBLISH_REJECT.colCheck,
          dataIndex: "title",
          width: 120,
          ellipsis: true,
        },
        {
          title: PROMPT_PUBLISH_REJECT.colCode,
          dataIndex: "code",
          width: 168,
          render: (code: string) => (
            <Text code style={{ fontSize: 11 }}>
              {code}
            </Text>
          ),
        },
        {
          title: PROMPT_PUBLISH_REJECT.colDetail,
          dataIndex: "detail",
          ellipsis: true,
        },
        {
          title: PROMPT_PUBLISH_REJECT.colFix,
          dataIndex: "remediation",
          ellipsis: true,
          render: (v: string | undefined, row: PromptPublishRejection) => {
            if (!v) return <Text type="secondary">—</Text>;
            if (row.gate === "skill_scope") {
              return (
                <Space direction="vertical" size={4}>
                  <Text style={{ fontSize: 12 }}>{v}</Text>
                  <Link to="/ai/tool-registry">技能与工具登记册</Link>
                </Space>
              );
            }
            if (row.gate === "scenario") {
              return (
                <Space direction="vertical" size={4}>
                  <Text style={{ fontSize: 12 }}>{v}</Text>
                  <Link to="/ai/runtime-orchestration?tab=routing">运行场景目录</Link>
                </Space>
              );
            }
            return <Text style={{ fontSize: 12 }}>{v}</Text>;
          },
        },
      ]}
      dataSource={rejections}
    />
  );
}

type Props = {
  trace: PromptPublishGateTrace | null;
  loading?: boolean;
  compact?: boolean;
  title?: string;
};

export function PromptPublishRejectTrace({ trace, loading = false, compact = false, title }: Props) {
  if (!trace && !loading) return null;

  const cardTitle = title ?? PROMPT_PUBLISH_REJECT.traceCardTitle;

  if (loading) {
    return (
      <Card size="small" className="admin-panel-card" title={cardTitle} loading>
        <div style={{ minHeight: 48 }} />
      </Card>
    );
  }

  if (!trace) return null;

  if (trace.ok) {
    return (
      <Alert
        type="success"
        showIcon
        style={{ marginBottom: compact ? 8 : 12 }}
        message={compact ? PROMPT_PUBLISH_REJECT.preflightOkCompact : PROMPT_PUBLISH_REJECT.preflightOk}
        description={
          <Text type="secondary" style={{ fontSize: 12 }}>
            检查于 {formatCheckedAt(trace.checkedAt)} · {PROMPT_PUBLISH_REJECT.preflightOkDetail}
          </Text>
        }
      />
    );
  }

  return (
    <Card
      size="small"
      className="admin-panel-card"
      style={{ marginBottom: compact ? 8 : 12 }}
      title={
        <Space>
          <span>{cardTitle}</span>
          <Tag color="error">{trace.rejections.length} 项未通过</Tag>
        </Space>
      }
      extra={
        <Text type="secondary" style={{ fontSize: 11 }}>
          {formatCheckedAt(trace.checkedAt)}
        </Text>
      }
    >
      <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 12 }}>
        {PROMPT_PUBLISH_REJECT.blockedLead}
      </Text>
      <PromptPublishRejectTraceTable rejections={trace.rejections} />
    </Card>
  );
}
