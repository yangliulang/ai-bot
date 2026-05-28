import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import {
  Button,
  Card,
  Descriptions,
  Divider,
  Empty,
  Input,
  Modal,
  Space,
  Table,
  Tabs,
  Tag,
  Tooltip,
  Typography,
} from "antd";
import type { ButtonProps } from "antd";
import type { ColumnsType } from "antd/es/table";
import { ProductPageShell } from "../../components/product";
import {
  getInstance,
  getInstanceAuditRows,
  getObsExecutionsForUser,
  getObsToolRowsForExecution,
} from "../../data/mock";
import type {
  AgentInstance,
  AgentInstanceAuditRow,
  AgentInstanceBindingEventMock,
  MockObsExecutionRow,
  MockObsToolRow,
} from "../../data/types";
import { buildObservabilitySearch } from "../../utils/observabilityDeepLink";
import {
  agentStateTagColor,
  formatInstanceAt,
  runtimeStateTagColor,
} from "../../utils/agentInstanceUi";
import {
  getInstanceRuntimeActionUi,
  type RuntimeCommandKind,
} from "../../utils/agentInstanceRuntimeActions";
import { isDemoGlobalAgentSwitchOn } from "../../utils/demoGlobalAgentSwitch";
import { AgentGlobalGateBanner } from "./components/AgentGlobalGateBanner";
import { AGENT_INSTANCES } from "../../copy/opsPanelHints";
import {
  zhExecutionOutcome,
  zhRuntimeState,
  zhAgentState,
  zhToolInvocation,
  zhSubAccountStatus,
} from "../../copy/zhLabels";

function RuntimeActionButton({
  disabledReason,
  ...props
}: ButtonProps & { disabledReason?: string }) {
  const btn = <Button {...props} />;
  if (props.disabled && disabledReason) {
    return (
      <Tooltip title={disabledReason}>
        <span style={{ display: "inline-block" }}>{btn}</span>
      </Tooltip>
    );
  }
  return btn;
}

type MainTab = "overview" | "binding" | "params" | "logs" | "audit";
type LogSub = "conversation" | "tool" | "error";

const { Text } = Typography;

function parseMainTab(raw: string | null): MainTab | undefined {
  const ok: MainTab[] = ["overview", "binding", "params", "logs", "audit"];
  return raw && ok.includes(raw as MainTab) ? (raw as MainTab) : undefined;
}

function tradingApiFootnote(inst: AgentInstance): string | null {
  const snap = inst.bindingSnapshot;
  const parts: string[] = [];
  if (snap?.lastBindVerifiedAt) parts.push(`上次校验 ${formatInstanceAt(snap.lastBindVerifiedAt)}`);
  if (snap?.tradingApiBindingRevision) {
    const r = snap.tradingApiBindingRevision;
    parts.push(r.length > 36 ? `revision ${r.slice(0, 18)}…` : `revision ${r}`);
  }
  return parts.length > 0 ? parts.join(" · ") : null;
}

export function InstanceDetailPage() {
  const { instanceId } = useParams<{ instanceId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const inst = instanceId ? getInstance(instanceId) : undefined;
  const [tab, setTab] = useState<MainTab>(() => parseMainTab(searchParams.get("tab")) ?? "overview");
  const [logSub, setLogSub] = useState<LogSub>("conversation");

  useEffect(() => {
    const v = parseMainTab(searchParams.get("tab"));
    if (v) setTab(v);
  }, [searchParams]);

  const handleMainTabChange = useCallback(
    (k: string) => {
      const nk = k as MainTab;
      setTab(nk);
      setSearchParams(
        (prev) => {
          const n = new URLSearchParams(prev);
          if (nk === "overview") n.delete("tab");
          else n.set("tab", nk);
          return n;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  const a = inst?.appendix82;
  const obsExecs = inst ? getObsExecutionsForUser(inst.userId) : [];
  const auditRows = inst ? getInstanceAuditRows(inst.instanceId) : [];
  const latestExec = obsExecs[0];
  const toolRowsAll = useMemo(
    () => getObsExecutionsForUser(inst?.userId ?? "").flatMap((e) => getObsToolRowsForExecution(e.executionId)),
    [inst?.userId],
  );
  const errorRows = useMemo(
    () => getObsExecutionsForUser(inst?.userId ?? "").filter((e) => e.outcome !== "PER_EXECUTION_FINAL"),
    [inst?.userId],
  );

  const convCols: ColumnsType<MockObsExecutionRow> = [
    { title: "时间", dataIndex: "startedAt", key: "t" },
    { title: "方向", key: "dir", render: () => "用户→智能体" },
    {
      title: "摘要",
      key: "sum",
      render: (_, ex) => (
        <>
          {ex.scenarioId} · {zhExecutionOutcome(ex.outcome)}
        </>
      ),
    },
    {
      title: "执行 ID",
      dataIndex: "executionId",
      key: "eid",
      render: (id: string) => <Text code>{id}</Text>,
    },
    {
      title: "",
      key: "go",
      width: 88,
      render: (_, ex) => (
        <Link
          to={`/observability${buildObservabilitySearch({
            executionId: ex.executionId,
            userId: inst!.userId,
            tab: "execution",
          })}`}
        >
          执行链路协查
        </Link>
      ),
    },
  ];

  const toolCols: ColumnsType<MockObsToolRow> = [
    { title: "时间", dataIndex: "at", key: "at" },
    { title: "工具 ID", dataIndex: "toolId", key: "tid" },
    { title: "路径摘要", dataIndex: "pathSummary", key: "p" },
    { title: "状态", dataIndex: "invocationState", key: "s", render: (s: string) => zhToolInvocation(s) },
    {
      title: "执行 ID",
      dataIndex: "executionId",
      key: "eid",
      render: (id: string) => <Text code>{id}</Text>,
    },
  ];

  const errCols: ColumnsType<MockObsExecutionRow> = [
    { title: "时间", dataIndex: "startedAt", key: "t" },
    { title: "级别", key: "lv", render: () => "错误" },
    { title: "错误码", dataIndex: "outcome", key: "o", render: (o: string) => zhExecutionOutcome(o) },
    { title: "摘要", key: "sum", render: () => AGENT_INSTANCES.errSummary },
    {
      title: "执行 ID",
      dataIndex: "executionId",
      key: "eid",
      render: (id: string) => <Text code>{id}</Text>,
    },
    {
      title: "",
      key: "go",
      width: 72,
      render: (_, ex) => (
        <Link
          to={`/observability${buildObservabilitySearch({
            executionId: ex.executionId,
            userId: inst!.userId,
            tab: ex.outcome === "BILLING_BLOCKED" ? "billing" : "execution",
          })}`}
        >
          下钻
        </Link>
      ),
    },
  ];

  const bindingEventCols: ColumnsType<AgentInstanceBindingEventMock> = [
    {
      title: "时间",
      dataIndex: "at",
      key: "at",
      width: 148,
      render: (s: string) => formatInstanceAt(s),
    },
    {
      title: "事件",
      dataIndex: "event",
      key: "event",
      width: 168,
      render: (e: string) => (
        <Text code style={{ fontSize: 12 }}>
          {e}
        </Text>
      ),
    },
    { title: "摘要", dataIndex: "detail", key: "detail", ellipsis: true },
  ];

  const auditCols: ColumnsType<AgentInstanceAuditRow> = [
    { title: "时间", dataIndex: "at", key: "at", render: (s: string) => s.replace("T", " ").slice(0, 19) },
    { title: "操作者", dataIndex: "actor", key: "actor" },
    { title: "动作", dataIndex: "action", key: "action" },
    { title: "资源", dataIndex: "resource", key: "resource" },
  ];

  const globalAgentSwitchOn = isDemoGlobalAgentSwitchOn();

  const runtimeUi = useMemo(
    () => (inst ? getInstanceRuntimeActionUi(inst, { globalAgentSwitchOn }) : null),
    [inst, globalAgentSwitchOn],
  );

  const onRuntimeDemo = useCallback((label: string) => {
    Modal.info({
      title: AGENT_INSTANCES.modalDemoTitle,
      content: AGENT_INSTANCES.detailRuntimeQuick(label),
      okText: AGENT_INSTANCES.modalOk,
    });
  }, []);

  const onDeleteDemo = useCallback(() => {
    Modal.confirm({
      title: AGENT_INSTANCES.deleteConfirmTitle,
      content: AGENT_INSTANCES.deleteConfirmContent,
      okText: AGENT_INSTANCES.deleteConfirmOk,
      okButtonProps: { danger: true },
      onOk: () => {
        Modal.success({
          title: AGENT_INSTANCES.deleteDoneTitle,
          content: AGENT_INSTANCES.deleteDoneContent,
          okText: AGENT_INSTANCES.modalOk,
        });
      },
    });
  }, []);

  const runtimeActionButtons = useMemo(() => {
    const ui = runtimeUi;
    if (!ui) return null;
    const rows: Array<{
      key: string;
      label: string;
      kind: RuntimeCommandKind;
      disabled?: boolean;
      disabledReason?: string;
    }> = [];
    if (ui.showStart) {
      rows.push({
        key: "start",
        label: "启动",
        kind: "start",
        disabled: ui.disableStart,
        disabledReason: ui.startDisabledReason,
      });
    }
    if (ui.showPause) {
      rows.push({ key: "pause", label: "暂停", kind: "pause" });
    }
    if (ui.showResume) {
      rows.push({
        key: "resume",
        label: "恢复",
        kind: "resume",
        disabled: ui.disableResume,
        disabledReason: ui.resumeDisabledReason,
      });
    }
    if (ui.showStop) {
      rows.push({ key: "stop", label: "停止", kind: "stop" });
    }
    rows.sort((x, y) => {
      const px = ui.primary === x.kind ? 0 : 1;
      const py = ui.primary === y.kind ? 0 : 1;
      return px - py;
    });
    return rows.map((it) => (
      <RuntimeActionButton
        key={it.key}
        type={ui.primary === it.kind ? "primary" : "default"}
        disabled={it.disabled}
        disabledReason={it.disabledReason}
        onClick={() => onRuntimeDemo(it.label)}
      >
        {it.label}
      </RuntimeActionButton>
    ));
  }, [runtimeUi, onRuntimeDemo]);

  if (!inst || !a) {
    return (
      <ProductPageShell pageId="ai.agent-instance-detail" showPageId={false} title="实例详情">
        <Empty description={instanceId ? `未找到实例 · ${instanceId}` : "缺少实例 ID"}>
          <Link to="/agents/instances">
            <Button type="primary">返回实例管理</Button>
          </Link>
        </Empty>
      </ProductPageShell>
    );
  }

  const overridesJson = JSON.stringify(inst.instanceOverrides, null, 2);
  const bindingTradingFootnote = tradingApiFootnote(inst);

  const logsCard = (
    <Card className="admin-panel-card" title={AGENT_INSTANCES.logsCardTitle}>
      <Space wrap style={{ marginBottom: 12 }}>
        <Link
          to={`/observability${buildObservabilitySearch({
            executionId: latestExec?.executionId,
            userId: inst.userId,
            tab: "execution",
          })}`}
        >
          <Button type="primary">执行链路协查 · 时间线</Button>
        </Link>
        {latestExec && (
          <Button type="link" style={{ padding: 0 }}>
            <Link
              to={`/observability${buildObservabilitySearch({
                executionId: latestExec.executionId,
                userId: inst.userId,
                tab: "tool",
              })}`}
            >
              工具链
            </Link>
          </Button>
        )}
        {latestExec && (
          <Button type="link" style={{ padding: 0 }}>
            <Link
              to={`/observability${buildObservabilitySearch({
                executionId: latestExec.executionId,
                userId: inst.userId,
                tab: "billing",
              })}`}
            >
              计费协查
            </Link>
          </Button>
        )}
        {!latestExec && (
          <Button type="link" style={{ padding: 0 }}>
            <Link to={`/observability${buildObservabilitySearch({ userId: inst.userId })}`}>按用户协查</Link>
          </Button>
        )}
      </Space>
      <Tabs
        activeKey={logSub}
        onChange={(k) => setLogSub(k as LogSub)}
        items={[
          { key: "conversation", label: "会话" },
          { key: "tool", label: "工具" },
          { key: "error", label: "错误" },
        ]}
        style={{ marginBottom: 12 }}
      />
      {logSub === "conversation" &&
        (obsExecs.length === 0 ? (
          <Text type="secondary">{AGENT_INSTANCES.logsNoConv}</Text>
        ) : (
          <Table rowKey="executionId" columns={convCols} dataSource={obsExecs} pagination={false} size="small" />
        ))}
      {logSub === "tool" &&
        (toolRowsAll.length === 0 ? (
          <Text type="secondary">{AGENT_INSTANCES.logsNoTool}</Text>
        ) : (
          <Table
            rowKey={(r) => `${r.executionId}-${r.toolCallSeq}`}
            columns={toolCols}
            dataSource={toolRowsAll}
            pagination={false}
            size="small"
          />
        ))}
      {logSub === "error" &&
        (obsExecs.length === 0 ? (
          <Text type="secondary">
            {AGENT_INSTANCES.logsNoExec}{" "}
            <Link to={`/observability${buildObservabilitySearch({ userId: inst.userId })}`}>执行链路协查</Link>
          </Text>
        ) : errorRows.length === 0 ? (
          <Text type="secondary">{AGENT_INSTANCES.logsNoErrorAllOk}</Text>
        ) : (
          <Table rowKey="executionId" columns={errCols} dataSource={errorRows} pagination={false} size="small" />
        ))}
    </Card>
  );

  return (
    <ProductPageShell
      pageId="ai.agent-instance-detail"
      showPageId={false}
      title={inst.instanceId}
      description={<Text code>{inst.userId}</Text>}
      tags={
        <Space size={[6, 6]} wrap>
          <Tag color={runtimeStateTagColor(inst.runtimeState)}>{zhRuntimeState(inst.runtimeState)}</Tag>
          <Tag color={agentStateTagColor(inst.agentState)}>{zhAgentState(inst.agentState)}</Tag>
        </Space>
      }
      extra={
        <Space wrap align="center">
          {runtimeActionButtons}
          <RuntimeActionButton
            danger
            disabled={runtimeUi?.deleteDisabled ?? false}
            disabledReason={runtimeUi?.deleteDisabledReason}
            onClick={onDeleteDemo}
          >
            删除
          </RuntimeActionButton>
        </Space>
      }
    >
      <AgentGlobalGateBanner />
      <Tabs
        activeKey={tab}
        onChange={handleMainTabChange}
        items={[
          {
            key: "overview",
            label: "概览",
            children: (
              <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                <Card className="admin-panel-card" title="关键状态">
                  <Descriptions
                    bordered
                    size="small"
                    column={{ xs: 1, sm: 1, md: 2, lg: 2 }}
                    styles={{ label: { width: 148 } }}
                  >
                    <Descriptions.Item label="创建时间">{formatInstanceAt(inst.createdAt)}</Descriptions.Item>
                    <Descriptions.Item label="创建者">{inst.createdByDisplay ?? "—"}</Descriptions.Item>
                    <Descriptions.Item label="最近活跃">{formatInstanceAt(inst.lastActiveAt)}</Descriptions.Item>
                    <Descriptions.Item label="运行状态">
                      <Tag color={agentStateTagColor(inst.agentState)}>{zhAgentState(inst.agentState)}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="实例状态">
                      <Tag color={runtimeStateTagColor(inst.runtimeState)}>{zhRuntimeState(inst.runtimeState)}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label={AGENT_INSTANCES.subAccountListLabel}>
                      {zhSubAccountStatus(inst.subAccountStatus)}
                    </Descriptions.Item>
                    <Descriptions.Item label="产品阻断原因">{inst.lastProductBlockReason || "—"}</Descriptions.Item>
                  </Descriptions>
                </Card>

                <Card className="admin-panel-card" title={AGENT_INSTANCES.summaryCardTitle}>
                  <Descriptions
                    bordered
                    size="small"
                    column={{ xs: 1, sm: 1, md: 2, lg: 2 }}
                    styles={{ label: { width: 168 } }}
                  >
                    <Descriptions.Item label={AGENT_INSTANCES.membershipLabel}>
                      {a.vipTier} / {a.agentMinVipTier}
                    </Descriptions.Item>
                    <Descriptions.Item label="专用子账户 ID">
                      <Text code>{a.agentSubAccountId}</Text>
                    </Descriptions.Item>
                    <Descriptions.Item label="子账户状态">{a.agentSubAccountStatus}</Descriptions.Item>
                    <Descriptions.Item label="交易 API 绑定">
                      {a.agentTradingApiBindingStatus}{" "}
                      {a.agentTradingApiKeyId ? <Text code>{a.agentTradingApiKeyId}</Text> : null}
                    </Descriptions.Item>
                    <Descriptions.Item label={AGENT_INSTANCES.runtimeStateAppendix}>
                      <Tag color={agentStateTagColor(a.agentState)}>{zhAgentState(a.agentState)}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="最近产品阻断原因">{a.lastProductBlockReason || "—"}</Descriptions.Item>
                  </Descriptions>
                </Card>
              </Space>
            ),
          },
          {
            key: "binding",
            label: "绑定",
            children: (
              <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                <Card className="admin-panel-card" title={AGENT_INSTANCES.bindingCardTitle}>
                  <Text type="secondary" style={{ display: "block", marginBottom: 12 }}>
                    {AGENT_INSTANCES.bindingIntro}
                  </Text>

                  <Descriptions bordered size="small" column={{ xs: 1, sm: 2 }} styles={{ label: { width: 132 } }}>
                    <Descriptions.Item label="TG 账号">
                      {inst.telegramUsername ? <Text>{inst.telegramUsername}</Text> : <Text type="secondary">—</Text>}
                    </Descriptions.Item>
                    <Descriptions.Item label="TG User ID">
                      {inst.telegramNumericId ? (
                        <Text code copyable={{ text: inst.telegramNumericId }}>
                          {inst.telegramNumericId}
                        </Text>
                      ) : (
                        <Text type="secondary">—</Text>
                      )}
                    </Descriptions.Item>
                    <Descriptions.Item label="subUid">
                      {inst.agentSubAccountUid ? (
                        <Text code copyable={{ text: inst.agentSubAccountUid }}>
                          {inst.agentSubAccountUid}
                        </Text>
                      ) : (
                        "—"
                      )}
                    </Descriptions.Item>
                    <Descriptions.Item label="专用子账户 ID">
                      <Text code>{a.agentSubAccountId}</Text>
                    </Descriptions.Item>
                    <Descriptions.Item label="关联阶段" span={2}>
                      <Text type="secondary">
                        {zhSubAccountStatus(inst.subAccountStatus)}（{AGENT_INSTANCES.bindingLinkStage}） ·{" "}
                        {a.agentSubAccountStatus}（{AGENT_INSTANCES.bindingAppendixStage}）
                      </Text>
                    </Descriptions.Item>
                    <Descriptions.Item label="托管绑定" span={2}>
                      <Space direction="vertical" size={6} style={{ width: "100%" }}>
                        <Space wrap align="center">
                          <Tag>{a.agentTradingApiBindingStatus}</Tag>
                          {a.agentTradingApiKeyId ? (
                            <>
                              <Text type="secondary">Key</Text>
                              <Text code copyable={{ text: a.agentTradingApiKeyId }}>
                                {a.agentTradingApiKeyId}
                              </Text>
                            </>
                          ) : (
                            <Text type="secondary">未登记 Key ID</Text>
                          )}
                        </Space>
                        {bindingTradingFootnote ? (
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {bindingTradingFootnote}
                          </Text>
                        ) : null}
                      </Space>
                    </Descriptions.Item>
                  </Descriptions>

                  {inst.bindingSnapshot?.bindEventRows && inst.bindingSnapshot.bindEventRows.length > 0 ? (
                    <>
                      <Divider style={{ margin: "14px 0 10px" }} />
                      <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
                        {AGENT_INSTANCES.bindingEventsTitle}
                      </Text>
                      <Table
                        rowKey={(r, idx) => `${r.at}-${r.event}-${idx}`}
                        columns={bindingEventCols}
                        dataSource={inst.bindingSnapshot.bindEventRows}
                        pagination={false}
                        size="small"
                      />
                    </>
                  ) : (
                    <Text type="secondary" style={{ display: "block", marginTop: 14 }}>
                      {AGENT_INSTANCES.bindingNoEvents}
                    </Text>
                  )}
                </Card>
              </Space>
            ),
          },
          {
            key: "params",
            label: "参数",
            children: (
              <Card className="admin-panel-card" title={AGENT_INSTANCES.paramsCardTitle}>
                <Text type="secondary">{AGENT_INSTANCES.paramsIntro}</Text>
                <Input.TextArea
                  rows={10}
                  readOnly
                  value={overridesJson}
                  style={{ marginTop: 12, fontFamily: "monospace", fontSize: 12 }}
                />
              </Card>
            ),
          },
          { key: "logs", label: "日志", children: logsCard },
          {
            key: "audit",
            label: "审计",
            children: (
              <Card className="admin-panel-card" title={AGENT_INSTANCES.auditCardTitle}>
                {auditRows.length === 0 ? (
                  <Text type="secondary">{AGENT_INSTANCES.auditEmpty}</Text>
                ) : (
                  <Table
                    rowKey={(r) => `${r.at}-${r.action}`}
                    columns={auditCols}
                    dataSource={auditRows}
                    pagination={false}
                    size="small"
                  />
                )}
              </Card>
            ),
          },
        ]}
      />

    </ProductPageShell>
  );
}
