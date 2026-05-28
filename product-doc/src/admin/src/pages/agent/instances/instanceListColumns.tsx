import { useMemo } from "react";
import { Button, Space, Tag, Tooltip, Typography } from "antd";
import { ArrowRightOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import { Link } from "react-router-dom";
import type { AgentInstance } from "../../../data/types";
import { buildObservabilitySearch } from "../../../utils/observabilityDeepLink";
import { agentStateTagColor, formatInstanceAt, runtimeStateTagColor } from "../../../utils/agentInstanceUi";
import { getInstanceRuntimeActionUi } from "../../../utils/agentInstanceRuntimeActions";
import { zhAgentState, zhRuntimeState } from "../../../copy/zhLabels";

const { Text } = Typography;

export type UseAgentInstanceColumnsOptions = {
  onPreview: (row: AgentInstance) => void;
  globalAgentSwitchOn: boolean;
  onRuntimeQuick: (label: string) => void;
};

/** 列「最小」宽度合计（px）；供表格 `scroll.x` 与行选择列预留对齐，避免残留过大横向滚动。 */
export const AGENT_INSTANCE_LIST_SCROLL_X =
  168 + 96 + 176 + 88 + 116 + 264 + 60;

/** 实例列表默认列（模板 / 渠道 / 子账户仅在详情查看）。 */
export function useAgentInstanceColumns(opts: UseAgentInstanceColumnsOptions): ColumnsType<AgentInstance> {
  const { onPreview, globalAgentSwitchOn, onRuntimeQuick } = opts;
  return useMemo<ColumnsType<AgentInstance>>(
    () => [
      {
        title: "实例 ID",
        dataIndex: "instanceId",
        key: "instanceId",
        width: 168,
        ellipsis: true,
        render: (id: string) => (
          <Text code style={{ fontSize: 12 }}>
            {id}
          </Text>
        ),
      },
      {
        title: "用户 UID",
        key: "user",
        width: 96,
        ellipsis: true,
        render: (_, i) => <div style={{ fontWeight: 500 }}>{i.userId}</div>,
      },
      {
        title: "运行状态",
        key: "gateAgg",
        width: 176,
        ellipsis: { showTitle: true },
        render: (_, i) => (
          <Space direction="vertical" size={4} style={{ width: "100%" }}>
            <Tag color={agentStateTagColor(i.agentState)} style={{ marginInlineEnd: 0 }}>
              {zhAgentState(i.agentState)}
            </Tag>
            <Text type="secondary" style={{ fontSize: 11 }} ellipsis={{ tooltip: i.lastProductBlockReason }}>
              {i.lastProductBlockReason || "—"}
            </Text>
          </Space>
        ),
      },
      {
        title: "实例状态",
        dataIndex: "runtimeState",
        key: "rt",
        width: 88,
        render: (s: string) => <Tag color={runtimeStateTagColor(s)}>{zhRuntimeState(s)}</Tag>,
      },
      {
        title: "最近活跃",
        dataIndex: "lastActiveAt",
        key: "la",
        width: 116,
        sorter: (a, b) => a.lastActiveAt.localeCompare(b.lastActiveAt),
        render: (s: string) => (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {formatInstanceAt(s)}
          </Text>
        ),
      },
      {
        title: "操作",
        key: "op",
        width: 264,
        fixed: "right",
        render: (_, i) => {
          const ui = getInstanceRuntimeActionUi(i, { globalAgentSwitchOn });
          const rtExtras: JSX.Element[] = [];
          if (ui.showStart) {
            const btn = (
              <Button
                type="link"
                size="small"
                style={{ padding: 0 }}
                disabled={ui.disableStart}
                onClick={(e) => {
                  e.stopPropagation();
                  onRuntimeQuick("启动");
                }}
              >
                启动
              </Button>
            );
            rtExtras.push(
              ui.disableStart && ui.startDisabledReason ? (
                <Tooltip key="st" title={ui.startDisabledReason}>
                  <span>{btn}</span>
                </Tooltip>
              ) : (
                <span key="st">{btn}</span>
              ),
            );
          }
          if (ui.showResume) {
            const btn = (
              <Button
                type="link"
                size="small"
                style={{ padding: 0 }}
                disabled={ui.disableResume}
                onClick={(e) => {
                  e.stopPropagation();
                  onRuntimeQuick("恢复");
                }}
              >
                恢复
              </Button>
            );
            rtExtras.push(
              ui.disableResume && ui.resumeDisabledReason ? (
                <Tooltip key="rs" title={ui.resumeDisabledReason}>
                  <span>{btn}</span>
                </Tooltip>
              ) : (
                <span key="rs">{btn}</span>
              ),
            );
          }

          return (
            <Space size={[4, 4]} onClick={(e) => e.stopPropagation()} wrap>
              {rtExtras}
              <Button type="link" size="small" style={{ padding: 0 }} onClick={() => onPreview(i)}>
                预览
              </Button>
              <Link to={`/agents/instances/${i.instanceId}`}>
                <Button type="link" size="small" style={{ padding: 0 }}>
                  详情 <ArrowRightOutlined style={{ fontSize: 11 }} />
                </Button>
              </Link>
              <Link to={`/agents/instances/${i.instanceId}?tab=logs`}>
                <Button type="link" size="small" style={{ padding: 0 }}>
                  日志
                </Button>
              </Link>
              <Link to={`/observability${buildObservabilitySearch({ userId: i.userId, tab: "execution" })}`}>
                <Button type="link" size="small" style={{ padding: 0 }}>
                  协查
                </Button>
              </Link>
            </Space>
          );
        },
      },
    ],
    [onPreview, globalAgentSwitchOn, onRuntimeQuick],
  );
}
