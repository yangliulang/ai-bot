import { Tag, Typography } from "antd";
import type { ToolRegistryRow } from "../../data/toolRegistryTypes";
import { SKILL_MATRIX_STATUS } from "./skillRegistryUiCopy";

const { Text } = Typography;

export function skillDomainLabel(skillId: string): string | null {
  if (skillId.startsWith("skill.spot.")) return "现货";
  if (skillId.startsWith("skill.futures.")) return "合约";
  if (skillId.startsWith("skill.margin.")) return "全仓";
  if (skillId.startsWith("skill.wealth.")) return "理财";
  return null;
}

export function matrixStatusTag(status: ToolRegistryRow["matrixStatus"]) {
  if (status === "frozen") {
    return (
      <Tag bordered={false} color="success">
        {SKILL_MATRIX_STATUS.frozen}
      </Tag>
    );
  }
  if (status === "tbd") {
    return (
      <Tag bordered={false} color="warning">
        {SKILL_MATRIX_STATUS.tbd}
      </Tag>
    );
  }
  return (
    <Tag bordered={false} color="default">
      {SKILL_MATRIX_STATUS.draft}
    </Tag>
  );
}

/** 列表行：仅技能身份，操作规范在抽屉 */
export function SkillIdentityCell({ row }: { row: ToolRegistryRow }) {
  return (
    <div className="admin-skill-registry-cell--identity">
      <Text strong className="admin-skill-registry-summary">
        {row.summary}
      </Text>
      <Text type="secondary" className="admin-skill-registry-skill-id">
        {row.stableId}
      </Text>
    </div>
  );
}

export function SkillUserFlowCell({ row }: { row: ToolRegistryRow }) {
  return (
    <Text className="admin-skill-registry-flow">{row.userFlow ?? "—"}</Text>
  );
}

export function SkillExchangeCell({ row }: { row: ToolRegistryRow }) {
  return (
    <Text type="secondary" className="admin-skill-registry-matrix">
      {row.exchangeAction ?? row.anchor}
    </Text>
  );
}
