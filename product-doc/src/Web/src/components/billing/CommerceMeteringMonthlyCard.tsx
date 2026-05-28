import { Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { MOCK_ME_COMMERCE_MONTHLY, type MeCommerceMonthlyMeteringRow } from "@/data/meCommerceConsumptionMock";

const { Paragraph } = Typography;

type Props = {
  compactLayout: boolean;
  embedded?: boolean;
};

export function CommerceMeteringMonthlyCard({ compactLayout, embedded = false }: Props) {
  const columns: ColumnsType<MeCommerceMonthlyMeteringRow> = [
    { title: "月份", dataIndex: "month", key: "month", width: 100 },
    {
      title: "核销合计",
      dataIndex: "entitlementDebits",
      key: "entitlementDebits",
      align: "right",
      width: 100,
      render: (n: number) => n.toLocaleString("zh-CN"),
    },
    {
      title: "分析",
      dataIndex: "analyzeDebits",
      key: "analyzeDebits",
      align: "right",
      width: 80,
      render: (n: number) => n.toLocaleString("zh-CN"),
    },
    {
      title: "交易",
      dataIndex: "tradeDebits",
      key: "tradeDebits",
      align: "right",
      width: 80,
      render: (n: number) => n.toLocaleString("zh-CN"),
    },
    {
      title: "成本观测",
      dataIndex: "tokensObserved",
      key: "tokensObserved",
      align: "right",
      width: 100,
      render: (n: number) => n.toLocaleString("zh-CN"),
    },
    {
      title: "状态",
      dataIndex: "notes",
      key: "notes",
      width: 88,
      render: (v: string) =>
        v === "进行中" ? <Tag color="processing">{v}</Tag> : <Tag bordered={false}>{v}</Tag>,
    },
  ];

  const table = (
    <Table
      size={compactLayout ? "small" : "middle"}
      pagination={false}
      rowKey="key"
      columns={columns}
      dataSource={MOCK_ME_COMMERCE_MONTHLY}
      scroll={{ x: "max-content" }}
    />
  );

  if (embedded) {
    return (
      <div className="coolbit-billing-tab-panel">
        <Paragraph type="secondary" className="coolbit-billing-tab-hint">
          按 Capability 核销次数汇总；成本观测列仅供参考，非扣款口径。
        </Paragraph>
        <div className="coolbit-billing-table-shell">{table}</div>
      </div>
    );
  }

  return (
    <div className="coolbit-billing-card coolbit-billing-card--block">
      <div className="coolbit-billing-card--block__title">月度 Capability 汇总</div>
      <Paragraph type="secondary" className="coolbit-billing-tab-hint">
        按 Capability 核销次数汇总；成本观测列仅供参考，非扣款口径。
      </Paragraph>
      <div className="coolbit-billing-table-shell">{table}</div>
    </div>
  );
}
