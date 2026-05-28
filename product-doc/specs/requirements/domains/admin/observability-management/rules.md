# Observability Management · 规则与约束

1. **隐私**：**默认** **不**展示 **完整**用户 Prompt / PII；**须**「申请临时解密」流（合规定）。
2. **权限**：**仅** L2+ 可下钻 **Token 级** LLM 日志。
3. **不可改现场**：控制台 **不**提供「删日志」按钮；**仅**走 **合规下架**流程。
4. **一致字段**：`executionId`、`promptPackVersion` **须**与 **编排事件** schema 对齐。
5. **成本**：大批量导出 **须** rate limit（导出任务排队、**单次行数上限** **`design`/OpenAPI 冻结**）。
6. **计费协查**：**不得**在时间线 UI **捏造** **`SUCCESS` 核销/扣费**——**仅以** **`billing.entitlement_debit_*`**（**主链**）**或** **`billing.charge_*`**（**轨 A 对读**）**与** **`observability` §2 **或**账务 API **同窗** **状态** 为准。
7. **跨域跳转**：自本域跳到 **`billing`** **协查页** **须 SSO** **与** **`billing.management` IAM** **一致**；**禁止**在 URL query **带出**明文 **密钥/完整 Prompt**。

---

**文档版本**：0.1.3 · **维护**：产品 + 合规 · **本版**：**§6 轨 B 核销 UI 诚实展示**。**承** **0.1.2**。
