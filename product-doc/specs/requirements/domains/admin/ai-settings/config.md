# AI Settings · 配置与 IA

## 1. 对象（示意字段）

| 对象 | 字段（示意） | 说明 |
|------|----------------|------|
| **Provider** | `providerId`、`displayName`、`catalogKind`（接入底座 / 预置模型清单族）、`baseUrl`、`secretRef`、`enabled`、`healthStatus`、`lastProbedAt` | `secretRef` **仅** KMS/Secret 名或 ARN；**禁止** `apiKeyPlain`；**Demo** 中 **「厂商」** 表单项合并 **底座选择 + 展示名**（见 [`overview.md`](overview.md) §1.1） |
| **Model** | `modelId`、`providerId`、`contextWindow`、`capabilities[]`、`deprecated`、`enabled` | `modelId` **须**在 **观测** 与 **FR-MC804** **同窗** |
| **Gateway defaults**（profile） | `temperatureDefault`、`temperatureMin`、`temperatureMax`、`maxOutputTokensDefault`、`maxOutputTokensCeiling`、`timeoutMs`、`rpmLimit`、`concurrencyLimit` | 与 **FR-MC403～406** **1:1 或可子集**；**OpenAPI** 终裁 |
| **Health policy** | `probeIntervalSec`、`failThreshold`、`alertHook`（可选） | 与 **FR-MC407** **同窗** |

## 2. IA（信息架构）

**生产 / 契约面**（可与 OpenAPI 拆面）：可分 **Provider**、**模型目录**、**网关默认 / Health** 等视图；字段真源仍以 **本文 + `design/api.md`** 为准。

**后台 Demo（`/ai-settings`，`ai.settings`）**：**单页两 Tab** — **厂商与模型**（厂商行展开维护下属模型）与 **使用策略**（Runtime 模型策略表单）。**策略中的 `modelId` 选择器** **只消费** 台账中当前 **可用** 模型子集（启用厂商 × 启用且未弃用模型），与 [`overview.md`](overview.md) **§1.1** 一致。

- **禁止**「粘贴 API Key」**落库**控件；若 **一次性** 录入，**须** **立即** 写 **Secret 后端** 且 UI **只回显** `secretRef` **或**「已配置」。
- **只读** 区：**Runtime** 实际 **effective** 路由摘要（可选，**BFF**）— **真源** **仍** **本域 + 网关**。

## 3. IAM（与运营角色）

| 能力 | 建议角色 |
|------|----------|
| 读 Provider/Model/默认 | `READ_ONLY` / 支持 |
| 写 Provider、`secretRef` 绑定 | **窄** **`AI_SETTINGS_OPERATOR`**（与 **全局配置** **分权**） |
| 改 **Gateway defaults** / Health 策略 | 同上或 **SRE 子集**（产品定） |

**双签**：**费率/计费** **不在本域** — 见 [`billing-management`](../billing-management/overview.md)。

## 4. 互引

[`integrations/llm/provider-routing.md`](../../../integrations/llm/provider-routing.md)；[`agent-management/config.md`](../agent-management/config.md)；[`design/api.md`](../../../../design/api.md)。
