# Backend 交付说明 · 2026-05-28--skill-contract-eval-staging

## 启动

```bash
cd server && uv run chainup-agent-api
```

Base URL：`http://127.0.0.1:8080`

## 实现摘要

| AC | 交付 |
|----|------|
| AC-1 | `eval_skill_contract.py` · `EVAL_SKILL_P0_SET_IDS`（4 条）· `EVAL_VERSION = "0.1.0"` |
| AC-2 | `assert_eval_skill_missing_qty_no_confirm` |
| AC-3 | `assert_eval_skill_flash_no_limit_price` |
| AC-4 | `assert_eval_skill_margin_double_confirm` → `margin_cross_write_allowed` |
| AC-5 | `assert_eval_skill_amend_cancel_before_order` |
| AC-6 | `run_eval_skill_p0_fixture` · `EVAL_SKILL_P0_FIXTURES`（同窗 `fixtures.ts`） |
| AC-7 | `tests/test_eval_skill_contract.py` |
| AC-8 | 存量 `GET /api/v1/runtime/skill-operation-spec/effective`（DB seed · `sections[].bodyMarkdown`） |

槽位门禁 Python 端口：`application/skill_contract_gates.py`（对齐 `product-doc/src/admin/src/skillContract/gates.ts`）。

**无新 HTTP 路由**；OpenAPI 文档化存量 effective + scenarios 读路径。

## 规格 SSOT

- `product-doc/specs/requirements/evals/skill-contract.md` **§3**
- `product-doc/specs/requirements/skill-specs/production-runtime.md` **§3**
- Vitest 同窗：`product-doc/src/admin/src/skillContract/`

## 自测

```bash
cd server && uv run pytest tests/test_eval_skill_contract.py -q
```

**2026-05-28**：**14 passed**。

## curl 示例

### Effective Given（AC-8）

```bash
curl -s "http://127.0.0.1:8080/api/v1/runtime/skill-operation-spec/effective?skillId=skill.spot.limit_order" \
  | jq '{skillId, lifecycle, skillSpecVersion, sectionCount: (.sections | length)}'
```

### P0 fixture scenario 对照（AC-6 可选）

```bash
for id in trade.spot.limit_order trade.spot.flash_convert margin.cross.market_order trade.spot.amend_limit_order; do
  curl -s -o /dev/null -w "$id %{http_code}\n" "http://127.0.0.1:8080/api/v1/agent/scenarios/$id"
done
```

## 错误码

本包 **无新路由**；effective 沿用 **`PROMPT_SKILL_REF_INVALID`** **403/404**（`AppError`）。

## 依赖

- **`2026-05-27--skill-publish-effective`** **done**（effective 读 DB + bundle import）
- **`2026-05-28--pipeline-eval-orchestration-align`** **done**（管线 Eval 分工独立）

## test-agent 提示

本包 `skips` 含 `frontend.integrate` · `test.e2e` · `designer.review`。API P0 通过后请提醒指挥官：

```text
/pipeline-skip 2026-05-28--skill-contract-eval-staging
```
