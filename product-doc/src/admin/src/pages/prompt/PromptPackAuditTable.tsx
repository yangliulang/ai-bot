import { Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { MockPromptAuditRow } from "../../data/types";

const { Text } = Typography;

const auditCols: ColumnsType<MockPromptAuditRow> = [
  {
    title: "时间",
    dataIndex: "at",
    width: 154,
    render: (s: string) => s.replace("T", " ").slice(0, 19),
  },
  { title: "操作者", dataIndex: "actor", ellipsis: true },
  { title: "动作", dataIndex: "action", width: 148, ellipsis: true },
  {
    title: "详情",
    dataIndex: "detail",
    ellipsis: { showTitle: true },
    render: (d: string) =>
      d ? (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {d}
        </Text>
      ) : (
        "—"
      ),
  },
];

export function PromptPackAuditTable({
  rows,
  title = "审计尾表（摘录）",
}: {
  rows: MockPromptAuditRow[];
  title?: string;
}) {
  return (
    <>
      <Text strong style={{ fontSize: 13, display: "block", margin: "14px 0 8px" }}>
        {title}
      </Text>
      <Table<MockPromptAuditRow>
        size="small"
        rowKey={(r) => `${r.at}-${r.action}-${r.actor}`}
        pagination={false}
        columns={auditCols}
        dataSource={rows}
        locale={{ emptyText: "暂无审计记录（接入 API 后与清单对签）" }}
      />
    </>
  );
}
