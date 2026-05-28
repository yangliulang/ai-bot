import { useEffect } from "react";
import { Space, Switch, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useAdminTablePagination } from "../../components/product";
import type { ToolRegistryRow } from "../../data/toolRegistryTypes";
import type { ToolRegistryStored } from "./toolRegistryStorage";
import { warmSkillOperationCache } from "./skillOperationCache";
import {
  SkillExchangeCell,
  SkillIdentityCell,
  SkillUserFlowCell,
} from "./skillRegistryDisplay";
import { listScenariosForSkill } from "../governance/orchestration/scenarioSkillIndex";
import { SKILL_TABLE } from "./skillRegistryUiCopy";
import { Link } from "react-router-dom";

const { Text } = Typography;

function isRowEnabled(row: ToolRegistryRow, store: ToolRegistryStored): boolean {
  return store.enabled[row.stableId] ?? row.defaultEnabled;
}

export type SkillRegistryTableProps = {
  rows: ToolRegistryRow[];
  store: ToolRegistryStored;
  activeSkillId?: string | null;
  paginationResetKey?: string;
  onToggle: (row: ToolRegistryRow, checked: boolean) => void;
  onOpenDrawer: (skillId: string) => void;
};

export function SkillRegistryTable({
  rows,
  store,
  activeSkillId,
  paginationResetKey,
  onToggle,
  onOpenDrawer,
}: SkillRegistryTableProps) {
  const { pagination, slice } = useAdminTablePagination(rows.length, { resetKey: paginationResetKey });
  const pageRows = slice(rows);

  useEffect(() => {
    warmSkillOperationCache(true);
  }, []);

  const columns: ColumnsType<ToolRegistryRow> = [
    {
      title: SKILL_TABLE.colSkill,
      key: "identity",
      width: 260,
      render: (_: unknown, record) => <SkillIdentityCell row={record} />,
    },
    {
      title: SKILL_TABLE.colUserFlow,
      key: "flow",
      width: 280,
      render: (_: unknown, record) => <SkillUserFlowCell row={record} />,
    },
    {
      title: SKILL_TABLE.colExchange,
      key: "exchange",
      width: 220,
      render: (_: unknown, record) => <SkillExchangeCell row={record} />,
    },
    {
      title: SKILL_TABLE.colScenarios,
      key: "scenarios",
      width: 200,
      ellipsis: true,
      render: (_: unknown, record) => {
        const ids = listScenariosForSkill(record.stableId);
        if (!ids.length) {
          return (
            <Text type="secondary" style={{ fontSize: 11 }}>
              —
            </Text>
          );
        }
        const first = ids[0]!;
        return (
          <Space direction="vertical" size={0}>
            <Link
              to={`/ai/runtime-orchestration?scenario=${encodeURIComponent(first)}`}
              onClick={(e) => e.stopPropagation()}
            >
              <Text code style={{ fontSize: 11 }}>
                {first}
              </Text>
            </Link>
            {ids.length > 1 ? (
              <Text type="secondary" style={{ fontSize: 10 }}>
                +{ids.length - 1} 个场景
              </Text>
            ) : null}
          </Space>
        );
      },
    },
    {
      title: SKILL_TABLE.colEnabled,
      key: "enabled",
      width: 88,
      align: "center",
      fixed: "right",
      render: (_: unknown, record) => (
        <Switch
          checked={isRowEnabled(record, store)}
          onChange={(c) => onToggle(record, c)}
          size="small"
          onClick={(_, e) => e.stopPropagation()}
        />
      ),
    },
  ];

  return (
    <Table<ToolRegistryRow>
      className="admin-tool-registry-table admin-skill-registry-drawer-table"
      size="middle"
      rowKey="stableId"
      bordered
      pagination={pagination}
      scroll={{ x: "max-content" }}
      columns={columns}
      dataSource={pageRows}
      locale={{ emptyText: SKILL_TABLE.empty }}
      rowClassName={(record) =>
        [
          record.matrixStatus === "tbd" ? "admin-tool-registry-row--tbd" : "",
          "admin-skill-registry-row--clickable",
          activeSkillId === record.stableId
            ? "admin-skill-registry-row--active"
            : "",
        ]
          .filter(Boolean)
          .join(" ")
      }
      onRow={(record) => ({
        onClick: () => onOpenDrawer(record.stableId),
      })}
    />
  );
}
