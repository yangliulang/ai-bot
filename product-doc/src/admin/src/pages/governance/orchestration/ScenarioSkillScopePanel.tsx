import { Descriptions, Space, Table, Tag, Typography, theme } from "antd";
import { Link } from "react-router-dom";
import { OpsHintAlert } from "../../../components/OpsHintAlert";
import { SCENARIO_SKILL_SCOPE } from "../../../copy/opsPanelHints";
import { promptPackEditorPath } from "../../prompt/promptPaths";
import { resolveScenarioSkillScope } from "./skillScopeForScenario";
import type { ScenarioCategory } from "./scenarioRegistryMock";

const { Text } = Typography;

const CONTRACT_COLOR: Record<string, string> = {
  complete: "success",
  missing: "warning",
  "n/a": "default",
};

const CONTRACT_LABEL: Record<string, string> = {
  complete: "说明就绪",
  missing: "说明未齐",
  "n/a": "无规范",
};

type Props = {
  scenarioId: string;
  category: ScenarioCategory;
  /** 外层已有卡片标题时可关闭顶栏提示 */
  showIntroAlert?: boolean;
};

/**
 * 场景详情 · Runtime Skill Scope（只读；Skill 正文在「技能与工具」）
 */
export function ScenarioSkillScopePanel({ scenarioId, category, showIntroAlert = false }: Props) {
  const { token } = theme.useToken();
  const scope = resolveScenarioSkillScope(scenarioId, category);

  return (
    <Space direction="vertical" size={12} style={{ width: "100%" }}>
      {showIntroAlert ? (
        <OpsHintAlert
          type="info"
          showIcon
          message={SCENARIO_SKILL_SCOPE.alertMessage}
          description={<Text style={{ fontSize: 12 }}>{SCENARIO_SKILL_SCOPE.alertDescription}</Text>}
        />
      ) : null}

      <Text style={{ fontSize: 12 }}>{scope.narrative}</Text>

      {scope.mode === "write_skill" && scope.skills.length > 0 ? (
        <Table
          size="small"
          pagination={false}
          rowKey="skillId"
          dataSource={scope.skills}
          columns={[
            {
              title: SCENARIO_SKILL_SCOPE.colSkillId,
              dataIndex: "skillId",
              render: (id: string) => (
                <Link to="/ai/tool-registry">
                  <Text code>{id}</Text>
                </Link>
              ),
            },
            { title: SCENARIO_SKILL_SCOPE.colSummary, dataIndex: "summary", ellipsis: true },
            {
              title: SCENARIO_SKILL_SCOPE.colVersion,
              dataIndex: "skillSpecVersion",
              width: 120,
              render: (v: string | null) => (v ? <Text code>{v}</Text> : "—"),
            },
            {
              title: SCENARIO_SKILL_SCOPE.colRegistry,
              dataIndex: "contractStatus",
              width: 96,
              render: (s: string) => <Tag color={CONTRACT_COLOR[s]}>{CONTRACT_LABEL[s] ?? s}</Tag>,
            },
            {
              title: SCENARIO_SKILL_SCOPE.colDemoEnabled,
              dataIndex: "demoEnabled",
              width: 88,
              render: (on: boolean) => (on ? <Tag color="success">开</Tag> : <Tag>关</Tag>),
            },
            {
              title: SCENARIO_SKILL_SCOPE.colMatrix,
              dataIndex: "matrixStatus",
              width: 72,
              render: (s: string) => <Text code>{s}</Text>,
            },
          ]}
        />
      ) : scope.mode === "read_only" ? (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {SCENARIO_SKILL_SCOPE.readOnlyHint}
        </Text>
      ) : (
        <OpsHintAlert
          type="warning"
          showIcon
          message={SCENARIO_SKILL_SCOPE.missingPrimarySkill}
          style={{ marginTop: 4 }}
        />
      )}

      <Descriptions
        bordered
        size="small"
        column={1}
        styles={{ label: { width: 140, color: token.colorTextSecondary } }}
      >
        <Descriptions.Item label={SCENARIO_SKILL_SCOPE.labelPromptPack}>
          {scope.promptStrategyPackId ? (
            <Link to={promptPackEditorPath(scope.promptStrategyPackId)}>
              <Text code>
                {scope.promptStrategyPackId}
                {scope.promptStrategyVersion != null ? `@v${scope.promptStrategyVersion}` : ""}
              </Text>
            </Link>
          ) : (
            <Text type="secondary">—（读侧或未发布）</Text>
          )}
        </Descriptions.Item>
        <Descriptions.Item label={SCENARIO_SKILL_SCOPE.labelGatePointer}>
          {scope.promptSkillScopeRef ? (
            <Text code copyable>
              {scope.promptSkillScopeRef}
            </Text>
          ) : (
            <Text type="secondary">—</Text>
          )}
        </Descriptions.Item>
      </Descriptions>
    </Space>
  );
}
