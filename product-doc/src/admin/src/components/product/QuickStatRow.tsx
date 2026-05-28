import { Card, Col, Row, Statistic } from "antd";
import type { ReactNode } from "react";

export interface QuickStatItem {
  title: string;
  value: string | number;
  suffix?: string;
  prefix?: ReactNode;
  valueStyle?: React.CSSProperties;
}

/** 顶部 KPI 带，贴近运营后台「待办 / 汇总」心智 */
export function QuickStatRow({ items }: { items: QuickStatItem[] }) {
  return (
    <Row gutter={[16, 16]} style={{ marginBottom: 20 }} className="admin-stat-row">
      {items.map((it, i) => (
        <Col xs={24} sm={12} lg={6} key={`${it.title}-${i}`}>
          <Card
            size="small"
            className="admin-stat-card"
            bordered
            styles={{ body: { padding: "16px 20px" } }}
          >
            <Statistic
              title={<span className="admin-stat-title">{it.title}</span>}
              value={it.value}
              suffix={it.suffix}
              prefix={it.prefix}
              valueStyle={{ fontWeight: 600, ...it.valueStyle }}
            />
          </Card>
        </Col>
      ))}
    </Row>
  );
}
