import { useMemo } from "react";
import { Button, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { Link } from "react-router-dom";
import { ADMIN_PRIMARY_TABLE_PROPS, useAdminTablePagination } from "../../components/product";
import type { MockPromptPack } from "../../data/types";
import { PromptPackIdText } from "./promptIdDisplay";
import { zhPromptPackKind, zhPromptPackLockState } from "../../copy/zhLabels";
import { promptPackLifecycleSummary } from "./promptLifecycle";
import { promptPackEditorPath } from "./promptPaths";
import { PROMPT_TABLE, formatRuntimeSkillScopeCell } from "./promptManagementUiCopy";

const { Text } = Typography;

function kindTagColor(k: MockPromptPack["kind"]) {
  if (k === "SYSTEM") return "blue";
  if (k === "TRADING") return "gold";
  if (k === "ANALYSIS") return "purple";
  return "red";
}

function showEffectiveBadge(p: MockPromptPack): boolean {
  return p.currentVersion != null && (p.lockState === "LOCKED" || p.lockState === "PUBLISHED");
}

function formatAt(iso?: string): string {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 16);
}

export function PromptPacksTable({
  data,
  onView,
  showKindColumn = true,
  rowClickOpensDetail = true,
  showPagination = true,
  bordered = false,
  listPagination = false,
  paginationResetKey,
  showLifecycleColumn = false,
}: {
  data: MockPromptPack[];
  onView: (p: MockPromptPack) => void;
  showKindColumn?: boolean;
  rowClickOpensDetail?: boolean;
  showPagination?: boolean;
  bordered?: boolean;
  listPagination?: boolean;
  paginationResetKey?: string;
  showLifecycleColumn?: boolean;
}) {
  const listPaginationOptions = listPagination
    ? {
        hideOnSinglePage: false as const,
        showSizeChanger: true,
        pageSizeOptions: [10, 15, 20, 50],
        showTotal: (total: number, range: [number, number]) =>
          `${range[0]}-${range[1]} / 共 ${total} 条`,
      }
    : undefined;

  const { pagination: tablePagination, slice } = useAdminTablePagination(data.length, {
    resetKey: paginationResetKey,
    ...listPaginationOptions,
  });

  const pageRows = showPagination ? slice(data) : data;

  const cols = useMemo(() => {
    const base: ColumnsType<MockPromptPack> = [
      {
        title: "Prompt ID",
        dataIndex: "promptPackId",
        width: 176,
        ellipsis: true,
        render: (id: string) => <PromptPackIdText promptPackId={id} />,
      },
      {
        title: "Prompt 名称",
        dataIndex: "title",
        ellipsis: true,
        width: 200,
        render: (t: string) => <span style={{ fontWeight: 500 }}>{t}</span>,
      },
    ];
    if (showKindColumn) {
      base.push({
        title: "类型",
        dataIndex: "kind",
        width: 100,
        render: (k: MockPromptPack["kind"]) => <Tag color={kindTagColor(k)}>{zhPromptPackKind(k)}</Tag>,
      });
    }
    base.push(
      {
        title: "版本",
        key: "ver",
        width: 128,
        render: (_, record) => (
          <Space size={8} wrap>
            <Text>{record.currentVersion != null ? `v${record.currentVersion}` : "—"}</Text>
            {showEffectiveBadge(record) ? (
              <Tag color="success" style={{ margin: 0 }}>
                生效
              </Tag>
            ) : null}
            {record.hasDraft ? (
              <Tag color="processing" style={{ margin: 0 }}>
                草稿
              </Tag>
            ) : null}
          </Space>
        ),
      },
      {
        title: "状态",
        dataIndex: "lockState",
        width: 88,
        ellipsis: true,
        render: (s: string) => zhPromptPackLockState(s),
      },
      {
        title: PROMPT_TABLE.colSkillScope,
        key: "skillScope",
        width: 220,
        ellipsis: true,
        render: (_, record) => {
          const cell = formatRuntimeSkillScopeCell(record);
          return (
            <div title={cell.title}>
              <Text style={{ fontSize: 12, display: "block" }}>{cell.primary}</Text>
              {cell.secondary ? (
                <Text type="secondary" style={{ fontSize: 11, display: "block" }}>
                  {cell.secondary}
                </Text>
              ) : null}
            </div>
          );
        },
      },
      ...(showLifecycleColumn
        ? [
            {
              title: "阶段",
              key: "lifecycle",
              width: 124,
              render: (_: unknown, record: MockPromptPack) => {
                const { label, color } = promptPackLifecycleSummary(record);
                return (
                  <Tag color={color} style={{ margin: 0 }}>
                    {label}
                  </Tag>
                );
              },
            } as ColumnsType<MockPromptPack>[number],
          ]
        : []),
      {
        title: "更新时间",
        dataIndex: "updatedAt",
        width: 136,
        render: (t?: string) => (
          <Text type="secondary" style={{ fontSize: 13 }}>
            {formatAt(t)}
          </Text>
        ),
      },
      {
        title: "操作",
        key: "op",
        width: 112,
        fixed: "right",
        render: (_, record) => (
          <Space size={8} onClick={(e) => e.stopPropagation()} wrap={false}>
            <Button type="link" size="small" style={{ padding: 0 }} onClick={() => onView(record)}>
              详情
            </Button>
            <Link to={promptPackEditorPath(record.promptPackId)} onClick={(e) => e.stopPropagation()}>
              <Button type="link" size="small" style={{ padding: 0 }}>
                编辑
              </Button>
            </Link>
          </Space>
        ),
      },
    );
    return base;
  }, [showKindColumn, onView, showLifecycleColumn]);

  return (
    <Table<MockPromptPack>
      rootClassName="admin-prompt-packs-table"
      size={ADMIN_PRIMARY_TABLE_PROPS.size}
      bordered={bordered}
      rowKey="promptPackId"
      pagination={showPagination ? tablePagination : false}
      dataSource={pageRows}
      columns={cols}
      scroll={{ x: showLifecycleColumn ? 1180 : 1000 }}
      locale={{ emptyText: "暂无 Prompt" }}
      onRow={
        rowClickOpensDetail
          ? (record) => ({
              onClick: () => onView(record),
              style: { cursor: "pointer" },
            })
          : undefined
      }
    />
  );
}
