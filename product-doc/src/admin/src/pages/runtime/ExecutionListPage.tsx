import { useCallback, useEffect, useMemo, useState } from "react";
import {
  App,
  Alert,
  Button,
  Card,
  Descriptions,
  Divider,
  Drawer,
  Space,
  Tag,
  Typography,
  theme,
} from "antd";
import { EyeOutlined, ThunderboltOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import { Link, useSearchParams } from "react-router-dom";
import { OpsHintAlert } from "../../components/OpsHintAlert";
import { adminPeekPanelShellStyle, ProductPageShell } from "../../components/product";
import { EXECUTION_LIST } from "../../copy/opsPanelHints";
import {
  correlationQueryToListApiParams,
  fetchObservabilityExecutions,
  isObservabilityApiEnabled,
  type ListObservabilityExecutionsParams,
} from "../../api/observabilityExecutions";
import { getObsToolRowsForExecution, mockObsExecutions } from "../../data/mock";
import type { MockObsExecutionRow } from "../../data/types";
import { buildObservabilitySearch } from "../../utils/observabilityDeepLink";
import {
  zhExecutionOutcome,
  zhExecutionRuntimeStatus,
  zhExecutionStage,
  zhToolInvocation,
} from "../../copy/zhLabels";
import { ExecutionListFilters } from "./ExecutionListFilters";
import { ExecutionListTableBlock } from "./ExecutionListTableBlock";
import {
  executionInDateRange,
  executionMatchesCorrelationKeyword,
  executionMatchesScenarioParam,
  executionMatchesStatus,
  parseExecutionStatusFilter,
  type ExecutionStatusFilter,
} from "./executionListTypes";

const { Text } = Typography;

function statusTag(status: string) {
  const label = zhExecutionRuntimeStatus(status);
  if (status === "COMPLETED") return <Tag color="success">{label}</Tag>;
  if (status === "RUNNING") return <Tag color="processing">{label}</Tag>;
  if (status === "UNKNOWN") return <Tag color="warning">{label}</Tag>;
  if (status === "FAILED" || status === "BLOCKED") return <Tag color="error">{label}</Tag>;
  if (status === "CREATED") return <Tag color="default">{label}</Tag>;
  return <Tag>{label}</Tag>;
}

function formatExecutionTime(iso: string): string {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 19);
}

export function ExecutionListPage() {
  const { token } = theme.useToken();
  const { message: messageApi } = App.useApp();
  const [searchParams, setSearchParams] = useSearchParams();
  const [preview, setPreview] = useState<MockObsExecutionRow | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const useObservabilityApi = isObservabilityApiEnabled();
  const [remoteRows, setRemoteRows] = useState<MockObsExecutionRow[]>([]);
  const [remoteLoading, setRemoteLoading] = useState(false);
  const [remoteLoadingMore, setRemoteLoadingMore] = useState(false);
  const [remoteError, setRemoteError] = useState<string | null>(null);
  const [remoteNextCursor, setRemoteNextCursor] = useState<string | null>(null);

  const qCorrelation = searchParams.get("q") ?? "";
  const qIntent = searchParams.get("intent") ?? "";
  const qScenario = searchParams.get("scenario") ?? "";
  const statusFilter = parseExecutionStatusFilter(searchParams.get("status"));
  const dateFrom = searchParams.get("from") ?? "";
  const dateTo = searchParams.get("to") ?? "";

  const mutateQuery = useCallback(
    (mutate: (n: URLSearchParams) => void) => {
      setSearchParams(
        (prev) => {
          const n = new URLSearchParams(prev);
          mutate(n);
          return n;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  const setQCorrelation = useCallback(
    (v: string) => {
      mutateQuery((n) => {
        const t = v.trim();
        if (t) n.set("q", t);
        else n.delete("q");
      });
    },
    [mutateQuery],
  );

  const setQIntent = useCallback(
    (v: string) => {
      mutateQuery((n) => {
        const t = v.trim();
        if (t) n.set("intent", t);
        else n.delete("intent");
      });
    },
    [mutateQuery],
  );

  const setStatusFilter = useCallback(
    (s: ExecutionStatusFilter) => {
      mutateQuery((n) => {
        if (s === "all") n.delete("status");
        else n.set("status", s);
      });
    },
    [mutateQuery],
  );

  const setDateFrom = useCallback(
    (v: string) => {
      mutateQuery((n) => {
        if (v) n.set("from", v);
        else n.delete("from");
      });
    },
    [mutateQuery],
  );

  const setDateTo = useCallback(
    (v: string) => {
      mutateQuery((n) => {
        if (v) n.set("to", v);
        else n.delete("to");
      });
    },
    [mutateQuery],
  );

  const tableFilterKey = searchParams.toString();

  const dateRangeInvalid = Boolean(dateFrom && dateTo && dateFrom > dateTo);
  const effectiveDateFrom = dateRangeInvalid ? "" : dateFrom;
  const effectiveDateTo = dateRangeInvalid ? "" : dateTo;

  const remoteQueryParams = useMemo((): ListObservabilityExecutionsParams => {
    const params: ListObservabilityExecutionsParams = { pageSize: 100 };
    const corr = correlationQueryToListApiParams(qCorrelation);
    if (corr.userId) params.userId = corr.userId;
    if (corr.executionId) params.executionId = corr.executionId;
    if (corr.scenarioId) params.scenarioId = corr.scenarioId;
    const sc = qScenario.trim();
    if (sc) params.scenarioId = sc;
    const int = qIntent.trim();
    if (int) params.intentContains = int;
    if (statusFilter !== "all") params.status = statusFilter;
    if (effectiveDateFrom) params.timeFrom = `${effectiveDateFrom}T00:00:00.000Z`;
    if (effectiveDateTo) params.timeTo = `${effectiveDateTo}T23:59:59.999Z`;
    return params;
  }, [qCorrelation, qScenario, qIntent, statusFilter, effectiveDateFrom, effectiveDateTo]);

  const loadRemoteExecutions = useCallback(async () => {
    setRemoteLoading(true);
    setRemoteError(null);
    try {
      const { items, nextCursor } = await fetchObservabilityExecutions(remoteQueryParams);
      setRemoteRows(items);
      setRemoteNextCursor(nextCursor);
    } catch (e) {
      setRemoteRows([]);
      setRemoteNextCursor(null);
      setRemoteError(e instanceof Error ? e.message : String(e));
    } finally {
      setRemoteLoading(false);
    }
  }, [remoteQueryParams]);

  const loadMoreRemoteExecutions = useCallback(async () => {
    if (!remoteNextCursor) return;
    setRemoteLoadingMore(true);
    setRemoteError(null);
    try {
      const { items, nextCursor } = await fetchObservabilityExecutions({
        ...remoteQueryParams,
        cursor: remoteNextCursor,
      });
      setRemoteRows((prev) => {
        const seen = new Set(prev.map((r) => r.executionId));
        const merged = [...prev];
        for (const r of items) {
          if (!seen.has(r.executionId)) {
            seen.add(r.executionId);
            merged.push(r);
          }
        }
        return merged;
      });
      setRemoteNextCursor(nextCursor);
    } catch (e) {
      setRemoteError(e instanceof Error ? e.message : String(e));
    } finally {
      setRemoteLoadingMore(false);
    }
  }, [remoteQueryParams, remoteNextCursor]);

  useEffect(() => {
    if (!useObservabilityApi) return;
    void loadRemoteExecutions();
  }, [useObservabilityApi, loadRemoteExecutions]);

  const totalCountForFilters = useObservabilityApi ? undefined : mockObsExecutions.length;

  const filtered = useMemo(() => {
    const qi = qIntent.trim().toLowerCase();
    return mockObsExecutions.filter((r) => {
      if (!executionMatchesScenarioParam(r, qScenario)) return false;
      if (!executionMatchesCorrelationKeyword(r, qCorrelation)) return false;
      if (qi && !r.intent.toLowerCase().includes(qi)) return false;
      if (!executionMatchesStatus(statusFilter, r.status)) return false;
      if (!executionInDateRange(r.createdAt, effectiveDateFrom, effectiveDateTo)) return false;
      return true;
    });
  }, [qScenario, qCorrelation, qIntent, statusFilter, effectiveDateFrom, effectiveDateTo]);

  const sortedRows = useMemo(() => {
    const base = useObservabilityApi ? remoteRows : filtered;
    return [...base].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }, [useObservabilityApi, remoteRows, filtered]);

  const resetFilters = useCallback(() => {
    mutateQuery((n) => {
      ["q", "intent", "scenario", "status", "from", "to"].forEach((k) => n.delete(k));
    });
    messageApi.success("已重置筛选条件");
  }, [mutateQuery, messageApi]);

  const handleRefreshDemo = useCallback(async () => {
    if (useObservabilityApi) {
      await loadRemoteExecutions();
      messageApi.success("已从 API 刷新列表");
      return;
    }
    setRefreshing(true);
    window.setTimeout(() => {
      setRefreshing(false);
      messageApi.success("已刷新列表（演示）");
    }, 420);
  }, [useObservabilityApi, loadRemoteExecutions, messageApi]);

  const listBusy = useObservabilityApi ? remoteLoading : refreshing;

  const previewTools = preview ? getObsToolRowsForExecution(preview.executionId) : [];

  const statusOptions: { value: ExecutionStatusFilter; label: string }[] = [
    { value: "all", label: "全部状态" },
    { value: "CREATED", label: zhExecutionRuntimeStatus("CREATED") },
    { value: "RUNNING", label: zhExecutionRuntimeStatus("RUNNING") },
    { value: "COMPLETED", label: zhExecutionRuntimeStatus("COMPLETED") },
    { value: "UNKNOWN", label: zhExecutionRuntimeStatus("UNKNOWN") },
    { value: "FAILED", label: zhExecutionRuntimeStatus("FAILED") },
    { value: "BLOCKED", label: zhExecutionRuntimeStatus("BLOCKED") },
  ];

  const cols: ColumnsType<MockObsExecutionRow> = useMemo(
    () => [
      {
        title: "执行 ID",
        dataIndex: "executionId",
        key: "e",
        width: 200,
        fixed: "left",
        ellipsis: true,
        render: (id: string) => (
          <Text ellipsis={{ tooltip: id }} style={{ display: "block", maxWidth: 180 }}>
            {id}
          </Text>
        ),
      },
      {
        title: "用户 UID",
        dataIndex: "userIdMasked",
        key: "u",
        width: 120,
        ellipsis: true,
        render: (s: string) => <Text ellipsis={{ tooltip: s }}>{s}</Text>,
      },
      {
        title: "场景 ID",
        dataIndex: "scenarioId",
        key: "sc",
        width: 168,
        ellipsis: true,
        render: (s: string) => (
          <Text ellipsis={{ tooltip: s }} style={{ display: "block", maxWidth: 152 }}>
            {s}
          </Text>
        ),
      },
      {
        title: "意图摘要",
        dataIndex: "intent",
        key: "i",
        ellipsis: true,
        render: (text: string) => (
          <Text ellipsis={{ tooltip: text }} style={{ display: "block", maxWidth: 240 }}>
            {text}
          </Text>
        ),
      },
      {
        title: "运行状态",
        dataIndex: "status",
        key: "st",
        width: 112,
        render: (s: string) => statusTag(s),
      },
      {
        title: "当前阶段",
        dataIndex: "currentStage",
        key: "cs",
        width: 112,
        render: (s: string) => zhExecutionStage(s),
      },
      {
        title: "业务终态",
        dataIndex: "outcome",
        key: "oc",
        width: 112,
        render: (o: string) => zhExecutionOutcome(o),
      },
      {
        title: "重试次数",
        dataIndex: "retries",
        key: "r",
        width: 88,
        align: "right",
      },
      {
        title: "创建时间",
        dataIndex: "createdAt",
        key: "c",
        width: 172,
        sorter: (a, b) => a.createdAt.localeCompare(b.createdAt),
        render: (s: string) => (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {formatExecutionTime(s)}
          </Text>
        ),
      },
      {
        title: "操作",
        key: "act",
        width: 132,
        fixed: "right",
        render: (_, row) => (
          <Space size="small" wrap onClick={(e) => e.stopPropagation()} role="group" aria-label="行操作">
            <Button
              type="link"
              size="small"
              style={{ padding: 0, height: "auto" }}
              onClick={() => setPreview(row)}
            >
              预览
            </Button>
            <Link to={`/runtime/executions/${row.executionId}`}>详情</Link>
          </Space>
        ),
      },
    ],
    [],
  );

  const obsForPreview = preview
    ? `/observability${buildObservabilitySearch({
        executionId: preview.executionId,
        userId: preview.userIdMasked,
        tab: "tool",
      })}`
    : "/observability";

  return (
    <ProductPageShell
      pageId="runtime.executions"
      showPageId={false}
      title="执行记录"
      tags={<Tag color="blue">{EXECUTION_LIST.tag}</Tag>}
      extra={
        <Space wrap>
          <Button
            icon={<ThunderboltOutlined />}
            loading={listBusy}
            onClick={() => void handleRefreshDemo()}
          >
            刷新
          </Button>
        </Space>
      }
    >
      <Card
        size="small"
        className="admin-panel-card"
        styles={{ body: { paddingTop: 8, paddingBottom: 8 } }}
        title="列表"
      >
        <Space direction="vertical" size="small" style={{ width: "100%" }}>
          {useObservabilityApi ? (
            <OpsHintAlert
              type="info"
              showIcon
              message={EXECUTION_LIST.apiEnabledMessage}
              description={EXECUTION_LIST.apiEnabledDescription}
              technicalDetail={EXECUTION_LIST.apiEnabledTechnical}
            />
          ) : null}
          {useObservabilityApi && remoteError ? (
            <Alert type="error" showIcon message="列表加载失败" description={remoteError} />
          ) : null}
          {qScenario.trim() ? (
            <Alert
              type="info"
              showIcon
              message={
                <span>
                  场景 <Text code>{qScenario.trim()}</Text>
                </span>
              }
              action={
                <Button
                  size="small"
                  type="link"
                  onClick={() =>
                    mutateQuery((n) => {
                      n.delete("scenario");
                    })
                  }
                >
                  清除场景条件
                </Button>
              }
            />
          ) : null}
          <ExecutionListFilters
            qCorrelation={qCorrelation}
            qIntent={qIntent}
            statusFilter={statusFilter}
            dateFrom={dateFrom}
            dateTo={dateTo}
            statusOptions={statusOptions}
            totalCount={totalCountForFilters}
            resultCount={sortedRows.length}
            dateRangeInvalid={dateRangeInvalid}
            onQCorrelation={setQCorrelation}
            onQIntent={setQIntent}
            onStatusFilter={setStatusFilter}
            onDateFrom={setDateFrom}
            onDateTo={setDateTo}
            onReset={resetFilters}
          />

          <ExecutionListTableBlock
            columns={cols}
            dataSource={sortedRows}
            paginationResetKey={tableFilterKey}
            loading={useObservabilityApi && remoteLoading}
            onRowPreview={setPreview}
          />
          {useObservabilityApi && remoteNextCursor ? (
            <div style={{ textAlign: "center", marginTop: 8 }}>
              <Button type="default" loading={remoteLoadingMore} onClick={() => void loadMoreRemoteExecutions()}>
                加载更多
              </Button>
              <Text type="secondary" style={{ display: "block", marginTop: 8, fontSize: 12 }}>
                当前共 {sortedRows.length} 条 · {EXECUTION_LIST.loadMoreHint}
              </Text>
            </div>
          ) : null}
        </Space>
      </Card>

      <Drawer
        title="执行摘要 · 预览"
        placement="right"
        width={440}
        open={preview !== null}
        onClose={() => setPreview(null)}
        destroyOnClose
        styles={{ body: { paddingBottom: 24 } }}
        extra={
          preview ? (
            <Link to={`/runtime/executions/${preview.executionId}`}>
              <Button type="primary">打开详情页</Button>
            </Link>
          ) : null
        }
      >
        {preview ? (
          <div>
            <div style={adminPeekPanelShellStyle(token)}>
              <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                执行 ID
              </Text>
              <Text style={{ wordBreak: "break-all" }}>{preview.executionId}</Text>
              <Space wrap size={[8, 8]} style={{ marginTop: 10 }}>
                {statusTag(preview.status)}
                <Tag>{zhExecutionOutcome(preview.outcome)}</Tag>
              </Space>
            </div>

            <Descriptions size="small" column={1} labelStyle={{ width: 96, color: token.colorTextSecondary }}>
              <Descriptions.Item label="用户 UID">
                <Text>{preview.userIdMasked}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="场景 ID">
                <Text style={{ wordBreak: "break-all" }}>{preview.scenarioId}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="编排版本">
                <Text style={{ wordBreak: "break-all" }}>{preview.orchestrationVersion}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="意图摘要">{preview.intent}</Descriptions.Item>
              <Descriptions.Item label="当前阶段">{zhExecutionStage(preview.currentStage)}</Descriptions.Item>
              <Descriptions.Item label="重试次数">{preview.retries}</Descriptions.Item>
              <Descriptions.Item label="创建时间">{formatExecutionTime(preview.createdAt)}</Descriptions.Item>
            </Descriptions>

            <Card
              size="small"
              className="admin-panel-card"
              title={`工具调用预览（${previewTools.length}）`}
              style={{ marginTop: 16 }}
            >
              {previewTools.length === 0 ? (
                <Text type="secondary">本条记录暂无关联工具行</Text>
              ) : (
                <ul style={{ margin: 0, paddingLeft: 18 }}>
                  {previewTools.map((t) => (
                    <li key={`${t.toolCallSeq}-${t.toolId}`}>
                      <Text code style={{ fontSize: 12 }}>
                        {t.toolId}
                      </Text>{" "}
                      · {zhToolInvocation(t.invocationState)}
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Divider plain style={{ margin: "12px 0" }} />
            <Space direction="vertical" size="small" style={{ width: "100%" }}>
              <Link
                to={`/ai/runtime-orchestration?tab=routing&scenario=${encodeURIComponent(preview.scenarioId)}`}
              >
                <Button block>编排</Button>
              </Link>
              <Link to={`/runtime/executions/${preview.executionId}?tab=queue`}>
                <Button block>任务队列</Button>
              </Link>
              <Link to={`/runtime/executions/${preview.executionId}?tab=events`}>
                <Button block>运行事件</Button>
              </Link>
              <Link to={obsForPreview}>
                <Button type="primary" icon={<EyeOutlined />} block>
                  可观测性
                </Button>
              </Link>
            </Space>
          </div>
        ) : null}
      </Drawer>

    </ProductPageShell>
  );
}
