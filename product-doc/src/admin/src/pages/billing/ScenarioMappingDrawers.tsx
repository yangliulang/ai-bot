import { App, Button, Drawer, Form, Input, Select, Space } from "antd";
import { useEffect } from "react";
import { BILLING_RULES } from "../../copy/opsPanelHints";
import { CAPABILITY_OPTIONS, type BillingScenarioMappingRow } from "../../data/billingRulesSeed";

type FormProps = {
  open: boolean;
  mode: "create" | "edit";
  row: BillingScenarioMappingRow | null;
  existingIds: string[];
  onClose: () => void;
  onSave: (row: BillingScenarioMappingRow) => void;
};

export function ScenarioMappingFormDrawer({ open, mode, row, existingIds, onClose, onSave }: FormProps) {
  const { message } = App.useApp();
  const [form] = Form.useForm<BillingScenarioMappingRow>();
  const isCreate = mode === "create";

  useEffect(() => {
    if (!open) return;
    if (isCreate) {
      form.setFieldsValue({ scenarioId: "", capabilitySkuId: CAPABILITY_OPTIONS[0]?.value ?? "" });
    } else if (row) {
      form.setFieldsValue({ ...row });
    }
  }, [open, isCreate, row, form]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const scenarioId = values.scenarioId.trim();
      if (!/^[a-z][a-z0-9_.-]*$/i.test(scenarioId)) {
        message.error(BILLING_RULES.scenarioIdInvalid);
        return;
      }
      if (isCreate && existingIds.includes(scenarioId)) {
        message.error(BILLING_RULES.duplicateScenarioId);
        return;
      }
      onSave({ scenarioId, capabilitySkuId: values.capabilitySkuId });
      message.success(isCreate ? BILLING_RULES.mappingCreateSuccess : BILLING_RULES.mappingSaveSuccess);
      onClose();
    } catch {
      message.error(BILLING_RULES.validateFailed);
    }
  };

  return (
    <Drawer
      title={isCreate ? BILLING_RULES.mappingCreateTitle : BILLING_RULES.mappingEditTitle}
      width={480}
      open={open}
      onClose={onClose}
      destroyOnClose
      footer={
        <div style={{ textAlign: "right" }}>
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
        <Form.Item
          name="scenarioId"
          label="执行场景键"
          rules={[{ required: true }]}
          extra={isCreate ? undefined : "创建后不可修改"}
        >
          <Input disabled={!isCreate} placeholder="trade.spot.limit_order" />
        </Form.Item>
        <Form.Item name="capabilitySkuId" label="归入类型" rules={[{ required: true }]}>
          <Select options={CAPABILITY_OPTIONS.map((o) => ({ value: o.value, label: o.label }))} />
        </Form.Item>
      </Form>
    </Drawer>
  );
}
