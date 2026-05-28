# Trading Agent Config · 规则与约束

与 [`functions.md`](functions.md)、[`keys.md`](keys.md) 一致。

## 1. SSOT 与私增键

新增 `configKey` 须先更新 [`keys.md`](keys.md) 与 PRD 附录 A §5.1；若影响 HTTP 契约则同步 [`design/api.md`](../../../../design/api.md)。禁止控制台写未登记键。

## 2. 审计

配置写路径永久可追溯审计（FR-MC707）。

## 3. 语义一致

不得发布与 `exchange-agent` / `telegram` FR 冲突的配置组合（[`functions.md`](functions.md) §6）。

## 4. 灰度与高危

`GLOBAL` 切换、`SYMBOL_ALLOWLIST` 清空须二次确认；可选金丝雀（[`functions.md`](functions.md) §7）。**`TELEGRAM_BOT_TOKEN_SECRET_REF`** 轮换、`deleteWebhook` **建议**等同 **高危**（二次确认 + **审计** + **可选双人**，见 [`telegram/admin-bot-config`](../../agent/telegram/admin-bot-config.md)）。

## 5. 回滚 SLA

RTO 数值由 observability / 运维协定，不由本文约束。

## 6. RBAC（V1 占位）

与 [`management-console-v1-prd.md`](../management-console-v1-prd.md) §8、`CONFIG_OPERATOR` 命名对齐；**原则**：Viewer 可读全局摘要；`CONFIG_OPERATOR` 可提交分组写入；`GLOBAL` / `OPS` 闸是否放开给该角色由 `design`/IAM 冻结（可收紧为仅 Ops）。

---

与 [`overview.md`](overview.md)、[`config.md`](config.md)、[`flow.md`](flow.md) 同步维护。
