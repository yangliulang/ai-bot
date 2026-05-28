import { useCallback, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Alert,
  App,
  Button,
  Drawer,
  Flex,
  Input,
  Segmented,
  Space,
  Switch,
  Table,
  Tag,
  Tooltip,
  Typography,
  theme,
} from "antd";
import { DeleteOutlined, EditOutlined, EyeOutlined, FilterOutlined, PlusOutlined, SearchOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import {
  AdminFilterSurface,
  ADMIN_FILTER_CONTROL_SIZE,
  adminListPagination,
  PagePrimaryButton,
  PageSecondaryButton,
} from "../../../components/product";
import { useConfirmationRules } from "../../../context/ConfirmationRulesContext";
import {
  formatTriggerLine,
  formatTriggerSummary,
  RISK_LEVEL_OPTIONS,
  RULE_ACTION_META,
  ruleActionNeedsStrongDisableGuard,
  scenarioLabels,
  type ConfirmationRuleDefinition,
  type RiskLevel,
} from "./confirmationRulesCatalog";

const { Text, Paragraph } = Typography;

function riskLevelTag(level: RiskLevel) {
  const m: Record<RiskLevel, { color: string; label: string }> = {
    low: { color: "green", label: "低风险" },
    medium: { color: "gold", label: "中风险" },
    high: { color: "red", label: "高风险" },
  };
  const x = m[level];
  return (
    <Tag color={x.color} style={{ margin: 0 }}>
      {x.label}
    </Tag>
  );
}

export function ConfirmationRulesPanel() {
  const { token } = theme.useToken();
  const navigate = useNavigate();
  const { modal, message } = App.useApp();
  const {
    mergedRules,
    customRules,
    enabledMap,
    isBuiltinRule,
    setRuleEnabled,
    removeCustomRule,
    resetRulesToCatalogDefaults,
  } = useConfirmationRules();

  const [riskFilter, setRiskFilter] = useState<RiskLevel | "all">("all");
  const [q, setQ] = useState("");
  const [active, setActive] = useState<ConfirmationRuleDefinition | null>(null);

  const filtered = useMemo(() => {
    let rows = mergedRules;
    if (riskFilter !== "all") rows = rows.filter((r) => r.riskLevel === riskFilter);
    const s = q.trim().toLowerCase();
    if (s) {
      rows = rows.filter(
        (r) =>
          r.title.toLowerCase().includes(s) ||
          r.summary.toLowerCase().includes(s) ||
          formatTriggerSummary(r.triggerConditions).toLowerCase().includes(s) ||
          scenarioLabels(r.scenarios).toLowerCase().includes(s) ||
          RULE_ACTION_META[r.action].label.toLowerCase().includes(s) ||
          r.id.toLowerCase().includes(s),
      );
    }
    return rows;
  }, [riskFilter, q, mergedRules]);

  const resolveEnabled = useCallback(
    (row: ConfirmationRuleDefinition) => enabledMap[row.id] ?? row.defaultEnabled,
    [enabledMap],
  );

  const enabledCount = useMemo(
    () => mergedRules.filter((r) => resolveEnabled(r)).length,
    [mergedRules, resolveEnabled],
  );

  const onToggle = useCallback(
    (row: ConfirmationRuleDefinition, next: boolean) => {
      if (!next && ruleActionNeedsStrongDisableGuard(row.action)) {
        modal.confirm({
          title: "确认关闭该规则？",
          content: "该规则涉及强制确认或禁止自动执行类管控，关闭可能增加误操作与资金风险。仅建议在演练环境评估。",
          okText: "仍要关闭",
          cancelText: "保持启用",
          onOk: () => setRuleEnabled(row.id, false),
        });
        return;
      }
      setRuleEnabled(row.id, next);
    },
    [modal, setRuleEnabled],
  );

  const onDelete = useCallback(
    (row: ConfirmationRuleDefinition) => {
      if (isBuiltinRule(row.id)) return;
      modal.confirm({
        title: "删除该自定义规则？",
        content: "删除后不可恢复，历史命中记录仍以当时配置为准（演示）。",
        okText: "删除",
        okType: "danger",
        cancelText: "取消",
        onOk: () => {
          removeCustomRule(row.id);
          if (active?.id === row.id) setActive(null);
          message.success("已删除");
        },
      });
    },
    [modal, removeCustomRule, active?.id, message, isBuiltinRule],
  );

  const onRestoreDefault = useCallback(() => {
    const run = () => {
      setRiskFilter("all");
      setQ("");
      resetRulesToCatalogDefaults();
      setActive(null);
      message.success("已恢复内置默认与演示自定义样例");
    };
    if (customRules.length > 0) {
      modal.confirm({
        title: "恢复默认？",
        content: "将自定义规则恢复为三条演示样例，并把内置规则的启用状态恢复为初始默认（当前会话中您自建的其它规则将被覆盖）。",
        okText: "恢复",
        okType: "danger",
        cancelText: "取消",
        onOk: run,
      });
      return;
    }
    run();
  }, [customRules.length, modal, resetRulesToCatalogDefaults, message]);

  const hasActiveFilter = riskFilter !== "all" || q.trim().length > 0;

  const columns: ColumnsType<ConfirmationRuleDefinition> = [
    {
      title: "规则",
      key: "rule",
      width: 260,
      fixed: "left",
      render: (_: unknown, row) => (
        <Space direction="vertical" size={2}>
          <Space size={6} wrap>
            <Text strong style={{ fontSize: 13 }}>
              {row.title}
            </Text>
            {isBuiltinRule(row.id) ? (
              <Tag style={{ margin: 0 }}>内置</Tag>
            ) : (
              <Tag color="geekblue" style={{ margin: 0 }}>
                自定义
              </Tag>
            )}
            {ruleActionNeedsStrongDisableGuard(row.action) ? (
              <Tag color="red" style={{ margin: 0 }}>
                强管控
              </Tag>
            ) : null}
          </Space>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {row.summary}
          </Text>
        </Space>
      ),
    },
    {
      title: "触发条件",
      key: "triggers",
      width: 240,
      render: (_: unknown, row) => {
        const line = formatTriggerSummary(row.triggerConditions);
        if (line === "—") {
          return (
            <Text type="secondary" style={{ fontSize: 12 }}>
              —
            </Text>
          );
        }
        return (
          <Tooltip title={line}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {line.length > 56 ? `${line.slice(0, 56)}…` : line}
            </Text>
          </Tooltip>
        );
      },
    },
    {
      title: "风险等级",
      dataIndex: "riskLevel",
      key: "risk",
      width: 96,
      render: (l: RiskLevel) => riskLevelTag(l),
    },
    {
      title: "适用场景",
      key: "scenes",
      width: 160,
      ellipsis: true,
      render: (_: unknown, row) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {scenarioLabels(row.scenarios)}
        </Text>
      ),
    },
    {
      title: "处理动作",
      dataIndex: "action",
      key: "action",
      width: 132,
      render: (a: ConfirmationRuleDefinition["action"]) => {
        const m = RULE_ACTION_META[a];
        return (
          <Tooltip title={m.hint}>
            <Tag color={m.color} style={{ margin: 0 }}>
              {m.label}
            </Tag>
          </Tooltip>
        );
      },
    },
    {
      title: "启用",
      key: "en",
      width: 76,
      fixed: "right",
      align: "center",
      render: (_: unknown, row) => (
        <Switch
          size="small"
          checked={resolveEnabled(row)}
          onChange={(v) => onToggle(row, v)}
          aria-label={`${row.title} 启用`}
        />
      ),
    },
    {
      title: "操作",
      key: "op",
      width: 168,
      fixed: "right",
      render: (_: unknown, row) => (
        <Space size={0} wrap>
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => setActive(row)}>
            详情
          </Button>
          {isBuiltinRule(row.id) ? (
            <Tooltip title="内置规则不可编辑；可新建自定义规则补充">
              <Button type="link" size="small" icon={<EditOutlined />} disabled>
                编辑
              </Button>
            </Tooltip>
          ) : (
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => navigate(`/ai/confirmation-rules/edit/${encodeURIComponent(row.id)}`)}
            >
              编辑
            </Button>
          )}
          {isBuiltinRule(row.id) ? (
            <Tooltip title="内置规则不可删除">
              <Button type="link" size="small" danger icon={<DeleteOutlined />} disabled>
                删除
              </Button>
            </Tooltip>
          ) : (
            <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={() => onDelete(row)}>
              删除
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <>
      <Alert
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        message="部分高风险交易需用户确认后才能执行，用于降低误操作与资金风险。以下为风险条件与处理动作治理；名义金额、杠杆等阈值可在「风险限制」统一配置。"
        action={<Link to="/ai/runtime-orchestration?tab=policy">风险限制</Link>}
      />

      <AdminFilterSurface
        className="admin-confirmation-rules-query-surface"
        style={{ padding: "12px 16px", marginBottom: 16 }}
        title={
          <Space align="center" size={8} wrap>
            <FilterOutlined style={{ color: token.colorTextSecondary, fontSize: 15 }} aria-hidden />
            <Text strong style={{ fontSize: 15, color: token.colorText }}>
              筛选条件
            </Text>
          </Space>
        }
        extra={
          <Space wrap size={8} align="center">
            <PagePrimaryButton icon={<PlusOutlined />} onClick={() => navigate("/ai/confirmation-rules/new")}>
              新建规则
            </PagePrimaryButton>
            <Tag color="processing" style={{ margin: 0 }}>
              命中 {filtered.length} / {mergedRules.length}
            </Tag>
            <Tag style={{ margin: 0 }}>
              已启用 {enabledCount} / {mergedRules.length}
            </Tag>
            <Tooltip title="恢复内置启用默认，并重置自定义为演示样例（非内置三条）">
              <PageSecondaryButton onClick={onRestoreDefault}>恢复默认</PageSecondaryButton>
            </Tooltip>
          </Space>
        }
      >
        <Flex vertical gap={12}>
          <Segmented<RiskLevel | "all">
            block
            value={riskFilter}
            onChange={(v) => setRiskFilter(v)}
            options={[
              { label: "全部风险", value: "all" },
              ...RISK_LEVEL_OPTIONS.map((o) => ({ label: o.label, value: o.value })),
            ]}
          />
          <Input
            allowClear
            size={ADMIN_FILTER_CONTROL_SIZE}
            placeholder="规则名称、说明、触发条件、场景、处理动作…"
            prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </Flex>
      </AdminFilterSurface>

      <Table<ConfirmationRuleDefinition>
        rowKey="id"
        size="middle"
        className="admin-confirmation-rules-table-host"
        scroll={{ x: 1320 }}
        pagination={adminListPagination({ pageSize: 8 })}
        columns={columns}
        dataSource={filtered}
        locale={{
          emptyText:
            mergedRules.length > 0 && hasActiveFilter
              ? "当前筛选下无规则，请调整条件或清空筛选"
              : "暂无规则，可通过「新建规则」添加自定义条目",
        }}
      />

      <Drawer
        title={active ? active.title : "规则详情"}
        width={520}
        open={!!active}
        onClose={() => setActive(null)}
        destroyOnClose
        extra={
          active && !isBuiltinRule(active.id) ? (
            <Space>
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => {
                  navigate(`/ai/confirmation-rules/edit/${encodeURIComponent(active.id)}`);
                  setActive(null);
                }}
              >
                编辑
              </Button>
            </Space>
          ) : null
        }
      >
        {active ? (
          <>
            <Paragraph style={{ marginBottom: 12 }}>
              <Space wrap>
                {isBuiltinRule(active.id) ? <Tag>内置</Tag> : <Tag color="geekblue">自定义</Tag>}
                {riskLevelTag(active.riskLevel)}
                <Tooltip title={RULE_ACTION_META[active.action].hint}>
                  <Tag color={RULE_ACTION_META[active.action].color}>{RULE_ACTION_META[active.action].label}</Tag>
                </Tooltip>
              </Space>
            </Paragraph>
            <Paragraph style={{ marginBottom: 12 }}>
              <Text type="secondary">触发条件</Text>
              <ul style={{ margin: "8px 0 0", paddingLeft: 20, fontSize: 13, color: token.colorTextSecondary }}>
                {active.triggerConditions?.length ? (
                  active.triggerConditions.map((row, i) => (
                    <li key={`${i}-${formatTriggerLine(row).slice(0, 32)}`}>{formatTriggerLine(row)}</li>
                  ))
                ) : (
                  <Text type="secondary">—</Text>
                )}
              </ul>
            </Paragraph>
            <Paragraph style={{ marginBottom: 12 }}>
              <Text type="secondary">规则说明</Text>
              <div>{active.summary}</div>
            </Paragraph>
            <Paragraph>
              <Text type="secondary">启用</Text>
              <div style={{ marginTop: 6 }}>
                <Switch checked={resolveEnabled(active)} onChange={(v) => onToggle(active, v)} />
              </div>
            </Paragraph>
            <Paragraph>
              <Text type="secondary">适用场景</Text>
              <div style={{ marginTop: 8, fontSize: 13 }}>{scenarioLabels(active.scenarios)}</div>
            </Paragraph>
            <Paragraph style={{ marginTop: 16 }}>
              <Space wrap>
                <Link to="/ai/runtime-orchestration?tab=routing">场景目录</Link>
                <Link to="/ai/runtime-orchestration?tab=policy">风险限制</Link>
              </Space>
            </Paragraph>
          </>
        ) : null}
      </Drawer>
    </>
  );
}
