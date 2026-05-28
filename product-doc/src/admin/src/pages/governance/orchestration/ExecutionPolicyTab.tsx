import { useCallback, useEffect, useState } from "react";
import { App, Button, Card, Collapse, Form, Input, InputNumber, Select, Space, Switch, Typography } from "antd";
import { OpsHintAlert } from "../../../components/OpsHintAlert";
import { EXECUTION_POLICY_DEV, EXECUTION_POLICY_TAB } from "../../../copy/opsPanelHints";
import { useOrchestrationPolicy } from "../../../context/OrchestrationPolicyContext";
import type { ExecutionPolicyState, FailureStopPolicy } from "./executionPolicyModel";
import {
  DEFAULT_EXECUTION_POLICY,
  ENGINEERING_SPEC_REFS,
  FAILURE_STOP_POLICY_LABEL,
} from "./executionPolicyModel";

const { Text, Paragraph } = Typography;

function policyToForm(s: ExecutionPolicyState): ExecutionPolicyState {
  return { ...s };
}

function formToPolicy(v: ExecutionPolicyState): ExecutionPolicyState {
  return { ...v };
}

export function ExecutionPolicyTab() {
  const { message } = App.useApp();
  const { effectivePolicy, applyPolicy, resetPolicyToDefault } = useOrchestrationPolicy();
  const [form] = Form.useForm<ExecutionPolicyState>();
  const [dirty, setDirty] = useState(false);
  const roundsEnabled = Form.useWatch("modelRoundsLimitEnabled", form);

  useEffect(() => {
    form.setFieldsValue(policyToForm(effectivePolicy));
    setDirty(false);
  }, [effectivePolicy, form]);

  const resetToDefault = useCallback(() => {
    resetPolicyToDefault();
    message.info("已恢复默认");
  }, [resetPolicyToDefault, message]);

  const onSave = useCallback(async () => {
    try {
      const v = await form.validateFields();
      applyPolicy(formToPolicy(v as ExecutionPolicyState));
      message.success("已应用");
      setDirty(false);
    } catch {
      message.error("请检查表单");
    }
  }, [form, applyPolicy, message]);

  const failureOptions = (Object.keys(FAILURE_STOP_POLICY_LABEL) as FailureStopPolicy[]).map((k) => ({
    value: k,
    label: FAILURE_STOP_POLICY_LABEL[k],
  }));

  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <OpsHintAlert
        type="info"
        showIcon
        message={EXECUTION_POLICY_TAB.introMessage}
        description={EXECUTION_POLICY_TAB.introDescription}
      />

      <Form<ExecutionPolicyState>
        form={form}
        layout="vertical"
        initialValues={policyToForm(DEFAULT_EXECUTION_POLICY)}
        onValuesChange={() => setDirty(true)}
        requiredMark={false}
      >
        <Card size="small" className="admin-panel-card" title="自动执行策略">
          <Form.Item label="允许自动执行" name="autoExecutionAllowed" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="高风控交易场景禁止自动落单" name="blockAutoHighRiskWrite" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="查询与行情类默认可自动执行" name="queryAutoDefault" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Card>

        <Card size="small" className="admin-panel-card" title="确认与加码">
          <Form.Item label="交易/资金写操作须用户确认" name="confirmationRequiredForWrites" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="大额名义须二次确认" name="secondConfirmLargeNotional" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="高杠杆变更须额外确认" name="highLeverageConfirm" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Card>

        <Card size="small" className="admin-panel-card" title="风险限制">
          <Form.Item
            label="单笔最大金额（USDT）"
            name="maxNotionalUsdt"
            rules={[{ required: true, type: "number", min: 1 }]}
          >
            <InputNumber min={1} style={{ width: "100%", maxWidth: 280 }} />
          </Form.Item>
          <Form.Item
            label="最大杠杆（倍）"
            name="maxLeverage"
            rules={[{ required: true, type: "number", min: 1, max: 125 }]}
          >
            <InputNumber min={1} max={125} style={{ width: "100%", maxWidth: 280 }} />
          </Form.Item>
          <Form.Item
            label="单日写类操作上限"
            name="maxDailyWriteOperations"
            rules={[{ required: true, type: "number", min: 1 }]}
          >
            <InputNumber min={1} style={{ width: "100%", maxWidth: 280 }} />
          </Form.Item>
          <Form.Item label="高频 / 频控说明" name="rateLimitNote">
            <Input.TextArea rows={2} placeholder="运营可读说明" />
          </Form.Item>
        </Card>

        <Card size="small" className="admin-panel-card" title="执行稳定性">
          <Form.Item
            label="最大自动重试次数"
            name="maxRetries"
            rules={[{ required: true, type: "number", min: 0, max: 20 }]}
          >
            <InputNumber min={0} max={20} style={{ width: "100%", maxWidth: 280 }} />
          </Form.Item>
          <Form.Item
            label="单次执行超时（秒）"
            name="executionTimeoutSeconds"
            rules={[{ required: true, type: "number", min: 5, max: 600 }]}
          >
            <InputNumber min={5} max={600} style={{ width: "100%", maxWidth: 280 }} />
          </Form.Item>
          <Form.Item label="失败终止策略" name="failureStopPolicy" rules={[{ required: true }]}>
            <Select<FailureStopPolicy> options={failureOptions} style={{ maxWidth: 400 }} />
          </Form.Item>
        </Card>

        <Collapse
          items={[
            {
              key: "engineering",
              label: EXECUTION_POLICY_DEV.collapseLabel,
              children: (
                <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                  <Paragraph type="secondary" style={{ marginBottom: 0, fontSize: 12 }}>
                    {EXECUTION_POLICY_DEV.collapseIntro}
                  </Paragraph>
                  <Form.Item
                    label="工具调用步数上限（引擎）"
                    name="maxToolCalls"
                    rules={[{ required: true, type: "number", min: 1, max: 999 }]}
                  >
                    <InputNumber min={1} max={999} style={{ width: "100%", maxWidth: 280 }} />
                  </Form.Item>
                  <Form.Item
                    label="编排步骤上限（引擎）"
                    name="maxOrchestrationSteps"
                    rules={[{ required: true, type: "number", min: 1, max: 999 }]}
                  >
                    <InputNumber min={1} max={999} style={{ width: "100%", maxWidth: 280 }} />
                  </Form.Item>
                  <Form.Item label="启用模型回合上限">
                    <Space align="center">
                      <Form.Item name="modelRoundsLimitEnabled" valuePropName="checked" noStyle>
                        <Switch />
                      </Form.Item>
                    </Space>
                  </Form.Item>
                  <Form.Item
                    label="模型回合上限"
                    name="maxModelRounds"
                    rules={[
                      {
                        validator: async (_, v) => {
                          if (!form.getFieldValue("modelRoundsLimitEnabled")) return;
                          if (typeof v !== "number" || v < 1 || v > 99) throw new Error("1～99");
                        },
                      },
                    ]}
                  >
                    <InputNumber min={1} max={99} style={{ width: "100%", maxWidth: 280 }} disabled={!roundsEnabled} />
                  </Form.Item>
                  <Form.Item label="预算超出稳定码（引擎）" name="budgetExceededStableCode">
                    <Input maxLength={64} showCount style={{ maxWidth: 400 }} />
                  </Form.Item>
                  <Form.Item label="C 类外网池（引擎文案）" name="cClassPoolNote">
                    <Input.TextArea rows={2} />
                  </Form.Item>
                  <Form.Item label="重试策略摘要（spec）" name="retrySummary">
                    <Input.TextArea rows={2} />
                  </Form.Item>
                  <Form.Item label="UNKNOWN / 超时摘要（spec）" name="unknownHandlingSummary">
                    <Input.TextArea rows={2} />
                  </Form.Item>
                  <div>
                    <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
                      规格互引
                    </Text>
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12 }}>
                      {ENGINEERING_SPEC_REFS.map((p) => (
                        <li key={p}>
                          <Text code>{p}</Text>
                        </li>
                      ))}
                    </ul>
                  </div>
                </Space>
              ),
            },
          ]}
        />

        <Space style={{ marginTop: 8 }}>
          <Button type="primary" onClick={() => void onSave()}>
            应用
          </Button>
          <Button onClick={resetToDefault}>恢复默认</Button>
          {dirty ? (
            <Text type="warning" style={{ fontSize: 12 }}>
              未应用
            </Text>
          ) : null}
        </Space>
      </Form>
    </Space>
  );
}
