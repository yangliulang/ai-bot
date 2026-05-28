# AI Settings · 流程

## 0. 单页分区与推荐顺序（控制台 · `ai.settings`）

界面将 **Infra 台账**（厂商与其下模型）与 **Runtime 模型策略** **分区展示**（[`overview.md`](overview.md) §1.1、`admin-console/naming-alignment.md` §6 **说明**）时，运营侧仍遵循 **先台账、后策略**，避免 **`modelId` 引用悬空**：

1. **厂商与模型**：新建或修改 **Provider**（接入底座、`baseUrl`、`secretRef` 等）→ **展开厂商行** → **添加模型**（仅允许底座预置清单、**`modelId` 全局唯一**）→ 对需对外路由的条目 **启用** → 视需要 **Health 探针**（与 **§1**、**§4**、**FR-MC407** 同窗）。
2. **使用策略**：在 **默认 / 分场景 / 降级** 等配置中选择 **`modelId`**；**可选集** **须限定为** 上一步台账中 **启用厂商** 下、**启用且未弃用** 的目录项。
3. **变更顺序**：调整台账（删除模型、禁用厂商/模型）可能使已有策略字段 **不合法** → **须** **保存前校验 / 保存后校正** 或 **阻断**（Demo 表单自动校正；生产与 **SC-AI-02**、错误模型叙事 **同窗**）。

以下 **§1～4** 为 **生命周期 / 契约向** 流程，与分区 **互补**：控制台只是把同一顺序 **摊开在两个 Tab**。

## 1. 接入 Provider

1. 运营登记 **元数据**（`baseUrl`、`providerId`）。
2. 在 **密钥服务** 创建 Secret → 控制台 **只保存** `secretRef`。
3. **手动或定时** **Health 探针** → 更新 `healthStatus`；失败 **按** [`Runtime/recovery.md`](../../../Runtime/recovery.md) **策略** **是否** **禁止** **新流量**（**网关** 实现）。

**审计**：创建/更新 **须** `admin.audit`（与 [`rules.md`](rules.md) **同窗**）。

## 2. 密钥轮换

1. 新 Secret **并行** 创建 → 新 `secretRef_B`。
2. **灰度**：网关 **可** 双引用验证（**所内** **实现定**）。
3. **切换** `secretRef` → **撤销** 旧 Secret（**密钥服务**）。
4. **全程** **审计**；**回滚** = 指回旧 `secretRef`（窗口内）。

## 3. 默认模型变更

1. 运营在 **模型目录** 或 **全局默认 / Runtime 模型策略**（Demo：**使用策略** Tab，所选 **`modelId` 须落在当前台账可用集**，见 [`overview.md`](overview.md) §1.1）修改 **默认 `modelId`**。
2. **须** **评估** **模板** `defaultModelRef` **是否** **仍合法**（**SC-AI-02**）；**不合法** **须** **阻塞发布** 或 **级联提示**（[`agent-management`](../agent-management/flow.md) **同窗**）。
3. **对外公告 / 灰度**（产品定，**非** **纯技术** **强制**）。

## 4. 熔断与降级

**Provider** 连续 **Health** 失败 **或** **错误率** **超阈**（与 **FR-MC407** **同窗**）→ **网关** **按** [`Runtime/recovery.md`](../../../Runtime/recovery.md) **切换** **备用 Provider/Model**；**须** **可观测**（`modelId` / `providerId` **在** **§2 事件** **可辨**）。

## 5. 互引

[`management-console-v1-prd.md`](../management-console-v1-prd.md) **附录 A**（`configKey`、会签等 **运营写路径** 口径）；[`observability-management/flow.md`](../observability-management/flow.md)（协查 **不** **替代** **本域** **配置**）。
