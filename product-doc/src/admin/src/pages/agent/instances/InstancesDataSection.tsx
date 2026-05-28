import { Empty, Typography, theme } from "antd";
import type { ColumnsType, TableProps } from "antd/es/table";
import type { ReactNode } from "react";
import { AdminPrimaryListTable, AdminTablePanel, PagePrimaryButton } from "../../../components/product";
import type { AgentInstance } from "../../../data/types";
import { AGENT_INSTANCE_LIST_SCROLL_X } from "./instanceListColumns";

const { Text } = Typography;

export type InstancesDataSectionProps = {
  sortedRows: AgentInstance[];
  columns: ColumnsType<AgentInstance>;
  /** 筛选 / URL 变化时重置表格分页 */
  paginationResetKey?: string;
  filtersActive: boolean;
  /** 重置筛选项（清空条件 + URL） */
  onResetFilters: () => void;
  onOpenPreview: (row: AgentInstance) => void;
  rowSelection?: TableProps<AgentInstance>["rowSelection"];
  /** 批量条（选中 ≥1 时由页组装） */
  batchToolbar?: ReactNode;
};

export function InstancesDataSection({
  sortedRows,
  columns,
  paginationResetKey,
  filtersActive,
  onResetFilters,
  onOpenPreview,
  rowSelection,
  batchToolbar,
}: InstancesDataSectionProps) {
  const { token } = theme.useToken();

  return (
    <div
      className="admin-instances-data-section"
      style={{
        marginTop: 8,
        paddingTop: 16,
        borderTop: `1px solid ${token.colorBorderSecondary}`,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "8px 16px",
          marginBottom: 12,
        }}
      >
        <Text strong style={{ fontSize: 15, color: token.colorText }}>
          数据列表
        </Text>
        <Text type="secondary" style={{ fontSize: 12 }}>
          共 {sortedRows.length} 条
        </Text>
      </div>

      {batchToolbar ? <div style={{ marginBottom: 12 }}>{batchToolbar}</div> : null}

      <AdminTablePanel marginTop={0}>
        <AdminPrimaryListTable<AgentInstance>
          rowKey="instanceId"
          columns={columns}
          dataSource={sortedRows}
          paginationResetKey={paginationResetKey}
          rowSelection={rowSelection}
          scroll={{ x: AGENT_INSTANCE_LIST_SCROLL_X }}
          locale={{
            emptyText: filtersActive ? (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="没有符合当前筛选条件的实例">
                <PagePrimaryButton onClick={onResetFilters}>重置筛选</PagePrimaryButton>
              </Empty>
            ) : (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无实例数据" />
            ),
          }}
          onRow={(record) => ({
            onClick: () => onOpenPreview(record),
            style: { cursor: "pointer" },
          })}
        />
      </AdminTablePanel>
    </div>
  );
}
