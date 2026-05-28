import { Card, Table, Tabs } from "antd";
import type { ColumnsType } from "antd/es/table";
import { EXECUTION_DETAIL } from "../../copy/opsPanelHints";
import type { MockObsBillingRow, MockObsLlmRow, MockObsToolRow } from "../../data/types";

type Props = {
  tools: MockObsToolRow[];
  llms: MockObsLlmRow[];
  billing: MockObsBillingRow[];
  toolCols: ColumnsType<MockObsToolRow>;
  llmCols: ColumnsType<MockObsLlmRow>;
  billCols: ColumnsType<MockObsBillingRow>;
};

export function ExecutionDetailUsageTabs({ tools, llms, billing, toolCols, llmCols, billCols }: Props) {
  return (
    <Card size="small" className="admin-panel-card" title={EXECUTION_DETAIL.usageCardTitle}>
      <Tabs
        size="small"
        items={[
          {
            key: "tools",
            label: `${EXECUTION_DETAIL.usageTabTools}（${tools.length}）`,
            children: (
              <Table
                size="small"
                rowKey={(r) => `${r.toolCallSeq}-${r.toolId}`}
                columns={toolCols}
                dataSource={tools}
                pagination={false}
                locale={{ emptyText: EXECUTION_DETAIL.toolsEmpty }}
                scroll={{ x: 720 }}
              />
            ),
          },
          {
            key: "llm",
            label: `${EXECUTION_DETAIL.usageTabLlm}（${llms.length}）`,
            children: (
              <Table
                size="small"
                rowKey={(r) => `${r.modelId}-${r.at}`}
                columns={llmCols}
                dataSource={llms}
                pagination={false}
                locale={{ emptyText: EXECUTION_DETAIL.llmEmpty }}
                scroll={{ x: 560 }}
              />
            ),
          },
          {
            key: "billing",
            label: `${EXECUTION_DETAIL.usageTabBilling}（${billing.length}）`,
            children: (
              <Table
                size="small"
                rowKey={(r) => r.billingTraceId}
                columns={billCols}
                dataSource={billing}
                pagination={false}
                locale={{ emptyText: EXECUTION_DETAIL.billingEmpty }}
                scroll={{ x: 780 }}
              />
            ),
          },
        ]}
      />
    </Card>
  );
}
