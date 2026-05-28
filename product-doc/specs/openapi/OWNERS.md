# OpenAPI 行级 Owner（B 阶段 · 花名回填）

**用途**：与 [`design/api.md`](../design/api.md) **登记表「Owner」列**对签；**职能角色** 已于 `design/api.md` **登记表第四列** 标明，**本文件** 给出 **主/备** **具名落点**。

**规则**：**契约变更** **须** **同步** **本表 + 登记表** **或** **于 MR 描述 `@` 对口人**。**生产/规模化** **建议** **主/备** **为** **不同真人**（见下表 **备** 列）。登记行 **已链** 仓库内 YAML（[`README.md`](README.md)）；**生产 Hosted Swagger** **可**与仓库 **并行**。

**本仓库 · 统一 DRI（2026-05-11）**：下列 **主 owner** **均为** **Jesson@chainup.com**（**花名** **Jesson**）；**备** **暂** **填** **「同主」**（单人兼职占位）。**后续** **按域** **拆** **备** **为** **第二责任人** **时** **须** **更新** **本表** **并不必** **保持** **「统一指派」**。

| Spec 文件 | 主 owner（花名@域） | 备 owner |
|-----------|---------------------|----------|
| `admin/agent-management.yaml` | Jesson@chainup.com | 同主 |
| `admin/prompt-management.yaml` | Jesson@chainup.com | 同主 |
| `admin/tool-management.yaml` | Jesson@chainup.com | 同主 |
| `admin/ai-settings.yaml` | Jesson@chainup.com | 同主 |
| `admin/billing-admin.yaml` | Jesson@chainup.com | 同主 |
| `admin/access-control.yaml` | Jesson@chainup.com | 同主 |
| `admin/observability.yaml` | Jesson@chainup.com | 同主 |
| `admin/telegram-channels.yaml` | Jesson@chainup.com | 同主 |
| `admin/users-global-config.yaml` | Jesson@chainup.com | 同主 |
| `exchange/coobit-spot.yaml` | Jesson@chainup.com | 同主 |
| `exchange/coobit-margin.yaml` | Jesson@chainup.com | 同主 |
| `exchange/coobit-futures.yaml` | Jesson@chainup.com | 同主 |
| `exchange/coobit-wealth.yaml` | Jesson@chainup.com | 同主 |
| `exchange/coobit-automation.yaml` | Jesson@chainup.com | 同主 |
| `exchange/coobit-public.yaml` | Jesson@chainup.com | 同主 |
| `user/onboarding.yaml` | Jesson@chainup.com | 同主 |
| `internal/billing-token.yaml` | Jesson@chainup.com | 同主 |
| `user/billing-me.yaml` | Jesson@chainup.com | 同主 |
| `stream/user-private-ws.yaml` | Jesson@chainup.com | 同主 |
| `components/billing-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/access-control-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/agent-management-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/observability-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/telegram-channels-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/users-global-config-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/ai-settings-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/prompt-management-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/tool-management-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/exchange-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/onboarding-schemas.yaml` | Jesson@chainup.com | 同主 |
| `components/stream-schemas.yaml` | Jesson@chainup.com | 同主 |

**索引**：[README.md](README.md) · [`contract-closure.md`](../requirements/contract-closure.md) **§1.2 · §8** · [`closure-remaining` §0](../requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../requirements/closure-remaining.md#cc-exec-solve-path)
