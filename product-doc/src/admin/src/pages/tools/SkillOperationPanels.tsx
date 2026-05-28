import type { ReactNode } from "react";
import { Alert, Card, Col, Row, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { ConfirmRule, SkillOperationView, SpecTable } from "./parseSkillOperationView";
import {
  formatConfirmRuleLines,
  formatConfirmRuleTitle,
} from "./parseSkillOperationView";
import { SKILL_SPEC_EMPTY, SKILL_SPEC_NOTE, SKILL_SPEC_SECTION } from "./skillRegistryUiCopy";

const { Paragraph, Text } = Typography;

function tableToColumns(table: SpecTable): ColumnsType<string[]> {
  if (!table.headers.length) {
    return [{ title: "项", dataIndex: 0, key: "0", ellipsis: true }];
  }
  return table.headers.map((h, i) => ({
    title: h || `列${i + 1}`,
    dataIndex: i,
    key: String(i),
    ellipsis: true,
    width: i === 0 ? 120 : undefined,
    render: (cell: string) => (
      <span className="admin-skill-op-cell" title={cell}>
        {cell ?? "—"}
      </span>
    ),
  }));
}

export function SpecDataTable({ table }: { table: SpecTable }) {
  return (
    <Table
      className="admin-skill-op-table"
      size="small"
      bordered
      pagination={false}
      rowKey={(_, i) => String(i)}
      columns={tableToColumns(table)}
      dataSource={table.rows}
      scroll={{ x: "max-content" }}
    />
  );
}

export function SpecSectionCard({
  id,
  title,
  extra,
  table,
  empty,
  children,
}: {
  id?: string;
  title: string;
  extra?: ReactNode;
  table?: SpecTable;
  empty?: string;
  children?: ReactNode;
}) {
  const count = table?.rows.length ?? 0;
  const showEmpty = !children && table && count === 0;
  return (
    <Card
      id={id}
      size="small"
      className="admin-skill-op-card"
      title={
        <span className="admin-skill-op-card-title">
          {title}
          {count > 0 ? (
            <Text type="secondary" className="admin-skill-op-card-count">
              {count} 条
            </Text>
          ) : null}
        </span>
      }
      extra={extra}
    >
      {children}
      {table && count > 0 ? <SpecDataTable table={table} /> : null}
      {showEmpty ? <Text type="secondary">{empty ?? "无数据"}</Text> : null}
    </Card>
  );
}

export function ApiBlock({ text }: { text: string }) {
  const lines = text
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
  const bullets = lines.filter((l) => /^[-*•]/.test(l) || /^\d+\./.test(l));
  if (bullets.length >= 2) {
    return (
      <ul className="admin-skill-op-api-list">
        {lines.map((line, i) => (
          <li key={i}>
            <Text style={{ fontSize: 13 }}>{line.replace(/^[-*•]\s*/, "")}</Text>
          </li>
        ))}
      </ul>
    );
  }
  return <pre className="admin-skill-op-api-pre">{text}</pre>;
}

export function ConfirmOrchestrationNotes({ rules }: { rules: ConfirmRule[] }) {
  const visible = rules.filter((r) => r.title.trim() || r.body.trim());
  if (!visible.length) return null;

  return (
    <div className="admin-skill-op-rules-block">
      <Text type="secondary" className="admin-skill-op-rules-heading">
        {SKILL_SPEC_NOTE.orchestration}
      </Text>
      <ul className="admin-skill-op-rules-list">
        {visible.map((rule) => {
          const title = formatConfirmRuleTitle(rule.title);
          const lines = formatConfirmRuleLines(rule.body);
          const hintOnly =
            !lines.length && /须.*展示|可见/i.test(rule.title);

          return (
            <li key={`${rule.title}-${title}`} className="admin-skill-op-rule-item">
              <Text strong className="admin-skill-op-rule-title">
                {title}
              </Text>
              {hintOnly ? (
                <Text type="secondary" className="admin-skill-op-rule-hint">
                  见下方字段列表，须全部向用户展示清楚。
                </Text>
              ) : lines.length > 0 ? (
                <ul className="admin-skill-op-rule-lines">
                  {lines.map((line) => (
                    <li key={line}>
                      <Text className="admin-skill-op-rule-line">{line}</Text>
                    </li>
                  ))}
                </ul>
              ) : null}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export function ConfirmFieldList({ view }: { view: SkillOperationView }) {
  const col = view.confirmation.headers.findIndex((h) => /字段|项/.test(h));
  const idx = col >= 0 ? col : 0;
  const descCol = view.confirmation.headers.length > 1 ? (idx === 0 ? 1 : 0) : -1;
  return (
    <ul className="admin-skill-op-confirm-list">
      {view.confirmation.rows.map((row, i) => (
        <li key={i}>
          <Text strong>{row[idx] ?? row[0]}</Text>
          {descCol >= 0 && row[descCol] ? (
            <Text type="secondary" className="admin-skill-op-confirm-desc">
              {row[descCol]}
            </Text>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

export type SkillOperationPanelsProps = {
  view: SkillOperationView;
  showApi?: boolean;
};

/** 全量展示（演示控制台抽屉已改用分段切换） */
export function SkillOperationPanels({
  view,
  showApi = true,
}: SkillOperationPanelsProps) {
  return (
    <div className="admin-skill-operation-panels">
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <SpecSectionCard
            title={SKILL_SPEC_SECTION.params.title}
            table={view.requiredParams}
            empty={SKILL_SPEC_EMPTY.params}
          />
        </Col>
        <Col xs={24} lg={12}>
          <SpecSectionCard
            title={SKILL_SPEC_SECTION.confirm.title}
            empty={SKILL_SPEC_EMPTY.noConfirmFields}
          >
            {view.confirmRules.length > 0 ? (
              <ConfirmOrchestrationNotes rules={view.confirmRules} />
            ) : null}
            {view.confirmation.rows.length > 0 ? (
              <>
                <Text type="secondary" className="admin-skill-op-fields-heading">
                  确认卡须展示的字段
                </Text>
                <ConfirmFieldList view={view} />
              </>
            ) : null}
          </SpecSectionCard>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <SpecSectionCard
            title={SKILL_SPEC_SECTION.validation.title}
            table={view.validations}
            empty={SKILL_SPEC_EMPTY.validation}
          />
        </Col>
        <Col xs={24} md={12}>
          <SpecSectionCard
            title={SKILL_SPEC_SECTION.unknown.title}
            table={view.unknown}
            empty={SKILL_SPEC_EMPTY.unknown}
          />
        </Col>
      </Row>

      <SpecSectionCard
        title={SKILL_SPEC_SECTION.refusal.title}
        table={view.refusals}
        empty={SKILL_SPEC_EMPTY.refusal}
      />

      {showApi && view.apiText ? (
        <Card size="small" className="admin-skill-op-card" title={SKILL_SPEC_SECTION.api.title}>
          <ApiBlock text={view.apiText} />
        </Card>
      ) : null}
    </div>
  );
}
