import { App, Button, Drawer, Form, Input, InputNumber, Space, Typography } from "antd";
import { useEffect, useState } from "react";
import {
  patchAdminBillingCommerceCapabilityCatalog,
  type AdminCommerceCapabilityCatalogJson,
} from "../../api/billingCommerceClient";
import { ApiError } from "../../api/http";
import { BILLING_COMMERCE } from "../../copy/opsPanelHints";
import type { MockCommercePhase2AdminSnapshot } from "../../data/types";
import { BillingDualSignModal, validateBillingDualSignIds } from "./BillingDualSignModal";

const { Text } = Typography;

/** 计费规则可编辑项（配额由资源管理入账，不在此维护） */
type RuleFormRow = {
  capabilitySkuId: string;
  displayLabel: string;
  debitUnitsPerExecution: number;
};

type Props = {
  open: boolean;
  onClose: () => void;
  snapshot: MockCommercePhase2AdminSnapshot;
  apiOn: boolean;
  onSaved: () => void;
  /** 本地扣减规则覆盖（同步到 API 前由计费规则页注入） */
  ruleRowsOverride?: RuleFormRow[] | null;
};

function snapshotToRuleRows(snapshot: MockCommercePhase2AdminSnapshot): RuleFormRow[] {
  return snapshot.capabilityBuckets.map((b) => ({
    capabilitySkuId: b.capabilitySkuId,
    displayLabel: b.displayLabel,
    debitUnitsPerExecution: b.debitUnitsPerExecution ?? 1,
  }));
}

function ruleRowsToCatalogBody(
  catalogVersion: string,
  rows: RuleFormRow[],
  snapshot: MockCommercePhase2AdminSnapshot,
): AdminCommerceCapabilityCatalogJson {
  const snapById = new Map(snapshot.capabilityBuckets.map((b) => [b.capabilitySkuId, b]));
  return {
    catalogVersion,
    items: rows.map((r) => {
      const base = snapById.get(r.capabilitySkuId);
      return {
        capabilitySkuId: r.capabilitySkuId,
        displayLabel: r.displayLabel,
        remaining: base?.remaining ?? 0,
        quotaTotal: base?.quotaTotal,
        debitUnitsPerExecution: r.debitUnitsPerExecution ?? 1,
        resetsAt: base?.resetsAt ?? null,
      };
    }),
  };
}

export function CommerceCapabilityCatalogEditor({
  open,
  onClose,
  snapshot,
  apiOn,
  onSaved,
  ruleRowsOverride,
}: Props) {
  const { message } = App.useApp();
  const [form] = Form.useForm<{ rows: RuleFormRow[] }>();
  const [dualSignOpen, setDualSignOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      const rows = ruleRowsOverride?.length ? ruleRowsOverride : snapshotToRuleRows(snapshot);
      form.setFieldsValue({ rows });
    }
  }, [open, snapshot, ruleRowsOverride, form]);

  const openDualSign = async () => {
    try {
      await form.validateFields();
      if (!apiOn) {
        message.warning(BILLING_COMMERCE.catalogEditApiRequired);
        return;
      }
      setDualSignOpen(true);
    } catch {
      message.error(BILLING_COMMERCE.catalogEditValidateFailed);
    }
  };

  const submitPatch = async (ids: { operatorId: string; approverId: string }) => {
    const dualErr = validateBillingDualSignIds(ids.operatorId, ids.approverId);
    if (dualErr) {
      message.warning(dualErr);
      return;
    }

    const rows = form.getFieldValue("rows") as RuleFormRow[];
    const nextVersion = `${snapshot.catalogVersion}-ds-${Date.now().toString(36).slice(-4)}`;
    const body = ruleRowsToCatalogBody(nextVersion, rows, snapshot);

    setSubmitting(true);
    try {
      await patchAdminBillingCommerceCapabilityCatalog(body, {
        ifMatch: snapshot.catalogVersion,
      });
      message.success(BILLING_COMMERCE.catalogSaveSuccess);
      setDualSignOpen(false);
      onClose();
      onSaved();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        message.error(BILLING_COMMERCE.catalogConflict);
      } else {
        message.error(BILLING_COMMERCE.catalogSaveFailed);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Drawer
        title={BILLING_COMMERCE.catalogRulesEditTitle}
        width={480}
        open={open}
        onClose={onClose}
        destroyOnClose
        extra={
          <Button type="primary" onClick={() => void openDualSign()}>
            {BILLING_COMMERCE.catalogEditSubmit}
          </Button>
        }
      >
        <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 16 }}>
          {BILLING_COMMERCE.catalogRulesEditHint}
        </Text>
        <Form form={form} layout="vertical" disabled={!apiOn}>
          <Form.List name="rows">
            {(fields) => (
              <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                {fields.map((field) => {
                  const sku = form.getFieldValue(["rows", field.name, "capabilitySkuId"]) as string;
                  return (
                    <div
                      key={field.key}
                      style={{
                        border: "1px solid var(--ant-color-border-secondary)",
                        borderRadius: 8,
                        padding: 12,
                      }}
                    >
                      <Text code style={{ fontSize: 12 }}>
                        {sku}
                      </Text>
                      <Form.Item name={[field.name, "displayLabel"]} label="展示名" rules={[{ required: true }]}>
                        <Input />
                      </Form.Item>
                      <Form.Item
                        name={[field.name, "debitUnitsPerExecution"]}
                        label="每次执行扣减"
                        rules={[{ required: true, type: "number", min: 1 }]}
                      >
                        <InputNumber min={1} style={{ width: "100%" }} addonAfter="单位/次" />
                      </Form.Item>
                    </div>
                  );
                })}
              </Space>
            )}
          </Form.List>
        </Form>
        {!apiOn ? (
          <Text type="warning" style={{ fontSize: 12 }}>
            {BILLING_COMMERCE.catalogEditApiRequired}
          </Text>
        ) : null}
      </Drawer>

      <BillingDualSignModal
        open={dualSignOpen}
        title={BILLING_COMMERCE.catalogDualSignTitle}
        body={BILLING_COMMERCE.catalogDualSignBody}
        ifMatchLabel={snapshot.catalogVersion}
        confirmLoading={submitting}
        onCancel={() => setDualSignOpen(false)}
        onConfirm={submitPatch}
      />
    </>
  );
}
