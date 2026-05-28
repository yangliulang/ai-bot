import { Card, Descriptions, Space, Table, Tag, Typography, theme } from "antd";
import { OpsHintAlert } from "../../components/OpsHintAlert";
import { EXECUTION_CANONICAL } from "../../copy/opsPanelHints";
import type { MockObsExecutionRow, MockObsTimelineEventRow } from "../../data/types";
import { buildExecutionCanonicalInspect } from "../../productionRuntime/executionCanonicalInspector";

const { Text } = Typography;

type Props = Pick<MockObsExecutionRow, "executionId" | "scenarioId" | "outcome"> & {
  timelineEvents?: MockObsTimelineEventRow[];
  embedded?: boolean;
};

export function ExecutionCanonicalInspector({
  executionId,
  scenarioId,
  outcome,
  timelineEvents,
  embedded = false,
}: Props) {
  const { token } = theme.useToken();
  const view = buildExecutionCanonicalInspect({ executionId, scenarioId, outcome, timelineEvents });

  const body = (
    <Space direction="vertical" size={12} style={{ width: "100%" }}>
      {embedded ? (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {EXECUTION_CANONICAL.alertMessage} · {view.note}
        </Text>
      ) : (
        <OpsHintAlert
          type="info"
          showIcon
          message={EXECUTION_CANONICAL.alertMessage}
          description={<Text style={{ fontSize: 12 }}>{view.note}</Text>}
        />
      )}

      {!view.applicable ? (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {EXECUTION_CANONICAL.notApplicable}
        </Text>
      ) : (
        <>
          <Descriptions
            bordered
            size="small"
            column={{ xs: 1, sm: 2 }}
            styles={{ label: { width: 120, color: token.colorTextSecondary } }}
          >
            <Descriptions.Item label={EXECUTION_CANONICAL.labelCanonicalOp}>
              <Text code>{view.canonicalOp ?? "—"}</Text>
            </Descriptions.Item>
            <Descriptions.Item label={EXECUTION_CANONICAL.labelSkillId}>
              <Text code>{view.skillId ?? "—"}</Text>
            </Descriptions.Item>
            <Descriptions.Item label={EXECUTION_CANONICAL.labelGateway} span={2}>
              {view.barrierOk === true ? (
                <Tag color="success">{EXECUTION_CANONICAL.gatewayPass}</Tag>
              ) : view.barrierOk === false ? (
                <Space direction="vertical" size={0}>
                  <Tag color="error">{view.barrierCode ?? "BLOCKED"}</Tag>
                  <Text type="secondary" style={{ fontSize: 11 }}>
                    {view.barrierMessage}
                  </Text>
                </Space>
              ) : (
                <Tag color="warning">{view.barrierCode ?? "待定"}</Tag>
              )}
            </Descriptions.Item>
          </Descriptions>

          <div>
            <Text strong style={{ fontSize: 12, display: "block", marginBottom: 6 }}>
              {EXECUTION_CANONICAL.payloadTitle}
            </Text>
            <pre
              style={{
                margin: 0,
                padding: 10,
                fontSize: 11,
                background: token.colorFillAlter,
                borderRadius: token.borderRadius,
                overflow: "auto",
              }}
            >
              {JSON.stringify(view.canonicalPayload, null, 2)}
            </pre>
          </div>

          {view.confirmationSnapshot ? (
            <div>
              <Text strong style={{ fontSize: 12, display: "block", marginBottom: 6 }}>
                {EXECUTION_CANONICAL.confirmationTitle}
              </Text>
              <pre
                style={{
                  margin: 0,
                  padding: 10,
                  fontSize: 11,
                  background: token.colorFillAlter,
                  borderRadius: token.borderRadius,
                  overflow: "auto",
                }}
              >
                {JSON.stringify(view.confirmationSnapshot, null, 2)}
              </pre>
            </div>
          ) : null}

          {view.provenance.length > 0 ? (
            <Table
              size="small"
              pagination={false}
              rowKey="field"
              title={() => <Text style={{ fontSize: 12 }}>{EXECUTION_CANONICAL.provenanceTitle}</Text>}
              columns={[
                { title: EXECUTION_CANONICAL.colField, dataIndex: "field", width: 120 },
                {
                  title: EXECUTION_CANONICAL.colSource,
                  dataIndex: "source",
                  render: (s: string) => <Text code>{s}</Text>,
                },
              ]}
              dataSource={view.provenance}
            />
          ) : null}
        </>
      )}
    </Space>
  );

  if (embedded) return body;

  return (
    <Card size="small" className="admin-panel-card" title={EXECUTION_CANONICAL.cardTitle}>
      {body}
    </Card>
  );
}
