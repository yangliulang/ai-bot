import { App, Input, Modal, Segmented, Select, Space, Typography } from "antd";
import { useEffect, useState } from "react";
import type { MockPromptPack } from "../../data/types";
import { zhPromptPackKind } from "../../copy/zhLabels";
import { createBlankEphemeralBootstrap } from "./promptEphemeral";
import type { EditorBootstrap } from "./promptEditorBootstrap";
import { PROMPT_GOVERNANCE_LIST_KINDS } from "./promptPackKinds";

const { Text, Paragraph } = Typography;

type CreateMode = "blank" | "template";

export function PromptCreateDraftModal({
  open,
  onClose,
  onBlankCreate,
  onCloneFromTemplate,
  templateRows,
  fixedKind,
  blankKindOptions,
  title: modalTitle = "新建 Prompt 草稿",
}: {
  open: boolean;
  onClose: () => void;
  /** 同步：空白草稿已构造，由父级持久化并路由 */
  onBlankCreate: (bootstrap: EditorBootstrap) => void;
  /** 异步：从已有包拉取编辑载荷后克隆 */
  onCloneFromTemplate: (templateId: string) => Promise<void>;
  templateRows: MockPromptPack[];
  /** 固定类型（如 SAFETY 页） */
  fixedKind?: MockPromptPack["kind"];
  /** 空白草稿可选 kind；默认策略页三选一 */
  blankKindOptions?: MockPromptPack["kind"][];
  title?: string;
}) {
  const { message } = App.useApp();
  const [mode, setMode] = useState<CreateMode>("blank");
  const [blankKind, setBlankKind] = useState<MockPromptPack["kind"]>("TRADING");
  const [blankTitle, setBlankTitle] = useState("");
  const [templateId, setTemplateId] = useState<string>("");
  const [cloning, setCloning] = useState(false);

  useEffect(() => {
    if (!open) return;
    setMode("blank");
    setBlankTitle("");
    setCloning(false);
    const kinds = blankKindOptions ?? (fixedKind ? [fixedKind] : [...PROMPT_GOVERNANCE_LIST_KINDS]);
    setBlankKind(fixedKind ?? kinds[0] ?? "TRADING");
  }, [open, fixedKind, blankKindOptions]);

  const selectKindOptions = blankKindOptions ?? (fixedKind ? [fixedKind] : [...PROMPT_GOVERNANCE_LIST_KINDS]);

  useEffect(() => {
    if (!open) return;
    setTemplateId((prev) =>
      templateRows.some((p) => p.promptPackId === prev) ? prev : (templateRows[0]?.promptPackId ?? ""),
    );
  }, [open, templateRows]);

  const onOk = async () => {
    if (mode === "blank") {
      const k = fixedKind ?? blankKind;
      const b = createBlankEphemeralBootstrap(k, blankTitle);
      onBlankCreate(b);
      return;
    }
    if (!templateId.trim()) {
      message.warning("请选择一个已有 Prompt 作为模板");
      return;
    }
    setCloning(true);
    try {
      await onCloneFromTemplate(templateId);
    } catch (e) {
      message.error(e instanceof Error ? e.message : String(e));
    } finally {
      setCloning(false);
    }
  };

  return (
    <Modal
      title={modalTitle}
      open={open}
      okText={mode === "template" ? "复制并打开" : "创建并打开"}
      cancelText="取消"
      confirmLoading={cloning}
      destroyOnClose
      onOk={() => void onOk()}
      onCancel={onClose}
    >
      <Space direction="vertical" size={14} style={{ width: "100%" }}>
        <Segmented
          block
          value={mode}
          onChange={(v) => setMode(v as CreateMode)}
          options={[
            { label: "空白草稿", value: "blank" },
            { label: "从模板复制", value: "template" },
          ]}
        />

        {mode === "blank" ? (
          <>
            <Paragraph type="secondary" style={{ marginBottom: 0, fontSize: 13 }}>
              将生成仅存在于本浏览器的 <Text code>local-draft-*</Text> ID；保存草稿写入会话。注册到治理列表需后续接入创建包 API。
            </Paragraph>
            {!fixedKind ? (
              <div>
                <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 6 }}>
                  包类型
                </Text>
                <Select
                  style={{ width: "100%" }}
                  value={blankKind}
                  onChange={setBlankKind}
                  options={selectKindOptions.map((k) => ({ value: k, label: zhPromptPackKind(k) }))}
                />
              </div>
            ) : (
              <Text type="secondary" style={{ fontSize: 13 }}>
                类型固定为 <Text>{zhPromptPackKind(fixedKind)}</Text>（<Text code>{fixedKind}</Text>）
              </Text>
            )}
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 6 }}>
                显示标题（可选）
              </Text>
              <Input
                placeholder="如 现货限价助手 v2"
                value={blankTitle}
                onChange={(e) => setBlankTitle(e.target.value)}
                allowClear
              />
            </div>
          </>
        ) : (
          <>
            <Paragraph type="secondary" style={{ marginBottom: 0, fontSize: 13 }}>
              拉取所选包的正文、Few-shot 与变量结构，生成新的本地草稿副本；不会覆盖原包。
            </Paragraph>
            <Select
              showSearch
              style={{ width: "100%" }}
              placeholder="搜索 ID 或标题"
              value={templateId || undefined}
              onChange={setTemplateId}
              options={templateRows.map((p) => ({
                value: p.promptPackId,
                label: `${p.title} · ${zhPromptPackKind(p.kind)} · ${p.promptPackId}`,
              }))}
              optionFilterProp="label"
              disabled={templateRows.length === 0}
            />
            {templateRows.length === 0 ? (
              <Text type="warning" style={{ fontSize: 12 }}>
                当前无可用模板，请刷新列表或改用空白草稿。
              </Text>
            ) : null}
          </>
        )}
      </Space>
    </Modal>
  );
}
