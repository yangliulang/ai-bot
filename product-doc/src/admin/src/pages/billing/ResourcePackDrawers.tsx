import {
  App,
  Button,
  Descriptions,
  Drawer,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Switch,
  Tag,
  Typography,
} from "antd";
import { useEffect } from "react";
import { zhCapabilitySku } from "../../copy/billingLabels";
import { BILLING_RESOURCES } from "../../copy/opsPanelHints";
import type { MockCommerceResourcePack, MockCommerceResourcePackKind } from "../../data/types";

const { Text, Paragraph } = Typography;

const CAPABILITY_OPTIONS = [
  { value: "cap.agent.analyze", label: "AI 分析" },
  { value: "cap.agent.trade", label: "自动交易" },
  { value: "cap.agent.monitoring", label: "盯盘监控" },
];

const PERIOD_OPTIONS = [{ value: "月" }, { value: "年" }, { value: "一次性" }, { value: "30 天" }];

function packKindLabel(kind: MockCommerceResourcePackKind): string {
  return kind === "subscription" ? "订阅资源" : "加购资源";
}

function formatResourcePrice(pack: MockCommerceResourcePack): string {
  if (pack.priceUsdt) return `${pack.priceUsdt} USDT`;
  if (pack.packKind === "subscription") return "含于套餐";
  return "—";
}

function formatCreatedAt(iso?: string): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("zh-CN", { hour12: false });
  } catch {
    return iso;
  }
}

type DetailProps = {
  open: boolean;
  pack: MockCommerceResourcePack | null;
  onClose: () => void;
};

export function ResourcePackDetailDrawer({ open, pack, onClose }: DetailProps) {
  return (
    <Drawer
      title={pack ? `资源详情 · ${pack.name}` : "资源详情"}
      width={560}
      open={open && !!pack}
      onClose={onClose}
      destroyOnClose
    >
      {pack ? (
        <Descriptions size="small" column={1} bordered>
          <Descriptions.Item label="资源 ID">
            <Text code>{pack.resourceId}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="资源名称">{pack.name}</Descriptions.Item>
          <Descriptions.Item label="资源类型">{packKindLabel(pack.packKind)}</Descriptions.Item>
          <Descriptions.Item label="Capability">{zhCapabilitySku(pack.capabilitySkuId)}</Descriptions.Item>
          <Descriptions.Item label="资源配额">
            {pack.quotaUnits.toLocaleString("zh-CN")} / {pack.periodLabel}
          </Descriptions.Item>
          <Descriptions.Item label="资源价格">{formatResourcePrice(pack)}</Descriptions.Item>
          <Descriptions.Item label="状态">
            {pack.active ? <Tag color="success">启用</Tag> : <Tag>停用</Tag>}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">{formatCreatedAt(pack.createdAt)}</Descriptions.Item>
          {pack.description ? (
            <Descriptions.Item label="说明">
              <Paragraph style={{ marginBottom: 0 }}>{pack.description}</Paragraph>
            </Descriptions.Item>
          ) : null}
        </Descriptions>
      ) : null}
    </Drawer>
  );
}

type EditFormValues = {
  resourceId: string;
  name: string;
  packKind: MockCommerceResourcePackKind;
  capabilitySkuId: string;
  quotaUnits: number;
  periodLabel: string;
  priceUsdt?: string;
  active: boolean;
  description?: string;
};

function packToForm(pack: MockCommerceResourcePack): EditFormValues {
  return {
    resourceId: pack.resourceId,
    name: pack.name,
    packKind: pack.packKind,
    capabilitySkuId: pack.capabilitySkuId,
    quotaUnits: pack.quotaUnits,
    periodLabel: pack.periodLabel,
    priceUsdt: pack.priceUsdt,
    active: pack.active,
    description: pack.description,
  };
}

function formToPack(values: EditFormValues, base: MockCommerceResourcePack | null): MockCommerceResourcePack {
  return {
    resourceId: values.resourceId.trim(),
    name: values.name.trim(),
    packKind: values.packKind,
    capabilitySkuId: values.capabilitySkuId,
    quotaUnits: values.quotaUnits,
    periodLabel: values.periodLabel.trim(),
    priceUsdt: values.priceUsdt?.trim() || undefined,
    active: values.active,
    description: values.description?.trim() || undefined,
    createdAt: base?.createdAt,
    updatedAt: base?.updatedAt,
  };
}

type FormDrawerProps = {
  open: boolean;
  mode: "create" | "edit";
  pack: MockCommerceResourcePack | null;
  onClose: () => void;
  onSave: (pack: MockCommerceResourcePack) => void;
};

export function ResourcePackFormDrawer({ open, mode, pack, onClose, onSave }: FormDrawerProps) {
  const { message } = App.useApp();
  const [form] = Form.useForm<EditFormValues>();
  const isCreate = mode === "create";

  useEffect(() => {
    if (!open) return;
    if (isCreate) {
      form.setFieldsValue({
        resourceId: "",
        name: "",
        packKind: "subscription",
        capabilitySkuId: "cap.agent.analyze",
        quotaUnits: 100,
        periodLabel: "月",
        priceUsdt: "",
        active: true,
        description: "",
      });
    } else if (pack) {
      form.setFieldsValue(packToForm(pack));
    }
  }, [open, isCreate, pack, form]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const resourceId = values.resourceId.trim();
      if (!/^\d+$/.test(resourceId)) {
        message.error(BILLING_RESOURCES.resourceIdInvalid);
        return;
      }
      onSave(formToPack(values, pack));
      message.success(isCreate ? BILLING_RESOURCES.createSuccess : BILLING_RESOURCES.saveSuccess);
      onClose();
    } catch {
      message.error(BILLING_RESOURCES.validateFailed);
    }
  };

  const title = isCreate
    ? BILLING_RESOURCES.createTitle
    : `${BILLING_RESOURCES.editTitle} · ${pack?.name ?? ""}`;

  return (
    <Drawer
      title={title}
      width={520}
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
      <Form form={form} layout="vertical" requiredMark="optional">
        <Form.Item
          name="resourceId"
          label="资源 ID"
          rules={[
            { required: true },
            { pattern: /^\d+$/, message: BILLING_RESOURCES.resourceIdInvalid },
          ]}
          extra={isCreate ? undefined : "创建后不可修改"}
        >
          <Input disabled={!isCreate} placeholder="2001" inputMode="numeric" />
        </Form.Item>
        <Form.Item name="name" label="资源名称" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="packKind" label="资源类型" rules={[{ required: true }]}>
          <Select
            options={[
              { value: "subscription", label: "订阅资源" },
              { value: "addon", label: "加购资源" },
            ]}
          />
        </Form.Item>
        <Form.Item name="capabilitySkuId" label="Capability" rules={[{ required: true }]}>
          <Select options={CAPABILITY_OPTIONS} />
        </Form.Item>
        <Space style={{ width: "100%" }} size={12}>
          <Form.Item name="quotaUnits" label="资源配额" rules={[{ required: true, type: "number", min: 0 }]} style={{ flex: 1 }}>
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="periodLabel" label="周期" rules={[{ required: true }]} style={{ width: 120 }}>
            <Select options={PERIOD_OPTIONS} />
          </Form.Item>
        </Space>
        <Form.Item name="priceUsdt" label="资源价格（USDT）">
          <Input placeholder="加购资源填写；订阅资源可留空" />
        </Form.Item>
        <Form.Item name="active" label="启用" valuePropName="checked">
          <Switch />
        </Form.Item>
        <Form.Item name="description" label="说明">
          <Input.TextArea rows={2} />
        </Form.Item>
      </Form>
    </Drawer>
  );
}
