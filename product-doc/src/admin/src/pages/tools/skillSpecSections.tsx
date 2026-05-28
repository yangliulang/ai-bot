import type { ReactNode } from "react";
import { Card, Col, Row, Typography } from "antd";
import type { SkillOperationView, SpecTable } from "./parseSkillOperationView";
import {
  ApiBlock,
  ConfirmFieldList,
  ConfirmOrchestrationNotes,
  SpecDataTable,
  SpecSectionCard,
} from "./SkillOperationPanels";
import {
  SKILL_OVERVIEW_METRICS,
  SKILL_SPEC_EMPTY,
  SKILL_SPEC_SECTION,
  type SkillSpecSectionKey,
} from "./skillRegistryUiCopy";

const { Text } = Typography;

export const SKILL_SPEC_SECTIONS: {
  key: SkillSpecSectionKey;
  label: string;
  count: (view: SkillOperationView) => number;
}[] = [
  {
    key: "params",
    label: SKILL_SPEC_SECTION.params.label,
    count: (v) => v.requiredParams.rows.length,
  },
  {
    key: "validation",
    label: SKILL_SPEC_SECTION.validation.label,
    count: (v) => v.validations.rows.length,
  },
  {
    key: "confirm",
    label: SKILL_SPEC_SECTION.confirm.label,
    count: (v) => v.confirmation.rows.length,
  },
  {
    key: "unknown",
    label: SKILL_SPEC_SECTION.unknown.label,
    count: (v) => v.unknown.rows.length,
  },
  {
    key: "refusal",
    label: SKILL_SPEC_SECTION.refusal.label,
    count: (v) => v.refusals.rows.length,
  },
  {
    key: "api",
    label: SKILL_SPEC_SECTION.api.label,
    count: (v) => (v.apiText?.trim() ? 1 : 0),
  },
];

export function SkillSpecSectionContent({
  section,
  view,
  showApi = true,
}: {
  section: SkillSpecSectionKey;
  view: SkillOperationView;
  showApi?: boolean;
}) {
  switch (section) {
    case "params":
      return (
        <SpecSectionCard
          title={SKILL_SPEC_SECTION.params.title}
          table={view.requiredParams}
          empty={SKILL_SPEC_EMPTY.params}
        />
      );
    case "validation":
      return (
        <SpecSectionCard
          title={SKILL_SPEC_SECTION.validation.title}
          table={view.validations}
          empty={SKILL_SPEC_EMPTY.validation}
        />
      );
    case "confirm":
      return (
        <SpecSectionCard title={SKILL_SPEC_SECTION.confirm.title} empty={SKILL_SPEC_EMPTY.confirm}>
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
          ) : (
            <Text type="secondary">{SKILL_SPEC_EMPTY.noConfirmFields}</Text>
          )}
        </SpecSectionCard>
      );
    case "unknown":
      return (
        <SpecSectionCard
          title={SKILL_SPEC_SECTION.unknown.title}
          table={view.unknown}
          empty={SKILL_SPEC_EMPTY.unknown}
        />
      );
    case "refusal":
      return (
        <SpecSectionCard
          title={SKILL_SPEC_SECTION.refusal.title}
          table={view.refusals}
          empty={SKILL_SPEC_EMPTY.refusal}
        />
      );
    case "api":
      if (!showApi || !view.apiText?.trim()) {
        return <Text type="secondary">{SKILL_SPEC_EMPTY.api}</Text>;
      }
      return (
        <Card size="small" className="admin-skill-op-card" title={SKILL_SPEC_SECTION.api.title}>
          <ApiBlock text={view.apiText} />
        </Card>
      );
    default:
      return null;
  }
}

export function countRequiredParams(view: SkillOperationView): number {
  return view.requiredParams.rows.filter((r) => (r[1] ?? "").includes("✓")).length;
}

export function SkillOverviewMetrics({ view }: { view: SkillOperationView }) {
  const items: { label: string; value: ReactNode }[] = [
    {
      label: SKILL_OVERVIEW_METRICS.required,
      value: `${countRequiredParams(view)} ${SKILL_OVERVIEW_METRICS.unitItem}`,
    },
    {
      label: SKILL_OVERVIEW_METRICS.validation,
      value: `${view.validations.rows.length} ${SKILL_OVERVIEW_METRICS.unitRule}`,
    },
    {
      label: SKILL_OVERVIEW_METRICS.confirm,
      value: `${view.confirmation.rows.length} ${SKILL_OVERVIEW_METRICS.unitItem}`,
    },
    {
      label: SKILL_OVERVIEW_METRICS.refusal,
      value: `${view.refusals.rows.length} ${SKILL_OVERVIEW_METRICS.unitRule}`,
    },
  ];
  return (
    <Row gutter={[8, 8]} className="admin-skill-drawer-metrics">
      {items.map((item) => (
        <Col key={item.label} xs={12} sm={6}>
          <div className="admin-skill-drawer-metric">
            <Text type="secondary" className="admin-skill-drawer-metric__label">
              {item.label}
            </Text>
            <Text strong className="admin-skill-drawer-metric__value">
              {item.value}
            </Text>
          </div>
        </Col>
      ))}
    </Row>
  );
}
