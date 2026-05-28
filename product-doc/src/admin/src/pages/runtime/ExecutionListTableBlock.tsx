import { Table } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useAdminTablePagination } from "../../components/product";
import type { MockObsExecutionRow } from "../../data/types";

function shouldIgnoreRowClick(target: HTMLElement): boolean {
  return Boolean(target.closest('a, button, input, select, textarea, [role="button"], .ant-typography-copy, .ant-select-selector'));
}

export function ExecutionListTableBlock({
  columns,
  dataSource,
  loading,
  paginationResetKey,
  onRowPreview,
}: {
  columns: ColumnsType<MockObsExecutionRow>;
  dataSource: MockObsExecutionRow[];
  loading?: boolean;
  paginationResetKey?: string;
  /** 单击行预览；点击链接/按钮/复制等控件不会触发 */
  onRowPreview?: (row: MockObsExecutionRow) => void;
}) {
  const { pagination, slice } = useAdminTablePagination(dataSource.length, { resetKey: paginationResetKey });
  const pageRows = slice(dataSource);

  return (
    <div className="admin-runtime-execution-table-host">
      <Table<MockObsExecutionRow>
        rowKey="executionId"
        columns={columns}
        dataSource={pageRows}
        loading={loading}
        pagination={pagination}
        size="middle"
        scroll={{ x: 1320, y: "calc(100vh - 392px)" }}
        locale={{ emptyText: "暂无匹配数据，可尝试放宽或重置筛选条件。" }}
        onRow={
          onRowPreview
            ? (record) => ({
                className: "admin-runtime-execution-table-row-interactive",
                onClick: (e) => {
                  if (!(e.target instanceof HTMLElement)) return;
                  if (shouldIgnoreRowClick(e.target)) return;
                  onRowPreview(record);
                },
              })
            : undefined
        }
      />
    </div>
  );
}
