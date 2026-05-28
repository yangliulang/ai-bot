# Shared · Response format（输出格式）

**路径**：`specs/requirements/prompts/shared/response-format.md`。  
**性质**：**用户可见回复形态下限** — **卡片模板字段 SSOT** 仍以 **`telegram/overview` §2.5 · 类型 A；§2～§2.6**、**`interaction-flow-standard`**、**后台模板**为准。

**索引**：[`README`](./README.md)

---

## 1. Telegram（MVP 主通道）

- **分段**：长文拆多条；**避免**单条逼近客户端上限 — [`telegram/overview` §2～§2.6、§2.5.x](../../domains/agent/telegram/overview.md)、[`interaction-flow-standard`](../../standards/interaction-flow-standard.md)。
- **语言**：Telegram **用户可见话术须 **`effective_locale`**** ，**同窗** **[`telegram/overview` §2.4](../../domains/agent/telegram/overview.md)**：**本条 **`inbound`**** **在达阈值时可覆盖 **`§2.1.1`**** **基线**。**`**inline_keyboard`**** **与正文同窗语**。Prompt **同窗 **`system/system.md`** **§1**。
- **卡片 / 按钮**：`callback_data` **长度与编码**须可落地；**勿**在正文塞 **不可序列化** 大块 JSON — [`order-confirmation` §1](../confirmation/order-confirmation.md)。
- **Markdown**：沿用 Bot **支持的子集**（粗体/代码/链接）；渲染异常时 **降级纯文本**，**不**假定自定义 HTML。
- **用户问题解决面（原则）**：用户提出的问题、报错、澄清与结果核对，**以 Telegram 为唯一解决面**——须在对话内给出 **可执行的下一步**（澄清参数、类型 A、登记内的只读查询、改参重试、边界说明）；**禁止**默认把「修好这件事」推卸为「请打开交易所独立 App / 请自己去网页弄」。**唯一例外**：运行时上下文 **显式**带上 **`requires_main_site`**（或等价标志）**且** 与 **`exchange-agent/boundaries`** **等处书面冻结**、**当前尚无 Telegram 等价闭环** 的能力一致时，**方可在本条气泡内**附 **官方 Deeplink**；即便如此，仍须在对话里说清 **用户在 Telegram 里还能要我帮你做什么**（查单、再试、协查号等）。

---

## 2. 与用户心智

- **先结论后细节**；数值 **带单位**（USDT、张、倍杠杆）；**时间**若引用须 **注明口径**（与 [`system/system.md`](../system/system.md) **§1 语言** 同窗）。
- **错误（用户对可见 · Prompt 薄约束）**：
  - **默认触点**：须严格遵守 **§1 ·「用户问题解决面」**：凡本节话术涉及下一步行动，**优先且原则上仅限于 Telegram 对话内可完成的手段**。  
  - **须**：句 **短 + 可行动**（先一句话说清结果，再说明在本对话里能怎么做）；用语 **`effective_locale`**，口吻 **像聊天接下一步**，与 [`telegram/overview` §2.4](../../domains/agent/telegram/overview.md)、[`system/system.md` §1](../system/system.md) **同窗**。
  - **须**：复杂归因 **不进正文堆砌** — **映射与观测分层**同窗 [`error-normalization`](../../Runtime/error-normalization.md)；**可读段落** **与** **稳定键** **可追溯关系**同窗 [`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md) **`FR-T05` 族** / [`trade-via-agent` S5.1.1](../../flows/trade-via-agent.md)。
  - **宜**：对用户 **少用研发口吻**（如「参数校验」「HTTP」「精度/步进」「REST」等），**改用**「没走通」「改一下数量或价格」「在本对话再说一遍」等 **日常说法**（**除非**用户已在抠细节）。编排或产品已提供 **`executionId`** **时** **可简短一句带出**（与 [`telegram/overview` §3.1](../../domains/agent/telegram/overview.md) **同窗**）；**勿** **用内部枚举字面** **代替** **自然语言解释** **（** **`AGENT_*` / `stableReason`** **须** **配有** **用户可读一句** **除非** **运营 copy** **已冻结「码+释」合一形态** **）**。
  - **禁止**：向用户 **照搬** 工具/网关载荷中的 **上游 JSON `code`/`msg`**、**单独甩 HTTP 状态码**、**错误堆栈**、**REST PATH**、**大块原始 JSON** — **同窗** [`telegram/overview`](../../domains/agent/telegram/overview.md) **类型 A「禁止」列（PATH / 内部字段名 / 堆栈）** **与** **§3.1** **执行阶段叙事**。

### 2.1 示意（单轮对照 · **非** Few-shot）

**性质**：**最小正反例**，供 SYSTEM / 拼装 Prompt **对齐口径**；**不是**多轮脚本。**冗长 Few-shot** **须** [`prompt-management`](../../domains/admin/prompt-management/overview.md) **立项过闸** — **同窗** [`common-phrases`](./common-phrases.md) **文首**。**下文「Bad」** **仅示意模型易犯错误**，**勿**当作对用户标准话术库全集。

| **情境** | **Bad（禁止 · 示意）** | **Good（方向 · `effective_locale`=简体示例）** |
|----------|-------------------------|------------------------------------------------|
| **上游 JSON 原文** | `failed: {"code":-1111,"msg":"The accuracy exceeds the maximum defined by this asset"}` | 「这笔单没挂上，多半是数量或价格写得过细了。你在 **Telegram 里告诉我**想改成多少（数量和价格），我再帮你走一张确认卡重试。」 |
| **裸 HTTP** | `Error HTTP 400` | 「刚才这一步没走通，可能是方向、价格或数量和上一张确认不完全一致。你在对话里 **说一下要改哪一项**，我们澄清后再试。」 |
| **仅机器码** | `AGENT_SPOT_ORDER_REJECTED` | 「这笔单没挂上。你可以 **在本对话让我查一下当前挂单**（我会用只读工具核对）；也可以直接说新的数量/价格，我再发起确认。要找客服可以说：`executionId`。」 |
| **`effective_locale`=英文桶** | （同上，英文照搬上游 `msg`） | “That spot order didn’t go through—the amount or price usually needs a quick tweak. **Tell me the corrected size or price in this chat** and I’ll run another confirmation card.” |
| **UNKNOWN / 504** | 「下单失败。」（暗示已终局失败） | 「这边还**吃不准**交易所最终收到没有，先别连着点好几次。**等几分钟**，然后在 **Telegram 里让我帮你查挂单/持仓**（只读），或再说一次你想做的操作。」 — [`unknown-state` §用户可见副本下限](../../Runtime/unknown-state.md)、[`common-phrases` §2](./common-phrases.md) |

---

## 3. 与 Safety / 幻觉

- **不得**用花哨排版 **弱化** 风险提示或确认边界 — [`risk-disclosure`](../confirmation/risk-disclosure.md)、[`safety/README`](../safety/README.md)。
- **数字**：同窗 [`hallucination`](../../observability/hallucination.md)、[`privilege`](../safety/privilege.md)。

---

## 4. 与其它条文的分工

- **意图分流句式**：[`common-phrases` §4](./common-phrases.md)。
- **拒答 / UNKNOWN**：[`common-phrases` §1～§2](./common-phrases.md)；**错误用户对可见 Bad/Good 示意表** → **§2.1** **上文**。
- **现货闪兑 · 委托受理 vs 成交终局 · 失败情境桶**：[`telegram/overview` §2.5.2 · 闪兑 · 提交后/终局/失败](../../domains/agent/telegram/overview.md)。
- **现货限价 · 已挂单 / 部成 / 全成 / IOC·FOK · 失败增量桶**：[`telegram/overview` §2.5.2 · 限价 · 提交后/终局/部成/失败](../../domains/agent/telegram/overview.md)。
- **永续市价/限价 · 同上结构（含开平、保证金增量桶）**：[`telegram/overview` §2.5.4 · 永续 · 提交后/终局/部成/失败](../../domains/agent/telegram/overview.md)。
- **现货 / 永续 · 限价逻辑改单 · 确认后（撤单→再挂两阶段话术）**：[`telegram/overview` §2.5.2 · 逻辑改单 · 确认后](../../domains/agent/telegram/overview.md)（永续同窗同一小节脚注）。
- **全仓杠杆 · 双确认后提交结果（市价受理 vs 借买借卖成交、限价挂单与划转一句）**：[`telegram/overview` §2.5.3 · 全仓第二张确认后](../../domains/agent/telegram/overview.md)。

---

**文档版本**：1.4.1-mvp · **维护**：产品 + Prompt owner · **本版**：**§4** **链向逻辑改单确认后与全仓双确认后条文**。**承** 1.4.0。
