import { useCallback, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Segmented, Space, Button, Tooltip, Typography } from "antd";
import {
  BoldOutlined,
  ItalicOutlined,
  UnorderedListOutlined,
  OrderedListOutlined,
  CodeOutlined,
  FontSizeOutlined,
} from "@ant-design/icons";
import { markdownLiteInsertPrefixAtLogicalLineHead, markdownLiteWrapSelection } from "./markdownLiteEdit";
import "./promptMarkdownLiteField.css";

const { Text } = Typography;

export type PromptMarkdownLiteFieldProps = {
  value: string;
  onChange: (markdown: string) => void;
  disabled?: boolean;
  minEditorHeightPx?: number;
};

/**
 * Prompt 治理用 **Markdown Lite**：源码编辑、安全预览、少量插入工具。
 * 不包含：完整 IDE、Playground、非标准 HTML。
 */
export function PromptMarkdownLiteField({
  value,
  onChange,
  disabled,
  minEditorHeightPx = 360,
}: PromptMarkdownLiteFieldProps) {
  const taRef = useRef<HTMLTextAreaElement | null>(null);
  const [mode, setMode] = useState<"edit" | "preview">("edit");

  const applyEdit = useCallback(
    (next: string, start: number, end: number) => {
      onChange(next);
      requestAnimationFrame(() => {
        const el = taRef.current;
        if (!el) return;
        el.focus();
        el.setSelectionRange(start, end);
      });
    },
    [onChange],
  );

  const onBold = useCallback(() => {
    const el = taRef.current;
    if (!el || disabled) return;
    const { selectionStart: s, selectionEnd: e } = el;
    const { next, focusStart, focusEnd } = markdownLiteWrapSelection(value, s, e, "**", "**", "加粗文案");
    applyEdit(next, focusStart, focusEnd);
  }, [applyEdit, disabled, value]);

  const onItalic = useCallback(() => {
    const el = taRef.current;
    if (!el || disabled) return;
    const { selectionStart: s, selectionEnd: e } = el;
    const { next, focusStart, focusEnd } = markdownLiteWrapSelection(value, s, e, "*", "*", "倾斜文案");
    applyEdit(next, focusStart, focusEnd);
  }, [applyEdit, disabled, value]);

  const onH2 = useCallback(() => {
    const el = taRef.current;
    if (!el || disabled) return;
    const caret = el.selectionStart;
    const { next, focus } = markdownLiteInsertPrefixAtLogicalLineHead(value, caret, "## ");
    applyEdit(next, focus, focus);
  }, [applyEdit, disabled, value]);

  const onBullet = useCallback(() => {
    const el = taRef.current;
    if (!el || disabled) return;
    const caret = el.selectionStart;
    const { next, focus } = markdownLiteInsertPrefixAtLogicalLineHead(value, caret, "- ");
    applyEdit(next, focus, focus);
  }, [applyEdit, disabled, value]);

  const onOrdered = useCallback(() => {
    const el = taRef.current;
    if (!el || disabled) return;
    const caret = el.selectionStart;
    const { next, focus } = markdownLiteInsertPrefixAtLogicalLineHead(value, caret, "1. ");
    applyEdit(next, focus, focus);
  }, [applyEdit, disabled, value]);

  const onFence = useCallback(() => {
    const el = taRef.current;
    if (!el || disabled) return;
    const { selectionStart: s, selectionEnd: e } = el;
    const { next, focusStart, focusEnd } = markdownLiteWrapSelection(value, s, e, "```\n", "\n```\n", "// 占位说明");
    applyEdit(next, focusStart, focusEnd);
  }, [applyEdit, disabled, value]);

  const previewPane =
    mode === "preview" ? (
      <div className="prompt-markdown-lite-preview" aria-live="polite">
        {value.trim() ? (
          <ReactMarkdown>{value}</ReactMarkdown>
        ) : (
          <Text type="secondary">暂无内容 · 切换到「源码」开始编写</Text>
        )}
      </div>
    ) : null;

  return (
    <Space direction="vertical" size={10} style={{ width: "100%" }}>
      <Space wrap align="center" style={{ width: "100%", justifyContent: "space-between" }}>
        <Space wrap size={6}>
          <Tooltip title="加粗">
            <Button type="text" size="small" icon={<BoldOutlined />} disabled={disabled} onClick={onBold} />
          </Tooltip>
          <Tooltip title="倾斜">
            <Button type="text" size="small" icon={<ItalicOutlined />} disabled={disabled} onClick={onItalic} />
          </Tooltip>
          <Tooltip title="二级标题（## ）">
            <Button type="text" size="small" icon={<FontSizeOutlined />} disabled={disabled} onClick={onH2} />
          </Tooltip>
          <Tooltip title="无序列表（-）">
            <Button type="text" size="small" icon={<UnorderedListOutlined />} disabled={disabled} onClick={onBullet} />
          </Tooltip>
          <Tooltip title="有序列表（1.）">
            <Button type="text" size="small" icon={<OrderedListOutlined />} disabled={disabled} onClick={onOrdered} />
          </Tooltip>
          <Tooltip title="围栏代码块">
            <Button type="text" size="small" icon={<CodeOutlined />} disabled={disabled} onClick={onFence} />
          </Tooltip>
        </Space>
        <Segmented
          size="small"
          value={mode}
          disabled={disabled}
          onChange={(v) => setMode(v as "edit" | "preview")}
          options={[
            { label: "源码", value: "edit" },
            { label: "Markdown Lite 预览", value: "preview" },
          ]}
        />
      </Space>

      {mode === "edit" ? (
        <textarea
          ref={taRef}
          value={value}
          disabled={disabled}
          spellCheck={false}
          onChange={(e) => onChange(e.target.value)}
          placeholder={"# Spot trading system prompt\n\n## 规则\n- 条目一\n"}
          aria-label="Prompt Markdown 源码"
          style={{
            width: "100%",
            boxSizing: "border-box",
            minHeight: minEditorHeightPx,
            resize: "vertical",
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, monospace',
            fontSize: 13,
            lineHeight: 1.55,
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid var(--ant-color-border, #d9d9d9)",
            outline: "none",
            background: "var(--ant-color-bg-container, #fff)",
            color: "var(--ant-color-text, rgba(0,0,0,0.88))",
          }}
        />
      ) : (
        previewPane
      )}
    </Space>
  );
}
