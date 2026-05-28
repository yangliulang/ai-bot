import { ArrowLeftOutlined, DeleteOutlined, PlusOutlined } from "@ant-design/icons";
import { App, Button, Card, Collapse, Form, Input, Select, SelectProps, Space, Switch, Typography } from "antd";
import { useEffect, useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PagePrimaryButton, PageSecondaryButton, ProductPageShell } from "../../../components/product";
import { useConfirmationRules } from "../../../context/ConfirmationRulesContext";
import {
  defaultOperatorForField,
  operatorsForField,
  RISK_LEVEL_OPTIONS,
  RULE_ACTION_OPTIONS,
  SCENARIO_OPTIONS,
  TRIGGER_FIELD_OPTIONS,
  TRIGGER_OPERATOR_OPTIONS,
  type ConfirmationRuleDefinition,
  type RiskLevel,
  type RuleAction,
  type ScenarioKey,
  type TriggerConditionRow,
  type TriggerFieldKey,
  type TriggerOpKey,
} from "./confirmationRulesCatalog";

const { Text } = Typography;

type FormValues = {
  title: string;
  summary: string;
  riskLevel: RiskLevel;
  triggerConditions: TriggerConditionRow[];
  scenarios: ScenarioKey[];
  action: RuleAction;
  defaultEnabled: boolean;
};

const emptyCondition = (): TriggerConditionRow => ({
  fieldKey: "nominal_usdt",
  operator: "gt",
  value: "",
});

function operatorSelectOptions(fieldKey: TriggerFieldKey | undefined): SelectProps["options"] {
  const fk = fieldKey ?? "nominal_usdt";
  return operatorsForField(fk).map((op) => {
    const o = TRIGGER_OPERATOR_OPTIONS.find((x) => x.value === op);
    return { value: op, label: o?.label ?? op };
  });
}

export function ConfirmationRuleEditorPage({ mode }: { mode: "create" | "edit" }) {
  const { ruleId: ruleIdParam } = useParams<{ ruleId: string }>();
  const ruleId = ruleIdParam ? decodeURIComponent(ruleIdParam) : "";
  const navigate = useNavigate();
  const { message } = App.useApp();
  const { customRules, addCustomRule, updateCustomRule, isBuiltinRule } = useConfirmationRules();
  const [form] = Form.useForm<FormValues>();

  const editingRule = useMemo(() => {
    if (mode !== "edit" || !ruleId) return null;
    return customRules.find((r) => r.id === ruleId) ?? null;
  }, [mode, ruleId, customRules]);

  useEffect(() => {
    if (mode !== "create") return;
    form.resetFields();
    form.setFieldsValue({
      title: "",
      summary: "",
      riskLevel: "medium",
      triggerConditions: [emptyCondition()],
      scenarios: [],
      action: "second_confirm",
      defaultEnabled: true,
    });
  }, [mode, form]);

  useEffect(() => {
    if (mode !== "edit" || !ruleId) return;
    if (isBuiltinRule(ruleId)) {
      message.error("内置规则请在列表中查看，不可在此编辑");
      navigate("/ai/confirmation-rules", { replace: true });
      return;
    }
    const rule = editingRule;
    if (!rule) {
      message.error("未找到该自定义规则");
      navigate("/ai/confirmation-rules", { replace: true });
      return;
    }
    form.setFieldsValue({
      title: rule.title,
      summary: rule.summary,
      riskLevel: rule.riskLevel,
      triggerConditions: rule.triggerConditions.length ? rule.triggerConditions : [emptyCondition()],
      scenarios: rule.scenarios,
      action: rule.action,
      defaultEnabled: rule.defaultEnabled,
    });
  }, [mode, ruleId, editingRule, form, isBuiltinRule, navigate, message]);

  const onFinish = (v: FormValues) => {
    const conditions = (v.triggerConditions ?? [])
      .filter((c) => String(c?.value ?? "").trim())
      .map((c) => {
        const fk = c.fieldKey as TriggerFieldKey;
        let op = c.operator as TriggerOpKey;
        if (!operatorsForField(fk).includes(op)) op = defaultOperatorForField(fk);
        return { fieldKey: fk, operator: op, value: String(c.value).trim() };
      });
    if (!conditions.length) {
      message.error("请至少添加一条触发条件并填写比较值");
      return;
    }
    if (!v.scenarios?.length) {
      message.error("请至少选择一个适用场景");
      return;
    }
    const body: Omit<ConfirmationRuleDefinition, "id"> = {
      title: v.title.trim(),
      summary: v.summary.trim(),
      riskLevel: v.riskLevel,
      triggerConditions: conditions,
      scenarios: v.scenarios,
      action: v.action,
      defaultEnabled: v.defaultEnabled,
    };
    if (mode === "create") {
      addCustomRule(body);
      message.success("已创建规则");
    } else if (editingRule) {
      updateCustomRule(editingRule.id, { ...body, id: editingRule.id });
      message.success("已保存");
    }
    navigate("/ai/confirmation-rules");
  };

  return (
    <ProductPageShell
      pageId="ai.confirmation-rules.editor"
      showPageId={false}
      title={mode === "create" ? "新建风控规则" : "编辑风控规则"}
      description="配置风险条件与命中后的处理方式；字段均为业务语义，不涉及渠道或引擎实现细节。"
      extra={
        <PageSecondaryButton icon={<ArrowLeftOutlined />} onClick={() => navigate("/ai/confirmation-rules")}>
          返回列表
        </PageSecondaryButton>
      }
    >
      <Form form={form} layout="vertical" requiredMark={false} onFinish={onFinish} style={{ maxWidth: 920 }}>
        <Card size="small" title="基础信息" style={{ marginBottom: 16 }} className="admin-panel-card">
          <Form.Item name="title" label="规则名称" rules={[{ required: true, message: "请输入规则名称" }]}>
            <Input placeholder="如：高杠杆交易二次确认" maxLength={80} showCount />
          </Form.Item>
          <Form.Item name="summary" label="规则说明" rules={[{ required: true, message: "请输入规则说明" }]}>
            <Input.TextArea
              placeholder="如：当杠杆超过 20× 时，用户需再次确认风险。"
              rows={4}
              maxLength={500}
              showCount
            />
          </Form.Item>
        </Card>

        <Card size="small" title="风险等级" style={{ marginBottom: 16 }} className="admin-panel-card">
          <Form.Item name="riskLevel" label="风险等级" rules={[{ required: true, message: "请选择风险等级" }]}>
            <Select options={RISK_LEVEL_OPTIONS} placeholder="选择等级" style={{ maxWidth: 320 }} />
          </Form.Item>
        </Card>

        <Card size="small" title="触发条件" style={{ marginBottom: 16 }} className="admin-panel-card">
          <Text type="secondary" style={{ display: "block", marginBottom: 12, fontSize: 13 }}>
            通过「字段 / 运算符 / 值」组合定义命中条件，可添加多行。数值与文案按运营习惯填写即可。
          </Text>
          <Form.List name="triggerConditions">
            {(fields, { add, remove }) => (
              <>
                <Space direction="vertical" size={12} style={{ width: "100%" }}>
                  {fields.map((field) => (
                    <div
                      key={field.key}
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: 12,
                        alignItems: "flex-start",
                        padding: "8px 0",
                        borderBottom: "1px solid var(--ant-color-split, rgba(0,0,0,0.06))",
                      }}
                    >
                      <Form.Item
                        name={[field.name, "fieldKey"]}
                        rules={[{ required: true, message: "选字段" }]}
                        style={{ marginBottom: 0, minWidth: 200 }}
                      >
                        <Select
                          options={TRIGGER_FIELD_OPTIONS}
                          placeholder="字段"
                          onChange={(fk) => {
                            const op = defaultOperatorForField(fk as TriggerFieldKey);
                            const rows = form.getFieldValue("triggerConditions") ?? [];
                            const next = [...rows];
                            if (next[field.name]) {
                              next[field.name] = { ...next[field.name], fieldKey: fk, operator: op };
                              form.setFieldValue("triggerConditions", next);
                            }
                          }}
                        />
                      </Form.Item>
                      <Form.Item noStyle shouldUpdate={(prev, cur) => prev.triggerConditions !== cur.triggerConditions}>
                        {() => {
                          const rows: TriggerConditionRow[] = form.getFieldValue("triggerConditions") ?? [];
                          const fk = rows[field.name]?.fieldKey ?? "nominal_usdt";
                          return (
                            <Form.Item
                              name={[field.name, "operator"]}
                              rules={[{ required: true, message: "选运算符" }]}
                              style={{ marginBottom: 0, width: 112 }}
                            >
                              <Select options={operatorSelectOptions(fk)} placeholder="运算符" />
                            </Form.Item>
                          );
                        }}
                      </Form.Item>
                      <Form.Item
                        name={[field.name, "value"]}
                        rules={[{ required: true, message: "填写值" }]}
                        style={{ marginBottom: 0, flex: "1 1 200px", maxWidth: 280 }}
                      >
                        <Input placeholder="如 50000、20 或简短说明" />
                      </Form.Item>
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => remove(field.name)}
                        disabled={fields.length <= 1}
                        style={{ marginTop: 4 }}
                      >
                        删除
                      </Button>
                    </div>
                  ))}
                </Space>
                <Button
                  type="dashed"
                  icon={<PlusOutlined />}
                  onClick={() => add(emptyCondition())}
                  style={{ marginTop: 12 }}
                  block
                >
                  添加条件
                </Button>
              </>
            )}
          </Form.List>
        </Card>

        <Card size="small" title="适用场景" style={{ marginBottom: 16 }} className="admin-panel-card">
          <Form.Item
            name="scenarios"
            label="场景"
            rules={[{ required: true, message: "请至少选择一个适用场景" }]}
            extra="可多选，覆盖规则生效的业务面"
          >
            <Select mode="multiple" options={SCENARIO_OPTIONS} placeholder="选择适用场景" optionFilterProp="label" />
          </Form.Item>
        </Card>

        <Card size="small" title="处理动作" style={{ marginBottom: 24 }} className="admin-panel-card">
          <Form.Item name="action" label="命中后的处理动作" rules={[{ required: true, message: "请选择处理动作" }]}>
            <Select options={RULE_ACTION_OPTIONS.map((o) => ({ value: o.value, label: o.label }))} placeholder="选择动作" />
          </Form.Item>
          <Collapse
            size="small"
            ghost
            items={[
              {
                key: "action-hints",
                label: "各动作说明（展开查看）",
                children: (
                  <Text type="secondary" style={{ fontSize: 12, display: "block" }}>
                    {RULE_ACTION_OPTIONS.map((o) => (
                      <span key={o.value} style={{ display: "block", marginBottom: 6 }}>
                        <Text strong>{o.label}</Text>：{o.hint}
                      </span>
                    ))}
                  </Text>
                ),
              },
            ]}
          />
          <Form.Item name="defaultEnabled" label="保存后立即启用" valuePropName="checked" style={{ marginTop: 12 }}>
            <Switch />
          </Form.Item>
        </Card>

        <Space size={12}>
          <PagePrimaryButton htmlType="submit">保存</PagePrimaryButton>
          <PageSecondaryButton onClick={() => navigate("/ai/confirmation-rules")}>取消</PageSecondaryButton>
        </Space>
      </Form>
    </ProductPageShell>
  );
}
