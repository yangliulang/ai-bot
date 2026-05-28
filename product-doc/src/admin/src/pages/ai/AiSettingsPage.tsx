import { useEffect, useMemo, useState } from "react";
import {
  App,
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Select,
  Space,
  Switch,
  Table,
  Tabs,
  Tag,
  Tooltip,
  Typography,
  theme,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { PlusOutlined, SaveOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { ProductPageShell } from "../../components/product";
import {
  AI_RUNTIME_POLICY_INITIAL,
  SCENARIO_MODEL_FIELDS,
} from "../../data/aiRuntimePolicyMock";
import {
  DEFAULT_BASE_URL_BY_CATALOG,
  LLM_MODEL_PRESETS,
  LLM_VENDOR_CATALOG_LABELS,
  MOCK_LLM_GATEWAY_INITIAL,
  buildRuntimeModelSelectOptions,
  capabilityLabel,
  flattenProviderModels,
  getAddablePresetModelsForProvider,
  healthStatusTag,
  type LlmVendorCatalogKind,
  type MockLlmModelEntry,
  type MockLlmProviderWithModels,
} from "../../data/aiSettingsInfraMock";

const { Text } = Typography;

const CATALOG_KIND_OPTIONS = (["openai", "anthropic", "deepseek", "none"] as const).map((k) => ({
  value: k,
  label: LLM_VENDOR_CATALOG_LABELS[k],
}));

const PROVIDER_ID_PATTERN = /^[a-z][a-z0-9_-]{0,63}$/;

/** 根据展示名生成唯一 providerId（不落界面；纯 ASCII 名称更可读，其余退化为 vendor / vendor-n） */
function suggestProviderId(displayName: string, existingIds: readonly string[]): string {
  const taken = new Set(existingIds);
  let slug = displayName
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9\s_-]/g, "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/_+/g, "-")
    .replace(/^-+|-+$/g, "");

  while (slug.length && !/[a-z]/.test(slug.charAt(0))) {
    slug = slug.slice(1);
  }

  let base = slug.length ? slug : "vendor";
  if (!PROVIDER_ID_PATTERN.test(base)) {
    base = "vendor";
  }
  base = base.slice(0, 48);

  let candidate = base;
  let n = 0;
  while (taken.has(candidate)) {
    n += 1;
    candidate = `${base}-${n}`;
    if (!PROVIDER_ID_PATTERN.test(candidate)) {
      candidate = `vendor-${n}`;
    }
    if (n > 500) {
      candidate = `vendor-${Date.now()}`;
      break;
    }
  }
  return candidate;
}

function formatTokens(n: number | string | null | undefined): string {
  if (n === "" || n == null) return "";
  const num = typeof n === "string" ? Number(String(n).replace(/\D/g, "")) : n;
  if (Number.isNaN(num)) return "";
  return num.toLocaleString("en-US");
}

function parseTokens(s: string | undefined): number {
  if (!s) return 0;
  const n = Number(String(s).replace(/,/g, ""));
  return Number.isNaN(n) ? 0 : n;
}

function cloneGatewayInitial(): MockLlmProviderWithModels[] {
  return structuredClone(MOCK_LLM_GATEWAY_INITIAL);
}

export function AiSettingsPage() {
  const { message } = App.useApp();
  const [policyForm] = Form.useForm();
  const [providerForm] = Form.useForm();
  const [modelForm] = Form.useForm();
  const { token } = theme.useToken();

  const [gatewayProviders, setGatewayProviders] = useState<MockLlmProviderWithModels[]>(() => cloneGatewayInitial());
  const [providerModalOpen, setProviderModalOpen] = useState(false);
  const [providerModalMode, setProviderModalMode] = useState<"create" | "edit">("create");
  const [editingProviderId, setEditingProviderId] = useState<string | null>(null);

  const [modelModalOpen, setModelModalOpen] = useState(false);
  const [modelModalProviderId, setModelModalProviderId] = useState<string | null>(null);

  const modelSelectOptions = useMemo(
    () => buildRuntimeModelSelectOptions(gatewayProviders),
    [gatewayProviders],
  );

  const policyModelFieldNames = useMemo(
    () =>
      ["defaultInferenceModel", ...SCENARIO_MODEL_FIELDS.map((s) => s.field), "fallbackModel"] as const,
    [],
  );

  /** 网关增删改后，策略里已选 modelId 若不再可用则回退到列表首项或清空 */
  useEffect(() => {
    const allowed = new Set(modelSelectOptions.map((o) => o.value));
    const cur = policyForm.getFieldsValue([...policyModelFieldNames]) as Record<string, string | undefined>;
    const patch: Record<string, string | undefined> = {};
    const fallback = modelSelectOptions[0]?.value;
    for (const f of policyModelFieldNames) {
      const v = cur[f];
      if (v != null && v !== "" && !allowed.has(v)) {
        patch[f] = fallback;
      }
    }
    if (Object.keys(patch).length > 0) {
      policyForm.setFieldsValue(patch);
    }
  }, [modelSelectOptions, policyForm, policyModelFieldNames]);

  const closeProviderModal = () => {
    setProviderModalOpen(false);
    setEditingProviderId(null);
    providerForm.resetFields();
  };

  const openCreateProvider = () => {
    setProviderModalMode("create");
    setEditingProviderId(null);
    providerForm.resetFields();
    providerForm.setFieldsValue({
      enabled: true,
      vendorPreset: "openai",
      baseUrl: DEFAULT_BASE_URL_BY_CATALOG.openai,
    });
    setProviderModalOpen(true);
  };

  const openEditProvider = (row: MockLlmProviderWithModels) => {
    setProviderModalMode("edit");
    setEditingProviderId(row.providerId);
    providerForm.setFieldsValue({
      vendorPreset: row.catalogKind,
      displayName: row.displayName,
      baseUrl: row.baseUrl,
      secretRef: row.secretRef,
      enabled: row.enabled,
    });
    setProviderModalOpen(true);
  };

  const saveProviderModal = () => {
    providerForm.validateFields().then((vals) => {
      const baseUrl = String(vals.baseUrl ?? "").trim();
      const secretTrim = String(vals.secretRef ?? "").trim();
      const enabled = Boolean(vals.enabled);

      if (providerModalMode === "create") {
        const preset = vals.vendorPreset as LlmVendorCatalogKind | undefined;
        if (!preset) {
          message.error("请选择厂商");
          return;
        }
        const catalogKind = preset;
        const displayName =
          preset !== "none"
            ? LLM_VENDOR_CATALOG_LABELS[preset]
            : String(vals.customDisplayName ?? "").trim();
        if (!displayName) {
          message.error("请填写厂商名称");
          return;
        }
        const rawId = suggestProviderId(displayName, gatewayProviders.map((p) => p.providerId));
        setGatewayProviders((prev) => [
          ...prev,
          {
            providerId: rawId,
            displayName,
            catalogKind,
            baseUrl,
            secretRef: secretTrim,
            enabled,
            healthStatus: "unknown",
            lastProbedAt: null,
            models: [],
          },
        ]);
        message.success("已添加厂商");
      } else if (editingProviderId) {
        const displayName = String(vals.displayName ?? "").trim();
        setGatewayProviders((prev) =>
          prev.map((p) =>
            p.providerId === editingProviderId
              ? {
                  ...p,
                  displayName: displayName || p.displayName,
                  baseUrl,
                  secretRef: secretTrim || p.secretRef,
                  enabled,
                }
              : p,
          ),
        );
        message.success("已保存");
      }
      closeProviderModal();
    });
  };

  const deleteProvider = (row: MockLlmProviderWithModels) => {
    const n = row.models.length;
    setGatewayProviders((prev) => prev.filter((p) => p.providerId !== row.providerId));
    message.success(n > 0 ? `已删除厂商（含 ${n} 个模型）` : "已删除厂商");
  };

  const probeProvider = (row: MockLlmProviderWithModels) => {
    setGatewayProviders((prev) =>
      prev.map((p) =>
        p.providerId === row.providerId
          ? {
              ...p,
              healthStatus: "healthy",
              lastProbedAt: new Date().toISOString(),
            }
          : p,
      ),
    );
    message.success("探测完成");
  };

  const toggleProviderInline = (row: MockLlmProviderWithModels, enabled: boolean) => {
    setGatewayProviders((prev) =>
      prev.map((p) => (p.providerId === row.providerId ? { ...p, enabled } : p)),
    );
  };

  const setModelEnabled = (providerId: string, modelId: string, enabled: boolean) => {
    setGatewayProviders((prev) =>
      prev.map((p) =>
        p.providerId !== providerId
          ? p
          : {
              ...p,
              models: p.models.map((m) => (m.modelId === modelId ? { ...m, enabled } : m)),
            },
      ),
    );
  };

  const deleteModelEntry = (providerId: string, modelId: string) => {
    setGatewayProviders((prev) =>
      prev.map((p) =>
        p.providerId !== providerId ? p : { ...p, models: p.models.filter((m) => m.modelId !== modelId) },
      ),
    );
    message.success("已删除模型");
  };

  const openAddModel = (parent: MockLlmProviderWithModels) => {
    setModelModalProviderId(parent.providerId);
    modelForm.resetFields();
    modelForm.setFieldsValue({ enabled: true });
    setModelModalOpen(true);
  };

  const presetSelectOptions = useMemo(() => {
    if (!modelModalOpen || !modelModalProviderId) return [];
    const parent = gatewayProviders.find((p) => p.providerId === modelModalProviderId);
    if (!parent) return [];
    return getAddablePresetModelsForProvider(parent, gatewayProviders).map((p) => ({
      value: p.modelId,
      label: p.displayLabel,
    }));
  }, [modelModalOpen, modelModalProviderId, gatewayProviders]);

  const closeModelModal = () => {
    setModelModalOpen(false);
    setModelModalProviderId(null);
    modelForm.resetFields();
  };

  const saveModelModal = () => {
    if (!modelModalProviderId) return;
    modelForm.validateFields().then((vals) => {
      const parent = gatewayProviders.find((p) => p.providerId === modelModalProviderId);
      if (!parent) {
        closeModelModal();
        return;
      }
      if (parent.catalogKind === "none") {
        message.error("当前厂商无预置模型目录");
        return;
      }
      const presetModelId = String(vals.presetModelId ?? "").trim();
      if (!presetModelId) {
        message.error("请选择模型");
        return;
      }
      const catalog = LLM_MODEL_PRESETS[parent.catalogKind];
      const preset = catalog.find((p) => p.modelId === presetModelId);
      if (!preset) {
        message.error("所选模型不在当前接入类型的清单内");
        return;
      }
      const taken = new Set(flattenProviderModels(gatewayProviders).map((m) => m.modelId));
      if (taken.has(preset.modelId)) {
        message.error("该模型已被接入");
        return;
      }
      const entry: MockLlmModelEntry = {
        ...preset,
        enabled: Boolean(vals.enabled),
      };
      setGatewayProviders((prev) =>
        prev.map((p) =>
          p.providerId !== modelModalProviderId ? p : { ...p, models: [...p.models, entry] },
        ),
      );
      message.success("已添加模型");
      closeModelModal();
    });
  };

  const resetDemo = () => {
    setGatewayProviders(cloneGatewayInitial());
    policyForm.setFieldsValue(AI_RUNTIME_POLICY_INITIAL);
    message.info("已恢复默认");
  };

  const nestedModelColumns = (providerId: string): ColumnsType<MockLlmModelEntry> => [
    {
      title: "modelId",
      dataIndex: "modelId",
      key: "mid",
      width: 200,
      render: (id: string) => (
        <Text code style={{ fontSize: 12 }}>
          {id}
        </Text>
      ),
    },
    { title: "展示名", dataIndex: "displayLabel", key: "lbl", width: 140 },
    {
      title: "上下文窗",
      dataIndex: "contextWindow",
      key: "ctx",
      width: 100,
      align: "right",
      render: (n: number) => n.toLocaleString("en-US"),
    },
    {
      title: "能力",
      dataIndex: "capabilities",
      key: "cap",
      render: (caps: MockLlmModelEntry["capabilities"]) => (
        <Space size={4} wrap>
          {caps.map((c) => (
            <Tag key={c} style={{ marginInlineEnd: 0 }}>
              {capabilityLabel(c)}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: "状态",
      key: "st",
      width: 80,
      render: (_, row) => (row.deprecated ? <Tag color="warning">弃用</Tag> : <Tag color="processing">现行</Tag>),
    },
    {
      title: "启用",
      key: "en",
      width: 80,
      render: (_, row) => (
        <Switch
          checked={row.enabled}
          disabled={row.deprecated}
          onChange={(v) => setModelEnabled(providerId, row.modelId, v)}
        />
      ),
    },
    {
      title: "操作",
      key: "act",
      width: 72,
      render: (_, row) => (
        <Popconfirm title="删除该模型？" onConfirm={() => deleteModelEntry(providerId, row.modelId)}>
          <Button type="link" size="small" danger style={{ paddingInline: 0 }}>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  const providerColumns: ColumnsType<MockLlmProviderWithModels> = [
    {
      title: "厂商",
      key: "vendor",
      width: 148,
      ellipsis: true,
      render: (_, row) => (
        <Text strong ellipsis={{ tooltip: row.displayName }}>
          {row.displayName}
        </Text>
      ),
    },
    {
      title: "下属模型",
      key: "mc",
      width: 96,
      render: (_, row) => {
        const active = row.models.filter((m) => m.enabled && !m.deprecated).length;
        const total = row.models.length;
        return (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {active}/{total}
          </Text>
        );
      },
    },
    {
      title: "Base URL",
      dataIndex: "baseUrl",
      key: "base",
      ellipsis: true,
      render: (u: string) => (
        <Text copyable={{ text: u }} style={{ fontSize: 12 }}>
          {u}
        </Text>
      ),
    },
    {
      title: "密钥",
      dataIndex: "secretRef",
      key: "sec",
      ellipsis: true,
      render: (ref: string) => (
        <Text type="secondary" ellipsis={{ tooltip: ref }} style={{ fontSize: 12 }}>
          {ref}
        </Text>
      ),
    },
    {
      title: "健康",
      dataIndex: "healthStatus",
      key: "h",
      width: 112,
      render: (h: MockLlmProviderWithModels["healthStatus"]) => {
        const t = healthStatusTag(h);
        return <Tag color={t.color}>{t.label}</Tag>;
      },
    },
    {
      title: "启用",
      dataIndex: "enabled",
      key: "en",
      width: 80,
      render: (_, row) => <Switch checked={row.enabled} onChange={(v) => toggleProviderInline(row, v)} />,
    },
    {
      title: "操作",
      key: "act",
      width: 212,
      fixed: "right",
      render: (_, row) => {
        const linkedModels = row.models.length;
        return (
          <Space size={4} wrap>
            <Button type="link" size="small" style={{ paddingInline: 0 }} onClick={() => openEditProvider(row)}>
              修改
            </Button>
            <Button
              type="link"
              size="small"
              icon={<ThunderboltOutlined />}
              style={{ paddingInline: 0 }}
              onClick={() => probeProvider(row)}
            >
              探测
            </Button>
            <Popconfirm
              title="确认删除该厂商？"
              description={linkedModels > 0 ? `将删除其下 ${linkedModels} 个模型。` : undefined}
              okText="删除"
              okButtonProps={{ danger: true }}
              onConfirm={() => deleteProvider(row)}
            >
              <Button type="link" size="small" danger style={{ paddingInline: 0 }}>
                删除
              </Button>
            </Popconfirm>
          </Space>
        );
      },
    },
  ];

  const gatewayPanel = (
    <Card
      size="small"
      className="admin-panel-card"
      title="厂商与模型"
      styles={{ body: { paddingTop: 8 } }}
      extra={
        <Button type="primary" size="small" icon={<PlusOutlined />} onClick={openCreateProvider}>
          添加厂商
        </Button>
      }
    >
        <Table<MockLlmProviderWithModels>
          rowKey="providerId"
          size="middle"
          columns={providerColumns}
          dataSource={gatewayProviders}
          pagination={false}
          scroll={{ x: 920 }}
          expandable={{
            expandedRowRender: (record) => {
              const addable = getAddablePresetModelsForProvider(record, gatewayProviders);
              const addDisabled = record.catalogKind === "none" || addable.length === 0;
              const tip =
                record.catalogKind === "none"
                  ? "请先在接入类型中选择带预置模型目录的底座"
                  : addable.length === 0
                    ? "可添加的预置模型已全部接入或已被其他厂商占用"
                    : undefined;
              return (
                <div
                  style={{
                    margin: "4px 0 12px 0",
                    padding: 16,
                    background: token.colorFillAlter,
                    borderRadius: token.borderRadius,
                  }}
                >
                  <Space direction="vertical" size={12} style={{ width: "100%" }}>
                    <Tooltip title={tip}>
                      <span>
                        <Button
                          size="small"
                          type="primary"
                          ghost
                          icon={<PlusOutlined />}
                          disabled={addDisabled}
                          onClick={() => openAddModel(record)}
                        >
                          添加模型
                        </Button>
                      </span>
                    </Tooltip>
                    <Table<MockLlmModelEntry>
                      size="small"
                      rowKey="modelId"
                      columns={nestedModelColumns(record.providerId)}
                      dataSource={record.models}
                      pagination={false}
                      locale={{ emptyText: "暂无模型" }}
                    />
                  </Space>
                </div>
              );
            },
            rowExpandable: () => true,
          }}
        />
      </Card>
  );

  const policyPanel = (
    <Form
      form={policyForm}
      layout="vertical"
      initialValues={AI_RUNTIME_POLICY_INITIAL}
      scrollToFirstError={{ behavior: "smooth", block: "center" }}
      onFinish={() => message.success("已保存")}
    >
      <Card size="small" className="admin-panel-card" title="推理与路由" style={{ marginBottom: 16 }}>
        <Form.Item name="defaultInferenceModel" label="默认模型" rules={[{ required: true, message: "请选择" }]}>
          <Select showSearch optionFilterProp="label" options={modelSelectOptions} placeholder="选择模型" />
        </Form.Item>
        <Row gutter={[16, 0]}>
          {SCENARIO_MODEL_FIELDS.map((s) => (
            <Col xs={24} md={8} key={s.rowKey}>
              <Form.Item name={s.field} label={s.label} rules={[{ required: true, message: "请选择" }]}>
                <Select showSearch optionFilterProp="label" options={modelSelectOptions} placeholder="选择模型" />
              </Form.Item>
            </Col>
          ))}
        </Row>
      </Card>

      <Card size="small" className="admin-panel-card" title="Token 与超时" style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Form.Item name="maxContextTokens" label="Max Context" rules={[{ required: true, message: "必填" }]}>
              <InputNumber
                min={1024}
                max={2000000}
                addonAfter="tokens"
                style={{ width: "100%" }}
                formatter={formatTokens}
                parser={parseTokens}
              />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="maxOutputTokens" label="Max Output" rules={[{ required: true, message: "必填" }]}>
              <InputNumber
                min={256}
                max={32768}
                addonAfter="tokens"
                style={{ width: "100%" }}
                formatter={formatTokens}
                parser={parseTokens}
              />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="timeoutSec" label="Timeout" rules={[{ required: true, message: "必填" }]}>
              <InputNumber min={5} max={600} addonAfter="秒" style={{ width: "100%" }} />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      <Card size="small" className="admin-panel-card" title="降级" style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Form.Item name="fallbackOnPrimaryFailure" label="失败时切换" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Col>
          <Col xs={24} sm={8}>
            <Form.Item name="fallbackOnTimeout" label="超时时降级" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Col>
          <Col xs={24} sm={8}>
            <Form.Item name="downgradePeakTraffic" label="高峰期降级" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item name="fallbackModel" label="降级模型" rules={[{ required: true, message: "请选择" }]}>
          <Select showSearch optionFilterProp="label" options={modelSelectOptions} placeholder="选择模型" />
        </Form.Item>
      </Card>

      <Card size="small" className="admin-panel-card" title="成本与限流" style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Form.Item
              name="maxTokensPerRequest"
              label="单次请求上限"
              dependencies={["maxContextTokens"]}
              rules={[
                { required: true, message: "必填" },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    const ctx = getFieldValue("maxContextTokens") as number | undefined;
                    if (ctx != null && typeof value === "number" && value > ctx) {
                      return Promise.reject(new Error("不得超过 Max Context"));
                    }
                    return Promise.resolve();
                  },
                }),
              ]}
            >
              <InputNumber
                min={1024}
                addonAfter="tokens"
                style={{ width: "100%" }}
                formatter={formatTokens}
                parser={parseTokens}
              />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="dailyTokenBudgetM" label="单日预算" rules={[{ required: true, message: "必填" }]}>
              <InputNumber min={1} max={10000} addonAfter="百万 tokens" style={{ width: "100%" }} precision={0} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="rateLimitRpm" label="RPM 上限" rules={[{ required: true, message: "必填" }]}>
              <InputNumber min={1} addonAfter="/ 分钟" style={{ width: "100%" }} precision={0} />
            </Form.Item>
          </Col>
        </Row>
      </Card>

      <div
        style={{
          position: "sticky",
          bottom: 0,
          paddingTop: 8,
          paddingBottom: 8,
          background: token.colorBgContainer,
          borderTop: `1px solid ${token.colorBorderSecondary}`,
        }}
      >
        <Space wrap>
          <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
            保存
          </Button>
          <Button onClick={resetDemo}>恢复默认</Button>
        </Space>
      </div>
    </Form>
  );

  const modelParentLabel = gatewayProviders.find((p) => p.providerId === modelModalProviderId)?.displayName ?? "";

  return (
    <ProductPageShell pageId="ai.settings" showPageId={false} title="模型配置">
      <Tabs
        defaultActiveKey="gateway"
        items={[
          { key: "gateway", label: "厂商与模型", children: gatewayPanel },
          { key: "policy", label: "使用策略", children: policyPanel },
        ]}
      />

      <Modal
        title={
          providerModalMode === "create"
            ? "添加厂商"
            : `修改 · ${gatewayProviders.find((p) => p.providerId === editingProviderId)?.displayName ?? ""}`
        }
        open={providerModalOpen}
        onOk={saveProviderModal}
        onCancel={closeProviderModal}
        destroyOnClose
        width={560}
        okText={providerModalMode === "create" ? "添加" : "保存"}
      >
        <Form
          form={providerForm}
          layout="vertical"
          onValuesChange={(changed) => {
            if (providerModalMode !== "create") return;
            if (changed.vendorPreset != null && changed.vendorPreset !== "none") {
              const k = changed.vendorPreset as keyof typeof DEFAULT_BASE_URL_BY_CATALOG;
              const def = DEFAULT_BASE_URL_BY_CATALOG[k];
              if (def) {
                const cur = providerForm.getFieldValue("baseUrl");
                if (!String(cur ?? "").trim()) {
                  providerForm.setFieldsValue({ baseUrl: def });
                }
              }
            }
          }}
        >
          {providerModalMode === "create" ? (
            <Form.Item label="厂商" required>
              <Space direction="vertical" size={8} style={{ width: "100%" }}>
                <Form.Item name="vendorPreset" noStyle rules={[{ required: true, message: "必选" }]}>
                  <Select options={CATALOG_KIND_OPTIONS} placeholder="选择厂商 / 接入底座" />
                </Form.Item>
                <Form.Item noStyle dependencies={["vendorPreset"]}>
                  {({ getFieldValue }) =>
                    getFieldValue("vendorPreset") === "none" ? (
                      <Form.Item name="customDisplayName" noStyle rules={[{ required: true, message: "必填" }]}>
                        <Input placeholder="自定义厂商名称" />
                      </Form.Item>
                    ) : null}
                </Form.Item>
              </Space>
            </Form.Item>
          ) : (
            <Form.Item label="厂商">
              <Space wrap align="center">
                <Form.Item name="vendorPreset" noStyle>
                  <Select disabled options={CATALOG_KIND_OPTIONS} style={{ minWidth: 200 }} />
                </Form.Item>
                <Form.Item name="displayName" noStyle rules={[{ required: true, message: "必填" }]}>
                  <Input placeholder="展示名称" style={{ minWidth: 220 }} />
                </Form.Item>
              </Space>
            </Form.Item>
          )}
          <Form.Item
            name="baseUrl"
            label="Base URL"
            rules={[{ required: true, message: "必填" }, { type: "url", message: "须为合法 URL" }]}
          >
            <Input placeholder="https://api.example.com/v1" />
          </Form.Item>
          <Form.Item
            name="secretRef"
            label="密钥"
            rules={providerModalMode === "create" ? [{ required: true, message: "必填" }] : []}
          >
            <Input.Password placeholder="KMS 引用或密钥标识" autoComplete="new-password" />
          </Form.Item>
          <Form.Item name="enabled" label="启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={modelModalProviderId ? `添加模型 · ${modelParentLabel}` : "添加模型"}
        open={modelModalOpen}
        onOk={saveModelModal}
        onCancel={closeModelModal}
        destroyOnClose
        width={520}
        okText="添加"
        okButtonProps={{ disabled: presetSelectOptions.length === 0 }}
      >
        <Form form={modelForm} layout="vertical">
          {presetSelectOptions.length === 0 ? (
            <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 12 }}>
              当前厂商接入类型下没有可添加的模型（可能已全部接入或被其他厂商占用）。
            </Text>
          ) : null}
          <Form.Item name="presetModelId" label="模型" rules={[{ required: true, message: "请选择模型" }]}>
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="从预置清单选择"
              options={presetSelectOptions}
            />
          </Form.Item>
          <Form.Item name="enabled" label="启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

    </ProductPageShell>
  );
}
