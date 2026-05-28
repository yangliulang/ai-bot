import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Button, Drawer, Flex, Input, Segmented, Space, Table, Tag, Tooltip, Typography, theme } from "antd";
import { EyeOutlined, FilterOutlined, SearchOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import {
  AdminFilterSurface,
  ADMIN_FILTER_CONTROL_SIZE,
  adminListPagination,
  PageSecondaryButton,
} from "../../../components/product";
import type { ScenarioCategory, ScenarioRegistryRow } from "./scenarioRegistryMock";
import {
  MOCK_SCENARIO_REGISTRY,
  opsRuntimeStatusColor,
  opsRuntimeStatusLabel,
  scenarioRiskTag,
} from "./scenarioRegistryMock";
import { resolveScenarioSkillScope } from "./skillScopeForScenario";
import { OrchestrationScenarioTechCollapse } from "./OrchestrationScenarioTechCollapse";
import { ScenarioSkillScopePanel } from "./ScenarioSkillScopePanel";
import { ORCHESTRATION_SCENARIO } from "../../../copy/opsPanelHints";

const { Text, Paragraph } = Typography;

const CATEGORY_LABEL: Record<ScenarioCategory | "all", string> = {
  all: "全部",
  read: "读侧与分析",
  write: "交易与委托",
  wealth: "理财",
  monitoring: "监控与自动化",
};

const CATEGORY_COLOR: Record<ScenarioCategory, string> = {
  read: "blue",
  write: "magenta",
  wealth: "gold",
  monitoring: "purple",
};

export function ScenarioRoutingTab({
  initialScenarioSearch = "",
  onClearScenarioParam,
}: {
  initialScenarioSearch?: string;
  /** 清空地址栏 `scenario=`（例如从执行页深链回来时） */
  onClearScenarioParam?: () => void;
}) {
  const { token } = theme.useToken();
  const [category, setCategory] = useState<ScenarioCategory | "all">("all");
  const [search, setSearch] = useState(initialScenarioSearch);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeRow, setActiveRow] = useState<ScenarioRegistryRow | null>(null);

  const clearFilters = useCallback(() => {
    setCategory("all");
    setSearch("");
    onClearScenarioParam?.();
  }, [onClearScenarioParam]);

  useEffect(() => {
    setSearch(initialScenarioSearch);
  }, [initialScenarioSearch]);

  const openDetail = useCallback((row: ScenarioRegistryRow) => {
    setActiveRow(row);
    setDrawerOpen(true);
  }, []);

  useEffect(() => {
    const id = initialScenarioSearch.trim();
    if (!id) return;
    const row = MOCK_SCENARIO_REGISTRY.find((r) => r.scenarioId === id);
    if (row) openDetail(row);
  }, [initialScenarioSearch, openDetail]);

  const filtered = useMemo(() => {
    let rows = MOCK_SCENARIO_REGISTRY;
    if (category !== "all") rows = rows.filter((r) => r.category === category);
    const q = search.trim().toLowerCase();
    if (q) {
      rows = rows.filter(
        (r) =>
          r.scenarioTitle.toLowerCase().includes(q) ||
          r.flowSummary.toLowerCase().includes(q) ||
          r.typicalGoal.toLowerCase().includes(q) ||
          r.scenarioId.toLowerCase().includes(q) ||
          r.flowAnchor.toLowerCase().includes(q) ||
          r.promptBindingHint.toLowerCase().includes(q) ||
          r.specRefs.some((p) => p.toLowerCase().includes(q)),
      );
    }
    return rows;
  }, [category, search]);

  const columns: ColumnsType<ScenarioRegistryRow> = [
    {
      title: "场景名称",
      dataIndex: "scenarioTitle",
      key: "title",
      width: 200,
      fixed: "left",
      ellipsis: true,
      render: (t: string, row) => (
        <Space direction="vertical" size={0}>
          <Text strong style={{ fontSize: 13 }}>
            {t}
          </Text>
          <Text type="secondary" style={{ fontSize: 11 }}>
            {row.typicalGoal}
          </Text>
        </Space>
      ),
    },
    {
      title: "类型",
      dataIndex: "category",
      key: "cat",
      width: 120,
      render: (c: ScenarioCategory) => (
        <Tag color={CATEGORY_COLOR[c]} style={{ margin: 0 }}>
          {CATEGORY_LABEL[c]}
        </Tag>
      ),
    },
    {
      title: "执行流程",
      dataIndex: "flowSummary",
      key: "flow",
      ellipsis: true,
    },
    {
      title: "风险等级",
      dataIndex: "riskLevel",
      key: "risk",
      width: 100,
      render: (level: ScenarioRegistryRow["riskLevel"]) => {
        const { label, color } = scenarioRiskTag(level);
        return <Tag color={color}>{label}</Tag>;
      },
    },
    {
      title: "状态",
      dataIndex: "closureStatus",
      key: "st",
      width: 100,
      render: (s: ScenarioRegistryRow["closureStatus"]) => (
        <Tag color={opsRuntimeStatusColor(s)}>{opsRuntimeStatusLabel(s)}</Tag>
      ),
    },
    {
      title: "技能范围",
      key: "skillScope",
      width: 168,
      ellipsis: true,
      render: (_: unknown, row: ScenarioRegistryRow) => {
        const scope = resolveScenarioSkillScope(row.scenarioId, row.category);
        if (scope.mode === "write_skill" && scope.skills[0]) {
          return (
            <Text code style={{ fontSize: 11 }}>
              {scope.skills[0].skillId.replace("skill.", "")}
            </Text>
          );
        }
        if (scope.mode === "read_only") {
          return (
            <Text type="secondary" style={{ fontSize: 11 }}>
              只读 Tool
            </Text>
          );
        }
        return (
          <Text type="secondary" style={{ fontSize: 11 }}>
            未映射
          </Text>
        );
      },
    },
    {
      title: "最近执行",
      key: "trace",
      width: 88,
      fixed: "right",
      render: (_: unknown, row: ScenarioRegistryRow) => (
        <Link to={`/runtime/executions?scenario=${encodeURIComponent(row.scenarioId)}`}>查看</Link>
      ),
    },
    {
      title: "操作",
      key: "op",
      width: 72,
      fixed: "right",
      render: (_: unknown, row: ScenarioRegistryRow) => (
        <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => openDetail(row)}>
          详情
        </Button>
      ),
    },
  ];

  return (
    <>
      <AdminFilterSurface
        className="admin-scenario-query-surface"
        style={{ padding: "12px 16px", marginBottom: 16 }}
        title={
          <Space align="center" size={8} wrap>
            <FilterOutlined style={{ color: token.colorTextSecondary, fontSize: 15 }} aria-hidden />
            <Text strong style={{ fontSize: 15, color: token.colorText }}>
              筛选条件
            </Text>
          </Space>
        }
        extra={
          <Space wrap size={8} align="center">
            <Tag color="processing" style={{ margin: 0 }}>
              命中 {filtered.length} / {MOCK_SCENARIO_REGISTRY.length}
            </Tag>
            <Tooltip title="清空类型与关键词，并移除地址栏中的 scenario 参数">
              <PageSecondaryButton onClick={clearFilters}>重置</PageSecondaryButton>
            </Tooltip>
          </Space>
        }
      >
        <Flex vertical gap={12}>
          <Segmented<ScenarioCategory | "all">
            block
            value={category}
            onChange={(v) => setCategory(v)}
            options={[
              { label: CATEGORY_LABEL.all, value: "all" },
              { label: CATEGORY_LABEL.read, value: "read" },
              { label: CATEGORY_LABEL.write, value: "write" },
              { label: CATEGORY_LABEL.wealth, value: "wealth" },
              { label: CATEGORY_LABEL.monitoring, value: "monitoring" },
            ]}
          />
          <Input
            allowClear
            size={ADMIN_FILTER_CONTROL_SIZE}
            placeholder={ORCHESTRATION_SCENARIO.searchPlaceholder}
            prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </Flex>
      </AdminFilterSurface>

      <Table<ScenarioRegistryRow>
        rowKey="scenarioId"
        size="middle"
        scroll={{ x: 1280 }}
        pagination={adminListPagination({ pageSize: 12 })}
        columns={columns}
        dataSource={filtered}
      />

      <Drawer
        title={activeRow ? activeRow.scenarioTitle : "场景详情"}
        width={560}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        destroyOnClose
      >
        {activeRow ? (
          <>
            <Paragraph>
              <Text type="secondary">类型</Text>
              <div>
                <Tag color={CATEGORY_COLOR[activeRow.category]}>{CATEGORY_LABEL[activeRow.category]}</Tag>
              </div>
            </Paragraph>
            <Paragraph>
              <Text type="secondary">执行流程</Text>
              <div>{activeRow.flowSummary}</div>
            </Paragraph>
            <Paragraph>
              <Text type="secondary">风险等级</Text>
              <div>
                <Tag color={scenarioRiskTag(activeRow.riskLevel).color}>{scenarioRiskTag(activeRow.riskLevel).label}</Tag>
              </div>
            </Paragraph>
            <Paragraph>
              <Text type="secondary">运行状态</Text>
              <div>
                <Tag color={opsRuntimeStatusColor(activeRow.closureStatus)}>{opsRuntimeStatusLabel(activeRow.closureStatus)}</Tag>
              </div>
            </Paragraph>
            <Paragraph>
              <Text type="secondary">产品目标（细）</Text>
              <div>{activeRow.typicalGoal}</div>
            </Paragraph>

            <Paragraph>
              <Text type="secondary">{ORCHESTRATION_SCENARIO.labelPromptHint}</Text>
              <div style={{ fontSize: 12 }}>{activeRow.promptBindingHint}</div>
            </Paragraph>

            <ScenarioSkillScopePanel
              scenarioId={activeRow.scenarioId}
              category={activeRow.category}
              showIntroAlert
            />

            <OrchestrationScenarioTechCollapse row={activeRow} />

            <Paragraph style={{ marginTop: 16 }}>
              <Space wrap>
                <Link to={`/runtime/executions?scenario=${encodeURIComponent(activeRow.scenarioId)}`}>最近执行</Link>
                <Link to="/ai/tool-registry">技能与工具登记册</Link>
                <Link to={`/ai/prompt-strategy`}>提示词治理</Link>
                <Link to={`/ai/runtime-orchestration?tab=policy`}>执行策略</Link>
              </Space>
            </Paragraph>
          </>
        ) : null}
      </Drawer>
    </>
  );
}
