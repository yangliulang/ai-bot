<a id="slice-eligibility-runtime"></a>

# Access Control · Eligibility Runtime（准入评估顺序、结果契约与用户能力）

**叙事**：[`overview.md`](overview.md)；**模块门禁 FR**：[`functions.md`](functions.md)；**运行时叠层**：[`runtime-policy.md`](../../agent/exchange-agent/boundaries.md) §2 · **会话 config 冻结**：同文 §5；**I02**：[`config.md`](config.md) §4。

---

## 文档定位

本文定义 **端到端准入（Eligibility）** 在 BFF / 权限服务 / Runtime 侧须一致遵守之：**评估顺序**、**否决优先级**、**HTTP/内部 DTO 结果契约**、**灰度命中策略**、**会话内瞬时违约与会话冻结**、**合规凌驾**、**读侧缓存**、**事件模型**、**运行时反应**及 **对用户能力裁剪模型**。不显式重复 [`functions §2～§4`](functions.md) 之 FR/SC 条文；冲突时以 **`functions`** 为准，本文收口 **实现契约**。`code` 全集须在 [**`agent-management` §7.1**](../agent-management/functions.md) 与 **`design`/OpenAPI 同窗**（[`SC-AC-08`](functions.md)）。

| 议题 | § |
|------|---|
| Eligibility Evaluation Order | [§1](#1-eligibility-evaluation-order准入评估顺序) |
| Access Priority（否决优先级） | [§2](#2-access-priority否决与归因优先级) |
| Compliance Override | [§3](#3-compliance-override-rule合规凌驾) |
| Eligibility Result Contract | [§4](#4-eligibility-result-contract准入结果信封) |
| Grey Release Strategy | [§5](#5-grey-release-strategy灰度命中策略) |
| Runtime Access Freeze & Mid-Session Violation | [§6](#6-runtime-access-freeze-rule会话内访问与瞬时违约) |
| Access Runtime Cache Strategy | [§7](#7-access-runtime-cache-strategy读侧缓存) |
| Access Event Model | [§8](#8-access-event-model准入相关事件) |
| Runtime Reaction Rules | [§9](#9-runtime-reaction-rules事件到-runtime-行为) |
| User Capability Model | [§10](#10-user-capability-model终端能力裁剪) |

---

## 1. Eligibility Evaluation Order（准入评估顺序）

对用户一次 **门禁请求**（I02 前置、`FR-T02` 新执行，或 `design` 冻结之 **EvaluateEligibility**）：按下表 **自上而下** 求值；**任一环节** `allowed=false` **则短路**，仍须返回 **§4 信封**，并按 **§2** 归因 **`primaryDenyCode`**。

| Step | 门闩 id | 说明 |
|:----:|---------|------|
| 1 | **Blacklist** | 运营/合规封禁、黑名单。含 **`AGENT_USER_BLOCKED`** |
| 2 | **Region** | 地域/合规管辖区。未通过 → **`AGENT_REGION_BLOCKED`**（§7.1 同窗登记） |
| 3 | **KYC** | KYC/测评阈值。未通过 → **`AGENT_KYC_REQUIRED`** 或 **`AGENT_KYC_INSUFFICIENT`**（同窗择一冻结为枚举别名或并列码，OpenAPI 二选一收口） |
| 4 | **VIP** | 对比生效 **`AGENT_MIN_VIP_TIER`**（[`keys §3`](../trading-agent-config/keys.md)）。**比对口径**：**须使用该 Agent 专用子账户所隶属之母账号（主账号 · `userId`）的 VIP 等级**，与同会话 **`vipTier`**、运营摘要 **`§8.2`** **同窗**；**禁止**以子账户维度独立 VIP（若交易所本体无「子账户 VIP」，本条仍为 **防误实现**之明示）。未通过 → **`AGENT_MEMBERSHIP_BLOCKED`** |
| 5 | **Grey Bucket** | 产品线/渠道灰度。未命中 → **`AGENT_ROLLOUT_BLOCKED`** |
| 6 | **Runtime Allow** | 本链通过。**后续**仍有 billing、子账户、`FEATURE_*`、`GLOBAL_OFF` 等门禁，见 **[`runtime-policy` Kill](../../agent/exchange-agent/boundaries.md)**，**不归本节短路**，由各域 FR 接续 |

**与 I02**：[`config §4`](config.md) 第 2 步须等价于 Step 1～5 已得 `allowed=true`（或与 `GLOBAL_OFF`/计费组合后的最终门闩一致且可追溯）。

---

## 2. Access Priority（否决与归因优先级）

当多信号在同一请求窗口共存（缓存、快照、异步事件未完成），**`primaryDenyCode` / 运维归因**优先级 **自上而下**：

1. **Compliance Restriction（合规凌驾）** — §3  
2. **Blacklist** → `AGENT_USER_BLOCKED`  
3. **Region Restriction** → `AGENT_REGION_BLOCKED`  
4. **KYC** → `AGENT_KYC_REQUIRED` **或** `AGENT_KYC_INSUFFICIENT`（同窗登记哪一种生效）  
5. **VIP** → `AGENT_MEMBERSHIP_BLOCKED`  
6. **Grey Bucket** → `AGENT_ROLLOUT_BLOCKED`  

---

## 3. Compliance Override Rule（合规凌驾）

**规则**：任一有效的 **ComplianceRestriction**（监管机构/法务系统或 `design` 冻结之列管标签）须在评估 Step 1 之前或与 Step 1 合并语义后立即否决；不因用户在 Grey 白名单、高 VIP、运营临时放白而放行。**`code`** 建议 **`AGENT_COMPLIANCE_RESTRICTED`**（§7.1、`SC-AC-08` 登记）。

**展示**：须有可读 `reason`/子类型（不脱敏法务内部编号外）与用户 **可读恢复 Deeplink**（合规/地域等 **常指向交易所站内**；**与 Agent Key/onboarding 相关** **须与 **`FR-WEB01`** **同窗** **产品线绑定页**，避免笼统「主站」）；具体 UI 稿不归本文。

---

## 4. Eligibility Result Contract（准入结果信封）

### 4.1 JSON（HTTP 或等价 BFF 内部 DTO）

须可被单用户摘要、I02 错误体、运行时门禁复用同一语义：`allowed` + machine `code` + readable `reason`。`locale` 可选。

```json
{
  "allowed": false,
  "code": "AGENT_KYC_REQUIRED",
  "reason": "KYC level insufficient"
}
```

### 4.2 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| **`allowed`** | 是 | 布尔。`false` 时 `code`、`reason` 必填（`design` 可 tighten） |
| **`code`** | 若 `allowed=false` | 与 **`agent-management` §7.1** `enum` 一致；禁止私自发明未登记串 |
| **`reason`** | 若 `allowed=false` | 人类可读，可复制到运营摘要；遵守 [`rules`](rules.md) PII/合规 |

### 4.3 扩展（可选，`design` 冻结）

- **`capabilities`**：见 §10；仅在 `allowed=true` 或「仅禁用交易」（§9）时可返回。  
- **`evaluatedAt` / `eligibilityDecisionId`**：审计与 `observability` join。

---

## 5. Grey Release Strategy（灰度命中策略）

灰度桶可多策略组合（AND/OR 由 `design`/ADR 冻结）。下列为策略族：

| 策略 | 说明 | 示例 |
|------|------|------|
| **userId hash** | 稳定哈希 `userId` → `[0,1)`，按比例放行 | 10% = 阈值 ≤ 0.1 |
| **whitelist** | 显式 UID 列表或导入批次 | 指定用户 |
| **region** | 与 Region 门闩共用事实或独立地域桶 | 指定地区仅命中桶 B |

未命中任一 **必需桶** → **`AGENT_ROLLOUT_BLOCKED`**。**确定性**：同名 `userId` 在未改配置时哈希结果须稳定。

---

## 6. Runtime Access Freeze Rule（会话内访问与瞬时违约）

### 6.1 与 Config Version Freeze 区别

[**`runtime-policy` §5**](../../agent/exchange-agent/boundaries.md) 冻结 **`configVersion` 护栏**。本文所述 Eligibility/VIP/KYC/灰度仍可因 **用户主权数据变更** 在会话中失效：§6.2 优先生效。

### 6.2 会话内瞬时违约（示例：VIP 降级）

**给定**：Runtime 已启动（`executionId` 已受理或 `design` Session 锚点）。

**规则**：若在 **会话存活期**检测到已通过之 Step 被违反（例如 **母账号** **`vipTier`** 降至 **`AGENT_MIN_VIP_TIER`** 之下、KYC 被撤销、进入黑名单）：**V1 默认**：**立即 Kill Session**（会话终局：不接受新 `Execute`/写；在途按 `flow` **FR-T04** 与 `design` 终局）。**不等价于**仅 Pause，除非 **`product`/ADR** 书面降级。

---

## 7. Access Runtime Cache Strategy（读侧缓存）

| 项 | V1 建议 | 说明 |
|----|---------|------|
| **Cache TTL** | **5 min** | 门禁读（Eligibility snapshot for BFF）默认 TTL；`design` 可调 |
| **Force Refresh** | Kill Switch · Compliance · Blacklist 等凌驾/安全事件 | 上述事件须使 `userId` 侧缓存立即失效或 `version` 递增；下一轮请求不得以陈旧快照放行 |
| **Session Freeze** | 可选 · 与 `runtime-policy` §5 组合 | 若启用：会话内可把 Eligibility **`effectiveSnapshot`** pin 至 Runtime Start，但仍须监听 §8 强制性 Kill 事件（如黑名单、合规关停、VIP 击穿门槛按 §9） |

---

## 8. Access Event Model（准入相关事件）

须可被 Kafka / 所内 Bus / observability 订阅。**EventType** 字符串由 `design`/OpenAPI 冻结。

| Event | 简述 |
|-------|------|
| **`USER_BLACKLISTED`** | 用户被列入封禁/黑名单 |
| **`VIP_DOWNGRADED`** | **母账号** `vipTier` 下移且可能影响门禁 |
| **`KYC_REVOKED`**（或 **`KYC_LEVEL_CHANGED`**） | KYC 不再满足 |
| **`AGENT_ACCESS_DISABLED`** | 合规模块或其它凌驾关停准入 |

---

## 9. Runtime Reaction Rules（事件 → Runtime 行为）

| Event | Runtime 行为 |
|-------|----------------|
| **`USER_BLACKLISTED`** | **Kill Runtime**（会话终局，§6.2） |
| **`VIP_DOWNGRADED`**（击穿 VIP 门槛） | **Kill Runtime**（与 §6 示例一致；若产品改 Pause-only 须 ADR） |
| **`KYC_PENDING`** 或 **`KYC_REVOKED`**（未达到交易门禁） | **Disable Trading**：拦截 `call_exchange_write` 与等价自动化写；只读/Fallback 由 `design` 定 |
| **`AGENT_ACCESS_DISABLED`** | **Kill Runtime** + 清除 eligible 读缓存 |

---

## 10. User Capability Model（终端能力裁剪）

### 10.1 用途

在用户触达端（Telegram/主站）展示「能看什么、不能自动交易什么」，与 `FEATURE_AGENT_*`、`runtime-policy` 对齐。**`autoTrading`** 须恒为 `false`（[无人值守禁令](../../agent/exchange-agent/boundaries.md)）。

### 10.2 JSON 示例

```json
{
  "spot": true,
  "futures": false,
  "autoTrading": false
}
```

### 10.3 推导

| 字段 | 推导须考虑 |
|------|------------|
| **`spot`** | `FEATURE_AGENT_SPOT`、`design` 矩阵、Grey |
| **`futures`** | `FEATURE_AGENT_FUTURES`（默认 OFF 见 [`keys`](../trading-agent-config/keys.md)）、`design` |
| **`autoTrading`** | 首版 `false` 固定；不得因 `spot=true` 隐式 `true` |

**OpenAPI**：`capabilities` 可加于单用户摘要或 **EvaluateEligibility** 分支响应；与 [`design/api.md`](../../../../design/api.md) 同窗 PR。

---

**文档版本**：0.1.3 · **维护**：Access Control + Runtime + BFF owner · **本版**：§3 Compliance **展示** **Deeplink** **分层**（承 **0.1.2**）。
