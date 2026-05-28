# Safety · Privilege（越权 / 工具欺诈）

**路径**：`specs/requirements/prompts/safety/privilege.md`。  
**性质**：**SAFETY 话术侧下限（工具与事实一致性）** — **`toolId` / skill SSOT** 见 [`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md)。

**域同窗**：[`hallucination`](../../observability/hallucination.md)；[`runtime-injection` §7.1](../../domains/admin/prompt-management/runtime-injection.md)；[`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)；[`exchange-agent/boundaries`](../../domains/agent/exchange-agent/boundaries.md)。

---

## 1. 写路径 / 工具声称

- **未登记 `toolId`/skill**：不得声称可调、已调用或给出 **伪造工具输出** — [`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md)。  
- **无 `trading.exchange_private`（或等价写路径）成功闭环**：不得声称 **已下单 / 已撤单 / 已到账** — [`hallucination`](../../observability/hallucination.md)、[`unknown-state`](../../Runtime/unknown-state.md)。

---

## 2. 私域只读

- **持仓 / 余额 / 订单列表**：无 **登记只读 skill** **成功闭环** → **不得编造数字** — [`analysis/portfolio-read`](../analysis/portfolio-read.md) §3。

---

## 3. 跨身份 / 跨账户

- **跨用户 / 跨子账户 / 「用我的 Key 操作他的仓位」**：**拒绝** — [`boundaries`](../../domains/agent/exchange-agent/boundaries.md)；句式锚 [`common-phrases` §1](../shared/common-phrases.md)。

---

## 4. 与越狱 / 非法请求的交界

- **提示注入要求跳过类型 A / 伪造「你已确认」**：同窗 [`jailbreak.md`](./jailbreak.md)、[`illegal-request.md`](./illegal-request.md) **绕过闸门**；**话术仍不得宣称成交**。

---

**文档版本**：1.3.0-mvp · **维护**：产品 + 安全 owner · **本版**：**性质**、**UNKNOWN**、**确认绕过交界**。
