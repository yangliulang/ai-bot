import { useCallback, useEffect, useMemo, useState } from "react";
import { Drawer, Modal, Space, Tag, Typography, theme, Button } from "antd";
import { ArrowRightOutlined, EyeOutlined } from "@ant-design/icons";
import { Link, useSearchParams } from "react-router-dom";
import {
  PagePrimaryButton,
  PageSecondaryButton,
  ProductPageShell,
  adminPeekPanelShellStyle,
} from "../../../components/product";
import { mockInstances } from "../../../data/mock";
import type { AgentInstance } from "../../../data/types";
import { buildObservabilitySearch } from "../../../utils/observabilityDeepLink";
import { agentStateTagColor, formatInstanceAt, runtimeStateTagColor } from "../../../utils/agentInstanceUi";
import { zhAgentState, zhRuntimeState } from "../../../copy/zhLabels";
import { filterInstanceRows } from "./instanceListFilters";
import { useAgentInstanceColumns } from "./instanceListColumns";
import { InstancesDataSection } from "./InstancesDataSection";
import { InstancesFilterPanel } from "./InstancesFilterPanel";
import { AgentGlobalGateBanner } from "../components/AgentGlobalGateBanner";
import { AGENT_INSTANCES } from "../../../copy/opsPanelHints";
import { isDemoGlobalAgentSwitchOn } from "../../../utils/demoGlobalAgentSwitch";

const { Text } = Typography;

function keywordFromSearchParams(searchParams: URLSearchParams): string {
  const q = searchParams.get("q")?.trim() ?? "";
  if (q) return q;
  const user = searchParams.get("user")?.trim() ?? "";
  const id = searchParams.get("id")?.trim() ?? "";
  return `${user}${user && id ? " " : ""}${id}`;
}

export function InstancesPage() {
  const { token } = theme.useToken();
  const [searchParams, setSearchParams] = useSearchParams();

  const qCommitted = useMemo(() => keywordFromSearchParams(searchParams), [searchParams]);
  const gateCommitted = searchParams.get("gate") ?? "all";
  const rtCommitted = searchParams.get("rt") ?? "all";

  const [keywordInput, setKeywordInput] = useState(qCommitted);
  const [gateDraft, setGateDraft] = useState(gateCommitted === "all" ? "all" : gateCommitted);
  const [rtDraft, setRtDraft] = useState(rtCommitted === "all" ? "all" : rtCommitted);
  const [userIdDraft, setUserIdDraft] = useState("");
  const [lastActiveFromDay, setLastActiveFromDay] = useState("");
  const [lastActiveToDay, setLastActiveToDay] = useState("");

  useEffect(() => {
    setKeywordInput(qCommitted);
    setGateDraft(gateCommitted === "all" ? "all" : gateCommitted);
    setRtDraft(rtCommitted === "all" ? "all" : rtCommitted);
  }, [qCommitted, gateCommitted, rtCommitted]);

  const filtered = useMemo(
    () =>
      filterInstanceRows(mockInstances, keywordInput, gateDraft || "all", rtDraft || "all", {
        userIdContains: userIdDraft,
        lastActiveFromDay: lastActiveFromDay || undefined,
        lastActiveToDay: lastActiveToDay || undefined,
      }),
    [keywordInput, gateDraft, rtDraft, userIdDraft, lastActiveFromDay, lastActiveToDay],
  );

  const sortedRows = useMemo(
    () => [...filtered].sort((a, b) => b.lastActiveAt.localeCompare(a.lastActiveAt)),
    [filtered],
  );

  const [preview, setPreview] = useState<AgentInstance | null>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  const globalAgentSwitchOn = isDemoGlobalAgentSwitchOn();

  useEffect(() => {
    setSelectedRowKeys([]);
  }, [keywordInput, gateDraft, rtDraft, userIdDraft, lastActiveFromDay, lastActiveToDay]);

  const onRuntimeQuick = useCallback((label: string) => {
    Modal.info({
      title: AGENT_INSTANCES.modalDemoTitle,
      content: AGENT_INSTANCES.runtimeQuickContent(label),
      okText: AGENT_INSTANCES.modalOk,
    });
  }, []);

  const rowSelection = useMemo(
    () => ({
      selectedRowKeys,
      onChange: (keys: React.Key[]) => setSelectedRowKeys(keys),
    }),
    [selectedRowKeys],
  );

  const onBatchPause = useCallback(() => {
    if (selectedRowKeys.length === 0) return;
    Modal.confirm({
      title: AGENT_INSTANCES.batchPauseTitle,
      content: AGENT_INSTANCES.batchPauseContent(selectedRowKeys.join("、")),
      okText: AGENT_INSTANCES.batchPauseOk,
      onOk: () => {
        Modal.success({
          title: AGENT_INSTANCES.modalDemoTitle,
          content: AGENT_INSTANCES.batchPauseDone,
          okText: AGENT_INSTANCES.modalOk,
        });
        setSelectedRowKeys([]);
      },
    });
  }, [selectedRowKeys]);

  const onBatchStop = useCallback(() => {
    if (selectedRowKeys.length === 0) return;
    Modal.confirm({
      title: AGENT_INSTANCES.batchStopTitle,
      content: AGENT_INSTANCES.batchStopContent(selectedRowKeys.join("、")),
      okText: AGENT_INSTANCES.batchStopOk,
      okButtonProps: { danger: true },
      onOk: () => {
        Modal.success({
          title: AGENT_INSTANCES.modalDemoTitle,
          content: AGENT_INSTANCES.batchStopDone,
          okText: AGENT_INSTANCES.modalOk,
        });
        setSelectedRowKeys([]);
      },
    });
  }, [selectedRowKeys]);

  const filtersActive = useMemo(
    () =>
      !!(
        keywordInput.trim() ||
        (gateDraft && gateDraft !== "all") ||
        (rtDraft && rtDraft !== "all") ||
        !!userIdDraft.trim() ||
        !!lastActiveFromDay.trim() ||
        !!lastActiveToDay.trim()
      ),
    [keywordInput, gateDraft, rtDraft, userIdDraft, lastActiveFromDay, lastActiveToDay],
  );

  const onExportListDemo = useCallback(() => {
    Modal.info({
      title: AGENT_INSTANCES.exportTitle,
      content: AGENT_INSTANCES.exportContent(sortedRows.length),
      okText: AGENT_INSTANCES.modalOk,
    });
  }, [sortedRows.length]);

  const resetFilters = useCallback(() => {
    setKeywordInput("");
    setGateDraft("all");
    setRtDraft("all");
    setUserIdDraft("");
    setLastActiveFromDay("");
    setLastActiveToDay("");
    setSearchParams(
      (prev) => {
        const n = new URLSearchParams(prev);
        n.delete("q");
        n.delete("user");
        n.delete("id");
        n.delete("gate");
        n.delete("rt");
        n.delete("tmpl");
        return n;
      },
      { replace: true },
    );
  }, [setSearchParams]);

  const onOpenPreview = useCallback((i: AgentInstance) => setPreview(i), []);

  const columns = useAgentInstanceColumns({
    onPreview: onOpenPreview,
    globalAgentSwitchOn,
    onRuntimeQuick,
  });

  return (
    <ProductPageShell
      pageId="ai.agents-instances"
      showPageId={false}
      title="实例管理"
      description={AGENT_INSTANCES.listDescription}
    >
      <AgentGlobalGateBanner />

      <InstancesFilterPanel
        resultCount={sortedRows.length}
        totalCount={mockInstances.length}
        keywordInput={keywordInput}
        gateDraft={gateDraft}
        rtDraft={rtDraft}
        onKeywordChange={setKeywordInput}
        onGateDraftChange={setGateDraft}
        onRtDraftChange={setRtDraft}
        onResetFilters={resetFilters}
        onExportListDemo={onExportListDemo}
        userIdDraft={userIdDraft}
        onUserIdDraftChange={setUserIdDraft}
        lastActiveFromDay={lastActiveFromDay}
        lastActiveToDay={lastActiveToDay}
        onLastActiveFromChange={setLastActiveFromDay}
        onLastActiveToChange={setLastActiveToDay}
      />

      <InstancesDataSection
        sortedRows={sortedRows}
        columns={columns}
        paginationResetKey={searchParams.toString()}
        filtersActive={filtersActive}
        onResetFilters={resetFilters}
        onOpenPreview={onOpenPreview}
        rowSelection={rowSelection}
        batchToolbar={
          selectedRowKeys.length > 0 ? (
            <Space wrap align="center">
              <Text type="secondary">{AGENT_INSTANCES.batchSelected(selectedRowKeys.length)}</Text>
              <PageSecondaryButton onClick={onBatchPause}>{AGENT_INSTANCES.batchPause}</PageSecondaryButton>
              <PageSecondaryButton danger onClick={onBatchStop}>
                {AGENT_INSTANCES.batchStop}
              </PageSecondaryButton>
              <Button type="link" size="small" onClick={() => setSelectedRowKeys([])}>
                清空选择
              </Button>
            </Space>
          ) : null
        }
      />

      <Drawer
        title="实例预览"
        placement="right"
        width={480}
        onClose={() => setPreview(null)}
        open={preview !== null}
        destroyOnClose
        styles={{ body: { paddingBottom: 24 } }}
        extra={
          preview ? (
            <Link to={`/agents/instances/${preview.instanceId}`}>
              <PagePrimaryButton icon={<ArrowRightOutlined />}>进入详情</PagePrimaryButton>
            </Link>
          ) : null
        }
      >
        {preview ? (
          <div>
            <div style={adminPeekPanelShellStyle(token)}>
              <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                实例 ID · 用户 UID
              </Text>
              <Text code copyable style={{ fontSize: 13 }}>
                {preview.instanceId}
              </Text>
              <div style={{ marginTop: 8 }}>
                <Text code copyable style={{ fontSize: 13 }}>
                  {preview.userId}
                </Text>
              </div>
              <Space wrap size={[8, 8]} style={{ marginTop: 10 }}>
                <Tag color={agentStateTagColor(preview.agentState)}>{zhAgentState(preview.agentState)}</Tag>
                <Tag color={runtimeStateTagColor(preview.runtimeState)}>{zhRuntimeState(preview.runtimeState)}</Tag>
              </Space>
            </div>

            <Space direction="vertical" size="middle" style={{ width: "100%" }}>
              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Telegram
                </Text>
                <div>
                  <Text strong>{preview.telegramUsername ?? "—"}</Text>
                  {preview.telegramNumericId ? (
                    <div>
                      <Text type="secondary" style={{ fontSize: 11 }}>
                        User ID{" "}
                      </Text>
                      <Text code copyable style={{ fontSize: 11 }}>
                        {preview.telegramNumericId}
                      </Text>
                    </div>
                  ) : null}
                </div>
              </div>
              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  子账户 UID
                </Text>
                <div>
                  <Text code copyable={!!preview.agentSubAccountUid} style={{ fontSize: 12 }}>
                    {preview.agentSubAccountUid ?? "—"}
                  </Text>
                </div>
              </div>
              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  阻断原因
                </Text>
                <div>{preview.lastProductBlockReason || "—"}</div>
              </div>
              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  最近活跃 · 创建
                </Text>
                <div>
                  {formatInstanceAt(preview.lastActiveAt)} · {formatInstanceAt(preview.createdAt)}
                </div>
              </div>

              <Link
                to={`/observability${buildObservabilitySearch({
                  userId: preview.userId,
                  tab: "execution",
                })}`}
              >
                <PagePrimaryButton icon={<EyeOutlined />} block>
                  执行链路协查
                </PagePrimaryButton>
              </Link>
              <Link to={`/runtime/executions`}>
                <PageSecondaryButton block>执行记录</PageSecondaryButton>
              </Link>
            </Space>
          </div>
        ) : null}
      </Drawer>
    </ProductPageShell>
  );
}
