import { Card, Descriptions, Space, Tag, Typography, theme } from "antd";
import { Link } from "react-router-dom";
import { OpsHintAlert } from "../../components/OpsHintAlert";
import { EXECUTION_PROMPT_TRACE } from "../../copy/opsPanelHints";
import type { MockObsTimelineEventRow, MockResolvedPromptBinding } from "../../data/types";
import {
  PROMPT_BINDING_RESOLVED_EVENT,
  bindingToAssemblyLayers,
  isAnalysisStrategyBinding,
  resolvePromptBindingForExecution,
} from "../../productionRuntime/promptBindingTimeline";
import { PromptAssemblyTraceTable } from "../prompt/PromptAssemblyTraceTable";
import { promptPackEditorPath } from "../prompt/promptPaths";

const { Text } = Typography;

export type ExecutionPromptAssemblyTraceProps = {
  executionId: string;
  scenarioId: string;
  sessionId: string;
  resolvedPromptBinding?: MockResolvedPromptBinding;
  timelineEvents?: MockObsTimelineEventRow[];
  embedded?: boolean;
};

/**
 * 执行详情 · Prompt 拼装追溯（SC-PM-22 / SC-OBS04）
 */
export function ExecutionPromptAssemblyTrace({
  executionId,
  scenarioId,
  sessionId,
  resolvedPromptBinding,
  timelineEvents,
  embedded = false,
}: ExecutionPromptAssemblyTraceProps) {
  const { token } = theme.useToken();
  const binding = resolvePromptBindingForExecution({
    scenarioId,
    sessionId,
    resolvedPromptBinding,
    timelineEvents,
  });
  const layers = bindingToAssemblyLayers(binding);
  const fromTimeline = timelineEvents?.some(
    (e) => e.eventName === PROMPT_BINDING_RESOLVED_EVENT || e.promptBindingResolved,
  );

  const sourceHint = fromTimeline
    ? EXECUTION_PROMPT_TRACE.sourceFromTimeline
    : resolvedPromptBinding
      ? EXECUTION_PROMPT_TRACE.sourceFromSummary
      : EXECUTION_PROMPT_TRACE.sourceInferred;

  const body = (
    <Space direction="vertical" size={12} style={{ width: "100%" }}>
      {embedded ? (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {EXECUTION_PROMPT_TRACE.alertMessage} · {sourceHint}
        </Text>
      ) : (
        <OpsHintAlert
          type="info"
          showIcon
          message={EXECUTION_PROMPT_TRACE.alertMessage}
          description={
            <span>
              {sourceHint}。{EXECUTION_PROMPT_TRACE.skillSpecCrossLink}
            </span>
          }
        />
      )}

        <Descriptions
          bordered
          size="small"
          column={{ xs: 1, sm: 2 }}
          styles={{ label: { width: 120, color: token.colorTextSecondary } }}
        >
          <Descriptions.Item label="执行 ID">
            <Text code>{executionId}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="场景键">
            <Text code>{binding.scenarioId}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="场景策略包" span={2}>
            {binding.tradingPromptPackId ? (
              <Link to={promptPackEditorPath(binding.tradingPromptPackId)}>
                <Text code>
                  {binding.tradingPromptPackId}
                  {binding.tradingPromptPackVersion != null ? `@v${binding.tradingPromptPackVersion}` : ""}
                </Text>
              </Link>
            ) : (
              <Text type="secondary">—</Text>
            )}
            {isAnalysisStrategyBinding(binding) ? (
              <Tag style={{ marginLeft: 8 }}>分析槽</Tag>
            ) : (
              <Tag style={{ marginLeft: 8 }}>场景槽</Tag>
            )}
          </Descriptions.Item>
          {binding.fewShotDigest ? (
            <Descriptions.Item label="示例集摘要" span={2}>
              <Text code copyable>
                {binding.fewShotDigest}
              </Text>
            </Descriptions.Item>
          ) : null}
        </Descriptions>

        <PromptAssemblyTraceTable rows={layers} />
      </Space>
  );

  if (embedded) {
    return (
      <>
        <div style={{ marginBottom: 8, textAlign: "right" }}>
          <Link to="/ai/prompt-strategy">提示词治理</Link>
        </div>
        {body}
      </>
    );
  }

  return (
    <Card
      size="small"
      className="admin-panel-card"
      title={EXECUTION_PROMPT_TRACE.cardTitle}
      extra={<Link to="/ai/prompt-strategy">提示词治理</Link>}
    >
      {body}
    </Card>
  );
}
