import { Card } from "antd";
import { Link } from "react-router-dom";
import { MOCK_SCENARIO_REGISTRY } from "../governance/orchestration/scenarioRegistryMock";
import { ScenarioSkillScopePanel } from "../governance/orchestration/ScenarioSkillScopePanel";
import type { ScenarioCategory } from "../governance/orchestration/scenarioRegistryMock";

type Props = {
  scenarioId: string;
  /** 嵌入治理折叠时：无外层卡片与顶栏说明 */
  embedded?: boolean;
};

function categoryForScenario(scenarioId: string): ScenarioCategory {
  return MOCK_SCENARIO_REGISTRY.find((r) => r.scenarioId === scenarioId)?.category ?? "read";
}

export function ExecutionScenarioSkillScope({ scenarioId, embedded = false }: Props) {
  const category = categoryForScenario(scenarioId);
  const panel = <ScenarioSkillScopePanel scenarioId={scenarioId} category={category} showIntroAlert={!embedded} />;

  if (embedded) {
    return (
      <>
        <div style={{ marginBottom: 8, textAlign: "right" }}>
          <Link to={`/ai/runtime-orchestration?scenario=${encodeURIComponent(scenarioId)}`}>运行场景详情</Link>
        </div>
        {panel}
      </>
    );
  }

  return (
    <Card
      size="small"
      className="admin-panel-card"
      title="场景 · 技能范围"
      extra={
        <Link to={`/ai/runtime-orchestration?scenario=${encodeURIComponent(scenarioId)}`}>
          运行场景详情
        </Link>
      }
    >
      {panel}
    </Card>
  );
}
