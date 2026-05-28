import {
  App,
  Button,
  Descriptions,
  Drawer,
  Form,
  Input,
  Select,
  Space,
  Switch,
  Table,
  Tabs,
  Tag,
  Typography,
} from "antd";
import { useEffect, useMemo, useState } from "react";
import { zhCapabilitySku } from "../../copy/billingLabels";
import { BILLING_SUBSCRIPTIONS } from "../../copy/opsPanelHints";
import type { MockCommerceResourcePack, MockCommerceSubscriptionTier } from "../../data/types";
import { resolvePacksForTier } from "./subscriptionPackUtils";

const { Text, Paragraph } = Typography;

type TierDrawerTab = "basic" | "resources";

function resourcePackKindLabel(kind: MockCommerceResourcePack["packKind"]): string {
  return kind === "subscription" ? "订阅资源" : "加购资源";
}

function formatResourceQuota(pack: MockCommerceResourcePack): string {
  return `${pack.quotaUnits.toLocaleString("zh-CN")} / ${pack.periodLabel}`;
}

function formatResourcePrice(pack: MockCommerceResourcePack): string {
  if (pack.priceUsdt) return `${pack.priceUsdt} USDT`;
  if (pack.packKind === "subscription") return "含于套餐";
  return "—";
}

const TIER_LINKED_RESOURCE_COLUMNS = [
  { title: "资源名称", dataIndex: "name", ellipsis: true },
  {
    title: "资源类型",
    dataIndex: "packKind",
    width: 100,
    render: (kind: MockCommerceResourcePack["packKind"]) => resourcePackKindLabel(kind),
  },
  {
    title: "资源配额",
    key: "quota",
    width: 120,
    align: "right" as const,
    render: (_: unknown, row: MockCommerceResourcePack) => formatResourceQuota(row),
  },
  {
    title: "资源价格",
    key: "price",
    width: 110,
    align: "right" as const,
    render: (_: unknown, row: MockCommerceResourcePack) => formatResourcePrice(row),
  },
];

function TierLinkedResourceTable({ linked }: { linked: MockCommerceResourcePack[] }) {
  return (
    <Table
      rowKey="resourceId"
      size="small"
      pagination={false}
      locale={{ emptyText: "暂未配置资源" }}
      dataSource={linked}
      columns={TIER_LINKED_RESOURCE_COLUMNS}
    />
  );
}

function TierResourceConfigView({ linked }: { linked: MockCommerceResourcePack[] }) {
  return <TierLinkedResourceTable linked={linked} />;
}

function TierResourceFormFields({
  packs,
  subscriptionPackOptions,
}: {
  packs: MockCommerceResourcePack[];
  subscriptionPackOptions: { value: string; label: string }[];
}) {
  const selectedIds = Form.useWatch<string[]>("resourcePackIds") ?? [];
  const linked = useMemo(
    () =>
      selectedIds
        .map((id) => packs.find((p) => p.resourceId === id))
        .filter((p): p is MockCommerceResourcePack => !!p),
    [selectedIds, packs],
  );

  return (
    <>
      <Form.Item
        name="resourcePackIds"
        label="添加资源"
        rules={[{ required: true, type: "array", min: 1, message: "请至少选择一个资源" }]}
      >
        <Select
          mode="multiple"
          placeholder="选择资源"
          options={subscriptionPackOptions}
          optionFilterProp="label"
        />
      </Form.Item>
      <TierLinkedResourceTable linked={linked} />
    </>
  );
}

type DetailProps = {
  open: boolean;
  tier: MockCommerceSubscriptionTier | null;
  packs: MockCommerceResourcePack[];
  onClose: () => void;
};

export function SubscriptionTierDetailDrawer({ open, tier, packs, onClose }: DetailProps) {
  const [tab, setTab] = useState<TierDrawerTab>("basic");
  const linked = tier ? resolvePacksForTier(tier, packs) : [];

  useEffect(() => {
    if (open) setTab("basic");
  }, [open, tier?.tierId]);

  return (
    <Drawer
      title={tier ? `套餐详情 · ${tier.name}` : "套餐详情"}
      width={600}
      open={open && !!tier}
      onClose={onClose}
      destroyOnClose
    >
      {tier ? (
        <Tabs
          activeKey={tab}
          onChange={(k) => setTab(k as TierDrawerTab)}
          items={[
            {
              key: "basic",
              label: "基本信息",
              children: (
                <Descriptions size="small" column={1} bordered>
                  <Descriptions.Item label="套餐 ID">
                    <Text code>{tier.tierId}</Text>
                  </Descriptions.Item>
                  <Descriptions.Item label="套餐名称">{tier.name}</Descriptions.Item>
                  <Descriptions.Item label="状态">
                    <Space size={4}>
                      {tier.active ? <Tag color="success">在售</Tag> : <Tag>下架</Tag>}
                      {tier.recommended ? <Tag color="blue">推荐</Tag> : null}
                    </Space>
                  </Descriptions.Item>
                  <Descriptions.Item label="标价">
                    {tier.priceUsdt} USDT / {tier.periodLabel}
                  </Descriptions.Item>
                  <Descriptions.Item label="介绍">{tier.tagline}</Descriptions.Item>
                  <Descriptions.Item label="卖点">
                    <ul style={{ margin: 0, paddingLeft: 18 }}>
                      {tier.highlights.map((h) => (
                        <li key={h} style={{ marginBottom: 4 }}>
                          {h}
                        </li>
                      ))}
                    </ul>
                  </Descriptions.Item>
                  {tier.internalNote ? (
                    <Descriptions.Item label="运营备注">
                      <Paragraph style={{ marginBottom: 0 }}>{tier.internalNote}</Paragraph>
                    </Descriptions.Item>
                  ) : null}
                </Descriptions>
              ),
            },
            {
              key: "resources",
              label: "资源配置",
              children: <TierResourceConfigView linked={linked} />,
            },
          ]}
        />
      ) : null}
    </Drawer>
  );
}

type EditFormValues = {
  tierId: string;
  name: string;
  tagline: string;
  priceUsdt: string;
  periodLabel: string;
  highlightsText: string;
  recommended: boolean;
  active: boolean;
  internalNote?: string;
  resourcePackIds: string[];
};

function tierToForm(tier: MockCommerceSubscriptionTier): EditFormValues {
  return {
    tierId: tier.tierId,
    name: tier.name,
    tagline: tier.tagline,
    priceUsdt: tier.priceUsdt,
    periodLabel: tier.periodLabel,
    highlightsText: tier.highlights.join("\n"),
    recommended: tier.recommended ?? false,
    active: tier.active,
    internalNote: tier.internalNote,
    resourcePackIds: [...tier.resourcePackIds],
  };
}

function formToTier(values: EditFormValues, base: MockCommerceSubscriptionTier | null): MockCommerceSubscriptionTier {
  const highlights = values.highlightsText
    .split("\n")
    .map((s) => s.trim())
    .filter(Boolean);
  return {
    tierId: values.tierId.trim(),
    name: values.name.trim(),
    tagline: values.tagline.trim(),
    priceUsdt: values.priceUsdt.trim(),
    periodLabel: values.periodLabel.trim(),
    highlights: highlights.length > 0 ? highlights : [values.name],
    recommended: values.recommended,
    active: values.active,
    internalNote: values.internalNote?.trim() || undefined,
    resourcePackIds: values.resourcePackIds ?? [],
    createdAt: base?.createdAt,
    updatedAt: base?.updatedAt,
  };
}

type FormDrawerProps = {
  open: boolean;
  mode: "create" | "edit";
  tier: MockCommerceSubscriptionTier | null;
  packs: MockCommerceResourcePack[];
  onClose: () => void;
  onSave: (tier: MockCommerceSubscriptionTier) => void;
};

export function SubscriptionTierFormDrawer({ open, mode, tier, packs, onClose, onSave }: FormDrawerProps) {
  const { message } = App.useApp();
  const [form] = Form.useForm<EditFormValues>();
  const [tab, setTab] = useState<TierDrawerTab>("basic");
  const isCreate = mode === "create";

  const subscriptionPackOptions = useMemo(
    () =>
      packs
        .filter((p) => p.packKind === "subscription" && p.active)
        .map((p) => ({
          value: p.resourceId,
          label: `${p.name}（${p.quotaUnits} · ${zhCapabilitySku(p.capabilitySkuId)}）`,
        })),
    [packs],
  );

  useEffect(() => {
    if (!open) return;
    setTab("basic");
    if (isCreate) {
      form.setFieldsValue({
        tierId: "",
        name: "",
        tagline: "",
        priceUsdt: "",
        periodLabel: "月",
        highlightsText: "",
        recommended: false,
        active: true,
        internalNote: "",
        resourcePackIds: [],
      });
    } else if (tier) {
      form.setFieldsValue(tierToForm(tier));
    }
  }, [open, isCreate, tier, form]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const tierId = values.tierId.trim();
      if (!/^\d+$/.test(tierId)) {
        message.error(BILLING_SUBSCRIPTIONS.tierIdInvalid);
        return;
      }
      onSave(formToTier(values, tier));
      message.success(isCreate ? BILLING_SUBSCRIPTIONS.createSuccess : BILLING_SUBSCRIPTIONS.saveSuccess);
      onClose();
    } catch {
      message.error(BILLING_SUBSCRIPTIONS.validateFailed);
    }
  };

  const title = isCreate
    ? BILLING_SUBSCRIPTIONS.createTitle
    : `${BILLING_SUBSCRIPTIONS.editTitle} · ${tier?.name ?? ""}`;

  return (
    <Drawer
      title={title}
      width={560}
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
        <Tabs
          activeKey={tab}
          onChange={(k) => setTab(k as TierDrawerTab)}
          items={[
            {
              key: "basic",
              label: "基本信息",
              children: (
                <>
                  <Form.Item
                    name="tierId"
                    label="套餐 ID"
                    rules={[
                      { required: true },
                      { pattern: /^\d+$/, message: BILLING_SUBSCRIPTIONS.tierIdInvalid },
                    ]}
                    extra={isCreate ? undefined : "创建后不可修改"}
                  >
                    <Input disabled={!isCreate} placeholder="1001" inputMode="numeric" />
                  </Form.Item>
                  <Form.Item name="name" label="套餐名称" rules={[{ required: true }]}>
                    <Input />
                  </Form.Item>
                  <Form.Item name="tagline" label="一句话介绍" rules={[{ required: true }]}>
                    <Input />
                  </Form.Item>
                  <Space style={{ width: "100%" }} size={12}>
                    <Form.Item name="priceUsdt" label="标价 USDT" rules={[{ required: true }]} style={{ flex: 1 }}>
                      <Input />
                    </Form.Item>
                    <Form.Item name="periodLabel" label="周期" rules={[{ required: true }]} style={{ width: 100 }}>
                      <Select options={[{ value: "月" }, { value: "年" }]} />
                    </Form.Item>
                  </Space>
                  <Form.Item name="highlightsText" label="卖点（每行一条）" rules={[{ required: true }]}>
                    <Input.TextArea rows={3} />
                  </Form.Item>
                  <Space size={24}>
                    <Form.Item name="recommended" label="推荐档位" valuePropName="checked">
                      <Switch />
                    </Form.Item>
                    <Form.Item name="active" label="在售" valuePropName="checked">
                      <Switch />
                    </Form.Item>
                  </Space>
                  <Form.Item name="internalNote" label="运营备注">
                    <Input.TextArea rows={2} />
                  </Form.Item>
                </>
              ),
            },
            {
              key: "resources",
              label: "资源配置",
              children: (
                <TierResourceFormFields packs={packs} subscriptionPackOptions={subscriptionPackOptions} />
              ),
            },
          ]}
        />
      </Form>
    </Drawer>
  );
}
