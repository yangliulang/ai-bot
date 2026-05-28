import { RightOutlined } from "@ant-design/icons";
import { Button, Card, Col, Descriptions, Row, Space, Tag, Typography } from "antd";
import { Link } from "react-router-dom";
import type { SkillRegistryEntry } from "./skillRegistryCatalog";
import {
  resolveSkillContractStatus,
  resolveSkillSpecVersion,
  SKILL_REGISTRY_ENTRIES,
} from "./skillRegistryCatalog";
import type { SkillOperationView } from "./parseSkillOperationView";
import {
  ConfirmFieldList,
  ConfirmOrchestrationNotes,
  SpecDataTable,
} from "./SkillOperationPanels";
import {
  SKILL_DRAWER,
  SKILL_MATRIX_STATUS,
  SKILL_OVERVIEW_METRICS,
  SKILL_SPEC_SECTION,
  type SkillSpecSectionKey,
} from "./skillRegistryUiCopy";
import { countRequiredParams, SKILL_SPEC_SECTIONS, SkillOverviewMetrics } from "./skillSpecSections";
import { loadToolRegistryState } from "./toolRegistryStorage";
import { listScenariosForSkill } from "../governance/orchestration/scenarioSkillIndex";

const { Paragraph, Text } = Typography;

const REQUIRED_PREVIEW_MAX = 6;
const CONFIRM_RULE_PREVIEW_MAX = 4;

function resolveSkillEnabled(entry: SkillRegistryEntry): boolean {
  const store = loadToolRegistryState(
    SKILL_REGISTRY_ENTRIES.map((e) => e.skillId),
    Object.fromEntries(
      SKILL_REGISTRY_ENTRIES.map((e) => [e.skillId, e.defaultEnabled]),
    ),
  );
  return store.enabled[entry.skillId] ?? entry.defaultEnabled;
}

function contractStatusLabel(skillId: string, hasSpec: boolean): string {
  if (!hasSpec) return SKILL_DRAWER.contractNa;
  const st = resolveSkillContractStatus(skillId);
  if (st === "complete") return SKILL_DRAWER.contractComplete;
  if (st === "missing") return SKILL_DRAWER.contractIncomplete;
  return SKILL_DRAWER.contractNa;
}

export type SkillOperationOverviewProps = {
  entry: SkillRegistryEntry;
  view: SkillOperationView | null;
  onGoToSpec: (section?: SkillSpecSectionKey) => void;
};

export function SkillOperationOverview({
  entry,
  view,
  onGoToSpec,
}: SkillOperationOverviewProps) {
  const enabled = resolveSkillEnabled(entry);
  const version =
    view?.version ?? resolveSkillSpecVersion(entry.skillId) ?? "—";
  const scenarioId = view?.scenarioId?.trim() || "—";
  const linkedScenarios = listScenariosForSkill(entry.skillId);
  const confirmRules = view?.confirmRules ?? [];
  const requiredPreview = view
    ? {
        headers: view.requiredParams.headers,
        rows: view.requiredParams.rows.slice(0, REQUIRED_PREVIEW_MAX),
      }
    : null;
  const requiredTotal = view ? view.requiredParams.rows.length : 0;
  const requiredMore =
    requiredTotal > REQUIRED_PREVIEW_MAX
      ? requiredTotal - REQUIRED_PREVIEW_MAX
      : 0;

  return (
    <div className="admin-skill-drawer-tab-pane admin-skill-overview">
      <Descriptions
        className="admin-skill-overview-meta"
        size="small"
        bordered
        column={{ xs: 1, sm: 2 }}
        items={[
          {
            key: "skillId",
            label: SKILL_DRAWER.labelSkillId,
            children: (
              <Text code className="admin-skill-overview-code">
                {entry.skillId}
              </Text>
            ),
          },
          {
            key: "version",
            label: SKILL_DRAWER.labelVersion,
            children: version,
          },
          {
            key: "scenario",
            label: SKILL_DRAWER.labelScenario,
            children: scenarioId,
          },
          {
            key: "matrix",
            label: SKILL_DRAWER.labelMatrix,
            children: SKILL_MATRIX_STATUS[entry.matrixStatus],
          },
          {
            key: "enabled",
            label: SKILL_DRAWER.labelPreviewEnabled,
            children: (
              <Tag color={enabled ? "success" : "default"}>
                {enabled ? SKILL_DRAWER.enabledOn : SKILL_DRAWER.enabledOff}
              </Tag>
            ),
          },
          {
            key: "contract",
            label: SKILL_DRAWER.labelContract,
            children: contractStatusLabel(entry.skillId, Boolean(entry.specPath)),
          },
        ]}
      />

      {linkedScenarios.length > 0 ? (
        <Card size="small" className="admin-skill-drawer-overview-card">
          <Text type="secondary" className="admin-skill-drawer-label">
            适用 scenarioId（寄存器 · 只读）
          </Text>
          <Space direction="vertical" size={4} style={{ width: "100%" }}>
            {linkedScenarios.map((sid) => (
              <Link
                key={sid}
                to={`/ai/runtime-orchestration?scenario=${encodeURIComponent(sid)}`}
                style={{ fontSize: 12 }}
              >
                <Text code>{sid}</Text>
              </Link>
            ))}
          </Space>
        </Card>
      ) : null}

      {view?.businessLine ? (
        <Card size="small" className="admin-skill-drawer-overview-card admin-skill-overview-biz">
          <Text type="secondary" className="admin-skill-drawer-label">
            {SKILL_DRAWER.labelBusiness}
          </Text>
          <Paragraph className="admin-skill-drawer-prose" style={{ marginBottom: 0 }}>
            {view.businessLine}
          </Paragraph>
        </Card>
      ) : null}

      {view ? (
        <>
          <SkillOverviewMetrics view={view} />
          {requiredPreview && requiredPreview.rows.length > 0 ? (
            <Card
              size="small"
              className="admin-skill-drawer-overview-card"
              title={SKILL_SPEC_SECTION.params.title}
              extra={
                requiredMore > 0 ? (
                  <Button type="link" size="small" onClick={() => onGoToSpec("params")}>
                    {SKILL_DRAWER.viewAllParams(requiredMore)}
                  </Button>
                ) : null
              }
            >
              <SpecDataTable
                table={{
                  headers: requiredPreview.headers,
                  rows: requiredPreview.rows,
                }}
              />
              <Text type="secondary" className="admin-skill-overview-footnote">
                {SKILL_DRAWER.requiredSummary(countRequiredParams(view), requiredTotal)}
              </Text>
            </Card>
          ) : null}

          {confirmRules.length > 0 || view.confirmation.rows.length > 0 ? (
            <Card
              size="small"
              className="admin-skill-drawer-overview-card"
              title={SKILL_SPEC_SECTION.confirm.title}
              extra={
                <Button type="link" size="small" onClick={() => onGoToSpec("confirm")}>
                  {SKILL_DRAWER.viewConfirmDetail}
                </Button>
              }
            >
              {confirmRules.length > 0 ? (
                <ConfirmOrchestrationNotes
                  rules={confirmRules.slice(0, CONFIRM_RULE_PREVIEW_MAX)}
                />
              ) : null}
              {view.confirmation.rows.length > 0 ? (
                <>
                  {confirmRules.length > 0 ? (
                    <Text type="secondary" className="admin-skill-op-rules-heading">
                      {SKILL_OVERVIEW_METRICS.confirm}
                    </Text>
                  ) : null}
                  <ConfirmFieldList view={view} />
                </>
              ) : null}
            </Card>
          ) : null}

          <Card size="small" className="admin-skill-drawer-overview-card admin-skill-overview-quick">
            <Text type="secondary" className="admin-skill-drawer-label">
              {SKILL_DRAWER.labelSpecQuickNav}
            </Text>
            <Space wrap size={[8, 8]} style={{ marginTop: 8 }}>
              {SKILL_SPEC_SECTIONS.map((s) => {
                const n = s.count(view);
                const apiDisabled = s.key === "api" && n === 0;
                return (
                  <Button
                    key={s.key}
                    size="small"
                    disabled={apiDisabled}
                    onClick={() => onGoToSpec(s.key)}
                  >
                    {s.label}
                    {n > 0 ? ` · ${n}` : ""}
                  </Button>
                );
              })}
            </Space>
          </Card>
        </>
      ) : null}

      <Row gutter={[12, 12]}>
        <Col xs={24} md={12}>
          <Card size="small" className="admin-skill-drawer-overview-card">
            <Text type="secondary" className="admin-skill-drawer-label">
              {SKILL_DRAWER.labelUserFlow}
            </Text>
            <Paragraph className="admin-skill-drawer-prose">{entry.userFlow}</Paragraph>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card size="small" className="admin-skill-drawer-overview-card">
            <Text type="secondary" className="admin-skill-drawer-label">
              {SKILL_DRAWER.labelExchange}
            </Text>
            <Paragraph className="admin-skill-drawer-prose">{entry.exchangeAction}</Paragraph>
          </Card>
        </Col>
      </Row>

      {entry.specNote ? (
        <Paragraph type="secondary" className="admin-skill-overview-note">
          {entry.specNote}
        </Paragraph>
      ) : null}

      {view ? (
        <Button
          type="link"
          className="admin-skill-drawer-goto-spec"
          icon={<RightOutlined />}
          onClick={() => onGoToSpec()}
        >
          {SKILL_DRAWER.gotoSpec}
        </Button>
      ) : !entry.specPath ? (
        <Paragraph type="secondary" style={{ marginBottom: 0 }}>
          {SKILL_DRAWER.emptySpec}
        </Paragraph>
      ) : null}
    </div>
  );
}
