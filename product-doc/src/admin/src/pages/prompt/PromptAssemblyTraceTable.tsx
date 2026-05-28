import { Table } from "antd";
import type { PromptAssemblyLayerRow } from "../../productionRuntime/promptBindingTimeline";
import { Link } from "react-router-dom";
import { promptPackEditorPath } from "./promptPaths";

export function PromptAssemblyTraceTable({ rows }: { rows: PromptAssemblyLayerRow[] }) {
  return (
    <Table
      size="small"
      pagination={false}
      rowKey="layer"
      columns={[
        { title: "层", dataIndex: "layer", width: 96 },
        {
          title: "来源",
          dataIndex: "source",
          ellipsis: true,
          render: (source: string, row: PromptAssemblyLayerRow) =>
            row.promptPackId ? (
              <Link to={promptPackEditorPath(row.promptPackId)}>{source}</Link>
            ) : (
              source
            ),
        },
      ]}
      dataSource={rows}
    />
  );
}
