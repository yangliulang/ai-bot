import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  App,
  Button,
  Card,
  Descriptions,
  Empty,
  Modal,
  Space,
  Spin,
  Table,
  Tabs,
  Tag,
  Typography,
} from "antd";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { PROMPT_LIST_SOURCE, PROMPT_SAFETY } from "../../copy/opsPanelHints";
import {
  ApiOutlined,
  CheckCircleOutlined,
  FileTextOutlined,
  PlusOutlined,
  SafetyCertificateOutlined,
  StopOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import { ProductPageShell, PagePrimaryButton, PageSecondaryButton } from "../../components/product";
import { getPromptPack, mockPromptPacks } from "../../data/mock";
import type { MockPromptPack } from "../../data/types";
import { PromptPackDetailDrawer } from "./PromptPackDetailDrawer";
import { isPromptApiEnabled } from "../../api/http";
import { loadAllPromptPacks, loadEditorBootstrap, loadPackForDrawer } from "./promptRemote";
import { PromptPacksTable } from "./PromptPacksTable";
import { cloneToEphemeralBootstrap, persistEphemeralBootstrap } from "./promptEphemeral";
import { PromptCreateDraftModal } from "./PromptCreateDraftModal";
import { promptPackEditorPath } from "./promptPaths";
import {
  MOCK_RUNTIME_SAFETY_GOVERNANCE,
  MOCK_SAFETY_INTERCEPTS,
  MOCK_TOOL_SAFETY_POLICIES,
  TOOL_ENFORCEMENT_LABEL,
  type RuntimeSafetyGovernanceRow,
  type SafetyInterceptCategory,
  type SafetyInterceptRow,
  type ToolSafetyPolicyRow,
} from "./safetyCenterMock";

const { Text } = Typography;

type SafetyTabKey = "prompt" | "runtime" | "tool" | "session";

/** 顶层 Tab：安全策略 | 拦截记录 */
type SafetyPanelKey = "strategy" | "intercepts";

function isSafetyPanel(s: string | null): s is SafetyPanelKey {
  return s === "strategy" || s === "intercepts";
}

function isSafetyTab(s: string | null): s is SafetyTabKey {
  return s === "prompt" || s === "runtime" || s === "tool" || s === "session";
}

const CATEGORY_TAG: Record<SafetyInterceptCategory, { label: string; color: string }> = {
  runtime: { label: "运行时", color: "red" },
  prompt: { label: "Prompt", color: "blue" },
  tool: { label: "工具", color: "volcano" },
  session: { label: "会话", color: "purple" },
};

const TOOL_POLICY_LABEL: Record<ToolSafetyPolicyRow["policy"], string> = {
  deny: "禁止",
  allowlist: "白名单",
  shadow: "审计与降级",
};

export function PromptSafetyPage() {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const packId = searchParams.get("pack") ?? "";
  const panelRaw = searchParams.get("panel");
  const activePanel: SafetyPanelKey = isSafetyPanel(panelRaw) ? panelRaw : "strategy";
  const tabRaw = searchParams.get("tab");
  const activeTab: SafetyTabKey = isSafetyTab(tabRaw) ? tabRaw : "prompt";

  const [draftModalOpen, setDraftModalOpen] = useState(false);
  const [newRuleModalOpen, setNewRuleModalOpen] = useState(false);

  const [listRows, setListRows] = useState<MockPromptPack[] | null>(null);
  const [listSource, setListSource] = useState<string>("mock");
  const [listError, setListError] = useState<string | undefined>();
  const [drawerPack, setDrawerPack] = useState<MockPromptPack | undefined>();

  const reloadList = useCallback(() => {
    setListRows(null);
    loadAllPromptPacks()
      .then(({ rows, source, error, supplementedFromMock }) => {
        setListRows(rows);
        setListSource(source);
        if (error) {
          setListError(error);
        } else if (supplementedFromMock?.length) {
          setListError(PROMPT_LIST_SOURCE.mergeHint(supplementedFromMock.length));
        } else {
          setListError(undefined);
        }
      })
      .catch((e) => {
        setListRows(mockPromptPacks);
        setListSource("mock");
        message.error(String(e));
      });
  }, [message]);

  useEffect(() => {
    reloadList();
  }, [reloadList]);

  useEffect(() => {
    if (!packId) {
      setDrawerPack(undefined);
      return;
    }
    setDrawerPack(getPromptPack(packId));
    let cancelled = false;
    loadPackForDrawer(packId).then((p) => {
      if (!cancelled && p) setDrawerPack(p);
      if (!cancelled && !p && !getPromptPack(packId)) {
        setSearchParams(
          (prev) => {
            const n = new URLSearchParams(prev);
            n.delete("pack");
            return n;
          },
          { replace: true },
        );
      }
    });
    return () => {
      cancelled = true;
    };
  }, [packId, setSearchParams]);

  useEffect(() => {
    if (!packId || listRows === null) return;
    const inList = listRows.some((p) => p.promptPackId === packId);
    const inMock = !!getPromptPack(packId);
    if (!inList && !inMock && !isPromptApiEnabled()) {
      setSearchParams(
        (prev) => {
          const n = new URLSearchParams(prev);
          n.delete("pack");
          return n;
        },
        { replace: true },
      );
    }
  }, [packId, listRows, setSearchParams]);

  const openPack = useCallback(
    (p: MockPromptPack) => {
      setSearchParams((prev) => {
        const n = new URLSearchParams(prev);
        n.set("pack", p.promptPackId);
        return n;
      });
    },
    [setSearchParams],
  );

  const closePack = useCallback(() => {
    setSearchParams((prev) => {
      const n = new URLSearchParams(prev);
      n.delete("pack");
      return n;
    });
  }, [setSearchParams]);

  const onPanelChange = useCallback(
    (key: string) => {
      setSearchParams((prev) => {
        const n = new URLSearchParams(prev);
        if (key === "strategy") n.delete("panel");
        else n.set("panel", key);
        return n;
      });
    },
    [setSearchParams],
  );

  const onStrategyLayerTabChange = useCallback(
    (key: string) => {
      setSearchParams((prev) => {
        const n = new URLSearchParams(prev);
        if (key === "prompt") n.delete("tab");
        else n.set("tab", key);
        return n;
      });
    },
    [setSearchParams],
  );

  const data = useMemo(() => (listRows ?? []).filter((p) => p.kind === "SAFETY"), [listRows]);

  const packsForForkSafety = useMemo(() => {
    if (data.length > 0) return data;
    return mockPromptPacks.filter((p) => p.kind === "SAFETY");
  }, [data]);

  const interceptColumns: ColumnsType<SafetyInterceptRow> = [
    { title: "时间", dataIndex: "timeLabel", key: "t", width: 120 },
    {
      title: "类型",
      key: "cat",
      width: 88,
      render: (_: unknown, row) => (
        <Tag color={CATEGORY_TAG[row.category].color}>{CATEGORY_TAG[row.category].label}</Tag>
      ),
    },
    { title: "场景", dataIndex: "scenarioLabel", key: "sc", width: 200, ellipsis: true },
    { title: "事件", dataIndex: "kindLabel", key: "k", width: 120 },
    { title: "原因 / 处置", dataIndex: "reason", key: "r", ellipsis: true },
    {
      title: "对象",
      dataIndex: "subject",
      key: "s",
      width: 140,
      ellipsis: true,
      render: (s: string | undefined) => s ?? "—",
    },
  ];

  const toolColumns: ColumnsType<ToolSafetyPolicyRow> = [
    { title: "工具范围", dataIndex: "toolPattern", key: "tp", ellipsis: true },
    {
      title: "生效模式",
      dataIndex: "enforcementMode",
      key: "em",
      width: 110,
      render: (m: ToolSafetyPolicyRow["enforcementMode"]) => (
        <Tag color={m === "default_deny" ? "red" : m === "allowlist_only" ? "blue" : "orange"}>
          {TOOL_ENFORCEMENT_LABEL[m]}
        </Tag>
      ),
    },
    {
      title: "处置口径",
      dataIndex: "policy",
      key: "pol",
      width: 110,
      render: (p: ToolSafetyPolicyRow["policy"]) => (
        <Tag color={p === "deny" ? "red" : p === "allowlist" ? "blue" : "orange"}>{TOOL_POLICY_LABEL[p]}</Tag>
      ),
    },
    { title: "说明", dataIndex: "note", key: "n", ellipsis: true },
  ];

  const runtimeGovernanceColumns: ColumnsType<RuntimeSafetyGovernanceRow> = [
    { title: "治理项", dataIndex: "name", key: "nm", width: 200, ellipsis: true },
    {
      title: "风险等级",
      dataIndex: "riskLevelLabel",
      key: "rl",
      width: 92,
      render: (v: string) => (
        <Tag
          color={v === "高" ? "red" : v === "中" ? "orange" : v === "低" ? "green" : "default"}
        >
          {v}
        </Tag>
      ),
    },
    { title: "自动执行", dataIndex: "autoExecSummary", key: "ae", ellipsis: true },
    { title: "人工确认", dataIndex: "confirmSummary", key: "cf", ellipsis: true },
    { title: "熔断策略", dataIndex: "breakerSummary", key: "br", ellipsis: true },
    {
      title: "关联配置",
      key: "lnk",
      width: 108,
      render: (_: unknown, row) => {
        const meta: Record<
          RuntimeSafetyGovernanceRow["hrefKind"],
          { label: string; to: string }
        > = {
          confirmation: { label: "确认规则", to: "/ai/confirmation-rules" },
          policy: { label: "风险与策略", to: "/ai/runtime-orchestration?tab=policy" },
          routing: { label: "运行场景", to: "/ai/runtime-orchestration?tab=routing" },
        };
        const m = meta[row.hrefKind];
        return (
          <Link to={m.to}>
            {m.label}
          </Link>
        );
      },
    },
  ];

  return (
    <ProductPageShell
      pageId="ai.prompt-safety"
      showPageId={false}
      title="AI 安全治理"
      description="安全策略分层（Prompt、运行时、工具、会话）与拦截流水。"
      tags={
        listSource === "remote" ? (
          <Tag color="green">{PROMPT_LIST_SOURCE.tagRemote}</Tag>
        ) : listSource === "remote+mock-ssot" ? (
          <Tag color="blue">{PROMPT_LIST_SOURCE.tagRemoteMerged}</Tag>
        ) : listSource === "remote+fallback" ? (
          <Tag color="orange">{PROMPT_SAFETY.tagApiUnavailable}</Tag>
        ) : (
          <Tag color="purple">{PROMPT_LIST_SOURCE.tagMock}</Tag>
        )
      }
      extra={
        <Space>
          <PagePrimaryButton icon={<PlusOutlined />} onClick={() => setNewRuleModalOpen(true)}>
            新建安全规则
          </PagePrimaryButton>
          <PageSecondaryButton onClick={reloadList}>刷新</PageSecondaryButton>
        </Space>
      }
    >
      <Tabs
        activeKey={activePanel}
        onChange={onPanelChange}
        size="large"
        items={[
          {
            key: "strategy",
            label: (
              <span>
                <SafetyCertificateOutlined /> 安全策略
              </span>
            ),
            children: (
              <>
                {listError ? (
                  <Alert
                    type="warning"
                    showIcon
                    closable
                    banner
                    style={{ marginBottom: 12 }}
                    message={`${PROMPT_SAFETY.apiFallbackMessage}：${listError}`}
                    description={PROMPT_SAFETY.apiFallbackDescription}
                  />
                ) : null}

                <Tabs
                  activeKey={activeTab}
                  onChange={onStrategyLayerTabChange}
                  items={[
                    {
                      key: "prompt",
                      label: "Prompt 安全",
                      children: (
                        <Spin spinning={listRows === null}>
                          <Card
                            size="small"
                            className="admin-panel-card"
                            title={`护栏 Prompt（${data.length}）`}
                            styles={{ body: { minHeight: 120 } }}
                          >
                            {data.length === 0 ? (
                              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无 SAFETY 类 Prompt">
                                <Button type="primary" icon={<PlusOutlined />} onClick={() => setNewRuleModalOpen(true)}>
                                  新建安全规则
                                </Button>
                              </Empty>
                            ) : (
                              <PromptPacksTable
                                data={data}
                                onView={openPack}
                                showKindColumn={false}
                                listPagination
                              />
                            )}
                          </Card>
                        </Spin>
                      ),
                    },
                    {
                      key: "runtime",
                      label: (
                        <span>
                          <ThunderboltOutlined /> 运行时安全
                        </span>
                      ),
                      children: (
                        <Space direction="vertical" size={16} style={{ width: "100%" }}>
                          <Card size="small" className="admin-panel-card" title="运行时安全">
                            <Table<RuntimeSafetyGovernanceRow>
                              rowKey="key"
                              size="middle"
                              pagination={false}
                              columns={runtimeGovernanceColumns}
                              dataSource={MOCK_RUNTIME_SAFETY_GOVERNANCE}
                            />
                            <Space wrap size="middle" style={{ marginTop: 12 }}>
                              <Link to="/ai/confirmation-rules">人工确认规则</Link>
                              <Link to="/ai/runtime-orchestration?tab=policy">全局风险与执行策略</Link>
                              <Link to="/ai/runtime-orchestration?tab=routing">运行场景目录</Link>
                            </Space>
                          </Card>
                        </Space>
                      ),
                    },
                    {
                      key: "tool",
                      label: (
                        <span>
                          <ApiOutlined /> Tool 安全
                        </span>
                      ),
                      children: (
                        <Card size="small" className="admin-panel-card" title="工具调用策略">
                          <Table<ToolSafetyPolicyRow>
                            rowKey="key"
                            size="middle"
                            pagination={false}
                            columns={toolColumns}
                            dataSource={MOCK_TOOL_SAFETY_POLICIES}
                          />
                          <Link to="/ai/runtime-orchestration" style={{ fontSize: 12, marginTop: 12, display: "inline-block" }}>
                            运行编排
                          </Link>
                        </Card>
                      ),
                    },
                    {
                      key: "session",
                      label: (
                        <span>
                          <SafetyCertificateOutlined /> Session 安全
                        </span>
                      ),
                      children: (
                        <Card size="small" className="admin-panel-card" title="会话与行为风控">
                          <Descriptions column={1} size="small" bordered>
                            <Descriptions.Item label="高频意图限速">
                              <Space>
                                <CheckCircleOutlined style={{ color: "var(--ant-color-success)" }} />
                                <span>同会话短窗口内重复高风险意图合并提示</span>
                              </Space>
                            </Descriptions.Item>
                            <Descriptions.Item label="异常行为检测">
                              <Space>
                                <StopOutlined style={{ color: "var(--ant-color-warning)" }} />
                                <span>短时多品种扫单、异常撤单比 — 标记并降级自动执行</span>
                              </Space>
                            </Descriptions.Item>
                            <Descriptions.Item label="会话维度熔断">
                              <Space>
                                <ThunderboltOutlined style={{ color: "var(--ant-color-info)" }} />
                                <span>连续拒答或工具失败率异常 — 临时收紧工具白名单</span>
                              </Space>
                            </Descriptions.Item>
                          </Descriptions>
                        </Card>
                      ),
                    },
                  ]}
                />

                <Text type="secondary" style={{ fontSize: 12, display: "block", marginTop: 16 }}>
                  非护栏类提示词见 <Link to="/prompts/strategy">提示词治理</Link>。
                </Text>
              </>
            ),
          },
          {
            key: "intercepts",
            label: (
              <span>
                <FileTextOutlined /> 拦截记录
              </span>
            ),
            children: (
              <Card size="small" className="admin-panel-card" title="拦截记录">
                <Table<SafetyInterceptRow>
                  rowKey="id"
                  size="middle"
                  pagination={{ pageSize: 10, showSizeChanger: false }}
                  columns={interceptColumns}
                  dataSource={MOCK_SAFETY_INTERCEPTS}
                />
              </Card>
            ),
          },
        ]}
      />

      <Modal
        title="新建安全规则"
        open={newRuleModalOpen}
        onCancel={() => setNewRuleModalOpen(false)}
        footer={null}
        width={520}
      >
        <Space direction="vertical" size={12} style={{ width: "100%" }}>
          <Card
            size="small"
            hoverable
            onClick={() => {
              setNewRuleModalOpen(false);
              setDraftModalOpen(true);
            }}
          >
            <Text strong>护栏 Prompt（SAFETY）</Text>
            <div style={{ marginTop: 8, fontSize: 13, color: "rgba(0,0,0,0.65)" }}>
              语义层防护，进入草稿编辑。
            </div>
          </Card>
          <Card
            size="small"
            hoverable
            onClick={() => {
              setNewRuleModalOpen(false);
              navigate("/ai/confirmation-rules/new");
            }}
          >
            <Text strong>人工确认规则</Text>
            <div style={{ marginTop: 8, fontSize: 13, color: "rgba(0,0,0,0.65)" }}>
              风险条件与确认动作。
            </div>
          </Card>
          <Card size="small">
            <Text strong>工具与会话策略</Text>
            <div style={{ marginTop: 8, fontSize: 13, color: "rgba(0,0,0,0.65)" }}>
              <Link to="/ai/runtime-orchestration">
                运行编排
              </Link>
            </div>
          </Card>
        </Space>
      </Modal>

      <PromptCreateDraftModal
        open={draftModalOpen}
        onClose={() => setDraftModalOpen(false)}
        title="新建 SAFETY 护栏草稿"
        fixedKind="SAFETY"
        templateRows={packsForForkSafety}
        onBlankCreate={(b) => {
          persistEphemeralBootstrap(b);
          setDraftModalOpen(false);
          navigate(promptPackEditorPath(b.pack.promptPackId));
          message.success("已创建 SAFETY 本地草稿");
        }}
        onCloneFromTemplate={async (templateId) => {
          const src = await loadEditorBootstrap(templateId);
          const next = cloneToEphemeralBootstrap(src);
          persistEphemeralBootstrap(next);
          setDraftModalOpen(false);
          navigate(promptPackEditorPath(next.pack.promptPackId));
          message.success("已从模板复制为新的本地 SAFETY 草稿");
        }}
      />

      <PromptPackDetailDrawer open={!!packId && !!drawerPack} pack={drawerPack ?? null} onClose={closePack} />
    </ProductPageShell>
  );
}
