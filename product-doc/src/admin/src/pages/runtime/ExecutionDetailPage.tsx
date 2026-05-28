import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Collapse,
  Descriptions,
  Empty,
  Progress,
  Spin,
  Space,
  Table,
  Tabs,
  Tag,
  Typography,
  theme,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { ProductPageShell } from "../../components/product";
import { useOrchestrationPolicy } from "../../context/OrchestrationPolicyContext";
import {
  getObsExecution,
  getObsToolRowsForExecution,
  getRuntimeEventsForExecution,
  getRuntimeTasksForExecution,
  mockObsBilling,
  mockObsLlms,
} from "../../data/mock";
import type {
  MockObsExecutionRow,
  MockObsLlmRow,
  MockObsTimelineEventRow,
  MockObsToolRow,
  MockRuntimeEventRow,
  MockRuntimeTask,
} from "../../data/types";
import {
  buildMinimalExecFromApiTimeline,
  fetchObservabilityExecutions,
  fetchObservabilityExecutionTimeline,
  isObservabilityApiEnabled,
} from "../../api/observabilityExecutions";
import { FAILURE_STOP_POLICY_LABEL } from "../governance/orchestration/executionPolicyModel";
import { MOCK_SCENARIO_REGISTRY } from "../governance/orchestration/scenarioRegistryMock";
import { ExecutionDetailBillingMirror } from "./ExecutionDetailBillingMirror";
import { ExecutionDetailGovernanceSection } from "./ExecutionDetailGovernanceSection";
import { ExecutionDetailTimelineTab } from "./ExecutionDetailTimelineTab";
import { ExecutionDetailUsageTabs } from "./ExecutionDetailUsageTabs";
import { obsBillingColumns } from "../billing/obsBillingColumns";
import { EXECUTION_DETAIL } from "../../copy/opsPanelHints";
import { buildObservabilitySearch } from "../../utils/observabilityDeepLink";
import {
  zhExecutionOutcome,
  zhExecutionRuntimeStatus,
  zhExecutionStage,
  zhRuntimeEventType,
  zhTaskState,
  zhToolInvocation,
} from "../../copy/zhLabels";

const { Text } = Typography;

const DETAIL_TAB_KEYS = ["overview", "timeline", "queue", "events", "retries", "recovery"] as const;
type DetailTabKey = (typeof DETAIL_TAB_KEYS)[number];

function isDetailTab(k: string): k is DetailTabKey {
  return (DETAIL_TAB_KEYS as readonly string[]).includes(k);
}

function isoAddMs(iso: string, ms: number): string {
  const d = new Date(iso);
  d.setTime(d.getTime() + ms);
  return d.toISOString().replace(/\.\d{3}Z$/, "Z");
}

function formatExecTime(iso: string): string {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 19);
}

function runtimeStatusTag(status: string) {
  const label = zhExecutionRuntimeStatus(status);
  if (status === "COMPLETED") return <Tag color="success">{label}</Tag>;
  if (status === "RUNNING") return <Tag color="processing">{label}</Tag>;
  if (status === "UNKNOWN") return <Tag color="warning">{label}</Tag>;
  if (status === "FAILED" || status === "BLOCKED") return <Tag color="error">{label}</Tag>;
  if (status === "CREATED") return <Tag color="default">{label}</Tag>;
  return <Tag>{label}</Tag>;
}

export function ExecutionDetailPage() {
  const { token } = theme.useToken();
  const { executionId } = useParams<{ executionId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const { effectivePolicy } = useOrchestrationPolicy();
  const rawTab = searchParams.get("tab") ?? "overview";
  const activeTab: DetailTabKey = isDetailTab(rawTab) ? rawTab : "overview";

  const [apiTimeline, setApiTimeline] = useState<MockObsTimelineEventRow[]>([]);
  const [timelineReady, setTimelineReady] = useState(false);
  const [timelineFailed, setTimelineFailed] = useState(false);
  const [apiSummary, setApiSummary] = useState<MockObsExecutionRow | undefined>(undefined);
  const [summaryReady, setSummaryReady] = useState(false);

  useEffect(() => {
    if (!executionId) {
      setApiTimeline([]);
      setTimelineReady(false);
      setTimelineFailed(false);
      setApiSummary(undefined);
      setSummaryReady(false);
      return;
    }
    if (!isObservabilityApiEnabled()) {
      setApiTimeline([]);
      setTimelineReady(true);
      setTimelineFailed(false);
      setApiSummary(undefined);
      setSummaryReady(true);
      return;
    }

    let cancelled = false;
    setApiTimeline([]);
    setTimelineReady(false);
    setTimelineFailed(false);
    setApiSummary(undefined);

    const mockRow = getObsExecution(executionId);
    if (mockRow) {
      setSummaryReady(true);
    } else {
      setSummaryReady(false);
      fetchObservabilityExecutions({ executionId, pageSize: 1 })
        .then((page) => {
          if (!cancelled) setApiSummary(page.items[0]);
        })
        .catch(() => {
          if (!cancelled) setApiSummary(undefined);
        })
        .finally(() => {
          if (!cancelled) setSummaryReady(true);
        });
    }

    fetchObservabilityExecutionTimeline(executionId)
      .then((rows) => {
        if (!cancelled) {
          setApiTimeline(rows);
          setTimelineFailed(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setApiTimeline([]);
          setTimelineFailed(true);
        }
      })
      .finally(() => {
        if (!cancelled) setTimelineReady(true);
      });

    return () => {
      cancelled = true;
    };
  }, [executionId]);

  const execMock = executionId ? getObsExecution(executionId) : undefined;
  const exec = useMemo(() => {
    if (!executionId) return undefined;
    if (execMock) return execMock;
    if (!isObservabilityApiEnabled()) return undefined;
    if (apiSummary) return apiSummary;
    if (apiTimeline.length > 0) return buildMinimalExecFromApiTimeline(executionId, apiTimeline);
    return undefined;
  }, [executionId, execMock, apiSummary, apiTimeline]);

  const stillLoading = Boolean(
    executionId && isObservabilityApiEnabled() && !execMock && (!summaryReady || !timelineReady),
  );

  const displayMc801Events = useMemo(() => {
    if (!exec) return undefined;
    if (!isObservabilityApiEnabled() || !timelineReady) return exec.timelineEvents;
    if (timelineFailed) return exec.timelineEvents;
    if (apiTimeline.length > 0) return apiTimeline;
    return exec.timelineEvents;
  }, [exec, apiTimeline, timelineReady, timelineFailed]);

  const mc801EmptyPresentation =
    isObservabilityApiEnabled() && timelineReady && !timelineFailed ? ("api-table" as const) : ("mock-alert" as const);

  const tools = useMemo(() => (exec ? getObsToolRowsForExecution(exec.executionId) : []), [exec]);
  const llms = useMemo(
    () => (exec ? mockObsLlms.filter((l) => l.executionId === exec.executionId) : []),
    [exec],
  );
  const billing = useMemo(
    () => (exec ? mockObsBilling.filter((b) => b.executionId === exec.executionId) : []),
    [exec],
  );
  const tasks = useMemo(() => (exec ? getRuntimeTasksForExecution(exec.executionId) : []), [exec]);
  const runtimeEvents = useMemo(() => (exec ? getRuntimeEventsForExecution(exec.executionId) : []), [exec]);

  const toolCallCountForBudget = tools.length;
  const maxTools = Math.max(1, effectivePolicy.maxToolCalls);
  const budgetRatioPct = Math.min(100, Math.round((toolCallCountForBudget / maxTools) * 100));
  const budgetWouldExceed = toolCallCountForBudget > effectivePolicy.maxToolCalls;

  const retryRows = useMemo(() => {
    if (!exec || exec.retries <= 0) return [];
    return Array.from({ length: exec.retries }, (_, i) => ({
      key: String(i + 1),
      attempt: i + 1,
      at: isoAddMs(exec.createdAt, (i + 1) * 1300),
      reason:
        exec.status === "UNKNOWN" && i === exec.retries - 1
          ? EXECUTION_DETAIL.retryReconcile
          : EXECUTION_DETAIL.retryTransient,
    }));
  }, [exec]);

  if (stillLoading) {
    return (
      <ProductPageShell
        pageId="runtime.execution-detail"
        showPageId={false}
        title={EXECUTION_DETAIL.pageTitle}
        showFreshnessBar={false}
      >
        <div style={{ padding: 48, textAlign: "center" }}>
          <Spin size="large" />
        </div>
      </ProductPageShell>
    );
  }

  if (!exec) {
    return (
      <ProductPageShell
        pageId="runtime.execution-detail"
        showPageId={false}
        title={EXECUTION_DETAIL.pageTitle}
        showFreshnessBar={false}
      >
        <Empty
          description={
            executionId ? `${EXECUTION_DETAIL.notFound} · ${executionId}` : EXECUTION_DETAIL.missingId
          }
        >
          <Link to="/runtime/executions">
            <Button type="primary">返回执行记录</Button>
          </Link>
        </Empty>
      </ProductPageShell>
    );
  }

  const unknown = exec.outcome === "UNKNOWN";
  const failed = exec.outcome === "FAILED";
  const running = exec.outcome === "RUNNING";

  const endEventTime =
    running
      ? isoAddMs(exec.startedAt, 1)
      : exec.durationMs > 0
        ? isoAddMs(exec.startedAt, exec.durationMs)
        : exec.startedAt;

  const obsHref = `/observability${buildObservabilitySearch({
    executionId: exec.executionId,
    userId: exec.userIdMasked,
    tab: "tool",
  })}`;

  const stageCurrent = Math.max(
    0,
    exec.stageTimeline.indexOf(exec.currentStage) >= 0
      ? exec.stageTimeline.indexOf(exec.currentStage)
      : exec.stageTimeline.length - 1,
  );

  const toolCols: ColumnsType<MockObsToolRow> = [
    { title: "序号", dataIndex: "toolCallSeq", width: 64 },
    { title: "工具 ID", dataIndex: "toolId", ellipsis: true, render: (id: string) => <Text code>{id}</Text> },
    { title: "调用结果", dataIndex: "invocationState", width: 100, render: (s: string) => zhToolInvocation(s) },
    { title: "路径摘要", dataIndex: "pathSummary", ellipsis: true },
    {
      title: "时间",
      dataIndex: "at",
      width: 172,
      render: (t: string) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {formatExecTime(t)}
        </Text>
      ),
    },
  ];

  const llmCols: ColumnsType<MockObsLlmRow> = [
    { title: "模型", dataIndex: "modelId", render: (id: string) => <Text code>{id}</Text> },
    { title: "输入 Token", dataIndex: "inputTokens", width: 96, align: "right" as const },
    { title: "输出 Token", dataIndex: "outputTokens", width: 96, align: "right" as const },
    {
      title: "时间",
      dataIndex: "at",
      width: 172,
      render: (t: string) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {formatExecTime(t)}
        </Text>
      ),
    },
  ];

  const billCols = useMemo(
    () => obsBillingColumns({ formatTime: formatExecTime }),
    [],
  );

  const taskCols: ColumnsType<MockRuntimeTask> = [
    { title: "任务 ID", dataIndex: "taskId", render: (id: string) => <Text code>{id}</Text> },
    {
      title: "状态",
      dataIndex: "state",
      width: 100,
      render: (s: string) => {
        const label = zhTaskState(s);
        if (s === "RUNNING") return <Tag color="processing">{label}</Tag>;
        if (s === "BLOCKED") return <Tag color="warning">{label}</Tag>;
        return <Tag>{label}</Tag>;
      },
    },
    {
      title: "计划时间",
      dataIndex: "scheduledAt",
      width: 180,
      render: (t: string) => formatExecTime(t),
    },
  ];

  const eventCols: ColumnsType<MockRuntimeEventRow> = [
    {
      title: "时间",
      dataIndex: "at",
      width: 176,
      render: (t: string) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {formatExecTime(t)}
        </Text>
      ),
    },
    {
      title: "类型",
      dataIndex: "eventType",
      width: 200,
      render: (t: string) => (
        <Space direction="vertical" size={0}>
          <Text style={{ fontSize: 12 }}>{zhRuntimeEventType(t)}</Text>
          {zhRuntimeEventType(t) !== t ? (
            <Text type="secondary" code style={{ fontSize: 10 }}>
              {t}
            </Text>
          ) : null}
        </Space>
      ),
    },
    { title: "摘要", dataIndex: "summary", ellipsis: true },
  ];

  const scenarioTitle =
    MOCK_SCENARIO_REGISTRY.find((r) => r.scenarioId === exec.scenarioId)?.scenarioTitle ?? exec.intent;

  const tabItems = [
    {
      key: "overview",
      label: EXECUTION_DETAIL.tabOverview,
      children: (
        <Space direction="vertical" size="middle" style={{ width: "100%" }}>
          <Card size="small" className="admin-panel-card" title={EXECUTION_DETAIL.summaryCardTitle}>
            <Descriptions
              bordered
              size="small"
              column={{ xs: 1, sm: 1, md: 2 }}
              styles={{ label: { width: 128, color: token.colorTextSecondary } }}
            >
              <Descriptions.Item label={EXECUTION_DETAIL.labelExecutionId}>
                <Text code copyable>
                  {exec.executionId}
                </Text>
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelSessionId}>
                <Text code>{exec.sessionId}</Text>
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelUserId}>
                <Text code>{exec.userIdMasked}</Text>
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelScenarioId}>
                <Text code>{exec.scenarioId}</Text>
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelOrchVersion}>
                <Text code>{exec.orchestrationVersion}</Text>
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelIntent} span={2}>
                {exec.intent}
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelRuntimeStatus}>
                {runtimeStatusTag(exec.status)}
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelStage}>
                {zhExecutionStage(exec.currentStage)}
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelOutcome}>
                {zhExecutionOutcome(exec.outcome)}
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelRetries}>{exec.retries}</Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelCreatedAt}>
                {formatExecTime(exec.createdAt)}
              </Descriptions.Item>
              <Descriptions.Item label={EXECUTION_DETAIL.labelDuration}>
                {exec.durationMs > 0
                  ? `${exec.durationMs} ms`
                  : running
                    ? EXECUTION_DETAIL.durationRunning
                    : "—"}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {unknown ? (
            <Alert
              type="error"
              showIcon
              message={EXECUTION_DETAIL.unknownCardTitle}
              description={
                <span>
                  {EXECUTION_DETAIL.unknownCardBody}{" "}
                  <Link to={obsHref}>{EXECUTION_DETAIL.obsLink}</Link>
                </span>
              }
            />
          ) : null}

          <ExecutionDetailGovernanceSection
            executionId={exec.executionId}
            scenarioId={exec.scenarioId}
            sessionId={exec.sessionId}
            outcome={exec.outcome}
            resolvedPromptBinding={exec.resolvedPromptBinding}
            timelineEvents={displayMc801Events}
          />

          <ExecutionDetailBillingMirror executionId={exec.executionId} billing={billing} />

          <Collapse
            ghost
            items={[
              {
                key: "policy",
                label: EXECUTION_DETAIL.policyCollapseLabel,
                children: (
                  <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                    <Descriptions
                      bordered
                      size="small"
                      column={{ xs: 1, sm: 2 }}
                      styles={{ label: { width: 140, color: token.colorTextSecondary } }}
                    >
                      <Descriptions.Item label="自动执行">
                        {effectivePolicy.autoExecutionAllowed ? "允许" : "关闭"}
                      </Descriptions.Item>
                      <Descriptions.Item label="高风控场景自动落单">
                        {effectivePolicy.blockAutoHighRiskWrite ? "禁止" : "允许"}
                      </Descriptions.Item>
                      <Descriptions.Item label="查询类自动">
                        {effectivePolicy.queryAutoDefault ? "默认开" : "默认关"}
                      </Descriptions.Item>
                      <Descriptions.Item label="交易/资金须确认">
                        {effectivePolicy.confirmationRequiredForWrites ? "必须" : "不要求"}
                      </Descriptions.Item>
                      <Descriptions.Item label="大额二次确认">
                        {effectivePolicy.secondConfirmLargeNotional ? "开" : "关"}
                      </Descriptions.Item>
                      <Descriptions.Item label="高杠杆确认">
                        {effectivePolicy.highLeverageConfirm ? "开" : "关"}
                      </Descriptions.Item>
                      <Descriptions.Item label="单笔上限（USDT）">{effectivePolicy.maxNotionalUsdt}</Descriptions.Item>
                      <Descriptions.Item label="最大杠杆">{effectivePolicy.maxLeverage}×</Descriptions.Item>
                      <Descriptions.Item label="单日交易写次数上限">
                        {effectivePolicy.maxDailyWriteOperations}
                      </Descriptions.Item>
                      <Descriptions.Item label="最大重试">{effectivePolicy.maxRetries}</Descriptions.Item>
                      <Descriptions.Item label="超时（秒）">{effectivePolicy.executionTimeoutSeconds}</Descriptions.Item>
                      <Descriptions.Item label="失败策略">
                        {FAILURE_STOP_POLICY_LABEL[effectivePolicy.failureStopPolicy]}
                      </Descriptions.Item>
                    </Descriptions>

                    <div>
                      <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
                        {EXECUTION_DETAIL.toolBudgetHint}
                      </Text>
                      <Progress percent={budgetRatioPct} status={budgetWouldExceed ? "exception" : "active"} />
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        本条 {toolCallCountForBudget} / 上限 {effectivePolicy.maxToolCalls}
                      </Text>
                    </div>

                    {budgetWouldExceed ? (
                      <Alert type="warning" showIcon message={EXECUTION_DETAIL.toolBudgetExceeded} />
                    ) : null}

                    <Space wrap>
                      <Link to="/ai/runtime-orchestration?tab=policy">执行策略</Link>
                      <Link
                        to={`/ai/runtime-orchestration?tab=routing&scenario=${encodeURIComponent(exec.scenarioId)}`}
                      >
                        场景
                      </Link>
                      <Link to={`/runtime/executions?scenario=${encodeURIComponent(exec.scenarioId)}`}>
                        同场景列表
                      </Link>
                    </Space>
                  </Space>
                ),
              },
            ]}
          />

          <ExecutionDetailUsageTabs
            tools={tools}
            llms={llms}
            billing={billing}
            toolCols={toolCols}
            llmCols={llmCols}
            billCols={billCols}
          />
        </Space>
      ),
    },
    {
      key: "timeline",
      label: EXECUTION_DETAIL.tabTimeline,
      children: (
        <ExecutionDetailTimelineTab
          exec={exec}
          displayMc801Events={displayMc801Events}
          mc801Loading={Boolean(isObservabilityApiEnabled() && !timelineReady && !execMock)}
          mc801EmptyPresentation={mc801EmptyPresentation}
          stageCurrent={stageCurrent}
          tools={tools}
          llms={llms}
          billing={billing}
          running={running}
          unknown={unknown}
          failed={failed}
          endEventTime={endEventTime}
        />
      ),
    },
    {
      key: "queue",
      label: `${EXECUTION_DETAIL.tabQueue}（${tasks.length}）`,
      children: (
        <Card size="small" className="admin-panel-card">
          <Table
            size="small"
            rowKey="taskId"
            columns={taskCols}
            dataSource={tasks}
            pagination={false}
            locale={{ emptyText: EXECUTION_DETAIL.queueEmpty }}
          />
        </Card>
      ),
    },
    {
      key: "events",
      label: `${EXECUTION_DETAIL.tabEvents}（${runtimeEvents.length}）`,
      children: (
        <Card size="small" className="admin-panel-card">
          <Table
            size="small"
            rowKey={(r, i) => `${r.at}-${r.eventType}-${i}`}
            columns={eventCols}
            dataSource={runtimeEvents}
            pagination={false}
            locale={{ emptyText: EXECUTION_DETAIL.eventsEmpty }}
            scroll={{ x: 640 }}
          />
        </Card>
      ),
    },
    {
      key: "retries",
      label: `${EXECUTION_DETAIL.tabRetries}（${exec.retries}）`,
      children: (
        <Card size="small" className="admin-panel-card">
          <Table
            size="small"
            rowKey="key"
            columns={[
              { title: "次序", dataIndex: "attempt", width: 72 },
              { title: "时间", dataIndex: "at", width: 196, render: (t: string) => formatExecTime(t) },
              { title: "原因", dataIndex: "reason", ellipsis: true },
            ]}
            dataSource={retryRows}
            pagination={false}
            locale={{ emptyText: EXECUTION_DETAIL.retryEmpty }}
          />
        </Card>
      ),
    },
    {
      key: "recovery",
      label: EXECUTION_DETAIL.tabRecovery,
      children: (
        <Card size="small" className="admin-panel-card" title={EXECUTION_DETAIL.recoveryTitle}>
          <Text style={{ fontSize: 13 }}>
            {EXECUTION_DETAIL.recoveryBody}{" "}
            <Link to={obsHref}>{EXECUTION_DETAIL.obsLink}</Link>
          </Text>
        </Card>
      ),
    },
  ];

  return (
    <ProductPageShell
      pageId="runtime.execution-detail"
      showPageId={false}
      title={scenarioTitle}
      description={
        <>
          <Text code copyable style={{ fontSize: 12 }}>
            {exec.executionId}
          </Text>
          <Text type="secondary">
            {" "}
            · 用户 <Text code>{exec.userIdMasked}</Text> · 场景 <Text code>{exec.scenarioId}</Text>
          </Text>
        </>
      }
      tags={
        <Space size={[6, 6]} wrap>
          {runtimeStatusTag(exec.status)}
          <Tag>{zhExecutionOutcome(exec.outcome)}</Tag>
          {unknown ? (
            <Tag color="error">需对账</Tag>
          ) : failed ? (
            <Tag color="error">失败</Tag>
          ) : exec.outcome === "BILLING_BLOCKED" ? (
            <Tag color="warning">计费受阻</Tag>
          ) : running ? (
            <Tag color="processing">进行中</Tag>
          ) : (
            <Tag color="success">已落地</Tag>
          )}
        </Space>
      }
      extra={
        <Space wrap>
          <Button type="primary" disabled>
            {EXECUTION_DETAIL.retryAction}
          </Button>
          <Link to={obsHref}>
            <Button type="default">{EXECUTION_DETAIL.obsLink}</Button>
          </Link>
          <Link to="/runtime/executions">
            <Button type="link">{EXECUTION_DETAIL.backToList}</Button>
          </Link>
        </Space>
      }
    >
      <Tabs
        activeKey={activeTab}
        onChange={(k) => {
          const next = isDetailTab(k) ? k : "overview";
          setSearchParams(next === "overview" ? {} : { tab: next });
        }}
        items={tabItems}
      />
    </ProductPageShell>
  );
}
