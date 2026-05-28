import { App, Button, Card, Popconfirm, Space, Table, Tabs, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { DeleteOutlined, EditOutlined, PlusOutlined, ReloadOutlined } from "@ant-design/icons";
import { useState } from "react";
import { zhCapabilitySku } from "../../copy/billingLabels";
import { BILLING_RULES } from "../../copy/opsPanelHints";
import type { BillingDebitRule, BillingScenarioMappingRow } from "../../data/billingRulesSeed";
import { useBillingDebitRules } from "../../hooks/useBillingDebitRules";
import { useCommerceAdminSnapshot } from "../../hooks/useCommerceAdminSnapshot";
import { useScenarioBillingMap } from "../../hooks/useScenarioBillingMap";
import { BillingDebitRulesDrawer } from "./BillingDebitRulesDrawer";
import { DebitRulesTable } from "./DebitRulesTable";
import { CommerceCapabilityCatalogEditor } from "./CommerceCapabilityCatalogEditor";
import { ScenarioMappingFormDrawer } from "./ScenarioMappingDrawers";
import {
  buildScenarioMappingTableRows,
  type ScenarioMappingTableRow,
} from "./scenarioMappingTableRows";

const { Text, Link: TypographyLink } = Typography;

type MappingPanelMode = "form" | null;

function debitRulesToApiRows(rules: BillingDebitRule[]) {
  return rules.map((r) => ({
    capabilitySkuId: r.capabilitySkuId,
    displayLabel: r.displayLabel,
    debitUnitsPerExecution: r.debitUnitsPerExecution,
  }));
}

export function BillingRulesPanel() {
  const { message } = App.useApp();
  const { rules: debitRules, upsertRules, resetToSeed: resetDebitRules } = useBillingDebitRules();
  const { rows: mappingRows, upsertRow, deleteRow, resetToSeed: resetMappingRows } = useScenarioBillingMap();
  const { snapshot: commerce, apiOn, reload } = useCommerceAdminSnapshot();

  const [debitDrawerOpen, setDebitDrawerOpen] = useState(false);
  const [apiEditorOpen, setApiEditorOpen] = useState(false);
  const [mappingMode, setMappingMode] = useState<MappingPanelMode>(null);
  const [mappingFormMode, setMappingFormMode] = useState<"create" | "edit">("create");
  const [selectedMapping, setSelectedMapping] = useState<BillingScenarioMappingRow | null>(null);

  const mappingTableRows = buildScenarioMappingTableRows(mappingRows);
  const existingScenarioIds = mappingRows.map((r) => r.scenarioId);

  const openMappingForm = (row: BillingScenarioMappingRow | null, mode: "create" | "edit") => {
    setSelectedMapping(row);
    setMappingFormMode(mode);
    setMappingMode("form");
  };

  const closeMapping = () => setMappingMode(null);

  const handleDeleteMapping = (scenarioId: string) => {
    deleteRow(scenarioId);
    message.success(BILLING_RULES.mappingDeleteSuccess);
    if (selectedMapping?.scenarioId === scenarioId) closeMapping();
  };

  const mappingColumns: ColumnsType<ScenarioMappingTableRow> = [
    {
      title: BILLING_RULES.colScenario,
      key: "scenario",
      ellipsis: true,
      render: (_, row) =>
        row.source === "auto" ? (
          <Space size="small">
            <Tag>{BILLING_RULES.mappingAutoTag}</Tag>
            <Text type="secondary">{row.scenarioPattern}</Text>
          </Space>
        ) : (
          <TypographyLink
            onClick={() => openMappingForm(row, "edit")}
            style={{ fontFamily: "monospace" }}
          >
            {row.scenarioId}
          </TypographyLink>
        ),
    },
    {
      title: BILLING_RULES.colCapability,
      dataIndex: "capabilitySkuId",
      render: (s: string) => zhCapabilitySku(s),
    },
    {
      title: BILLING_RULES.colActions,
      key: "actions",
      width: 88,
      render: (_, row) =>
        row.source === "custom" ? (
          <Space size="small">
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => openMappingForm(row, "edit")}
            />
            <Popconfirm
              title={BILLING_RULES.mappingDeleteConfirm}
              onConfirm={() => handleDeleteMapping(row.scenarioId)}
            >
              <Button type="link" size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Space>
        ) : (
          <Text type="secondary">—</Text>
        ),
    },
  ];

  const debitTab = (
    <Card size="small" className="admin-panel-card">
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12, flexWrap: "wrap", gap: 8 }}>
        <Text type="secondary" style={{ fontSize: 13 }}>
          {BILLING_RULES.debitRuleSectionHint}
        </Text>
        <Space wrap>
          <Tag>{BILLING_RULES.localPreviewTag}</Tag>
          <Popconfirm title={BILLING_RULES.debitResetConfirm} onConfirm={resetDebitRules}>
            <Button size="small" icon={<ReloadOutlined />}>
              {BILLING_RULES.debitResetSeed}
            </Button>
          </Popconfirm>
          <Button type="primary" size="small" icon={<EditOutlined />} onClick={() => setDebitDrawerOpen(true)}>
            {BILLING_RULES.debitEditButton}
          </Button>
        </Space>
      </div>
      <DebitRulesTable rules={debitRules} />
      <BillingDebitRulesDrawer
        open={debitDrawerOpen}
        rules={debitRules}
        onClose={() => setDebitDrawerOpen(false)}
        onSave={upsertRules}
        apiOn={apiOn}
        onPushApi={() => {
          setDebitDrawerOpen(false);
          setApiEditorOpen(true);
        }}
      />
      <CommerceCapabilityCatalogEditor
        open={apiEditorOpen}
        onClose={() => setApiEditorOpen(false)}
        snapshot={commerce}
        apiOn={apiOn}
        onSaved={() => void reload()}
        ruleRowsOverride={debitRulesToApiRows(debitRules)}
      />
    </Card>
  );

  const mappingTab = (
    <Card size="small" className="admin-panel-card">
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12, flexWrap: "wrap", gap: 8 }}>
        <Text type="secondary" style={{ fontSize: 13, maxWidth: 520 }}>
          {BILLING_RULES.mappingSectionHint}
        </Text>
        <Space wrap>
          <Tag>{BILLING_RULES.localPreviewTag}</Tag>
          <Popconfirm title={BILLING_RULES.mappingResetConfirm} onConfirm={resetMappingRows}>
            <Button size="small" icon={<ReloadOutlined />}>
              {BILLING_RULES.mappingResetSeed}
            </Button>
          </Popconfirm>
          <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => openMappingForm(null, "create")}>
            {BILLING_RULES.mappingCreateButton}
          </Button>
        </Space>
      </div>
      <Table
        rowKey="rowKey"
        size="small"
        pagination={{ pageSize: 12, hideOnSinglePage: true }}
        dataSource={mappingTableRows}
        columns={mappingColumns}
        onRow={(row) =>
          row.source === "auto"
            ? { style: { background: "var(--ant-color-fill-quaternary)" } }
            : {}
        }
      />
      <ScenarioMappingFormDrawer
        open={mappingMode === "form"}
        mode={mappingFormMode}
        row={mappingFormMode === "edit" ? selectedMapping : null}
        existingIds={existingScenarioIds}
        onClose={closeMapping}
        onSave={upsertRow}
      />
    </Card>
  );

  return (
    <Tabs
      defaultActiveKey="debit"
      items={[
        { key: "debit", label: BILLING_RULES.tabDebit, children: debitTab },
        { key: "mapping", label: BILLING_RULES.tabMapping, children: mappingTab },
      ]}
    />
  );
}
