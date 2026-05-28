import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { App, Alert, Button, Card, Descriptions, Divider, Drawer, Form, Input, Select, Space, Table, Tabs, Tag, Timeline, Typography, theme } from "antd";
import { LinkOutlined, SearchOutlined, ShareAltOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import { ProductPageShell, AdminFilterSurface, ADMIN_FILTER_CONTROL_SIZE, ADMIN_PAGE_FILTER_FORM_PROPS, adminListPagination } from "../../components/product";
import {
  mockObsAudits,
  mockObsBilling,
  mockObsExecutions,
  mockObsLlms,
  mockObsTools,
} from "../../data/mock";
import type {
  MockObsAuditRow,
  MockObsBillingRow,
  MockObsExecutionRow,
  MockObsLlmRow,
  MockObsToolRow,
} from "../../data/types";
import { buildObservabilitySearch, isObservabilityTab, readObservabilityTraceQuery, type ObservabilityTab } from "../../utils/observabilityDeepLink";
import {
  executionTraceOutcomeTag,
  getTraceTimelineSteps,
  promptSummaryLine,
  riskHitSummary,
} from "./executionTraceHelpers";
import { OpsHintAlert } from "../../components/OpsHintAlert";
import { OBSERVABILITY } from "../../copy/opsPanelHints";
import { Mc801TimelineAudit } from "../runtime/Mc801TimelineAudit";
import { obsBillingColumns } from "../billing/obsBillingColumns";
import { zhEntitlementDebitStatus } from "../../copy/billingLabels";
import { zhToolInvocation } from "../../copy/zhLabels";

const { Text } = Typography;

const TAB_LABELS: Record<ObservabilityTab, string> = {
  execution: "执行",
  tool: "工具调用",
  llm: "大模型",
  billing: "计费",
  audit: "审计",
};

export function ObservabilityPage() {
  const { message } = App.useApp();
  const { token } = theme.useToken();
  const [searchParams, setSearchParams] = useSearchParams();

  const tabFromUrl = searchParams.get("tab");
  const activeTab: ObservabilityTab =
    tabFromUrl !== null && isObservabilityTab(tabFromUrl) ? tabFromUrl : "execution";

  const [execQ, setExecQ] = useState("");
  const [userQ, setUserQ] = useState("");
  const [traceQ, setTraceQ] = useState("");
  const [toolQ, setToolQ] = useState("");
  const [llmQ, setLlmQ] = useState("");
  const [billQ, setBillQ] = useState("");
  const [billStatus, setBillStatus] = useState<string | undefined>(undefined);
  const [urlHydrated, setUrlHydrated] = useState(false);
  const [traceDrawerId, setTraceDrawerId] = useState<string | null>(null);

  useEffect(() => {
    setExecQ(searchParams.get("executionId") ?? "");
    setUserQ(searchParams.get("userId") ?? "");
    setTraceQ(readObservabilityTraceQuery(searchParams));
    setUrlHydrated(true);
  }, [searchParams]);

  const commitQueryToUrl = useCallback(() => {
    const next = new URLSearchParams();
    if (execQ.trim()) next.set("executionId", execQ.trim());
    if (userQ.trim()) next.set("userId", userQ.trim());
    if (traceQ.trim()) next.set("traceId", traceQ.trim());
    next.set("tab", activeTab);
    setSearchParams(next, { replace: true });
    message.success("检索条件已更新");
  }, [execQ, userQ, traceQ, activeTab, setSearchParams, message]);

  const onTabChange = (key: string) => {
    const next = new URLSearchParams(searchParams);
    next.set("tab", key);
    setSearchParams(next, { replace: true });
  };

  const onQuery = () => {
    commitQueryToUrl();
  };

  const shareHref = useMemo(() => {
    return `${window.location.pathname}${buildObservabilitySearch({
      executionId: execQ || undefined,
      userId: userQ || undefined,
      traceId: traceQ || undefined,
      tab: activeTab,
    })}`;
  }, [execQ, userQ, traceQ, activeTab]);

  const execFiltered = useMemo(() => {
    const ex = execQ.trim().toLowerCase();
    const us = userQ.trim().toLowerCase();
    return mockObsExecutions.filter((e) => {
      if (ex && !e.executionId.toLowerCase().includes(ex)) return false;
      if (us && !e.userIdMasked.toLowerCase().includes(us)) return false;
      return true;
    });
  }, [execQ, userQ]);

  const timelineAnchor = useMemo(() => {
    const q = execQ.trim();
    if (q) {
      const exact = mockObsExecutions.find((e) => e.executionId === q);
      if (exact) return exact;
    }
    if (execFiltered.length === 1) return execFiltered[0];
    return undefined;
  }, [execQ, execFiltered]);

  const drawerExecution = useMemo(
    () => (traceDrawerId ? mockObsExecutions.find((e) => e.executionId === traceDrawerId) : undefined),
    [traceDrawerId],
  );

  const drawerTools = useMemo(
    () => (traceDrawerId ? mockObsTools.filter((t) => t.executionId === traceDrawerId) : []),
    [traceDrawerId],
  );

  const drawerLlms = useMemo(
    () => (traceDrawerId ? mockObsLlms.filter((l) => l.executionId === traceDrawerId) : []),
    [traceDrawerId],
  );

  const toolFiltered = useMemo(() => {
    const t = toolQ.trim().toLowerCase();
    const ex = execQ.trim().toLowerCase();
    const us = userQ.trim().toLowerCase();
    return mockObsTools.filter((c) => {
      if (ex && !c.executionId.toLowerCase().includes(ex)) return false;
      if (us) {
        const execUser = mockObsExecutions.find((e) => e.executionId === c.executionId)?.userIdMasked ?? "";
        if (!execUser.toLowerCase().includes(us)) return false;
      }
      if (t && !`${c.toolId} ${c.executionId} ${c.invocationState}`.toLowerCase().includes(t)) return false;
      return true;
    });
  }, [toolQ, execQ, userQ]);

  const llmFiltered = useMemo(() => {
    const t = llmQ.trim().toLowerCase();
    const ex = execQ.trim().toLowerCase();
    const us = userQ.trim().toLowerCase();
    return mockObsLlms.filter((c) => {
      if (ex && !c.executionId.toLowerCase().includes(ex)) return false;
      if (us) {
        const execUser = mockObsExecutions.find((e) => e.executionId === c.executionId)?.userIdMasked ?? "";
        if (!execUser.toLowerCase().includes(us)) return false;
      }
      if (t && !`${c.modelId} ${c.executionId}`.toLowerCase().includes(t)) return false;
      return true;
    });
  }, [llmQ, execQ, userQ]);

  const billFiltered = useMemo(() => {
    const t = billQ.trim().toLowerCase();
    const tr = traceQ.trim().toLowerCase();
    const ex = execQ.trim().toLowerCase();
    const us = userQ.trim().toLowerCase();
    return mockObsBilling.filter((r) => {
      if (ex && !r.executionId.toLowerCase().includes(ex)) return false;
      if (us) {
        const execUser = mockObsExecutions.find((e) => e.executionId === r.executionId)?.userIdMasked ?? "";
        if (!execUser.toLowerCase().includes(us)) return false;
      }
      if (tr && !r.billingTraceId.toLowerCase().includes(tr)) return false;
      const statusOk = !billStatus || r.debitStatus === billStatus;
      const textOk =
        !t ||
        `${r.billingTraceId} ${r.capabilitySkuId} ${r.executionId}`
          .toLowerCase()
          .includes(t);
      return statusOk && textOk;
    });
  }, [billQ, billStatus, traceQ, execQ, userQ]);

  const auditFiltered = useMemo(() => {
    const ex = execQ.trim().toLowerCase();
    if (!ex) return mockObsAudits;
    return mockObsAudits.filter(
      (a) =>
        a.resource.toLowerCase().includes(ex) ||
        a.action.toLowerCase().includes(ex) ||
        a.actor.toLowerCase().includes(ex),
    );
  }, [execQ]);

  const renderExecutionIdLink = (id: string) => (
    <Typography.Link
      onClick={() => setTraceDrawerId(id)}
      style={{ fontFamily: "var(--ant-font-family-code, monospace)", fontSize: 12 }}
    >
      {id}
    </Typography.Link>
  );

  const traceTimelineItems =
    timelineAnchor != null
      ? getTraceTimelineSteps(timelineAnchor).map((s) => ({
          color:
            s.state === "error" ? "red" : s.state === "warning" ? "orange" : s.state === "success" ? "green" : "gray",
          children: (
            <div>
              <Text strong style={{ marginRight: 8 }}>
                {s.time}
              </Text>
              <Text>{s.title}</Text>
              {s.detail ? (
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {s.detail}
                  </Text>
                </div>
              ) : null}
            </div>
          ),
        }))
      : [];

  const drawerTimelineItems =
    drawerExecution != null
      ? getTraceTimelineSteps(drawerExecution).map((s) => ({
          color:
            s.state === "error" ? "red" : s.state === "warning" ? "orange" : s.state === "success" ? "green" : "gray",
          children: (
            <div>
              <Text strong style={{ marginRight: 8 }}>
                {s.time}
              </Text>
              <Text>{s.title}</Text>
              {s.detail ? (
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {s.detail}
                  </Text>
                </div>
              ) : null}
            </div>
          ),
        }))
      : [];

  const execColumns: ColumnsType<MockObsExecutionRow> = [
    {
      title: "执行 ID",
      dataIndex: "executionId",
      width: 140,
      ellipsis: true,
      render: (id: string) => renderExecutionIdLink(id),
    },
    { title: "用户 UID", dataIndex: "userIdMasked", width: 110 },
    { title: "场景", dataIndex: "scenarioId", ellipsis: true },
    {
      title: "终态",
      dataIndex: "outcome",
      width: 120,
      render: (_o: string, row) => {
        const { label, color } = executionTraceOutcomeTag(row);
        return <Tag color={color}>{label}</Tag>;
      },
    },
    { title: "耗时（毫秒）", dataIndex: "durationMs", width: 100 },
    { title: "开始时间", dataIndex: "startedAt", width: 180 },
  ];

  const toolColumns: ColumnsType<MockObsToolRow> = [
    {
      title: "执行 ID",
      dataIndex: "executionId",
      width: 140,
      ellipsis: true,
      render: (id: string) => renderExecutionIdLink(id),
    },
    { title: "序号", dataIndex: "toolCallSeq", width: 64 },
    { title: "工具 ID", dataIndex: "toolId", width: 220, ellipsis: true },
    { title: "状态", dataIndex: "invocationState", width: 120, render: (s: string) => zhToolInvocation(s) },
    { title: "路径摘要", dataIndex: "pathSummary", ellipsis: true },
    { title: "时间", dataIndex: "at", width: 180 },
  ];

  const llmColumns: ColumnsType<MockObsLlmRow> = [
    {
      title: "执行 ID",
      dataIndex: "executionId",
      width: 140,
      ellipsis: true,
      render: (id: string) => renderExecutionIdLink(id),
    },
    { title: "模型 ID", dataIndex: "modelId", width: 140 },
    {
      title: "Token 合计",
      key: "tok",
      width: 100,
      render: (_, r) => r.inputTokens + r.outputTokens,
    },
    { title: "时间", dataIndex: "at", width: 180 },
  ];

  const billColumns: ColumnsType<MockObsBillingRow> = [
    {
      title: "执行 ID",
      dataIndex: "executionId",
      width: 120,
      ellipsis: true,
      render: (id: string) => renderExecutionIdLink(id),
    },
    ...obsBillingColumns(),
  ];

  const auditColumns: ColumnsType<MockObsAuditRow> = [
    { title: "时间", dataIndex: "at", width: 180 },
    { title: "操作者", dataIndex: "actor", width: 140 },
    { title: "动作", dataIndex: "action", ellipsis: true },
    { title: "资源", dataIndex: "resource", ellipsis: true },
  ];

  const hasDeepLink =
    urlHydrated &&
    Boolean(
      searchParams.get("executionId") ||
        searchParams.get("userId") ||
        searchParams.get("traceId") ||
        searchParams.get("traceKey"),
    );

  const tabItems = (["execution", "tool", "llm", "billing", "audit"] as ObservabilityTab[]).map((k) => ({
    key: k,
    label: (
      <span>
        {TAB_LABELS[k]}
        <Tag style={{ marginLeft: 6 }} bordered={false}>
          {
            k === "execution"
              ? execFiltered.length
              : k === "tool"
                ? toolFiltered.length
                : k === "llm"
                  ? llmFiltered.length
                  : k === "billing"
                    ? billFiltered.length
                    : auditFiltered.length
          }
        </Tag>
      </span>
    ),
    children: (
      <div style={{ paddingTop: 8 }}>
        {k === "execution" && (
          <>
            <Table
              size="small"
              rowKey="executionId"
              dataSource={execFiltered}
              columns={execColumns}
              pagination={adminListPagination()}
              scroll={{ x: true }}
            />
          </>
        )}
        {k === "tool" && (
          <>
            <div style={{ marginBottom: 14 }}>
              <Text type="secondary" strong style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
                附加筛选
              </Text>
              <Input
                allowClear
                size={ADMIN_FILTER_CONTROL_SIZE}
                placeholder="工具 ID、调用状态、路径关键词…"
                prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                value={toolQ}
                onChange={(e) => setToolQ(e.target.value)}
              />
            </div>
            <Table
              size="small"
              rowKey={(r) => `${r.executionId}-${r.toolCallSeq}-${r.toolId}`}
              dataSource={toolFiltered}
              columns={toolColumns}
              pagination={adminListPagination()}
              scroll={{ x: true }}
            />
          </>
        )}
        {k === "llm" && (
          <>
            <div style={{ marginBottom: 14 }}>
              <Text type="secondary" strong style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
                附加筛选
              </Text>
              <Input
                allowClear
                size={ADMIN_FILTER_CONTROL_SIZE}
                placeholder="模型 ID、执行 ID 片段…"
                prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                value={llmQ}
                onChange={(e) => setLlmQ(e.target.value)}
              />
            </div>
            <Table
              size="small"
              rowKey={(r) => `${r.executionId}-${r.modelId}-${r.at}`}
              dataSource={llmFiltered}
              columns={llmColumns}
              pagination={adminListPagination()}
              scroll={{ x: true }}
            />
          </>
        )}
        {k === "billing" && (
          <>
            <div style={{ marginBottom: 14 }}>
              <Text type="secondary" strong style={{ display: "block", marginBottom: 8, fontSize: 13 }}>
                附加筛选
              </Text>
              <Space wrap style={{ width: "100%" }} size={[12, 12]}>
                <Input
                  allowClear
                  size={ADMIN_FILTER_CONTROL_SIZE}
                  style={{ width: "100%", minWidth: 200, maxWidth: 280 }}
                  placeholder="Capability / 链路 ID / 执行 ID…"
                  prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                  value={billQ}
                  onChange={(e) => setBillQ(e.target.value)}
                />
                <Select
                  allowClear
                  placeholder="核销状态"
                  size={ADMIN_FILTER_CONTROL_SIZE}
                  style={{ width: 200 }}
                  options={Array.from(new Set(mockObsBilling.map((r) => r.debitStatus))).map((s) => ({
                    label: zhEntitlementDebitStatus(s),
                    value: s,
                  }))}
                  value={billStatus}
                  onChange={(v) => setBillStatus(v ?? undefined)}
                />
              </Space>
            </div>
            <Table
              size="small"
              rowKey={(r) => `${r.billingTraceId}-${r.at}`}
              dataSource={billFiltered}
              columns={billColumns}
              pagination={adminListPagination()}
              scroll={{ x: true }}
            />
          </>
        )}
        {k === "audit" && (
          <>
            <Text type="secondary" style={{ display: "block", marginBottom: 12, fontSize: 12 }}>
              {OBSERVABILITY.auditTabHint}
            </Text>
            <Table
              size="small"
              rowKey={(r) => `${r.at}-${r.action}-${r.resource}`}
              dataSource={auditFiltered}
              columns={auditColumns}
              pagination={adminListPagination()}
              scroll={{ x: true }}
            />
          </>
        )}
      </div>
    ),
  }));

  return (
    <ProductPageShell
      pageId="obs.traces-logs"
      title="执行链路协查"
      description="按执行 ID、用户 UID、计费链路快速定位问题；以执行生命周期查看工具、模型与计费，而非纯日志行表格。"
      tags={<Tag color="purple">{OBSERVABILITY.tag}</Tag>}
      extra={
        <Space wrap>
          <Button icon={<LinkOutlined />} onClick={() => void navigator.clipboard.writeText(shareHref).then(() => message.success("已复制协查链接"))}>
            复制链接
          </Button>
          <Button type="primary" icon={<SearchOutlined />} onClick={onQuery}>
            应用检索
          </Button>
        </Space>
      }
    >
      {hasDeepLink ? (
        <OpsHintAlert
          type="info"
          showIcon
          icon={<ShareAltOutlined />}
          message={OBSERVABILITY.deepLinkRestored}
          style={{ marginBottom: 16 }}
          closable
        />
      ) : null}

      <AdminFilterSurface
        title="检索上下文"
        extra={
          <Text type="secondary" style={{ fontSize: 12 }}>
            当前视图：<Text strong>{TAB_LABELS[activeTab]}</Text>
          </Text>
        }
        footer={
          <Text type="secondary" style={{ fontSize: 12 }}>
            {OBSERVABILITY.filterFooter}
          </Text>
        }
        style={{ marginBottom: 16 }}
      >
        <Form {...ADMIN_PAGE_FILTER_FORM_PROPS} style={{ marginBottom: 0 }}>
          <div className="admin-filter-query-grid">
            <div className="admin-filter-span-4">
              <Form.Item label="执行 ID" style={{ marginBottom: 0 }}>
                <Input
                  allowClear
                  size={ADMIN_FILTER_CONTROL_SIZE}
                  placeholder="executionId"
                  prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                  value={execQ}
                  onChange={(e) => setExecQ(e.target.value)}
                />
              </Form.Item>
            </div>
            <div className="admin-filter-span-4">
              <Form.Item label="用户 UID" style={{ marginBottom: 0 }}>
                <Input
                  allowClear
                  size={ADMIN_FILTER_CONTROL_SIZE}
                  placeholder="用户 UID（掩码）"
                  prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                  value={userQ}
                  onChange={(e) => setUserQ(e.target.value)}
                />
              </Form.Item>
            </div>
            <div className="admin-filter-span-4">
              <Form.Item
                label={OBSERVABILITY.filterTraceLabel}
                extra={<Text type="secondary">{OBSERVABILITY.filterTraceExtra}</Text>}
                style={{ marginBottom: 0 }}
              >
                <Input
                  allowClear
                  size={ADMIN_FILTER_CONTROL_SIZE}
                  placeholder={OBSERVABILITY.filterTracePlaceholder}
                  prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                  value={traceQ}
                  onChange={(e) => setTraceQ(e.target.value)}
                />
              </Form.Item>
            </div>
          </div>
        </Form>
      </AdminFilterSurface>

      <Card size="small" className="admin-panel-card" title={OBSERVABILITY.timelineCardTitle} style={{ marginBottom: 16 }}>
        {timelineAnchor ? (
          <>
            <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 12 }}>
              {OBSERVABILITY.timelineLocked}：<Text code>{timelineAnchor.executionId}</Text> · {timelineAnchor.intent}
            </Text>
            <Mc801TimelineAudit timelineEvents={timelineAnchor.timelineEvents} />
            <Divider plain style={{ margin: "16px 0" }}>
              {OBSERVABILITY.narrativeDivider}
            </Divider>
            <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
              {OBSERVABILITY.narrativeHint}
            </Text>
            <Timeline items={traceTimelineItems} />
          </>
        ) : (
          <Text type="secondary">{OBSERVABILITY.timelineEmpty}</Text>
        )}
      </Card>

      <Card size="small" className="admin-panel-card" title={OBSERVABILITY.lifecycleCardTitle}>
        <Tabs activeKey={activeTab} onChange={onTabChange} items={tabItems} />
      </Card>

      <Drawer
        title={drawerExecution ? drawerExecution.executionId : "协查"}
        width={720}
        open={traceDrawerId != null}
        onClose={() => setTraceDrawerId(null)}
        destroyOnClose
        extra={
          drawerExecution ? (
            <Link to={`/runtime/executions/${drawerExecution.executionId}`}>
              <Button type="primary">打开执行详情页</Button>
            </Link>
          ) : null
        }
      >
        {drawerExecution ? (
          <Space direction="vertical" size="large" style={{ width: "100%" }}>
            <Descriptions size="small" column={2} bordered>
              <Descriptions.Item label="用户 UID">{drawerExecution.userIdMasked}</Descriptions.Item>
              <Descriptions.Item label="会话">{drawerExecution.sessionId}</Descriptions.Item>
              <Descriptions.Item label="场景" span={2}>
                {drawerExecution.scenarioId}
              </Descriptions.Item>
              <Descriptions.Item label="终态" span={2}>
                <Tag color={executionTraceOutcomeTag(drawerExecution).color}>
                  {executionTraceOutcomeTag(drawerExecution).label}
                </Tag>
              </Descriptions.Item>
            </Descriptions>

            <div>
              <Divider orientation="left" plain style={{ marginTop: 0 }}>
                {OBSERVABILITY.drawerMc801Section}
              </Divider>
              <Mc801TimelineAudit timelineEvents={drawerExecution.timelineEvents} variant="plain" />
            </div>

            <div>
              <Divider orientation="left" plain>
                {OBSERVABILITY.narrativeDivider}
              </Divider>
              <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
                {OBSERVABILITY.narrativeHint}
              </Text>
              <Timeline items={drawerTimelineItems} />
            </div>

            <div>
              <Divider orientation="left" plain>
                {OBSERVABILITY.drawerToolsSection}
              </Divider>
              {drawerTools.length > 0 ? (
                <Table
                  size="small"
                  rowKey={(r) => `${r.executionId}-${r.toolCallSeq}`}
                  dataSource={drawerTools}
                  pagination={false}
                  columns={[
                    { title: "序号", dataIndex: "toolCallSeq", width: 56 },
                    { title: "工具", dataIndex: "toolId", ellipsis: true },
                    { title: "状态", dataIndex: "invocationState", width: 100, render: (s: string) => zhToolInvocation(s) },
                    { title: "时间", dataIndex: "at", width: 160 },
                  ]}
                />
              ) : (
                <Text type="secondary">{OBSERVABILITY.drawerToolsEmpty}</Text>
              )}
            </div>

            <div>
              <Divider orientation="left" plain>
                {OBSERVABILITY.drawerPromptSection}
              </Divider>
              <Text>{promptSummaryLine(drawerExecution)}</Text>
            </div>

            <div>
              <Divider orientation="left" plain>
                {OBSERVABILITY.drawerLlmSection}
              </Divider>
              {drawerLlms.length > 0 ? (
                drawerLlms.map((r) => (
                  <Card key={`${r.executionId}-${r.at}`} size="small" style={{ marginBottom: 8 }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {r.modelId} · tokens {r.inputTokens}+{r.outputTokens} · {r.at}
                    </Text>
                    <div style={{ marginTop: 8 }}>
                      <Text>{OBSERVABILITY.drawerLlmOutputPending}</Text>
                    </div>
                  </Card>
                ))
              ) : (
                <Text type="secondary">{OBSERVABILITY.drawerLlmEmpty}</Text>
              )}
            </div>

            <div>
              <Divider orientation="left" plain>
                {OBSERVABILITY.drawerRiskSection}
              </Divider>
              <Text>{riskHitSummary(drawerExecution)}</Text>
            </div>

            <div>
              <Divider orientation="left" plain>
                最终结果
              </Divider>
              <Tag color={executionTraceOutcomeTag(drawerExecution).color}>
                {executionTraceOutcomeTag(drawerExecution).label}
              </Tag>
              <Text style={{ marginLeft: 8 }}>{drawerExecution.intent}</Text>
            </div>
          </Space>
        ) : null}
      </Drawer>
    </ProductPageShell>
  );
}
