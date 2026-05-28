import { App, Button, Card, Popconfirm, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { useMemo, useState } from "react";
import { zhCapabilitySku } from "../../copy/billingLabels";
import { BILLING_RESOURCES } from "../../copy/opsPanelHints";
import type { MockCommerceResourcePack } from "../../data/types";
import { useResourcePacks } from "../../hooks/useResourcePacks";
import { ResourcePackDetailDrawer, ResourcePackFormDrawer } from "./ResourcePackDrawers";

const { Link: TypographyLink } = Typography;

type PanelMode = "detail" | "form" | null;

function formatCreatedAt(iso?: string): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("zh-CN", { hour12: false });
  } catch {
    return iso;
  }
}

function formatPrice(pack: MockCommerceResourcePack): string {
  if (pack.priceUsdt) return `${pack.priceUsdt} USDT`;
  if (pack.packKind === "subscription") return "含于套餐";
  return "—";
}

export function ResourcesPanel() {
  const { message } = App.useApp();
  const { packs, upsertPack, deletePack } = useResourcePacks();
  const [selected, setSelected] = useState<MockCommerceResourcePack | null>(null);
  const [mode, setMode] = useState<PanelMode>(null);
  const [formMode, setFormMode] = useState<"create" | "edit">("edit");

  const sortedPacks = useMemo(
    () =>
      [...packs].sort((a, b) => {
        const ta = a.createdAt ? Date.parse(a.createdAt) : 0;
        const tb = b.createdAt ? Date.parse(b.createdAt) : 0;
        return tb - ta || Number(a.resourceId) - Number(b.resourceId);
      }),
    [packs],
  );

  const openDetail = (pack: MockCommerceResourcePack) => {
    setSelected(pack);
    setMode("detail");
  };

  const openForm = (pack: MockCommerceResourcePack | null, edit: "create" | "edit") => {
    setSelected(pack);
    setFormMode(edit);
    setMode("form");
  };

  const close = () => setMode(null);

  const handleDelete = (pack: MockCommerceResourcePack) => {
    deletePack(pack.resourceId);
    message.success(BILLING_RESOURCES.deleteSuccess);
    if (selected?.resourceId === pack.resourceId) close();
  };

  const columns: ColumnsType<MockCommerceResourcePack> = [
    {
      title: "资源 ID",
      dataIndex: "resourceId",
      width: 100,
      ellipsis: true,
      render: (id: string, row) => (
        <TypographyLink onClick={() => openDetail(row)} style={{ fontFamily: "monospace" }}>
          {id}
        </TypographyLink>
      ),
    },
    { title: "资源名称", dataIndex: "name", width: 160, ellipsis: true },
    {
      title: "资源类型",
      dataIndex: "packKind",
      width: 96,
      render: (k: MockCommerceResourcePack["packKind"]) =>
        k === "subscription" ? <Tag>订阅资源</Tag> : <Tag color="purple">加购资源</Tag>,
    },
    {
      title: "Capability",
      dataIndex: "capabilitySkuId",
      width: 108,
      ellipsis: true,
      render: (s: string) => zhCapabilitySku(s),
    },
    {
      title: "资源配额",
      key: "quota",
      width: 112,
      align: "right",
      render: (_: unknown, row) => `${row.quotaUnits.toLocaleString("zh-CN")} / ${row.periodLabel}`,
    },
    {
      title: "资源价格",
      key: "price",
      width: 108,
      align: "right",
      render: (_: unknown, row) => formatPrice(row),
    },
    {
      title: "状态",
      dataIndex: "active",
      width: 72,
      align: "center",
      render: (a: boolean) => (a ? <Tag color="success">启用</Tag> : <Tag>停用</Tag>),
    },
    {
      title: "创建时间",
      dataIndex: "createdAt",
      width: 168,
      ellipsis: true,
      render: (v: string | undefined) => formatCreatedAt(v),
    },
    {
      title: "操作",
      key: "actions",
      width: 140,
      fixed: "right",
      render: (_: unknown, row) => (
        <Space size={4}>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openForm(row, "edit")}>
            修改
          </Button>
          <Popconfirm
            title={BILLING_RESOURCES.deleteConfirmTitle}
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
            新建资源
          </Button>
        }
      >
        <Table
          rowKey="resourceId"
          size="small"
          tableLayout="fixed"
          pagination={{ pageSize: 12, hideOnSinglePage: true }}
          dataSource={sortedPacks}
          columns={columns}
          scroll={{ x: 1060 }}
        />
      </Card>

      <ResourcePackDetailDrawer open={mode === "detail"} pack={selected} onClose={close} />
      <ResourcePackFormDrawer
        open={mode === "form"}
        mode={formMode}
        pack={formMode === "edit" ? selected : null}
        onClose={close}
        onSave={(pack) => {
          if (formMode === "create" && packs.some((p) => p.resourceId === pack.resourceId)) {
            message.error(BILLING_RESOURCES.duplicateResourceId);
            return;
          }
          upsertPack(pack);
        }}
      />
    </>
  );
}
