import { useCallback, useEffect, useMemo, useState } from "react";
import { ReloadOutlined, SearchOutlined } from "@ant-design/icons";
import {
  App,
  Button,
  Card,
  Col,
  Input,
  Row,
  Space,
  Statistic,
  Switch,
  Table,
  Tabs,
  Tag,
  Typography,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { ProductPageShell, useAdminTablePagination } from "../../components/product";
import {
  MOCK_SKILL_REGISTRY_ROWS,
  MOCK_TOOL_B_ROWS,
  MOCK_TOOL_C_ROWS,
  type ToolRegistryRow,
} from "../../data/toolRegistryMock";
import {
  loadToolRegistryState,
  persistToggle,
  resetToolRegistryDemo,
  type ToolRegistryStored,
} from "./toolRegistryStorage";
import { SkillOperationDrawer } from "./SkillOperationDrawer";
import { SkillRegistryTable } from "./SkillRegistryTable";
import { matrixStatusTag } from "./skillRegistryDisplay";
import {
  SKILL_REGISTRY_PAGE,
  SKILL_TABLE,
  TOOL_REGISTRY_TABLE,
} from "./skillRegistryUiCopy";

const { Paragraph, Text, Title } = Typography;

function isRowEnabled(row: ToolRegistryRow, store: ToolRegistryStored): boolean {
  return store.enabled[row.stableId] ?? row.defaultEnabled;
}

function RegistryTable({
  columns,
  data,
  store,
  paginationResetKey,
  rowClassName,
}: {
  columns: ColumnsType<ToolRegistryRow>;
  data: ToolRegistryRow[];
  store: ToolRegistryStored;
  paginationResetKey?: string;
  rowClassName?: (row: ToolRegistryRow) => string;
}) {
  const { pagination, slice } = useAdminTablePagination(data.length, { resetKey: paginationResetKey });
  const pageRows = slice(data);

  return (
    <Table<ToolRegistryRow>
      className="admin-tool-registry-table"
      size="middle"
      rowKey="stableId"
      pagination={pagination}
      bordered
      scroll={{ x: "max-content" }}
      columns={columns}
      dataSource={pageRows}
      locale={{ emptyText: SKILL_TABLE.empty }}
      rowClassName={(record) => rowClassName?.(record) ?? ""}
    />
  );
}

function renderRegistryTable(
  columns: ColumnsType<ToolRegistryRow>,
  data: ToolRegistryRow[],
  store: ToolRegistryStored,
  paginationResetKey?: string,
  rowClassName?: (row: ToolRegistryRow) => string,
) {
  return (
    <RegistryTable
      columns={columns}
      data={data}
      store={store}
      paginationResetKey={paginationResetKey}
      rowClassName={rowClassName}
    />
  );
}

export function ToolRegistryPage() {
  const { message } = App.useApp();
  const allRows = useMemo(
    () => [...MOCK_SKILL_REGISTRY_ROWS, ...MOCK_TOOL_B_ROWS, ...MOCK_TOOL_C_ROWS],
    [],
  );
  const defaultEnabledMap = useMemo(() => {
    const m: Record<string, boolean> = {};
    for (const r of allRows) m[r.stableId] = r.defaultEnabled;
    return m;
  }, [allRows]);
  const allIds = useMemo(() => allRows.map((r) => r.stableId), [allRows]);

  const [store, setStore] = useState<ToolRegistryStored>(() =>
    loadToolRegistryState(allIds, defaultEnabledMap),
  );
  const [detailSkillId, setDetailSkillId] = useState<string | null>(null);
  const [skillFilter, setSkillFilter] = useState("");

  const filteredSkillRows = useMemo(() => {
    const kw = skillFilter.trim().toLowerCase();
    if (!kw) return MOCK_SKILL_REGISTRY_ROWS;
    return MOCK_SKILL_REGISTRY_ROWS.filter(
      (r) =>
        r.stableId.toLowerCase().includes(kw) ||
        r.summary.toLowerCase().includes(kw) ||
        (r.userFlow ?? "").toLowerCase().includes(kw) ||
        (r.exchangeAction ?? "").toLowerCase().includes(kw),
    );
  }, [skillFilter]);

  const stats = useMemo(() => {
    const countOn = (rows: ToolRegistryRow[]) =>
      rows.filter((r) => isRowEnabled(r, store)).length;
    return {
      aOn: countOn(MOCK_SKILL_REGISTRY_ROWS),
      aTotal: MOCK_SKILL_REGISTRY_ROWS.length,
      bOn: countOn(MOCK_TOOL_B_ROWS),
      bTotal: MOCK_TOOL_B_ROWS.length,
      cOn: countOn(MOCK_TOOL_C_ROWS),
      cTotal: MOCK_TOOL_C_ROWS.length,
      audit: store.audit.length,
    };
  }, [store]);

  const onToggle = useCallback(
    (row: ToolRegistryRow, checked: boolean) => {
      if (row.matrixStatus === "tbd" && checked) {
        message.warning(SKILL_REGISTRY_PAGE.enableWarning);
      }
      setStore((prev) =>
        persistToggle({
          allIds,
          rowDefaults: defaultEnabledMap,
          stableId: row.stableId,
          entryClass: row.entryClass,
          enabled: checked,
          prev,
        }),
      );
    },
    [allIds, defaultEnabledMap, message],
  );

  const resetDemo = useCallback(() => {
    setStore(resetToolRegistryDemo(allIds, defaultEnabledMap));
    message.success(SKILL_REGISTRY_PAGE.resetSuccess);
  }, [allIds, defaultEnabledMap, message]);

  const openSkillDetail = useCallback((skillId: string) => {
    setDetailSkillId(skillId);
  }, []);

  const toolColumns: ColumnsType<ToolRegistryRow> = useMemo(
    () => [
      {
        title: TOOL_REGISTRY_TABLE.colTool,
        dataIndex: "stableId",
        key: "stableId",
        width: 260,
        render: (id: string, record) => (
          <>
            <Text strong>{record.summary}</Text>
            <br />
            <Text code copyable={{ text: id }} style={{ fontSize: 12 }}>
              {id}
            </Text>
          </>
        ),
      },
      {
        title: TOOL_REGISTRY_TABLE.colDesc,
        dataIndex: "anchor",
        key: "anchor",
        ellipsis: { showTitle: true },
        render: (t: string) => (
          <Text type="secondary" style={{ fontSize: 13 }}>
            {t}
          </Text>
        ),
      },
      {
        title: TOOL_REGISTRY_TABLE.colStatus,
        dataIndex: "matrixStatus",
        key: "matrixStatus",
        width: 96,
        align: "center",
        render: (s: ToolRegistryRow["matrixStatus"]) => matrixStatusTag(s),
      },
      {
        title: TOOL_REGISTRY_TABLE.colEnabled,
        key: "enabled",
        width: 88,
        align: "center",
        fixed: "right",
        render: (_: unknown, record) => (
          <Switch
            checked={isRowEnabled(record, store)}
            onChange={(c) => onToggle(record, c)}
            size="small"
          />
        ),
      },
    ],
    [onToggle, store],
  );

  const auditColumns: ColumnsType<ToolRegistryStored["audit"][0]> = [
    {
      title: TOOL_REGISTRY_TABLE.auditTime,
      dataIndex: "at",
      key: "at",
      width: 200,
      render: (t) => <Text code>{t}</Text>,
    },
    {
      title: TOOL_REGISTRY_TABLE.auditType,
      dataIndex: "entryClass",
      key: "c",
      width: 48,
      align: "center",
      render: (c: string) => (
        <Tag bordered={false} color={c === "A" ? "magenta" : c === "B" ? "blue" : "geekblue"}>
          {c}
        </Tag>
      ),
    },
    {
      title: TOOL_REGISTRY_TABLE.auditId,
      dataIndex: "stableId",
      key: "id",
      ellipsis: true,
      render: (id) => (
        <Text code copyable={{ text: id }}>
          {id}
        </Text>
      ),
    },
    {
      title: TOOL_REGISTRY_TABLE.auditAction,
      dataIndex: "enabled",
      key: "en",
      width: 72,
      align: "center",
      render: (e: boolean) =>
        e ? (
          <Tag bordered={false} color="processing">
            启用
          </Tag>
        ) : (
          <Tag bordered={false}>停用</Tag>
        ),
    },
    { title: TOOL_REGISTRY_TABLE.auditActor, dataIndex: "actor", key: "actor", width: 100 },
  ];

  return (
    <div className="admin-tool-registry-page">
      <ProductPageShell
        title={SKILL_REGISTRY_PAGE.title}
        pageId="ai.tool-registry"
        tags={
          <>
            <Tag color="processing">{SKILL_REGISTRY_PAGE.tagTrading}</Tag>
            <Tag>{SKILL_REGISTRY_PAGE.tagPreview}</Tag>
          </>
        }
        description={
          <Paragraph type="secondary" style={{ marginBottom: 0, maxWidth: 880 }}>
            {SKILL_REGISTRY_PAGE.description}
          </Paragraph>
        }
        extra={
          <Button icon={<ReloadOutlined />} onClick={resetDemo}>
            {SKILL_REGISTRY_PAGE.resetButton}
          </Button>
        }
      >
        <Row gutter={[12, 12]} className="admin-tool-registry-stats" style={{ marginBottom: 16 }}>
          <Col xs={12} sm={12} lg={6}>
            <Card size="small" className="admin-panel-card admin-tool-registry-stat-card">
              <Statistic
                title={SKILL_REGISTRY_PAGE.statTradingEnabled}
                value={stats.aOn}
                suffix={`/ ${stats.aTotal}`}
              />
            </Card>
          </Col>
          <Col xs={12} sm={12} lg={6}>
            <Card size="small" className="admin-panel-card admin-tool-registry-stat-card">
              <Statistic
                title={SKILL_REGISTRY_PAGE.statToolsEnabled}
                value={stats.bOn + stats.cOn}
                suffix={`/ ${stats.bTotal + stats.cTotal}`}
              />
            </Card>
          </Col>
          <Col xs={12} sm={12} lg={6}>
            <Card size="small" className="admin-panel-card admin-tool-registry-stat-card">
              <Statistic title={SKILL_REGISTRY_PAGE.statAudit} value={stats.audit} />
            </Card>
          </Col>
        </Row>

        <Card
          size="small"
          className="admin-panel-card"
          title={
            <Title level={5} style={{ margin: 0 }}>
              {SKILL_REGISTRY_PAGE.cardTitle}
            </Title>
          }
          styles={{ body: { paddingTop: 12 } }}
        >
          <Tabs
            className="admin-tool-registry-tabs"
            defaultActiveKey="skills"
            destroyInactiveTabPane
            items={[
              {
                key: "skills",
                label: (
                  <Space size={6}>
                    <span>{SKILL_REGISTRY_PAGE.tabTrading}</span>
                    <Tag bordered={false} color="magenta" style={{ marginInlineEnd: 0 }}>
                      {filteredSkillRows.length}
                      {skillFilter.trim() ? ` / ${MOCK_SKILL_REGISTRY_ROWS.length}` : ""}
                    </Tag>
                  </Space>
                ),
                children: (
                  <>
                    <Input
                      allowClear
                      prefix={<SearchOutlined style={{ color: "rgba(0,0,0,0.25)" }} />}
                      placeholder={SKILL_REGISTRY_PAGE.searchPlaceholder}
                      value={skillFilter}
                      onChange={(e) => setSkillFilter(e.target.value)}
                      style={{ maxWidth: 360, marginBottom: 12 }}
                    />
                    <SkillRegistryTable
                      rows={filteredSkillRows}
                      store={store}
                      activeSkillId={detailSkillId}
                      paginationResetKey={skillFilter}
                      onToggle={onToggle}
                      onOpenDrawer={openSkillDetail}
                    />
                  </>
                ),
              },
              {
                key: "tools-b",
                label: (
                  <Space size={6}>
                    <span>{SKILL_REGISTRY_PAGE.tabReadonly}</span>
                    <Tag bordered={false} color="blue" style={{ marginInlineEnd: 0 }}>
                      {MOCK_TOOL_B_ROWS.length}
                    </Tag>
                  </Space>
                ),
                children: renderRegistryTable(toolColumns, MOCK_TOOL_B_ROWS, store),
              },
              {
                key: "tools-c",
                label: (
                  <Space size={6}>
                    <span>{SKILL_REGISTRY_PAGE.tabExternal}</span>
                    <Tag bordered={false} color="geekblue" style={{ marginInlineEnd: 0 }}>
                      {MOCK_TOOL_C_ROWS.length}
                    </Tag>
                  </Space>
                ),
                children: renderRegistryTable(toolColumns, MOCK_TOOL_C_ROWS, store),
              },
              {
                key: "audit",
                label: (
                  <Space size={6}>
                    <span>{SKILL_REGISTRY_PAGE.tabAudit}</span>
                    {store.audit.length > 0 ? (
                      <Tag bordered={false} style={{ marginInlineEnd: 0 }}>
                        {store.audit.length}
                      </Tag>
                    ) : null}
                  </Space>
                ),
                children: (
                  <Table
                    className="admin-tool-registry-table"
                    size="middle"
                    bordered
                    rowKey={(r) => `${r.at}-${r.stableId}`}
                    pagination={{ pageSize: 10, showSizeChanger: false }}
                    columns={auditColumns}
                    dataSource={[...store.audit].reverse()}
                    locale={{ emptyText: TOOL_REGISTRY_TABLE.auditEmpty }}
                  />
                ),
              },
            ]}
          />
        </Card>

        <SkillOperationDrawer skillId={detailSkillId} onClose={() => setDetailSkillId(null)} />
      </ProductPageShell>
    </div>
  );
}
