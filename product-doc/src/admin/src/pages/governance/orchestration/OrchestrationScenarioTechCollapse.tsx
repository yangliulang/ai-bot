import { Collapse, Typography } from "antd";
import type { ScenarioRegistryRow } from "./scenarioRegistryMock";
import { ORCHESTRATION_VERSION_DISPLAY } from "./scenarioRegistryMock";
import { ORCHESTRATION_SCENARIO } from "../../../copy/opsPanelHints";

const { Text } = Typography;

type Props = {
  row: ScenarioRegistryRow;
};

/** 场景抽屉 · 契约字段与规格路径（默认折叠） */
export function OrchestrationScenarioTechCollapse({ row }: Props) {
  return (
    <Collapse
      ghost
      size="small"
      style={{ marginTop: 8 }}
      items={[
        {
          key: "tech",
          label: ORCHESTRATION_SCENARIO.techCollapseLabel,
          children: (
            <>
              <div style={{ marginBottom: 8 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {ORCHESTRATION_SCENARIO.labelScenarioId}
                </Text>
                <div>
                  <Text code copyable style={{ fontSize: 12 }}>
                    {row.scenarioId}
                  </Text>
                </div>
              </div>
              <div style={{ marginBottom: 8 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {ORCHESTRATION_SCENARIO.labelOrchVersion}
                </Text>
                <div>
                  <Text code style={{ fontSize: 12 }}>
                    {ORCHESTRATION_VERSION_DISPLAY}
                  </Text>
                </div>
              </div>
              <div style={{ marginBottom: 8 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {ORCHESTRATION_SCENARIO.labelClosureKey}
                </Text>
                <div>
                  <Text code style={{ fontSize: 12 }}>
                    {row.closureStatus}
                  </Text>
                </div>
              </div>
              <div style={{ marginBottom: 8 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {ORCHESTRATION_SCENARIO.labelFlowAnchor}
                </Text>
                <div style={{ wordBreak: "break-word", fontSize: 12 }}>{row.flowAnchor}</div>
              </div>
              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {ORCHESTRATION_SCENARIO.labelSpecRefs}
                </Text>
                <ul style={{ margin: "6px 0 0", paddingLeft: 20, fontSize: 12 }}>
                  {row.specRefs.map((p) => (
                    <li key={p}>
                      <Text code style={{ fontSize: 11 }}>
                        {p}
                      </Text>
                    </li>
                  ))}
                </ul>
              </div>
            </>
          ),
        },
      ]}
    />
  );
}
