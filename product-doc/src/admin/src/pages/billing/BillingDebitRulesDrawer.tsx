import { App, Button, Drawer, Form, Input, InputNumber, Space, Tag, Typography } from "antd";
import { useEffect } from "react";
import { BILLING_RULES } from "../../copy/opsPanelHints";
import {
  debitCapabilityShortId,
  debitCapabilityTagColor,
  type BillingDebitRule,
} from "../../data/billingRulesSeed";

const { Text } = Typography;

type FormValues = {
  rows: BillingDebitRule[];
};

type Props = {
  open: boolean;
  rules: BillingDebitRule[];
  onClose: () => void;
  onSave: (rules: BillingDebitRule[]) => void;
  apiOn?: boolean;
  onPushApi?: () => void;
  pushingApi?: boolean;
};

export function BillingDebitRulesDrawer({
  open,
  rules,
  onClose,
  onSave,
  apiOn,
  onPushApi,
  pushingApi,
}: Props) {
  const { message } = App.useApp();
  const [form] = Form.useForm<FormValues>();

  useEffect(() => {
    if (open) {
      form.setFieldsValue({ rows: rules.map((r) => ({ ...r })) });
    }
  }, [open, rules, form]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const normalized = values.rows.map((r) => ({
        ...r,
        displayLabel: r.displayLabel.trim(),
        summary: typeof r.summary === "string" ? r.summary.trim() : "",
        debitUnitsPerExecution: Number(r.debitUnitsPerExecution),
      }));
      onSave(normalized);
      message.success(BILLING_RULES.debitSaveSuccess);
      onClose();
    } catch {
      message.error(BILLING_RULES.validateFailed);
    }
  };

  return (
    <Drawer
      title={BILLING_RULES.debitEditTitle}
      width={480}
      open={open}
      onClose={onClose}
      destroyOnClose
      footer={
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <Space>
            {apiOn && onPushApi ? (
              <Button loading={pushingApi} onClick={() => void onPushApi()}>
                {BILLING_RULES.debitPushApi}
              </Button>
            ) : null}
          </Space>
          <Space>
            <Button onClick={onClose}>取消</Button>
            <Button type="primary" onClick={() => void handleSave()}>
              保存
            </Button>
          </Space>
        </div>
      }
    >
      <Form form={form} layout="vertical">
        <Form.List name="rows">
          {(fields) => (
            <Space direction="vertical" size="middle" style={{ width: "100%" }}>
              {fields.map((field) => {
                const seed = rules[field.name];
                const sku = seed?.capabilitySkuId ?? "";
                const tagColor = debitCapabilityTagColor(sku);
                const shortId = debitCapabilityShortId(sku);
                return (
                  <div
                    key={field.key}
                    style={{
                      border: "1px solid var(--ant-color-border-secondary)",
                      borderRadius: 8,
                      padding: 12,
                    }}
                  >
                    <Form.Item name={[field.name, "capabilitySkuId"]} hidden>
                      <Input />
                    </Form.Item>
                    <Form.Item name={[field.name, "summary"]} hidden>
                      <Input />
                    </Form.Item>
                    <Space size="small" style={{ marginBottom: 8 }}>
                      <Text strong>{seed?.displayLabel}</Text>
                      {tagColor ? <Tag color={tagColor}>{shortId}</Tag> : <Tag>{shortId}</Tag>}
                    </Space>
                    {seed?.summary ? (
                      <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 12 }}>
                        {seed.summary}
                      </Text>
                    ) : null}
                    <Form.Item
                      name={[field.name, "displayLabel"]}
                      label={BILLING_RULES.debitFieldDisplayLabel}
                      rules={[{ required: true }]}
                    >
                      <Input />
                    </Form.Item>
                    <Form.Item
                      name={[field.name, "debitUnitsPerExecution"]}
                      label={BILLING_RULES.debitFieldAmount}
                      rules={[{ required: true, type: "number", min: 1 }]}
                      extra={BILLING_RULES.debitPerSuccessHint}
                    >
                      <InputNumber min={1} style={{ width: "100%" }} addonAfter={BILLING_RULES.debitUnitSuffix} />
                    </Form.Item>
                  </div>
                );
              })}
            </Space>
          )}
        </Form.List>
      </Form>
    </Drawer>
  );
}
