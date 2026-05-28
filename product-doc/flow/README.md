# `flow/` — 鸟瞰流程图（非步骤 SSOT）

本目录存放 **端到端鸟瞰**、可视化索引类 Markdown（例如 **Mermaid**）。**业务步骤级主流程、FR/SC 条文**仍以 **`specs/requirements/flows/`** 与各 **`domains/`** 文档为准。

| 文件 | 说明 |
|------|------|
| [`e2e-closed-loop.md`](e2e-closed-loop.md) | **端到端鸟瞰**（Telegram→Runtime→计费）；**阶段 F** 链 [**tool-registry-reconciliation §0**](../specs/requirements/domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) · [**billing-reconciliation §0**](../specs/requirements/domains/admin/billing-management/admin-console-billing-pages-reconciliation.md)；文首 **「架构语言」** → [`architecture`](../specs/design/architecture.md)；契约 [**`closure-remaining` §7**](../specs/requirements/closure-remaining.md#cc-remaining-open-items) 等 |
| [`e2e-closed-loop.html`](e2e-closed-loop.html) | **v1.8.0 四 Tab**（**业务场景总图** / 端到端鸟瞰 / Runtime-first / Sequence）；业务图同窗 [`product/flows` §0～§7](../product/flows.md)；技术图同窗 [`end-to-end-guide` §2](../product/end-to-end-guide.md)；改图须 **双文件同步** |
