import { Card, Timeline, Typography, theme } from "antd";
import { EXECUTION_DETAIL } from "../../copy/opsPanelHints";
import type { MockObsBillingRow, MockObsExecutionRow, MockObsLlmRow, MockObsToolRow } from "../../data/types";
import { zhCapabilitySku, zhEntitlementDebitStatus } from "../../copy/billingLabels";
import { zhExecutionOutcome } from "../../copy/zhLabels";

const { Text } = Typography;

function formatSignalTime(iso: string): string {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 19);
}

function shortToolLabel(toolId: string, pathSummary?: string): string {
  const path = pathSummary?.trim();
  if (path) return path;
  const tail = toolId.split(".").pop();
  return tail ?? toolId;
}

type Props = {
  exec: MockObsExecutionRow;
  tools: MockObsToolRow[];
  llms: MockObsLlmRow[];
  billing: MockObsBillingRow[];
  running: boolean;
  unknown: boolean;
  failed: boolean;
  endEventTime: string;
};

export function ExecutionDetailSignalTimeline({
  exec,
  tools,
  llms,
  billing,
  running,
  unknown,
  failed,
  endEventTime,
}: Props) {
  const { token } = theme.useToken();

  const items = [
    { label: EXECUTION_DETAIL.signalStart, time: exec.startedAt, color: "blue" as const },
    ...tools.map((t) => ({
      label: `${EXECUTION_DETAIL.signalTool} · ${shortToolLabel(t.toolId, t.pathSummary)}`,
      time: t.at,
      color: "gray" as const,
    })),
    ...llms.map((l) => ({
      label: `${EXECUTION_DETAIL.signalModel} · ${l.modelId}`,
      time: l.at,
      color: "green" as const,
    })),
    ...billing.map((b) => ({
      label: `${EXECUTION_DETAIL.signalBilling} · ${zhCapabilitySku(b.capabilitySkuId)}（${zhEntitlementDebitStatus(b.debitStatus)}）`,
      time: b.at,
      color:
        b.debitStatus === "INSUFFICIENT" || b.debitStatus === "FAILED"
          ? ("red" as const)
          : b.debitStatus === "AWAITING_FINAL"
            ? ("orange" as const)
            : ("gray" as const),
    })),
    {
      label: running
        ? `${EXECUTION_DETAIL.signalOutcomeRunning} · ${zhExecutionOutcome("RUNNING")}`
        : `${EXECUTION_DETAIL.signalOutcomeFinal} · ${zhExecutionOutcome(exec.outcome)}`,
      time: endEventTime,
      color: unknown ? ("red" as const) : failed ? ("red" as const) : running ? ("blue" as const) : ("green" as const),
    },
  ].sort((a, b) => String(a.time).localeCompare(String(b.time)));

  return (
    <Card size="small" className="admin-panel-card" title={EXECUTION_DETAIL.signalTimelineTitle}>
      <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 12 }}>
        {EXECUTION_DETAIL.signalTimelineIntro}
      </Text>
      <Timeline
        items={items.map((it) => ({
          color: it.color,
          children: (
            <>
              <Text strong style={{ fontSize: 13 }}>
                {it.label}
              </Text>
              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {formatSignalTime(it.time)}
                </Text>
              </div>
            </>
          ),
        }))}
        style={{ marginTop: 4, paddingTop: 4, borderTop: `1px solid ${token.colorBorderSecondary}` }}
      />
    </Card>
  );
}
