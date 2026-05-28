import { App, Button, Card, Popconfirm, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { useMemo, useState } from "react";
import { BILLING_SUBSCRIPTIONS } from "../../copy/opsPanelHints";
import type { MockCommerceSubscriptionTier } from "../../data/types";
import { useResourcePacks } from "../../hooks/useResourcePacks";
import { useSubscriptionTiers } from "../../hooks/useSubscriptionTiers";
import { SubscriptionTierDetailDrawer, SubscriptionTierFormDrawer } from "./SubscriptionTierDrawers";

const { Link: TypographyLink } = Typography;

type PanelMode = "detail" | "form" | null;

function formatTierCreatedAt(iso?: string): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("zh-CN", { hour12: false });
  } catch {
    return iso;
  }
}

export function SubscriptionsPanel() {
  const { message } = App.useApp();
  const { tiers, upsertTier, deleteTier } = useSubscriptionTiers();
  const { packs } = useResourcePacks();
  const [selected, setSelected] = useState<MockCommerceSubscriptionTier | null>(null);
  const [mode, setMode] = useState<PanelMode>(null);
  const [formMode, setFormMode] = useState<"create" | "edit">("edit");

  const sortedTiers = useMemo(
    () =>
      [...tiers].sort((a, b) => {
        const ta = a.createdAt ? Date.parse(a.createdAt) : 0;
        const tb = b.createdAt ? Date.parse(b.createdAt) : 0;
        return tb - ta || Number(a.tierId) - Number(b.tierId);
      }),
    [tiers],
  );

  const openDetail = (tier: MockCommerceSubscriptionTier) => {
    setSelected(tier);
    setMode("detail");
  };

  const openForm = (tier: MockCommerceSubscriptionTier | null, edit: "create" | "edit") => {
    setSelected(tier);
    setFormMode(edit);
    setMode("form");
  };

  const close = () => setMode(null);

  const handleDelete = (tier: MockCommerceSubscriptionTier) => {
    deleteTier(tier.tierId);
    message.success(BILLING_SUBSCRIPTIONS.deleteSuccess);
    if (selected?.tierId === tier.tierId) close();
  };

  const columns: ColumnsType<MockCommerceSubscriptionTier> = [
    {
      title: "套餐 ID",
      dataIndex: "tierId",
      width: 120,
      ellipsis: true,
      render: (id: string, row) => (
        <TypographyLink onClick={() => openDetail(row)} style={{ fontFamily: "monospace" }}>
          {id}
        </TypographyLink>
      ),
    },
    {
      title: "套餐名称",
      dataIndex: "name",
      width: 140,
      ellipsis: true,
    },
    {
      title: "价格",
      key: "price",
      width: 168,
      ellipsis: true,
      render: (_: unknown, row) => `${row.priceUsdt} USDT / ${row.periodLabel}`,
    },
    {
      title: "状态",
      key: "status",
      width: 96,
      align: "center",
      render: (_: unknown, row) => (row.active ? <Tag color="success">在售</Tag> : <Tag>下架</Tag>),
    },
    {
      title: "创建时间",
      dataIndex: "createdAt",
      width: 176,
      ellipsis: true,
      render: (v: string | undefined) => formatTierCreatedAt(v),
    },
    {
      title: "操作",
      key: "actions",
      width: 152,
      fixed: "right",
      render: (_: unknown, row) => (
        <Space size={4}>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openForm(row, "edit")}>
            修改
          </Button>
          <Popconfirm
            title={BILLING_SUBSCRIPTIONS.deleteConfirmTitle}
            onConfirm={() => handleDelete(row)}
            okText="删除"
            okButtonProps={{ danger: true }}
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Card
        size="small"
        className="admin-panel-card"
        extra={
          <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => openForm(null, "create")}>
            新建套餐
          </Button>
        }
      >
        <Table
          rowKey="tierId"
          size="small"
          tableLayout="fixed"
          pagination={{ pageSize: 10, hideOnSinglePage: true }}
          dataSource={sortedTiers}
          columns={columns}
          scroll={{ x: 852 }}
        />
      </Card>

      <SubscriptionTierDetailDrawer open={mode === "detail"} tier={selected} packs={packs} onClose={close} />
      <SubscriptionTierFormDrawer
        open={mode === "form"}
        mode={formMode}
        tier={formMode === "edit" ? selected : null}
        packs={packs}
        onClose={close}
        onSave={(tier) => {
          if (formMode === "create" && tiers.some((t) => t.tierId === tier.tierId)) {
            message.error(BILLING_SUBSCRIPTIONS.duplicateTierId);
            return;
          }
          upsertTier(tier);
        }}
      />
    </>
  );
}
