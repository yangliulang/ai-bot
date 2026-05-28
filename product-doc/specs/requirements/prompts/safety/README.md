# `safety/` · 索引（MVP）

**路径**：`specs/requirements/prompts/safety/README.md`。

本目录三篇为 **SAFETY Prompt 话术侧下限**；**黑名单扫描 Scope、`safetyPhraseBlocklistRevision`、 denylist 真源** → [`runtime-injection` §7.1](../../domains/admin/prompt-management/runtime-injection.md)。**线上运营包**：**`pp-safety-global`**（[`governance-map.md` §2](../governance-map.md)）· 控制台 **`/prompts/safety`** · [`prompt-management/overview`](../../domains/admin/prompt-management/overview.md)。

---

## 文件

| 文件 | 主题 |
|------|------|
| [`jailbreak.md`](./jailbreak.md) | 越狱 / 注入 / 角色伪造 |
| [`privilege.md`](./privilege.md) | 越权工具、私域数据、写闭环一致性 |
| [`illegal-request.md`](./illegal-request.md) | 违法 / 合规拒绝、绕过闸门、滥用 |

---

## 阅读顺序（建议）

1. [`runtime-injection` §7.1](../../domains/admin/prompt-management/runtime-injection.md)  
2. [`privilege.md`](./privilege.md)（工具与事实 — 与 [`hallucination`](../../observability/hallucination.md) 最近）
3. [`jailbreak.md`](./jailbreak.md) ↔ [`illegal-request.md`](./illegal-request.md)

---

## 横向宿主

| 主题 | 文档 |
|------|------|
| **幻觉 / 成交真实性** | [`observability/hallucination`](../../observability/hallucination.md) |
| **确认链** | [`confirmation/README`](../confirmation/README.md) |
| **合规边界** | [`exchange-agent/boundaries`](../../domains/agent/exchange-agent/boundaries.md) |
| **拒答句式锚** | [`shared/common-phrases` §1](../shared/common-phrases.md) |

---

## 上级

[`../README.md`](../README.md)

---

**文档版本**：1.1.1 · **维护**：产品 + 安全 owner · **本版**：**`pp-safety-global`** · governance-map 链；**承** 1.1.0。
